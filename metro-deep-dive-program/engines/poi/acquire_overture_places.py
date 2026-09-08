#!/usr/bin/env python3
"""Acquire a source-faithful, governed Overture Places cache for one market.

Usage:
    python3 metro-deep-dive-program/engines/poi/acquire_overture_places.py --market richmond_va

The script resolves the CBSA through Geography-owned county relationships and
tract geometry, uses its bbox only to reduce the remote scan, then retains
records intersecting the true governed market boundary. It intentionally does
not normalize records or classify taxonomy; those are later POI Engine epics.
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
DEFAULT_CONFIG = ENGINE_DIR / "sources" / "overture_places.yml"
DEFAULT_OUTPUT_ROOT = ENGINE_DIR / "outputs"
IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")


def database_path(override: Path | None) -> Path:
    """Resolve the shared DuckDB location without committing a local path."""

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
    """Quote a value that must be embedded in a DuckDB COPY or parquet call."""

    return "'" + value.replace("'", "''") + "'"


def read_config(path: Path) -> dict[str, Any]:
    """Load and minimally validate the checked-in source declaration."""

    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    required = {"source_system", "source_dataset", "source_release", "source_path", "query_method", "markets"}
    missing = required - set(config or {})
    if missing:
        raise ValueError(f"Source configuration is missing: {', '.join(sorted(missing))}.")
    if config["source_system"] != "overture" or config["source_dataset"] != "places":
        raise ValueError("This acquisition script supports only the declared Overture Places source.")
    return config


def resolve_market(config: dict[str, Any], market_name: str) -> tuple[str, str]:
    """Return the declared market slug and CBSA identifier after safe validation."""

    market = config["markets"].get(market_name)
    if not market or not str(market.get("market_id", "")).isdigit():
        raise ValueError(f"Market {market_name!r} is not declared with a numeric market_id.")
    if not IDENTIFIER.fullmatch(market_name):
        raise ValueError(f"Unsafe market name: {market_name!r}.")
    return market_name, str(market["market_id"])


def configure_extensions(con: duckdb.DuckDBPyConnection, source_path: str) -> None:
    """Load only the spatial and remote-file helpers required by this source."""

    try:
        con.execute("LOAD spatial")
    except duckdb.IOException:
        con.execute("INSTALL spatial")
        con.execute("LOAD spatial")
    if source_path.startswith(("s3://", "http://", "https://")):
        try:
            con.execute("LOAD httpfs")
        except duckdb.IOException:
            con.execute("INSTALL httpfs")
            con.execute("LOAD httpfs")
        if source_path.startswith("s3://"):
            con.execute("SET s3_region = 'us-west-2'")


def boundary_sql() -> str:
    """Build one Geography-owned CBSA boundary from current tract membership."""

    return """
    WITH market_counties AS (
        SELECT county_geoid, boundary_vintage
        FROM mart_geography.rollup_county_to_cbsa
        WHERE cbsa_code = ?
    ), market_boundary AS (
        SELECT
            ST_Union_Agg(t.geom) AS geom,
            MIN(c.boundary_vintage) AS boundary_vintage,
            COUNT(DISTINCT t.tract_geoid) AS tract_count
        FROM geo.tracts_all_us t
        INNER JOIN market_counties c ON t.county_geoid = c.county_geoid
    )
    SELECT
        ST_XMin(ST_Extent_Agg(geom)) AS west,
        ST_YMin(ST_Extent_Agg(geom)) AS south,
        ST_XMax(ST_Extent_Agg(geom)) AS east,
        ST_YMax(ST_Extent_Agg(geom)) AS north,
        MIN(boundary_vintage) AS boundary_vintage,
        MIN(tract_count) AS tract_count,
        ST_AsWKB(ST_Union_Agg(geom)) AS geom
    FROM market_boundary
    """


def resolve_boundary(con: duckdb.DuckDBPyConnection, market_id: str) -> dict[str, Any]:
    """Resolve the market geometry and vintage through the Geography Engine."""

    row = con.execute(boundary_sql(), [market_id]).fetchone()
    if not row or row[0] is None or row[4] is None:
        raise RuntimeError(f"Geography Engine returned no tract boundary for CBSA {market_id}.")
    return {
        "west": row[0], "south": row[1], "east": row[2], "north": row[3],
        "boundary_vintage": int(row[4]), "tract_count": int(row[5]), "geometry": row[6],
    }


def bbox_predicate() -> str:
    """Use Overture's bbox metadata as a prefilter before spatial intersection."""

    return "bbox.xmin <= ? AND bbox.xmax >= ? AND bbox.ymin <= ? AND bbox.ymax >= ?"


