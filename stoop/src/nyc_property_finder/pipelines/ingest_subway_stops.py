"""Ingest subway stops from a local CSV or JSON file."""

from __future__ import annotations

from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile

import pandas as pd

from nyc_property_finder.services.duckdb_service import DuckDBService


SUBWAY_STOP_COLUMNS = ["subway_stop_id", "stop_name", "lines", "lat", "lon"]
REQUIRED_SUBWAY_STOP_COLUMNS = {"subway_stop_id", "stop_name", "lat", "lon"}
COLUMN_ALIASES = {
    "stop_id": "subway_stop_id",
    "id": "subway_stop_id",
    "name": "stop_name",
    "station_name": "stop_name",
    "line": "lines",
}
MTA_SUBWAY_GTFS_URL = "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_subway.zip"


def read_subway_stops_file(path: str | Path) -> pd.DataFrame:
    """Read subway stop records from CSV or JSON."""

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Subway stops file does not exist: {path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".json":
        return pd.read_json(path)
    if suffix == ".zip":
        return read_subway_gtfs_zip(path)
    raise ValueError(f"Unsupported subway stops file format: {suffix}")


def download_subway_gtfs(destination_path: str | Path, source_url: str = MTA_SUBWAY_GTFS_URL) -> Path:
    """Download the MTA subway static GTFS feed."""

    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    urlretrieve(source_url, destination)
    return destination


def read_subway_gtfs_zip(path: str | Path) -> pd.DataFrame:
    """Read and normalize MTA subway GTFS stops from a static feed zip."""

    path = Path(path)
    with ZipFile(path) as gtfs_zip:
        with gtfs_zip.open("stops.txt") as file:
            stops = pd.read_csv(file, dtype=str)

        lines_by_stop = pd.DataFrame(columns=["subway_stop_id", "lines"])
        required_line_files = {"stop_times.txt", "trips.txt"}
        if required_line_files.issubset(set(gtfs_zip.namelist())):
            with gtfs_zip.open("trips.txt") as file:
                trips = pd.read_csv(file, dtype=str, usecols=["route_id", "trip_id"])
            with gtfs_zip.open("stop_times.txt") as file:
                stop_times = pd.read_csv(file, dtype=str, usecols=["trip_id", "stop_id"])

            stop_parent = stops[["stop_id", "parent_station"]].copy() if "parent_station" in stops.columns else None
            stop_routes = stop_times.merge(trips, on="trip_id", how="left")
            if stop_parent is not None:
                stop_routes = stop_routes.merge(stop_parent, on="stop_id", how="left")
                stop_routes["subway_stop_id"] = stop_routes["parent_station"].where(
                    stop_routes["parent_station"].fillna("") != "",
                    stop_routes["stop_id"],
                )
            else:
                stop_routes["subway_stop_id"] = stop_routes["stop_id"]
            lines_by_stop = (
                stop_routes.dropna(subset=["route_id"])
                .groupby("subway_stop_id")["route_id"]
                .apply(lambda values: " ".join(sorted(set(str(value) for value in values if str(value)))))
                .reset_index(name="lines")
            )

    station_rows = stops.copy()
    if "location_type" in station_rows.columns:
        parent_stations = station_rows[station_rows["location_type"].fillna("") == "1"].copy()
        if not parent_stations.empty:
            station_rows = parent_stations

    station_rows = station_rows.rename(
        columns={
            "stop_id": "subway_stop_id",
            "stop_name": "stop_name",
            "stop_lat": "lat",
            "stop_lon": "lon",
        }
    )
    station_rows = station_rows.merge(lines_by_stop, on="subway_stop_id", how="left")
    return station_rows[["subway_stop_id", "stop_name", "lines", "lat", "lon"]]


def normalize_subway_stops(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Normalize subway stop records to the MVP schema."""

    output = dataframe.rename(
        columns={column: COLUMN_ALIASES[column] for column in dataframe.columns if column in COLUMN_ALIASES}
    ).copy()
    missing_columns = REQUIRED_SUBWAY_STOP_COLUMNS.difference(output.columns)
    if missing_columns:
        raise ValueError(f"Missing required subway stop columns: {sorted(missing_columns)}")

    if "lines" not in output.columns:
        output["lines"] = ""

    output["subway_stop_id"] = output["subway_stop_id"].fillna("").astype(str).str.strip()
    output["stop_name"] = output["stop_name"].fillna("").astype(str).str.strip()
    output["lines"] = output["lines"].fillna("").astype(str).str.strip()
    output["lat"] = pd.to_numeric(output["lat"], errors="coerce")
    output["lon"] = pd.to_numeric(output["lon"], errors="coerce")
    output = output.dropna(subset=["lat", "lon"])
    output = output[output["subway_stop_id"] != ""]
    return output[SUBWAY_STOP_COLUMNS].drop_duplicates("subway_stop_id", keep="last").reset_index(drop=True)


def ingest_subway_stops(path: str | Path) -> pd.DataFrame:
    """Read and normalize local subway stop records."""

    return normalize_subway_stops(read_subway_stops_file(path))


def write_subway_stops(
    stops: pd.DataFrame,
    duckdb_service: DuckDBService,
    table_name: str = "dim_subway_stop",
    schema: str = "property_explorer_gold",
) -> None:
    """Persist subway stops."""

    duckdb_service.write_dataframe(stops, table_name=table_name, schema=schema, if_exists="replace")


def run(path: str | Path, database_path: str | Path) -> pd.DataFrame:
    """Pipeline entry point for subway stop ingestion."""

    stops = ingest_subway_stops(path)
    with DuckDBService(database_path) as duckdb_service:
        write_subway_stops(stops, duckdb_service)
    return stops
