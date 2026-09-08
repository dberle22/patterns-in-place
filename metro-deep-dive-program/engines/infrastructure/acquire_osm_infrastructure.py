#!/usr/bin/env python3
"""Create a source-faithful, clipped OSM infrastructure run for one market.

This is Epic 2 acquisition only. It reads a declared cached OSM GeoPackage,
keeps the source fields needed to reproduce core road, rail, and river/canal
selection, and writes market-clipped candidates plus an immutable manifest.
It intentionally does not publish a normalized serving layer or repair
geometry; those are later epics.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

import duckdb
import yaml


ENGINE_DIR = Path(__file__).resolve().parent
REPO_ROOT = ENGINE_DIR.parents[2]
DEFAULT_CONFIG = ENGINE_DIR / "sources" / "osm_infrastructure.yml"
DEFAULT_OUTPUT_ROOT = ENGINE_DIR / "outputs"
MARKET_NAME = re.compile(r"^[a-z][a-z0-9_]*$")

# The first contract deliberately keeps this vocabulary narrow. Water bodies
# such as ponds and reservoirs stay in the source asset until a consumer needs
# an explicitly governed conditional-context rule.
HIGHWAY_TYPES = ("motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link")
RAIL_TYPES = ("rail", "light_rail", "subway")
WATERWAY_TYPES = ("river", "canal")


def database_path(override: Path | None) -> Path:
    """Resolve the shared DuckDB path without committing a local machine path."""

    if override:
        return override
    configured = os.environ.get("DB_PATH", "").strip()
    if configured:
        return Path(configured).expanduser()
    renviron = REPO_ROOT / ".Renviron"
    if renviron.exists():
        for line in renviron.read_text(encoding="utf-8").splitlines():
            if line.startswith("DB_PATH="):
                return Path(line.split("=", 1)[1].strip().strip('"')).expanduser()
    raise RuntimeError("Set DB_PATH, add it to .Renviron, or pass --db-path.")


def sql_literal(value: str) -> str:
    """Quote a path embedded in DuckDB's table-function syntax."""

    return "'" + value.replace("'", "''") + "'"


def values_sql(values: tuple[str, ...]) -> str:
    """Render a fixed, internal list of source tag values for a SQL IN clause."""

    return ", ".join(sql_literal(value) for value in values)


