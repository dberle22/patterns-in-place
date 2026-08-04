"""Census geocoding and tract-resolution helpers for Place Intelligence."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen

import duckdb

from site_prep import Site


REPO_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = REPO_ROOT / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
GEOCODER_ROOT = "https://geocoding.geo.census.gov/geocoder"
CENSUS_CURRENT_BENCHMARK = "4"
CENSUS_CURRENT_VINTAGE = "4"


@dataclass(frozen=True)
class GeocodeResult:
    """Resolved site point plus tract provenance for downstream catchment work."""

    lat: float
    lon: float
    matched_address: str
    match_type: str
    tract_geoid: str
    geocode_source: str


def geocode_address(address: str) -> GeocodeResult:
    """Geocode a single U.S. address through the Census geographies endpoint."""

    if not isinstance(address, str) or not address.strip():
        raise ValueError("Address must be a non-empty string.")

    payload = _fetch_geocoder_json(
        "geographies/onelineaddress",
        {
            "address": address.strip(),
            "benchmark": CENSUS_CURRENT_BENCHMARK,
            "vintage": CENSUS_CURRENT_VINTAGE,
            "format": "json",
        },
    )
    match = _extract_single_match(payload, address)
    tract_geoid = _extract_tract_geoid(match)
    coordinates = match.get("coordinates") or {}
    benchmark_name = _extract_nested_name(payload, ("result", "input", "benchmark", "benchmarkName"))
    vintage_name = _extract_nested_name(payload, ("result", "input", "vintage", "vintageName"))

    return GeocodeResult(
        lat=float(coordinates["y"]),
        lon=float(coordinates["x"]),
        matched_address=str(match["matchedAddress"]),
        # The Census API docs state the current engine calculates coordinates
        # along an address range, so we record that explicit service behavior
        # rather than inventing a rooftop precision label the payload lacks.
        match_type="address_range",
        tract_geoid=tract_geoid,
        geocode_source=f"census_geocoder:{benchmark_name}:{vintage_name}",
    )


def resolve_site_geocode(site: Site) -> GeocodeResult:
    """Resolve a site to coordinates and tract, honoring manual overrides."""

    if site.lat is not None and site.lon is not None:
        tract_geoid = resolve_tract_from_coordinates(site.lon, site.lat)
        return GeocodeResult(
            lat=site.lat,
            lon=site.lon,
            matched_address=site.address,
            match_type="manual_override",
            tract_geoid=tract_geoid,
            geocode_source="manual_override",
        )

    geocode_result = geocode_address(site.address)
    spatial_tract_geoid = resolve_tract_from_coordinates(geocode_result.lon, geocode_result.lat)
    if spatial_tract_geoid != geocode_result.tract_geoid:
        return GeocodeResult(
            lat=geocode_result.lat,
            lon=geocode_result.lon,
            matched_address=geocode_result.matched_address,
            match_type=geocode_result.match_type,
            tract_geoid=spatial_tract_geoid,
            geocode_source=f"{geocode_result.geocode_source}:tract_corrected_by_spatial_join",
        )
    return geocode_result


def resolve_tract_from_coordinates(lon: float, lat: float) -> str:
    """Resolve a lon/lat pair to a tract GEOID from the shared tract geometry table."""

    con = get_connection()
    try:
        con.execute("LOAD spatial;")
        row = con.execute(
            """
            SELECT tract_geoid
            FROM patterns_in_place.geo.tracts_all_us
            WHERE ST_Contains(
                geom,
                ST_Point(CAST(? AS DOUBLE), CAST(? AS DOUBLE))
            )
            LIMIT 1
            """,
            [float(lon), float(lat)],
        ).fetchone()
    finally:
        con.close()

    if row is None or row[0] is None:
        raise ValueError(f"No containing tract found for lon={lon}, lat={lat}.")
    return str(row[0])


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open the shared repo DuckDB in read-only mode."""

    return duckdb.connect(str(DB_PATH), read_only=True)


def _fetch_geocoder_json(path: str, params: dict[str, Any]) -> dict[str, Any]:
    """Call the Census geocoder and parse the JSON payload defensively."""

    url = f"{GEOCODER_ROOT}/{path}?{urlencode(params)}"
    with urlopen(url) as response:  # noqa: S310 - fixed Census API endpoint
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Census geocoder returned a non-object JSON payload.")
    return payload


def _extract_single_match(payload: dict[str, Any], address: str) -> dict[str, Any]:
    """Require one usable address match so failures surface clearly to the caller."""

    matches = ((payload.get("result") or {}).get("addressMatches")) or []
    if not matches:
        raise ValueError(f"Census geocoder returned no match for address: {address}")
    match = matches[0]
    if not isinstance(match, dict):
        raise ValueError("Census geocoder returned an invalid address match payload.")
    return match


def _extract_tract_geoid(match: dict[str, Any]) -> str:
    """Pull the tract GEOID from the geographies payload and fail loudly if absent."""

    geographies = match.get("geographies") or {}
    tracts = geographies.get("Census Tracts") or []
    if not tracts:
        raise ValueError("Census geocoder response did not include a tract geography.")
    tract_geoid = tracts[0].get("GEOID")
    if not tract_geoid:
        raise ValueError("Census geocoder tract geography was missing GEOID.")
    return str(tract_geoid)


def _extract_nested_name(payload: dict[str, Any], path: tuple[str, ...]) -> str:
    """Read nested benchmark/vintage metadata without assuming every key exists."""

    current: Any = payload
    for key in path:
        if not isinstance(current, dict) or key not in current:
            raise ValueError(f"Census geocoder response was missing required metadata: {'/'.join(path)}")
        current = current[key]
    return str(current)
