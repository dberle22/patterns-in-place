"""Shared Google Places helpers for multiple curated POI ingestion paths."""

from __future__ import annotations

from collections.abc import Callable
import json
from pathlib import Path
from typing import Any

import pandas as pd

from nyc_property_finder.curated_poi.google_takeout.cache import (
    RESOLUTION_CACHE_COLUMNS,
    merge_resolution_cache,
    read_resolution_cache,
    write_resolution_cache,
)
from nyc_property_finder.curated_poi.google_takeout.client import search_text_place_id
from nyc_property_finder.curated_poi.google_takeout.config import (
    DEFAULT_API_KEYS_PATH,
    DEFAULT_ENV_PATH,
    DEFAULT_MAX_TEXT_SEARCH_CALLS,
    DEFAULT_RESOLUTION_CACHE_PATH,
    get_google_maps_api_key,
)


ResolutionFetcher = Callable[[str, str], dict[str, Any]]


def resolve_source_dataframe(
    source_rows: pd.DataFrame,
    *,
    input_path: str,
    api_key: str | None = None,
    resolution_cache_path: str | Path = DEFAULT_RESOLUTION_CACHE_PATH,
    max_text_search_calls: int = DEFAULT_MAX_TEXT_SEARCH_CALLS,
    env_path: str | Path = DEFAULT_ENV_PATH,
    api_keys_path: str | Path = DEFAULT_API_KEYS_PATH,
    fetcher: ResolutionFetcher = search_text_place_id,
) -> "ResolveReport":
    """Resolve source rows that already match the shared pre-resolution contract."""

    api_key = api_key or get_google_maps_api_key(env_path=env_path, api_keys_path=api_keys_path)
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY is required for Places resolution.")

    parsed = _normalize_source_rows(source_rows)
    cache = read_resolution_cache(resolution_cache_path)
    cache = _refresh_cache_source_metadata(cache, parsed)

    cached_source_ids = set(cache.loc[cache["google_place_id"] != "", "source_record_id"])
    parsed_source_ids = set(parsed["source_record_id"])
    input_cached_source_ids = parsed_source_ids & cached_source_ids
    unresolved = parsed[~parsed["source_record_id"].isin(cached_source_ids)].copy()

    if len(unresolved) > max_text_search_calls:
        raise ValueError(
            "Resolve run would exceed max_text_search_calls: "
            f"{len(unresolved)} needed, cap is {max_text_search_calls}."
        )

    new_rows: list[dict[str, str]] = []
    for row in unresolved.to_dict("records"):
        result = fetcher(str(row["search_query"]), api_key)
        new_rows.append(_build_resolution_cache_row(row, result))

        merged_cache = merge_resolution_cache(cache, pd.DataFrame(new_rows))
        write_resolution_cache(merged_cache, resolution_cache_path)

    new_cache_rows = pd.DataFrame(new_rows, columns=RESOLUTION_CACHE_COLUMNS)
    if new_rows or not cache.empty:
        write_resolution_cache(merge_resolution_cache(cache, new_cache_rows), resolution_cache_path)
    resolved = int((new_cache_rows.get("google_place_id", pd.Series(dtype=str)) != "").sum())
    no_match = int((new_cache_rows.get("match_status", pd.Series(dtype=str)) == "no_match").sum())

    from nyc_property_finder.curated_poi.google_takeout.resolve import ResolveReport

    return ResolveReport(
        input_path=input_path,
        resolution_cache_path=str(resolution_cache_path),
        parsed_rows=len(parsed),
        input_cache_hits=len(input_cached_source_ids),
        existing_resolved_cache_rows=len(cached_source_ids),
        attempted_text_search_calls=len(unresolved),
        max_text_search_calls=max_text_search_calls,
        resolved=resolved,
        no_match=no_match,
    )


def build_canonical_dim_from_stages(stage_frames: list[pd.DataFrame], canonical_columns: list[str]) -> pd.DataFrame:
    """Combine stage frames into one canonical-place view."""

    non_empty = [frame.copy() for frame in stage_frames if not frame.empty]
    if not non_empty:
        return pd.DataFrame(columns=canonical_columns)
    if len(non_empty) == 1:
        return non_empty[0][canonical_columns]
    combined = pd.concat(non_empty, ignore_index=True)
    rows = [_merge_stage_group(group, canonical_columns) for _, group in combined.groupby("google_place_id", sort=True)]
    return pd.DataFrame(rows, columns=canonical_columns)


