"""Helpers for the reference Streamlit data explorer."""

from __future__ import annotations

from copy import deepcopy
import json
import math
import os
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd
import streamlit as st
import yaml

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional in bare environments
    def load_dotenv(*args: Any, **kwargs: Any) -> bool:
        return False


SUBJECT_AREA_TABLES = {
    "population": "gold.population_demographics",
    "housing": "gold.housing_core_wide",
    "income": "gold.economics_income_wide",
}
DEFAULT_RUNTIME_DB = Path(__file__).resolve().parent.parent / "data" / "duckdb" / "metro_deep_dive_runtime.duckdb"

VALID_GEO_LEVELS = {"state", "region", "division", "county", "cbsa"}

VALID_STATE_FIPS = (
    "01",
    "04",
    "05",
    "06",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "16",
    "17",
    "18",
    "19",
    "20",
    "21",
    "22",
    "23",
    "24",
    "25",
    "26",
    "27",
    "28",
    "29",
    "30",
    "31",
    "32",
    "33",
    "34",
    "35",
    "36",
    "37",
    "38",
    "39",
    "40",
    "41",
    "42",
    "44",
    "45",
    "46",
    "47",
    "48",
    "49",
    "50",
    "51",
    "53",
    "54",
    "55",
    "56",
)

REGION_NAME_TO_CODE = {
    "Northeast": "1",
    "Midwest": "2",
    "South": "3",
    "West": "4",
}
REGION_CODE_TO_NAME = {value: key for key, value in REGION_NAME_TO_CODE.items()}

DIVISION_NAME_TO_CODE = {
    "New England": "1",
    "Middle Atlantic": "2",
    "East North Central": "3",
    "West North Central": "4",
    "South Atlantic": "5",
    "East South Central": "6",
    "West South Central": "7",
    "Mountain": "8",
    "Pacific": "9",
}
DIVISION_CODE_TO_NAME = {value: key for key, value in DIVISION_NAME_TO_CODE.items()}

GROWTH_COLUMNS = {
    "population": ["pop_growth_1yr", "pop_growth_3yr", "pop_growth_5yr"],
    "housing": ["hu_growth_1yr", "hu_growth_3yr", "hu_growth_5yr"],
    "income": ["income_pc_growth_1yr", "income_pc_growth_5yr", "income_pc_cagr_5yr"],
}

COMPUTED_METRIC_METADATA = {
    "hu_growth_1yr": {
        "metric_id": "hu_growth_1yr",
        "display_name": "Housing Unit Growth (1 Year)",
        "source_column": "hu_growth_1yr",
        "unit_format": "percent",
        "subject_area": "housing",
        "valid_geo_levels": ["state", "region", "division", "county", "cbsa"],
    },
    "hu_growth_3yr": {
        "metric_id": "hu_growth_3yr",
        "display_name": "Housing Unit Growth (3 Year)",
        "source_column": "hu_growth_3yr",
        "unit_format": "percent",
        "subject_area": "housing",
        "valid_geo_levels": ["state", "region", "division", "county", "cbsa"],
    },
    "hu_growth_5yr": {
        "metric_id": "hu_growth_5yr",
        "display_name": "Housing Unit Growth (5 Year)",
        "source_column": "hu_growth_5yr",
        "unit_format": "percent",
        "subject_area": "housing",
        "valid_geo_levels": ["state", "region", "division", "county", "cbsa"],
    },
}


def _load_project_env() -> None:
    """Load the repo .env explicitly to avoid brittle frame inspection."""
    project_root = Path(__file__).resolve().parent.parent
    load_dotenv(project_root / ".env")


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_connection() -> duckdb.DuckDBPyConnection:
    """Return a read-only DuckDB connection using DB_CONNECTION or the repo runtime DB."""
    _load_project_env()
    db_connection = os.getenv("DB_CONNECTION") or str(DEFAULT_RUNTIME_DB)

    path = Path(db_connection)
    if not path.exists():
        raise FileNotFoundError(f"DuckDB file does not exist: {db_connection}")

    return duckdb.connect(str(path), read_only=True)


def get_valid_state_fips() -> set[str]:
    """Return the contiguous-state-plus-DC FIPS allowlist."""
    return set(VALID_STATE_FIPS)


def _normalize_geo_level(geo_level: str) -> str:
    normalized = geo_level.strip().lower()
    if normalized not in VALID_GEO_LEVELS:
        raise ValueError(f"Unsupported geo_level: {geo_level}")
    return normalized