def sha256(path: Path) -> str:
    """Return a streaming SHA-256 so the manifest identifies exact local bytes."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_config(path: Path) -> dict[str, Any]:
    """Load and minimally validate the checked-in OSM source declaration."""

    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    required = {"source_system", "source_dataset", "query_method", "markets"}
    missing = required - set(config or {})
    if missing:
        raise ValueError(f"Source configuration is missing: {', '.join(sorted(missing))}.")
    if config["source_system"] != "osm" or config["source_dataset"] != "infrastructure":
        raise ValueError("This builder supports only the declared OSM infrastructure source.")
    return config


def resolve_market(config: dict[str, Any], name: str) -> tuple[str, dict[str, Any]]:
    """Return one safely named market declaration with its numeric CBSA identity."""

    if not MARKET_NAME.fullmatch(name):
        raise ValueError(f"Unsafe market name: {name!r}.")
    market = config["markets"].get(name)
    required = {"market_id", "source_release", "provider", "source_asset_uri", "source_asset_path", "source_adapter_path"}
    if not market or required - set(market):
        raise ValueError(f"Market {name!r} is missing a complete OSM source declaration.")
    if not str(market["market_id"]).isdigit():
        raise ValueError(f"Market {name!r} has a non-numeric market_id.")
    return name, market


def configure_spatial(con: duckdb.DuckDBPyConnection) -> None:
    """Load the installed spatial extension; acquisition must not install dependencies."""

    con.execute("LOAD spatial")


def resolve_boundary(con: duckdb.DuckDBPyConnection, market_id: str) -> dict[str, Any]:
    """Resolve the current Geography CBSA identity and its available geometry role."""

    row = con.execute(
        """
        SELECT
            g.cbsa_code,
            i.boundary_vintage,
            ST_XMin(g.geom) AS west,
            ST_YMin(g.geom) AS south,
            ST_XMax(g.geom) AS east,
            ST_YMax(g.geom) AS north,
            ST_AsWKB(g.geom) AS geometry_wkb,
            COALESCE(c.geometry_role, 'legacy_unclassified') AS geometry_role
        FROM geo.cbsas g
        INNER JOIN mart_geography.identity_current i
            ON i.geo_level = 'cbsa' AND i.geo_id = g.cbsa_code
        LEFT JOIN mart_geography.geometry_catalog c
            ON c.geo_level = 'cbsa' AND c.table_name = 'cbsas'
        WHERE g.cbsa_code = ?
        """,
        [market_id],
    ).fetchone()
    if not row:
        raise RuntimeError(f"Geography Engine returned no current CBSA geometry for {market_id}.")
    return {
        "market_id": row[0], "boundary_vintage": int(row[1]),
        "west": row[2], "south": row[3], "east": row[4], "north": row[5],
        "geometry_wkb": row[6], "geometry_role": row[7],
    }


def source_columns(con: duckdb.DuckDBPyConnection, adapter: Path, layer: str) -> set[str]:
    """Return available GeoPackage fields because legacy source schemas differ by market."""

    rows = con.execute(f"DESCRIBE SELECT * FROM ST_Read({sql_literal(str(adapter))}, layer={sql_literal(layer)})").fetchall()
    return {row[0] for row in rows}


def field(columns: set[str], name: str) -> str:
    """Return a safely quoted source field or a typed null for a missing legacy tag."""

    return f'"{name}"' if name in columns else "NULL::VARCHAR"


def core_source_sql(adapter: Path, line_columns: set[str], polygon_columns: set[str]) -> str:
    """Select only the initial contract's source features while retaining raw tags."""

    line_highway = field(line_columns, "highway")
    line_railway = field(line_columns, "railway")
    line_waterway = field(line_columns, "waterway")
    polygon_water = field(polygon_columns, "water")
    polygon_waterway = field(polygon_columns, "waterway")

    def select(layer: str, columns: set[str], group: str, type_sql: str, geometry_type: str, where_sql: str) -> str:
        return f"""
        SELECT
            {sql_literal(layer)} AS source_layer,
            NULLIF(TRIM({field(columns, 'osm_id')}), '') AS source_feature_id,
            {field(columns, 'name')} AS source_name,
            {group} AS source_group,
            {type_sql} AS source_type,
            {sql_literal(geometry_type)} AS geometry_type,
            ST_AsWKB(geometry) AS source_geometry_wkb,
            sha256(hex(ST_AsWKB(geometry))) AS source_geometry_id,
            to_json(struct_pack(
                highway := {field(columns, 'highway')}, railway := {field(columns, 'railway')},
                waterway := {field(columns, 'waterway')}, water := {field(columns, 'water')},
                natural := {field(columns, 'natural')}, bridge := {field(columns, 'bridge')},
                tunnel := {field(columns, 'tunnel')}, layer := {field(columns, 'layer')},
                oneway := {field(columns, 'oneway')}, maxspeed := {field(columns, 'maxspeed')},
                lanes := {field(columns, 'lanes')}, other_tags := {field(columns, 'other_tags')}
            )) AS source_tags
        FROM ST_Read({sql_literal(str(adapter))}, layer={sql_literal(layer)})
        WHERE {where_sql}
        """

    roads = select("lines", line_columns, sql_literal("road"), line_highway, "line", f"{line_highway} IN ({values_sql(HIGHWAY_TYPES)})")
    rail = select("lines", line_columns, sql_literal("rail"), line_railway, "line", f"{line_railway} IN ({values_sql(RAIL_TYPES)})")
    water_lines = select("lines", line_columns, sql_literal("water_network"), line_waterway, "line", f"{line_waterway} IN ({values_sql(WATERWAY_TYPES)})")
    water_surfaces = select(
        "multipolygons", polygon_columns, sql_literal("water_network"),
        f"COALESCE({polygon_water}, {polygon_waterway})",
        "polygon",
        f"{polygon_water} = 'river' OR {polygon_waterway} = 'riverbank'",
    )
    return f"({roads} UNION ALL {rail} UNION ALL {water_lines} UNION ALL {water_surfaces})"


