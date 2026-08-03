"""Shared helpers for split D3 source and site products."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from site_prep import (
    D3_BARRIER_SPACING_THRESHOLD_MI,
    D3_FRONTAGE_DISTANCE_THRESHOLD_MI,
    D3_JOB_BREAKOUT_COLUMNS,
    D3_SITE_CARD_SEVERED_POP_SHARE_THRESHOLD,
    Site,
    _apportion_metric_series,
    _build_barrier_summary,
    _build_cumulative_ring_series,
    _build_cumulative_rings,
    _build_typology_input,
    _collapse_linear_barriers,
    _compute_crossing_spacing,
    _compute_cumulative_weighted_population,
    _compute_severed_area_share,
    _compute_severed_population_share,
    _load_osm_lines,
    _load_osm_points,
    _load_osm_polygons,
    _load_overture_pois,
    _prepare_water_barriers,
    _query_lodes_surface,
    _resolve_site_coordinates,
    classify_node_typology,
    classify_poi,
)


def normalize_weight_table(weight_table: pd.DataFrame) -> pd.DataFrame:
    """Keep tract ids string-typed so site-level D3 joins are stable."""

    if weight_table.empty:
        return weight_table.copy()
    normalized = weight_table.copy()
    if "tract_geoid" in normalized.columns:
        normalized["tract_geoid"] = normalized["tract_geoid"].astype(str).str.zfill(11)
    return normalized


def build_daytime_tract_inputs_frame(site: Site) -> pd.DataFrame:
    """Stage the tract-level D3 daytime surface from DuckDB once per site."""

    frame = _query_lodes_surface(site.market_id).copy()
    if frame.empty:
        return pd.DataFrame(
            columns=[
                "tract_geoid",
                "year",
                "jobs_total",
                "workers_total",
                *D3_JOB_BREAKOUT_COLUMNS.values(),
            ]
        )
    frame["tract_geoid"] = frame["tract_geoid"].astype(str).str.zfill(11)
    return frame.sort_values("tract_geoid", kind="mergesort").reset_index(drop=True)


def build_daytime_population_frame(site: Site, weight_table: pd.DataFrame, tract_inputs: pd.DataFrame) -> pd.DataFrame:
    """Aggregate the staged daytime tract surface into cumulative ring summaries."""

    if tract_inputs.empty:
        return pd.DataFrame(
            columns=[
                "site_id",
                "ring_mi",
                "year",
                "jobs_total",
                "workers_total",
                "jobs_to_workers_ratio",
                "daytime_net_change",
                "jobs_retail",
                "jobs_accommodation_food",
                "jobs_health_care",
                "jobs_professional_scientific",
            ]
        )

    tract_inputs = tract_inputs.copy()
    tract_inputs["tract_geoid"] = tract_inputs["tract_geoid"].astype(str).str.zfill(11)
    normalized_weights = normalize_weight_table(weight_table)
    payload = pd.DataFrame({"ring_mi": site.rings_mi})
    jobs_total = _build_cumulative_ring_series(
        _apportion_metric_series("jobs_total", "extensive", tract_inputs.set_index("tract_geoid")["jobs_total"], normalized_weights),
        site.rings_mi,
    )
    workers_total = _build_cumulative_ring_series(
        _apportion_metric_series("workers_total", "extensive", tract_inputs.set_index("tract_geoid")["workers_total"], normalized_weights),
        site.rings_mi,
    )
    payload["jobs_total"] = payload["ring_mi"].map(jobs_total).astype(float)
    payload["workers_total"] = payload["ring_mi"].map(workers_total).astype(float)
    payload["jobs_to_workers_ratio"] = payload["jobs_total"] / payload["workers_total"].replace({0: pd.NA})
    payload["daytime_net_change"] = payload["jobs_total"] - payload["workers_total"]

    for breakout_label, column_name in D3_JOB_BREAKOUT_COLUMNS.items():
        apportioned = _apportion_metric_series(
            column_name,
            "extensive",
            tract_inputs.set_index("tract_geoid")[column_name],
            normalized_weights,
        )
        cumulative = _build_cumulative_ring_series(apportioned, site.rings_mi)
        payload[f"jobs_{breakout_label}"] = payload["ring_mi"].map(cumulative).astype(float)

    payload["site_id"] = site.site_id
    payload["year"] = int(tract_inputs["year"].max())
    return payload[
        [
            "site_id",
            "ring_mi",
            "year",
            "jobs_total",
            "workers_total",
            "jobs_to_workers_ratio",
            "daytime_net_change",
            "jobs_retail",
            "jobs_accommodation_food",
            "jobs_health_care",
            "jobs_professional_scientific",
        ]
    ]


def build_market_pois_frame(site: Site) -> pd.DataFrame:
    """Stage market-wide POIs once so site counts can be separate and repeatable."""

    pois = _load_overture_pois(site.market_id)
    if pois.empty:
        return pd.DataFrame(columns=["name", "poi_class", "lon", "lat"])
    pois = pois.copy()
    pois["poi_class"] = pois.apply(classify_poi, axis=1)
    pois = pois.loc[pois["poi_class"].notna()].copy()
    if pois.empty:
        return pd.DataFrame(columns=["name", "poi_class", "lon", "lat"])
    pois = pois.to_crs("EPSG:4326")
    return pd.DataFrame(
        {
            "name": pois["name"] if "name" in pois.columns else None,
            "poi_class": pois["poi_class"],
            "lon": pois.geometry.x,
            "lat": pois.geometry.y,
        }
    ).dropna(subset=["lon", "lat"]).reset_index(drop=True)


def build_poi_counts_frame(site: Site, market_pois: pd.DataFrame) -> pd.DataFrame:
    """Count staged POIs inside each cumulative ring for one site."""

    if market_pois.empty:
        return pd.DataFrame(columns=["site_id", "ring_mi", "poi_class", "count"])
    lat, lon = _resolve_site_coordinates(site)
    rings = _build_cumulative_rings(lat, lon, site.rings_mi)
    pois = gpd.GeoDataFrame(
        market_pois.copy(),
        geometry=gpd.points_from_xy(market_pois["lon"], market_pois["lat"]),
        crs="EPSG:4326",
    ).to_crs(rings.crs)

    rows: list[dict[str, Any]] = []
    for ring in rings.itertuples(index=False):
        within_ring = pois.loc[pois.geometry.within(ring.geometry)].copy()
        if within_ring.empty:
            continue
        counts = within_ring.groupby("poi_class").size()
        for poi_class, count in counts.items():
            rows.append(
                {
                    "site_id": site.site_id,
                    "ring_mi": int(ring.ring_mi),
                    "poi_class": str(poi_class),
                    "count": int(count),
                }
            )
    if not rows:
        return pd.DataFrame(columns=["site_id", "ring_mi", "poi_class", "count"])
    return pd.DataFrame(rows).sort_values(["ring_mi", "poi_class"], kind="mergesort").reset_index(drop=True)


def build_market_infrastructure_frames(site: Site) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Stage market-wide infrastructure layers once for road and barrier work."""

    lines = _load_osm_lines(site.market_id)
    points = _load_osm_points(site.market_id)
    polygons = _load_osm_polygons(site.market_id)
    empty = gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")
    return (
        lines.to_crs("EPSG:4326") if not lines.empty else empty.copy(),
        points.to_crs("EPSG:4326") if not points.empty else empty.copy(),
        polygons.to_crs("EPSG:4326") if not polygons.empty else empty.copy(),
    )


