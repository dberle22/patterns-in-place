import pandas as pd

from nyc_property_finder.services.geosearch import geocode_missing_listing_coordinates


def test_geocode_missing_listing_coordinates_uses_fetcher_and_writes_cache(tmp_path) -> None:
    cache_path = tmp_path / "listing_geocodes.csv"
    quarantine_path = tmp_path / "listing_geocode_quarantine.csv"
    listings = pd.DataFrame(
        [
            {
                "address": "414 East 83rd Street, New York, NY 10028",
                "lat": pd.NA,
                "lon": pd.NA,
                "price": 4998,
            }
        ]
    )

    def fetcher(address: str):
        assert address == "414 East 83rd Street, New York, NY 10028"
        return {
            "matched_address": "414 E 83 St, Manhattan",
            "lat": 40.774,
            "lon": -73.951,
            "geocode_source": "nyc_geosearch",
            "coordinate_quality": "geocoded",
            "status": "matched",
            "error": "",
        }

    geocoded, quarantine = geocode_missing_listing_coordinates(
        listings,
        cache_path=cache_path,
        quarantine_path=quarantine_path,
        fetcher=fetcher,
    )

    assert quarantine.empty
    assert geocoded.iloc[0]["lat"] == 40.774
    assert geocoded.iloc[0]["lon"] == -73.951
    assert geocoded.iloc[0]["geocode_source"] == "nyc_geosearch"
    assert cache_path.exists()
    assert quarantine_path.exists()
    assert pd.read_csv(quarantine_path).empty


def test_geocode_missing_listing_coordinates_quarantines_unmatched_rows(tmp_path) -> None:
    quarantine_path = tmp_path / "listing_geocode_quarantine.csv"
    listings = pd.DataFrame([{"address": "Unknown place", "lat": pd.NA, "lon": pd.NA, "price": 1000}])

    geocoded, quarantine = geocode_missing_listing_coordinates(
        listings,
        quarantine_path=quarantine_path,
        fetcher=lambda address: None,
    )

    assert pd.isna(geocoded.iloc[0]["lat"])
    assert len(quarantine) == 1
    assert quarantine.iloc[0]["geocode_error"] == "unmatched"
    assert quarantine_path.exists()
