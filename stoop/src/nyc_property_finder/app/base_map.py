"""Reusable map helpers for the Neighborhood Explorer Streamlit app."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
import pydeck as pdk
from shapely.geometry import MultiPolygon, Point, Polygon

from nyc_property_finder.app.explorer import load_optional_table, table_exists
from nyc_property_finder.curated_poi.google_takeout.build_dim import build_dim_user_poi_v2
from nyc_property_finder.curated_poi.google_takeout.cache import read_details_cache
from nyc_property_finder.curated_poi.google_takeout.config import (
    DEFAULT_DETAILS_CACHE_PATH,
    DEFAULT_RESOLUTION_CACHE_PATH,
)
from nyc_property_finder.public_poi.config import CATEGORY_SLUGS
from nyc_property_finder.services.duckdb_service import DuckDBService


GOLD_SCHEMA = "property_explorer_gold"
TRACT_FEATURE_TABLE = f"{GOLD_SCHEMA}.fct_tract_features"
NTA_FEATURE_TABLE = f"{GOLD_SCHEMA}.fct_nta_features"
TRACT_TO_NTA_TABLE = f"{GOLD_SCHEMA}.dim_tract_to_nta"
POI_TABLE = f"{GOLD_SCHEMA}.dim_user_poi"
POI_V2_TABLE = f"{GOLD_SCHEMA}.dim_user_poi_v2"
POI_V3_TABLE = f"{GOLD_SCHEMA}.dim_user_poi_v3"
PUBLIC_POI_TABLE = f"{GOLD_SCHEMA}.dim_public_poi"

BOROUGH_TO_COUNTY_GEOID = {
    "Bronx": "36005",
    "Brooklyn": "36047",
    "Manhattan": "36061",
    "Queens": "36081",
    "Staten Island": "36085",
}
TARGET_BOROUGHS = tuple(BOROUGH_TO_COUNTY_GEOID)
TARGET_COUNTY_GEOIDS = tuple(BOROUGH_TO_COUNTY_GEOID.values())

DEMOGRAPHIC_METRICS: dict[str, dict[str, str]] = {
    "median_income": {"label": "Median household income", "format": "currency"},
    "median_rent": {"label": "Median gross rent", "format": "currency"},
    "median_home_value": {"label": "Median home value", "format": "currency"},
    "pct_bachelors_plus": {"label": "Bachelor's plus", "format": "percent"},
    "median_age": {"label": "Median age", "format": "number"},
}

CORE_PUBLIC_TOOLTIP_CATEGORIES = (
    "grocery_store",
    "citi_bike_station",
    "subway_station",
    "bank",
    "gym",
    "pharmacy",
)

DEFAULT_PUBLIC_POI_SELECTION = ("subway_station",)

BASE_COLUMNS = [
    "tract_id",
    "nta_id",
    "nta_name",
    "borough",
    *DEMOGRAPHIC_METRICS.keys(),
]

POI_COLUMNS = [
    "poi_id",
    "source_list_names",
    "category",
    "subcategory",
    "categories",
    "primary_category",
    "name",
    "input_title",
    "address",
    "lat",
    "lon",
]

POI_COLOR_PALETTE = [
    [205, 83, 64, 230],
    [45, 129, 150, 230],
    [233, 169, 55, 230],
    [92, 111, 191, 230],
    [71, 151, 102, 230],
    [174, 88, 157, 230],
    [39, 98, 113, 230],
    [190, 104, 54, 230],
]

EMPTY_MAP_STATS = {
    "tract_count": 0,
    "neighborhood_count": 0,
    "metric_non_null_count": 0,
    "metric_coverage": 0.0,
}

PUBLIC_POI_COLUMNS = [
    "poi_id",
    "source_system",
    "source_id",
    "category",
    "subcategory",
    "name",
    "address",
    "lat",
    "lon",
    "attributes",
    "snapshotted_at",
]

PUBLIC_POI_CATEGORY_ALIASES = {
    "museum_institution": "museum_institutional",
}

DEFAULT_PUBLIC_POI_CATEGORIES = (
    "atm",
    "bank",
    "citi_bike_station",
    "dog_run",
    "farmers_market",
    "ferry_terminal",
    "grocery_store",
    "gym",
    "hospital",
    "landmark",
    "museum_institutional",
    "park",
    "path_station",
    "pharmacy",
    "post_office",
    "public_art",
    "public_library",
    "subway_station",
    "urgent_care",
)

PUBLIC_POI_COLOR_PALETTE = [
    [50, 112, 194, 190],
    [54, 146, 97, 190],
    [210, 131, 36, 190],
    [177, 83, 77, 190],
    [108, 90, 179, 190],
    [35, 140, 149, 190],
    [144, 112, 58, 190],
    [190, 96, 141, 190],
]


@dataclass(frozen=True)
class BaseGeographyData:
    """Prepared tract and neighborhood geography before metric-specific formatting."""

    tracts: gpd.GeoDataFrame
    neighborhoods: gpd.GeoDataFrame
    stats: dict[str, Any]


@dataclass(frozen=True)
class BaseMapData:
    """Prepared tract and neighborhood map layers."""

    tracts: gpd.GeoDataFrame
    neighborhoods: gpd.GeoDataFrame
    metric: str
    stats: dict[str, Any]


@dataclass(frozen=True)
class PoiMapData:
    """Prepared point-of-interest layer records."""

    points: pd.DataFrame
    source: str
    stats: dict[str, Any]


def metric_label(metric: str) -> str:
    """Return a display label for a demographic metric."""

    return DEMOGRAPHIC_METRICS.get(metric, {}).get("label", metric.replace("_", " ").title())


def metric_options() -> dict[str, str]:
    """Return Streamlit-friendly metric labels keyed by metric column."""

    return {metric: metric_label(metric) for metric in DEMOGRAPHIC_METRICS}


def format_metric_value(value: Any, metric: str) -> str:
    """Format a demographic value for map tooltips and detail tables."""

    if value is None or pd.isna(value):
        return "Unavailable"

    metric_format = DEMOGRAPHIC_METRICS.get(metric, {}).get("format", "number")
    numeric = float(value)
    if metric_format == "currency":
        return f"${numeric:,.0f}"
    if metric_format == "percent":
        percent_value = numeric * 100 if 0 <= numeric <= 1 else numeric
        return f"{percent_value:.1f}%"
    return f"{numeric:g}"


def parse_json_text_array(value: Any) -> list[str]:
    """Parse a JSON text array or scalar value into clean display strings."""

    if isinstance(value, list | tuple | set):
        raw_values = list(value)
    else:
        if value is None or pd.isna(value):
            return []
        text = str(value).strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = text
        raw_values = parsed if isinstance(parsed, list) else [parsed]

    cleaned = []
    for item in raw_values:
        item_text = str(item).strip()
        if item_text and item_text not in cleaned:
            cleaned.append(item_text)
    return cleaned


def format_poi_list_name(value: str) -> str:
    """Return a readable POI source-list label."""

    text = str(value).strip()
    return text if text else "Unlisted POIs"


def format_poi_category(value: Any) -> str:
    """Return a readable POI category label."""

    text = str(value).strip()
    return text.replace("_", " ").title() if text else "Other"


def format_poi_subcategory(value: Any) -> str:
    """Return a readable POI subcategory label."""

    text = str(value).strip()
    if not text or text in {"__unknown__", "nan"}:
        return ""
    if text == "mixed_restaurants":
        return "Mixed Restaurant Scene"
    if text == "restaurants":
        return "General Restaurant Scene"
    return text.replace("_", " ").title()


def canonical_public_poi_category(value: str) -> str:
    """Map UI-friendly public category aliases to stored category slugs."""

    text = str(value).strip()
    if not text:
        return ""
    return PUBLIC_POI_CATEGORY_ALIASES.get(text, text)


def _sql_quote(value: str) -> str:
    """Return a safely single-quoted SQL string literal."""

    return "'" + str(value).replace("'", "''") + "'"


def available_public_poi_categories(poi: pd.DataFrame) -> list[str]:
    """Return sorted public category slugs present in the point dataframe."""

    if poi.empty or "category" not in poi.columns:
        return []
    categories = {
        canonical_public_poi_category(category)
        for category in poi["category"].fillna("").astype(str)
        if str(category).strip()
    }
    return sorted(categories)


def format_public_poi_source(value: Any) -> str:
    """Return a readable public-POI source label."""

    text = str(value).strip()
    if not text:
        return "Unknown source"
    if text == "nyc_open_data":
        return "NYC Open Data"
    if text == "nypl_api":
        return "NYPL API"
    if text == "mta_gtfs":
        return "MTA GTFS"
    if text == "gbfs":
        return "GBFS"
    if text == "osm":
        return "OpenStreetMap"
    return text.replace("_", " ").title()


def normalize_metric_series(values: pd.Series) -> pd.Series:
    """Normalize a numeric series to 0-1 for color ramps."""

    numeric = pd.to_numeric(values, errors="coerce")
    valid = numeric.dropna()
    if valid.empty:
        return pd.Series(0.0, index=values.index)

    min_value = float(valid.min())
    max_value = float(valid.max())
    if min_value == max_value:
        return pd.Series(0.5, index=values.index).where(numeric.notna(), 0.0)

    normalized = (numeric - min_value) / (max_value - min_value)
    return normalized.clip(0, 1).fillna(0.0)


def color_for_value(normalized_value: float, has_value: bool) -> list[int]:
    """Return a muted blue-green ramp color for a normalized metric value."""

    if not has_value:
        return [198, 202, 208, 58]

    t = max(0.0, min(1.0, float(normalized_value)))
    low = (241, 245, 232)
    mid = (91, 169, 157)
    high = (34, 82, 111)
    if t < 0.5:
        local_t = t / 0.5
        start, end = low, mid
    else:
        local_t = (t - 0.5) / 0.5
        start, end = mid, high

    rgb = [round(start[index] + (end[index] - start[index]) * local_t) for index in range(3)]
    return [*rgb, 178]


def add_metric_display_columns(dataframe: gpd.GeoDataFrame, metric: str) -> gpd.GeoDataFrame:
    """Add tooltip and color fields for a selected metric."""

    output = dataframe.copy()
    if metric not in output.columns:
        output[metric] = pd.NA

    numeric = pd.to_numeric(output[metric], errors="coerce")
    normalized = normalize_metric_series(numeric)
    output["selected_metric"] = metric
    output["selected_metric_label"] = metric_label(metric)
    output["selected_metric_value"] = numeric
    output["selected_metric_display"] = [format_metric_value(value, metric) for value in numeric]
    output["metric_available"] = numeric.notna()
    output["fill_color"] = [
        color_for_value(value, has_value)
        for value, has_value in zip(normalized, output["metric_available"], strict=True)
    ]
    return output


def add_demographic_summary_columns(dataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Add formatted demographic fields for summary tooltips."""

    output = dataframe.copy()
    for metric in DEMOGRAPHIC_METRICS:
        if metric not in output.columns:
            output[metric] = pd.NA
        output[f"{metric}_display"] = [
            format_metric_value(value, metric)
            for value in pd.to_numeric(output[metric], errors="coerce")
        ]
    return output