def _normalize_source_rows(source_rows: pd.DataFrame) -> pd.DataFrame:
    required_columns = [
        "source_record_id",
        "source_system",
        "source_file",
        "source_list_name",
        "category",
        "subcategory",
        "detail_level_3",
        "input_title",
        "note",
        "tags",
        "comment",
        "source_url",
        "search_query",
    ]
    output = source_rows.copy()
    for column in required_columns:
        if column not in output.columns:
            output[column] = ""
    return output[required_columns].fillna("")


def _build_resolution_cache_row(source_row: dict[str, Any], result: dict[str, Any]) -> dict[str, str]:
    google_place_id = str(result.get("google_place_id", "") or "")
    match_status = str(result.get("match_status", "top_candidate" if google_place_id else "no_match"))
    return {
        "source_record_id": str(source_row.get("source_record_id", "")),
        "source_system": str(source_row.get("source_system", "")),
        "source_file": str(source_row.get("source_file", "")),
        "source_list_name": str(source_row.get("source_list_name", "")),
        "category": str(source_row.get("category", "")),
        "subcategory": str(source_row.get("subcategory", "")),
        "detail_level_3": str(source_row.get("detail_level_3", "")),
        "input_title": str(source_row.get("input_title", "")),
        "note": str(source_row.get("note", "")),
        "tags": str(source_row.get("tags", "")),
        "comment": str(source_row.get("comment", "")),
        "source_url": str(source_row.get("source_url", "")),
        "search_query": str(source_row.get("search_query", "")),
        "google_place_id": google_place_id,
        "match_status": match_status,
    }


def _refresh_cache_source_metadata(cache: pd.DataFrame, parsed: pd.DataFrame) -> pd.DataFrame:
    if cache.empty:
        return cache

    metadata_columns = [
        "source_system",
        "source_file",
        "source_list_name",
        "category",
        "subcategory",
        "detail_level_3",
        "input_title",
        "note",
        "tags",
        "comment",
        "source_url",
        "search_query",
    ]
    parsed_metadata = parsed.set_index("source_record_id")
    output = cache.copy()
    for index, row in output.iterrows():
        source_record_id = row["source_record_id"]
        if source_record_id not in parsed_metadata.index:
            continue
        for column in metadata_columns:
            if not str(output.at[index, column]).strip():
                output.at[index, column] = str(parsed_metadata.at[source_record_id, column])
    return output


def _merge_stage_group(group: pd.DataFrame, canonical_columns: list[str]) -> dict[str, Any]:
    first = group.iloc[0]
    output: dict[str, Any] = {}
    json_array_columns = {
        "source_systems",
        "source_record_id",
        "source_list_names",
        "categories",
        "subcategories",
        "detail_level_3_values",
        "note",
        "tags",
        "comment",
        "source_url",
    }
    for column in canonical_columns:
        if column in json_array_columns:
            output[column] = _merge_json_text_arrays(group[column])
        elif column == "has_place_details":
            output[column] = bool(group[column].fillna(False).astype(bool).any())
        elif column in {"lat", "lon"}:
            numeric_values = pd.to_numeric(group[column], errors="coerce").dropna()
            output[column] = numeric_values.iloc[0] if not numeric_values.empty else None
        elif column == "details_fetched_at":
            values = pd.to_datetime(group[column], errors="coerce").dropna()
            output[column] = values.max() if not values.empty else pd.NaT
        else:
            output[column] = _first_non_empty(group[column], default=first.get(column))
    return output


def _merge_json_text_arrays(values: pd.Series) -> str:
    cleaned: list[str] = []
    for value in values.fillna(""):
        for item in _coerce_json_text_array(value):
            if item not in cleaned:
                cleaned.append(item)
    return json.dumps(cleaned, ensure_ascii=False)


def _coerce_json_text_array(value: object) -> list[str]:
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return []
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return [raw]
        if isinstance(payload, list):
            return [str(item).strip() for item in payload if str(item).strip()]
        if isinstance(payload, str) and payload.strip():
            return [payload.strip()]
        return []
    if pd.isna(value):
        return []
    text = str(value).strip()
    return [text] if text else []


def _first_non_empty(values: pd.Series, default: object = "") -> object:
    for value in values:
        if pd.isna(value):
            continue
        if isinstance(value, str):
            if value.strip():
                return value
            continue
        return value
    return default
