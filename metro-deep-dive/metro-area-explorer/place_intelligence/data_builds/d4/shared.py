"""Shared helpers for split D4 market and site products."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import geopandas as gpd
import pandas as pd


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from site_prep import (
    D4_FRONTAGE_MAX_SEGMENTS,
    D4_FRONTAGE_SNAP_TOLERANCE_MI,
    Site,
    _load_fdot_aadt_historical_segments,
    _load_fdot_aadt_segments,
    build_cumulative_rings_for_site,
    build_frontage_aadt_trend,
    rank_aadt_segments_in_ring,
    snap_frontage_aadt,
)


def build_market_current_segments(site: Site) -> gpd.GeoDataFrame:
    """Stage the current FDOT AADT segment cache once per market."""

    segments = _load_fdot_aadt_segments(site.market_id)
    if segments.empty:
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")
    return segments.to_crs("EPSG:4326")


def build_market_historical_segments(site: Site) -> gpd.GeoDataFrame:
    """Stage the historical FDOT AADT segment cache once per market."""

    segments = _load_fdot_aadt_historical_segments(site.market_id)
    if segments.empty:
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")
    return segments.to_crs("EPSG:4326")


def read_geojson_frame(path: Path) -> gpd.GeoDataFrame:
    """Read one staged GeoJSON frame, preserving a usable empty geometry frame."""

    if not path.exists():
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")
    frame = gpd.read_file(path)
    if frame.crs is None:
        frame = frame.set_crs("EPSG:4326")
    return frame


def build_frontage_segments_frame(
    site: Site,
    current_segments: gpd.GeoDataFrame,
    *,
    snap_tolerance_mi: float = D4_FRONTAGE_SNAP_TOLERANCE_MI,
    max_segments: int = D4_FRONTAGE_MAX_SEGMENTS,
) -> pd.DataFrame:
    """Snap one site's frontage set from the staged current segment layer."""

    if current_segments.empty:
        return pd.DataFrame()
    rings = build_cumulative_rings_for_site(site)
    return snap_frontage_aadt(
        site,
        segments=current_segments,
        target_crs=rings.crs,
        snap_tolerance_mi=snap_tolerance_mi,
        max_segments=max_segments,
    )


def build_frontage_trend_frame(
    site: Site,
    frontage_segments: pd.DataFrame,
    historical_segments: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Build the frontage trend from the snapped frontage set plus staged history."""

    return build_frontage_aadt_trend(site, frontage_segments=frontage_segments, historical_segments=historical_segments)


def build_ranked_segments_frame(
    site: Site,
    current_segments: gpd.GeoDataFrame,
    *,
    ring_mi: int = 1,
) -> pd.DataFrame:
    """Rank current AADT segments inside one configured cumulative ring."""

    rings = build_cumulative_rings_for_site(site)
    return rank_aadt_segments_in_ring(site, segments=current_segments, cumulative_rings=rings, ring_mi=ring_mi)


def build_d4_meta(site: Site, current_segments: gpd.GeoDataFrame) -> dict[str, Any]:
    """Build the small D4 meta contract from the staged current segment layer."""

    count_year = int(current_segments["year"].dropna().max()) if not current_segments.empty and current_segments["year"].notna().any() else None
    return {
        "count_year": count_year,
        "copy_note": "AADT is an annual average daily traffic statistic, not a peak-hour observed count.",
    }
