#!/usr/bin/env python3
"""Normalize one acquired Overture source run and publish identity diagnostics."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import duckdb

from acquire_overture_places import ENGINE_DIR, REPO_ROOT, configure_extensions, database_path, resolve_boundary, sql_literal


def checksum(path: Path) -> str:
    """Return a stable checksum for each derived local artifact."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def latest_source_run(output_root: Path, market: str) -> Path:
    """Select the newest completed source run when the caller does not name one."""

    runs = sorted(path.parent for path in (output_root / market).glob("*/source_run_manifest.json"))
    if not runs:
        raise FileNotFoundError(f"No completed source run found for {market}.")
    return runs[-1]


def normalize_sql(source_path: Path, run: dict, boundary_wkb: bytes) -> str:
    """Create a source-place record without applying governed taxonomy rules."""

    source = f"read_parquet({sql_literal(str(source_path))})"
    boundary = sql_literal(boundary_wkb.hex())
    return f"""
    WITH raw AS (
        SELECT *,
            row_number() OVER (PARTITION BY id ORDER BY id) AS source_id_rank
        FROM {source}
    ), shaped AS (
        SELECT
            'overture' AS source_system,
            {sql_literal(run['source_release'])} AS source_release,
            id AS source_id,
            concat('overture|', {sql_literal(run['source_release'])}, '|', id) AS source_record_key,
            names.primary AS source_name,
            addresses[1].freeform AS source_address,
            addresses[1].postcode AS source_postal_zip,
            categories.primary AS source_category_primary,
            basic_category AS source_category_basic,
            taxonomy.primary AS source_taxonomy_primary,
            taxonomy.hierarchy AS source_taxonomy_hierarchy,
            to_json(struct_pack(categories := categories, confidence := confidence,
                sources := sources, brand := brand, operating_status := operating_status,
                websites := websites, phones := phones)) AS source_attributes,
            geometry,
            ST_GeometryType(geometry) AS geometry_type,
            ST_PointOnSurface(geometry) AS representative_point,
            {sql_literal(str(run['market_id']))} AS market_id,
            {int(run['boundary']['boundary_vintage'])} AS market_boundary_vintage,
            {sql_literal(run['source_run_id'])} AS source_run_id,
            {sql_literal(run['extracted_at'])} AS extracted_at,
            {sql_literal(json.dumps(run['query'], sort_keys=True))} AS source_query,
            {sql_literal(run['cache']['uri'])} AS cache_uri,
            source_id_rank
        FROM raw
    ), validated AS (
        SELECT *,
            ST_X(representative_point) AS longitude,
            ST_Y(representative_point) AS latitude,
            CASE
                WHEN source_id IS NULL OR trim(source_id) = '' THEN 'missing_source_id'
                WHEN source_id_rank > 1 THEN 'duplicate_source_identity'
                WHEN representative_point IS NULL OR NOT ST_IsValid(representative_point)
                  OR ST_X(representative_point) NOT BETWEEN -180 AND 180
                  OR ST_Y(representative_point) NOT BETWEEN -90 AND 90 THEN 'invalid_coordinate'
                WHEN NOT ST_Intersects(representative_point, ST_GeomFromWKB(from_hex({boundary}))) THEN 'outside_market_boundary'
            END AS rejection_reason
        FROM shaped
    )
    SELECT * EXCLUDE (representative_point, source_id_rank),
        CASE WHEN rejection_reason IS NULL THEN 'valid' ELSE 'invalid' END AS coordinate_status,
        rejection_reason IS NULL AS is_within_market_boundary,
        CASE WHEN rejection_reason IS NULL THEN 'retained' ELSE 'rejected' END AS record_status
    FROM validated
    """


def write_query(con: duckdb.DuckDBPyConnection, query: str, path: Path) -> None:
    """Materialize a query as an ignored local Parquet review artifact."""

    path.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY ({query}) TO {sql_literal(str(path))} (FORMAT PARQUET, COMPRESSION ZSTD)")


