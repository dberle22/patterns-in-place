"""DuckDB execution layer for validated queries."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import duckdb

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency in bare environments
    def load_dotenv() -> bool:
        return False

try:
    import pandas as pd
except ImportError:  # pragma: no cover - optional dependency in bare environments
    pd = None

from chatbot.query.generator import RenderedQuery

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNTIME_DB = REPO_ROOT / "data" / "duckdb" / "metro_deep_dive_runtime.duckdb"


class QueryExecutor:
    """Execute validated read-only SQL against DuckDB."""

    def __init__(self, db_connection: str | None = None, read_only: bool = True) -> None:
        load_dotenv()
        self.db_connection = db_connection or os.getenv("DB_CONNECTION") or str(DEFAULT_RUNTIME_DB)
        self.read_only = read_only

    def execute(self, query: str | RenderedQuery) -> pd.DataFrame:
        if pd is None:
            raise ImportError("pandas is required to execute queries into DataFrames")
        sql = query.sql if isinstance(query, RenderedQuery) else query
        connection = self._connect()
        try:
            return connection.execute(sql).fetchdf()
        finally:
            connection.close()

    def execute_scalar(self, query: str | RenderedQuery) -> Any:
        sql = query.sql if isinstance(query, RenderedQuery) else query
        connection = self._connect()
        try:
            row = connection.execute(sql).fetchone()
            return None if row is None else row[0]
        finally:
            connection.close()

    def _connect(self) -> duckdb.DuckDBPyConnection:
        path = Path(self.db_connection)
        if not path.exists():
            raise FileNotFoundError(f"DuckDB file does not exist: {self.db_connection}")
        return duckdb.connect(str(path), read_only=self.read_only)
