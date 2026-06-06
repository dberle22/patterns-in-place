"""Dry-run planning for the Google Places POI workflow."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from nyc_property_finder.curated_poi.google_takeout.cache import details_cache_row_is_current, read_resolution_cache
from nyc_property_finder.curated_poi.google_takeout.config import (
    DEFAULT_DETAILS_CACHE_PATH,
    DEFAULT_RESOLUTION_CACHE_PATH,
    DEFAULT_SEARCH_CONTEXT,
)
from nyc_property_finder.curated_poi.google_takeout.parse_takeout import parse_google_places_saved_list_csv


@dataclass(frozen=True)
class DryRunReport:
    """Summary of expected API work before making any Google calls."""

    input_path: str
    search_context: str
    input_rows: int
    unique_source_records: int
    resolution_cache_path: str
    details_cache_path: str
    resolution_cache_hits: int
    resolution_cache_misses: int
    cached_google_place_ids: int
    details_cache_hits: int
    details_cache_misses_for_cached_places: int
    estimated_text_search_calls: int
    estimated_place_details_calls: int
    categories: list[str]
    subcategories: list[str]
    detail_level_3_values: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dict for logging, notebooks, or future CLI output."""

        return asdict(self)


def plan_dry_run(
    csv_path: str | Path,
    resolution_cache_path: str | Path = DEFAULT_RESOLUTION_CACHE_PATH,
    details_cache_path: str | Path = DEFAULT_DETAILS_CACHE_PATH,
    search_context: str = DEFAULT_SEARCH_CONTEXT,
) -> DryRunReport:
    """Estimate cache coverage and API calls for one saved-list CSV."""

    csv_path = Path(csv_path)
    parsed = parse_google_places_saved_list_csv(csv_path, search_context=search_context)
    source_record_ids = set(parsed["source_record_id"].dropna().astype(str))

    resolution_cache = read_resolution_cache(resolution_cache_path)
    cached_resolutions = resolution_cache[resolution_cache["source_record_id"].isin(source_record_ids)]
    cached_resolutions = cached_resolutions[cached_resolutions["google_place_id"] != ""]

    cached_source_ids = set(cached_resolutions["source_record_id"])
    cached_place_ids = set(cached_resolutions["google_place_id"])
    details_place_ids = read_details_cache_place_ids(details_cache_path)

    resolution_misses = source_record_ids - cached_source_ids
    detail_hits = cached_place_ids & details_place_ids
    detail_misses_for_cached_places = cached_place_ids - details_place_ids

    # Details calls are estimated pessimistically: cached resolved places that
    # lack details, plus one future details call for every source row that still
    # needs Text Search and may resolve to a new unique place.
    estimated_place_details_calls = len(detail_misses_for_cached_places) + len(resolution_misses)

    return DryRunReport(
        input_path=str(csv_path),
        search_context=search_context,
        input_rows=len(parsed),
        unique_source_records=len(source_record_ids),
        resolution_cache_path=str(resolution_cache_path),
        details_cache_path=str(details_cache_path),
        resolution_cache_hits=len(cached_source_ids),
        resolution_cache_misses=len(resolution_misses),
        cached_google_place_ids=len(cached_place_ids),
        details_cache_hits=len(detail_hits),
        details_cache_misses_for_cached_places=len(detail_misses_for_cached_places),
        estimated_text_search_calls=len(resolution_misses),
        estimated_place_details_calls=estimated_place_details_calls,
        categories=_unique_sorted_values(parsed.get("category")),
        subcategories=_unique_sorted_values(parsed.get("subcategory")),
        detail_level_3_values=_unique_sorted_tokens(parsed.get("detail_level_3")),
    )


@dataclass(frozen=True)
class DirectoryDryRunReport:
    """Dry-run summary for a whole curated POI directory."""

    input_dir: str
    file_count: int
    files: list[DryRunReport]
    estimated_text_search_calls: int
    estimated_place_details_calls: int
    input_rows: int
    unique_source_records: int

    def to_dict(self) -> dict[str, Any]:
        output = asdict(self)
        output["files"] = [report.to_dict() for report in self.files]
        return output


def plan_directory_dry_run(
    input_dir: str | Path,
    resolution_cache_path: str | Path = DEFAULT_RESOLUTION_CACHE_PATH,
    details_cache_path: str | Path = DEFAULT_DETAILS_CACHE_PATH,
    search_context: str = DEFAULT_SEARCH_CONTEXT,
) -> DirectoryDryRunReport:
    """Estimate cache coverage and API calls for every CSV in one directory."""

    input_dir = Path(input_dir)
    files = [
        plan_dry_run(
            csv_path=path,
            resolution_cache_path=resolution_cache_path,
            details_cache_path=details_cache_path,
            search_context=search_context,
        )
        for path in iter_input_csv_paths(input_dir)
    ]
    return DirectoryDryRunReport(
        input_dir=str(input_dir),
        file_count=len(files),
        files=files,
        estimated_text_search_calls=sum(report.estimated_text_search_calls for report in files),
        estimated_place_details_calls=sum(report.estimated_place_details_calls for report in files),
        input_rows=sum(report.input_rows for report in files),
        unique_source_records=sum(report.unique_source_records for report in files),
    )


def iter_input_csv_paths(input_dir: str | Path) -> list[Path]:
    """Return sorted curated POI CSVs from one directory."""

    input_dir = Path(input_dir)
    return sorted(path for path in input_dir.glob("*.csv") if path.is_file())


def read_details_cache_place_ids(path: str | Path) -> set[str]:
    """Read Google place IDs whose details cache rows match the active shape."""

    path = Path(path)
    if not path.exists():
        return set()

    place_ids: set[str] = set()
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            place_id = _extract_place_id(payload)
            if place_id and details_cache_row_is_current(_coerce_details_cache_row(payload, place_id)):
                place_ids.add(place_id)
    return place_ids


def _extract_place_id(payload: dict[str, Any]) -> str:
    # Support both wrapped cache rows and raw-ish API payloads so the cache file
    # can evolve without breaking dry-run estimates.
    for key in ("google_place_id", "place_id", "id", "name"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value

    nested_payload = payload.get("payload")
    if isinstance(nested_payload, dict):
        return _extract_place_id(nested_payload)
    return ""


def _coerce_details_cache_row(payload: dict[str, Any], place_id: str) -> dict[str, Any]:
    if "payload" in payload and isinstance(payload.get("payload"), dict):
        return payload
    return {
        "google_place_id": place_id,
        "payload": payload if isinstance(payload, dict) else {},
    }


def _unique_sorted_values(values: Any) -> list[str]:
    if values is None:
        return []
    output = sorted({str(value).strip() for value in values if str(value).strip()})
    return output


def _unique_sorted_tokens(values: Any, delimiter: str = "|") -> list[str]:
    if values is None:
        return []
    output: set[str] = set()
    for value in values:
        for token in str(value).split(delimiter):
            token = token.strip()
            if token:
                output.add(token)
    return sorted(output)
