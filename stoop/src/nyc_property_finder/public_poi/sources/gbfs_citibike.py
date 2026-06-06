"""Citi Bike GBFS public POI source adapter."""

from __future__ import annotations

import json
import shutil
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from nyc_property_finder.public_poi.config import (
    NORMALIZED_SOURCE_COLUMNS,
    SNAPSHOT_DIRS,
    SOURCE_SYSTEM_GBFS,
)

STATION_INFORMATION_URL = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"


def fetch_snapshot(output_dir: str | Path = SNAPSHOT_DIRS["citi_bike"]) -> Path:
    """Download today's Citi Bike GBFS station information snapshot."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    today = datetime.now(UTC).strftime("%Y%m%d")
    path = output_path / f"station_information_{today}.json"
    if not path.exists():
        request = urllib.request.Request(
            STATION_INFORMATION_URL,
            headers={"User-Agent": "nyc-property-finder/0.1"},
        )
        with urllib.request.urlopen(request, timeout=60) as response, path.open("wb") as file:
            shutil.copyfileobj(response, file)
    return path


def load(snapshot_path: str | Path) -> pd.DataFrame:
    """Parse a Citi Bike GBFS station information snapshot."""

    payload = json.loads(Path(snapshot_path).read_text(encoding="utf-8"))
    stations = pd.DataFrame(payload.get("data", {}).get("stations", []))
    if stations.empty:
        return pd.DataFrame(columns=NORMALIZED_SOURCE_COLUMNS)

    return pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_GBFS,
            "source_id": "citi_bike_station:" + stations["station_id"].astype(str),
            "category": "citi_bike_station",
            "subcategory": "station",
            "name": stations["name"].fillna(""),
            "address": stations.get("address", pd.Series("", index=stations.index)).fillna(""),
            "lat": pd.to_numeric(stations["lat"], errors="coerce"),
            "lon": pd.to_numeric(stations["lon"], errors="coerce"),
            "attributes": stations.apply(_attributes, axis=1),
        }
    )[NORMALIZED_SOURCE_COLUMNS]


def _attributes(row: pd.Series) -> str:
    return json.dumps(
        {
            "capacity": _nullable_int(row.get("capacity")),
            "region_id": _nullable_str(row.get("region_id")),
            "short_name": _nullable_str(row.get("short_name")),
        },
        sort_keys=True,
    )


def _nullable_int(value: object) -> int | None:
    if pd.isna(value):
        return None
    return int(value)


def _nullable_str(value: object) -> str | None:
    if pd.isna(value) or value is None:
        return None
    return str(value)
