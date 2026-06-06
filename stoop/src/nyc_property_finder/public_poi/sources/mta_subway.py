"""MTA subway public POI source adapter."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pandas as pd

from nyc_property_finder.public_poi.config import (
    DEFAULT_MTA_SUBWAY_GTFS_PATH,
    NORMALIZED_SOURCE_COLUMNS,
    SOURCE_SYSTEM_MTA_GTFS,
)


def load(snapshot_path: str | Path = DEFAULT_MTA_SUBWAY_GTFS_PATH) -> pd.DataFrame:
    """Load subway stations, entrances, and shape centroids from a GTFS zip."""

    gtfs_path = Path(snapshot_path)
    if not gtfs_path.exists():
        raise FileNotFoundError(f"MTA subway GTFS zip does not exist: {gtfs_path}")

    with zipfile.ZipFile(gtfs_path) as gtfs:
        stops = _read_gtfs_csv(
            gtfs,
            "stops.txt",
            ["stop_id", "stop_name", "stop_lat", "stop_lon", "location_type", "parent_station"],
        )
        line_lookup = _station_lines(gtfs, stops)
        frames = [
            _station_rows(stops, line_lookup),
            _entrance_rows(stops, line_lookup),
            _shape_rows(gtfs),
        ]

    return pd.concat(frames, ignore_index=True)[NORMALIZED_SOURCE_COLUMNS]


def _read_gtfs_csv(gtfs: zipfile.ZipFile, filename: str, usecols: list[str]) -> pd.DataFrame:
    return pd.read_csv(gtfs.open(filename), usecols=usecols, dtype=str, keep_default_na=False)


def _station_lines(gtfs: zipfile.ZipFile, stops: pd.DataFrame) -> dict[str, list[str]]:
    stop_parent = stops.set_index("stop_id")["parent_station"].to_dict()
    trips = _read_gtfs_csv(gtfs, "trips.txt", ["trip_id", "route_id"])
    stop_times = _read_gtfs_csv(gtfs, "stop_times.txt", ["trip_id", "stop_id"])
    routes = _read_gtfs_csv(gtfs, "routes.txt", ["route_id", "route_short_name"])

    served_stops = stop_times.merge(trips, on="trip_id", how="left").merge(
        routes,
        on="route_id",
        how="left",
    )
    served_stops["station_id"] = served_stops["stop_id"].map(
        lambda stop_id: stop_parent.get(stop_id) or stop_id
    )

    line_lookup: dict[str, list[str]] = {}
    for station_id, group in served_stops.groupby("station_id")["route_short_name"]:
        lines = sorted({line for line in group.astype(str) if line})
        if lines:
            line_lookup[str(station_id)] = lines
    return line_lookup


def _station_rows(stops: pd.DataFrame, line_lookup: dict[str, list[str]]) -> pd.DataFrame:
    stations = stops.loc[stops["location_type"] == "1"].copy()
    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_MTA_GTFS,
            "source_id": "subway_station:" + stations["stop_id"],
            "category": "subway_station",
            "subcategory": "station",
            "name": stations["stop_name"],
            "address": "",
            "lat": pd.to_numeric(stations["stop_lat"], errors="coerce"),
            "lon": pd.to_numeric(stations["stop_lon"], errors="coerce"),
            "attributes": stations["stop_id"].map(
                lambda stop_id: _json_attributes({"lines": line_lookup.get(str(stop_id), [])})
            ),
        }
    )


def _entrance_rows(stops: pd.DataFrame, line_lookup: dict[str, list[str]]) -> pd.DataFrame:
    entrances = stops.loc[stops["location_type"] == "2"].copy()
    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_MTA_GTFS,
            "source_id": "subway_entrance:" + entrances["stop_id"],
            "category": "subway_entrance",
            "subcategory": "entrance",
            "name": entrances["stop_name"],
            "address": "",
            "lat": pd.to_numeric(entrances["stop_lat"], errors="coerce"),
            "lon": pd.to_numeric(entrances["stop_lon"], errors="coerce"),
            "attributes": entrances["parent_station"].map(
                lambda station_id: _json_attributes(
                    {"parent_station": station_id, "lines": line_lookup.get(str(station_id), [])}
                )
            ),
        }
    )


def _shape_rows(gtfs: zipfile.ZipFile) -> pd.DataFrame:
    shapes = pd.read_csv(
        gtfs.open("shapes.txt"),
        usecols=["shape_id", "shape_pt_lat", "shape_pt_lon"],
        dtype={"shape_id": str},
    )
    grouped = (
        shapes.groupby("shape_id", as_index=False)
        .agg(
            lat=("shape_pt_lat", "mean"),
            lon=("shape_pt_lon", "mean"),
            point_count=("shape_pt_lat", "size"),
        )
        .sort_values("shape_id")
    )
    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_MTA_GTFS,
            "source_id": "subway_line:" + grouped["shape_id"],
            "category": "subway_line",
            "subcategory": "shape_centroid",
            "name": "Subway shape " + grouped["shape_id"],
            "address": "",
            "lat": grouped["lat"],
            "lon": grouped["lon"],
            "attributes": grouped.apply(
                lambda row: _json_attributes(
                    {"shape_id": row["shape_id"], "point_count": int(row["point_count"])}
                ),
                axis=1,
            ),
        }
    )


def _json_attributes(value: dict[str, object]) -> str:
    return json.dumps(value, sort_keys=True)
