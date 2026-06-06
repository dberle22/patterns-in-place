import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

from nyc_property_finder.pipelines.build_neighborhood_character_mart import run
from nyc_property_finder.services.duckdb_service import DuckDBService
from nyc_property_finder.services.schema import initialize_database


def _fixture_curated_poi() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "poi_id": "r1",
                "category": "restaurants",
                "subcategory": "pizza",
                "primary_category": "restaurants",
                "primary_subcategory": "pizza",
                "lat": 40.700,
                "lon": -73.950,
            },
            {
                "poi_id": "r2",
                "category": "restaurants",
                "subcategory": "pizza",
                "primary_category": "restaurants",
                "primary_subcategory": "pizza",
                "lat": 40.701,
                "lon": -73.949,
            },
            {
                "poi_id": "r3",
                "category": "restaurants",
                "subcategory": "sushi",
                "primary_category": "restaurants",
                "primary_subcategory": "sushi",
                "lat": 40.702,
                "lon": -73.948,
            },
            {
                "poi_id": "r4",
                "category": "restaurants",
                "subcategory": "diner",
                "primary_category": "restaurants",
                "primary_subcategory": "diner",
                "lat": 40.750,
                "lon": -73.851,
            },
            {
                "poi_id": "r5",
                "category": "restaurants",
                "subcategory": "diner",
                "primary_category": "restaurants",
                "primary_subcategory": "diner",
                "lat": 40.751,
                "lon": -73.850,
            },
            {
                "poi_id": "b1",
                "category": "bookstores",
                "subcategory": "indie_bookstore",
                "primary_category": "bookstores",
                "primary_subcategory": "indie_bookstore",
                "lat": 40.703,
                "lon": -73.947,
            },
        ]
    )


def _fixture_public_poi() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "poi_id": "s1",
                "category": "subway_station",
                "subcategory": "station",
                "lat": 40.7005,
                "lon": -73.9495,
            },
            {
                "poi_id": "g1",
                "category": "grocery_store",
                "subcategory": "grocery",
                "lat": 40.7505,
                "lon": -73.8505,
            },
        ]
    )


def test_run_builds_neighborhood_character_mart_from_tracts(tmp_path) -> None:
    database_path = tmp_path / "nyc_property_finder.duckdb"
    tract_path = tmp_path / "tracts.geojson"
    equivalency_path = tmp_path / "tract_to_nta.csv"

    initialize_database(database_path)

    tracts = gpd.GeoDataFrame(
        [
            {
                "tract_id": "36047000100",
                "geometry": Polygon([(-74.00, 40.69), (-73.94, 40.69), (-73.94, 40.74), (-74.00, 40.74)]),
            },
            {
                "tract_id": "36081000100",
                "geometry": Polygon([(-73.90, 40.73), (-73.84, 40.73), (-73.84, 40.78), (-73.90, 40.78)]),
            },
        ],
        crs="EPSG:4326",
    )
    tracts.to_file(tract_path, driver="GeoJSON")

    pd.DataFrame(
        [
            {
                "tract_id": "36047000100",
                "nta_id": "BK0101",
                "nta_name": "Test Brooklyn",
                "borough": "Brooklyn",
            },
            {
                "tract_id": "36081000100",
                "nta_id": "QN0101",
                "nta_name": "Test Queens",
                "borough": "Queens",
            },
        ]
    ).to_csv(equivalency_path, index=False)

    with DuckDBService(database_path) as duckdb_service:
        curated = _fixture_curated_poi()
        for column in [
            "source_system",
            "source_systems",
            "primary_source_system",
            "source_record_id",
            "source_list_names",
            "detail_level_3",
            "categories",
            "subcategories",
            "detail_level_3_values",
            "primary_detail_level_3",
            "name",
            "input_title",
            "note",
            "tags",
            "comment",
            "source_url",
            "google_place_id",
            "match_status",
            "address",
            "has_place_details",
            "details_fetched_at",
            "rating",
            "user_rating_count",
            "business_status",
            "editorial_summary",
            "editorial_summary_language_code",
            "price_level",
            "website_uri",
        ]:
            if column not in curated.columns:
                curated[column] = pd.NA
        curated = curated[
            [
                "poi_id",
                "source_system",
                "source_systems",
                "primary_source_system",
                "source_record_id",
                "source_list_names",
                "category",
                "subcategory",
                "detail_level_3",
                "categories",
                "primary_category",
                "subcategories",
                "primary_subcategory",
                "detail_level_3_values",
                "primary_detail_level_3",
                "name",
                "input_title",
                "note",
                "tags",
                "comment",
                "source_url",
                "google_place_id",
                "match_status",
                "address",
                "lat",
                "lon",
                "has_place_details",
                "details_fetched_at",
                "rating",
                "user_rating_count",
                "business_status",
                "editorial_summary",
                "editorial_summary_language_code",
                "price_level",
                "website_uri",
            ]
        ]
        duckdb_service.write_dataframe(curated, "dim_user_poi_v2", schema="property_explorer_gold")

        public = _fixture_public_poi()
        for column in ["source_system", "source_id", "name", "address", "attributes", "snapshotted_at"]:
            if column not in public.columns:
                public[column] = pd.NA
        public = public[
            [
                "poi_id",
                "source_system",
                "source_id",
                "category",
                "subcategory",
                "name",
                "address",
                "lat",
                "lon",
                "attributes",
                "snapshotted_at",
            ]
        ]
        duckdb_service.write_dataframe(public, "dim_public_poi", schema="property_explorer_gold")

    run(database_path=database_path, tract_path=tract_path, equivalency_path=equivalency_path, nta_path=None)

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        tables = duckdb_service.query_df(
            """
            select table_name
            from information_schema.tables
            where table_schema = 'neighborhood_character_mart'
            order by table_name
            """
        )["table_name"].tolist()
        density = duckdb_service.query_df(
            """
            select *
            from neighborhood_character_mart.nta_category_density
            where source = 'curated'
              and category = 'restaurants'
            order by poi_count desc, nta_name
            """
        )
        profile = duckdb_service.query_df(
            """
            select *
            from neighborhood_character_mart.nta_character_profile
            where nta_id = 'BK0101'
            """
        )

    assert tables == [
        "nta_boundaries",
        "nta_category_controls",
        "nta_category_density",
        "nta_character_profile",
        "nta_curated_poi_counts",
        "nta_poi_assignments",
        "nta_public_poi_counts",
    ]
    assert density.iloc[0]["nta_name"] == "Test Brooklyn"
    assert density.iloc[0]["poi_count"] == 3
    assert density.iloc[0]["subcategory_diversity"] == 2
    assert bool(density.iloc[0]["meets_evidence_threshold"]) is True
    assert density.iloc[0]["concentration_tier"] == "destination"
    assert profile.iloc[0]["top_category"] == "restaurants"
    assert profile.iloc[0]["top_subcategory"] == "pizza"
    assert profile.iloc[0]["destination_categories"] == "restaurants"
    assert profile.iloc[0]["subway_station_count"] == 1