def counts(con: duckdb.DuckDBPyConnection, source_path: str, boundary: dict[str, Any]) -> tuple[int, int]:
    """Count broad extraction candidates and true-boundary retained records."""

    source = f"read_parquet({sql_literal(source_path)}, hive_partitioning = 1)"
    predicate = bbox_predicate()
    params = [boundary["east"], boundary["west"], boundary["north"], boundary["south"]]
    extracted = con.execute(f"SELECT COUNT(*) FROM {source} WHERE {predicate}", params).fetchone()[0]
    retained = con.execute(
        f"SELECT COUNT(*) FROM {source} WHERE {predicate} AND ST_Intersects(geometry, ST_GeomFromWKB(?))",
        [*params, boundary["geometry"]],
    ).fetchone()[0]
    return int(extracted), int(retained)


def cache_source_faithful(con: duckdb.DuckDBPyConnection, source_path: str, boundary: dict[str, Any], destination: Path) -> None:
    """Write every retained native source field without applying POI taxonomy logic."""

    source = f"read_parquet({sql_literal(source_path)}, hive_partitioning = 1)"
    predicate = bbox_predicate()
    params = [boundary["east"], boundary["west"], boundary["north"], boundary["south"], boundary["geometry"]]
    destination.parent.mkdir(parents=True, exist_ok=True)
    con.execute(
        f"COPY (SELECT * FROM {source} WHERE {predicate} AND ST_Intersects(geometry, ST_GeomFromWKB(?))) "
        f"TO {sql_literal(str(destination))} (FORMAT PARQUET, COMPRESSION ZSTD)",
        params,
    )


def sha256(path: Path) -> str:
    """Hash the completed local cache so a manifest identifies its exact bytes."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_id(market_id: str, release: str) -> str:
    """Create a readable unique run identifier; reproducibility lives in its manifest."""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    release_token = re.sub(r"[^A-Za-z0-9]+", "-", release).strip("-")
    return f"overture-places-{market_id}-{release_token}-{timestamp}"


def main() -> None:
    """Acquire one declared market/release and write its immutable run artifacts."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True, help="Market key from the source configuration.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Source configuration path.")
    parser.add_argument("--db-path", type=Path, help="Override DB_PATH for this invocation.")
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT, help="Root for local source-run caches.")
    parser.add_argument("--dry-run", action="store_true", help="Resolve boundary and counts without writing a cache or manifest.")
    args = parser.parse_args()

    config = read_config(args.config)
    market_name, market_id = resolve_market(config, args.market)
    database = database_path(args.db_path)
    if not database.exists():
        raise FileNotFoundError(f"DuckDB database does not exist: {database}")

    with duckdb.connect(str(database), read_only=True) as con:
        configure_extensions(con, config["source_path"])
        boundary = resolve_boundary(con, market_id)
        extracted, retained = counts(con, config["source_path"], boundary)
        run = run_id(market_id, config["source_release"])
        run_dir = args.output_root / market_name / run
        cache_path = run_dir / "overture_places_source.parquet"
        manifest_path = run_dir / "source_run_manifest.json"
        if not args.dry_run:
            cache_source_faithful(con, config["source_path"], boundary, cache_path)
            manifest = {
                "source_run_id": run, "source_system": config["source_system"],
                "source_dataset": config["source_dataset"], "source_release": config["source_release"],
                "market_id": market_id, "market_slug": market_name,
                "boundary": {key: boundary[key] for key in ("west", "south", "east", "north", "boundary_vintage", "tract_count")},
                "query": {"method": config["query_method"], "source_path": config["source_path"], "bbox_prefilter": True, "true_boundary_filter": "ST_Intersects"},
                "cache": {"uri": str(cache_path.relative_to(REPO_ROOT)), "sha256": sha256(cache_path)},
                "row_counts": {"extracted_bbox": extracted, "retained_market": retained, "outside_market_boundary": extracted - retained, "rejected": 0},
                "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "notes": ["Source-faithful cache only; normalization, coordinate validation, and taxonomy mapping are deferred to later epics."],
            }
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"market": market_name, "market_id": market_id, "source_release": config["source_release"], "extracted_bbox": extracted, "retained_market": retained, "outside_market_boundary": extracted - retained, "dry_run": args.dry_run}, indent=2))


if __name__ == "__main__":
    main()
