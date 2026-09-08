"""Shared DuckDB connection helpers for benchmarking consumers."""

from __future__ import annotations

import os
from pathlib import Path

import duckdb


REPO_ROOT = Path(__file__).resolve().parents[3]


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


def connect(db_path: str | None = None, read_only: bool = True) -> duckdb.DuckDBPyConnection:
    """Open the configured DuckDB connection for benchmark queries."""

    return duckdb.connect(db_path or load_db_path(), read_only=read_only)
