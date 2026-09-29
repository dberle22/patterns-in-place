"""Shared DuckDB helpers for Metro Deep Dive issue notebooks."""

from __future__ import annotations

import os
from pathlib import Path

import duckdb
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[4]


def load_db_path() -> str:
    """Resolve DB_PATH from the environment or the repo-level .Renviron file."""
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


def connect_duckdb(read_only: bool = True) -> duckdb.DuckDBPyConnection:
    """Open the shared project DuckDB with the standard repo path resolution."""
    return duckdb.connect(load_db_path(), read_only=read_only)


def read_sql(query_path: Path) -> str:
    """Read a SQL file from disk without adding another query abstraction layer."""
    if not query_path.exists():
        raise FileNotFoundError(f"Query file not found: {query_path}")
    return query_path.read_text()


def run_param_query(
    con: duckdb.DuckDBPyConnection,
    query_path: Path,
    cbsa_code: str,
) -> pd.DataFrame:
    """Run a query file that uses the shared `__CBSA_CODE__` placeholder."""
    sql = read_sql(query_path).replace("'__CBSA_CODE__'", f"'{cbsa_code}'")
    return con.sql(sql).df()


def get_cbsa_options(con: duckdb.DuckDBPyConnection) -> dict[str, str]:
    """Build a readable CBSA selector map from the promoted cross-frame mart."""
    options_df = con.sql(
        """
        SELECT
          cbsa_code,
          cbsa_name
        FROM mart_intelligence.intelligence_cross_frame
        ORDER BY cbsa_name
        """
    ).df()

    return {
        f"{row.cbsa_name} ({row.cbsa_code})": row.cbsa_code
        for row in options_df.itertuples(index=False)
    }
