"""Cache helpers for Google Places POI resolution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from nyc_property_finder.curated_poi.google_takeout.client import (
    PLACE_DETAILS_CACHE_SCHEMA_VERSION,
    PLACE_DETAILS_FIELD_MASK,
)


RESOLUTION_CACHE_COLUMNS = [
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
    "google_place_id",
    "match_status",
]


def read_resolution_cache(path: str | Path) -> pd.DataFrame:
    """Read the source-row to Google place ID cache if it exists."""

    path = Path(path)
    if not path.exists():
        return pd.DataFrame(columns=RESOLUTION_CACHE_COLUMNS)

    cache = pd.read_csv(path, dtype=str).fillna("")
    # Cache files may gain extra audit columns later. The resolver only depends
    # on the stable core columns declared above.
    for column in RESOLUTION_CACHE_COLUMNS:
        if column not in cache.columns:
            cache[column] = ""
    return cache[RESOLUTION_CACHE_COLUMNS]


def write_resolution_cache(cache: pd.DataFrame, path: str | Path) -> None:
    """Write the resolution cache with one latest row per source record."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    output = cache.copy()
    for column in RESOLUTION_CACHE_COLUMNS:
        if column not in output.columns:
            output[column] = ""

    # Re-runs should replace stale attempts for the same source row rather than
    # accumulating duplicate cache entries.
    output = output[RESOLUTION_CACHE_COLUMNS].drop_duplicates(
        subset=["source_record_id"],
        keep="last",
    )
    output.to_csv(path, index=False)


def merge_resolution_cache(existing: pd.DataFrame, new_rows: pd.DataFrame) -> pd.DataFrame:
    """Merge newly resolved rows into the existing resolution cache."""

    frames = [frame for frame in (existing, new_rows) if not frame.empty]
    if not frames:
        return pd.DataFrame(columns=RESOLUTION_CACHE_COLUMNS)
    return pd.concat(frames, ignore_index=True)


def read_details_cache(path: str | Path) -> dict[str, dict[str, Any]]:
    """Read cached Place Details payloads keyed by Google place ID."""

    path = Path(path)
    if not path.exists():
        return {}

    cache: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            google_place_id = row.get("google_place_id")
            payload = row.get("payload")
            if isinstance(google_place_id, str) and google_place_id and isinstance(payload, dict):
                cache[google_place_id] = row
    return cache


def append_details_cache_row(
    google_place_id: str,
    payload: dict[str, Any],
    fetched_at: str,
    path: str | Path,
    field_mask: str = PLACE_DETAILS_FIELD_MASK,
    cache_schema_version: str = PLACE_DETAILS_CACHE_SCHEMA_VERSION,
) -> None:
    """Append one Place Details payload to the JSONL cache."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "google_place_id": google_place_id,
        "fetched_at": fetched_at,
        "field_mask": field_mask,
        "cache_schema_version": cache_schema_version,
        "payload": payload,
    }
    # JSONL appends make the enrichment step interruption-friendly. If a later
    # run refetches the same ID, read_details_cache keeps the latest row.
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def details_cache_row_is_current(row: dict[str, Any]) -> bool:
    """Return True when a cached details row matches the active payload shape."""

    if not isinstance(row, dict):
        return False
    if row.get("cache_schema_version") != PLACE_DETAILS_CACHE_SCHEMA_VERSION:
        return False
    if row.get("field_mask") != PLACE_DETAILS_FIELD_MASK:
        return False
    payload = row.get("payload")
    return isinstance(payload, dict)
