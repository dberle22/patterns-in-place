import pandas as pd

from nyc_property_finder.app.stoop_explore import (
    load_explore_category_controls,
    load_explore_rankings,
    load_nta_character_profile,
    parse_pipe_list,
)
from nyc_property_finder.services.duckdb_service import DuckDBService


def _write_explore_tables(database_path) -> None:
    controls = pd.DataFrame(
        [
            {
                "category": "restaurants",
                "include_in_explore_v1": True,
                "known_for_enabled": True,
                "min_nyc_category_total": 5,
                "display_label": "Restaurants",
                "notes": "First-class Explore input.",
            },
            {
                "category": "music_venues",
                "include_in_explore_v1": False,
                "known_for_enabled": False,
                "min_nyc_category_total": 5,
                "display_label": "Music venues",
                "notes": "Hidden for now.",
            },
            {
                "category": "shopping",
                "include_in_explore_v1": True,
                "known_for_enabled": True,
                "min_nyc_category_total": 5,
                "display_label": "Shopping",
                "notes": "Useful destination signal.",
            },
        ]
    )
    density = pd.DataFrame(
        [
            {
                "nta_id": "BK0101",
                "nta_name": "Williamsburg",
                "borough": "Brooklyn",
                "area_sqkm": 1.2,
                "source": "curated",
                "category": "restaurants",
                "poi_count": 29,
                "poi_density_per_sqkm": 24.1,
                "subcategory_diversity": 11,
                "nyc_category_total": 930,
                "nyc_percentile": 0.90,
                "concentration_tier": "destination",
                "meets_evidence_threshold": True,
            },
            {
                "nta_id": "MN0101",
                "nta_name": "West Village",
                "borough": "Manhattan",
                "area_sqkm": 1.1,
                "source": "curated",
                "category": "restaurants",
                "poi_count": 66,
                "poi_density_per_sqkm": 60.0,
                "subcategory_diversity": 14,
                "nyc_category_total": 930,
                "nyc_percentile": 0.98,
                "concentration_tier": "destination",
                "meets_evidence_threshold": True,
            },
            {
                "nta_id": "QN0101",
                "nta_name": "Astoria",
                "borough": "Queens",
                "area_sqkm": 1.5,
                "source": "curated",
                "category": "music_venues",
                "poi_count": 5,
                "poi_density_per_sqkm": 3.3,
                "subcategory_diversity": 2,
                "nyc_category_total": 22,
                "nyc_percentile": 0.70,
                "concentration_tier": "present",
                "meets_evidence_threshold": True,
            },
            {
                "nta_id": "BK0101",
                "nta_name": "Williamsburg",
                "borough": "Brooklyn",
                "area_sqkm": 1.2,
                "source": "curated",
                "category": "shopping",
                "poi_count": 10,
                "poi_density_per_sqkm": 8.3,
                "subcategory_diversity": 4,
                "nyc_category_total": 69,
                "nyc_percentile": 1.0,
                "concentration_tier": "destination",
                "meets_evidence_threshold": True,
            },
        ]
    )
    profiles = pd.DataFrame(
        [
            {
                "nta_id": "BK0101",
                "nta_name": "Williamsburg",
                "borough": "Brooklyn",
                "area_sqkm": 1.2,
                "total_curated_poi_count": 39,
                "destination_categories": "restaurants|shopping",
                "strong_categories": "bookstores",
                "top_category": "restaurants",
                "top_subcategory": "pizza",
                "subway_station_count": 3,
                "bus_stop_count": 12,
                "grocery_store_count": 4,
                "pharmacy_count": 2,
                "park_count": 1,
                "public_library_count": 1,
                "public_school_count": 2,
                "built_at": pd.Timestamp("2026-05-10 10:00:00"),
            }
        ]
    )
    with DuckDBService(database_path) as duckdb_service:
        duckdb_service.write_dataframe(
            controls,
            "nta_category_controls",
            schema="neighborhood_character_mart",
        )
        duckdb_service.write_dataframe(
            density,
            "nta_category_density",
            schema="neighborhood_character_mart",
        )
        duckdb_service.write_dataframe(
            profiles,
            "nta_character_profile",
            schema="neighborhood_character_mart",
        )


def test_parse_pipe_list_handles_null_blank_and_duplicates() -> None:
    assert parse_pipe_list(None) == []
    assert parse_pipe_list("") == []
    assert parse_pipe_list("restaurants|shopping|restaurants") == ["restaurants", "shopping"]


def test_load_explore_category_controls_keeps_only_visible_categories(tmp_path) -> None:
    database_path = tmp_path / "app.duckdb"
    _write_explore_tables(database_path)

    controls = load_explore_category_controls(database_path)

    assert controls["category"].tolist() == ["restaurants", "shopping"]
    assert controls["display_label"].tolist() == ["Restaurants", "Shopping"]


def test_load_explore_rankings_filters_to_visible_threshold_passing_category(tmp_path) -> None:
    database_path = tmp_path / "app.duckdb"
    _write_explore_tables(database_path)

    rankings = load_explore_rankings(database_path, "restaurants")

    assert rankings["nta_name"].tolist() == ["West Village", "Williamsburg"]
    assert rankings["display_label"].tolist() == ["Restaurants", "Restaurants"]
    assert "music_venues" not in rankings["category"].tolist()


def test_load_nta_character_profile_parses_category_lists(tmp_path) -> None:
    database_path = tmp_path / "app.duckdb"
    _write_explore_tables(database_path)

    profile = load_nta_character_profile(database_path, "BK0101")

    assert profile is not None
    assert profile["top_category"] == "restaurants"
    assert profile["destination_category_list"] == ["restaurants", "shopping"]
    assert profile["strong_category_list"] == ["bookstores"]