def _normalize_subject_area(subject_area: str) -> str:
    normalized = subject_area.strip().lower()
    if normalized not in SUBJECT_AREA_TABLES:
        raise ValueError(f"Unsupported subject_area: {subject_area}")
    return normalized


def _normalize_state_filter(state_filter: list[str] | None) -> list[str]:
    if not state_filter:
        return []

    normalized = sorted({state.strip() for state in state_filter if state and state.strip()})
    invalid = sorted(set(normalized) - get_valid_state_fips())
    if invalid:
        raise ValueError(f"Invalid state FIPS codes in state_filter: {invalid}")
    return normalized


def _quoted_sql_list(values: list[str] | tuple[str, ...]) -> str:
    return ", ".join(f"'{value}'" for value in values)


def _load_spatial_extension(connection: duckdb.DuckDBPyConnection) -> None:
    try:
        connection.execute("LOAD spatial")
    except duckdb.Error as exc:
        raise RuntimeError(
            "DuckDB spatial extension is required for GeoJSON queries. "
            "Install it once with `INSTALL spatial;` in a writable DuckDB session, then retry."
        ) from exc


def _region_case_expression(column_name: str) -> str:
    cases = " ".join(
        f"WHEN {column_name} = '{name}' THEN '{code}'"
        for name, code in REGION_NAME_TO_CODE.items()
    )
    return f"CASE {cases} END"


def _division_case_expression(column_name: str) -> str:
    cases = " ".join(
        f"WHEN {column_name} = '{name}' THEN '{code}'"
        for name, code in DIVISION_NAME_TO_CODE.items()
    )
    return f"CASE {cases} END"


@st.cache_data(ttl=3600)
def load_metric_catalog() -> list[dict[str, Any]]:
    catalog_path = _project_root() / "semantic_layer" / "metric_catalog.yml"
    with catalog_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    metrics = payload.get("metrics", [])
    if not isinstance(metrics, list):
        raise ValueError("metric_catalog.yml does not contain a valid metrics list")
    return metrics


def get_metric_metadata(subject_area: str) -> dict[str, dict[str, Any]]:
    normalized_subject_area = _normalize_subject_area(subject_area)
    metadata = {
        metric["source_column"]: metric
        for metric in load_metric_catalog()
        if metric.get("subject_area") == normalized_subject_area
        and metric.get("source_column")
    }
    for column_name, metric in COMPUTED_METRIC_METADATA.items():
        if metric["subject_area"] == normalized_subject_area:
            metadata[column_name] = metric
    return metadata


