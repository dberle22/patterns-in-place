#!/usr/bin/env python3
"""Validate and publish an Epic 4 serving artifact for one normalized OSM run.

The script keeps source WGS84 geometry for interchange, declares a local UTM
analytical CRS for each first-slice market, and writes only valid line/polygon
records to the serving artifact. It creates QA JSON and a deliberately small
SVG review map; it does not simplify or dissolve analytical features.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any

import duckdb

from acquire_osm_infrastructure import ENGINE_DIR, REPO_ROOT, sql_literal
from normalize_osm_infrastructure import latest_source_run


DEFAULT_OUTPUT_ROOT = ENGINE_DIR / "outputs"
MAPPING_VERSION = "osm_core_v1"
# NAD83 UTM provides local metric measurements without promising one national
# projection. Additional markets must declare their CRS before serving.
ANALYTICAL_CRS = {"richmond_va": "EPSG:26918", "jacksonville_fl": "EPSG:26917"}


def checksum(path: Path) -> str:
    """Hash a written artifact so the serving manifest identifies exact bytes."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_query(con: duckdb.DuckDBPyConnection, query: str, destination: Path) -> None:
    """Write a scoped local Parquet artifact without touching managed tables."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY ({query}) TO {sql_literal(str(destination))} (FORMAT PARQUET, COMPRESSION ZSTD)")


def validated_sql(feature_path: Path, rejected_path: Path, analytical_crs: str) -> str:
    """Apply the documented type/empty/validity/repair/rejection gate once."""

    return f"""
    WITH input_rows AS (
        SELECT * FROM read_parquet({sql_literal(str(feature_path))})
        UNION ALL BY NAME
        SELECT * FROM read_parquet({sql_literal(str(rejected_path))})
    ), typed AS (
        SELECT *, ST_GeomFromWKB(geometry) AS geom,
            CASE WHEN feature_form = 'linear' THEN ARRAY['LINESTRING', 'MULTILINESTRING']
                 WHEN feature_form = 'surface' THEN ARRAY['POLYGON', 'MULTIPOLYGON']
                 ELSE ARRAY[]::VARCHAR[] END AS allowed_types,
            row_number() OVER (PARTITION BY source_record_key ORDER BY source_geometry_id) AS identity_rank
        FROM input_rows
    ), assessed AS (
        SELECT *,
            CASE WHEN geom IS NULL OR ST_IsEmpty(geom) THEN NULL
                 WHEN ST_IsValid(geom) THEN geom
                 ELSE ST_MakeValid(geom) END AS candidate_geom,
            geom IS NOT NULL AND NOT ST_IsEmpty(geom) AND NOT ST_IsValid(geom) AS needs_repair
        FROM typed
    ), decided AS (
        SELECT *,
            CASE
                WHEN record_status = 'rejected' THEN rejection_reason
                WHEN source_record_key IS NULL OR identity_rank > 1 THEN 'duplicate_source_identity'
                WHEN candidate_geom IS NULL OR ST_IsEmpty(candidate_geom) THEN 'invalid_geometry'
                WHEN needs_repair AND NOT (ST_GeometryType(candidate_geom) = ANY(allowed_types)) THEN 'invalid_geometry'
                WHEN NOT (ST_GeometryType(candidate_geom) = ANY(allowed_types)) THEN 'unsupported_geometry'
                WHEN NOT ST_IsValid(candidate_geom) THEN 'invalid_geometry'
                ELSE NULL
            END AS validation_rejection_reason
        FROM assessed
    )
    SELECT
        * EXCLUDE (geom, allowed_types, identity_rank, candidate_geom, needs_repair, validation_rejection_reason,
            geometry, analytical_crs, geometry_status, record_status, rejection_reason, was_repaired, geometry_type),
        -- Cast extension WKB and the source BLOB to one portable Parquet type.
        CASE WHEN validation_rejection_reason IS NULL THEN CAST(ST_AsWKB(candidate_geom) AS BLOB)
             ELSE CAST(geometry AS BLOB) END AS geometry,
        {sql_literal(analytical_crs)} AS analytical_crs,
        CASE WHEN validation_rejection_reason IS NULL AND needs_repair THEN 'repaired_valid'
             WHEN validation_rejection_reason IS NULL THEN 'valid'
             ELSE 'rejected' END AS geometry_status,
        CASE WHEN validation_rejection_reason IS NULL THEN 'retained' ELSE 'rejected' END AS record_status,
        validation_rejection_reason AS rejection_reason,
        validation_rejection_reason IS NULL AND needs_repair AS was_repaired,
        CASE WHEN validation_rejection_reason IS NULL THEN CAST(ST_GeometryType(candidate_geom) AS VARCHAR)
             ELSE CAST(geometry_type AS VARCHAR) END AS geometry_type
    FROM decided
    """


def qa_summary(con: duckdb.DuckDBPyConnection, query: str, analytical_crs: str) -> dict[str, Any]:
    """Build reviewable counts and water complexity metrics without any dissolve."""

    def rows(sql: str, fields: list[str]) -> list[dict[str, Any]]:
        return [dict(zip(fields, row)) for row in con.execute(sql).fetchall()]

    counts = rows(
        f"SELECT record_status, geometry_status, COALESCE(rejection_reason, 'none') AS rejection_reason, COUNT(*) AS features FROM ({query}) GROUP BY 1,2,3 ORDER BY 1,2,3",
        ["record_status", "geometry_status", "rejection_reason", "features"],
    )
    feature_counts = rows(
        f"SELECT feature_group, feature_type, feature_form, geometry_type, record_status, COUNT(*) AS features FROM ({query}) GROUP BY 1,2,3,4,5 ORDER BY 1,2,3,4,5",
        ["feature_group", "feature_type", "feature_form", "geometry_type", "record_status", "features"],
    )
    mapping = rows(
        f"SELECT mapping_status, COALESCE(mapping_rule_id, 'none') AS mapping_rule_id, COUNT(*) AS features FROM ({query}) GROUP BY 1,2 ORDER BY 1,2",
        ["mapping_status", "mapping_rule_id", "features"],
    )
    unmapped_tags = rows(
        f"SELECT source_tags, COUNT(*) AS features FROM ({query}) WHERE record_status = 'retained' AND mapping_status = 'unmapped' GROUP BY 1 ORDER BY 2 DESC, 1 LIMIT 50",
        ["source_tags", "features"],
    )
    water = rows(
        f"""
        SELECT feature_type, feature_form, geometry_type, COUNT(*) AS features,
            ROUND(SUM(CASE WHEN feature_form = 'surface' THEN ST_Area(ST_Transform(ST_GeomFromWKB(geometry), 'EPSG:4326', {sql_literal(analytical_crs)})) ELSE 0 END), 2) AS area_sqm,
            ROUND(AVG(ST_NPoints(ST_GeomFromWKB(geometry))), 2) AS avg_vertices,
            MAX(ST_NPoints(ST_GeomFromWKB(geometry))) AS max_vertices
        FROM ({query})
        WHERE record_status = 'retained' AND feature_group = 'water_network'
        GROUP BY 1,2,3 ORDER BY 1,2,3
        """,
        ["feature_type", "feature_form", "geometry_type", "features", "area_sqm", "avg_vertices", "max_vertices"],
    )
    return {
        "geometry_validation": counts,
        "feature_counts": feature_counts,
        "mapping_counts": mapping,
        "unmapped_tag_summary": unmapped_tags,
        "water_profile": water,
        "display_derivative": "not_created: no named consumer has requested a scale-specific derivative",
    }


def coordinates(geometry: dict[str, Any]) -> list[list[tuple[float, float]]]:
    """Flatten a GeoJSON line or polygon into SVG-ready coordinate paths."""

    kind, value = geometry["type"], geometry["coordinates"]
    if kind == "LineString":
        return [[tuple(point) for point in value]]
    if kind == "MultiLineString":
        return [[tuple(point) for point in line] for line in value]
    if kind == "Polygon":
        return [[tuple(point) for point in ring] for ring in value]
    if kind == "MultiPolygon":
        return [[tuple(point) for point in ring] for polygon in value for ring in polygon]
    return []


def write_review_svg(con: duckdb.DuckDBPyConnection, query: str, destination: Path) -> int:
    """Create a bounded, map-ready review sample; it is never a serving layer."""

    rows = con.execute(
        f"""
        WITH sample AS (
            SELECT *, row_number() OVER (PARTITION BY feature_group, feature_type, feature_form ORDER BY source_record_key) AS sample_rank
            FROM ({query}) WHERE record_status = 'retained'
        )
        SELECT feature_group, feature_form,
            ST_AsGeoJSON(ST_SimplifyPreserveTopology(ST_GeomFromWKB(geometry), 0.0001)) AS geojson
        FROM sample WHERE sample_rank <= 500
        """
    ).fetchall()
    paths: list[tuple[str, list[list[tuple[float, float]]]]] = []
    points = []
    for group, form, encoded in rows:
        for path in coordinates(json.loads(encoded)):
            points.extend(path)
            paths.append(("water" if group == "water_network" else "rail" if group == "rail" else "road", [path]))
    if not points:
        raise RuntimeError("No retained geometries available for the review map.")
    west, east = min(x for x, _ in points), max(x for x, _ in points)
    south, north = min(y for _, y in points), max(y for _, y in points)
    width, height, padding = 900, 600, 20
    scale = min((width - 2 * padding) / (east - west), (height - 2 * padding) / (north - south))

    def xy(point: tuple[float, float]) -> str:
        return f"{padding + (point[0] - west) * scale:.1f},{height - padding - (point[1] - south) * scale:.1f}"

    colors = {"road": "#777777", "rail": "#8b3a3a", "water": "#2787b8"}
    fragments = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="#fbfbf8"/>']
    for kind, parts in paths:
        for part in parts:
            if len(part) > 1:
                fragments.append(f'<polyline points="{" ".join(xy(point) for point in part)}" fill="none" stroke="{colors[kind]}" stroke-width="0.6" opacity="0.7"/>')
    fragments.append(f'<text x="20" y="24" font-family="sans-serif" font-size="14">Infrastructure QA review sample ({len(rows)} features; max 500 per group/type/form)</text></svg>')
    destination.write_text("".join(fragments), encoding="utf-8")
    return len(rows)


def main() -> None:
    """Validate one normalized run and write serving plus QA artifacts."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True, choices=sorted(ANALYTICAL_CRS))
    parser.add_argument("--source-run-dir", type=Path, help="Completed source run; defaults to latest for --market.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing Epic 4 artifact after review.")
    args = parser.parse_args()

    source_dir = args.source_run_dir or latest_source_run(args.output_root, args.market)
    source_manifest = json.loads((source_dir / "source_run_manifest.json").read_text(encoding="utf-8"))
    normalized_dir = source_dir / "normalized" / MAPPING_VERSION
    feature_path = normalized_dir / "infrastructure_feature.parquet"
    rejected_path = normalized_dir / "infrastructure_rejected_feature.parquet"
    if not feature_path.exists() or not rejected_path.exists():
        raise FileNotFoundError("Epic 3 feature and rejected artifacts are required before validation.")
    output_dir = source_dir / "validated" / MAPPING_VERSION
    manifest_path = output_dir / "validation_manifest.json"
    if manifest_path.exists() and not args.overwrite:
        raise FileExistsError(f"Validated artifact already exists: {output_dir}. Use --overwrite after review.")

    serving_path = output_dir / "infrastructure_feature.parquet"
    rejected_output = output_dir / "infrastructure_rejected_feature.parquet"
    qa_path = output_dir / "qa_summary.json"
    map_path = output_dir / "review_map.svg"
    query = validated_sql(feature_path, rejected_path, ANALYTICAL_CRS[args.market])
    with duckdb.connect() as con:
        con.execute("LOAD spatial")
        write_query(con, f"SELECT * FROM ({query}) WHERE record_status = 'retained'", serving_path)
        write_query(con, f"SELECT * FROM ({query}) WHERE record_status = 'rejected'", rejected_output)
        summary = qa_summary(con, query, ANALYTICAL_CRS[args.market])
        # The source run already measured governed-boundary coverage during
        # clipping; carry it into the serving QA surface rather than recompute
        # a market-wide union of features or boundary geometry.
        summary["source_coverage"] = source_manifest["coverage"]
        map_features = write_review_svg(con, query, map_path)
    qa_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "source_run_id": source_manifest["source_run_id"],
        "mapping_version": MAPPING_VERSION,
        "validated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "analytical_crs": ANALYTICAL_CRS[args.market],
        "outputs": {name: {"uri": str(path.relative_to(REPO_ROOT)), "sha256": checksum(path)} for name, path in {"features": serving_path, "rejected": rejected_output, "qa_summary": qa_path, "review_map": map_path}.items()},
        "review_map_features": map_features,
        "notes": ["Geometry validation and deterministic ST_MakeValid repair only; no display simplification or dissolve derivative is published.", "The SVG is a bounded qualitative review sample and does not replace analytical geometry."],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"market": args.market, "analytical_crs": ANALYTICAL_CRS[args.market], "qa": summary, "review_map_features": map_features}, indent=2))


if __name__ == "__main__":
    main()
