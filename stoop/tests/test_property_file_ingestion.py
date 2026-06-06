import pandas as pd
import pytest

from nyc_property_finder.pipelines.ingest_property_file import ingest_property_file, run
from nyc_property_finder.services.duckdb_service import DuckDBService
from nyc_property_finder.services.schema import initialize_database


def test_ingest_property_file_normalizes_and_deduplicates_csv(tmp_path) -> None:
    listing_path = tmp_path / "listings.csv"
    pd.DataFrame(
        [
            {
                "source_listing_id": "abc",
                "address": "1 Main St",
                "lat": 40.7,
                "lon": -73.9,
                "price": "3500",
                "beds": "1",
                "baths": "1",
                "listing_type": "rent",
                "url": "https://example.com/abc",
            },
            {
                "source_listing_id": "abc",
                "address": "1 Main St",
                "lat": 40.7,
                "lon": -73.9,
                "price": "3600",
                "beds": "1",
                "baths": "1",
                "listing_type": "rental",
                "url": "https://example.com/abc-new",
            },
        ]
    ).to_csv(listing_path, index=False)

    listings = ingest_property_file(listing_path, source="fixture")

    assert len(listings) == 1
    assert listings.iloc[0]["source"] == "fixture"
    assert listings.iloc[0]["price"] == 3600
    assert listings.iloc[0]["listing_type"] == "rental"
    assert listings.iloc[0]["active"] is True or listings.iloc[0]["active"] == 1
    assert listings.iloc[0]["property_id"].startswith("prop_")


def test_ingest_property_file_requires_minimum_columns(tmp_path) -> None:
    listing_path = tmp_path / "listings.csv"
    pd.DataFrame([{"address": "1 Main St", "price": 3500}]).to_csv(listing_path, index=False)

    with pytest.raises(ValueError, match="lat/lon columns"):
        ingest_property_file(listing_path)


def test_run_writes_property_listings_to_duckdb(tmp_path) -> None:
    database_path = tmp_path / "nyc_property_finder.duckdb"
    listing_path = tmp_path / "listings.csv"
    initialize_database(database_path)
    pd.DataFrame(
        [
            {
                "source_listing_id": "abc",
                "address": "1 Main St",
                "lat": 40.7,
                "lon": -73.9,
                "price": 3500,
            }
        ]
    ).to_csv(listing_path, index=False)

    run(path=listing_path, database_path=database_path, source="fixture")

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        listings = duckdb_service.query_df("SELECT * FROM property_explorer_gold.dim_property_listing")

    assert len(listings) == 1
    assert listings.iloc[0]["source_listing_id"] == "abc"
