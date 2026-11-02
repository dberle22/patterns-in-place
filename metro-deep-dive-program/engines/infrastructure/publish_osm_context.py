#!/usr/bin/env python3
"""Append validated OSM context polygons to their own DuckDB table.

Usage:
    python metro-deep-dive-program/engines/infrastructure/publish_osm_context.py --market new_york_state_context

Core roads, rail and water stay as local Parquet; only this context layer is
served from the warehouse. A run already in the table is refused, never replaced.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import duckdb

from acquire_osm_infrastructure import DEFAULT_OUTPUT_ROOT, ENGINE_DIR, database_path, sql_literal
from normalize_osm_infrastructure import latest_source_run

sys.path.insert(0, str(ENGINE_DIR.parent / "_shared"))
from append_run import append_run


MAPPING_VERSION = "osm_context_v1"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", required=True)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--db-path", type=Path)
    args = parser.parse_args()

    run = latest_source_run(args.output_root, args.market)
    manifest = json.loads((run / "source_run_manifest.json").read_text(encoding="utf-8"))
    path = run / "validated" / MAPPING_VERSION / "infrastructure_feature.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Validate the run before publishing: {path}")
    select = f"SELECT * REPLACE (ST_GeomFromWKB(geometry) AS geometry) FROM read_parquet({sql_literal(str(path))})"
    with duckdb.connect(str(database_path(args.db_path))) as con:
        con.execute("LOAD spatial")
        rows = append_run(con, "mart_infrastructure", "infrastructure_context_feature", select, manifest["source_run_id"])
    print(f"mart_infrastructure.infrastructure_context_feature: appended {rows:,} rows for {manifest['source_run_id']}")


if __name__ == "__main__":
    main()
