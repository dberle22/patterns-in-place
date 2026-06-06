"""NYC GeoSearch helpers for listing address geocoding."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import urlopen

import pandas as pd


GEOSEARCH_URL = "https://geosearch.planninglabs.nyc/v2/search"
GEOCODE_COLUMNS = [
    "original_address",
    "matched_address",
    "lat",
    "lon",
    "geocode_source",
    "coordinate_quality",
    "status",
    "error",
]
GeocodeFetcher = Callable[[str], dict[str, Any] | None]


def read_geocode_cache(path: str | Path | None) -> pd.DataFrame:
    """Read an existing geocode cache, returning an empty cache when absent."""

    if path is None:
        return pd.DataFrame(columns=GEOCODE_COLUMNS)

    cache_path = Path(path)
    if not cache_path.exists():
        return pd.DataFrame(columns=GEOCODE_COLUMNS)

    cache = pd.read_csv(cache_path)
    for column in GEOCODE_COLUMNS:
        if column not in cache.columns:
            cache[column] = pd.NA
    return cache[GEOCODE_COLUMNS]


def fetch_nyc_geosearch(address: str, timeout_seconds: int = 20) -> dict[str, Any] | None:
    """Fetch the best NYC GeoSearch match for one address."""

    query = urlencode({"text": address})
    with urlopen(f"{GEOSEARCH_URL}?{query}", timeout=timeout_seconds) as response:
        payload = json.loads(response.read().decode("utf-8"))

    features = payload.get("features") or []
    if not features:
        return None

    feature = features[0]
    coordinates = feature.get("geometry", {}).get("coordinates") or []
    if len(coordinates) < 2:
        return None

    properties = feature.get("properties", {})
    return {
        "matched_address": properties.get("label") or properties.get("name") or address,
        "lat": coordinates[1],
        "lon": coordinates[0],
        "geocode_source": "nyc_geosearch",
        "coordinate_quality": "geocoded",
        "status": "matched",
        "error": "",
    }


def _cache_key(value: object) -> str:
    return "" if pd.isna(value) else str(value).strip().lower()


def _cache_lookup(cache: pd.DataFrame) -> dict[str, dict[str, Any]]:
    if cache.empty:
        return {}

    valid = cache[cache["status"].fillna("") == "matched"].copy()
    valid["_cache_key"] = valid["original_address"].map(_cache_key)
    return {
        row["_cache_key"]: row.drop(labels=["_cache_key"]).to_dict()
        for _, row in valid.drop_duplicates("_cache_key", keep="last").iterrows()
    }


def _write_csv(dataframe: pd.DataFrame, path: str | Path | None) -> None:
    if path is None:
        return

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)


def geocode_name_records(
    records: pd.DataFrame,
    name_column: str,
    cache_path: str | Path | None = None,
    quarantine_path: str | Path | None = None,
    fetcher: GeocodeFetcher | None = None,
    query_suffix: str = "New York, NY",
    use_network: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Resolve named POI records to coordinates with cache and quarantine output."""

    output = records.copy()
    for column in ["lat", "lon", "matched_address", "geocode_source", "coordinate_quality"]:
        if column not in output.columns:
            output[column] = pd.NA

    cache = read_geocode_cache(cache_path)
    lookup = _cache_lookup(cache)
    fetch = fetcher or fetch_nyc_geosearch
    new_cache_rows: list[dict[str, Any]] = []
    quarantined_rows: list[dict[str, Any]] = []

    for index, row in output.iterrows():
        has_lat = not pd.isna(row.get("lat"))
        has_lon = not pd.isna(row.get("lon"))
        if has_lat and has_lon:
            continue

        name = str(row.get(name_column) or "").strip()
        if not name:
            quarantine = row.to_dict()
            quarantine["geocode_error"] = "missing_name"
            quarantined_rows.append(quarantine)
            continue

        query = f"{name} {query_suffix}".strip()
        match = lookup.get(_cache_key(query))
        if match is None and use_network:
            try:
                match = fetch(query)
            except Exception as exc:
                match = {
                    "matched_address": "",
                    "lat": pd.NA,
                    "lon": pd.NA,
                    "geocode_source": "nyc_geosearch",
                    "coordinate_quality": "unknown",
                    "status": "error",
                    "error": str(exc),
                }

            cache_row = {"original_address": query}
            if match is None:
                cache_row.update(
                    {
                        "matched_address": "",
                        "lat": pd.NA,
                        "lon": pd.NA,
                        "geocode_source": "nyc_geosearch",
                        "coordinate_quality": "unknown",
                        "status": "unmatched",
                        "error": "no_geosearch_match",
                    }
                )
            else:
                cache_row.update(match)
            new_cache_rows.append(cache_row)

        if match and not pd.isna(match.get("lat")) and not pd.isna(match.get("lon")):
            output.at[index, "lat"] = match["lat"]
            output.at[index, "lon"] = match["lon"]
            output.at[index, "matched_address"] = match.get("matched_address", "")
            output.at[index, "geocode_source"] = match.get("geocode_source", "nyc_geosearch")
            output.at[index, "coordinate_quality"] = match.get("coordinate_quality", "geocoded")
            continue

        quarantine = row.to_dict()
        quarantine["geocode_error"] = "unmatched"
        quarantined_rows.append(quarantine)

    if new_cache_rows:
        cache = pd.concat([cache, pd.DataFrame(new_cache_rows)], ignore_index=True)
        cache = cache[GEOCODE_COLUMNS].drop_duplicates("original_address", keep="last")
        _write_csv(cache, cache_path)

    quarantine_columns = list(records.columns) + [
        "lat",
        "lon",
        "matched_address",
        "geocode_source",
        "coordinate_quality",
        "geocode_error",
    ]
    quarantine = pd.DataFrame(quarantined_rows, columns=list(dict.fromkeys(quarantine_columns)))
    _write_csv(quarantine, quarantine_path)

    return output, quarantine


