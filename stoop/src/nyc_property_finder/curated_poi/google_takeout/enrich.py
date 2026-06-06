"""Fetch minimal Place Details for resolved Google place IDs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from nyc_property_finder.curated_poi.google_takeout.cache import (
    append_details_cache_row,
    details_cache_row_is_current,
    read_details_cache,
    read_resolution_cache,
)
from nyc_property_finder.curated_poi.google_takeout.client import get_place_details
from nyc_property_finder.curated_poi.google_takeout.config import (
    DEFAULT_API_KEYS_PATH,
    DEFAULT_DETAILS_CACHE_PATH,
    DEFAULT_ENV_PATH,
    DEFAULT_MAX_DETAILS_CALLS,
    DEFAULT_RESOLUTION_CACHE_PATH,
    get_google_maps_api_key,
)


DetailsFetcher = Callable[[str, str], dict[str, Any]]


@dataclass(frozen=True)
class EnrichReport:
    """Summary of one guarded Place Details enrichment run."""

    resolution_cache_path: str
    details_cache_path: str
    resolved_place_ids: int
    details_cache_hits: int
    attempted_details_calls: int
    max_details_calls: int

    def to_dict(self) -> dict[str, Any]:
        """Return a plain dict for logging, notebooks, or future CLI output."""

        return asdict(self)


def enrich_place_details(
    resolution_cache_path: str | Path = DEFAULT_RESOLUTION_CACHE_PATH,
    details_cache_path: str | Path = DEFAULT_DETAILS_CACHE_PATH,
    api_key: str | None = None,
    max_details_calls: int = DEFAULT_MAX_DETAILS_CALLS,
    env_path: str | Path = DEFAULT_ENV_PATH,
    api_keys_path: str | Path = DEFAULT_API_KEYS_PATH,
    fetcher: DetailsFetcher = get_place_details,
) -> EnrichReport:
    """Fetch missing or stale Place Details for cached Google place IDs."""

    api_key = api_key or get_google_maps_api_key(env_path=env_path, api_keys_path=api_keys_path)
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY is required for enrich_place_details.")

    resolution_cache = read_resolution_cache(resolution_cache_path)
    place_ids = sorted(set(resolution_cache["google_place_id"].dropna()) - {""})
    details_cache = read_details_cache(details_cache_path)
    missing_place_ids = [
        place_id
        for place_id in place_ids
        if place_id not in details_cache or not details_cache_row_is_current(details_cache[place_id])
    ]

    if len(missing_place_ids) > max_details_calls:
        raise ValueError(
            "Enrichment run would exceed max_details_calls: "
            f"{len(missing_place_ids)} needed, cap is {max_details_calls}."
        )

    for place_id in missing_place_ids:
        # The fetcher only sees the place ID and key. Tests can inject a fake
        # fetcher, while production uses the minimal Place Details client.
        payload = fetcher(place_id, api_key)
        append_details_cache_row(
            google_place_id=place_id,
            payload=payload,
            fetched_at=datetime.now(UTC).isoformat(),
            path=details_cache_path,
        )

    return EnrichReport(
        resolution_cache_path=str(resolution_cache_path),
        details_cache_path=str(details_cache_path),
        resolved_place_ids=len(place_ids),
        details_cache_hits=len(place_ids) - len(missing_place_ids),
        attempted_details_calls=len(missing_place_ids),
        max_details_calls=max_details_calls,
    )
