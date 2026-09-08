#!/usr/bin/env python3
"""Build the first-pass mart_benchmarking schema from the local SQL assets."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import duckdb


REPO_ROOT = Path(__file__).resolve().parents[3]
ENGINE_DIR = Path(__file__).resolve().parent
QUERY_DIR = ENGINE_DIR / "queries"

BUILD_FILES = [
    "build_benchmark_metric_catalog.sql",
    "build_benchmark_cbsa_metrics.sql",
    "build_benchmark_sets.sql",
    "build_benchmark_set_members.sql",
]

CHECK_QUERIES = {
    "benchmark_metric_catalog": "SELECT COUNT(*) AS n FROM mart_benchmarking.benchmark_metric_catalog",
    "benchmark_cbsa_metrics": "SELECT COUNT(*) AS n FROM mart_benchmarking.benchmark_cbsa_metrics",
    "benchmark_sets": "SELECT COUNT(*) AS n FROM mart_benchmarking.benchmark_sets",
    "benchmark_set_members": "SELECT COUNT(*) AS n FROM mart_benchmarking.benchmark_set_members",
}


def load_db_path() -> str:
    """Resolve DB_PATH from the environment or repo-level .Renviron."""

    db_path = os.environ.get("DB_PATH", "").strip()
    if db_path:
        return db_path

    renviron_path = REPO_ROOT / ".Renviron"
    if renviron_path.exists():
        for raw_line in renviron_path.read_text().splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "DB_PATH":
                return value.strip()

    raise RuntimeError("DB_PATH is not set and could not be found in .Renviron.")


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for build and validation behavior."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db-path",
        default=None,
        help="Optional DuckDB path override. Defaults to DB_PATH or .Renviron.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Skip rebuild and only report row-count checks for existing tables.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the benchmark schema build in dependency order, then report counts."""

    args = parse_args()
    db_path = args.db_path or load_db_path()

    with duckdb.connect(db_path) as con:
        if not args.validate_only:
            for sql_file in BUILD_FILES:
                sql = (QUERY_DIR / sql_file).read_text()
                con.execute(sql)

        print("mart_benchmarking row-count checks:")
        for table_name, sql in CHECK_QUERIES.items():
            count = con.execute(sql).fetchone()[0]
            print(f"  {table_name}: {count}")


if __name__ == "__main__":
    main()
