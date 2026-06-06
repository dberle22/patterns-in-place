"""DuckDB connection helpers for NYC Property Finder.

The service keeps database access small and explicit. Pipelines can use it as a
context manager, register pandas/geopandas dataframes, and write tables without
needing to repeat connection setup.
"""

from __future__ import annotations

from contextlib import AbstractContextManager
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd


class DuckDBService(AbstractContextManager["DuckDBService"]):
    """Thin wrapper around a DuckDB connection."""

    def __init__(self, database_path: str | Path, read_only: bool = False) -> None:
        self.database_path = Path(database_path)
        self.read_only = read_only
        self._connection: duckdb.DuckDBPyConnection | None = None

    @property
    def connection(self) -> duckdb.DuckDBPyConnection:
        """Return an active DuckDB connection, opening it if needed."""

        if self._connection is None:
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = duckdb.connect(
                str(self.database_path),
                read_only=self.read_only,
            )
        return self._connection

    def execute(self, sql: str, parameters: dict[str, Any] | None = None) -> duckdb.DuckDBPyConnection:
        """Execute a SQL statement and return the DuckDB cursor."""

        if parameters:
            return self.connection.execute(sql, parameters)
        return self.connection.execute(sql)

    def query_df(self, sql: str, parameters: dict[str, Any] | None = None) -> pd.DataFrame:
        """Run a query and return a pandas DataFrame."""

        return self.execute(sql, parameters).df()

    def register_dataframe(self, view_name: str, dataframe: pd.DataFrame) -> None:
        """Register a pandas or GeoPandas dataframe as a temporary DuckDB view."""

        self.connection.register(view_name, dataframe)

    def write_dataframe(
        self,
        dataframe: pd.DataFrame,
        table_name: str,
        schema: str = "main",
        if_exists: str = "replace",
    ) -> None:
        """Write a dataframe into DuckDB.

        Parameters
        ----------
        dataframe:
            DataFrame to persist.
        table_name:
            Destination table name.
        schema:
            Destination schema. Created automatically when needed.
        if_exists:
            Either ``replace`` or ``append``.
        """

        if if_exists not in {"replace", "append"}:
            raise ValueError("if_exists must be either 'replace' or 'append'")

        full_table_name = f"{schema}.{table_name}"
        temp_view = f"tmp_{schema}_{table_name}"
        self.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        self.register_dataframe(temp_view, dataframe)

        if if_exists == "replace":
            self.execute(f"CREATE OR REPLACE TABLE {full_table_name} AS SELECT * FROM {temp_view}")
        else:
            self.execute(f"INSERT INTO {full_table_name} SELECT * FROM {temp_view}")

        self.connection.unregister(temp_view)

    def close(self) -> None:
        """Close the active connection."""

        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self.close()


def get_duckdb_service(database_path: str | Path, read_only: bool = False) -> DuckDBService:
    """Factory used by pipelines and the Streamlit app."""

    return DuckDBService(database_path=database_path, read_only=read_only)
