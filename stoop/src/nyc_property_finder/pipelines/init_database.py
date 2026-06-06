"""Initialize the local DuckDB database schema."""

from __future__ import annotations

from pathlib import Path

from nyc_property_finder.services.config import PROJECT_ROOT, load_config
from nyc_property_finder.services.schema import DEFAULT_DDL_DIR, initialize_database


def run(
    database_path: str | Path | None = None,
    ddl_dir: str | Path = DEFAULT_DDL_DIR,
) -> list[Path]:
    """Create project schemas and empty tables in DuckDB."""

    if database_path is None:
        settings = load_config()["settings"]
        database_path = PROJECT_ROOT / settings["database_path"]
    return initialize_database(database_path=database_path, ddl_dir=ddl_dir)


if __name__ == "__main__":
    executed_files = run()
    for path in executed_files:
        print(f"Executed DDL: {path}")
