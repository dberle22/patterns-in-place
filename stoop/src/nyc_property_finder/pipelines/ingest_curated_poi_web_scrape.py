"""Ingest one normalized curated web-scrape CSV into staging and canonical POI tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from nyc_property_finder.curated_poi.web_scraping.pipeline import run


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve one normalized curated web-scrape CSV and merge it into dim_user_poi_v2."
    )
    parser.add_argument("--csv", required=True, help="Normalized scrape CSV path.")
    parser.add_argument("--database-path", help="Optional DuckDB path override.")
    parser.add_argument("--resolution-cache-path", help="Optional resolution cache CSV override.")
    parser.add_argument("--details-cache-path", help="Optional Place Details cache JSONL override.")
    parser.add_argument("--max-text-search-calls", type=int, help="Optional text search call cap override.")
    parser.add_argument("--max-details-calls", type=int, help="Optional Place Details call cap override.")
    parser.add_argument(
        "--skip-db-write",
        action="store_true",
        help="Run resolve/enrich/build without writing DuckDB tables.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    kwargs: dict[str, object] = {
        "csv_path": Path(args.csv),
        "write_database": not args.skip_db_write,
    }
    if args.database_path:
        kwargs["database_path"] = Path(args.database_path)
    if args.resolution_cache_path:
        kwargs["resolution_cache_path"] = Path(args.resolution_cache_path)
    if args.details_cache_path:
        kwargs["details_cache_path"] = Path(args.details_cache_path)
    if args.max_text_search_calls is not None:
        kwargs["max_text_search_calls"] = args.max_text_search_calls
    if args.max_details_calls is not None:
        kwargs["max_details_calls"] = args.max_details_calls

    report = run(**kwargs)
    print(json.dumps(report.to_dict(), default=str, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
