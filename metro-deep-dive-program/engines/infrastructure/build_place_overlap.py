#!/usr/bin/env python3
"""Materialize Census Place overlap evidence for retained infrastructure features.

The output is a physical-context interface: it clips each retained line or
polygon to governed Census Place analytical geometry and records the measured
portion.  It deliberately does not assign points, infer access or barriers, or
combine line length with polygon area into a score.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

import duckdb

from acquire_osm_infrastructure import ENGINE_DIR, database_path, sql_literal
from normalize_osm_infrastructure import latest_source_run


REPO_ROOT = ENGINE_DIR.parents[2]
DEFAULT_OUTPUT_ROOT = ENGINE_DIR / "outputs"
MAPPING_VERSION = "osm_core_v1"
METHOD_VERSION = "infrastructure_place_overlap_v1"
# Measurements are in metres or square metres. This absorbs only spatial-engine
# floating-point noise; it is not a materiality threshold.
MEASURE_TOLERANCE = 0.01


def checksum(path: Path) -> str:
    """Return a streaming checksum for manifest-level output provenance."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_query(con: duckdb.DuckDBPyConnection, query: str, destination: Path) -> None:
    """Write one query as a portable Parquet artifact without a managed-table write."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY ({query}) TO {sql_literal(str(destination))} (FORMAT PARQUET, COMPRESSION ZSTD)")


def required_place_metadata(con: duckdb.DuckDBPyConnection) -> dict[str, str]:
    """Gate the build on Geography's governed analytical Place geometry."""

    columns = {row[0] for row in con.execute("DESCRIBE geo.places_analysis").fetchall()}
    required = {"place_geoid", "boundary_vintage", "geometry_role", "interchange_crs", "analytical_crs", "geom"}
    missing = sorted(required - columns)
    if missing:
        raise RuntimeError(f"geo.places_analysis is missing required fields: {', '.join(missing)}")
    rows = con.execute(
        """
        SELECT geometry_role, interchange_crs, analytical_crs
        FROM geo.places_analysis
        GROUP BY 1, 2, 3
        """
    ).fetchall()
    if len(rows) != 1 or rows[0][0] != "analysis" or not rows[0][2]:
        raise RuntimeError("geo.places_analysis must expose one declared analytical geometry role and CRS.")
    if "places_analysis_qa" not in {row[0] for row in con.execute("SHOW TABLES FROM geo").fetchall()}:
        raise RuntimeError("geo.places_analysis_qa is required before Infrastructure can publish Place overlaps.")
    failures = con.execute("SELECT check_name FROM geo.places_analysis_qa WHERE check_status != 'pass'").fetchall()
    if failures:
        raise RuntimeError("geo.places_analysis QA has failed checks: " + ", ".join(row[0] for row in failures))
    return {"geometry_role": rows[0][0], "interchange_crs": rows[0][1], "analytical_crs": rows[0][2]}


def overlap_sql(feature_path: Path, market_id: str, measurement_crs: str) -> str:
    """Build positive-measure line and polygon intersections in Place's declared CRS."""

    feature_literal = sql_literal(str(feature_path))
    crs_literal = sql_literal(measurement_crs)
    # A Place joins the run only when it intersects the retained, governed-CBSA
    # feature footprint. This is a geometric coverage scope, not a claim that
    # Place/CBSA membership is exclusive or an administrative allocation.
    return f"""
    WITH retained_features AS (
        SELECT *, ST_Transform(ST_GeomFromWKB(geometry), source_crs, {crs_literal}, true) AS feature_geom
        FROM read_parquet({feature_literal})
        WHERE record_status = 'retained' AND market_id = {sql_literal(market_id)}
    ), place_scope AS (
        SELECT p.*, ST_Transform(p.geom, p.interchange_crs, {crs_literal}, true) AS place_geom
        FROM geo.places_analysis p
        WHERE EXISTS (
            SELECT 1 FROM retained_features f
            WHERE ST_Intersects(f.feature_geom, ST_Transform(p.geom, p.interchange_crs, {crs_literal}, true))
        )
    ), intersections AS (
        SELECT
            f.source_system, f.source_release, f.source_feature_id, f.source_geometry_id, f.source_record_key,
            f.source_name, f.source_tags, f.source_attributes,
            f.feature_group, f.feature_type, f.feature_form, f.mapping_version, f.mapping_status,
            f.mapping_rule_id, f.mapping_evidence, f.review_status,
            f.source_crs, f.analytical_crs AS source_analytical_crs,
            f.market_id, f.market_boundary_geo_level, f.market_boundary_vintage,
            f.source_run_id, f.extracted_at, f.source_asset_uri, f.source_asset_checksum, f.source_query,
            f.geometry_status, f.record_status, f.was_clipped, f.was_repaired,
            p.place_geoid, p.place_name, p.place_name_long, p.state_fips, p.state_abbr,
            p.boundary_vintage AS place_boundary_vintage,
            p.geometry_authority AS place_geometry_authority,
            p.interchange_crs AS place_interchange_crs,
            ST_Intersection(f.feature_geom, p.place_geom) AS overlap_geom
        FROM retained_features f
        INNER JOIN place_scope p ON ST_Intersects(f.feature_geom, p.place_geom)
    ), measured AS (
        SELECT *,
            CASE WHEN feature_form = 'linear' THEN ST_Length(overlap_geom) ELSE NULL END AS overlap_length_m,
            CASE WHEN feature_form = 'surface' THEN ST_Area(overlap_geom) ELSE NULL END AS overlap_area_sqm
        FROM intersections
    )
    SELECT
        * EXCLUDE (overlap_geom),
        CAST(ST_AsWKB(overlap_geom) AS BLOB) AS overlap_geometry,
        {crs_literal} AS measurement_crs,
        {sql_literal(METHOD_VERSION)} AS measurement_method,
        CASE WHEN feature_form = 'linear' THEN 'length_m' ELSE 'area_sqm' END AS measurement_unit,
        CASE WHEN feature_form = 'linear' THEN overlap_length_m ELSE overlap_area_sqm END AS overlap_measure
    FROM measured
    WHERE (feature_form = 'linear' AND overlap_length_m > {MEASURE_TOLERANCE})
       OR (feature_form = 'surface' AND overlap_area_sqm > {MEASURE_TOLERANCE})
    """


