import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

from nyc_property_finder.pipelines.build_property_context import (
    add_poi_context,
    add_scores,
    add_transit_context,
    build_context_quality_summary,
    count_subway_lines,
    run,
)
from nyc_property_finder.services.duckdb_service import DuckDBService
from nyc_property_finder.services.schema import initialize_database


def _fixture_properties() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "property_id": "p1",
                "source": "fixture",
                "source_listing_id": "abc",
                "address": "1 Main St",
                "lat": 40.7,
                "lon": -73.9,
                "price": 3500,
                "beds": 1,
                "baths": 1,
                "listing_type": "rental",
                "active": True,
                "url": "https://example.com/abc",
                "ingest_timestamp": pd.Timestamp.now(tz="UTC"),
            }
        ]
    )


def test_run_builds_and_writes_property_context(tmp_path) -> None:
    database_path = tmp_path / "nyc_property_finder.duckdb"
    tract_path = tmp_path / "tracts.geojson"
    initialize_database(database_path)

    tracts = gpd.GeoDataFrame(
        [{"tract_id": "t1", "geometry": Polygon([(-74, 40.6), (-73.8, 40.6), (-73.8, 40.8), (-74, 40.8)])}],
        crs="EPSG:4326",
    )
    tracts.to_file(tract_path, driver="GeoJSON")

    with DuckDBService(database_path) as duckdb_service:
        duckdb_service.write_dataframe(
            _fixture_properties(),
            table_name="dim_property_listing",
            schema="property_explorer_gold",
        )
        duckdb_service.write_dataframe(
            pd.DataFrame([{"tract_id": "t1", "nta_id": "n1", "nta_name": "Test NTA", "geometry_wkt": ""}]),
            table_name="dim_tract_to_nta",
            schema="property_explorer_gold",
        )
        duckdb_service.write_dataframe(
            pd.DataFrame(
                [
                    {
                        "subway_stop_id": "A01",
                        "stop_name": "Main St",
                        "lines": "A C",
                        "lat": 40.7005,
                        "lon": -73.9005,
                    }
                ]
            ),
            table_name="dim_subway_stop",
            schema="property_explorer_gold",
        )
        duckdb_service.write_dataframe(
            pd.DataFrame(
                [
                    {
                        "poi_id": "poi1",
                        "name": "Coffee Place",
                        "category": "coffee_shops",
                        "source_list_name": "Favorites",
                        "lat": 40.701,
                        "lon": -73.901,
                    }
                ]
            ),
            table_name="dim_user_poi",
            schema="property_explorer_gold",
        )
        duckdb_service.write_dataframe(
            pd.DataFrame(
                [
                    {
                        "tract_id": "t1",
                        "median_income": 100000,
                        "median_rent": 2500,
                        "median_home_value": 900000,
                        "pct_bachelors_plus": 0.6,
                        "median_age": 36,
                        "crime_rate_proxy": 1,
                    }
                ]
            ),
            table_name="fct_tract_features",
            schema="property_explorer_gold",
        )

    context = run(database_path=database_path, tract_path=tract_path)

    assert len(context) == 1
    assert context.iloc[0]["tract_id"] == "t1"
    assert context.iloc[0]["nta_id"] == "n1"
    assert context.iloc[0]["nta_name"] == "Test NTA"
    assert context.iloc[0]["nearest_subway_stop"] == "Main St"
    assert context.iloc[0]["subway_lines_count"] == 2
    assert context.iloc[0]["poi_count_nearby"] == 1
    assert context.iloc[0]["poi_count_10min"] == 1
    assert context.iloc[0]["property_fit_score"] > 0
    assert context.iloc[0]["neighborhood_score_status"] == "scored"
    assert context.iloc[0]["personal_fit_score_status"] == "scored"
    assert context.iloc[0]["property_fit_score_status"] == "scored"
    assert context.iloc[0]["poi_category_counts"] == '{"coffee_shops": 1}'

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        persisted = duckdb_service.query_df("SELECT * FROM property_explorer_gold.fct_property_context")

    assert len(persisted) == 1
    assert persisted.iloc[0]["property_id"] == "p1"


