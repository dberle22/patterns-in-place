"""Shared pytest fixtures."""

import pytest
import duckdb


@pytest.fixture(scope="session")
def db_path():
    from retail_opportunity_finder.utils.config import get_db_path
    return get_db_path()


@pytest.fixture(scope="session")
def prod_con(db_path):
    """Read-only connection to the production app database. Skips if DB absent."""
    if not db_path.exists():
        pytest.skip(f"App database not found: {db_path}")
    return duckdb.connect(str(db_path), read_only=True)


@pytest.fixture
def mem_con():
    """
    In-memory DuckDB with the rof_gold schema and user_shortlist table.
    Used for upsert and write tests that must not touch the production DB.
    """
    con = duckdb.connect(":memory:")
    con.execute("CREATE SCHEMA rof_gold")
    con.execute("""
        CREATE TABLE rof_gold.user_shortlist (
            parcel_uid  VARCHAR,
            market_key  VARCHAR,
            user_id     VARCHAR,
            status      VARCHAR DEFAULT 'active',
            notes       VARCHAR DEFAULT '',
            created_at  TIMESTAMPTZ DEFAULT now(),
            updated_at  TIMESTAMPTZ DEFAULT now(),
            PRIMARY KEY (parcel_uid, market_key, user_id)
        )
    """)
    return con
