"""Google Places API client helpers for the POI workflow."""

from __future__ import annotations

import json
from typing import Any
from urllib.parse import quote
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from nyc_property_finder.curated_poi.google_takeout.config import PLACE_DETAILS_URL_TEMPLATE, TEXT_SEARCH_URL


TEXT_SEARCH_ID_FIELD_MASK = "places.id"
PLACE_DETAILS_FIELD_MASK = (
    "displayName,formattedAddress,location,rating,userRatingCount,"
    "businessStatus,editorialSummary,priceLevel,websiteUri"
)
PLACE_DETAILS_CACHE_SCHEMA_VERSION = "2026-04-29-pro-v1"


class GooglePlacesClientError(RuntimeError):
    """Raised when a Google Places request fails."""


def search_text_place_id(
    text_query: str,
    api_key: str,
    timeout_seconds: int = 20,
) -> dict[str, Any]:
    """Return the top Google Places Text Search ID-only result."""

    request = build_text_search_id_request(text_query=text_query, api_key=api_key)
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise GooglePlacesClientError(f"Google Text Search failed with HTTP {error.code}: {body}") from error
    except URLError as error:
        raise GooglePlacesClientError(f"Google Text Search request failed: {error}") from error

    places = payload.get("places", [])
    if not places:
        return {"google_place_id": "", "match_status": "no_match", "raw_response": payload}

    top_place = places[0]
    google_place_id = str(top_place.get("id", ""))
    return {
        "google_place_id": google_place_id,
        "match_status": "top_candidate" if google_place_id else "no_match",
        "raw_response": payload,
    }


def build_text_search_id_request(text_query: str, api_key: str) -> Request:
    """Build the low-cost Text Search request that asks only for place IDs."""

    # This body intentionally stays minimal: query text in, top candidate ID
    # out. We do not request display names, addresses, ratings, or photos here.
    body = json.dumps({"textQuery": text_query}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": TEXT_SEARCH_ID_FIELD_MASK,
    }
    return Request(TEXT_SEARCH_URL, data=body, headers=headers, method="POST")


def get_place_details(
    google_place_id: str,
    api_key: str,
    timeout_seconds: int = 20,
) -> dict[str, Any]:
    """Return the canonical Place Details payload for curated POI enrichment."""

    request = build_place_details_request(google_place_id=google_place_id, api_key=api_key)
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise GooglePlacesClientError(f"Google Place Details failed with HTTP {error.code}: {body}") from error
    except URLError as error:
        raise GooglePlacesClientError(f"Google Place Details request failed: {error}") from error


def build_place_details_request(google_place_id: str, api_key: str) -> Request:
    """Build the canonical Place Details request for curated POI enrichment."""

    # Details are the paid enrichment step. Keep one shared field mask so all
    # curated-source pipelines populate the same cache payload shape.
    place_id = quote(google_place_id, safe="")
    url = PLACE_DETAILS_URL_TEMPLATE.format(place_id=place_id)
    headers = {
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": PLACE_DETAILS_FIELD_MASK,
    }
    return Request(url, headers=headers, method="GET")
