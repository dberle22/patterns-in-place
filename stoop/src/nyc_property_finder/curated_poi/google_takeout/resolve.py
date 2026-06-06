"""Resolve Takeout source rows to Google place IDs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from nyc_property_finder.curated_poi.google_takeout.client import search_text_place_id
from nyc_property_finder.curated_poi.google_takeout.config import (
    DEFAULT_API_KEYS_PATH,
    DEFAULT_ENV_PATH,
    DEFAULT_MAX_TEXT_SEARCH_CALLS,
    DEFAULT_RESOLUTION_CACHE_PATH,
    DEFAULT_SEARCH_CONTEXT,
)
from nyc_property_finder.curated_poi.google_takeout.parse_takeout import parse_google_places_saved_list_csv
from nyc_property_finder.curated_poi.shared.places import resolve_source_dataframe


ResolutionFetcher = Callable[[str, str], dict[str, Any]]


@dataclass(frozen=True)
class ResolveReport:
    """Summary of one guarded resolve-only run."""

    input_path: str
    resolution_cache_path: str
    parsed_rows: int
    input_cache_hits: int
    existing_resolved_cache_rows: int
    attempted_text_search_calls: int
    max_text_search_calls: int
    resolved: int
    no_match: int

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dict for logging, notebooks, or future CLI output."""

        return asdict(self)


def resolve_place_ids(
    csv_path: str | Path,
    api_key: str | None = None,
    resolution_cache_path: str | Path = DEFAULT_RESOLUTION_CACHE_PATH,
    search_context: str = DEFAULT_SEARCH_CONTEXT,
    max_text_search_calls: int = DEFAULT_MAX_TEXT_SEARCH_CALLS,
    env_path: str | Path = DEFAULT_ENV_PATH,
    api_keys_path: str | Path = DEFAULT_API_KEYS_PATH,
    fetcher: ResolutionFetcher = search_text_place_id,
) -> ResolveReport:
    """Resolve uncached saved-list rows to Google place IDs with a hard call cap."""

    csv_path = Path(csv_path)
    parsed = parse_google_places_saved_list_csv(csv_path, search_context=search_context)
    return resolve_source_dataframe(
        parsed,
        input_path=str(csv_path),
        api_key=api_key,
        resolution_cache_path=resolution_cache_path,
        max_text_search_calls=max_text_search_calls,
        env_path=env_path,
        api_keys_path=api_keys_path,
        fetcher=fetcher,
    )
