"""Ingest property listings from a local CSV or JSON file."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from nyc_property_finder.services.config import PROJECT_ROOT
from nyc_property_finder.services.duckdb_service import DuckDBService
from nyc_property_finder.services.geosearch import GeocodeFetcher, geocode_missing_listing_coordinates
from nyc_property_finder.transforms.listings import normalize_property_listings


REQUIRED_LISTING_COLUMNS = {"address", "price"}
DEFAULT_GEOCODE_CACHE_PATH = PROJECT_ROOT / "data" / "interim" / "geocoding" / "listing_geocodes.csv"
DEFAULT_GEOCODE_QUARANTINE_PATH = (
    PROJECT_ROOT / "data" / "interim" / "geocoding" / "listing_geocode_quarantine.csv"
)


def read_property_file(path: str | Path) -> pd.DataFrame:
    """Read a local property listing file from CSV or JSON."""

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Property listing file does not exist: {path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".json":
        return pd.read_json(path)
    raise ValueError(f"Unsupported property listing file format: {suffix}")


def validate_property_listings(dataframe: pd.DataFrame) -> None:
    """Validate the minimum source columns needed for MVP listing ingestion."""

    missing_columns = REQUIRED_LISTING_COLUMNS.difference(dataframe.columns)
    if missing_columns:
        raise ValueError(f"Missing required listing columns: {sorted(missing_columns)}")

    if not {"lat", "lon"}.issubset(dataframe.columns):
        raise ValueError("Listing rows need lat/lon columns, even when values are blank before geocoding")


def ingest_property_file(
    path: str | Path,
    source: str = "local_file",
    geocode_missing: bool = True,
    geocode_cache_path: str | Path | None = DEFAULT_GEOCODE_CACHE_PATH,
    geocode_quarantine_path: str | Path | None = DEFAULT_GEOCODE_QUARANTINE_PATH,
    geocode_fetcher: GeocodeFetcher | None = None,
) -> pd.DataFrame:
    """Read, validate, normalize, and deduplicate local listing records."""

    raw_listings = read_property_file(path)
    validate_property_listings(raw_listings)

    if geocode_missing and raw_listings[["lat", "lon"]].isna().any(axis=None):
        raw_listings, _ = geocode_missing_listing_coordinates(
            raw_listings,
            cache_path=geocode_cache_path,
            quarantine_path=geocode_quarantine_path,
            fetcher=geocode_fetcher,
        )

    listings = normalize_property_listings(raw_listings, source=source)
    listings = listings.dropna(subset=["lat", "lon"])
    return listings.drop_duplicates("property_id", keep="last").reset_index(drop=True)


def write_property_listings(
    listings: pd.DataFrame,
    duckdb_service: DuckDBService,
    table_name: str = "dim_property_listing",
    schema: str = "property_explorer_gold",
) -> None:
    """Persist normalized property listings."""

    duckdb_service.write_dataframe(listings, table_name=table_name, schema=schema, if_exists="replace")


def run(
    path: str | Path,
    database_path: str | Path,
    source: str = "local_file",
    geocode_missing: bool = True,
) -> pd.DataFrame:
    """Pipeline entry point for local property listing ingestion."""

    listings = ingest_property_file(path=path, source=source, geocode_missing=geocode_missing)
    with DuckDBService(database_path) as duckdb_service:
        write_property_listings(listings, duckdb_service)
    return listings
