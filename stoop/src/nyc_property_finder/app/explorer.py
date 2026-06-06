"""Testable helpers for the Property Explorer Streamlit app."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from nyc_property_finder.services.duckdb_service import DuckDBService


GOLD_SCHEMA = "property_explorer_gold"
CONTEXT_TABLE = f"{GOLD_SCHEMA}.fct_property_context"
POI_TABLE = f"{GOLD_SCHEMA}.dim_user_poi"
SUBWAY_TABLE = f"{GOLD_SCHEMA}.dim_subway_stop"
NTA_FEATURE_TABLE = f"{GOLD_SCHEMA}.fct_nta_features"
SHORTLIST_TABLE = f"{GOLD_SCHEMA}.fct_user_shortlist"

CONTEXT_COLUMNS = [
    "property_id",
    "source",
    "source_listing_id",
    "address",
    "lat",
    "lon",
    "price",
    "beds",
    "baths",
    "listing_type",
    "active",
    "url",
    "ingest_timestamp",
    "tract_id",
    "nta_id",
    "nta_name",
    "nearest_subway_stop",
    "nearest_subway_distance_miles",
    "subway_lines_count",
    "poi_data_available",
    "poi_count_nearby",
    "poi_count_10min",
    "poi_category_counts",
    "neighborhood_score",
    "neighborhood_score_status",
    "mobility_score",
    "personal_fit_score",
    "personal_fit_score_status",
    "property_fit_score",
    "property_fit_score_status",
]


@dataclass(frozen=True)
class PropertyFilters:
    """Filter values selected in the Streamlit sidebar."""

    include_inactive: bool = False
    listing_types: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()
    ntas: tuple[str, ...] = ()
    price_min: float | None = None
    price_max: float | None = None
    min_beds: float | None = None
    min_baths: float | None = None
    max_subway_distance_miles: float | None = None
    min_property_fit_score: float | None = None
    min_mobility_score: float | None = None
    min_personal_fit_score: float | None = None
    poi_categories: tuple[str, ...] = ()
    shortlist_statuses: tuple[str, ...] = ()


@dataclass(frozen=True)
class SortOption:
    """Sort definition for listing cards."""

    label: str
    columns: tuple[str, ...]
    ascending: tuple[bool, ...]


SORT_OPTIONS: dict[str, SortOption] = {
    "Best overall fit": SortOption(
        label="Best overall fit",
        columns=("property_fit_score", "price", "address", "property_id"),
        ascending=(False, True, True, True),
    ),
    "Highest personal fit": SortOption(
        label="Highest personal fit",
        columns=("personal_fit_score", "price", "address", "property_id"),
        ascending=(False, True, True, True),
    ),
    "Best mobility": SortOption(
        label="Best mobility",
        columns=("mobility_score", "price", "address", "property_id"),
        ascending=(False, True, True, True),
    ),
    "Nearest subway": SortOption(
        label="Nearest subway",
        columns=("nearest_subway_distance_miles", "price", "address", "property_id"),
        ascending=(True, True, True, True),
    ),
    "Lowest price": SortOption(
        label="Lowest price",
        columns=("price", "address", "property_id"),
        ascending=(True, True, True),
    ),
    "Highest price": SortOption(
        label="Highest price",
        columns=("price", "address", "property_id"),
        ascending=(False, True, True),
    ),
    "Most beds": SortOption(
        label="Most beds",
        columns=("beds", "price", "address", "property_id"),
        ascending=(False, True, True, True),
    ),
    "Neighborhood then price": SortOption(
        label="Neighborhood then price",
        columns=("nta_name", "price", "address", "property_id"),
        ascending=(True, True, True, True),
    ),
}

STATUS_LABELS = {
    "scored": "Scored",
    "partial": "Partially scored",
    "unavailable": "Unavailable",
    "reweighted_missing_components": "Reweighted",
}


def table_exists(database_path: str | Path, full_table_name: str) -> bool:
    """Return whether a DuckDB table exists."""

    db_path = Path(database_path)
    if not db_path.exists() or "." not in full_table_name:
        return False

    schema, table = full_table_name.split(".", maxsplit=1)
    with DuckDBService(db_path, read_only=True) as duckdb_service:
        result = duckdb_service.query_df(
            """
            SELECT COUNT(*) AS table_count
            FROM information_schema.tables
            WHERE table_schema = $schema
              AND table_name = $table
            """,
            {"schema": schema, "table": table},
        )
    return int(result["table_count"].iloc[0]) > 0


def load_optional_table(
    database_path: str | Path,
    full_table_name: str,
    expected_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Load a table if available, otherwise return an empty dataframe."""

    if not table_exists(database_path, full_table_name):
        return ensure_columns(pd.DataFrame(), expected_columns or [])

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        try:
            dataframe = duckdb_service.query_df(f"SELECT * FROM {full_table_name}")
        except Exception:
            dataframe = pd.DataFrame()

    return ensure_columns(dataframe, expected_columns or [])