@st.cache_data(ttl=3600)
def build_geojson(geo_level: str, state_filter: list[str] | None = None) -> dict[str, Any]:
    """Build a GeoJSON FeatureCollection for the requested geography level."""
    normalized_geo_level = _normalize_geo_level(geo_level)
    normalized_state_filter = _normalize_state_filter(state_filter)
    valid_states_sql = _quoted_sql_list(VALID_STATE_FIPS)
    filtered_states_sql = (
        _quoted_sql_list(tuple(normalized_state_filter)) if normalized_state_filter else valid_states_sql
    )

    if normalized_geo_level == "state":
        sql = f"""
            SELECT
                state_fips AS geo_id,
                state_name AS geo_name,
                geojson_str
            FROM geo.states
            WHERE state_fips IN ({filtered_states_sql})
            ORDER BY state_fips
        """
        fallback_sql = f"""
            SELECT
                state_fips AS geo_id,
                state_name AS geo_name,
                ST_AsGeoJSON(geom) AS geojson_str
            FROM geo.states
            WHERE state_fips IN ({filtered_states_sql})
            ORDER BY state_fips
        """
    elif normalized_geo_level == "county":
        sql = f"""
            SELECT
                county_geoid AS geo_id,
                county_name AS geo_name,
                geojson_str
            FROM geo.counties
            WHERE state_fips IN ({filtered_states_sql})
            ORDER BY county_geoid
        """
        fallback_sql = f"""
            SELECT
                county_geoid AS geo_id,
                county_name AS geo_name,
                ST_AsGeoJSON(geom) AS geojson_str
            FROM geo.counties
            WHERE state_fips IN ({filtered_states_sql})
            ORDER BY county_geoid
        """
    elif normalized_geo_level == "cbsa":
        sql = f"""
            SELECT DISTINCT
                c.cbsa_code AS geo_id,
                c.cbsa_name AS geo_name,
                c.geojson_str
            FROM geo.cbsas c
            INNER JOIN silver.xwalk_cbsa_state x
                ON c.cbsa_code = x.cbsa_code
            WHERE x.state_fips IN ({filtered_states_sql})
            ORDER BY c.cbsa_code
        """
        fallback_sql = f"""
            SELECT DISTINCT
                c.cbsa_code AS geo_id,
                c.cbsa_name AS geo_name,
                ST_AsGeoJSON(c.geom) AS geojson_str
            FROM geo.cbsas c
            INNER JOIN silver.xwalk_cbsa_state x
                ON c.cbsa_code = x.cbsa_code
            WHERE x.state_fips IN ({filtered_states_sql})
            ORDER BY c.cbsa_code
        """
    elif normalized_geo_level == "region":
        sql = f"""
            SELECT
                geo_id,
                geo_name,
                geojson_str
            FROM geo.regions
            ORDER BY 1
        """
        fallback_sql = f"""
            SELECT
                {_region_case_expression('x.census_region')} AS geo_id,
                x.census_region AS geo_name,
                ST_AsGeoJSON(ST_Union_Agg(s.geom)) AS geojson_str
            FROM geo.states s
            INNER JOIN silver.xwalk_state_region x
                ON s.state_fips = x.state_fips
            WHERE s.state_fips IN ({filtered_states_sql})
            GROUP BY 1, 2
            ORDER BY 1
        """
    else:
        sql = f"""
            SELECT
                geo_id,
                geo_name,
                geojson_str
            FROM geo.divisions
            ORDER BY 1
        """
        fallback_sql = f"""
            SELECT
                {_division_case_expression('x.census_division')} AS geo_id,
                x.census_division AS geo_name,
                ST_AsGeoJSON(ST_Union_Agg(s.geom)) AS geojson_str
            FROM geo.states s
            INNER JOIN silver.xwalk_state_region x
                ON s.state_fips = x.state_fips
            WHERE s.state_fips IN ({filtered_states_sql})
            GROUP BY 1, 2
            ORDER BY 1
        """

    connection = get_connection()
    try:
        try:
            rows = connection.execute(sql).fetchall()
        except duckdb.Error:
            _load_spatial_extension(connection)
            rows = connection.execute(fallback_sql).fetchall()
    finally:
        connection.close()

    features = [
        {
            "type": "Feature",
            "properties": {"geo_id": geo_id, "geo_name": geo_name},
            "geometry": json.loads(geojson_str),
        }
        for geo_id, geo_name, geojson_str in rows
    ]
    return {"type": "FeatureCollection", "features": features}


def _build_base_query(table_name: str, geo_level: str, state_filter: list[str]) -> tuple[str, list[Any]]:
    params: list[Any] = [geo_level]

    if geo_level == "state":
        state_values = state_filter or list(VALID_STATE_FIPS)
        placeholders = ", ".join(["?"] * len(state_values))
        params.extend(state_values)
        sql = f"""
            SELECT *
            FROM {table_name}
            WHERE lower(geo_level) = ?
              AND geo_id IN ({placeholders})
        """
        return sql, params

    if geo_level == "county":
        state_values = state_filter or list(VALID_STATE_FIPS)
        placeholders = ", ".join(["?"] * len(state_values))
        params.extend(state_values)
        sql = f"""
            SELECT *
            FROM {table_name}
            WHERE lower(geo_level) = ?
              AND substr(geo_id, 1, 2) IN ({placeholders})
        """
        return sql, params

    if geo_level == "cbsa":
        state_values = state_filter or list(VALID_STATE_FIPS)
        placeholders = ", ".join(["?"] * len(state_values))
        params.extend(state_values)
        sql = f"""
            SELECT DISTINCT t.*
            FROM {table_name} t
            INNER JOIN silver.xwalk_cbsa_state x
                ON t.geo_id = x.cbsa_code
            WHERE lower(t.geo_level) = ?
              AND x.state_fips IN ({placeholders})
        """
        return sql, params

    sql = f"""
        SELECT *
        FROM {table_name}
        WHERE lower(geo_level) = ?
    """
    return sql, params


def _compute_housing_growth_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        for column in GROWTH_COLUMNS["housing"]:
            df[column] = pd.Series(dtype="float64")
        return df

    result = df.sort_values(["geo_level", "geo_id", "year"]).copy()
    grouped = result.groupby(["geo_level", "geo_id"])["hu_total"]
    result["hu_growth_1yr"] = grouped.pct_change(periods=1)
    result["hu_growth_3yr"] = grouped.pct_change(periods=3)
    result["hu_growth_5yr"] = grouped.pct_change(periods=5)
    return result


