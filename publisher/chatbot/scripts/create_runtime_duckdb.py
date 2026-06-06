"""Build a slim runtime DuckDB for the chatbot and reference dashboard."""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import yaml

from chatbot.query.catalogs import SEMANTIC_DIR


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPO_ROOT / "data" / "duckdb" / "metro_deep_dive_reference.duckdb"
DEFAULT_TARGET = REPO_ROOT / "data" / "duckdb" / "metro_deep_dive_runtime.duckdb"
TABLE_CATALOG_PATH = SEMANTIC_DIR / "table_catalog.yml"
METRIC_CATALOG_PATH = SEMANTIC_DIR / "metric_catalog.yml"


SUPPORT_TABLES: dict[str, list[str]] = {
    "gold.dim_geo": [
        "geo_level",
        "geo_id",
        "geo_name",
        "display_name",
        "hierarchy_rank",
        "state_fips",
        "state_name",
        "state_abbr",
        "region_id",
        "region_name",
        "division_id",
        "division_name",
        "cbsa_code",
        "cbsa_name",
        "cbsa_type",
        "cbsa_type_short",
        "is_metro",
        "is_micro",
        "county_geoid",
        "county_name",
        "county_name_long",
        "county_flag",
        "primary_city_name",
        "parent_geo_level",
        "parent_geo_id",
        "parent_us_id",
        "parent_region_id",
        "parent_division_id",
        "parent_state_fips",
        "parent_cbsa_code",
        "state_count",
        "region_count",
        "division_count",
        "county_count",
        "vintage",
        "source",
    ],
    "silver.xwalk_cbsa_state": ["cbsa_code", "state_fips"],
    "silver.xwalk_state_region": ["state_fips", "census_region", "census_division"],
}

BENCHMARK_COLUMNS = [
    "benchmark_level",
    "benchmark_geo_id",
    "benchmark_label",
    "source_table",
    "metric_id",
    "year",
    "metric_value",
]


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _quoted_columns(columns: list[str]) -> str:
    return ", ".join(f'"{column}"' for column in columns)


def _active_runtime_tables() -> dict[str, dict]:
    table_catalog = _load_yaml(TABLE_CATALOG_PATH)
    metric_catalog = _load_yaml(METRIC_CATALOG_PATH)

    active_tables = {
        entry["table_id"]: entry
        for entry in table_catalog["tables"]
        if entry.get("status") == "active"
    }

    metric_columns_by_table: dict[str, set[str]] = {table_id: set() for table_id in active_tables}
    for metric in metric_catalog["metrics"]:
        table_id = metric.get("source_table")
        source_column = metric.get("source_column")
        if table_id in metric_columns_by_table and source_column:
            metric_columns_by_table[table_id].add(source_column)

    selected: dict[str, dict] = {}
    for table_id, entry in active_tables.items():
        core_columns = {
            entry["geo_id_field"],
            entry["geo_level_field"],
            entry["geo_name_field"],
            entry["time_field"],
            *entry.get("primary_key", []),
        }
        selected_columns = sorted(core_columns | metric_columns_by_table[table_id])
        fq_table = f'{entry["schema"]}.{entry["table_name"]}'
        selected[fq_table] = {
            "table_id": table_id,
            "table_name": entry["table_name"],
            "schema": entry["schema"],
            "columns": selected_columns,
        }
    return selected


def build_runtime_duckdb(source: Path, target: Path) -> None:
    runtime_tables = _active_runtime_tables()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()

    con = duckdb.connect(str(target), read_only=False)
    try:
        con.execute(f"ATTACH '{source}' AS source_db (READ_ONLY)")
        con.execute("LOAD spatial")

        for schema in ("gold", "geo", "silver"):
            con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

        for fq_table, meta in runtime_tables.items():
            create_sql = f"""
                CREATE TABLE {fq_table} AS
                SELECT {_quoted_columns(meta["columns"])}
                FROM source_db.{fq_table}
            """
            con.execute(create_sql)

        active_table_names = sorted(meta["table_name"] for meta in runtime_tables.values())
        active_tables_sql = ", ".join(f"'{name}'" for name in active_table_names)
        con.execute(
            f"""
            CREATE TABLE gold.benchmark_reference AS
            SELECT {_quoted_columns(BENCHMARK_COLUMNS)}
            FROM source_db.gold.benchmark_reference
            WHERE source_table IN ({active_tables_sql})
            """
        )

        for fq_table, columns in SUPPORT_TABLES.items():
            con.execute(
                f"""
                CREATE TABLE {fq_table} AS
                SELECT {_quoted_columns(columns)}
                FROM source_db.{fq_table}
                """
            )

        con.execute(
            """
            CREATE TABLE geo.states AS
            SELECT
              state_fips,
              state_name,
              ST_AsGeoJSON(geom) AS geojson_str
            FROM source_db.geo.states
            """
        )
        con.execute(
            """
            CREATE TABLE geo.counties AS
            SELECT
              county_geoid,
              county_name,
              state_fips,
              ST_AsGeoJSON(geom) AS geojson_str
            FROM source_db.geo.counties
            """
        )
        con.execute(
            """
            CREATE TABLE geo.cbsas AS
            SELECT
              cbsa_code,
              cbsa_name,
              ST_AsGeoJSON(geom) AS geojson_str
            FROM source_db.geo.cbsas
            """
        )
        con.execute(
            """
            CREATE TABLE geo.regions AS
            SELECT
              CASE
                WHEN x.census_region = 'Northeast' THEN '1'
                WHEN x.census_region = 'Midwest' THEN '2'
                WHEN x.census_region = 'South' THEN '3'
                WHEN x.census_region = 'West' THEN '4'
              END AS geo_id,
              x.census_region AS geo_name,
              ST_AsGeoJSON(ST_Union_Agg(s.geom)) AS geojson_str
            FROM source_db.geo.states s
            INNER JOIN source_db.silver.xwalk_state_region x
              ON s.state_fips = x.state_fips
            GROUP BY 1, 2
            """
        )
        con.execute(
            """
            CREATE TABLE geo.divisions AS
            SELECT
              CASE
                WHEN x.census_division = 'New England' THEN '1'
                WHEN x.census_division = 'Middle Atlantic' THEN '2'
                WHEN x.census_division = 'East North Central' THEN '3'
                WHEN x.census_division = 'West North Central' THEN '4'
                WHEN x.census_division = 'South Atlantic' THEN '5'
                WHEN x.census_division = 'East South Central' THEN '6'
                WHEN x.census_division = 'West South Central' THEN '7'
                WHEN x.census_division = 'Mountain' THEN '8'
                WHEN x.census_division = 'Pacific' THEN '9'
              END AS geo_id,
              x.census_division AS geo_name,
              ST_AsGeoJSON(ST_Union_Agg(s.geom)) AS geojson_str
            FROM source_db.geo.states s
            INNER JOIN source_db.silver.xwalk_state_region x
              ON s.state_fips = x.state_fips
            GROUP BY 1, 2
            """
        )

        con.execute("CHECKPOINT")
    finally:
        con.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_runtime_duckdb(source=args.source, target=args.target)
    print(f"Created runtime DuckDB: {args.target}")


if __name__ == "__main__":
    main()