def ensure_columns(dataframe: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Ensure a dataframe exposes expected columns for null-safe app rendering."""

    output = dataframe.copy()
    for column in columns:
        if column not in output.columns:
            output[column] = pd.NA
    return output


def parse_poi_category_counts(value: Any) -> dict[str, int]:
    """Parse persisted POI category JSON into an integer dictionary."""

    if value is None or pd.isna(value):
        return {}
    if isinstance(value, dict):
        raw_counts = value
    elif isinstance(value, str):
        if not value.strip():
            return {}
        try:
            raw_counts = json.loads(value)
        except json.JSONDecodeError:
            return {}
    else:
        return {}

    if not isinstance(raw_counts, dict):
        return {}

    counts: dict[str, int] = {}
    for category, count in raw_counts.items():
        try:
            numeric_count = int(count)
        except (TypeError, ValueError):
            continue
        if numeric_count > 0:
            counts[str(category)] = numeric_count
    return counts


def available_poi_categories(context: pd.DataFrame) -> list[str]:
    """Return sorted POI categories present in context category-count JSON."""

    categories: set[str] = set()
    if "poi_category_counts" not in context.columns:
        return []
    for value in context["poi_category_counts"]:
        categories.update(parse_poi_category_counts(value).keys())
    return sorted(categories)


def _series_numeric(dataframe: pd.DataFrame, column: str) -> pd.Series:
    if column not in dataframe.columns:
        return pd.Series(pd.NA, index=dataframe.index, dtype="Float64")
    return pd.to_numeric(dataframe[column], errors="coerce")


def _series_text(dataframe: pd.DataFrame, column: str) -> pd.Series:
    if column not in dataframe.columns:
        return pd.Series("", index=dataframe.index, dtype="string")
    return dataframe[column].fillna("").astype(str)


def _has_selected_poi_category(value: Any, selected_categories: tuple[str, ...]) -> bool:
    if not selected_categories:
        return True
    counts = parse_poi_category_counts(value)
    return any(counts.get(category, 0) > 0 for category in selected_categories)


def apply_property_filters(
    context: pd.DataFrame,
    filters: PropertyFilters,
) -> pd.DataFrame:
    """Apply sidebar filters to property context rows."""

    filtered = context.copy()
    if filtered.empty:
        return filtered

    if not filters.include_inactive and "active" in filtered.columns:
        filtered = filtered[filtered["active"].fillna(False).astype(bool)]

    if filters.listing_types and "listing_type" in filtered.columns:
        filtered = filtered[_series_text(filtered, "listing_type").isin(filters.listing_types)]

    if filters.sources and "source" in filtered.columns:
        filtered = filtered[_series_text(filtered, "source").isin(filters.sources)]

    if filters.ntas and "nta_name" in filtered.columns:
        filtered = filtered[_series_text(filtered, "nta_name").isin(filters.ntas)]

    if filters.price_min is not None:
        filtered = filtered[_series_numeric(filtered, "price") >= filters.price_min]
    if filters.price_max is not None:
        filtered = filtered[_series_numeric(filtered, "price") <= filters.price_max]

    if filters.min_beds is not None:
        filtered = filtered[_series_numeric(filtered, "beds") >= filters.min_beds]
    if filters.min_baths is not None:
        filtered = filtered[_series_numeric(filtered, "baths") >= filters.min_baths]

    if filters.max_subway_distance_miles is not None:
        filtered = filtered[
            _series_numeric(filtered, "nearest_subway_distance_miles")
            <= filters.max_subway_distance_miles
        ]

    score_filters = {
        "property_fit_score": filters.min_property_fit_score,
        "mobility_score": filters.min_mobility_score,
        "personal_fit_score": filters.min_personal_fit_score,
    }
    for column, threshold in score_filters.items():
        if threshold is not None:
            filtered = filtered[_series_numeric(filtered, column) >= threshold]

    if filters.poi_categories and "poi_category_counts" in filtered.columns:
        mask = filtered["poi_category_counts"].apply(
            lambda value: _has_selected_poi_category(value, filters.poi_categories)
        )
        filtered = filtered[mask]

    if filters.shortlist_statuses and "shortlist_status" in filtered.columns:
        filtered = filtered[_series_text(filtered, "shortlist_status").isin(filters.shortlist_statuses)]

    return filtered


def sort_properties(context: pd.DataFrame, sort_label: str) -> pd.DataFrame:
    """Sort property context rows using a named Sprint 4 sort option."""

    if context.empty:
        return context.copy()

    option = SORT_OPTIONS.get(sort_label, SORT_OPTIONS["Best overall fit"])
    sorted_context = context.copy()
    sort_columns: list[str] = []
    ascending: list[bool] = []
    for column, column_ascending in zip(option.columns, option.ascending, strict=True):
        if column in sorted_context.columns:
            sort_columns.append(column)
            ascending.append(column_ascending)

    if not sort_columns:
        return sorted_context

    return sorted_context.sort_values(
        by=sort_columns,
        ascending=ascending,
        na_position="last",
        kind="mergesort",
    )


def selected_property_id(current_selection: str | None, visible_properties: pd.DataFrame) -> str | None:
    """Return a valid selected property ID for the visible set."""

    if visible_properties.empty or "property_id" not in visible_properties.columns:
        return None
    property_ids = visible_properties["property_id"].dropna().astype(str).tolist()
    if not property_ids:
        return None
    if current_selection in property_ids:
        return current_selection
    return property_ids[0]


def score_label(value: Any) -> str:
    """Format a score for display without turning nulls into zeroes."""

    if value is None or pd.isna(value):
        return "Unavailable"
    return f"{float(value):.0f}/100"


def status_label(status: Any) -> str:
    """Format score status values for display."""

    if status is None or pd.isna(status) or not str(status).strip():
        return "Unknown"
    return STATUS_LABELS.get(str(status), str(status).replace("_", " ").title())


def score_status_message(component: str, status: Any) -> str:
    """Return user-facing score status copy."""

    normalized = "" if status is None or pd.isna(status) else str(status)
    if component == "neighborhood" and normalized == "unavailable":
        return (
            "Neighborhood metrics are unavailable because the current Metro Deep Dive "
            "NYC tract metric inputs are null."
        )
    if component == "personal_fit" and normalized == "scored":
        return "Personal fit uses loaded Google Maps saved places and straight-line nearby counts."
    if component == "personal_fit" and normalized == "unavailable":
        return "Personal fit is unavailable because POI data is absent."
    if component == "property_fit" and normalized == "reweighted_missing_components":
        return "Total fit is reweighted across available components; neighborhood scoring is missing."
    if normalized == "scored":
        return "Score is available."
    if normalized == "unavailable":
        return "Score is unavailable."
    return status_label(normalized)


def join_shortlist_status(context: pd.DataFrame, shortlist: pd.DataFrame) -> pd.DataFrame:
    """Attach shortlist status and notes to current context rows."""

    output = context.copy()
    if "property_id" not in output.columns:
        return output
    if shortlist.empty or "property_id" not in shortlist.columns:
        output["shortlist_status"] = pd.NA
        output["shortlist_notes"] = pd.NA
        return output

    shortlist_columns = [
        column
        for column in ["property_id", "status", "notes", "saved_timestamp", "updated_timestamp"]
        if column in shortlist.columns
    ]
    joined_shortlist = shortlist[shortlist_columns].copy()
    rename_map = {
        "status": "shortlist_status",
        "notes": "shortlist_notes",
        "saved_timestamp": "shortlist_saved_timestamp",
        "updated_timestamp": "shortlist_updated_timestamp",
    }
    joined_shortlist = joined_shortlist.rename(columns=rename_map)
    return output.merge(joined_shortlist, on="property_id", how="left")


def make_shortlist_id(user_id: str, property_id: str) -> str:
    """Create a stable shortlist row ID for one local user/listing pair."""

    digest = hashlib.sha1(f"{user_id}:{property_id}".encode("utf-8")).hexdigest()[:16]
    return f"shortlist_{digest}"


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def load_shortlist(database_path: str | Path, user_id: str) -> pd.DataFrame:
    """Load all shortlist rows for the configured local user."""

    if not table_exists(database_path, SHORTLIST_TABLE):
        return pd.DataFrame()
    with DuckDBService(database_path, read_only=True) as duckdb_service:
        return duckdb_service.query_df(
            f"""
            SELECT *
            FROM {SHORTLIST_TABLE}
            WHERE user_id = $user_id
            """,
            {"user_id": user_id},
        )


def upsert_shortlist_row(
    database_path: str | Path,
    user_id: str,
    property_id: str,
    status: str = "active",
    notes: str | None = None,
    metadata_json: str | None = None,
) -> str:
    """Insert or update one persisted shortlist row."""

    if status not in {"active", "archived", "rejected"}:
        raise ValueError("status must be one of: active, archived, rejected")

    db_path = Path(database_path)
    shortlist_id = make_shortlist_id(user_id, property_id)
    now = _utc_now_iso()
    with DuckDBService(db_path) as duckdb_service:
        existing = duckdb_service.query_df(
            f"""
            SELECT saved_timestamp, notes, metadata_json
            FROM {SHORTLIST_TABLE}
            WHERE user_id = $user_id
              AND property_id = $property_id
            """,
            {"user_id": user_id, "property_id": property_id},
        )

        if existing.empty:
            duckdb_service.execute(
                f"""
                INSERT INTO {SHORTLIST_TABLE}
                (shortlist_id, user_id, property_id, saved_timestamp, updated_timestamp,
                 status, notes, metadata_json)
                VALUES ($shortlist_id, $user_id, $property_id, $saved_timestamp,
                        $updated_timestamp, $status, $notes, $metadata_json)
                """,
                {
                    "shortlist_id": shortlist_id,
                    "user_id": user_id,
                    "property_id": property_id,
                    "saved_timestamp": now,
                    "updated_timestamp": now,
                    "status": status,
                    "notes": notes,
                    "metadata_json": metadata_json,
                },
            )
        else:
            current = existing.iloc[0]
            duckdb_service.execute(
                f"""
                UPDATE {SHORTLIST_TABLE}
                SET updated_timestamp = $updated_timestamp,
                    status = $status,
                    notes = $notes,
                    metadata_json = $metadata_json
                WHERE user_id = $user_id
                  AND property_id = $property_id
                """,
                {
                    "updated_timestamp": now,
                    "status": status,
                    "notes": notes if notes is not None else current.get("notes"),
                    "metadata_json": metadata_json
                    if metadata_json is not None
                    else current.get("metadata_json"),
                    "user_id": user_id,
                    "property_id": property_id,
                },
            )

    return shortlist_id


def summarize_visible_properties(properties: pd.DataFrame) -> dict[str, Any]:
    """Return compact metrics for the visible listing set."""

    if properties.empty:
        return {"count": 0, "min_price": None, "max_price": None, "median_fit": None}
    return {
        "count": len(properties),
        "min_price": _series_numeric(properties, "price").min(),
        "max_price": _series_numeric(properties, "price").max(),
        "median_fit": _series_numeric(properties, "property_fit_score").median(),
    }


def display_category_counts(value: Any) -> str:
    """Format POI category counts for listing cards and detail."""

    counts = parse_poi_category_counts(value)
    if not counts:
        return "No nearby personal POIs in the MVP radius"
    return ", ".join(f"{category.replace('_', ' ')}: {count}" for category, count in sorted(counts.items()))
