"""Build the app-ready dim_public_poi dataframe."""

from __future__ import annotations

from hashlib import sha256

import pandas as pd

from nyc_property_finder.public_poi.config import DIM_PUBLIC_POI_COLUMNS, NORMALIZED_SOURCE_COLUMNS


def build_dim_public_poi(
    frames: list[pd.DataFrame],
    snapshotted_at: pd.Timestamp | str | None = None,
) -> pd.DataFrame:
    """Normalize source frames into the dim_public_poi column contract."""

    if not frames:
        return pd.DataFrame(columns=DIM_PUBLIC_POI_COLUMNS)

    output = pd.concat(frames, ignore_index=True)
    missing_columns = [
        column for column in NORMALIZED_SOURCE_COLUMNS if column not in output.columns
    ]
    if missing_columns:
        raise ValueError(f"Public POI source frame is missing columns: {missing_columns}")

    output = output[NORMALIZED_SOURCE_COLUMNS].copy()
    output["source_system"] = output["source_system"].fillna("").astype(str).str.strip()
    output["source_id"] = output["source_id"].fillna("").astype(str).str.strip()
    output["poi_id"] = output.apply(
        lambda row: _stable_poi_id(row["source_system"], row["source_id"]),
        axis=1,
    )
    output["lat"] = pd.to_numeric(output["lat"], errors="coerce")
    output["lon"] = pd.to_numeric(output["lon"], errors="coerce")
    output["snapshotted_at"] = pd.to_datetime(snapshotted_at or pd.Timestamp.now(tz="UTC"))
    return output[DIM_PUBLIC_POI_COLUMNS]


def _stable_poi_id(source_system: str, source_id: str) -> str:
    key = f"{source_system.strip().lower()}|{source_id.strip()}"
    return f"public_poi_{sha256(key.encode('utf-8')).hexdigest()[:16]}"
