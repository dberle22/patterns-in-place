#!/usr/bin/env python3
"""Create a clipped source run of OSM context polygons for one state market.

Usage:
    python metro-deep-dive-program/engines/infrastructure/acquire_osm_context.py --market new_york_state_context --dry-run

Reads the same cached GeoPackage as the core run but writes to its own market
folder, so core artifacts and their consumers cannot change. A matching run is
refused; there is deliberately no overwrite option.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

import duckdb

from acquire_osm_infrastructure import (
    DEFAULT_CONFIG, DEFAULT_OUTPUT_ROOT, REPO_ROOT, configure_spatial, database_path, deterministic_run_id,
    diagnostics, field, prepare_views, read_config, resolve_boundary, resolve_market, scalar_counts, sha256,
    source_columns, sql_literal, write_parquet,
)


def group_sql(columns: set[str]) -> tuple[str, str]:
    """Give each feature one group and raw type, so its identity stays unique.

    OSM features can carry several of these tags. The order is the review
    precedence: a specific facility first, then protected land over a park tag.
    """

    aeroway, amenity = field(columns, "aeroway"), field(columns, "amenity")
    boundary, leisure = field(columns, "boundary"), field(columns, "leisure")
    branches = (
        (f"{aeroway} = 'aerodrome'", "airport", aeroway),
        (f"{amenity} IN ('university', 'college')", "campus", amenity),
        (f"{amenity} = 'hospital'", "hospital", amenity),
        (f"{amenity} = 'prison'", "prison", amenity),
        (f"{amenity} IN ('bus_station', 'bus_depot')", "bus_facility", amenity),
        (f"{boundary} = 'protected_area'", "protected_area", boundary),
        (f"{leisure} IN ('park', 'nature_reserve')", "park", leisure),
    )
    group = "CASE " + " ".join(f"WHEN {test} THEN {sql_literal(name)}" for test, name, _ in branches) + " END"
    source_type = "CASE " + " ".join(f"WHEN {test} THEN {value}" for test, _, value in branches) + " END"
    return group, source_type


def context_source_sql(adapter: Path, columns: set[str]) -> str:
    """Select context polygons in the source shape the core normalizer reads."""

    group, source_type = group_sql(columns)
    # GDAL puts polygon ways in osm_way_id and relations in osm_id, matching the
    # identity rule in the core acquisition.
    identity = f"COALESCE(NULLIF(TRIM({field(columns, 'osm_id')}), ''), 'way:' || NULLIF(TRIM({field(columns, 'osm_way_id')}), ''))"
    # Clipping fails on an invalid polygon. Repair it to polygons only, count it
    # in the manifest, and keep the identity hash of the geometry as supplied.
    repaired = "CASE WHEN ST_IsValid(geometry) THEN geometry ELSE ST_CollectionExtract(ST_MakeValid(geometry), 3) END"
    return f"""(
        SELECT * FROM (
            SELECT
                'multipolygons' AS source_layer,
                {identity} AS source_feature_id,
                {field(columns, 'name')} AS source_name,
                {group} AS source_group,
                {source_type} AS source_type,
                'polygon' AS geometry_type,
                ST_AsWKB({repaired}) AS source_geometry_wkb,
                sha256(hex(ST_AsWKB(geometry))) AS source_geometry_id,
                NOT ST_IsValid(geometry) AS source_geometry_repaired,
                to_json(struct_pack(
                    aeroway := {field(columns, 'aeroway')}, amenity := {field(columns, 'amenity')},
                    boundary := {field(columns, 'boundary')}, leisure := {field(columns, 'leisure')},
                    landuse := {field(columns, 'landuse')}, other_tags := {field(columns, 'other_tags')}
                )) AS source_tags
            FROM ST_Read({sql_literal(str(adapter))}, layer='multipolygons')
        ) WHERE source_group IS NOT NULL
    )"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--db-path", type=Path)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--dry-run", action="store_true", help="Resolve, select, and count without writing files.")
    args = parser.parse_args()

    config = read_config(args.config)
    market_slug, market = resolve_market(config, args.market)
    source_asset, adapter = REPO_ROOT / market["source_asset_path"], REPO_ROOT / market["source_adapter_path"]
    source_checksum, adapter_checksum = sha256(source_asset), sha256(adapter)
    run = deterministic_run_id(str(market["market_id"]), market["source_release"], source_checksum).replace("osm-infrastructure-", "osm-context-")
    run_dir = args.output_root / market_slug / run
    if run_dir.exists() and not args.dry_run:
        raise FileExistsError(f"Run already exists and will not be overwritten: {run_dir}")

    with duckdb.connect(str(database_path(args.db_path)), read_only=True) as con:
        configure_spatial(con)
        boundary = resolve_boundary(con, str(market["market_id"]), market.get("boundary_level", "cbsa"))
        source_sql = context_source_sql(adapter, source_columns(con, adapter, "multipolygons"))
        prepare_views(con, source_sql, boundary, str(market["market_id"]), market["source_release"])
        counts = scalar_counts(con)
        counts["source_geometry_repaired"] = int(con.execute("SELECT count(*) FROM source_features WHERE source_geometry_repaired").fetchone()[0])
        coverage = diagnostics(con)
        if not args.dry_run:
            write_parquet(con, "SELECT * FROM market_features", run_dir / "infrastructure_source_feature.parquet")
            write_parquet(con, "SELECT * FROM market_features WHERE record_status = 'rejected'", run_dir / "infrastructure_rejected_source_feature.parquet")
            manifest = {
                "source_run_id": run, "source_system": config["source_system"], "source_dataset": "context",
                "source_release": market["source_release"], "provider": market["provider"],
                "market_id": str(market["market_id"]), "market_slug": market_slug,
                "boundary": {key: boundary[key] for key in ("market_id", "geo_level", "boundary_vintage", "west", "south", "east", "north", "geometry_role")},
                "source_asset": {
                    "uri": market["source_asset_uri"], "cache_uri": market["source_asset_path"], "sha256": source_checksum,
                    "adapter_uri": market["source_adapter_path"], "adapter_sha256": adapter_checksum,
                },
                "query": {
                    "method": config["query_method"], "groups": sorted({row["feature_group"] for row in coverage}),
                    "market_filter": f"ST_Intersects then ST_Intersection against declared {boundary['geo_level']} geometry",
                },
                "row_counts": counts, "coverage": coverage,
                "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "notes": ["Context polygons only; the core run is not read or changed."],
            }
            (run_dir / "source_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"source_run_id": run, "market": market_slug, "row_counts": counts, "coverage": coverage, "dry_run": args.dry_run}, indent=2))


if __name__ == "__main__":
    main()