def read_geojson_frame(path: Path) -> gpd.GeoDataFrame:
    """Read one staged GeoJSON frame, preserving a usable empty geometry frame."""

    if not path.exists():
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")
    frame = gpd.read_file(path)
    if frame.crs is None:
        frame = frame.set_crs("EPSG:4326")
    return frame


def build_road_context_payload(site: Site, market_lines: gpd.GeoDataFrame) -> dict[str, Any]:
    """Summarize which road classes reach the site and how close the nearest ramp is."""

    lat, lon = _resolve_site_coordinates(site)
    rings = _build_cumulative_rings(lat, lon, site.rings_mi)
    if market_lines.empty:
        return {
            "fronting_classes": [],
            "nearest_interstate_ramp_miles": None,
            "highways_present": False,
            "rail_present": False,
        }

    projected = market_lines.to_crs(rings.crs).copy()
    site_point = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(rings.crs).iloc[0]
    projected["distance_mi"] = projected.geometry.distance(site_point) / 1609.344
    fronting = projected.loc[projected["distance_mi"] <= D3_FRONTAGE_DISTANCE_THRESHOLD_MI, "layer_group"].dropna().unique().tolist()
    attrs = projected["attributes"].apply(lambda value: value or {})
    ramp_mask = attrs.apply(lambda value: value.get("highway") in {"motorway_link", "trunk_link"})
    nearest_ramp = projected.loc[ramp_mask, "distance_mi"].min() if ramp_mask.any() else None

    return {
        "fronting_classes": sorted(fronting),
        "nearest_interstate_ramp_miles": None if nearest_ramp is None or pd.isna(nearest_ramp) else float(nearest_ramp),
        "highways_present": bool(((projected["layer_group"] == "highways") & (projected["distance_mi"] <= 1.0)).any()),
        "rail_present": bool(((projected["layer_group"] == "rail") & (projected["distance_mi"] <= 1.0)).any()),
    }