def prepare_views(con: duckdb.DuckDBPyConnection, source_sql: str, boundary: dict[str, Any], market_id: str, release: str) -> None:
    """Create temporary source, bbox, and true-boundary views for one declared run."""

    # DuckDB does not prepare CREATE VIEW statements. Render only values that
    # originated from the trusted Geography query or checked-in configuration.
    boundary_geometry = f"ST_GeomFromWKB(from_hex({sql_literal(boundary['geometry_wkb'].hex())}))"
    envelope = "ST_MakeEnvelope({}, {}, {}, {})".format(
        boundary["west"], boundary["south"], boundary["east"], boundary["north"]
    )
    con.execute(f"CREATE OR REPLACE TEMP VIEW source_features AS SELECT * FROM {source_sql}")
    con.execute(
        f"""
        CREATE OR REPLACE TEMP VIEW bbox_candidates AS
        SELECT *
        FROM source_features
        WHERE ST_Intersects(ST_GeomFromWKB(source_geometry_wkb), {envelope})
        """
    )
    con.execute(
        f"""
        CREATE OR REPLACE TEMP VIEW market_features AS
        SELECT
            {sql_literal(market_id)} AS market_id,
            {sql_literal(release)} AS source_release,
            source_layer,
            source_feature_id,
            source_geometry_id,
            CASE
                WHEN source_feature_id IS NULL THEN NULL
                ELSE concat('osm:', {sql_literal(release)}, ':', source_layer, ':', source_feature_id)
            END AS source_record_key,
            source_name,
            source_group,
            source_type,
            geometry_type,
            source_geometry_wkb,
            ST_AsWKB(ST_Intersection(ST_GeomFromWKB(source_geometry_wkb), {boundary_geometry})) AS geometry_wkb,
            source_tags,
            CASE WHEN source_feature_id IS NULL THEN 'rejected' ELSE 'retained' END AS record_status,
            CASE WHEN source_feature_id IS NULL THEN 'missing_source_identity' ELSE NULL END AS rejection_reason,
            ST_Within(ST_GeomFromWKB(source_geometry_wkb), {boundary_geometry}) AS is_within_market_boundary,
            NOT ST_Within(ST_GeomFromWKB(source_geometry_wkb), {boundary_geometry}) AS was_clipped
        FROM bbox_candidates
        WHERE ST_Intersects(ST_GeomFromWKB(source_geometry_wkb), {boundary_geometry})
        """
    )


def scalar_counts(con: duckdb.DuckDBPyConnection) -> dict[str, int]:
    """Return the run's declared extraction, clipping, and identity accounting."""

    source = con.execute("SELECT COUNT(*) FROM source_features").fetchone()[0]
    bbox = con.execute("SELECT COUNT(*) FROM bbox_candidates").fetchone()[0]
    retained, rejected = con.execute(
        "SELECT COUNT(*) FILTER (WHERE record_status = 'retained'), COUNT(*) FILTER (WHERE record_status = 'rejected') FROM market_features"
    ).fetchone()
    return {
        "source_selector": int(source), "extracted_bbox": int(bbox),
        "retained_market": int(retained), "rejected_market": int(rejected),
        "outside_market_boundary": int(bbox - retained - rejected),
    }


def diagnostics(con: duckdb.DuckDBPyConnection) -> list[dict[str, Any]]:
    """Summarize source-to-clipped coverage without performing unbounded unions."""

    rows = con.execute(
        """
        WITH bbox AS (
            SELECT
                source_group, source_type, geometry_type,
                COUNT(*) AS extracted_bbox_features,
                ROUND(SUM(CASE WHEN source_layer = 'multipolygons' THEN ST_Area(ST_Transform(ST_GeomFromWKB(source_geometry_wkb), 'EPSG:4326', 'EPSG:5070')) ELSE 0 END), 2) AS extracted_bbox_polygon_area_sqm
            FROM bbox_candidates
            GROUP BY 1, 2, 3
        ), market AS (
            SELECT
                source_group, source_type, geometry_type,
                COUNT(*) AS market_features,
                COUNT(*) FILTER (WHERE record_status = 'retained') AS retained_features,
                COUNT(*) FILTER (WHERE record_status = 'rejected') AS rejected_features,
                ROUND(SUM(CASE WHEN source_layer = 'multipolygons' THEN ST_Area(ST_Transform(ST_GeomFromWKB(geometry_wkb), 'EPSG:4326', 'EPSG:5070')) ELSE 0 END), 2) AS clipped_polygon_area_sqm
            FROM market_features
            GROUP BY 1, 2, 3
        )
        SELECT
            market.source_group, market.source_type, market.geometry_type,
            bbox.extracted_bbox_features, market.market_features,
            market.retained_features, market.rejected_features,
            bbox.extracted_bbox_polygon_area_sqm, market.clipped_polygon_area_sqm
        FROM market
        INNER JOIN bbox USING (source_group, source_type, geometry_type)
        ORDER BY 1, 2, 3
        """
    ).fetchall()
    keys = ["feature_group", "feature_type", "geometry_type", "extracted_bbox_features", "market_features", "retained_features", "rejected_features", "extracted_bbox_polygon_area_sqm", "clipped_polygon_area_sqm"]
    return [dict(zip(keys, row)) for row in rows]