def _count_points_by_geography(
    geography: gpd.GeoDataFrame,
    geography_id_col: str,
    points: pd.DataFrame,
    count_column_prefix: str,
    category_col: str | None = None,
    categories: tuple[str, ...] = (),
) -> gpd.GeoDataFrame:
    """Attach total and optional per-category point counts to a geography layer."""

    output = geography.copy()
    total_column = f"{count_column_prefix}_count_total"
    output[total_column] = 0
    for category in categories:
        output[f"{count_column_prefix}_count_{category}"] = 0

    if output.empty or points.empty or geography_id_col not in output.columns:
        return output

    point_frame = points.copy()
    point_frame["lat"] = pd.to_numeric(point_frame["lat"], errors="coerce")
    point_frame["lon"] = pd.to_numeric(point_frame["lon"], errors="coerce")
    point_frame = point_frame.dropna(subset=["lat", "lon"]).copy()
    if point_frame.empty:
        return output

    point_geo = gpd.GeoDataFrame(
        point_frame,
        geometry=gpd.points_from_xy(point_frame["lon"], point_frame["lat"]),
        crs="EPSG:4326",
    )
    joined = gpd.sjoin(
        point_geo,
        output[[geography_id_col, "geometry"]],
        how="inner",
        predicate="within",
    )
    if joined.empty:
        return output

    total_counts = joined.groupby(geography_id_col).size().rename(total_column)
    output = output.merge(total_counts, on=geography_id_col, how="left", suffixes=("", "_joined"))
    if f"{total_column}_joined" in output.columns:
        output[total_column] = output[f"{total_column}_joined"].fillna(output[total_column]).fillna(0).astype(int)
        output = output.drop(columns=[f"{total_column}_joined"])
    else:
        output[total_column] = output[total_column].fillna(0).astype(int)

    if category_col and categories and category_col in joined.columns:
        joined[category_col] = joined[category_col].fillna("").astype(str)
        for category in categories:
            column = f"{count_column_prefix}_count_{category}"
            category_counts = (
                joined.loc[joined[category_col] == category]
                .groupby(geography_id_col)
                .size()
                .rename(column)
            )
            output = output.merge(category_counts, on=geography_id_col, how="left", suffixes=("", "_joined"))
            if f"{column}_joined" in output.columns:
                output[column] = output[f"{column}_joined"].fillna(output[column]).fillna(0).astype(int)
                output = output.drop(columns=[f"{column}_joined"])
            else:
                output[column] = output[column].fillna(0).astype(int)

    return output