def prepare_barrier_features(lines: gpd.GeoDataFrame, polygons: gpd.GeoDataFrame, target_crs) -> gpd.GeoDataFrame:
    """Collect the water/highway/rail geometries that can sever a catchment."""

    barrier_frames: list[gpd.GeoDataFrame] = []
    if not lines.empty:
        for barrier_type in ("highways", "rail"):
            collapsed = _collapse_linear_barriers(lines, barrier_type, target_crs)
            if not collapsed.empty:
                barrier_frames.append(collapsed[["barrier_type", "feature_name", "geometry"]])
    water_barriers = _prepare_water_barriers(lines, polygons, target_crs)
    if not water_barriers.empty:
        barrier_frames.append(water_barriers[["barrier_type", "feature_name", "geometry"]])
    if not barrier_frames:
        return gpd.GeoDataFrame(columns=["barrier_type", "feature_name", "geometry"], geometry="geometry", crs=target_crs)
    return gpd.GeoDataFrame(pd.concat(barrier_frames, ignore_index=True), geometry="geometry", crs=target_crs)


def prepare_crossing_network(lines: gpd.GeoDataFrame, target_crs) -> gpd.GeoDataFrame:
    """Collect the road network that can create barrier crossings."""

    if lines.empty:
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs=target_crs)
    rows = lines.loc[lines["layer_group"].isin(["highways", "major_roads"])].copy()
    if rows.empty:
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs=target_crs)
    return rows.to_crs(target_crs)