def summary_sql(overlap_path: Path) -> str:
    """Keep line and surface totals in distinct typed columns for consumers."""

    return f"""
    SELECT
        source_run_id, market_id, market_boundary_vintage,
        place_geoid, place_name, place_name_long, state_fips, state_abbr, place_boundary_vintage,
        feature_group, feature_type, feature_form,
        measurement_crs, measurement_method,
        COUNT(*) AS overlapping_feature_count,
        SUM(overlap_length_m) AS overlap_length_m,
        SUM(overlap_area_sqm) AS overlap_area_sqm
    FROM read_parquet({sql_literal(str(overlap_path))})
    GROUP BY ALL
    ORDER BY place_geoid, feature_group, feature_type, feature_form
    """


def qa_summary(con: duckdb.DuckDBPyConnection, feature_path: Path, overlap_path: Path, market_id: str, measurement_crs: str) -> dict[str, Any]:
    """Produce coverage, identity, validity, and clipped-geometry accounting QA."""

    feature_literal = sql_literal(str(feature_path))
    overlap_literal = sql_literal(str(overlap_path))
    crs_literal = sql_literal(measurement_crs)
    feature_count = con.execute(
        f"SELECT count(*) FROM read_parquet({feature_literal}) WHERE record_status = 'retained' AND market_id = {sql_literal(market_id)}"
    ).fetchone()[0]
    overlap_count = con.execute(f"SELECT count(*) FROM read_parquet({overlap_literal})").fetchone()[0]
    duplicate_count = con.execute(
        f"""SELECT count(*) FROM (
            SELECT source_run_id, source_record_key, place_geoid, place_boundary_vintage, count(*) AS rows
            FROM read_parquet({overlap_literal}) GROUP BY ALL HAVING count(*) > 1
        )"""
    ).fetchone()[0]
    invalid_overlap_count = con.execute(
        f"SELECT count(*) FROM read_parquet({overlap_literal}) WHERE NOT ST_IsValid(ST_GeomFromWKB(overlap_geometry))"
    ).fetchone()[0]
    coverage = con.execute(
        f"""
        WITH features AS (
            SELECT source_record_key,
                   ST_Transform(ST_GeomFromWKB(geometry), source_crs, {crs_literal}, true) AS geom
            FROM read_parquet({feature_literal})
            WHERE record_status = 'retained' AND market_id = {sql_literal(market_id)}
        ), scoped_places AS (
            SELECT place_geoid, boundary_vintage,
                   ST_Transform(geom, interchange_crs, {crs_literal}, true) AS geom
            FROM geo.places_analysis
            WHERE EXISTS (SELECT 1 FROM features f WHERE ST_Intersects(f.geom, ST_Transform(geo.places_analysis.geom, interchange_crs, {crs_literal}, true)))
        ), overlap_features AS (
            SELECT DISTINCT source_record_key FROM read_parquet({overlap_literal})
        ), overlap_places AS (
            SELECT DISTINCT place_geoid, place_boundary_vintage FROM read_parquet({overlap_literal})
        )
        SELECT
            (SELECT count(*) FROM scoped_places),
            (SELECT count(*) FROM overlap_places),
            (SELECT count(*) FROM features),
            (SELECT count(*) FROM overlap_features)
        """
    ).fetchone()
    reconciliation = con.execute(
        f"""
        WITH source_measures AS (
            SELECT source_record_key, feature_form,
                CASE WHEN feature_form = 'linear' THEN ST_Length(ST_Transform(ST_GeomFromWKB(geometry), source_crs, {crs_literal}, true)) END AS source_length_m,
                CASE WHEN feature_form = 'surface' THEN ST_Area(ST_Transform(ST_GeomFromWKB(geometry), source_crs, {crs_literal}, true)) END AS source_area_sqm
            FROM read_parquet({feature_literal})
            WHERE record_status = 'retained' AND market_id = {sql_literal(market_id)}
        ), clipped AS (
            SELECT source_record_key, feature_form, ST_Union_Agg(ST_GeomFromWKB(overlap_geometry)) AS geom
            FROM read_parquet({overlap_literal}) GROUP BY 1, 2
        ), compared AS (
            SELECT s.source_record_key, s.feature_form,
                CASE WHEN s.feature_form = 'linear' THEN s.source_length_m - ST_Length(c.geom)
                     ELSE s.source_area_sqm - ST_Area(c.geom) END AS unallocated_measure
            FROM source_measures s INNER JOIN clipped c USING (source_record_key, feature_form)
        )
        SELECT count(*), COALESCE(max(unallocated_measure), 0),
               COALESCE(max(-unallocated_measure), 0),
               count_if(unallocated_measure < -{MEASURE_TOLERANCE})
        FROM compared
        """
    ).fetchone()
    return {
        "method_version": METHOD_VERSION,
        "measurement_crs": measurement_crs,
        "measurement_tolerance": MEASURE_TOLERANCE,
        "geometry_validity": {"overlap_invalid_geometries": invalid_overlap_count, "status": "pass" if invalid_overlap_count == 0 else "fail"},
        "overlap_rows": overlap_count,
        "duplicate_overlap_keys": duplicate_count,
        "coverage": {
            "scoped_places": coverage[0], "places_with_measurable_overlap": coverage[1],
            "retained_features": feature_count, "features_with_measurable_overlap": coverage[3],
            "places_without_measurable_overlap": coverage[0] - coverage[1],
            "features_without_measurable_overlap": feature_count - coverage[3],
            "zero_rows_are_not_materialized": True,
        },
        "reconciliation": {
            "overlapping_features_compared": reconciliation[0],
            "max_unallocated_measure": reconciliation[1],
            "max_excess_measure": reconciliation[2],
            "features_exceeding_tolerance": reconciliation[3],
            "status": "pass" if reconciliation[3] == 0 else "fail",
            "method": "union each feature's Place-clipped portions before comparing them to its retained source geometry; unallocated portions remain valid coverage evidence",
        },
    }


