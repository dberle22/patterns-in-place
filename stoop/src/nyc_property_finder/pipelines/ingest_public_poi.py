"""Pipeline entry point for public baseline POIs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nyc_property_finder.public_poi.pipeline import run

__all__ = ["run"]


def main() -> None:
    """Run public baseline POI ingestion and print a compact JSON report."""

    parser = argparse.ArgumentParser(
        description="Ingest public baseline POIs into dim_public_poi.",
    )
    parser.add_argument(
        "--database-path",
        type=Path,
        default=None,
        help="DuckDB path. Defaults to config/settings.yaml.",
    )
    parser.add_argument(
        "--table-name",
        default="dim_public_poi",
        help="Destination table name. Default: dim_public_poi.",
    )
    parser.add_argument(
        "--schema",
        default="property_explorer_gold",
        help="Destination schema. Default: property_explorer_gold.",
    )
    parser.add_argument(
        "--no-write-database",
        action="store_true",
        help="Build the public POI dataframe without writing it to DuckDB.",
    )
    args = parser.parse_args()

    report = run(
        database_path=args.database_path,
        write_database=not args.no_write_database,
        table_name=args.table_name,
        schema=args.schema,
    )
    print(json.dumps(report.to_dict(), indent=2, default=str))


if __name__ == "__main__":
    main()
