"""Build the app-ready dim_user_poi_v2 dataframe."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

import pandas as pd

from nyc_property_finder.curated_poi.google_takeout.cache import read_details_cache, read_resolution_cache
from nyc_property_finder.curated_poi.google_takeout.config import (
    DEFAULT_DETAILS_CACHE_PATH,
    DEFAULT_RESOLUTION_CACHE_PATH,
)


DIM_USER_POI_V2_COLUMNS = [
    "poi_id",
    "source_system",
    "source_systems",
    "primary_source_system",
    "source_record_id",
    "source_list_names",
    "category",
    "subcategory",
    "detail_level_3",
    "categories",
    "primary_category",
    "subcategories",
    "primary_subcategory",
    "detail_level_3_values",
    "primary_detail_level_3",
    "name",
    "input_title",
    "note",
    "tags",
    "comment",
    "source_url",
    "google_place_id",
    "match_status",
    "address",
    "lat",
    "lon",
    "has_place_details",
    "details_fetched_at",
    "rating",
    "user_rating_count",
    "business_status",
    "editorial_summary",
    "editorial_summary_language_code",
    "price_level",
    "website_uri",
]


def build_dim_user_poi_v2(
    resolution_cache_path: str | Path = DEFAULT_RESOLUTION_CACHE_PATH,
    details_cache_path: str | Path = DEFAULT_DETAILS_CACHE_PATH,
    source_record_ids: set[str] | None = None,
) -> pd.DataFrame:
    """Build one deduplicated POI row per Google place ID."""

    resolution_cache = read_resolution_cache(resolution_cache_path)
    if source_record_ids is not None:
        resolution_cache = resolution_cache[resolution_cache["source_record_id"].isin(source_record_ids)].copy()
    details_cache = read_details_cache(details_cache_path)
    resolved = resolution_cache[resolution_cache["google_place_id"] != ""].copy()
    if resolved.empty:
        return pd.DataFrame(columns=DIM_USER_POI_V2_COLUMNS)

    rows: list[dict[str, Any]] = []
    for google_place_id, group in resolved.groupby("google_place_id", sort=True):
        details_row = details_cache.get(google_place_id, {})
        payload = details_row.get("payload", {}) if isinstance(details_row, dict) else {}
        if not isinstance(payload, dict):
            payload = {}

        # Details payloads are the Google-standardized source for display name,
        # address, and map coordinates. Fall back to source title if needed.
        display_name = payload.get("displayName", {})
        name = display_name.get("text") if isinstance(display_name, dict) else None
        location = payload.get("location", {})
        first = group.iloc[0]

        rows.append(
            {
                "poi_id": _stable_poi_id("google_places", google_place_id),
                "source_system": "google_places",
                "source_systems": _json_array(group["source_system"]),
                "primary_source_system": _fallback_text(first["source_system"]),
                "source_record_id": _json_array(group["source_record_id"]),
                "source_list_names": _json_array(group["source_list_name"]),
                "category": _fallback_category(first["category"]),
                "subcategory": _fallback_subcategory(first["category"], first["subcategory"]),
                "detail_level_3": _first_token(first["detail_level_3"]),
                "categories": _json_array(group["category"].map(_fallback_category)),
                "primary_category": _fallback_category(first["category"]),
                "subcategories": _json_array(
                    group.apply(lambda row: _fallback_subcategory(row["category"], row["subcategory"]), axis=1)
                ),
                "primary_subcategory": _fallback_subcategory(first["category"], first["subcategory"]),
                "detail_level_3_values": _json_array(group["detail_level_3"], split_delimiter="|"),
                "primary_detail_level_3": _first_token(first["detail_level_3"]),
                "name": name or first["input_title"],
                "input_title": first["input_title"],
                "note": _json_array(group["note"]),
                "tags": _json_array(group["tags"]),
                "comment": _json_array(group["comment"]),
                "source_url": _json_array(group["source_url"]),
                "google_place_id": google_place_id,
                "match_status": first["match_status"],
                "address": payload.get("formattedAddress", ""),
                "lat": _location_value(location, "latitude"),
                "lon": _location_value(location, "longitude"),
                "has_place_details": bool(details_row),
                "details_fetched_at": details_row.get("fetched_at", ""),
                "rating": payload.get("rating"),
                "user_rating_count": payload.get("userRatingCount"),
                "business_status": _extract_string(payload.get("businessStatus")),
                "editorial_summary": _extract_localized_text(payload.get("editorialSummary")),
                "editorial_summary_language_code": _extract_localized_language_code(payload.get("editorialSummary")),
                "price_level": _extract_string(payload.get("priceLevel")),
                "website_uri": _extract_string(payload.get("websiteUri")),
            }
        )

    output = pd.DataFrame(rows)
    output["details_fetched_at"] = pd.to_datetime(output["details_fetched_at"], errors="coerce")
    output["lat"] = pd.to_numeric(output["lat"], errors="coerce")
    output["lon"] = pd.to_numeric(output["lon"], errors="coerce")
    output["rating"] = pd.to_numeric(output["rating"], errors="coerce")
    output["user_rating_count"] = pd.to_numeric(output["user_rating_count"], errors="coerce").astype("Int64")
    return output[DIM_USER_POI_V2_COLUMNS]


def _stable_poi_id(source_system: str, stable_source_key: str) -> str:
    key = f"{source_system.strip().lower()}|{stable_source_key.strip()}"
    return f"poi_{sha256(key.encode('utf-8')).hexdigest()[:16]}"


def _json_array(values: pd.Series, split_delimiter: str | None = None) -> str:
    # Store multi-list fields as JSON text for now. This keeps dim_user_poi_v2
    # one-row-per-place while preserving source membership for later modeling.
    cleaned = []
    for value in values.fillna("").astype(str):
        raw_items = [value]
        if split_delimiter:
            raw_items = str(value).split(split_delimiter)
        for item in raw_items:
            item = str(item).strip()
            if item and item not in cleaned:
                cleaned.append(item)
    return json.dumps(cleaned, ensure_ascii=False)


def _fallback_category(category: str) -> str:
    return str(category).strip() or "other"


def _fallback_text(value: str) -> str:
    return str(value).strip()


def _fallback_subcategory(category: str, subcategory: str) -> str:
    cleaned_subcategory = str(subcategory).strip()
    if cleaned_subcategory:
        return cleaned_subcategory
    return _fallback_category(category)


def _first_token(value: str, delimiter: str = "|") -> str:
    for token in str(value).split(delimiter):
        token = token.strip()
        if token:
            return token
    return ""


def _location_value(location: Any, key: str) -> float | None:
    if not isinstance(location, dict):
        return None
    value = location.get(key)
    return float(value) if value not in (None, "") else None


def _extract_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _extract_localized_text(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    return _extract_string(value.get("text"))


def _extract_localized_language_code(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    return _extract_string(value.get("languageCode"))
