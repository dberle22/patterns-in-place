"""Print a small v2026.1 affordability query from a canonical release directory."""

import sys

import duckdb


if len(sys.argv) != 2:
    raise SystemExit("Usage: python quickstart.py <canonical-release-directory-url>")

# DuckDB's httpfs extension lets the same query read a Source Cooperative HTTP directory.
panel_base_url = sys.argv[1].rstrip("/")
connection = duckdb.connect()
connection.execute("INSTALL httpfs; LOAD httpfs")
result = connection.execute(
    """
    SELECT geo_name, annualized_median_rent, rent_to_income
    FROM read_parquet(? || '/affordability_wide.parquet')
    WHERE year = 2024
    ORDER BY rent_to_income DESC
    LIMIT 10
    """,
    [panel_base_url],
).fetchdf()
print(result.to_string(index=False))