def _normalize_geo_names(df: pd.DataFrame, geo_level: str) -> pd.DataFrame:
    result = df.copy()
    result["geo_level"] = result["geo_level"].str.lower()

    if geo_level == "region":
        result["geo_name"] = result["geo_id"].map(REGION_CODE_TO_NAME).fillna(result["geo_name"])
    elif geo_level == "division":
        result["geo_name"] = result["geo_id"].map(DIVISION_CODE_TO_NAME).fillna(result["geo_name"])

    return result


def _reorder_columns(df: pd.DataFrame, subject_area: str) -> pd.DataFrame:
    base_columns = ["geo_name", "geo_level", "geo_id", "year"]
    growth_columns = [column for column in GROWTH_COLUMNS[subject_area] if column in df.columns]
    metric_columns = [
        column for column in df.columns if column not in set(base_columns) | set(growth_columns)
    ]
    ordered_columns = base_columns + metric_columns + growth_columns
    return df.loc[:, ordered_columns]


@st.cache_data(ttl=3600)
def query_gold(
    geo_level: str,
    subject_area: str,
    year: int,
    state_filter: list[str] | None = None,
) -> pd.DataFrame:
    """Query the Gold layer for a supported subject area and geography."""
    normalized_geo_level = _normalize_geo_level(geo_level)
    normalized_subject_area = _normalize_subject_area(subject_area)
    normalized_state_filter = _normalize_state_filter(state_filter)
    table_name = SUBJECT_AREA_TABLES[normalized_subject_area]

    sql, params = _build_base_query(table_name, normalized_geo_level, normalized_state_filter)
    connection = get_connection()
    try:
        df = connection.execute(sql, params).fetchdf()
    finally:
        connection.close()

    if df.empty:
        return df

    df = _normalize_geo_names(df, normalized_geo_level)

    if normalized_subject_area == "housing":
        df = _compute_housing_growth_columns(df)

    df = df.loc[df["year"] == year].copy()
    df = _reorder_columns(df, normalized_subject_area)
    return df.sort_values(["geo_name", "geo_id"]).reset_index(drop=True)


def merge_for_map(geojson: dict[str, Any], df: pd.DataFrame, kpi_col: str) -> dict[str, Any]:
    """Attach KPI values from a DataFrame onto a GeoJSON FeatureCollection."""
    merged_geojson = deepcopy(geojson)
    if df.empty:
        for feature in merged_geojson.get("features", []):
            properties = feature.setdefault("properties", {})
            properties["kpi_value"] = None
        return merged_geojson

    lookup = df.set_index("geo_id").to_dict(orient="index")
    for feature in merged_geojson.get("features", []):
        properties = feature.setdefault("properties", {})
        geo_id = properties.get("geo_id")
        row = lookup.get(geo_id)
        if row is None:
            properties["kpi_value"] = None
            continue
        properties["geo_name"] = row.get("geo_name", properties.get("geo_name"))
        value = row.get(kpi_col)
        properties["kpi_value"] = None if pd.isna(value) else value
    return merged_geojson


def format_value(value: Any, unit_format: str) -> str:
    """Format a scalar value according to the dashboard display spec."""
    if value is None:
        return "—"
    try:
        if pd.isna(value):
            return "—"
    except TypeError:
        pass

    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return "—"

    if unit_format == "integer":
        return f"{value:,.0f}"
    if unit_format == "percent":
        return f"{value * 100:.1f}%"
    if unit_format == "currency":
        return f"${value:,.0f}"
    if unit_format == "number_1dp":
        return f"{value:.1f}"
    if unit_format in {"ratio", "index"}:
        return f"{value:.2f}"
    if unit_format == "rate_per_1000":
        return f"{value:.1f} per 1,000"
    return str(value)


def format_dataframe(df: pd.DataFrame, metric_meta: list[dict[str, Any]]) -> pd.DataFrame:
    """Apply display formatting to metric columns using metric metadata."""
    formatted = df.copy()
    for metric in metric_meta:
        column_name = metric.get("source_column") or metric.get("name")
        if not column_name or column_name not in formatted.columns:
            continue
        unit_format = metric.get("unit_format", "integer")
        formatted[column_name] = formatted[column_name].map(
            lambda value: format_value(value, unit_format)
        )
    return formatted
