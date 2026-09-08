"""Minimal Python use of the containment-first geography mart."""

import duckdb


def tract_to_cbsa(connection: duckdb.DuckDBPyConnection, tract_geoid: str):
    """Return the exact current CBSA parent, if the tract is in a CBSA."""
    return connection.execute(
        """
        SELECT cbsa_code, tract_boundary_vintage, cbsa_boundary_vintage
        FROM mart_geography.rollup_tract_to_cbsa
        WHERE tract_geoid = ?
        """,
        [tract_geoid],
    ).fetchall()
