#!/usr/bin/env python3
"""Append a built OSM anchor run to `mart_poi.poi_osm_anchor`.

Usage:
    python metro-deep-dive-program/engines/poi/publish_osm_anchors.py

The anchors have their own table so they cannot change Overture category counts
or the POI tables' consumers. A run already in the table is refused.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import duckdb

from acquire_overture_places import ENGINE_DIR, configure_extensions, database_path, sql_literal
from build_osm_anchors import OUTPUT_SLUG

sys.path.insert(0, str(ENGINE_DIR.parent / "_shared"))
from append_run import append_run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ENGINE_DIR / "outputs")
    parser.add_argument("--db-path", type=Path)
    args = parser.parse_args()

    runs = sorted(path.parent for path in (args.output_root / OUTPUT_SLUG).glob("*/osm_anchor_manifest.json"))
    if not runs:
        raise FileNotFoundError("Run build_osm_anchors.py before publishing.")
    run = runs[-1]
    manifest = json.loads((run / "osm_anchor_manifest.json").read_text(encoding="utf-8"))
    select = f"SELECT * FROM read_parquet({sql_literal(str(run / 'poi_osm_anchor.parquet'))})"
    with duckdb.connect(str(database_path(args.db_path))) as con:
        # Load spatial first so geometry arrives as GEOMETRY rather than BLOB.
        configure_extensions(con, "local.parquet")
        rows = append_run(con, "mart_poi", "poi_osm_anchor", select, manifest["source_run_id"])
    print(f"mart_poi.poi_osm_anchor: appended {rows:,} rows for {manifest['source_run_id']}")


if __name__ == "__main__":
    main()