def add_poi_summary_columns(
    dataframe: gpd.GeoDataFrame,
    geography_id_col: str,
    curated_points: pd.DataFrame,
    public_points: pd.DataFrame,
) -> gpd.GeoDataFrame:
    """Attach curated/public POI totals and core public-category counts."""

    output = _count_points_by_geography(
        dataframe,
        geography_id_col=geography_id_col,
        points=curated_points,
        count_column_prefix="curated_poi",
    )
    output = _count_points_by_geography(
        output,
        geography_id_col=geography_id_col,
        points=public_points,
        count_column_prefix="public_poi",
        category_col="category",
        categories=CORE_PUBLIC_TOOLTIP_CATEGORIES,
    )
    output["total_poi_count"] = (
        output["curated_poi_count_total"].fillna(0).astype(int)
        + output["public_poi_count_total"].fillna(0).astype(int)
    )
    return output


def add_tooltip_columns(dataframe: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Add pre-rendered tooltip text for flat PyDeck polygon records."""

    output = dataframe.copy()
    def _count_series(column: str) -> pd.Series:
        if column not in output.columns:
            return pd.Series(0, index=output.index, dtype="int64")
        return pd.to_numeric(output[column], errors="coerce").fillna(0).astype(int)

    shared_metric_details = (
        "<br/>Curated places: "
        + _count_series("curated_poi_count_total").astype(str)
        + "<br/>Public POIs: "
        + _count_series("public_poi_count_total").astype(str)
        + "<br/>Subway stations: "
        + _count_series("public_poi_count_subway_station").astype(str)
        + "<br/>Grocery stores: "
        + _count_series("public_poi_count_grocery_store").astype(str)
        + "<br/>Pharmacies: "
        + _count_series("public_poi_count_pharmacy").astype(str)
    )
    selected_metric_details = (
        "<br/>"
        + output["selected_metric_label"].fillna("Metric").astype(str)
        + ": "
        + output["selected_metric_display"].fillna("Unavailable").astype(str)
    )
    context_details = (
        "<br/>Median household income: "
        + output["median_income_display"].fillna("Unavailable").astype(str)
        + "<br/>Median gross rent: "
        + output["median_rent_display"].fillna("Unavailable").astype(str)
        + "<br/>Median home value: "
        + output["median_home_value_display"].fillna("Unavailable").astype(str)
        + "<br/>Bachelor's plus: "
        + output["pct_bachelors_plus_display"].fillna("Unavailable").astype(str)
        + "<br/>Median age: "
        + output["median_age_display"].fillna("Unavailable").astype(str)
    )

    output["selected_metric_tooltip"] = (
        "<b>"
        + output["nta_name"].fillna("Unavailable").astype(str)
        + "</b><br/>Borough: "
        + output["borough"].fillna("Unavailable").astype(str)
        + "<br/>Tract: "
        + output["tract_id"].fillna("Unavailable").astype(str)
        + selected_metric_details
        + shared_metric_details
    )
    output["neighborhood_metric_tooltip"] = (
        "<b>"
        + output["nta_name"].fillna("Unavailable").astype(str)
        + "</b><br/>Borough: "
        + output["borough"].fillna("Unavailable").astype(str)
        + selected_metric_details
        + shared_metric_details
    )
    output["nta_summary_tooltip"] = (
        "<b>"
        + output["nta_name"].fillna("Unavailable").astype(str)
        + "</b><br/>Borough: "
        + output["borough"].fillna("Unavailable").astype(str)
        + shared_metric_details
        + context_details
    )
    return output


def load_mapping(database_path: str | Path) -> pd.DataFrame:
    """Load the tract-to-NTA mapping from the gold schema."""

    return load_optional_table(
        database_path,
        TRACT_TO_NTA_TABLE,
        ["tract_id", "nta_id", "nta_name", "borough"],
    )


def load_feature_table(
    database_path: str | Path,
    full_table_name: str,
    id_columns: list[str],
) -> pd.DataFrame:
    """Load a demographic feature table with expected metric columns."""

    return load_optional_table(
        database_path,
        full_table_name,
        [*id_columns, "borough", "tract_count", *DEMOGRAPHIC_METRICS.keys()],
    )


def load_curated_poi_count_data(database_path: str | Path) -> pd.DataFrame:
    """Load minimal curated POI columns needed for geography-level counts."""

    if table_exists(database_path, POI_V3_TABLE):
        poi = load_optional_table(database_path, POI_V3_TABLE, ["lat", "lon"])
        if not poi.empty:
            return poi[["lat", "lon"]].copy()
    if table_exists(database_path, POI_V2_TABLE):
        poi = load_optional_table(database_path, POI_V2_TABLE, ["lat", "lon"])
        if not poi.empty:
            return poi[["lat", "lon"]].copy()
    if table_exists(database_path, POI_TABLE):
        poi = load_optional_table(database_path, POI_TABLE, ["lat", "lon"])
        if not poi.empty:
            return poi[["lat", "lon"]].copy()
    return pd.DataFrame(columns=["lat", "lon"])


def load_public_poi_count_data(
    database_path: str | Path,
    selected_categories: tuple[str, ...] = CORE_PUBLIC_TOOLTIP_CATEGORIES,
) -> pd.DataFrame:
    """Load minimal public POI columns needed for geography-level counts."""

    if not table_exists(database_path, PUBLIC_POI_TABLE):
        return pd.DataFrame(columns=["category", "lat", "lon"])

    categories = tuple(
        category
        for category in (
            canonical_public_poi_category(value) for value in selected_categories
        )
        if category in CATEGORY_SLUGS
    )
    if categories:
        literal_categories = ", ".join(_sql_quote(category) for category in categories)
        query = (
            f"SELECT category, lat, lon "
            f"FROM {PUBLIC_POI_TABLE} "
            f"WHERE category IN ({literal_categories})"
        )
    else:
        query = f"SELECT category, lat, lon FROM {PUBLIC_POI_TABLE} WHERE 1 = 0"

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        return duckdb_service.query_df(query)


def load_poi_map_data(
    database_path: str | Path,
    resolution_cache_path: str | Path = DEFAULT_RESOLUTION_CACHE_PATH,
    details_cache_path: str | Path = DEFAULT_DETAILS_CACHE_PATH,
) -> PoiMapData:
    """Load app-ready POIs, preferring DuckDB v3/v2 and falling back to caches."""

    source = "unavailable"
    poi = pd.DataFrame(columns=POI_COLUMNS)

    if table_exists(database_path, POI_V3_TABLE):
        poi = load_optional_table(database_path, POI_V3_TABLE, POI_COLUMNS)
        source = "duckdb_v3"

    if table_exists(database_path, POI_V2_TABLE):
        if poi.empty:
            poi = load_optional_table(database_path, POI_V2_TABLE, POI_COLUMNS)
            source = "duckdb_v2"

    if poi.empty and table_exists(database_path, POI_TABLE):
        legacy = load_optional_table(
            database_path,
            POI_TABLE,
            ["poi_id", "name", "category", "source_list_name", "lat", "lon"],
        )
        if not legacy.empty:
            poi = legacy.rename(
                columns={
                    "category": "category",
                    "source_list_name": "source_list_names",
                }
            )
            poi["subcategory"] = poi["category"]
            poi["primary_category"] = poi["category"]
            poi["categories"] = poi["category"]
            poi["input_title"] = poi["name"]
            poi["address"] = ""
            source = "duckdb_legacy"

    if poi.empty:
        poi = build_dim_user_poi_v2(
            resolution_cache_path=resolution_cache_path,
            details_cache_path=details_cache_path,
        )
        source = "cache_v2" if not poi.empty else source

    if poi.empty:
        poi = _poi_dataframe_from_details_cache(details_cache_path)
        source = "details_cache" if not poi.empty else source

    points = prepare_poi_points(poi)
    return PoiMapData(
        points=points,
        source=source,
        stats={
            "poi_count": int(len(points)),
            "source_list_count": len(available_poi_source_lists(points)),
            "category_count": len(available_poi_categories(points)),
        },
    )


def load_public_poi_map_data(
    database_path: str | Path,
    selected_categories: tuple[str, ...] = DEFAULT_PUBLIC_POI_CATEGORIES,
) -> PoiMapData:
    """Load app-ready public POIs filtered to the selected category set."""

    categories = tuple(
        category
        for category in (
            canonical_public_poi_category(value) for value in selected_categories
        )
        if category in CATEGORY_SLUGS
    )
    if not table_exists(database_path, PUBLIC_POI_TABLE):
        return PoiMapData(
            points=pd.DataFrame(columns=PUBLIC_POI_COLUMNS),
            source="unavailable",
            stats={
                "poi_count": 0,
                "category_count": 0,
                "configured_category_count": len(categories),
            },
        )

    if categories:
        literal_categories = ", ".join(_sql_quote(category) for category in categories)
        query = (
            f"SELECT {', '.join(PUBLIC_POI_COLUMNS)} "
            f"FROM {PUBLIC_POI_TABLE} "
            f"WHERE category IN ({literal_categories})"
        )
    else:
        query = f"SELECT {', '.join(PUBLIC_POI_COLUMNS)} FROM {PUBLIC_POI_TABLE} WHERE 1 = 0"

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        public_poi = duckdb_service.query_df(query)

    points = prepare_public_poi_points(public_poi)
    return PoiMapData(
        points=points,
        source="duckdb_public",
        stats={
            "poi_count": int(len(points)),
            "category_count": len(available_public_poi_categories(points)),
            "configured_category_count": len(categories),
        },
    )


def _poi_dataframe_from_details_cache(details_cache_path: str | Path) -> pd.DataFrame:
    """Build minimal POI records when only Place Details cache rows are available."""

    rows = []
    for google_place_id, row in read_details_cache(details_cache_path).items():
        payload = row.get("payload", {}) if isinstance(row, dict) else {}
        if not isinstance(payload, dict):
            continue
        display_name = payload.get("displayName", {})
        location = payload.get("location", {})
        rows.append(
            {
                "poi_id": f"google_place_{google_place_id}",
                "source_list_names": json.dumps(["Google Places cache"]),
                "categories": json.dumps(["google_places_cache"]),
                "primary_category": "google_places_cache",
                "name": display_name.get("text", google_place_id)
                if isinstance(display_name, dict)
                else google_place_id,
                "input_title": "",
                "address": payload.get("formattedAddress", ""),
                "lat": location.get("latitude") if isinstance(location, dict) else None,
                "lon": location.get("longitude") if isinstance(location, dict) else None,
            }
        )
    return pd.DataFrame(rows, columns=POI_COLUMNS)


def prepare_poi_points(poi: pd.DataFrame) -> pd.DataFrame:
    """Normalize POI records for PyDeck filtering and hover tooltips."""

    output = poi.copy()
    for column in POI_COLUMNS:
        if column not in output.columns:
            output[column] = pd.NA

    output["lat"] = pd.to_numeric(output["lat"], errors="coerce")
    output["lon"] = pd.to_numeric(output["lon"], errors="coerce")
    output = output.dropna(subset=["lat", "lon"]).copy()
    if output.empty:
        return output

    output["source_list_values"] = output["source_list_names"].apply(parse_json_text_array)
    output["source_list_values"] = output["source_list_values"].apply(
        lambda values: values or ["Unlisted POIs"]
    )
    output["primary_source_list"] = output["source_list_values"].apply(
        lambda values: format_poi_list_name(values[0])
    )
    output["source_list_display"] = output["source_list_values"].apply(
        lambda values: ", ".join(format_poi_list_name(value) for value in values)
    )
    output["category_values"] = output["categories"].apply(parse_json_text_array)
    output["category_values"] = [
        values or [canonical_category]
        for values, canonical_category in zip(
            output["category_values"],
            output["category"].fillna("").astype(str),
            strict=True,
        )
    ]
    output["category_display"] = [
        format_poi_category(canonical_category or category or primary)
        for canonical_category, category, primary in zip(
            output["category"].fillna(""),
            output["category_values"].apply(lambda values: values[0] if values else ""),
            output["primary_category"].fillna(""),
            strict=True,
        )
    ]
    output["subcategory_display"] = output["subcategory"].apply(format_poi_subcategory)
    output["poi_color_key"] = [
        f"{category} | {subcategory}" if subcategory else category
        for category, subcategory in zip(
            output["category_display"],
            output["subcategory_display"],
            strict=True,
        )
    ]

    categories = sorted(
        {
            value
            for value in output["poi_color_key"].fillna("").astype(str)
            if str(value).strip()
        }
    )
    color_lookup = {
        category: POI_COLOR_PALETTE[index % len(POI_COLOR_PALETTE)]
        for index, category in enumerate(categories)
    }
    output["poi_color"] = output["poi_color_key"].map(color_lookup).apply(
        lambda color: color if isinstance(color, list) else [205, 83, 64, 230]
    )
    output["tooltip_html"] = (
        "<b>"
        + output["name"].fillna("Unnamed POI").astype(str)
        + "</b><br/>List: "
        + output["source_list_display"].fillna("Unlisted POIs").astype(str)
        + "<br/>Type: "
        + output["category_display"].fillna("Other").astype(str)
    )
    with_subcategory = output["subcategory_display"].ne("")
    output.loc[with_subcategory, "tooltip_html"] = (
        output.loc[with_subcategory, "tooltip_html"]
        + "<br/>Sub Category: "
        + output.loc[with_subcategory, "subcategory_display"]
    )
    output["tooltip_html"] = output["tooltip_html"] + "<br/>" + output["address"].fillna("").astype(str)
    return output


def available_poi_source_lists(poi: pd.DataFrame) -> list[str]:
    """Return sorted source-list labels available in a POI dataframe."""

    if poi.empty or "source_list_values" not in poi.columns:
        return []

    values = set()
    for source_lists in poi["source_list_values"]:
        values.update(format_poi_list_name(value) for value in source_lists)
    return sorted(values)


def available_poi_categories(poi: pd.DataFrame) -> list[str]:
    """Return sorted curated-category labels available in a POI dataframe."""

    if poi.empty or "category_display" not in poi.columns:
        return []

    values = {
        format_poi_category(value)
        for value in poi["category_display"].fillna("").astype(str)
        if str(value).strip()
    }
    return sorted(values)


def available_poi_subcategories(poi: pd.DataFrame) -> list[str]:
    """Return sorted curated subcategory labels available in a POI dataframe."""

    if poi.empty or "subcategory_display" not in poi.columns:
        return []

    values = {
        str(value).strip()
        for value in poi["subcategory_display"].fillna("").astype(str)
        if str(value).strip()
    }
    return sorted(values)


def poi_color_legend_rows(poi: pd.DataFrame) -> pd.DataFrame:
    """Return unique legend rows for visible curated POI colors."""

    if poi.empty:
        return pd.DataFrame(columns=["Category", "Sub Category", "Color"])

    legend = poi[["category_display", "subcategory_display", "poi_color_key", "poi_color"]].copy()
    legend["Category"] = legend["category_display"].fillna("").astype(str)
    legend["Sub Category"] = legend["subcategory_display"].fillna("").astype(str)
    legend["Color"] = legend["poi_color"].apply(
        lambda rgba: "#{:02x}{:02x}{:02x}".format(*rgba[:3]) if isinstance(rgba, list) and len(rgba) >= 3 else ""
    )
    legend = legend.drop_duplicates(subset=["Category", "Sub Category", "poi_color_key", "Color"])
    return legend.sort_values(["Category", "Sub Category", "poi_color_key"]).reset_index(drop=True)[
        ["Category", "Sub Category", "Color"]
    ]


def filter_poi_points_by_categories(
    poi: pd.DataFrame,
    selected_categories: tuple[str, ...],
    selected_subcategories: tuple[str, ...] = (),
) -> pd.DataFrame:
    """Filter POIs to any selected curated category."""

    if poi.empty or not selected_categories:
        return poi.iloc[0:0].copy()

    selected = {format_poi_category(value) for value in selected_categories if str(value).strip()}
    mask = poi["category_display"].apply(lambda value: format_poi_category(value) in selected)
    output = poi.loc[mask].copy()
    if selected_subcategories:
        selected_subcategory_set = {str(value).strip() for value in selected_subcategories if str(value).strip()}
        output = output.loc[
            output["subcategory_display"].fillna("").astype(str).isin(selected_subcategory_set)
        ].copy()
    return output


def prepare_public_poi_points(poi: pd.DataFrame) -> pd.DataFrame:
    """Normalize public POI records for PyDeck filtering and hover tooltips."""

    output = poi.copy()
    for column in PUBLIC_POI_COLUMNS:
        if column not in output.columns:
            output[column] = pd.NA

    output["lat"] = pd.to_numeric(output["lat"], errors="coerce")
    output["lon"] = pd.to_numeric(output["lon"], errors="coerce")
    output["category"] = output["category"].apply(canonical_public_poi_category)
    output = output.dropna(subset=["lat", "lon"]).copy()
    if output.empty:
        return output

    category_order = available_public_poi_categories(output)
    color_lookup = {
        category: PUBLIC_POI_COLOR_PALETTE[index % len(PUBLIC_POI_COLOR_PALETTE)]
        for index, category in enumerate(category_order)
    }
    output["category_display"] = output["category"].apply(format_poi_category)
    output["subcategory_display"] = output["subcategory"].fillna("").astype(str).str.strip()
    output["source_display"] = output["source_system"].apply(format_public_poi_source)
    output["poi_color"] = output["category"].map(color_lookup).apply(
        lambda color: color if isinstance(color, list) else [50, 112, 194, 190]
    )
    output["tooltip_html"] = (
        "<b>"
        + output["name"].fillna("Unnamed POI").astype(str)
        + "</b><br/>Category: "
        + output["category_display"].fillna("Other").astype(str)
        + "<br/>Source: "
        + output["source_display"].fillna("Unknown source").astype(str)
    )
    with_subcategory = output["subcategory_display"].ne("")
    output.loc[with_subcategory, "tooltip_html"] = (
        output.loc[with_subcategory, "tooltip_html"]
        + "<br/>Subtype: "
        + output.loc[with_subcategory, "subcategory_display"]
    )
    with_address = output["address"].fillna("").astype(str).str.strip().ne("")
    output.loc[with_address, "tooltip_html"] = (
        output.loc[with_address, "tooltip_html"]
        + "<br/>"
        + output.loc[with_address, "address"].fillna("").astype(str)
    )
    return output


def filter_public_poi_points_by_categories(
    poi: pd.DataFrame,
    selected_categories: tuple[str, ...],
) -> pd.DataFrame:
    """Filter public POIs to the selected category slugs."""

    if poi.empty or not selected_categories:
        return poi.iloc[0:0].copy()

    selected = {
        canonical_public_poi_category(category)
        for category in selected_categories
        if canonical_public_poi_category(category)
    }
    return poi.loc[poi["category"].isin(selected)].copy()


def filter_points_to_supported_geography(
    points: pd.DataFrame,
    geography: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Filter point rows to those that fall within the loaded tract geography."""

    if points.empty:
        return points.copy()
    if geography.empty or "geometry" not in geography.columns:
        return points.iloc[0:0].copy()

    valid_geometries = geography.geometry.dropna()
    valid_geometries = valid_geometries[~valid_geometries.is_empty]
    if valid_geometries.empty:
        return points.iloc[0:0].copy()

    coverage_geometry = valid_geometries.union_all()
    min_x, min_y, max_x, max_y = coverage_geometry.bounds
    bbox_mask = (
        points["lon"].between(min_x, max_x)
        & points["lat"].between(min_y, max_y)
    )
    if not bbox_mask.any():
        return points.iloc[0:0].copy()

    bounded = points.loc[bbox_mask].copy()
    inside_mask = [
        coverage_geometry.intersects(Point(lon, lat))
        for lon, lat in zip(bounded["lon"], bounded["lat"], strict=True)
    ]
    return bounded.loc[inside_mask].copy()


def load_tract_geometries(
    tract_path: str | Path,
    tract_id_col: str = "GEOID",
    target_county_geoids: tuple[str, ...] = TARGET_COUNTY_GEOIDS,
) -> gpd.GeoDataFrame:
    """Load target Brooklyn and Manhattan tract geometries."""

    tract_path = Path(tract_path)
    if not tract_path.exists():
        raise FileNotFoundError(
            "Tract geometry file is missing: "
            f"{tract_path}. Streamlit Cloud only sees files committed to the repository, "
            "so local-only geography assets must be checked in or downloaded during app startup."
        )

    try:
        tracts = gpd.read_file(tract_path)
    except Exception as exc:
        raise RuntimeError(
            "Unable to read tract geometry file: "
            f"{tract_path}. Confirm that the file is a valid GeoJSON/OGR-readable dataset in the deployed app."
        ) from exc
    if tract_id_col not in tracts.columns:
        raise ValueError(f"Missing tract id column in tract geometry file: {tract_id_col}")

    tracts = tracts.rename(columns={tract_id_col: "tract_id"}).to_crs("EPSG:4326")
    tracts["tract_id"] = (
        tracts["tract_id"]
        .fillna("")
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(11)
    )
    target_mask = tracts["tract_id"].str.startswith(target_county_geoids)
    columns = [
        column
        for column in ["tract_id", "BoroName", "NTA2020", "NTAName", "geometry"]
        if column in tracts.columns
    ]
    return tracts.loc[target_mask, columns].copy()


def attach_tract_attributes(
    tracts: gpd.GeoDataFrame,
    mapping: pd.DataFrame,
    tract_features: pd.DataFrame,
) -> gpd.GeoDataFrame:
    """Attach NTA labels and tract demographic metrics to tract geometries."""

    output = tracts.copy()
    if "BoroName" in output.columns:
        output = output.rename(columns={"BoroName": "geometry_borough"})

    mapping_columns = [
        column
        for column in ["tract_id", "nta_id", "nta_name", "borough"]
        if column in mapping.columns
    ]
    if mapping_columns:
        output = output.merge(
            mapping[mapping_columns].drop_duplicates("tract_id"),
            on="tract_id",
            how="left",
        )

    if "nta_id" not in output.columns and "NTA2020" in output.columns:
        output["nta_id"] = output["NTA2020"]
    if "nta_name" not in output.columns and "NTAName" in output.columns:
        output["nta_name"] = output["NTAName"]
    if "borough" not in output.columns:
        output["borough"] = output.get("geometry_borough", pd.NA)

    feature_columns = [
        column
        for column in ["tract_id", *DEMOGRAPHIC_METRICS.keys()]
        if column in tract_features.columns
    ]
    if feature_columns:
        output = output.merge(
            tract_features[feature_columns].drop_duplicates("tract_id"),
            on="tract_id",
            how="left",
        )

    for column in BASE_COLUMNS:
        if column not in output.columns:
            output[column] = pd.NA
    return output[BASE_COLUMNS + ["geometry"]].copy()


def build_neighborhood_geometries(
    tract_map: gpd.GeoDataFrame,
    nta_features: pd.DataFrame,
) -> gpd.GeoDataFrame:
    """Dissolve tracts into neighborhood boundaries and attach NTA-native metrics."""

    if tract_map.empty:
        return gpd.GeoDataFrame(
            columns=BASE_COLUMNS + ["geometry"],
            geometry="geometry",
            crs="EPSG:4326",
        )

    dissolved = (
        tract_map.dissolve(
            by=["nta_id", "nta_name", "borough"],
            as_index=False,
            dropna=False,
        )[["nta_id", "nta_name", "borough", "geometry"]]
        .copy()
    )

    feature_columns = [
        column
        for column in ["nta_id", "nta_name", "borough", "tract_count", *DEMOGRAPHIC_METRICS.keys()]
        if column in nta_features.columns
    ]
    if feature_columns:
        dissolved = dissolved.merge(
            nta_features[feature_columns].drop_duplicates("nta_id"),
            on=["nta_id", "nta_name"] if "nta_name" in feature_columns else ["nta_id"],
            how="left",
            suffixes=("", "_feature"),
        )
        if "borough_feature" in dissolved.columns:
            dissolved["borough"] = dissolved["borough_feature"].combine_first(dissolved["borough"])
            dissolved = dissolved.drop(columns=["borough_feature"])

    for metric in DEMOGRAPHIC_METRICS:
        if metric not in dissolved.columns:
            dissolved[metric] = pd.NA
    if "tract_id" not in dissolved.columns:
        dissolved["tract_id"] = pd.NA
    return dissolved[BASE_COLUMNS + ["geometry"]].copy()


def load_base_geography_data(
    database_path: str | Path,
    tract_path: str | Path,
    tract_id_col: str = "GEOID",
 ) -> BaseGeographyData:
    """Load geography, feature, and POI-summary inputs shared across metrics."""

    mapping = load_mapping(database_path)
    tract_features = load_feature_table(database_path, TRACT_FEATURE_TABLE, ["tract_id"])
    nta_features = load_feature_table(database_path, NTA_FEATURE_TABLE, ["nta_id", "nta_name"])
    curated_poi_points = load_curated_poi_count_data(database_path)
    public_poi_points = load_public_poi_count_data(
        database_path,
        selected_categories=CORE_PUBLIC_TOOLTIP_CATEGORIES,
    )

    tracts = load_tract_geometries(tract_path, tract_id_col=tract_id_col)
    tract_map = attach_tract_attributes(tracts, mapping, tract_features)
    neighborhoods = build_neighborhood_geometries(tract_map, nta_features)
    tract_map = add_poi_summary_columns(
        tract_map,
        geography_id_col="tract_id",
        curated_points=curated_poi_points,
        public_points=public_poi_points,
    )
    neighborhoods = add_poi_summary_columns(
        neighborhoods,
        geography_id_col="nta_id",
        curated_points=curated_poi_points,
        public_points=public_poi_points,
    )
    tract_map = add_demographic_summary_columns(tract_map)
    neighborhoods = add_demographic_summary_columns(neighborhoods)

    return BaseGeographyData(
        tracts=tract_map,
        neighborhoods=neighborhoods,
        stats={
            "tract_count": int(len(tract_map)),
            "neighborhood_count": (
                int(neighborhoods["nta_id"].nunique(dropna=True))
                if "nta_id" in neighborhoods
                else 0
            ),
            "database_ready": Path(database_path).exists(),
            "mapping_ready": table_exists(database_path, TRACT_TO_NTA_TABLE),
            "tract_features_ready": table_exists(database_path, TRACT_FEATURE_TABLE),
            "nta_features_ready": table_exists(database_path, NTA_FEATURE_TABLE),
        },
    )


def build_base_map_data_from_loaded(
    geography_data: BaseGeographyData,
    metric: str = "median_income",
) -> BaseMapData:
    """Apply the selected metric to preloaded geography layers."""

    if metric not in DEMOGRAPHIC_METRICS:
        raise ValueError(f"Unsupported demographic metric: {metric}")

    tract_map = add_tooltip_columns(add_metric_display_columns(geography_data.tracts, metric))
    neighborhoods = add_tooltip_columns(add_metric_display_columns(geography_data.neighborhoods, metric))

    metric_values = (
        pd.to_numeric(tract_map[metric], errors="coerce")
        if metric in tract_map
        else pd.Series(dtype="float64")
    )
    stats = {
        **geography_data.stats,
        "metric_non_null_count": int(metric_values.notna().sum()),
        "metric_coverage": float(metric_values.notna().mean()) if len(metric_values) else 0.0,
        "metric_label": metric_label(metric),
    }

    return BaseMapData(tracts=tract_map, neighborhoods=neighborhoods, metric=metric, stats=stats)


def prepare_base_map_data(
    database_path: str | Path,
    tract_path: str | Path,
    tract_id_col: str = "GEOID",
    metric: str = "median_income",
) -> BaseMapData:
    """Backward-compatible wrapper that loads geography then applies a metric."""

    geography_data = load_base_geography_data(
        database_path=database_path,
        tract_path=tract_path,
        tract_id_col=tract_id_col,
    )
    return build_base_map_data_from_loaded(geography_data, metric=metric)


def _polygon_coordinates(geometry: Polygon) -> list[list[list[float]]]:
    exterior = [[float(x), float(y)] for x, y in geometry.exterior.coords]
    interiors = [
        [[float(x), float(y)] for x, y in interior.coords]
        for interior in geometry.interiors
    ]
    return [exterior, *interiors]


def _polygon_records(dataframe: gpd.GeoDataFrame, tooltip_column: str) -> list[dict[str, Any]]:
    display_columns = [
        "tract_id",
        "nta_id",
        "nta_name",
        "borough",
        "selected_metric_label",
        "selected_metric_display",
        "metric_available",
        "fill_color",
        *[f"{metric}_display" for metric in DEMOGRAPHIC_METRICS],
        tooltip_column,
    ]
    available_columns = [column for column in display_columns if column in dataframe.columns]
    records = []
    for row in dataframe[[*available_columns, "geometry"]].itertuples(index=False):
        record = {
            column: getattr(row, column)
            for column in available_columns
            if column != "geometry"
        }
        record["tooltip_html"] = record.get(tooltip_column, "")
        geometry = row.geometry
        if geometry is None or geometry.is_empty:
            continue
        simplified = geometry.simplify(0.00008, preserve_topology=True)
        polygons = simplified.geoms if isinstance(simplified, MultiPolygon) else [simplified]
        for polygon in polygons:
            if not isinstance(polygon, Polygon) or polygon.is_empty:
                continue
            records.append({**record, "polygon": _polygon_coordinates(polygon)})
    return records


def build_base_map_deck(
    map_data: BaseMapData,
    layer_mode: str = "Tracts",
    show_demographics: bool = True,
    poi_points: pd.DataFrame | None = None,
    show_pois: bool = False,
    public_poi_points: pd.DataFrame | None = None,
    show_public_pois: bool = False,
    selected_nta_id: str | None = None,
    center_lat: float = 40.7128,
    center_lon: float = -74.0060,
    zoom: int = 10,
) -> pdk.Deck:
    """Build a PyDeck map for the selected geography layer."""

    show_neighborhoods = layer_mode == "Neighborhoods"
    demographic_layer = map_data.neighborhoods if show_neighborhoods else map_data.tracts

    layers = []
    demographic_tooltip = "neighborhood_metric_tooltip" if show_neighborhoods else "selected_metric_tooltip"

    if show_demographics:
        layers.append(
            pdk.Layer(
                "PolygonLayer",
                id="demographic-fill",
                data=_polygon_records(demographic_layer, demographic_tooltip),
                get_polygon="polygon",
                stroked=True,
                filled=True,
                get_fill_color="fill_color",
                get_line_color=[22, 28, 32, 145],
                get_line_width=46 if show_neighborhoods else 26,
                line_width_min_pixels=1,
                pickable=True,
                auto_highlight=True,
            )
        )
    if show_neighborhoods and not show_demographics:
        layers.append(
            pdk.Layer(
                "PolygonLayer",
                id="neighborhood-boundaries",
                data=_polygon_records(map_data.neighborhoods, "nta_summary_tooltip"),
                get_polygon="polygon",
                stroked=True,
                filled=True,
                get_line_color=[0, 0, 0, 210],
                get_line_width=46,
                line_width_min_pixels=1,
                get_fill_color=[0, 0, 0, 0],
                pickable=True,
                auto_highlight=True,
                highlight_color=[0, 0, 0, 28],
            )
        )
    if not show_neighborhoods:
        layers.append(
            pdk.Layer(
                "PolygonLayer",
                id="nta-boundaries",
                data=_polygon_records(map_data.neighborhoods, "nta_summary_tooltip"),
                get_polygon="polygon",
                stroked=True,
                filled=not show_demographics,
                get_line_color=[0, 0, 0, 210],
                get_line_width=46,
                line_width_min_pixels=1,
                get_fill_color=[0, 0, 0, 0],
                pickable=not show_demographics,
                auto_highlight=not show_demographics,
                highlight_color=[0, 0, 0, 28],
            )
        )

    if selected_nta_id:
        selected_neighborhoods = map_data.neighborhoods.loc[
            map_data.neighborhoods["nta_id"].fillna("").astype(str) == str(selected_nta_id)
        ].copy()
        if not selected_neighborhoods.empty:
            layers.append(
                pdk.Layer(
                    "PolygonLayer",
                    id="selected-nta-highlight",
                    data=_polygon_records(selected_neighborhoods, "nta_summary_tooltip"),
                    get_polygon="polygon",
                    stroked=True,
                    filled=True,
                    get_line_color=[201, 87, 52, 255],
                    get_line_width=70,
                    line_width_min_pixels=3,
                    get_fill_color=[201, 87, 52, 24],
                    pickable=True,
                    auto_highlight=False,
                )
            )

    if show_pois and poi_points is not None and not poi_points.empty:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                id="poi-points",
                data=poi_points.to_dict("records"),
                get_position="[lon, lat]",
                get_fill_color="poi_color",
                get_line_color=[255, 255, 255, 230],
                get_radius=48,
                radius_min_pixels=5,
                radius_max_pixels=13,
                stroked=True,
                line_width_min_pixels=1,
                pickable=True,
                auto_highlight=True,
                highlight_color=[255, 255, 255, 90],
            )
        )

    if show_public_pois and public_poi_points is not None and not public_poi_points.empty:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                id="public-poi-points",
                data=public_poi_points.to_dict("records"),
                get_position="[lon, lat]",
                get_fill_color="poi_color",
                get_line_color=[255, 255, 255, 210],
                get_radius=34,
                radius_min_pixels=4,
                radius_max_pixels=10,
                stroked=True,
                line_width_min_pixels=1,
                pickable=True,
                auto_highlight=True,
                highlight_color=[255, 255, 255, 90],
            )
        )

    view_state = pdk.ViewState(latitude=center_lat, longitude=center_lon, zoom=zoom, pitch=0)
    return pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="light",
        tooltip={"html": "{tooltip_html}"},
    )
