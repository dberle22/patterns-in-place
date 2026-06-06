import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

from nyc_property_finder.app.base_map import (
    DEFAULT_PUBLIC_POI_CATEGORIES,
    TARGET_COUNTY_GEOIDS,
    add_metric_display_columns,
    available_poi_categories,
    available_poi_subcategories,
    available_public_poi_categories,
    build_base_map_deck,
    filter_public_poi_points_by_categories,
    filter_points_to_supported_geography,
    filter_poi_points_by_categories,
    format_metric_value,
    load_poi_map_data,
    load_public_poi_map_data,
    poi_color_legend_rows,
    prepare_public_poi_points,
    prepare_poi_points,
    prepare_base_map_data,
)
from nyc_property_finder.services.duckdb_service import DuckDBService


def _write_tract_fixture(path) -> None:
    tracts = gpd.GeoDataFrame(
        [
            {
                "GEOID": "36047000100",
                "BoroName": "Brooklyn",
                "NTA2020": "BK0101",
                "NTAName": "Test Brooklyn",
                "geometry": Polygon(
                    [(-74.00, 40.70), (-73.99, 40.70), (-73.99, 40.71), (-74.00, 40.71)]
                ),
            },
            {
                "GEOID": "36061000100",
                "BoroName": "Manhattan",
                "NTA2020": "MN0101",
                "NTAName": "Test Manhattan",
                "geometry": Polygon(
                    [(-73.99, 40.71), (-73.98, 40.71), (-73.98, 40.72), (-73.99, 40.72)]
                ),
            },
            {
                "GEOID": "36081000100",
                "BoroName": "Queens",
                "NTA2020": "QN0101",
                "NTAName": "Skipped Queens",
                "geometry": Polygon(
                    [(-73.98, 40.72), (-73.97, 40.72), (-73.97, 40.73), (-73.98, 40.73)]
                ),
            },
        ],
        geometry="geometry",
        crs="EPSG:4326",
    )
    tracts.to_file(path, driver="GeoJSON")


def _write_gold_fixtures(database_path) -> None:
    mapping = pd.DataFrame(
        [
            {
                "tract_id": "36047000100",
                "nta_id": "BK0101",
                "nta_name": "Test Brooklyn",
                "borough": "Brooklyn",
            },
            {
                "tract_id": "36061000100",
                "nta_id": "MN0101",
                "nta_name": "Test Manhattan",
                "borough": "Manhattan",
            },
        ]
    )
    tract_features = pd.DataFrame(
        [
            {
                "tract_id": "36047000100",
                "median_income": 100000,
                "median_rent": 2500,
                "median_home_value": 900000,
                "pct_bachelors_plus": 0.5,
                "median_age": 35,
                "crime_rate_proxy": None,
            },
            {
                "tract_id": "36061000100",
                "median_income": 150000,
                "median_rent": 3200,
                "median_home_value": 1200000,
                "pct_bachelors_plus": 0.7,
                "median_age": 42,
                "crime_rate_proxy": None,
            },
        ]
    )
    nta_features = pd.DataFrame(
        [
            {
                "nta_id": "BK0101",
                "nta_name": "Test Brooklyn",
                "median_income": 100000,
                "median_rent": 2500,
                "median_home_value": 900000,
                "pct_bachelors_plus": 0.5,
                "median_age": 35,
                "crime_rate_proxy": None,
            },
            {
                "nta_id": "MN0101",
                "nta_name": "Test Manhattan",
                "median_income": 150000,
                "median_rent": 3200,
                "median_home_value": 1200000,
                "pct_bachelors_plus": 0.7,
                "median_age": 42,
                "crime_rate_proxy": None,
            },
        ]
    )
    with DuckDBService(database_path) as duckdb_service:
        duckdb_service.write_dataframe(mapping, "dim_tract_to_nta", schema="property_explorer_gold")
        duckdb_service.write_dataframe(
            tract_features,
            "fct_tract_features",
            schema="property_explorer_gold",
        )
        duckdb_service.write_dataframe(
            nta_features,
            "fct_nta_features",
            schema="property_explorer_gold",
        )


def test_format_metric_value_handles_currency_percent_and_nulls() -> None:
    assert format_metric_value(123456.7, "median_income") == "$123,457"
    assert format_metric_value(0.42, "pct_bachelors_plus") == "42.0%"
    assert format_metric_value(None, "median_age") == "Unavailable"


def test_add_metric_display_columns_marks_null_values_with_muted_color() -> None:
    data = gpd.GeoDataFrame(
        [{"median_income": 100}, {"median_income": None}],
        geometry=[
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
            Polygon([(1, 1), (2, 1), (2, 2), (1, 2)]),
        ],
        crs="EPSG:4326",
    )

    output = add_metric_display_columns(data, "median_income")

    assert output["metric_available"].tolist() == [True, False]
    assert output.iloc[0]["fill_color"][3] > output.iloc[1]["fill_color"][3]


