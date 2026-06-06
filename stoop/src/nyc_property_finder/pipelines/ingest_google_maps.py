"""Ingest Google Maps saved places exports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from nyc_property_finder.services.config import PROJECT_ROOT
from nyc_property_finder.services.config import load_config
from nyc_property_finder.services.duckdb_service import DuckDBService
from nyc_property_finder.services.geosearch import GeocodeFetcher, geocode_name_records
from nyc_property_finder.transforms.poi import (
    normalize_poi_dataframe,
    parse_google_maps_csv,
    parse_google_maps_json,
    parse_google_maps_kml,
)

DEFAULT_POI_GEOCODE_CACHE_PATH = PROJECT_ROOT / "data" / "interim" / "geocoding" / "poi_geocodes.csv"
DEFAULT_POI_GEOCODE_QUARANTINE_PATH = (
    PROJECT_ROOT / "data" / "interim" / "geocoding" / "poi_geocode_quarantine.csv"
)


def parse_google_maps_export(path: str | Path) -> pd.DataFrame:
    """Parse a Google Maps export from KML, JSON, or saved-list CSV."""

    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".json":
        return parse_google_maps_json(path)
    if suffix == ".kml":
        return parse_google_maps_kml(path)
    if suffix == ".csv":
        return parse_google_maps_csv(path)
    raise ValueError(f"Unsupported Google Maps export format: {suffix}")


def _parse_google_maps_input(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    if path.is_dir():
        frames = [parse_google_maps_export(csv_path) for csv_path in sorted(path.glob("*.csv"))]
        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return parse_google_maps_export(path)


def ingest_google_maps(
    path: str | Path,
    category_keywords: dict[str, list[str]] | None = None,
    geocode_missing: bool = True,
    geocode_cache_path: str | Path | None = DEFAULT_POI_GEOCODE_CACHE_PATH,
    geocode_quarantine_path: str | Path | None = DEFAULT_POI_GEOCODE_QUARANTINE_PATH,
    geocode_fetcher: GeocodeFetcher | None = None,
) -> pd.DataFrame:
    """Parse and normalize a Google Maps export."""

    raw_poi = _parse_google_maps_input(path)
    if geocode_missing and not raw_poi.empty and raw_poi[["lat", "lon"]].isna().any(axis=None):
        raw_poi, _ = geocode_name_records(
            raw_poi,
            name_column="name",
            cache_path=geocode_cache_path,
            quarantine_path=geocode_quarantine_path,
            fetcher=geocode_fetcher,
        )
    return normalize_poi_dataframe(raw_poi, category_keywords=category_keywords)


def write_poi(
    poi: pd.DataFrame,
    duckdb_service: DuckDBService,
    table_name: str = "dim_user_poi",
    schema: str = "property_explorer_gold",
) -> None:
    """Persist normalized POI records."""

    duckdb_service.write_dataframe(poi, table_name=table_name, schema=schema, if_exists="replace")


def run(
    path: str | Path,
    database_path: str | Path,
    category_keywords: dict[str, object] | None = None,
    geocode_missing: bool = True,
) -> pd.DataFrame:
    """Pipeline entry point for Google Maps POI ingestion."""

    if category_keywords is None:
        poi_config = load_config()["poi_categories"]
        category_keywords = poi_config.get("keyword_taxonomy_rules") or poi_config.get("categories")
    poi = ingest_google_maps(
        path,
        category_keywords=category_keywords,
        geocode_missing=geocode_missing,
    )
    with DuckDBService(database_path) as duckdb_service:
        write_poi(poi, duckdb_service)
    return poi
