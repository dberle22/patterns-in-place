"""Validate the standalone Phase 7 tract-frame SQL against legacy app logic.

This script compares the new explicit SQL artifact to the former Python-built
query contract. It also checks the governed Gold materialization SQL shape
without writing a table to the on-disk DuckDB file.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import duckdb


REPO_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = REPO_ROOT / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
TRACT_FRAME_SQL_PATH = REPO_ROOT / "exploration" / "intelligence_framework" / "phase_7_zone_methodology" / "sql" / "phase7_tract_frame.sql"
GOLD_SQL_PATH = REPO_ROOT / "foundations" / "etl" / "gold" / "gold_intelligence_zone_inputs.sql"
CONFIG_PATH = REPO_ROOT / "exploration" / "intelligence_framework" / "phase_7_zone_methodology" / "app" / "config.py"


def load_config_module():
    """Load the app config without importing the full Streamlit app package."""
    spec = importlib.util.spec_from_file_location("phase7_config", CONFIG_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load config module from {CONFIG_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_legacy_sql(config_module) -> str:
    """Recreate the former dynamic SQL so we can prove the new file matches it."""
    table_to_kpis: dict[tuple[str, str], list[str]] = {}
    for kpi_id in config_module.KPI_IDS:
        if kpi_id not in config_module.KPI_SOURCE_MAP:
            continue
        schema, table, _ = config_module.KPI_SOURCE_MAP[kpi_id]
        table_to_kpis.setdefault((schema, table), []).append(kpi_id)

    base_cte = """
        base AS (
            SELECT DISTINCT
                xwt.tract_geoid,
                xwc.cbsa_code,
                xwc.county_geoid
            FROM silver.xwalk_tract_county xwt
            JOIN silver.xwalk_cbsa_county xwc
                ON xwc.county_geoid = (xwt.state_fip || xwt.county_fip)
        )
    """

    source_ctes: list[str] = []
    join_clauses: list[str] = []
    for (schema, table), kpi_ids_in_table in table_to_kpis.items():
        if (schema, table) == ("gold", "environment_wide"):
            source_ctes.extend(
                [
                    f"""
                    src_environment_ejs AS (
                        SELECT
                            geo_id AS tract_geoid,
                            ejs_pm25
                        FROM {schema}.{table}
                        WHERE geo_level = 'tract'
                          AND year = (
                              SELECT MAX(year)
                              FROM {schema}.{table}
                              WHERE geo_level = 'tract'
                                AND ejs_pm25 IS NOT NULL
                          )
                    )
                    """,
                    f"""
                    src_environment_fema AS (
                        SELECT
                            geo_id AS tract_geoid,
                            fema_risk_score
                        FROM {schema}.{table}
                        WHERE geo_level = 'tract'
                          AND year = (
                              SELECT MAX(year)
                              FROM {schema}.{table}
                              WHERE geo_level = 'tract'
                                AND fema_risk_score IS NOT NULL
                          )
                    )
                    """,
                ]
            )
            join_clauses.append(
                "LEFT JOIN src_environment_ejs ON src_environment_ejs.tract_geoid = base.tract_geoid"
            )
            join_clauses.append(
                "LEFT JOIN src_environment_fema ON src_environment_fema.tract_geoid = base.tract_geoid"
            )
            continue

        safe_alias = f"src_{table}"
        col_selects = ", ".join(
            f"{safe_alias}.{config_module.KPI_SOURCE_MAP[k][2]} AS {k}"
            for k in kpi_ids_in_table
        )
        source_ctes.append(
            f"""
            {safe_alias} AS (
                SELECT
                    geo_id AS tract_geoid,
                    {col_selects}
                FROM {schema}.{table} AS {safe_alias}
                WHERE geo_level = 'tract'
                  AND year = (
                      SELECT MAX(year)
                      FROM {schema}.{table}
                      WHERE geo_level = 'tract'
                  )
            )
            """
        )
        join_clauses.append(
            f"LEFT JOIN {safe_alias} ON {safe_alias}.tract_geoid = base.tract_geoid"
        )

    all_kpi_cols = ", ".join(
        (
            "src_environment_ejs.ejs_pm25"
            if k == "ejs_pm25"
            else "src_environment_fema.fema_risk_score"
            if k == "fema_risk_score"
            else f"src_{config_module.KPI_SOURCE_MAP[k][1]}.{k}"
        )
        for k in config_module.KPI_IDS
        if k in config_module.KPI_SOURCE_MAP
    )

    cte_block = "WITH " + base_cte
    if source_ctes:
        cte_block += ",\n" + ",\n".join(source_ctes)

    joins = "\n".join(join_clauses)
    return f"""
        {cte_block}
        SELECT
            base.tract_geoid,
            base.cbsa_code,
            base.county_geoid,
            {all_kpi_cols}
        FROM base
        {joins}
    """


def load_standalone_sql() -> str:
    """Read the standalone SQL file and remove the optional CBSA filter token."""
    return TRACT_FRAME_SQL_PATH.read_text().replace("/*__CBSA_FILTER__*/", "")


def load_materialization_query() -> str:
    """Strip the CREATE TABLE wrapper so we can validate the query as a temp view."""
    materialization_sql = GOLD_SQL_PATH.read_text()
    return re.sub(
        r".*?create\s+or\s+replace\s+table\s+.+?\s+as\s+",
        "",
        materialization_sql,
        count=1,
        flags=re.IGNORECASE | re.DOTALL,
    )


def query_value(con: duckdb.DuckDBPyConnection, sql: str):
    return con.execute(sql).fetchone()[0]


def compare_column_order(config_module):
    """The KPI and geography columns must stay in the exact app-facing order."""
    return [
        "tract_geoid",
        "cbsa_code",
        "county_geoid",
        *config_module.KPI_IDS,
    ]


def coverage_counts_sql(view_name: str, kpi_ids: list[str]) -> str:
    """Build a compact null-count check so coverage parity is easy to assert."""
    select_bits = [
        f"sum(case when {kpi_id} is null then 1 else 0 end) as {kpi_id}_nulls"
        for kpi_id in kpi_ids
    ]
    return f"select {', '.join(select_bits)} from {view_name}"


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"DuckDB file does not exist: {DB_PATH}")

    config_module = load_config_module()
    expected_primary_columns = compare_column_order(config_module)
    audit_columns = [
        "population_demographics_year",
        "migration_wide_year",
        "housing_core_wide_year",
        "social_infra_wide_year",
        "transport_built_form_wide_year",
        "transport_built_form_sld_year",
        "environment_ejs_year",
        "environment_fema_year",
        "economics_income_wide_year",
        "economics_labor_wide_year",
        "economics_lodes_wide_year",
    ]

    standalone_sql = load_standalone_sql()
    legacy_sql = build_legacy_sql(config_module)
    materialization_query = load_materialization_query()

    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        con.execute(f"create or replace temp view legacy_frame as {legacy_sql}")
        con.execute(f"create or replace temp view standalone_frame as {standalone_sql}")
        con.execute(f"create or replace temp view materialized_candidate as {materialization_query}")

        print("Phase 7 tract-frame validation")
        print(f"DB: {DB_PATH}")

        # These count checks protect the tract base and the joined output shape.
        legacy_rows = query_value(con, "select count(*) from legacy_frame")
        standalone_rows = query_value(con, "select count(*) from standalone_frame")
        materialized_rows = query_value(con, "select count(*) from materialized_candidate")
        print(f"Row count: legacy={legacy_rows}, standalone={standalone_rows}, materialized_candidate={materialized_rows}")

        legacy_dupes = query_value(
            con,
            "select count(*) from (select tract_geoid from legacy_frame group by 1 having count(*) > 1)",
        )
        standalone_dupes = query_value(
            con,
            "select count(*) from (select tract_geoid from standalone_frame group by 1 having count(*) > 1)",
        )
        print(f"Duplicate tract_geoid rows: legacy={legacy_dupes}, standalone={standalone_dupes}")

        legacy_cbsas = query_value(con, "select count(distinct cbsa_code) from legacy_frame")
        standalone_cbsas = query_value(con, "select count(distinct cbsa_code) from standalone_frame")
        print(f"Distinct CBSAs: legacy={legacy_cbsas}, standalone={standalone_cbsas}")

        standalone_columns = [
            row[0]
            for row in con.execute("describe select * from standalone_frame").fetchall()
        ]
        materialized_columns = [
            row[0]
            for row in con.execute("describe select * from materialized_candidate").fetchall()
        ]
        print(f"Primary columns preserved: {standalone_columns[:len(expected_primary_columns)] == expected_primary_columns}")
        print(f"Audit columns present: {standalone_columns[-len(audit_columns):] == audit_columns}")
        print(f"Materialization matches standalone columns: {materialized_columns == standalone_columns}")

        # A full-row parity join is safer than a sampled eyeball check.
        diff_predicates = " OR ".join(
            f"NOT (l.{col} IS NOT DISTINCT FROM s.{col})"
            for col in expected_primary_columns
        )
        mismatch_rows = query_value(
            con,
            f"""
            select count(*)
            from legacy_frame l
            join standalone_frame s using (tract_geoid)
            where {diff_predicates}
            """,
        )
        print(f"Legacy-vs-standalone mismatched tract rows: {mismatch_rows}")

        coverage_legacy = con.execute(
            coverage_counts_sql("legacy_frame", config_module.KPI_IDS)
        ).fetchone()
        coverage_standalone = con.execute(
            coverage_counts_sql("standalone_frame", config_module.KPI_IDS)
        ).fetchone()
        print(f"Coverage parity across KPI null counts: {coverage_legacy == coverage_standalone}")

        expected_years = {
            "population_demographics_year": 2024,
            "migration_wide_year": 2024,
            "housing_core_wide_year": 2024,
            "social_infra_wide_year": 2024,
            "transport_built_form_wide_year": 2024,
            "transport_built_form_sld_year": 2021,
            "environment_ejs_year": 2024,
            "environment_fema_year": 2025,
            "economics_income_wide_year": 2024,
            "economics_labor_wide_year": 2024,
            "economics_lodes_wide_year": 2023,
        }
        for audit_column, expected_year in expected_years.items():
            years = con.execute(
                f"select distinct {audit_column} from standalone_frame order by 1"
            ).fetchall()
            print(f"{audit_column}: {years} (expected includes {expected_year})")

        null_geo_rows = query_value(
            con,
            """
            select count(*)
            from standalone_frame
            where cbsa_code is null
               or county_geoid is null
            """,
        )
        print(f"Rows with null base geography fields: {null_geo_rows}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