def test_prepare_base_map_data_filters_to_target_boroughs_and_joins_metrics(tmp_path) -> None:
    database_path = tmp_path / "app.duckdb"
    tract_path = tmp_path / "tracts.geojson"
    _write_tract_fixture(tract_path)
    _write_gold_fixtures(database_path)

    map_data = prepare_base_map_data(database_path, tract_path, metric="median_income")

    assert set(map_data.tracts["tract_id"]) == {
        "36047000100",
        "36061000100",
        "36081000100",
    }
    assert tuple(TARGET_COUNTY_GEOIDS) == ("36005", "36047", "36061", "36081", "36085")
    assert map_data.stats["tract_count"] == 3
    assert map_data.stats["neighborhood_count"] == 2
    assert map_data.stats["metric_non_null_count"] == 2
    assert map_data.tracts["median_income"].iloc[0] == 100000
    assert map_data.tracts["median_income"].iloc[1] == 150000
    assert pd.isna(map_data.tracts["median_income"].iloc[2])
    assert map_data.neighborhoods["median_income_display"].tolist() == [
        "$100,000",
        "$150,000",
        "Unavailable",
    ]
    assert map_data.neighborhoods["pct_bachelors_plus_display"].tolist() == [
        "50.0%",
        "70.0%",
        "Unavailable",
    ]


def test_build_base_map_deck_can_hide_demographic_fill(tmp_path) -> None:
    database_path = tmp_path / "app.duckdb"
    tract_path = tmp_path / "tracts.geojson"
    _write_tract_fixture(tract_path)
    _write_gold_fixtures(database_path)
    map_data = prepare_base_map_data(database_path, tract_path, metric="median_income")

    with_demographics = build_base_map_deck(map_data, layer_mode="Tracts", show_demographics=True)
    without_demographics = build_base_map_deck(
        map_data,
        layer_mode="Neighborhoods",
        show_demographics=False,
    )

    assert [layer.id for layer in with_demographics.layers] == [
        "demographic-fill",
        "nta-boundaries",
    ]
    assert [layer.id for layer in without_demographics.layers] == [
        "neighborhood-boundaries",
    ]
    assert with_demographics.layers[-1].pickable is False
    assert with_demographics.layers[-1].filled is False
    assert without_demographics.layers[0].pickable is True
    assert without_demographics.layers[0].filled is True
    assert without_demographics._tooltip["html"] == "{tooltip_html}"
    assert with_demographics._tooltip["html"] == "{tooltip_html}"
    assert "Median household income: $100,000" in (
        without_demographics.layers[0].data[0]["nta_summary_tooltip"]
    )
    assert "Median household income: $100,000" in (
        without_demographics.layers[0].data[0]["tooltip_html"]
    )
    assert "Median household income: $100,000" in (
        with_demographics.layers[0].data[0]["selected_metric_tooltip"]
    )


def test_build_base_map_deck_can_highlight_selected_neighborhood(tmp_path) -> None:
    database_path = tmp_path / "app.duckdb"
    tract_path = tmp_path / "tracts.geojson"
    _write_tract_fixture(tract_path)
    _write_gold_fixtures(database_path)
    map_data = prepare_base_map_data(database_path, tract_path, metric="median_income")

    deck = build_base_map_deck(
        map_data,
        layer_mode="Neighborhoods",
        show_demographics=True,
        selected_nta_id="BK0101",
    )

    assert "selected-nta-highlight" in [layer.id for layer in deck.layers]


def test_prepare_poi_points_supports_category_filtering() -> None:
    poi = pd.DataFrame(
        [
            {
                "poi_id": "poi_1",
                "source_list_names": '["Bookstores", "Favorites"]',
                "category": "bookstores",
                "categories": '["bookstores"]',
                "primary_category": "bookstores",
                "name": "Ursula Bookshop",
                "address": "1016 Union St, Brooklyn, NY",
                "lat": 40.674,
                "lon": -73.963,
            },
            {
                "poi_id": "poi_2",
                "source_list_names": '["Museums"]',
                "category": "museums",
                "categories": '["museums"]',
                "primary_category": "museums",
                "name": "Brooklyn Museum",
                "address": "200 Eastern Pkwy, Brooklyn, NY",
                "lat": 40.671,
                "lon": -73.964,
            },
        ]
    )

    points = prepare_poi_points(poi)
    filtered = filter_poi_points_by_categories(points, ("Bookstores",))

    assert available_poi_categories(points) == ["Bookstores", "Museums"]
    assert filtered["name"].tolist() == ["Ursula Bookshop"]


