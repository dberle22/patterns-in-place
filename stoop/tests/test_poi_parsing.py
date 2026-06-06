import json

from nyc_property_finder.pipelines.ingest_google_maps import ingest_google_maps
from nyc_property_finder.transforms.poi import infer_taxonomy_from_text
from nyc_property_finder.transforms.poi import normalize_category


def test_normalize_category_uses_keyword_mapping() -> None:
    assert normalize_category("Neighborhood Coffee") == "coffee_shops"
    assert normalize_category("Tiny Cocktail Bar") == "bars"
    assert normalize_category("Prospect Park") == "parks"
    assert normalize_category("Somewhere Unknown") == "other"


def test_infer_taxonomy_from_text_uses_restaurants_plus_subcategory() -> None:
    taxonomy = infer_taxonomy_from_text("Excellent Japanese ramen spot")

    assert taxonomy["category"] == "restaurants"
    assert taxonomy["subcategory"] == "japanese"


def test_ingest_google_maps_json_parses_and_normalizes(tmp_path) -> None:
    export_path = tmp_path / "saved_places.json"
    export_path.write_text(
        json.dumps(
            {
                "places": [
                    {
                        "name": "Neighborhood Coffee",
                        "list_name": "Favorites",
                        "location": {"lat": 40.7, "lng": -73.9},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    poi = ingest_google_maps(export_path)

    assert len(poi) == 1
    assert poi.iloc[0]["category"] == "coffee_shops"
    assert poi.iloc[0]["source_list_name"] == "Favorites"
    assert poi.iloc[0]["poi_id"].startswith("poi_")


def test_ingest_google_maps_csv_geocodes_and_uses_list_category(tmp_path) -> None:
    export_path = tmp_path / "New York - Bookstores.csv"
    export_path.write_text(
        "\n".join(
            [
                "Title,Note,URL,Tags,Comment",
                ",,,,",
                "Ursula Bookshop,,https://www.google.com/maps/place/Ursula+Bookshop/data=!4m2!3m1!1sabc,,",
            ]
        ),
        encoding="utf-8",
    )

    def fetcher(query: str):
        assert query == "Ursula Bookshop New York, NY"
        return {
            "matched_address": "Ursula Bookshop, Brooklyn",
            "lat": 40.686,
            "lon": -73.986,
            "geocode_source": "nyc_geosearch",
            "coordinate_quality": "geocoded",
            "status": "matched",
            "error": "",
        }

    poi = ingest_google_maps(
        export_path,
        geocode_cache_path=tmp_path / "poi_geocodes.csv",
        geocode_quarantine_path=tmp_path / "poi_quarantine.csv",
        geocode_fetcher=fetcher,
    )

    assert len(poi) == 1
    assert poi.iloc[0]["name"] == "Ursula Bookshop"
    assert poi.iloc[0]["source_list_name"] == "New York - Bookstores"
    assert poi.iloc[0]["category"] == "bookstores"
    assert poi.iloc[0]["lat"] == 40.686
