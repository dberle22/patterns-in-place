#!/usr/bin/env python3
"""Apply versioned core OSM mappings to one Epic 2 infrastructure source run.

This is Epic 3 normalization only. It preserves the source and clipped
geometry, raw tags, identity, and rejected records from acquisition. Geometry
validity, repair, display generalization, and serving remain later epics.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

import duckdb
import yaml

from acquire_osm_infrastructure import ENGINE_DIR, REPO_ROOT, sql_literal


DEFAULT_OUTPUT_ROOT = ENGINE_DIR / "outputs"
DEFAULT_RULES = ENGINE_DIR / "sources" / "osm_core_mappings_v1.yml"


def checksum(path: Path) -> str:
    """Hash a local artifact so the normalization manifest records exact bytes."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def latest_source_run(output_root: Path, market: str) -> Path:
    """Select the newest completed deterministic acquisition run for one market."""

    runs = sorted(path.parent for path in (output_root / market).glob("*/source_run_manifest.json"))
    if not runs:
        raise FileNotFoundError(f"No completed infrastructure source run found for {market}.")
    return runs[-1]


def read_rules(path: Path) -> dict[str, Any]:
    """Load and validate the small, explicit first-core mapping vocabulary."""

    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    required = {"mapping_version", "rules"}
    if not config or required - set(config):
        raise ValueError("Mapping declaration must contain mapping_version and rules.")
    for rule in config["rules"]:
        needed = {"rule_id", "source_group", "source_types", "source_layer", "feature_group", "feature_form", "review_status", "evidence"}
        if needed - set(rule):
            raise ValueError(f"Mapping rule is incomplete: {rule}")
    return config


def values_sql(values: list[str]) -> str:
    """Render source tag values read from checked-in YAML into a SQL IN clause."""

    return ", ".join(sql_literal(value) for value in values)


def mapping_case(rules: list[dict[str, Any]], output_field: str, default: str = "NULL") -> str:
    """Build one deterministic CASE expression from the versioned rule declaration."""

    clauses = []
    for rule in rules:
        condition = (
            f"source_group = {sql_literal(rule['source_group'])} "
            f"AND source_type IN ({values_sql(rule['source_types'])}) "
            f"AND source_layer = {sql_literal(rule['source_layer'])}"
        )
        value = rule[output_field]
        clauses.append(f"WHEN {condition} THEN {sql_literal(value)}")
    return "CASE " + " ".join(clauses) + f" ELSE {default} END"


def normalized_sql(source_path: Path, run: dict[str, Any], rules: dict[str, Any]) -> str:
    """Shape source-run rows into logical infrastructure features without spatial repair."""

    mapping_rules = rules["rules"]
    rule_id = mapping_case(mapping_rules, "rule_id")
    feature_group = mapping_case(mapping_rules, "feature_group")
    feature_form = mapping_case(mapping_rules, "feature_form")
    review_status = mapping_case(mapping_rules, "review_status")
    evidence = mapping_case(mapping_rules, "evidence")
    return f"""
    WITH source AS (
        SELECT * FROM read_parquet({sql_literal(str(source_path))})
    ), mapped AS (
        SELECT
            'osm' AS source_system,
            source_release,
            source_feature_id,
            source_geometry_id,
            source_record_key,
            source_name,
            source_tags,
            to_json(struct_pack(source_layer := source_layer, source_group := source_group,
                source_type := source_type, source_geometry_id := source_geometry_id)) AS source_attributes,
            {feature_group} AS feature_group,
            source_type AS feature_type,
            {feature_form} AS feature_form,
            {sql_literal(rules['mapping_version'])} AS mapping_version,
            CASE WHEN {rule_id} IS NULL THEN 'unmapped' ELSE 'mapped' END AS mapping_status,
            {rule_id} AS mapping_rule_id,
            {evidence} AS mapping_evidence,
            CASE WHEN {review_status} IS NULL THEN 'needs_review' ELSE {review_status} END AS review_status,
            geometry_wkb AS geometry,
            geometry_type,
            source_geometry_wkb,
            'EPSG:4326' AS source_crs,
            NULL::VARCHAR AS analytical_crs,
            'unvalidated' AS geometry_status,
            market_id,
            'cbsa' AS market_boundary_geo_level,
            {int(run['boundary']['boundary_vintage'])} AS market_boundary_vintage,
            {sql_literal(run['source_run_id'])} AS source_run_id,
            {sql_literal(run['extracted_at'])} AS extracted_at,
            {sql_literal(run['source_asset']['uri'])} AS source_asset_uri,
            {sql_literal(run['source_asset']['sha256'])} AS source_asset_checksum,
            {sql_literal(json.dumps(run['query'], sort_keys=True))} AS source_query,
            record_status,
            rejection_reason,
            is_within_market_boundary,
            was_clipped,
            FALSE AS was_repaired
        FROM source
    )
    SELECT * FROM mapped
    """


