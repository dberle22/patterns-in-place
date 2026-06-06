"""MTA bus public POI source adapter."""

from __future__ import annotations

import json
import shutil
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from nyc_property_finder.public_poi.config import (
    NORMALIZED_SOURCE_COLUMNS,
    SNAPSHOT_DIRS,
    SOURCE_SYSTEM_MTA_GTFS,
)

BOROUGH_FEEDS = {
    "bronx": "http://web.mta.info/developers/data/nyct/bus/google_transit_bronx.zip",
    "brooklyn": "http://web.mta.info/developers/data/nyct/bus/google_transit_brooklyn.zip",
    "manhattan": "http://web.mta.info/developers/data/nyct/bus/google_transit_manhattan.zip",
    "queens": "http://web.mta.info/developers/data/nyct/bus/google_transit_queens.zip",
    "staten_island": (
        "http://web.mta.info/developers/data/nyct/bus/google_transit_staten_island.zip"
    ),
}


def fetch_snapshot(output_dir: str | Path = SNAPSHOT_DIRS["mta_bus"]) -> dict[str, Path]:
    """Download today's five MTA bus GTFS borough snapshots."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    today = datetime.now(UTC).strftime("%Y%m%d")
    snapshots: dict[str, Path] = {}
    for borough, url in BOROUGH_FEEDS.items():
        path = output_path / f"{borough}_{today}.zip"
        if not path.exists():
            request = urllib.request.Request(url, headers={"User-Agent": "nyc-property-finder/0.1"})
            with urllib.request.urlopen(request, timeout=60) as response, path.open("wb") as file:
                shutil.copyfileobj(response, file)
        snapshots[borough] = path
    return snapshots


def load(snapshot_paths: dict[str, str | Path] | list[str | Path] | str | Path) -> pd.DataFrame:
    """Union MTA bus ``stops.txt`` files and dedupe by ``stop_id``."""

    paths = _coerce_snapshot_paths(snapshot_paths)
    frames = [_load_one(path, borough) for borough, path in paths.items()]
    if not frames:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    stops = pd.concat(frames, ignore_index=True)
    stops = stops.sort_values(["source_id", "subcategory"]).drop_duplicates(
        "source_id",
        keep="first",
    )
    return stops[NORMALIZED_SOURCE_COLUMNS].reset_index(drop=True)


def _coerce_snapshot_paths(
    snapshot_paths: dict[str, str | Path] | list[str | Path] | str | Path,
) -> dict[str, Path]:
    if isinstance(snapshot_paths, dict):
        return {borough: Path(path) for borough, path in snapshot_paths.items()}
    if isinstance(snapshot_paths, (str, Path)):
        path = Path(snapshot_paths)
        if path.is_dir():
            return {path.stem.split("_20")[0]: path for path in sorted(path.glob("*.zip"))}
        return {_borough_from_path(path): path}
    return {_borough_from_path(Path(path)): Path(path) for path in snapshot_paths}


def _borough_from_path(path: Path) -> str:
    name = path.stem
    for borough in BOROUGH_FEEDS:
        if name.startswith(borough):
            return borough
    return name


def _load_one(path: Path, borough: str) -> pd.DataFrame:
    with zipfile.ZipFile(path) as gtfs:
        stops = pd.read_csv(
            gtfs.open("stops.txt"),
            usecols=lambda column: column
            in {"stop_id", "stop_name", "stop_lat", "stop_lon", "location_type"},
            dtype=str,
            keep_default_na=False,
        )
    if "location_type" in stops.columns:
        stops = stops.loc[stops["location_type"].isin(["", "0"])].copy()
    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_MTA_GTFS,
            "source_id": "bus_stop:" + stops["stop_id"],
            "category": "bus_stop",
            "subcategory": borough,
            "name": stops["stop_name"],
            "address": "",
            "lat": pd.to_numeric(stops["stop_lat"], errors="coerce"),
            "lon": pd.to_numeric(stops["stop_lon"], errors="coerce"),
            "attributes": stops["stop_id"].map(
                lambda stop_id: json.dumps(
                    {"borough_feed": borough, "stop_id": str(stop_id)},
                    sort_keys=True,
                )
            ),
        }
    )