def test_prepare_poi_points_supports_subcategory_filtering_and_legend() -> None:
    poi = pd.DataFrame(
        [
            {
                "poi_id": "poi_1",
                "source_list_names": '["Restaurants"]',
                "category": "restaurants",
                "subcategory": "pizza",
                "categories": '["restaurants"]',
                "primary_category": "restaurants",
                "primary_subcategory": "pizza",
                "name": "L'industrie Pizzeria",
                "address": "254 S 2nd St, Brooklyn, NY",
                "lat": 40.714,
                "lon": -73.959,
            },
            {
                "poi_id": "poi_2",
                "source_list_names": '["Restaurants"]',
                "category": "restaurants",
                "subcategory": "italian",
                "categories": '["restaurants"]',
                "primary_category": "restaurants",
                "primary_subcategory": "italian",
                "name": "Lilia",
                "address": "567 Union Ave, Brooklyn, NY",
                "lat": 40.717,
                "lon": -73.951,
            },
        ]
    )

    points = prepare_poi_points(poi)
    filtered = filter_poi_points_by_categories(points, ("Restaurants",), ("Pizza",))
    legend = poi_color_legend_rows(points)

    assert available_poi_subcategories(points) == ["Italian", "Pizza"]
    assert filtered["name"].tolist() == ["L'industrie Pizzeria"]
    assert "Sub Category: Pizza" in points.iloc[0]["tooltip_html"]
    assert set(legend["Sub Category"].tolist()) == {"Italian", "Pizza"}
    assert "List: Restaurants" in filtered.iloc[0]["tooltip_html"]
    assert "Type: Restaurants" in filtered.iloc[0]["tooltip_html"]


def test_build_base_map_deck_adds_poi_layer_when_enabled(tmp_path) -> None:
    database_path = tmp_path / "app.duckdb"
    tract_path = tmp_path / "tracts.geojson"
    _write_tract_fixture(tract_path)
    _write_gold_fixtures(database_path)
    map_data = prepare_base_map_data(database_path, tract_path, metric="median_income")
    poi_points = prepare_poi_points(
        pd.DataFrame(
            [
                {
                    "poi_id": "poi_1",
                    "source_list_names": '["Bookstores"]',
                    "category": "bookstores",
                    "categories": '["bookstores"]',
                    "primary_category": "bookstores",
                    "name": "Ursula Bookshop",
                    "address": "1016 Union St, Brooklyn, NY",
                    "lat": 40.674,
                    "lon": -73.963,
                }
            ]
        )
    )

    deck = build_base_map_deck(map_data, poi_points=poi_points, show_pois=True)

    assert [layer.id for layer in deck.layers] == [
        "demographic-fill",
        "nta-boundaries",
        "poi-points",
    ]
    assert deck.layers[-1].pickable is True
    assert deck.layers[-1].data[0]["name"] == "Ursula Bookshop"


def test_prepare_public_poi_points_supports_category_filtering_and_aliases() -> None:
    poi = pd.DataFrame(
        [
            {
                "poi_id": "public_1",
                "source_system": "nyc_open_data",
                "source_id": "landmark:1",
                "category": "landmark",
                "subcategory": "historic_district",
                "name": "Historic Block",
                "address": "Brooklyn, NY",
                "lat": 40.67,
                "lon": -73.95,
            },
            {
                "poi_id": "public_2",
                "source_system": "nyc_open_data",
                "source_id": "museum:1",
                "category": "museum_institutional",
                "subcategory": "museum",
                "name": "City Museum",
                "address": "Manhattan, NY",
                "lat": 40.78,
                "lon": -73.97,
            },
        ]
    )

    points = prepare_public_poi_points(poi)
    filtered = filter_public_poi_points_by_categories(points, ("museum_institution",))

    assert available_public_poi_categories(points) == ["landmark", "museum_institutional"]
    assert filtered["name"].tolist() == ["City Museum"]
    assert "Source: NYC Open Data" in filtered.iloc[0]["tooltip_html"]
    assert "Subtype: museum" in filtered.iloc[0]["tooltip_html"]


def test_filter_points_to_supported_geography_drops_points_outside_loaded_tracts(tmp_path) -> None:
    database_path = tmp_path / "app.duckdb"
    tract_path = tmp_path / "tracts.geojson"
    _write_tract_fixture(tract_path)
    _write_gold_fixtures(database_path)
    map_data = prepare_base_map_data(database_path, tract_path, metric="median_income")
    points = pd.DataFrame(
        [
            {"name": "Inside Brooklyn", "lat": 40.705, "lon": -73.995},
            {"name": "Outside Jersey", "lat": 40.735, "lon": -74.20},
        ]
    )

    filtered = filter_points_to_supported_geography(points, map_data.tracts)

    assert filtered["name"].tolist() == ["Inside Brooklyn"]