def write_query(con: duckdb.DuckDBPyConnection, query: str, destination: Path) -> None:
    """Write one ignored local derived artifact without changing warehouse state."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY ({query}) TO {sql_literal(str(destination))} (FORMAT PARQUET, COMPRESSION ZSTD)")


def main() -> None:
    """Normalize one source run and publish mapping/rejection review artifacts."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True)
    parser.add_argument("--source-run-dir", type=Path, help="Completed acquisition run; defaults to the latest run for --market.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing mapping-version artifact after review.")
    args = parser.parse_args()

    source_dir = args.source_run_dir or latest_source_run(args.output_root, args.market)
    run = json.loads((source_dir / "source_run_manifest.json").read_text(encoding="utf-8"))
    source_path = source_dir / "infrastructure_source_feature.parquet"
    if not source_path.exists():
        raise FileNotFoundError(f"Missing acquired source artifact: {source_path}")
    rules = read_rules(args.rules)
    normalized_dir = source_dir / "normalized" / rules["mapping_version"]
    manifest_path = normalized_dir / "normalization_manifest.json"
    if manifest_path.exists() and not args.overwrite:
        raise FileExistsError(f"Mapping output already exists: {normalized_dir}. Use --overwrite only after review.")

    feature_path = normalized_dir / "infrastructure_feature.parquet"
    rejected_path = normalized_dir / "infrastructure_rejected_feature.parquet"
    unmapped_path = normalized_dir / "infrastructure_unmapped_feature.parquet"
    ambiguous_path = normalized_dir / "infrastructure_ambiguous_feature.parquet"
    query = normalized_sql(source_path, run, rules)
    with duckdb.connect() as con:
        write_query(con, f"SELECT * FROM ({query}) WHERE record_status = 'retained'", feature_path)
        write_query(con, f"SELECT * FROM ({query}) WHERE record_status = 'rejected'", rejected_path)
        write_query(con, f"SELECT * FROM ({query}) WHERE record_status = 'retained' AND mapping_status = 'unmapped'", unmapped_path)
        # v1 has no overlapping rules; retain an explicit empty review surface
        # so later ambiguous rules do not change the consumer artifact shape.
        write_query(con, f"SELECT * FROM ({query}) WHERE FALSE", ambiguous_path)
        counts = dict(con.execute(f"SELECT record_status, count(*) FROM ({query}) GROUP BY 1").fetchall())
        mappings = dict(con.execute(f"SELECT mapping_status, count(*) FROM ({query}) WHERE record_status = 'retained' GROUP BY 1").fetchall())

    # Keep the manifest schema stable across markets: an absent status means zero,
    # not an unknown count. This makes cross-market QA comparisons straightforward.
    counts = {status: counts.get(status, 0) for status in ("retained", "rejected")}
    mappings = {status: mappings.get(status, 0) for status in ("mapped", "unmapped", "ambiguous")}

    manifest = {
        "source_run_id": run["source_run_id"],
        "mapping_version": rules["mapping_version"],
        "mapping_rules_sha256": checksum(args.rules),
        "normalized_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "boundary_vintage": run["boundary"]["boundary_vintage"],
        "boundary_geometry_role": run["boundary"]["geometry_role"],
        "row_counts": counts,
        "mapping_counts": mappings,
        "outputs": {
            "features": {"uri": str(feature_path.relative_to(REPO_ROOT)), "sha256": checksum(feature_path)},
            "rejected": {"uri": str(rejected_path.relative_to(REPO_ROOT)), "sha256": checksum(rejected_path)},
            "unmapped": {"uri": str(unmapped_path.relative_to(REPO_ROOT)), "sha256": checksum(unmapped_path)},
            "ambiguous": {"uri": str(ambiguous_path.relative_to(REPO_ROOT)), "sha256": checksum(ambiguous_path)},
        },
        "notes": [
            "Epic 3 mapping output only; geometry_status is unvalidated until Epic 4.",
            "Unmapped retained features remain in the feature artifact and are also written to the unmapped review artifact.",
            "No airport, port, warehouse/logistics, industrial, access, barrier, routing, or corridor classification is produced.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"source_run_id": run["source_run_id"], "mapping_version": rules["mapping_version"], "row_counts": counts, "mapping_counts": mappings}, indent=2))


if __name__ == "__main__":
    main()
