"""DuckDB schema initialization helpers."""

from __future__ import annotations

from pathlib import Path

from nyc_property_finder.services.config import PROJECT_ROOT
from nyc_property_finder.services.duckdb_service import DuckDBService


DEFAULT_DDL_DIR = PROJECT_ROOT / "sql" / "ddl"


def iter_ddl_files(ddl_dir: str | Path = DEFAULT_DDL_DIR) -> list[Path]:
    """Return DDL files in deterministic execution order."""

    ddl_path = Path(ddl_dir)
    if not ddl_path.exists():
        raise FileNotFoundError(f"DDL directory does not exist: {ddl_path}")
    return sorted(path for path in ddl_path.glob("*.sql") if path.is_file())


def initialize_database(
    database_path: str | Path,
    ddl_dir: str | Path = DEFAULT_DDL_DIR,
) -> list[Path]:
    """Initialize a DuckDB database from project DDL files.

    Returns the executed DDL paths so callers can log or test what happened.
    """

    ddl_files = iter_ddl_files(ddl_dir)
    with DuckDBService(database_path) as duckdb_service:
        for ddl_file in ddl_files:
            duckdb_service.execute(ddl_file.read_text(encoding="utf-8"))
    return ddl_files
