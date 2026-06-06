"""NYC Ferry and PATH public POI source adapter."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from nyc_property_finder.public_poi.config import (
    NORMALIZED_SOURCE_COLUMNS,
    SNAPSHOT_DIRS,
    SOURCE_SYSTEM_HAND_ENTRY,
)

DEFAULT_TERMINALS_PATH = SNAPSHOT_DIRS["ferry_path"] / "terminals.csv"


def load(snapshot_path: str | Path = DEFAULT_TERMINALS_PATH) -> pd.DataFrame:
    """Load hand-maintained NYC Ferry terminal and PATH station rows."""

    path = Path(snapshot_path)
    if not path.exists():
        raise FileNotFoundError(f"Ferry/PATH hand-entry CSV does not exist: {path}")

    rows = pd.read_csv(path, dtype=str, keep_default_na=False)
    required = {"source_id", "category", "name", "address", "lat", "lon", "notes"}
    missing = required.difference(rows.columns)
    if missing:
        raise ValueError(f"Ferry/PATH CSV is missing columns: {sorted(missing)}")

    output = pd.DataFrame(
        {
            "source_system": SOURCE_SYSTEM_HAND_ENTRY,
            "source_id": rows["category"] + ":" + rows["source_id"],
            "category": rows["category"],
            "subcategory": rows["category"].str.replace("_", " ", regex=False),
            "name": rows["name"],
            "address": rows["address"],
            "lat": pd.to_numeric(rows["lat"], errors="coerce"),
            "lon": pd.to_numeric(rows["lon"], errors="coerce"),
            "attributes": rows["notes"].map(
                lambda notes: json.dumps({"notes": notes}, sort_keys=True)
            ),
        }
    )
    return output[NORMALIZED_SOURCE_COLUMNS]
