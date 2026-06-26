"""GeoJSON loading helpers for Area Explorer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st


def _data_root() -> Path:
    return Path(__file__).resolve().parents[1] / "data"


def _load_geojson(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@st.cache_data(ttl=3600)
def load_cbsa_geojson() -> dict[str, Any]:
    """Load the pre-baked CBSA GeoJSON."""
    return _load_geojson(_data_root() / "cbsa_boundaries.geojson")


@st.cache_data(ttl=3600)
def load_state_geojson() -> dict[str, Any]:
    """Load the pre-baked state GeoJSON."""
    return _load_geojson(_data_root() / "state_boundaries.geojson")


@st.cache_data(ttl=3600)
def load_county_geojson() -> dict[str, Any]:
    """Load the pre-baked county GeoJSON."""
    return _load_geojson(_data_root() / "county_boundaries.geojson")


def merge_data_onto_geojson(
    geojson: dict[str, Any],
    rows_by_geo_id: dict[str, dict[str, Any]],
    geo_id_property: str,
) -> dict[str, Any]:
    """Attach metric rows to feature properties for downstream rendering."""
    merged = {"type": geojson["type"], "features": []}
    for feature in geojson.get("features", []):
        properties = dict(feature.get("properties", {}))
        geo_id = str(properties.get(geo_id_property, ""))
        if geo_id in rows_by_geo_id:
            properties.update(rows_by_geo_id[geo_id])
        merged["features"].append(
            {
                "type": feature.get("type", "Feature"),
                "geometry": feature.get("geometry"),
                "properties": properties,
            }
        )
    return merged

