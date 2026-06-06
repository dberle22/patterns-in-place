import pandas as pd

from nyc_property_finder.app.neighborhood_qa import (
    build_curated_poi_coverage,
    build_metric_coverage,
    build_pipeline_timestamps,
    build_public_poi_coverage,
    build_source_status,
    build_table_status,
)
from nyc_property_finder.services.duckdb_service import DuckDBService


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
            },
            {
                "tract_id": "36061000100",
                "median_income": None,
                "median_rent": 3200,
                "median_home_value": 1200000,
                "pct_bachelors_plus": 0.7,
                "median_age": 42,
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
            }
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


def test_neighborhood_qa_summarizes_tables_and_metric_coverage(tmp_path) -> None:
    database_path = tmp_path / "app.duckdb"
    _write_gold_fixtures(database_path)

    table_status = build_table_status(database_path)
    tract_coverage = build_metric_coverage(database_path, "tract")

    assert table_status.loc[
        table_status["Area"].isin(["Tract to NTA mapping", "Tract features", "NTA features"]),
        "Status",
    ].tolist() == ["ready", "ready", "ready"]
    assert table_status.loc[
        table_status["Area"] == "Curated POI canonical", "Status"
    ].iloc[0] == "missing"
    assert table_status.loc[table_status["Area"] == "Tract features", "Rows"].iloc[0] == 2

    median_income = tract_coverage[tract_coverage["Column"] == "median_income"].iloc[0]
    assert median_income["Rows"] == 2
    assert median_income["Populated"] == 1
    assert median_income["Coverage label"] == "50.0%"


def test_neighborhood_qa_reports_configured_source_path_status(tmp_path) -> None:
    ready_file = tmp_path / "ready.geojson"
    ready_file.write_text("{}", encoding="utf-8")
    data_sources = {
        "sources": {
            "ready_source": {
                "path": "ready.geojson",
                "expected_format": "geojson",
                "owner": "manual_download",
            },
            "missing_source": {
                "path": "missing.csv",
                "expected_format": "csv",
                "owner": "manual_download",
            },
        }
    }

    source_status = build_source_status(data_sources, project_root=tmp_path)

    assert source_status.loc[source_status["Source"] == "ready_source", "Status"].iloc[0] == "ready"
    assert (
        source_status.loc[source_status["Source"] == "missing_source", "Status"].iloc[0]
        == "missing"
    )


def test_neighborhood_qa_reports_curated_and_public_poi_coverage(tmp_path) -> None:
    database_path = tmp_path / "app.duckdb"
    curated = pd.DataFrame(
        [
            {
                "poi_id": "poi_1",
                "category": "bookstores",
                "subcategory": "independent_bookstores",
                "primary_subcategory": "independent_bookstores",
                "google_place_id": "places/bookstore_1",
                "details_fetched_at": "2026-04-28T01:00:00+00:00",
            },
            {
                "poi_id": "poi_2",
                "category": "other",
                "google_place_id": "places/bookstore_1",
                "details_fetched_at": "2026-04-28T01:30:00+00:00",
            },
        ]
    )
    public = pd.DataFrame(
        [
            {
                "poi_id": "public_1",
                "source_system": "osm",
                "source_id": "pharmacy:1",
                "category": "pharmacy",
                "subcategory": "pharmacy",
                "name": "Neighborhood Pharmacy",
                "address": "",
                "lat": 40.67,
                "lon": -73.95,
                "attributes": "{}",
                "snapshotted_at": "2026-04-28T02:00:00+00:00",
            }
        ]
    )
    with DuckDBService(database_path) as duckdb_service:
        duckdb_service.write_dataframe(curated, "dim_user_poi_v2", schema="property_explorer_gold")
        duckdb_service.write_dataframe(public, "dim_public_poi", schema="property_explorer_gold")

    curated_coverage = build_curated_poi_coverage(database_path)
    public_coverage = build_public_poi_coverage(database_path)
    timestamps = build_pipeline_timestamps(database_path)

    curated_summary = curated_coverage.attrs["summary"]
    public_summary = public_coverage.attrs["summary"]

    assert curated_summary["duplicate_place_ids"] == 1
    assert curated_summary["unresolved_rows"] == 1
    assert curated_summary["rows_without_place_details"] == 0
    assert curated_coverage.loc[
        (curated_coverage["Category"] == "bookstores")
        & (curated_coverage["Subcategory"] == "independent_bookstores"),
        "Present",
    ].iloc[0]
    assert not curated_coverage.loc[
        (curated_coverage["Category"] == "restaurants")
        & (curated_coverage["Subcategory"] == "pizza"),
        "Present",
    ].iloc[0]
    assert "poi_bookstores_nyc.csv" in curated_coverage.loc[
        (curated_coverage["Category"] == "bookstores")
        & (curated_coverage["Subcategory"] == "independent_bookstores"),
        "Expected files",
    ].iloc[0]

    assert public_coverage.loc[public_coverage["Category"] == "pharmacy", "Present"].iloc[0]
    assert not public_coverage.loc[public_coverage["Category"] == "bank", "Present"].iloc[0]
    assert public_coverage.loc[
        public_coverage["Category"] == "pharmacy", "Included in WS3 UI"
    ].iloc[0]
    assert public_coverage.loc[
        public_coverage["Category"] == "pharmacy", "Source systems"
    ].iloc[0] == "osm"
    assert public_summary["latest_snapshot"] is not None
    assert public_summary["total_rows"] == 1

    assert {
        "DuckDB file",
        "Curated POI details",
        "Public POI snapshot",
        "Curated POI resolution cache",
        "Curated POI details cache",
    }.issubset(set(timestamps["Asset"]))
