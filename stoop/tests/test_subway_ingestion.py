import pandas as pd
import pytest
from zipfile import ZipFile

from nyc_property_finder.pipelines.ingest_subway_stops import ingest_subway_stops, run
from nyc_property_finder.services.duckdb_service import DuckDBService
from nyc_property_finder.services.schema import initialize_database


def test_ingest_subway_stops_normalizes_alias_columns(tmp_path) -> None:
    stops_path = tmp_path / "subway_stops.csv"
    pd.DataFrame(
        [
            {"stop_id": "A01", "name": "Main St", "line": "A C", "lat": "40.7", "lon": "-73.9"},
            {"stop_id": "A01", "name": "Main St Updated", "line": "A C E", "lat": "40.7", "lon": "-73.9"},
        ]
    ).to_csv(stops_path, index=False)

    stops = ingest_subway_stops(stops_path)

    assert len(stops) == 1
    assert stops.iloc[0]["subway_stop_id"] == "A01"
    assert stops.iloc[0]["stop_name"] == "Main St Updated"
    assert stops.iloc[0]["lines"] == "A C E"


def test_ingest_subway_stops_requires_minimum_columns(tmp_path) -> None:
    stops_path = tmp_path / "subway_stops.csv"
    pd.DataFrame([{"stop_id": "A01", "lat": 40.7, "lon": -73.9}]).to_csv(stops_path, index=False)

    with pytest.raises(ValueError, match="Missing required subway stop columns"):
        ingest_subway_stops(stops_path)


def test_run_writes_subway_stops_to_duckdb(tmp_path) -> None:
    database_path = tmp_path / "nyc_property_finder.duckdb"
    stops_path = tmp_path / "subway_stops.csv"
    initialize_database(database_path)
    pd.DataFrame(
        [{"subway_stop_id": "A01", "stop_name": "Main St", "lines": "A C", "lat": 40.7, "lon": -73.9}]
    ).to_csv(stops_path, index=False)

    run(path=stops_path, database_path=database_path)

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        stops = duckdb_service.query_df("SELECT * FROM property_explorer_gold.dim_subway_stop")

    assert len(stops) == 1
    assert stops.iloc[0]["stop_name"] == "Main St"


def test_ingest_subway_stops_normalizes_gtfs_zip(tmp_path) -> None:
    gtfs_path = tmp_path / "gtfs_subway.zip"
    with ZipFile(gtfs_path, "w") as gtfs:
        gtfs.writestr(
            "stops.txt",
            "\n".join(
                [
                    "stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station",
                    "A01,Main St,40.7,-73.9,1,",
                    "A01N,Main St Northbound,40.7001,-73.9001,0,A01",
                ]
            ),
        )
        gtfs.writestr("trips.txt", "route_id,trip_id\nA,trip_a\nC,trip_c\n")
        gtfs.writestr("stop_times.txt", "trip_id,stop_id\ntrip_a,A01N\ntrip_c,A01N\n")

    stops = ingest_subway_stops(gtfs_path)

    assert len(stops) == 1
    assert stops.iloc[0]["subway_stop_id"] == "A01"
    assert stops.iloc[0]["stop_name"] == "Main St"
    assert stops.iloc[0]["lines"] == "A C"
