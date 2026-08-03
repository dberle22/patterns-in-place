"""Shared helpers for split context-map data products."""

from __future__ import annotations

from pathlib import Path
import sys
import json
from typing import Any

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import deserialize_resolved_site, deserialize_site, read_dataframe, read_json
from data_builds.d3.shared import build_market_pois_frame, build_ring_variants_payload, read_geojson_frame
from site_prep import (
    D6_TRACT_FILL_METRICS,
    Site,
    _build_cumulative_rings,
    _build_context_flood_layer,
    _build_context_road_layer,
    _build_severed_area_features,
    _frame_to_feature_collection,
    _load_overture_pois,
    _ordered_category_candidates,
    _resolve_site_coordinates,
    build_context_tract_fill,
)


def default_fill_metric() -> str:
    """Return the stable seed metric used by shared map builders."""

    metrics = list(D6_TRACT_FILL_METRICS)
    if not metrics:
        raise ValueError("D6_TRACT_FILL_METRICS must define at least one tract-fill layer.")
    return metrics[0]


def build_all_tract_fills(site: Site) -> dict[str, dict[str, Any]]:
    """Build one tract-fill payload per configured metric."""

    payloads: dict[str, dict[str, Any]] = {}
    for metric in D6_TRACT_FILL_METRICS:
        payloads[metric] = build_context_tract_fill(site, metric)
    return payloads


def read_base_rings(artifact_dir: Path) -> gpd.GeoDataFrame:
    """Read the built cumulative ring geometry for one site."""

    return read_geojson_frame(artifact_dir / "base_cumulative_rings.geojson")


def build_adjusted_rings(site: Site, artifact_dir: Path, market_dir: Path) -> dict[str, Any]:
    """Build the water-adjusted ring geometry directly from split D3 source products."""

    market_lines = read_geojson_frame(market_dir / "d3_market_lines.geojson")
    market_polygons = read_geojson_frame(market_dir / "d3_market_polygons.geojson")
    barrier_summary = read_dataframe(artifact_dir / "d3_barrier_summary.csv")
    return build_ring_variants_payload(site, market_lines, market_polygons, barrier_summary)


def build_site_point_and_view_state(artifact_dir: Path) -> tuple[list[dict[str, Any]], dict[str, float]]:
    """Read the resolved site metadata and shape it into the map contract."""

    built_site = deserialize_site(read_json(artifact_dir / "site.json"))
    resolved_site = deserialize_resolved_site(read_json(artifact_dir / "resolved_site.json"), built_site)
    return (
        [
            {
                "name": built_site.address,
                "lat": resolved_site.lat,
                "lon": resolved_site.lon,
                "match_type": resolved_site.match_type,
                "geocode_source": resolved_site.geocode_source,
            }
        ],
        {
            "latitude": float(resolved_site.lat),
            "longitude": float(resolved_site.lon),
            "zoom": 10.5,
        },
    )


def build_poi_rows(site: Site) -> pd.DataFrame:
    """Build site-local point rows for the shared context-map POI layer."""

    pois = _load_overture_pois(site.market_id)
    if pois.empty:
        return pd.DataFrame(columns=["name", "poi_class", "display_category", "lon", "lat", "ring_mi"])
    lat, lon = _resolve_site_coordinates(site)
    rings = _build_cumulative_rings(lat, lon, site.rings_mi)
    largest_ring = rings.sort_values("ring_mi").iloc[-1].geometry
    site_point = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(rings.crs).iloc[0]
    prepared = pois.to_crs(rings.crs).copy()
    prepared = prepared.loc[prepared.geometry.within(largest_ring)].copy()
    if prepared.empty:
        return pd.DataFrame(columns=["name", "poi_class", "display_category", "lon", "lat", "ring_mi"])
    prepared["poi_class"] = prepared.apply(lambda row: row.get("poi_class") or None, axis=1)
    prepared["display_category"] = prepared.apply(_display_poi_category, axis=1)
    prepared["distance_mi"] = prepared.geometry.distance(site_point) / 1609.344
    prepared["ring_mi"] = prepared["distance_mi"].apply(lambda value: _assign_cumulative_ring(value, site.rings_mi))
    prepared = prepared.loc[prepared["ring_mi"].notna()].copy()
    prepared = prepared.to_crs("EPSG:4326")
    return pd.DataFrame(
        {
            "name": prepared["name"] if "name" in prepared.columns else None,
            "poi_class": prepared["poi_class"],
            "display_category": prepared["display_category"],
            "lon": prepared.geometry.x,
            "lat": prepared.geometry.y,
            "ring_mi": prepared["ring_mi"].astype(int),
        }
    ).dropna(subset=["lon", "lat"]).reset_index(drop=True)


def build_road_geojson(site: Site) -> dict[str, Any]:
    """Build the road overlay directly from staged market transport sources."""

    return _build_context_road_layer(site)


def build_flood_geojson(artifact_dir: Path) -> dict[str, Any]:
    """Build the flood overlay from built baseline rings."""

    rings = read_base_rings(artifact_dir)
    return _build_context_flood_layer(rings)


def build_severed_area_geojson(site: Site, artifact_dir: Path, market_dir: Path) -> dict[str, Any]:
    """Build the severed-area shading from baseline and water-adjusted ring geometry."""

    baseline_rings = read_base_rings(artifact_dir)
    adjusted_payload = build_adjusted_rings(site, artifact_dir, market_dir)
    baseline = adjusted_payload["baseline_rings"].to_crs("EPSG:4326")
    adjusted = adjusted_payload["water_adjusted_rings"].to_crs("EPSG:4326")
    return _build_severed_area_features(baseline, adjusted)


def _display_poi_category(row: pd.Series) -> str:
    """Choose the first reader-facing Overture category label available on one POI row."""

    ordered = _ordered_category_candidates(row)
    if not ordered:
        return "Uncategorized"
    return ordered[0].replace("_", " ").title()


def _assign_cumulative_ring(distance_mi: float, rings_mi: list[int]) -> int | None:
    """Assign a POI to the first cumulative ring that contains it."""

    for ring_mi in sorted(int(value) for value in rings_mi):
        if distance_mi <= ring_mi:
            return ring_mi
    return None
