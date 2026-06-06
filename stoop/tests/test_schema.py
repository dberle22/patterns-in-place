from nyc_property_finder.services.duckdb_service import DuckDBService
from nyc_property_finder.services.schema import initialize_database


def test_initialize_database_creates_expected_property_explorer_gold_tables(tmp_path) -> None:
    database_path = tmp_path / "nyc_property_finder.duckdb"

    executed_files = initialize_database(database_path)

    assert executed_files
    with DuckDBService(database_path, read_only=True) as duckdb_service:
        tables = duckdb_service.query_df(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'property_explorer_gold'
            ORDER BY table_name
            """
        )["table_name"].tolist()

    assert tables == [
        "dim_property_listing",
        "dim_public_poi",
        "dim_subway_stop",
        "dim_tract_to_nta",
        "dim_user_poi",
        "dim_user_poi_v2",
        "dim_user_poi_v3",
        "fct_nta_features",
        "fct_property_context",
        "fct_tract_features",
        "fct_user_shortlist",
        "stg_user_poi_google_takeout",
        "stg_user_poi_manual_upload",
        "stg_user_poi_web_scrape",
    ]


def test_initialize_database_is_idempotent(tmp_path) -> None:
    database_path = tmp_path / "nyc_property_finder.duckdb"

    initialize_database(database_path)
    initialize_database(database_path)

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        table_count = duckdb_service.query_df(
            """
            SELECT COUNT(*) AS table_count
            FROM information_schema.tables
            WHERE table_schema = 'property_explorer_gold'
            """
        )["table_count"].iloc[0]

    assert table_count == 14


def test_initialize_database_creates_expected_neighborhood_character_tables(tmp_path) -> None:
    database_path = tmp_path / "nyc_property_finder.duckdb"

    initialize_database(database_path)

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        tables = duckdb_service.query_df(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'neighborhood_character_mart'
            ORDER BY table_name
            """
        )["table_name"].tolist()

    assert tables == [
        "nta_boundaries",
        "nta_category_controls",
        "nta_category_density",
        "nta_character_profile",
        "nta_curated_poi_counts",
        "nta_poi_assignments",
        "nta_public_poi_counts",
    ]


def test_user_poi_v2_schema_is_source_aware(tmp_path) -> None:
    database_path = tmp_path / "nyc_property_finder.duckdb"

    initialize_database(database_path)

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        columns = duckdb_service.query_df(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'property_explorer_gold'
              AND table_name = 'dim_user_poi_v2'
            ORDER BY ordinal_position
            """
        )["column_name"].tolist()

    assert columns == [
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


def test_user_poi_v3_schema_promotes_classified_fields(tmp_path) -> None:
    database_path = tmp_path / "nyc_property_finder.duckdb"

    initialize_database(database_path)

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        columns = duckdb_service.query_df(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'property_explorer_gold'
              AND table_name = 'dim_user_poi_v3'
            ORDER BY ordinal_position
            """
        )["column_name"].tolist()

    assert columns == [
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
        "original_category",
        "original_subcategory",
        "original_detail_level_3",
        "classification_method",
        "classification_confidence",
        "classification_score",
        "classification_run_at",
    ]


def test_public_poi_schema_matches_wave_contract(tmp_path) -> None:
    database_path = tmp_path / "nyc_property_finder.duckdb"

    initialize_database(database_path)

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        columns = duckdb_service.query_df(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'property_explorer_gold'
              AND table_name = 'dim_public_poi'
            ORDER BY ordinal_position
            """
        )["column_name"].tolist()

    assert columns == [
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


def test_nta_features_schema_matches_refined_contract(tmp_path) -> None:
    database_path = tmp_path / "nyc_property_finder.duckdb"

    initialize_database(database_path)

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        columns = duckdb_service.query_df(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'property_explorer_gold'
              AND table_name = 'fct_nta_features'
            ORDER BY ordinal_position
            """
        )["column_name"].tolist()

    assert columns == [
        "nta_id",
        "nta_name",
        "borough",
        "tract_count",
        "median_income",
        "median_rent",
        "median_home_value",
        "pct_bachelors_plus",
        "median_age",
        "crime_rate_proxy",
    ]


def test_property_context_schema_has_sprint_3_app_fields(tmp_path) -> None:
    database_path = tmp_path / "nyc_property_finder.duckdb"

    initialize_database(database_path)

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        columns = duckdb_service.query_df(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'property_explorer_gold'
              AND table_name = 'fct_property_context'
            ORDER BY ordinal_position
            """
        )["column_name"].tolist()

    assert columns == [
        "property_id",
        "source",
        "source_listing_id",
        "address",
        "lat",
        "lon",
        "price",
        "beds",
        "baths",
        "listing_type",
        "active",
        "url",
        "ingest_timestamp",
        "tract_id",
        "nta_id",
        "nta_name",
        "nearest_subway_stop",
        "nearest_subway_distance_miles",
        "subway_lines_count",
        "poi_data_available",
        "poi_count_nearby",
        "poi_count_10min",
        "poi_category_counts",
        "neighborhood_score",
        "neighborhood_score_status",
        "mobility_score",
        "personal_fit_score",
        "personal_fit_score_status",
        "property_fit_score",
        "property_fit_score_status",
    ]