def geocode_missing_listing_coordinates(
    listings: pd.DataFrame,
    cache_path: str | Path | None = None,
    quarantine_path: str | Path | None = None,
    fetcher: GeocodeFetcher | None = None,
    use_network: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fill missing listing coordinates from cache and NYC GeoSearch.

    Returns a tuple of ``(geocoded_listings, quarantined_rows)``. Rows that still
    lack coordinates after cache/API lookup are included in the quarantine
    dataframe and left with null coordinates in the returned listings dataframe.
    """

    output = listings.copy()
    cache = read_geocode_cache(cache_path)
    lookup = _cache_lookup(cache)
    fetch = fetcher or fetch_nyc_geosearch
    new_cache_rows: list[dict[str, Any]] = []
    quarantined_rows: list[dict[str, Any]] = []

    for index, row in output.iterrows():
        has_lat = not pd.isna(row.get("lat"))
        has_lon = not pd.isna(row.get("lon"))
        if has_lat and has_lon:
            continue

        address = str(row.get("address") or "").strip()
        if not address:
            quarantine = row.to_dict()
            quarantine["geocode_error"] = "missing_address"
            quarantined_rows.append(quarantine)
            continue

        match = lookup.get(_cache_key(address))
        if match is None and use_network:
            try:
                match = fetch(address)
            except Exception as exc:
                match = {
                    "matched_address": "",
                    "lat": pd.NA,
                    "lon": pd.NA,
                    "geocode_source": "nyc_geosearch",
                    "coordinate_quality": "unknown",
                    "status": "error",
                    "error": str(exc),
                }

            cache_row = {"original_address": address}
            if match is None:
                cache_row.update(
                    {
                        "matched_address": "",
                        "lat": pd.NA,
                        "lon": pd.NA,
                        "geocode_source": "nyc_geosearch",
                        "coordinate_quality": "unknown",
                        "status": "unmatched",
                        "error": "no_geosearch_match",
                    }
                )
            else:
                cache_row.update(match)
            new_cache_rows.append(cache_row)

        if match and not pd.isna(match.get("lat")) and not pd.isna(match.get("lon")):
            output.at[index, "lat"] = match["lat"]
            output.at[index, "lon"] = match["lon"]
            output.at[index, "coordinate_quality"] = match.get("coordinate_quality", "geocoded")
            output.at[index, "geocode_source"] = match.get("geocode_source", "nyc_geosearch")
            output.at[index, "geocoded_from_address"] = True
            continue

        quarantine = row.to_dict()
        quarantine["geocode_error"] = "unmatched"
        quarantined_rows.append(quarantine)

    if new_cache_rows:
        cache = pd.concat([cache, pd.DataFrame(new_cache_rows)], ignore_index=True)
        cache = cache[GEOCODE_COLUMNS].drop_duplicates("original_address", keep="last")
        _write_csv(cache, cache_path)

    quarantine_columns = list(listings.columns) + ["geocode_error"]
    quarantine = pd.DataFrame(quarantined_rows, columns=quarantine_columns)
    _write_csv(quarantine, quarantine_path)

    return output, quarantine
