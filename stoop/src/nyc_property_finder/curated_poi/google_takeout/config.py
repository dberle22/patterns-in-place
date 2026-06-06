"""Configuration helpers for the Google Places POI workflow."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from nyc_property_finder.services.config import PROJECT_ROOT


DEFAULT_ENV_PATH = PROJECT_ROOT / ".env"
DEFAULT_API_KEYS_PATH = PROJECT_ROOT / "config" / "api_keys.yaml"
DEFAULT_SEARCH_CONTEXT = "New York, NY"
GOOGLE_MAPS_API_KEY_ENV = "GOOGLE_MAPS_API_KEY"
SOURCE_SYSTEM = "google_maps_takeout"
DEFAULT_GOOGLE_PLACES_INTERIM_DIR = PROJECT_ROOT / "data" / "interim" / "google_places"
DEFAULT_RESOLUTION_CACHE_PATH = DEFAULT_GOOGLE_PLACES_INTERIM_DIR / "place_resolution_cache.csv"
DEFAULT_DETAILS_CACHE_PATH = DEFAULT_GOOGLE_PLACES_INTERIM_DIR / "place_details_cache.jsonl"
DEFAULT_MAX_TEXT_SEARCH_CALLS = 50
DEFAULT_MAX_DETAILS_CALLS = 50
TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
PLACE_DETAILS_URL_TEMPLATE = "https://places.googleapis.com/v1/places/{place_id}"


def read_env_file(path: str | Path = DEFAULT_ENV_PATH) -> dict[str, str]:
    """Read simple KEY=VALUE pairs from a local env file."""

    path = Path(path)
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            # Keep this parser intentionally small: local .env files only need
            # plain KEY=VALUE pairs for this workflow.
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                values[key] = value
    return values


def get_google_maps_api_key(
    env_var: str = GOOGLE_MAPS_API_KEY_ENV,
    env_path: str | Path = DEFAULT_ENV_PATH,
    api_keys_path: str | Path = DEFAULT_API_KEYS_PATH,
) -> str | None:
    """Return the Google Maps API key from local secret sources."""

    # Prefer an already-exported environment variable so shells, CI, and secret
    # managers can override the local file without editing project config.
    value = os.getenv(env_var)
    if value:
        return value
    return read_env_file(env_path).get(env_var) or read_api_keys_file(api_keys_path)


def read_api_keys_file(path: str | Path = DEFAULT_API_KEYS_PATH) -> str | None:
    """Read the Google Maps API key from the ignored local YAML key file."""

    path = Path(path)
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    # Allow a bare YAML scalar for quick local setup, plus a few explicit
    # mapping keys for a cleaner secret file later.
    if isinstance(data, str):
        return data.strip() or None
    if not isinstance(data, dict):
        return None

    value = _find_google_maps_api_key(data)
    if value:
        return value
    return None


def _find_google_maps_api_key(data: dict[str, object]) -> str | None:
    # Support both flat local files and a one-level ``keys`` namespace, which
    # keeps this compatible with the user's current ignored config shape.
    candidate_mappings = [data]
    nested_keys = data.get("keys")
    if isinstance(nested_keys, dict):
        candidate_mappings.append(nested_keys)

    for mapping in candidate_mappings:
        for key in (
            GOOGLE_MAPS_API_KEY_ENV,
            "google_maps_api_key",
            "google_places_api_key",
            "places_api_key",
        ):
            value = mapping.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, dict):
                nested_value = value.get("key")
                if isinstance(nested_value, str) and nested_value.strip():
                    return nested_value.strip()
    return None