def main() -> None:
    """Normalize one source run and write retained/rejected/duplicate outputs."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True)
    parser.add_argument("--source-run-dir", type=Path, help="Completed acquisition run directory; defaults to newest market run.")
    parser.add_argument("--output-root", type=Path, default=ENGINE_DIR / "outputs")
    parser.add_argument("--db-path", type=Path)
    args = parser.parse_args()

    source_dir = args.source_run_dir or latest_source_run(args.output_root, args.market)
    run = json.loads((source_dir / "source_run_manifest.json").read_text(encoding="utf-8"))
    source_path = source_dir / "overture_places_source.parquet"
    if not source_path.exists():
        raise FileNotFoundError(f"Missing source cache: {source_path}")
    database = database_path(args.db_path)
    derived_dir = source_dir / "normalized"
    normalized_path = derived_dir / "poi_source_place.parquet"
    rejected_path = derived_dir / "poi_source_place_rejected.parquet"
    duplicate_path = derived_dir / "poi_near_duplicate_candidates.parquet"
    exact_duplicate_path = derived_dir / "poi_exact_duplicate_candidates.parquet"
    manifest_path = derived_dir / "normalization_manifest.json"

    with duckdb.connect(str(database), read_only=True) as con:
        configure_extensions(con, "local.parquet")
        boundary = resolve_boundary(con, str(run["market_id"]))
        query = normalize_sql(source_path, run, boundary["geometry"])
        write_query(con, query + " WHERE record_status = 'retained'", normalized_path)
        write_query(con, query + " WHERE record_status = 'rejected'", rejected_path)
        # A same-name, roughly 11 m grid co-location is a review candidate only,
        # not an entity-resolution rule or a reason to drop either source row.
        duplicate_query = f"""
        WITH places AS ({query})
        SELECT lower(trim(source_name)) AS normalized_name,
            round(longitude, 4) AS longitude_grid, round(latitude, 4) AS latitude_grid,
            count(*) AS candidate_count, list(source_record_key ORDER BY source_record_key) AS source_record_keys
        FROM places
        WHERE record_status = 'retained' AND nullif(trim(source_name), '') IS NOT NULL
        GROUP BY 1, 2, 3 HAVING count(*) > 1
        """
        write_query(con, duplicate_query, duplicate_path)
        exact_duplicate_query = f"""
        WITH places AS ({query})
        SELECT source_system, source_release, source_id, count(*) AS candidate_count,
            list(source_record_key ORDER BY source_record_key) AS source_record_keys
        FROM places
        GROUP BY 1, 2, 3 HAVING count(*) > 1
        """
        write_query(con, exact_duplicate_query, exact_duplicate_path)
        counts = con.execute(f"SELECT record_status, count(*) FROM ({query}) GROUP BY 1").fetchall()
        candidate_groups = con.execute(f"SELECT count(*) FROM ({duplicate_query})").fetchone()[0]
        exact_candidate_groups = con.execute(f"SELECT count(*) FROM ({exact_duplicate_query})").fetchone()[0]

    normalized_counts = {"retained": 0, "rejected": 0}
    normalized_counts.update({status: count for status, count in counts})
    manifest = {
        "source_run_id": run["source_run_id"], "normalization_version": "v1",
        "normalized_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "boundary_vintage": boundary["boundary_vintage"],
        "outputs": {
            "retained": {"uri": str(normalized_path.relative_to(REPO_ROOT)), "sha256": checksum(normalized_path)},
            "rejected": {"uri": str(rejected_path.relative_to(REPO_ROOT)), "sha256": checksum(rejected_path)},
            "exact_duplicate_candidates": {"uri": str(exact_duplicate_path.relative_to(REPO_ROOT)), "sha256": checksum(exact_duplicate_path)},
            "near_duplicate_candidates": {"uri": str(duplicate_path.relative_to(REPO_ROOT)), "sha256": checksum(duplicate_path)},
        },
        "row_counts": normalized_counts,
        "exact_duplicate_candidate_groups": exact_candidate_groups,
        "near_duplicate_candidate_groups": candidate_groups,
        "notes": ["Representative points use ST_PointOnSurface for every source geometry.", "Near-duplicate candidates are not merged."],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"source_run_id": run["source_run_id"], **manifest["row_counts"], "exact_duplicate_candidate_groups": exact_candidate_groups, "near_duplicate_candidate_groups": candidate_groups}, indent=2))


if __name__ == "__main__":
    main()