def main() -> None:
    """Build a market-scoped Place overlap interface from validated features."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True)
    parser.add_argument("--db-path", type=Path, help="Shared DuckDB containing geo.places_analysis.")
    parser.add_argument("--source-run-dir", type=Path, help="Completed source run; defaults to latest for --market.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing local overlap artifact after review.")
    args = parser.parse_args()

    source_dir = args.source_run_dir or latest_source_run(args.output_root, args.market)
    source_manifest = json.loads((source_dir / "source_run_manifest.json").read_text(encoding="utf-8"))
    feature_path = source_dir / "validated" / MAPPING_VERSION / "infrastructure_feature.parquet"
    if not feature_path.exists():
        raise FileNotFoundError("Validated retained infrastructure features are required before Place overlap.")
    output_dir = source_dir / "place_overlap" / METHOD_VERSION
    overlap_path = output_dir / "infrastructure_feature_place_overlap.parquet"
    summary_path = output_dir / "infrastructure_place_summary.parquet"
    qa_path = output_dir / "place_overlap_qa.json"
    manifest_path = output_dir / "place_overlap_manifest.json"
    if manifest_path.exists() and not args.overwrite:
        raise FileExistsError(f"Place overlap artifact already exists: {output_dir}. Use --overwrite after review.")

    with duckdb.connect(str(database_path(args.db_path)), read_only=True) as con:
        con.execute("LOAD spatial")
        place_metadata = required_place_metadata(con)
        query = overlap_sql(feature_path, str(source_manifest["market_id"]), place_metadata["analytical_crs"])
        write_query(con, query, overlap_path)
        write_query(con, summary_sql(overlap_path), summary_path)
        qa = qa_summary(con, feature_path, overlap_path, str(source_manifest["market_id"]), place_metadata["analytical_crs"])
    if qa["geometry_validity"]["status"] != "pass" or qa["duplicate_overlap_keys"] or qa["reconciliation"]["status"] != "pass":
        raise RuntimeError("Place overlap QA failed; local artifacts remain for review but are not published as a completed handoff.")
    qa_path.write_text(json.dumps(qa, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "method_version": METHOD_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_run_id": source_manifest["source_run_id"],
        "market_id": source_manifest["market_id"],
        "place_geometry": place_metadata,
        "outputs": {name: {"uri": str(path.relative_to(REPO_ROOT)), "sha256": checksum(path)} for name, path in {"feature_overlap": overlap_path, "place_summary": summary_path, "qa": qa_path}.items()},
        "limitations": [
            "Physical context only; this interface does not identify barriers, connectivity, travel time, access, or anchor status.",
            "Line length and polygon area remain separate measures and are never combined into an infrastructure-present score.",
            "No-overlap cases are reported through coverage QA and are not represented as fabricated zero rows.",
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"market": args.market, "source_run_id": source_manifest["source_run_id"], "outputs": manifest["outputs"], "qa": qa}, indent=2))


if __name__ == "__main__":
    main()