def test_build_base_map_deck_adds_public_poi_layer_when_enabled(tmp_path) -> None:
    database_path = tmp_path / "app.duckdb"
    tract_path = tmp_path / "tracts.geojson"
    _write_tract_fixture(tract_path)
    _write_gold_fixtures(database_path)
    map_data = prepare_base_map_data(database_path, tract_path, metric="median_income")
    public_poi_points = prepare_public_poi_points(
        pd.DataFrame(
            [
                {
                    "poi_id": "public_1",
                    "source_system": "osm",
                    "source_id": "pharmacy:1",
                    "category": "pharmacy",
                    "subcategory": "pharmacy",
                    "name": "Neighborhood Pharmacy",
                    "address": "1 Main St, Brooklyn, NY",
                    "lat": 40.674,
                    "lon": -73.963,
                }
            ]
        )
    )

    deck = build_base_map_deck(
        map_data,
        public_poi_points=public_poi_points,
        show_public_pois=True,
    )

    assert [layer.id for layer in deck.layers] == [
        "demographic-fill",
        "nta-boundaries",
        "public-poi-points",
    ]
    assert deck.layers[-1].pickable is True
    assert deck.layers[-1].data[0]["name"] == "Neighborhood Pharmacy"


def test_load_poi_map_data_prefers_v2_table(tmp_path) -> None:
    database_path = tmp_path / "app.duckdb"
    poi = pd.DataFrame(
        [
            {
                "poi_id": "poi_1",
                "source_system": "google_places",
                "source_record_id": '["src_1"]',
                "source_list_names": '["Bookstores"]',
                "category": "bookstores",
                "categories": '["bookstores"]',
                "primary_category": "bookstores",
                "name": "Ursula Bookshop",
                "input_title": "Ursula",
                "note": "[]",
                "tags": "[]",
                "comment": "[]",
                "source_url": "[]",
                "google_place_id": "places/ursula",
                "match_status": "top_candidate",
                "address": "1016 Union St, Brooklyn, NY",
                "lat": 40.674,
                "lon": -73.963,
                "details_fetched_at": "2026-04-20T00:00:00+00:00",
            }
        ]
    )
    with DuckDBService(database_path) as duckdb_service:
        duckdb_service.write_dataframe(
            poi,
            "dim_user_poi_v2",
            schema="property_explorer_gold",
        )

    poi_data = load_poi_map_data(database_path)

    assert poi_data.source == "duckdb_v2"
    assert poi_data.stats == {"poi_count": 1, "source_list_count": 1, "category_count": 1}
    assert poi_data.points.iloc[0]["primary_source_list"] == "Bookstores"
    assert poi_data.points.iloc[0]["category_display"] == "Bookstores"


def test_load_public_poi_map_data_filters_to_ws3_categories(tmp_path) -> None:
    database_path = tmp_path / "app.duckdb"
    public_poi = pd.DataFrame(
        [
            {
                "poi_id": "public_1",
                "source_system": "osm",
                "source_id": "pharmacy:1",
                "category": "pharmacy",
                "subcategory": "pharmacy",
                "name": "Neighborhood Pharmacy",
                "address": "1 Main St, Brooklyn, NY",
                "lat": 40.674,
                "lon": -73.963,
                "attributes": "{}",
                "snapshotted_at": "2026-04-28T00:00:00+00:00",
            },
            {
                "poi_id": "public_2",
                "source_system": "mta_gtfs",
                "source_id": "bus_stop:1",
                "category": "bus_stop",
                "subcategory": "brooklyn",
                "name": "Ignored Bus Stop",
                "address": "",
                "lat": 40.675,
                "lon": -73.964,
                "attributes": "{}",
                "snapshotted_at": "2026-04-28T00:00:00+00:00",
            },
        ]
    )
    with DuckDBService(database_path) as duckdb_service:
        duckdb_service.write_dataframe(
            public_poi,
            "dim_public_poi",
            schema="property_explorer_gold",
        )

    poi_data = load_public_poi_map_data(
        database_path,
        selected_categories=DEFAULT_PUBLIC_POI_CATEGORIES,
    )

    assert poi_data.source == "duckdb_public"
    assert poi_data.stats["poi_count"] == 1
    assert poi_data.stats["configured_category_count"] == len(DEFAULT_PUBLIC_POI_CATEGORIES)
    assert poi_data.points["name"].tolist() == ["Neighborhood Pharmacy"]