def build_barrier_summary_frame(
    site: Site,
    weight_table: pd.DataFrame,
    market_lines: gpd.GeoDataFrame,
    market_polygons: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Compute per-ring barrier signals from staged infrastructure geometry."""

    lat, lon = _resolve_site_coordinates(site)
    rings = _build_cumulative_rings(lat, lon, site.rings_mi)
    if market_lines.empty and market_polygons.empty:
        return pd.DataFrame(
            columns=[
                "site_id",
                "ring_mi",
                "barrier_type",
                "feature_name",
                "crossing_count",
                "mean_crossing_spacing_mi",
                "severed_area_share",
                "severed_population_share",
                "qualified_barrier",
                "site_card_flag",
                "summary",
            ]
        )

    site_point = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(rings.crs).iloc[0]
    ring_population = _compute_cumulative_weighted_population(site.market_id, normalize_weight_table(weight_table), site.rings_mi)
    barriers = prepare_barrier_features(market_lines, market_polygons, rings.crs)
    crossing_network = prepare_crossing_network(market_lines, rings.crs)

    rows: list[dict[str, Any]] = []
    for ring in rings.itertuples(index=False):
        for barrier in barriers.itertuples(index=False):
            if not barrier.geometry.intersects(ring.geometry):
                continue
            barrier_geom = barrier.geometry.intersection(ring.geometry)
            crossing_count, spacing_mi = _compute_crossing_spacing(barrier_geom, barrier.barrier_type, crossing_network)
            qualified = barrier.barrier_type == "water" or (spacing_mi is not None and spacing_mi > D3_BARRIER_SPACING_THRESHOLD_MI)
            severed_area_share, far_side_geom = _compute_severed_area_share(ring.geometry, barrier_geom, site_point)
            severed_pop_share = _compute_severed_population_share(
                ring_mi=int(ring.ring_mi),
                far_side_geom=far_side_geom,
                ring_population=ring_population,
            )
            site_card_flag = bool(
                qualified
                and severed_pop_share is not None
                and severed_pop_share >= D3_SITE_CARD_SEVERED_POP_SHARE_THRESHOLD
            )
            rows.append(
                {
                    "site_id": site.site_id,
                    "ring_mi": int(ring.ring_mi),
                    "barrier_type": barrier.barrier_type,
                    "feature_name": barrier.feature_name,
                    "crossing_count": int(crossing_count),
                    "mean_crossing_spacing_mi": spacing_mi,
                    "severed_area_share": severed_area_share,
                    "severed_population_share": severed_pop_share,
                    "qualified_barrier": bool(qualified),
                    "site_card_flag": site_card_flag,
                    "summary": _build_barrier_summary(
                        barrier_type=barrier.barrier_type,
                        feature_name=barrier.feature_name,
                        crossing_count=int(crossing_count),
                        spacing_mi=spacing_mi,
                    ),
                }
            )
    if not rows:
        return pd.DataFrame(
            columns=[
                "site_id",
                "ring_mi",
                "barrier_type",
                "feature_name",
                "crossing_count",
                "mean_crossing_spacing_mi",
                "severed_area_share",
                "severed_population_share",
                "qualified_barrier",
                "site_card_flag",
                "summary",
            ]
        )
    return pd.DataFrame(rows).sort_values(["ring_mi", "barrier_type", "feature_name"], kind="mergesort").reset_index(drop=True)


def build_ring_variants_payload(
    site: Site,
    market_lines: gpd.GeoDataFrame,
    market_polygons: gpd.GeoDataFrame,
    barrier_summary: pd.DataFrame,
) -> dict[str, Any]:
    """Build baseline and water-adjusted ring comparisons from staged barrier inputs."""

    lat, lon = _resolve_site_coordinates(site)
    baseline_rings = _build_cumulative_rings(lat, lon, site.rings_mi)
    site_point = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(baseline_rings.crs).iloc[0]
    barriers = prepare_barrier_features(market_lines, market_polygons, baseline_rings.crs)

    adjusted_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    for ring in baseline_rings.itertuples(index=False):
        ring_barrier_rows = barrier_summary.loc[
            (barrier_summary["ring_mi"] == int(ring.ring_mi))
            & (barrier_summary["barrier_type"] == "water")
            & (barrier_summary["qualified_barrier"])
        ].copy() if not barrier_summary.empty else pd.DataFrame()

        adjusted_geom = ring.geometry
        removed_features: list[str] = []
        for barrier_name in ring_barrier_rows["feature_name"].dropna().unique().tolist():
            barrier_match = barriers.loc[
                (barriers["barrier_type"] == "water")
                & (barriers["feature_name"] == barrier_name)
            ].copy()
            if barrier_match.empty:
                continue
            barrier_geom = barrier_match.iloc[0].geometry.intersection(ring.geometry)
            _, far_side_geom = _compute_severed_area_share(ring.geometry, barrier_geom, site_point)
            if far_side_geom is None or far_side_geom.is_empty:
                continue
            adjusted_geom = adjusted_geom.difference(far_side_geom)
            removed_features.append(str(barrier_name))

        baseline_area_sqmi = float(ring.geometry.area / 2_589_988.110336)
        adjusted_area_sqmi = float(adjusted_geom.area / 2_589_988.110336)
        removed_area_sqmi = max(baseline_area_sqmi - adjusted_area_sqmi, 0.0)
        removed_area_share = (removed_area_sqmi / baseline_area_sqmi) if baseline_area_sqmi else 0.0

        adjusted_rows.append({"ring_mi": int(ring.ring_mi), "geometry": adjusted_geom})
        comparison_rows.append(
            {
                "site_id": site.site_id,
                "ring_mi": int(ring.ring_mi),
                "baseline_area_sqmi": baseline_area_sqmi,
                "water_adjusted_area_sqmi": adjusted_area_sqmi,
                "removed_area_sqmi": removed_area_sqmi,
                "removed_area_share": removed_area_share,
                "removed_water_features": removed_features,
                "has_water_adjustment": bool(removed_features),
            }
        )

    return {
        "baseline_rings": baseline_rings,
        "water_adjusted_rings": gpd.GeoDataFrame(adjusted_rows, geometry="geometry", crs=baseline_rings.crs),
        "comparison_table": pd.DataFrame(comparison_rows),
    }


def build_node_typology_meta(daytime: pd.DataFrame, poi_counts: pd.DataFrame, road_context: dict[str, Any]) -> dict[str, str]:
    """Build the late-stage D3 node typology metadata from prior site outputs."""

    typology_input = _build_typology_input(daytime, poi_counts, road_context)
    node_label, node_rationale = classify_node_typology(pd.Series(typology_input))
    return {
        "node_typology_label": node_label,
        "node_typology_rationale": node_rationale,
        "copy_note": (
            "Proximity is measured with straight-line rings, not a routed drive-time network. "
            "The baseline rings stay visible for first-pass context, while the water-adjusted companion rings "
            "screen out far-side areas cut off by qualifying river barriers. "
            "Barrier flags are screening heuristics rather than routing results."
        ),
    }