def test_subway_line_count_normalizes_delimiters() -> None:
    assert count_subway_lines("A C") == 2
    assert count_subway_lines("A,C/E") == 3
    assert count_subway_lines("A A C") == 2
    assert count_subway_lines(None) == 0


def test_absent_poi_data_sets_personal_fit_null() -> None:
    context = add_scores(add_poi_context(_fixture_properties(), poi=None))

    assert bool(context.iloc[0]["poi_data_available"]) is False
    assert context.iloc[0]["poi_count_nearby"] == 0
    assert pd.isna(context.iloc[0]["personal_fit_score"])
    assert context.iloc[0]["personal_fit_score_status"] == "unavailable"
    assert context.iloc[0]["property_fit_score_status"] == "unavailable"


def test_loaded_poi_data_with_no_nearby_places_scores_zero_personal_fit() -> None:
    poi = pd.DataFrame(
        [
            {
                "poi_id": "far",
                "name": "Far Place",
                "category": "restaurants",
                "source_list_name": "Favorites",
                "lat": 40.1,
                "lon": -73.1,
            }
        ]
    )

    context = add_scores(add_poi_context(_fixture_properties(), poi=poi))

    assert bool(context.iloc[0]["poi_data_available"]) is True
    assert context.iloc[0]["poi_count_nearby"] == 0
    assert context.iloc[0]["poi_category_counts"] == {}
    assert context.iloc[0]["personal_fit_score"] == 0
    assert context.iloc[0]["personal_fit_score_status"] == "scored"


def test_all_null_neighborhood_metrics_do_not_zero_fill_score() -> None:
    properties = _fixture_properties().assign(tract_id="t1")
    tract_features = pd.DataFrame(
        [
            {
                "tract_id": "t1",
                "median_income": None,
                "median_rent": None,
                "median_home_value": None,
                "pct_bachelors_plus": None,
                "median_age": None,
            }
        ]
    )

    context = add_scores(add_poi_context(properties, poi=None), tract_features=tract_features)

    assert pd.isna(context.iloc[0]["neighborhood_score"])
    assert context.iloc[0]["neighborhood_score_status"] == "unavailable"
    assert context.iloc[0]["property_fit_score_status"] == "unavailable"


def test_transit_context_missing_data_leaves_mobility_null() -> None:
    context = add_scores(add_transit_context(_fixture_properties(), subway_stops=None))

    assert pd.isna(context.iloc[0]["nearest_subway_stop"])
    assert pd.isna(context.iloc[0]["nearest_subway_distance_miles"])
    assert context.iloc[0]["subway_lines_count"] == 0
    assert pd.isna(context.iloc[0]["mobility_score"])


def test_quality_summary_reports_assignment_and_score_ranges() -> None:
    context = pd.DataFrame(
        [
            {
                "property_id": "p1",
                "active": True,
                "tract_id": "t1",
                "nta_name": "Test NTA",
                "nearest_subway_distance_miles": 0.2,
                "neighborhood_score": None,
                "mobility_score": 80,
                "personal_fit_score": 10,
                "property_fit_score": 50,
            },
            {
                "property_id": "p2",
                "active": False,
                "tract_id": None,
                "nta_name": None,
                "nearest_subway_distance_miles": 2.5,
                "neighborhood_score": None,
                "mobility_score": 110,
                "personal_fit_score": None,
                "property_fit_score": 50,
            },
        ]
    )

    summary = build_context_quality_summary(context)

    assert summary["row_count"] == 2
    assert summary["active_row_count"] == 1
    assert summary["tract_assigned_count"] == 1
    assert summary["missing_nta_name_count"] == 1
    assert summary["subway_distance_over_2_miles_count"] == 1
    assert summary["invalid_score_counts"]["mobility_score"] == 1
