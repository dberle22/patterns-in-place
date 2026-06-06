"""Ingest StreetEasy property listings."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from nyc_property_finder.scrapers.streeteasy import StreetEasyScraper
from nyc_property_finder.services.duckdb_service import DuckDBService
from nyc_property_finder.transforms.listings import normalize_property_listings


def ingest_property_streeteasy(search_url: str, limit: int | None = None) -> pd.DataFrame:
    """Fetch and normalize StreetEasy listing records."""

    scraper = StreetEasyScraper()
    raw_listings = scraper.fetch_listings(search_url=search_url, limit=limit)
    return normalize_property_listings(raw_listings, source=scraper.source_name)


def write_property_listings(
    listings: pd.DataFrame,
    duckdb_service: DuckDBService,
    table_name: str = "dim_property_listing",
    schema: str = "property_explorer_gold",
) -> None:
    """Persist normalized property listings."""

    duckdb_service.write_dataframe(listings, table_name=table_name, schema=schema, if_exists="replace")


def run(search_url: str, database_path: str | Path, limit: int | None = None) -> pd.DataFrame:
    """Pipeline entry point for StreetEasy ingestion."""

    listings = ingest_property_streeteasy(search_url=search_url, limit=limit)
    with DuckDBService(database_path) as duckdb_service:
        write_property_listings(listings, duckdb_service)
    return listings