def write_parquet(con: duckdb.DuckDBPyConnection, query: str, destination: Path) -> None:
    """Write a scoped local artifact without materializing a managed DuckDB table."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    con.execute(f"COPY ({query}) TO {sql_literal(str(destination))} (FORMAT PARQUET, COMPRESSION ZSTD)")


def deterministic_run_id(market_id: str, release: str, source_checksum: str) -> str:
    """Name a rerunnable run from declared inputs rather than a wall-clock timestamp."""

    release_token = re.sub(r"[^A-Za-z0-9]+", "-", release).strip("-").lower()
    return f"osm-infrastructure-{market_id}-{release_token}-{source_checksum[:12]}"


def main() -> None:
    """Build or inspect one declared local OSM source run."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True, help="Market key from the source declaration.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Checked-in source declaration.")
    parser.add_argument("--db-path", type=Path, help="Override DB_PATH for this invocation.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT, help="Ignored root for local source runs.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve, select, and count without writing files.")
    parser.add_argument("--overwrite", action="store_true", help="Replace a matching deterministic local run after inspection.")
    args = parser.parse_args()

    config = read_config(args.config)
    market_slug, market = resolve_market(config, args.market)
    database = database_path(args.db_path)
    if not database.exists():
        raise FileNotFoundError(f"DuckDB database does not exist: {database}")
    source_asset = REPO_ROOT / market["source_asset_path"]
    adapter = REPO_ROOT / market["source_adapter_path"]
    for path in (source_asset, adapter):
        if not path.exists():
            raise FileNotFoundError(f"Declared cached OSM asset does not exist: {path.relative_to(REPO_ROOT)}")
    source_checksum = sha256(source_asset)
    adapter_checksum = sha256(adapter)
    run = deterministic_run_id(str(market["market_id"]), market["source_release"], source_checksum)
    run_dir = args.output_root / market_slug / run

    with duckdb.connect(str(database), read_only=True) as con:
        configure_spatial(con)
        boundary = resolve_boundary(con, str(market["market_id"]))
        source_sql = core_source_sql(adapter, source_columns(con, adapter, "lines"), source_columns(con, adapter, "multipolygons"))
        prepare_views(con, source_sql, boundary, str(market["market_id"]), market["source_release"])
        counts = scalar_counts(con)
        coverage = diagnostics(con)
        if not args.dry_run:
            if run_dir.exists() and not args.overwrite:
                raise FileExistsError(f"Run already exists: {run_dir}. Use --overwrite only after reviewing it.")
            write_parquet(con, "SELECT * FROM market_features", run_dir / "infrastructure_source_feature.parquet")
            write_parquet(con, "SELECT * FROM market_features WHERE record_status = 'rejected'", run_dir / "infrastructure_rejected_source_feature.parquet")
            manifest = {
                "source_run_id": run,
                "source_system": config["source_system"],
                "source_dataset": config["source_dataset"],
                "source_release": market["source_release"],
                "provider": market["provider"],
                "market_id": str(market["market_id"]),
                "market_slug": market_slug,
                "boundary": {key: boundary[key] for key in ("market_id", "boundary_vintage", "west", "south", "east", "north", "geometry_role")},
                "source_asset": {
                    "uri": market["source_asset_uri"],
                    "cache_uri": str(source_asset.relative_to(REPO_ROOT)),
                    "sha256": source_checksum,
                    "adapter_uri": str(adapter.relative_to(REPO_ROOT)),
                    "adapter_sha256": adapter_checksum,
                },
                "query": {
                    "method": config["query_method"],
                    "core_groups": ["road", "rail", "water_network"],
                    "water_network": {"lines": list(WATERWAY_TYPES), "surfaces": ["water=river", "waterway=riverbank"]},
                    "market_filter": "ST_Intersects then ST_Intersection against declared CBSA geometry",
                },
                "row_counts": counts,
                "coverage": coverage,
                "cache": {
                    "source_feature_uri": str((run_dir / "infrastructure_source_feature.parquet").relative_to(REPO_ROOT)),
                    "rejected_feature_uri": str((run_dir / "infrastructure_rejected_source_feature.parquet").relative_to(REPO_ROOT)),
                },
                "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "notes": [
                    "Epic 2 source acquisition only; mapping, geometry validation, and serving are deferred.",
                    "Rows without a source feature ID are preserved in the rejected audit artifact and cannot enter a serving layer.",
                    "Boundary geometry role is recorded explicitly; replace legacy_unclassified geometry with Geography analytical geometry when materialized.",
                ],
            }
            (run_dir / "source_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"source_run_id": run, "market": market_slug, "market_id": market["market_id"], "geometry_role": boundary["geometry_role"], "row_counts": counts, "coverage": coverage, "dry_run": args.dry_run}, indent=2))


if __name__ == "__main__":
    main()
