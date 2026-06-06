"""Compatibility wrapper for curated POI Google Takeout ingestion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nyc_property_finder.curated_poi.google_takeout.config import (
    DEFAULT_MAX_DETAILS_CALLS,
    DEFAULT_MAX_TEXT_SEARCH_CALLS,
    DEFAULT_RESOLUTION_CACHE_PATH,
    DEFAULT_SEARCH_CONTEXT,
)
from nyc_property_finder.curated_poi.google_takeout.dry_run import (
    DEFAULT_DETAILS_CACHE_PATH,
    plan_directory_dry_run,
    plan_dry_run,
)
from nyc_property_finder.curated_poi.google_takeout.pipeline import run, run_input_dir


__all__ = ["run"]


def main() -> None:
    """Run Google Places POI ingestion from one CSV or a whole directory."""

    parser = argparse.ArgumentParser(
        description="Ingest curated Google saved-list CSVs into dim_user_poi_v2.",
    )
    parser.add_argument("csv_path", nargs="?", type=Path, help="Path to one Google Takeout saved-list CSV.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Directory containing curated CSVs to ingest together.",
    )
    parser.add_argument(
        "--database-path",
        type=Path,
        default=None,
        help="DuckDB path. Defaults to config/settings.yaml.",
    )
    parser.add_argument(
        "--search-context",
        default=DEFAULT_SEARCH_CONTEXT,
        help="Geography appended to Text Search queries. Default: New York, NY.",
    )
    parser.add_argument(
        "--max-text-search-calls",
        type=int,
        default=DEFAULT_MAX_TEXT_SEARCH_CALLS,
        help="Hard cap for new Text Search calls.",
    )
    parser.add_argument(
        "--max-details-calls",
        type=int,
        default=DEFAULT_MAX_DETAILS_CALLS,
        help="Hard cap for new Place Details calls.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print per-file expected API work and taxonomy assignments without hitting the API or writing the DB.",
    )
    parser.add_argument(
        "--no-write-database",
        action="store_true",
        help="Build caches and summary without writing dim_user_poi_v2 to DuckDB.",
    )
    args = parser.parse_args()

    if bool(args.csv_path) == bool(args.input_dir):
        parser.error("Pass exactly one input source: either csv_path or --input-dir.")

    if args.dry_run:
        if args.input_dir:
            report = plan_directory_dry_run(
                input_dir=args.input_dir,
                resolution_cache_path=DEFAULT_RESOLUTION_CACHE_PATH,
                details_cache_path=DEFAULT_DETAILS_CACHE_PATH,
                search_context=args.search_context,
            )
        else:
            report = plan_dry_run(
                csv_path=args.csv_path,
                resolution_cache_path=DEFAULT_RESOLUTION_CACHE_PATH,
                details_cache_path=DEFAULT_DETAILS_CACHE_PATH,
                search_context=args.search_context,
            )
    elif args.input_dir:
        report = run_input_dir(
            input_dir=args.input_dir,
            database_path=args.database_path,
            search_context=args.search_context,
            max_text_search_calls=args.max_text_search_calls,
            max_details_calls=args.max_details_calls,
            write_database=not args.no_write_database,
        )
    else:
        report = run(
            csv_path=args.csv_path,
            database_path=args.database_path,
            search_context=args.search_context,
            max_text_search_calls=args.max_text_search_calls,
            max_details_calls=args.max_details_calls,
            write_database=not args.no_write_database,
        )
    # Print JSON so reruns are easy to skim or save from the terminal.
    print(json.dumps(report.to_dict(), indent=2, default=str))


if __name__ == "__main__":
    main()
