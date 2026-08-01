"""Site configuration loading and D2 prep helpers for Place Intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any, Literal

import duckdb
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point, shape
from shapely import wkb
from shapely.ops import linemerge, split, unary_union
import yaml


VALID_ASSET_TYPES = {"retail", "residential", "mixed"}
DEFAULT_RINGS_MI = [1, 3, 5]
DEFAULT_PRIMARY_RING_MI = 3
REPO_ROOT = Path(__file__).resolve().parents[3]
SECTION_ROOT = Path(__file__).resolve().parent
DB_PATH = REPO_ROOT / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
D3_OUTPUTS_ROOT = SECTION_ROOT / "outputs"
D4_FRONTAGE_SNAP_TOLERANCE_MI = 0.1
D4_FRONTAGE_MAX_SEGMENTS = 3
D3_BARRIER_SPACING_THRESHOLD_MI = 1.0
D3_SITE_CARD_SEVERED_POP_SHARE_THRESHOLD = 0.2
D3_FRONTAGE_DISTANCE_THRESHOLD_MI = 0.1
D3_WATER_BARRIER_BUFFER_M = 30.0
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))


@dataclass(frozen=True)
class MetricDefinition:
    """Metadata that keeps D2 querying and labeling consistent across surfaces."""

    metric_id: str
    label: str
    table_name: str
    value_column: str
    kind: Literal["extensive", "intensive"]
    topic: str


METRIC_DEFINITIONS: tuple[MetricDefinition, ...] = (
    MetricDefinition("pop_total", "Population", "population_demographics", "pop_total", "extensive", "population"),
    MetricDefinition("households", "Households", "housing_core_wide", "occ_occupied", "extensive", "households"),
    MetricDefinition("median_age", "Median age", "population_demographics", "median_age", "intensive", "age"),
    MetricDefinition("pct_age_under_18", "Share under 18", "population_demographics", "pct_age_under_18", "intensive", "age"),
    MetricDefinition("pct_age_over_64", "Share 65+", "population_demographics", "pct_age_over_64", "intensive", "age"),
    MetricDefinition("pct_white_nh", "White non-Hispanic share", "population_demographics", "pct_white_nh", "intensive", "race_ethnicity"),
    MetricDefinition("pct_black_nh", "Black non-Hispanic share", "population_demographics", "pct_black_nh", "intensive", "race_ethnicity"),
    MetricDefinition("pct_hispanic", "Hispanic share", "population_demographics", "pct_hispanic", "intensive", "race_ethnicity"),
    MetricDefinition("pct_ba_plus", "BA+ share", "population_demographics", "pct_ba_plus", "intensive", "education"),
    MetricDefinition("median_hh_income", "Median household income", "economics_income_wide", "median_hh_income", "intensive", "income"),
    MetricDefinition("acs_income_pc", "Per-capita income", "economics_income_wide", "acs_income_pc", "intensive", "income"),
    MetricDefinition("pov_rate", "Poverty rate", "economics_income_wide", "pov_rate", "intensive", "income"),
    MetricDefinition("owner_occ_rate", "Owner-occupied share", "housing_core_wide", "owner_occ_rate", "intensive", "housing"),
    MetricDefinition("renter_occ_rate", "Renter-occupied share", "housing_core_wide", "renter_occ_rate", "intensive", "housing"),
    MetricDefinition("vacancy_rate", "Vacancy rate", "housing_core_wide", "vacancy_rate", "intensive", "housing"),
    MetricDefinition("median_home_value", "Median home value", "housing_core_wide", "median_home_value", "intensive", "housing"),
    MetricDefinition("median_gross_rent", "Median gross rent", "housing_core_wide", "median_gross_rent", "intensive", "housing"),
    MetricDefinition("pct_struct_multifam", "Multifamily share", "housing_core_wide", "pct_struct_multifam", "intensive", "housing"),
    MetricDefinition("pct_commute_drive_alone", "Drive-alone share", "transport_built_form_wide", "pct_commute_drive_alone", "intensive", "commute"),
    MetricDefinition("mean_travel_time", "Mean travel time", "transport_built_form_wide", "mean_travel_time", "intensive", "commute"),
    MetricDefinition("pct_hh_0_vehicles", "Zero-vehicle household share", "transport_built_form_wide", "pct_hh_0_vehicles", "intensive", "commute"),
    MetricDefinition("pct_commute_wfh", "Work-from-home share", "transport_built_form_wide", "pct_commute_wfh", "intensive", "commute"),
)
METRIC_DEFINITION_MAP = {metric.metric_id: metric for metric in METRIC_DEFINITIONS}
COMPETITIVE_CATEGORY_VALUES = {
    "department_store",
    "shopping_center",
    "retail",
    "retail_store",
    "mall",
    "clothing_store",
    "shoe_store",
    "discount_store",
    "home_improvement_store",
    "furniture_store",
    "electronics_store",
}
COMPLEMENTARY_CATEGORY_VALUES = {
    "grocery_store",
    "supermarket",
    "specialty_grocery_store",
    "international_grocery_store",
    "pharmacy",
    "drugstore",
    "gym",
    "fitness_center",
    "quick_service_restaurant",
    "fast_food_restaurant",
    "coffee_shop",
    "bank",
    "atm",
    "bank_or_credit_union",
}
ANCHOR_CATEGORY_VALUES = {
    "hospital",
    "medical_center",
    "outpatient_care_facility",
    "university",
    "college",
    "school",
    "civic",
    "government_office",
    "courthouse",
    "airport",
    "port",
    "warehouse",
    "logistics",
}
D3_JOB_BREAKOUT_COLUMNS = {
    "retail": "jobs_ind_retail",
    "accommodation_food": "jobs_ind_accommodation_food",
    "health_care": "jobs_ind_health_care_social_assistance",
    "professional_scientific": "jobs_ind_professional_scientific_technical",
}


@dataclass(frozen=True)
class Site:
    """Typed site configuration shared by all downstream deliverables."""

    site_id: str
    address: str
    lat: float | None
    lon: float | None
    geocode_source: str
    market_id: str
    asset_type: str
    rings_mi: list[int]
    primary_ring_mi: int


@dataclass(frozen=True)
class MetricSkipReason:
    """Structured reason for a metric being absent from the D2 payload."""

    metric: str
    reason: str
    table_name: str


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open the standard repo DuckDB in read-only mode."""

    return duckdb.connect(str(DB_PATH), read_only=True)


def load_site(path: str) -> Site:
    """Load a site YAML file, apply spec defaults, and validate field types."""

    payload = _read_site_yaml(path)
    required_fields = [
        "site_id",
        "address",
        "lat",
        "lon",
        "geocode_source",
        "market_id",
        "asset_type",
    ]
    _assert_required_fields(payload, required_fields)

    rings_mi = _parse_rings(payload.get("rings_mi", DEFAULT_RINGS_MI))
    primary_ring_mi = _parse_primary_ring(
        payload.get("primary_ring_mi", DEFAULT_PRIMARY_RING_MI),
        rings_mi,
    )

    return Site(
        site_id=_parse_required_string(payload["site_id"], "site_id"),
        address=_parse_required_string(payload["address"], "address"),
        lat=_parse_optional_float(payload["lat"], "lat"),
        lon=_parse_optional_float(payload["lon"], "lon"),
        geocode_source=_parse_required_string(payload["geocode_source"], "geocode_source"),
        market_id=_parse_required_string(payload["market_id"], "market_id"),
        asset_type=_parse_asset_type(payload["asset_type"]),
        rings_mi=rings_mi,
        primary_ring_mi=primary_ring_mi,
    )


def build_catchment_profile(site: Site, weight_table: pd.DataFrame) -> pd.DataFrame:
    """Build the long-format D2 catchment surface from tract metrics plus weights."""

    payload = build_d2_profile_payload(site, weight_table)
    return payload["catchment_profile"]


def build_benchmark_table(site: Site) -> pd.DataFrame:
    """Build current-year benchmark rows for the site's primary ring from Gold tables."""

    benchmark_rows: list[dict[str, Any]] = []
    county_geoid, state_fips = _get_site_county_and_state(site)
    for metric in METRIC_DEFINITIONS:
        metric_surface = _query_metric_surface(metric, site.market_id)
        benchmark_frame = metric_surface.loc[
            metric_surface["geo_level_normalized"].isin({"cbsa", "county", "state", "us"})
        ].copy()
        if benchmark_frame.empty:
            continue

        latest_year = int(benchmark_frame["year"].max())
        latest_frame = benchmark_frame.loc[benchmark_frame["year"] == latest_year].copy()
        selector = (
            ((latest_frame["geo_level_normalized"] == "cbsa") & (latest_frame["geo_id"] == str(site.market_id)))
            | ((latest_frame["geo_level_normalized"] == "county") & (latest_frame["geo_id"] == county_geoid))
            | ((latest_frame["geo_level_normalized"] == "state") & (latest_frame["geo_id"] == state_fips))
            | (latest_frame["geo_level_normalized"] == "us")
        )
        selected = latest_frame.loc[selector].copy()
        if selected.empty:
            continue

        for row in selected.itertuples(index=False):
            benchmark_rows.append(
                {
                    "site_id": site.site_id,
                    "ring_mi": site.primary_ring_mi,
                    "benchmark_level": _normalize_benchmark_level(str(row.geo_level_normalized)),
                    "benchmark_geo_id": str(row.geo_id),
                    "benchmark_geo_name": str(row.geo_name),
                    "metric": metric.metric_id,
                    "metric_label": metric.label,
                    "topic": metric.topic,
                    "value": float(row.metric_value) if pd.notna(row.metric_value) else None,
                    "year": int(row.year),
                    "source_table": metric.table_name,
                }
            )

    return pd.DataFrame(benchmark_rows).sort_values(
        ["metric", "benchmark_level"],
        kind="mergesort",
    ).reset_index(drop=True) if benchmark_rows else pd.DataFrame(
        columns=[
            "site_id",
            "ring_mi",
            "benchmark_level",
            "benchmark_geo_id",
            "benchmark_geo_name",
            "metric",
            "metric_label",
            "topic",
            "value",
            "year",
            "source_table",
        ]
    )


def compute_percentile(metric: str, ring_value: float, market_id: str) -> tuple[float, int]:
    """Return the percentile position of a ring value against the market tract distribution."""

    metric_def = _get_metric_definition(metric)
    metric_surface = _query_metric_surface(metric_def, market_id)
    tract_frame = metric_surface.loc[metric_surface["geo_level_normalized"] == "tract"].copy()
    if tract_frame.empty:
        raise ValueError(f"No tract rows available for metric '{metric}'.")

    latest_year = int(tract_frame["year"].max())
    latest_values = tract_frame.loc[tract_frame["year"] == latest_year, "metric_value"].dropna()
    denominator = int(len(latest_values))
    if denominator == 0:
        raise ValueError(f"No non-null tract values available for metric '{metric}'.")

    percentile = float((latest_values <= float(ring_value)).sum() / denominator * 100.0)
    return percentile, denominator


def build_d2_profile_payload(site: Site, weight_table: pd.DataFrame) -> dict[str, Any]:
    """Assemble the current D2 payload, including structured skip reasons for the UI."""

    catchment_rows: list[dict[str, Any]] = []
    skip_reasons: list[MetricSkipReason] = []
    for metric in METRIC_DEFINITIONS:
        metric_rows = _build_metric_catchment_rows(site, weight_table, metric)
        if metric_rows.empty:
            skip_reasons.append(
                MetricSkipReason(
                    metric=metric.metric_id,
                    reason="No tract-grain values available for the configured market/rings.",
                    table_name=metric.table_name,
                )
            )
            continue
        catchment_rows.extend(metric_rows.to_dict("records"))

    return {
        "catchment_profile": pd.DataFrame(catchment_rows).sort_values(
            ["metric", "ring_mi"],
            kind="mergesort",
        ).reset_index(drop=True) if catchment_rows else pd.DataFrame(),
        "benchmark_table": build_benchmark_table(site),
        "skip_reasons": pd.DataFrame([reason.__dict__ for reason in skip_reasons]),
    }


def classify_poi(row: pd.Series) -> str | None:
    """Classify one Overture POI into the D3 competitive/complementary/anchor buckets."""

    category_candidates = _ordered_category_candidates(row)
    if any(category in ANCHOR_CATEGORY_VALUES for category in category_candidates):
        return "anchor"
    if any(category in COMPLEMENTARY_CATEGORY_VALUES for category in category_candidates):
        return "complementary"
    if any(category in COMPETITIVE_CATEGORY_VALUES for category in category_candidates):
        return "competitive"
    return None


def classify_node_typology(row: pd.Series) -> tuple[str, str]:
    """Mirror the current Industry D4 heuristic for the site-level D3 node label."""

    infra_score = (
        int(row.get("highways_present", False))
        + int(row.get("rail_present", False))
        + int(row.get("airports_present", False))
        + int(row.get("ports_present", False))
        + min(int(row.get("warehouses_logistics_count", 0)), 2)
    )
    institution_score = (
        min(int(row.get("hospitals_count", 0)), 2)
        + min(int(row.get("universities_count", 0)), 2)
        + min(int(row.get("schools_count", 0)), 1)
    )
    dominant_sector = row.get("dominant_sector_id")

    if infra_score >= 3 and dominant_sector in {"transport_util", "manufacturing", "wholesale", "construction"}:
        return (
            "Infrastructure / logistics-led",
            "Nearby corridors and freight-oriented features outweigh the institutional signals in this site's buffer.",
        )
    if institution_score >= 2 and dominant_sector in {"educ_health", "professional", "other_services"}:
        return (
            "Institutional",
            "Hospitals, universities, or schools show up repeatedly near this site, which fits an institutional node read.",
        )
    if dominant_sector in {"professional", "finance_real", "information"} and infra_score <= 1 and institution_score <= 1:
        return (
            "Office / professional",
            "The dominant sector leans office-oriented and the nearby freight or institutional anchors are limited in this first-pass buffer.",
        )
    return (
        "Mixed",
        "No single infrastructure or institutional signal dominates strongly enough to treat this site as a pure one-type node in v0.",
    )


def get_d3_context_payload(site: Site, weight_table: pd.DataFrame) -> dict[str, Any]:
    """Build the D3 payload from LEHD, Overture, and normalized OSM cache outputs."""

    lat, lon = _resolve_site_coordinates(site)
    cumulative_rings = _build_cumulative_rings(lat, lon, site.rings_mi)
    daytime = build_daytime_population_payload(site, weight_table)
    poi_counts = count_pois_in_rings(site, cumulative_rings)
    road_context = summarize_road_context(site, cumulative_rings)
    barrier_summary = compute_barrier_flags(site, weight_table, cumulative_rings)
    ring_variants = build_ring_variants(site, weight_table, cumulative_rings, barrier_summary)
    typology_input = _build_typology_input(daytime, poi_counts, road_context)
    node_label, node_rationale = classify_node_typology(pd.Series(typology_input))
    return {
        "site_id": site.site_id,
        "daytime_population": daytime,
        "poi_counts": poi_counts,
        "road_context": road_context,
        "barrier_summary": barrier_summary,
        "ring_variants": ring_variants,
        "node_typology_label": node_label,
        "node_typology_rationale": node_rationale,
        "copy_note": (
            "Proximity is measured with straight-line rings, not a routed drive-time network. "
            "The baseline rings stay visible for first-pass context, while the water-adjusted companion rings "
            "screen out far-side areas cut off by qualifying river barriers. "
            "Barrier flags are screening heuristics rather than routing results."
        ),
    }


def build_daytime_population_payload(site: Site, weight_table: pd.DataFrame) -> pd.DataFrame:
    """Apportion jobs/workers into cumulative rings and compute day/night divergence."""

    lodes = _query_lodes_surface(site.market_id)
    rows: list[pd.DataFrame] = []
    jobs_total = _build_cumulative_ring_series(
        _apportion_metric_series("jobs_total", "extensive", lodes.set_index("tract_geoid")["jobs_total"], weight_table),
        site.rings_mi,
    )
    workers_total = _build_cumulative_ring_series(
        _apportion_metric_series("workers_total", "extensive", lodes.set_index("tract_geoid")["workers_total"], weight_table),
        site.rings_mi,
    )
    payload = pd.DataFrame({"ring_mi": site.rings_mi})
    payload["jobs_total"] = payload["ring_mi"].map(jobs_total).astype(float)
    payload["workers_total"] = payload["ring_mi"].map(workers_total).astype(float)
    payload["jobs_to_workers_ratio"] = payload["jobs_total"] / payload["workers_total"].replace({0: np.nan})
    payload["daytime_net_change"] = payload["jobs_total"] - payload["workers_total"]

    for breakout_label, column_name in D3_JOB_BREAKOUT_COLUMNS.items():
        apportioned = _apportion_metric_series(column_name, "extensive", lodes.set_index("tract_geoid")[column_name], weight_table)
        cumulative = _build_cumulative_ring_series(apportioned, site.rings_mi)
        payload[f"jobs_{breakout_label}"] = payload["ring_mi"].map(cumulative).astype(float)

    payload["site_id"] = site.site_id
    payload["year"] = int(lodes["year"].max())
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


def count_pois_in_rings(site: Site, cumulative_rings: gpd.GeoDataFrame | None = None) -> pd.DataFrame:
    """Count competitive/complementary/anchor POIs by direct point-in-ring joins."""

    lat, lon = _resolve_site_coordinates(site)
    rings = cumulative_rings if cumulative_rings is not None else _build_cumulative_rings(lat, lon, site.rings_mi)
    pois = _load_overture_pois(site.market_id)
    if pois.empty:
        return pd.DataFrame(columns=["site_id", "ring_mi", "poi_class", "count"])

    pois = pois.copy()
    pois["poi_class"] = pois.apply(classify_poi, axis=1)
    pois = pois.loc[pois["poi_class"].notna()].copy()
    if pois.empty:
        return pd.DataFrame(columns=["site_id", "ring_mi", "poi_class", "count"])
    pois = pois.to_crs(rings.crs)

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
    return pd.DataFrame(rows).sort_values(["ring_mi", "poi_class"], kind="mergesort").reset_index(drop=True) if rows else pd.DataFrame(
        columns=["site_id", "ring_mi", "poi_class", "count"]
    )


def summarize_road_context(site: Site, cumulative_rings: gpd.GeoDataFrame | None = None) -> dict[str, Any]:
    """Summarize which road classes reach the site and how close the nearest ramp is."""

    lat, lon = _resolve_site_coordinates(site)
    rings = cumulative_rings if cumulative_rings is not None else _build_cumulative_rings(lat, lon, site.rings_mi)
    lines = _load_osm_lines(site.market_id)
    if lines.empty:
        return {
            "fronting_classes": [],
            "nearest_interstate_ramp_miles": None,
            "highways_present": False,
            "rail_present": False,
        }

    projected = lines.to_crs(rings.crs)
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


def compute_barrier_flags(
    site: Site,
    weight_table: pd.DataFrame,
    cumulative_rings: gpd.GeoDataFrame | None = None,
) -> pd.DataFrame:
    """Compute per-ring barrier signals from water/highway/rail geometry."""

    lat, lon = _resolve_site_coordinates(site)
    rings = cumulative_rings if cumulative_rings is not None else _build_cumulative_rings(lat, lon, site.rings_mi)
    lines = _load_osm_lines(site.market_id)
    polygons = _load_osm_polygons(site.market_id)
    if lines.empty and polygons.empty:
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
    ring_population = _compute_cumulative_weighted_population(site.market_id, weight_table, site.rings_mi)
    barriers = _prepare_barrier_features(lines, polygons, rings.crs)
    crossing_network = _prepare_crossing_network(lines, rings.crs)

    rows: list[dict[str, Any]] = []
    for ring in rings.itertuples(index=False):
        for barrier in barriers.itertuples(index=False):
            if not barrier.geometry.intersects(ring.geometry):
                continue
            barrier_geom = barrier.geometry.intersection(ring.geometry)
            crossing_count, spacing_mi = _compute_crossing_spacing(barrier_geom, barrier.barrier_type, crossing_network)
            qualified = barrier.barrier_type == "water" or (
                spacing_mi is not None and spacing_mi > D3_BARRIER_SPACING_THRESHOLD_MI
            )
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
    return pd.DataFrame(rows).sort_values(
        ["ring_mi", "barrier_type", "feature_name"],
        kind="mergesort",
    ).reset_index(drop=True) if rows else pd.DataFrame(
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


def build_ring_variants(
    site: Site,
    weight_table: pd.DataFrame,
    cumulative_rings: gpd.GeoDataFrame | None = None,
    barrier_summary: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Build baseline and water-adjusted ring geometries plus a simple comparison table."""

    lat, lon = _resolve_site_coordinates(site)
    baseline_rings = cumulative_rings if cumulative_rings is not None else _build_cumulative_rings(lat, lon, site.rings_mi)
    if barrier_summary is None:
        if weight_table.empty:
            raise ValueError("`weight_table` is required when `barrier_summary` is not provided.")
        barrier_rows = compute_barrier_flags(site, weight_table, baseline_rings)
    else:
        barrier_rows = barrier_summary
    site_point = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(baseline_rings.crs).iloc[0]
    lines = _load_osm_lines(site.market_id)
    polygons = _load_osm_polygons(site.market_id)
    barriers = _prepare_barrier_features(lines, polygons, baseline_rings.crs)

    adjusted_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    for ring in baseline_rings.itertuples(index=False):
        ring_barrier_rows = barrier_rows.loc[
            (barrier_rows["ring_mi"] == int(ring.ring_mi))
            & (barrier_rows["barrier_type"] == "water")
            & (barrier_rows["qualified_barrier"])
        ].copy() if not barrier_rows.empty else pd.DataFrame()

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
        "baseline_rings": baseline_rings.copy(),
        "water_adjusted_rings": gpd.GeoDataFrame(adjusted_rows, geometry="geometry", crs=baseline_rings.crs),
        "comparison_table": pd.DataFrame(comparison_rows),
    }


def get_d4_traffic_payload(
    site: Site,
    cumulative_rings: gpd.GeoDataFrame | None = None,
    snap_tolerance_mi: float = D4_FRONTAGE_SNAP_TOLERANCE_MI,
    max_frontage_segments: int = D4_FRONTAGE_MAX_SEGMENTS,
) -> dict[str, Any]:
    """Build the D4 traffic payload from cached FDOT AADT segments."""

    lat, lon = _resolve_site_coordinates(site)
    rings = cumulative_rings if cumulative_rings is not None else _build_cumulative_rings(lat, lon, site.rings_mi)
    segments = _load_fdot_aadt_segments(site.market_id)
    if segments.empty:
        return {
            "frontage_segments": pd.DataFrame(),
            "frontage_trend": pd.DataFrame(),
            "ranked_segments_1mi": pd.DataFrame(),
            "count_year": None,
            "copy_note": "AADT is an annual average daily traffic statistic, not a peak-hour observed count.",
        }

    frontage = snap_frontage_aadt(site, segments, rings.crs, snap_tolerance_mi=snap_tolerance_mi, max_segments=max_frontage_segments)
    frontage_trend = build_frontage_aadt_trend(site, frontage_segments=frontage)
    ranked_segments = rank_aadt_segments_in_ring(site, segments, rings, ring_mi=1)
    count_year = int(segments["year"].dropna().max()) if segments["year"].notna().any() else None
    return {
        "frontage_segments": frontage,
        "frontage_trend": frontage_trend,
        "ranked_segments_1mi": ranked_segments,
        "count_year": count_year,
        "copy_note": "AADT is an annual average daily traffic statistic, not a peak-hour observed count.",
    }


def snap_frontage_aadt(
    site: Site,
    segments: gpd.GeoDataFrame | None = None,
    target_crs=None,
    snap_tolerance_mi: float = D4_FRONTAGE_SNAP_TOLERANCE_MI,
    max_segments: int = D4_FRONTAGE_MAX_SEGMENTS,
) -> pd.DataFrame:
    """Return the nearest frontage segment set within tolerance or fail loudly."""

    lat, lon = _resolve_site_coordinates(site)
    frame = segments if segments is not None else _load_fdot_aadt_segments(site.market_id)
    if frame.empty:
        raise ValueError("No FDOT AADT segments are available for frontage snapping.")

    target = target_crs or frame.estimate_utm_crs()
    if target is None:
        raise ValueError("Could not determine a projected CRS for frontage snapping.")
    projected = frame.to_crs(target).copy()
    site_point = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(target).iloc[0]
    projected["distance_mi"] = projected.geometry.distance(site_point) / 1609.344
    frontage = projected.loc[projected["distance_mi"] <= snap_tolerance_mi].copy()
    if frontage.empty:
        nearest_distance = projected["distance_mi"].min()
        raise ValueError(
            f"No FDOT AADT segment was found within {snap_tolerance_mi:.3f} miles of the site. "
            f"Nearest segment distance: {nearest_distance:.3f} miles."
        )

    frontage = frontage.sort_values(["distance_mi", "aadt"], ascending=[True, False], kind="mergesort").head(max_segments)
    return pd.DataFrame(frontage.drop(columns="geometry")).reset_index(drop=True)


def rank_aadt_segments_in_ring(
    site: Site,
    segments: gpd.GeoDataFrame | None = None,
    cumulative_rings: gpd.GeoDataFrame | None = None,
    ring_mi: int = 1,
) -> pd.DataFrame:
    """Rank AADT segments that intersect one cumulative ring."""

    lat, lon = _resolve_site_coordinates(site)
    frame = segments if segments is not None else _load_fdot_aadt_segments(site.market_id)
    if frame.empty:
        return pd.DataFrame()

    rings = cumulative_rings if cumulative_rings is not None else _build_cumulative_rings(lat, lon, site.rings_mi)
    ring_rows = rings.loc[rings["ring_mi"] == int(ring_mi)].copy()
    if ring_rows.empty:
        raise ValueError(f"Ring {ring_mi} is not present in the configured ring set.")
    ring_geom = ring_rows.iloc[0].geometry

    projected = frame.to_crs(rings.crs).copy()
    projected["segment_length_mi_in_ring"] = projected.geometry.intersection(ring_geom).length / 1609.344
    ranked = projected.loc[projected["segment_length_mi_in_ring"] > 0].copy()
    if ranked.empty:
        return pd.DataFrame()
    ranked = ranked.sort_values(["aadt", "segment_length_mi_in_ring"], ascending=[False, False], kind="mergesort")
    return pd.DataFrame(ranked.drop(columns="geometry")).reset_index(drop=True)


def build_frontage_aadt_trend(
    site: Site,
    frontage_segments: pd.DataFrame | None = None,
    historical_segments: gpd.GeoDataFrame | None = None,
) -> pd.DataFrame:
    """Build a one-series frontage-road AADT history from the FDOT five-year layer."""

    frontage = frontage_segments if frontage_segments is not None else pd.DataFrame()
    if frontage.empty:
        return pd.DataFrame(columns=["year", "roadway", "aadt", "distance_mi", "series_role"])
    frontage = frontage.copy()
    if "distance_mi" not in frontage.columns:
        frontage["distance_mi"] = 0.0
    if "aadt" not in frontage.columns:
        frontage["aadt"] = 0.0

    history = historical_segments if historical_segments is not None else _load_fdot_aadt_historical_segments(site.market_id)
    if history.empty:
        return pd.DataFrame(columns=["year", "roadway", "aadt", "distance_mi", "series_role"])

    primary_frontage = frontage.sort_values(["distance_mi", "aadt"], ascending=[True, False], kind="mergesort").iloc[0]
    roadway_id = str(primary_frontage["roadway"]) if pd.notna(primary_frontage["roadway"]) else None
    if roadway_id is None:
        return pd.DataFrame(columns=["year", "roadway", "aadt", "distance_mi", "series_role"])

    matched = history.loc[history["roadway"].astype(str) == roadway_id].copy()
    if matched.empty:
        return pd.DataFrame(columns=["year", "roadway", "aadt", "distance_mi", "series_role"])

    site_point = gpd.GeoSeries([Point(float(site.lon), float(site.lat))], crs="EPSG:4326").to_crs(history.estimate_utm_crs()).iloc[0]
    projected = matched.to_crs(history.estimate_utm_crs()).copy()
    projected["distance_mi"] = projected.geometry.distance(site_point) / 1609.344
    projected = projected.dropna(subset=["year", "aadt"]).copy()
    projected["year"] = projected["year"].astype(int)
    projected["aadt"] = projected["aadt"].astype(float)
    projected = projected.sort_values(["year", "distance_mi", "aadt"], ascending=[True, True, False], kind="mergesort")
    projected = projected.drop_duplicates(subset=["year"], keep="first").copy()
    projected["series_role"] = "primary_frontage"

    output = pd.DataFrame(projected.drop(columns="geometry"))[["year", "roadway", "aadt", "distance_mi", "series_role"]]
    return output.sort_values("year", kind="mergesort").reset_index(drop=True)


def _build_metric_catchment_rows(
    site: Site,
    weight_table: pd.DataFrame,
    metric: MetricDefinition,
) -> pd.DataFrame:
    """Aggregate one metric into ring rows and wire in vintages, percentiles, and change."""

    metric_surface = _query_metric_surface(metric, site.market_id)
    tract_frame = metric_surface.loc[metric_surface["geo_level_normalized"] == "tract"].copy()
    if tract_frame.empty:
        return pd.DataFrame()

    latest_year = int(tract_frame["year"].max())
    latest_values = tract_frame.loc[tract_frame["year"] == latest_year, ["geo_id", "metric_value"]].dropna()
    if latest_values.empty:
        return pd.DataFrame()

    latest_series = latest_values.set_index("geo_id")["metric_value"]
    latest_result = _apportion_metric_series(metric.metric_id, metric.kind, latest_series, weight_table)
    if latest_result.empty:
        return pd.DataFrame()

    prior_year = latest_year - 5
    prior_values = tract_frame.loc[tract_frame["year"] == prior_year, ["geo_id", "metric_value"]].dropna()
    prior_result = (
        _apportion_metric_series(metric.metric_id, metric.kind, prior_values.set_index("geo_id")["metric_value"], weight_table)
        if not prior_values.empty
        else pd.Series(dtype=float)
    )

    rows: list[dict[str, Any]] = []
    for ring_mi, value in latest_result.items():
        percentile = None
        denominator = None
        if int(ring_mi) == int(site.primary_ring_mi):
            percentile, denominator = compute_percentile(metric.metric_id, float(value), site.market_id)

        change_value = None
        change_years = None
        if not prior_result.empty and ring_mi in prior_result.index:
            change_value = float(value) - float(prior_result.loc[ring_mi])
            change_years = f"{prior_year}-{latest_year}"

        rows.append(
            {
                "site_id": site.site_id,
                "ring_mi": int(ring_mi),
                "metric": metric.metric_id,
                "metric_label": metric.label,
                "topic": metric.topic,
                "value": float(value),
                "year": latest_year,
                "source_table": metric.table_name,
                "change_5yr": change_value,
                "change_5yr_period": change_years,
                "cbsa_percentile": percentile,
                "cbsa_percentile_denominator": denominator,
            }
        )

    return pd.DataFrame(rows)


def _apportion_metric_series(
    metric_name: str,
    kind: Literal["extensive", "intensive"],
    metric_series: pd.Series,
    weight_table: pd.DataFrame,
) -> pd.Series:
    """Proxy into `apportion.py` without importing that module at top level."""

    from apportion import apportion

    named_series = metric_series.copy()
    named_series.name = metric_name
    method = "approximate" if _is_median_metric(metric_name) else None
    result = apportion(named_series, weight_table, kind=kind, method=method)
    if isinstance(result.index, pd.MultiIndex):
        # Current D2 work is scoped to one site at a time; flatten to ring rows.
        result = result.droplevel(0)
    return result.sort_index()


def _get_site_county_and_state(site: Site) -> tuple[str, str]:
    """Resolve the site's containing county and state for benchmark lookup."""

    tract_geoid: str
    if site.lat is not None and site.lon is not None:
        from geocode import resolve_tract_from_coordinates

        tract_geoid = resolve_tract_from_coordinates(site.lon, site.lat)
    else:
        from geocode import resolve_site_geocode

        tract_geoid = resolve_site_geocode(site).tract_geoid

    con = get_connection()
    try:
        row = con.execute(
            """
            SELECT county_geoid, state_fips
            FROM patterns_in_place.geo.tracts_all_us
            WHERE tract_geoid = ?
            LIMIT 1
            """,
            [tract_geoid],
        ).fetchone()
    finally:
        con.close()

    if row is None:
        raise ValueError(f"Could not resolve county/state for tract {tract_geoid}.")
    return str(row[0]), str(row[1]).zfill(2)


@lru_cache(maxsize=None)
def _query_metric_surface(metric: MetricDefinition, market_id: str) -> pd.DataFrame:
    """Read tract + benchmark rows for one metric through one shared SQL path."""

    con = get_connection()
    try:
        rows = con.execute(
            f"""
            WITH market_counties AS (
                SELECT DISTINCT county_geoid
                FROM patterns_in_place.silver.xwalk_cbsa_county
                WHERE cbsa_code = ?
            )
            SELECT
                LOWER(t.geo_level) AS geo_level_normalized,
                t.geo_level,
                t.geo_id,
                t.geo_name,
                t.year,
                t.{metric.value_column} AS metric_value
            FROM patterns_in_place.gold.{metric.table_name} t
            LEFT JOIN patterns_in_place.geo.tracts_all_us g
                ON t.geo_level = 'tract'
               AND t.geo_id = g.tract_geoid
            WHERE t.{metric.value_column} IS NOT NULL
              AND (
                    (LOWER(t.geo_level) = 'tract' AND g.county_geoid IN (SELECT county_geoid FROM market_counties))
                 OR (LOWER(t.geo_level) IN ('cbsa', 'county', 'state', 'us'))
              )
              AND (
                    LOWER(t.geo_level) != 'cbsa'
                 OR t.geo_id = ?
              )
            ORDER BY t.year, t.geo_level, t.geo_id
            """,
            [str(market_id), str(market_id)],
        ).fetchdf()
    finally:
        con.close()
    return rows


def _get_metric_definition(metric: str) -> MetricDefinition:
    """Resolve a metric id into its static metadata or fail loudly."""

    if metric not in METRIC_DEFINITION_MAP:
        available = ", ".join(sorted(METRIC_DEFINITION_MAP))
        raise ValueError(f"Unknown metric '{metric}'. Available metrics: {available}")
    return METRIC_DEFINITION_MAP[metric]


def _normalize_benchmark_level(level: str) -> str:
    """Normalize storage-level names to the app's benchmark labels."""

    return "national" if level.lower() == "us" else level.lower()


def _is_median_metric(metric_name: str) -> bool:
    """Mirror the D1 median guard so D2 does not silently bypass it."""

    lowered = metric_name.lower()
    return "median" in lowered or lowered.startswith("med_") or "_med_" in lowered or lowered.endswith("_med")


def _ordered_category_candidates(row: pd.Series) -> list[str]:
    """Apply the Richmond review's preferred category priority for governed rollups."""

    raw_values: list[str] = []
    for key in ("basic_category", "taxonomy_primary"):
        raw_values.extend(_normalize_category_values(row.get(key)))

    hierarchy_value = row.get("taxonomy_hierarchy")
    if isinstance(hierarchy_value, list):
        for item in hierarchy_value:
            raw_values.extend(_normalize_category_values(item))
    else:
        raw_values.extend(_normalize_category_values(hierarchy_value))

    raw_values.extend(_normalize_category_values(row.get("primary_category")))

    seen: set[str] = set()
    ordered_values: list[str] = []
    for value in raw_values:
        if value not in seen:
            ordered_values.append(value)
            seen.add(value)
    return ordered_values


def _normalize_category_values(value: Any) -> list[str]:
    """Normalize one category/taxonomy field into lowercase tokens for matching."""

    if value is None:
        return []
    if isinstance(value, str):
        cleaned = value.strip().lower()
        return [cleaned] if cleaned else []
    return []


def _resolve_site_coordinates(site: Site) -> tuple[float, float]:
    """Return resolved site coordinates, geocoding only if the config is still blank."""

    if site.lat is not None and site.lon is not None:
        return float(site.lat), float(site.lon)
    from geocode import resolve_site_geocode

    resolved = resolve_site_geocode(site)
    return float(resolved.lat), float(resolved.lon)


def _build_cumulative_rings(lat: float, lon: float, rings_mi: list[int]) -> gpd.GeoDataFrame:
    """Convert D1's band geometries into cumulative circles for direct spatial joins."""

    from apportion import build_rings

    bands = build_rings(lat=lat, lon=lon, rings_mi=rings_mi)
    rows: list[dict[str, Any]] = []
    for ring_mi in sorted(rings_mi):
        geometry = unary_union(bands.loc[bands["ring_mi"] <= ring_mi, "geometry"].tolist())
        rows.append({"ring_mi": int(ring_mi), "geometry": geometry})
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=bands.crs)


@lru_cache(maxsize=None)
def _query_lodes_surface(market_id: str) -> pd.DataFrame:
    """Read the latest market-scoped WAC/RAC tract surface needed for D3."""

    con = get_connection()
    try:
        rows = con.execute(
            """
            WITH market_counties AS (
                SELECT DISTINCT county_geoid
                FROM patterns_in_place.silver.xwalk_cbsa_county
                WHERE cbsa_code = ?
            ),
            latest_wac_year AS (
                SELECT MAX(year) AS year
                FROM patterns_in_place.silver.lehd_lodes_wac
                WHERE geo_level = 'tract'
            ),
            latest_rac_year AS (
                SELECT MAX(year) AS year
                FROM patterns_in_place.silver.lehd_lodes_rac
                WHERE geo_level = 'tract'
            )
            SELECT
                w.geo_id AS tract_geoid,
                LEAST(w.year, r.year) AS year,
                w.jobs_total,
                w.jobs_ind_retail,
                w.jobs_ind_accommodation_food,
                w.jobs_ind_health_care_social_assistance,
                w.jobs_ind_professional_scientific_technical,
                r.workers_total
            FROM patterns_in_place.silver.lehd_lodes_wac w
            INNER JOIN patterns_in_place.geo.tracts_all_us g
                ON w.geo_id = g.tract_geoid
            INNER JOIN market_counties c
                ON g.county_geoid = c.county_geoid
            LEFT JOIN patterns_in_place.silver.lehd_lodes_rac r
                ON w.geo_id = r.geo_id
               AND r.geo_level = 'tract'
               AND r.year = (SELECT year FROM latest_rac_year)
            WHERE w.geo_level = 'tract'
              AND w.year = (SELECT year FROM latest_wac_year)
            ORDER BY w.geo_id
            """,
            [str(market_id)],
        ).fetchdf()
    finally:
        con.close()
    return rows


def _build_cumulative_ring_series(band_series: pd.Series, ring_order: list[int]) -> dict[int, float]:
    """Turn band-level values into cumulative ring values for D3 direct spatial outputs."""

    running_total = 0.0
    output: dict[int, float] = {}
    for ring_mi in sorted(ring_order):
        value = band_series.get(ring_mi, 0.0)
        running_total += 0.0 if pd.isna(value) else float(value)
        output[int(ring_mi)] = running_total
    return output


@lru_cache(maxsize=None)
def _load_overture_pois(market_id: str) -> gpd.GeoDataFrame:
    """Load the Jacksonville Overture POI cache as a GeoDataFrame."""

    path = get_spatial_output_dir(market_id) / "overture_pois.parquet"
    if not path.exists():
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")
    con = duckdb.connect()
    try:
        frame = con.execute("SELECT * FROM read_parquet(?)", [str(path)]).fetchdf()
    finally:
        con.close()
    frame["attributes"] = frame["attributes_json"].apply(lambda value: json.loads(value) if isinstance(value, str) and value else {})
    frame["basic_category"] = frame["attributes"].apply(lambda value: value.get("basic_category"))
    frame["taxonomy_primary"] = frame["attributes"].apply(lambda value: value.get("taxonomy_primary"))
    frame["taxonomy_hierarchy"] = frame["attributes"].apply(lambda value: value.get("taxonomy_hierarchy"))
    frame["primary_category"] = frame["attributes"].apply(lambda value: value.get("primary_category"))
    geometry = frame["geometry"].apply(lambda value: shape(json.loads(value)) if isinstance(value, str) and value else None)
    return gpd.GeoDataFrame(frame, geometry=geometry, crs="EPSG:4326").dropna(subset=["geometry"])


def get_spatial_output_dir(market_id: str) -> Path:
    """Return the D3 cache directory for one market."""

    direct = D3_OUTPUTS_ROOT / str(market_id)
    if direct.exists():
        return direct
    aliases = {"27260": "jacksonville_fl"}
    alias = aliases.get(str(market_id))
    if alias and (D3_OUTPUTS_ROOT / alias).exists():
        return D3_OUTPUTS_ROOT / alias
    return direct


def _load_osm_frame(market_id: str, filename: str) -> gpd.GeoDataFrame:
    """Load one normalized OSM cache parquet into a GeoDataFrame."""

    path = get_spatial_output_dir(market_id) / filename
    if not path.exists():
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")
    con = duckdb.connect()
    try:
        frame = con.execute("SELECT * FROM read_parquet(?)", [str(path)]).fetchdf()
    finally:
        con.close()
    frame["attributes"] = frame["attributes_json"].apply(lambda value: json.loads(value) if isinstance(value, str) and value else {})
    geometry = frame["geometry"].apply(lambda value: shape(json.loads(value)) if isinstance(value, str) and value else None)
    return gpd.GeoDataFrame(frame, geometry=geometry, crs="EPSG:4326").dropna(subset=["geometry"])


@lru_cache(maxsize=None)
def _load_osm_lines(market_id: str) -> gpd.GeoDataFrame:
    """Load normalized OSM line features for D3 road/barrier work."""

    return _load_osm_frame(market_id, "osm_infrastructure_lines.parquet")


@lru_cache(maxsize=None)
def _load_osm_points(market_id: str) -> gpd.GeoDataFrame:
    """Load normalized OSM point features for D3 context work."""

    return _load_osm_frame(market_id, "osm_infrastructure_points.parquet")


@lru_cache(maxsize=None)
def _load_osm_polygons(market_id: str) -> gpd.GeoDataFrame:
    """Load normalized OSM polygon features for D3 context work."""

    return _load_osm_frame(market_id, "osm_infrastructure_polygons.parquet")


@lru_cache(maxsize=None)
def _load_fdot_aadt_segments(market_id: str) -> gpd.GeoDataFrame:
    """Load the cached FDOT AADT linework for D4 traffic context."""

    path = get_spatial_output_dir(market_id) / "fdot_aadt_segments.parquet"
    if not path.exists():
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")
    con = duckdb.connect()
    try:
        frame = con.execute("SELECT * FROM read_parquet(?)", [str(path)]).fetchdf()
    finally:
        con.close()
    geometry = frame["geometry"].apply(lambda value: shape(json.loads(value)) if isinstance(value, str) and value else None)
    return gpd.GeoDataFrame(frame, geometry=geometry, crs="EPSG:4326").dropna(subset=["geometry"])


@lru_cache(maxsize=None)
def _load_fdot_aadt_historical_segments(market_id: str) -> gpd.GeoDataFrame:
    """Load the cached FDOT historical AADT linework for frontage trends."""

    path = get_spatial_output_dir(market_id) / "fdot_aadt_historical_segments.parquet"
    if not path.exists():
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")
    con = duckdb.connect()
    try:
        frame = con.execute("SELECT * FROM read_parquet(?)", [str(path)]).fetchdf()
    finally:
        con.close()
    geometry = frame["geometry"].apply(lambda value: shape(json.loads(value)) if isinstance(value, str) and value else None)
    return gpd.GeoDataFrame(frame, geometry=geometry, crs="EPSG:4326").dropna(subset=["geometry"])


def _prepare_barrier_features(lines: gpd.GeoDataFrame, polygons: gpd.GeoDataFrame, target_crs) -> gpd.GeoDataFrame:
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
    return gpd.GeoDataFrame(
        pd.concat(barrier_frames, ignore_index=True),
        geometry="geometry",
        crs=target_crs,
    )


def _prepare_water_barriers(lines: gpd.GeoDataFrame, polygons: gpd.GeoDataFrame, target_crs) -> gpd.GeoDataFrame:
    """Promote fragmented OSM water features into a few meaningful ring-splitting barriers."""

    water_lines = lines.loc[lines["layer_group"] == "water"].copy() if not lines.empty else gpd.GeoDataFrame()
    if water_lines.empty:
        return gpd.GeoDataFrame(columns=["barrier_type", "feature_name", "geometry"], geometry="geometry", crs=target_crs)

    projected_lines = water_lines.to_crs(target_crs).copy()
    projected_lines["feature_name"] = projected_lines["feature_name"].replace("", pd.NA)

    water_surfaces = polygons.loc[polygons["layer_group"] == "water"].copy() if not polygons.empty else gpd.GeoDataFrame()
    projected_surfaces = water_surfaces.to_crs(target_crs).copy() if not water_surfaces.empty else None

    rows: list[dict[str, Any]] = []
    named_lines = projected_lines.loc[projected_lines["feature_name"].notna()].copy()
    for feature_name, feature_rows in named_lines.groupby("feature_name", dropna=True):
        geometry = unary_union(feature_rows.geometry.tolist())
        geometry = _attach_water_surface(geometry, feature_rows, projected_surfaces)
        if geometry is None or geometry.is_empty:
            continue
        rows.append({"barrier_type": "water", "feature_name": str(feature_name), "geometry": geometry})

    if not rows:
        return gpd.GeoDataFrame(columns=["barrier_type", "feature_name", "geometry"], geometry="geometry", crs=target_crs)

    frame = gpd.GeoDataFrame(rows, geometry="geometry", crs=target_crs)
    frame = frame.loc[frame.geometry.notna() & ~frame.geometry.is_empty].copy()
    frame["feature_name"] = frame["feature_name"].astype(str)
    return frame.reset_index(drop=True)


def _collapse_linear_barriers(lines: gpd.GeoDataFrame, barrier_type: str, target_crs) -> gpd.GeoDataFrame:
    """Merge segmented OSM linework into connected barrier corridors."""

    rows = lines.loc[lines["layer_group"] == barrier_type].copy()
    if rows.empty:
        return gpd.GeoDataFrame(columns=["barrier_type", "feature_name", "geometry"], geometry="geometry", crs=target_crs)

    projected = rows.to_crs(target_crs)
    merged = linemerge(unary_union(projected.geometry.tolist()))
    components = list(getattr(merged, "geoms", [merged]))

    output_rows: list[dict[str, Any]] = []
    for idx, geom in enumerate(components, start=1):
        if geom is None or geom.is_empty:
            continue
        if geom.length < 300:
            continue
        output_rows.append(
            {
                "barrier_type": barrier_type,
                "feature_name": f"{barrier_type}_{idx}",
                "geometry": geom,
            }
        )

    return gpd.GeoDataFrame(output_rows, geometry="geometry", crs=target_crs)


def _attach_water_surface(line_geometry, source_rows: gpd.GeoDataFrame, projected_surfaces: gpd.GeoDataFrame | None):
    """Fuse a named river/canal line with nearby water polygons without letting tiny ponds dominate."""

    if projected_surfaces is None or projected_surfaces.empty:
        return line_geometry

    search_area = line_geometry.buffer(D3_WATER_BARRIER_BUFFER_M)
    candidate_surfaces = projected_surfaces.loc[projected_surfaces.geometry.intersects(search_area)].copy()
    if candidate_surfaces.empty:
        return line_geometry

    candidate_surfaces["surface_area"] = candidate_surfaces.geometry.area
    candidate_surfaces = candidate_surfaces.loc[candidate_surfaces["surface_area"] >= 2_500].copy()
    if candidate_surfaces.empty:
        return line_geometry

    merged_surface = unary_union(candidate_surfaces.geometry.tolist())
    merged_boundary = merged_surface.boundary
    if merged_boundary.is_empty:
        return line_geometry
    return unary_union([line_geometry, merged_boundary])


def _prepare_crossing_network(lines: gpd.GeoDataFrame, target_crs) -> gpd.GeoDataFrame:
    """Collect the road network that can create barrier crossings."""

    if lines.empty:
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs=target_crs)
    rows = lines.loc[lines["layer_group"].isin(["highways", "major_roads"])].copy()
    if rows.empty:
        return gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs=target_crs)
    return rows.to_crs(target_crs)


def _extract_intersection_points(geometry) -> list[Point]:
    """Reduce a shapely intersection into representative point locations."""

    if geometry.is_empty:
        return []
    geom_type = geometry.geom_type
    if geom_type == "Point":
        return [geometry]
    if geom_type == "MultiPoint":
        return list(geometry.geoms)
    if geom_type in {"LineString", "LinearRing"}:
        return [geometry.interpolate(0.5, normalized=True)]
    if geom_type == "MultiLineString":
        return [line.interpolate(0.5, normalized=True) for line in geometry.geoms if not line.is_empty]
    if geom_type == "GeometryCollection":
        points: list[Point] = []
        for geom in geometry.geoms:
            points.extend(_extract_intersection_points(geom))
        return points
    return [geometry.representative_point()]


def _compute_crossing_spacing(barrier_geom, barrier_type: str, crossing_network: gpd.GeoDataFrame) -> tuple[int, float | None]:
    """Count crossings and estimate their mean spacing along the barrier feature."""

    if barrier_geom.is_empty or crossing_network.empty:
        return 0, None
    barrier_line = barrier_geom.boundary if barrier_geom.geom_type in {"Polygon", "MultiPolygon"} else barrier_geom
    candidate_lines = crossing_network.loc[crossing_network.geometry.intersects(barrier_geom)].copy()
    crossing_points: list[Point] = []
    for geom in candidate_lines.geometry:
        crossing_points.extend(_extract_intersection_points(geom.intersection(barrier_geom)))
    unique_points: list[Point] = []
    seen: set[tuple[float, float]] = set()
    for point in crossing_points:
        key = (round(point.x, 6), round(point.y, 6))
        if key not in seen:
            seen.add(key)
            unique_points.append(point)
    crossing_count = len(unique_points)
    if crossing_count < 2:
        return crossing_count, None if crossing_count == 0 else float("inf")
    distances = sorted(barrier_line.project(point) for point in unique_points)
    deltas = [distances[idx + 1] - distances[idx] for idx in range(len(distances) - 1)]
    mean_spacing_mi = (float(sum(deltas)) / len(deltas)) / 1609.344
    return crossing_count, mean_spacing_mi


def _compute_severed_area_share(ring_geom, barrier_geom, site_point: Point) -> tuple[float | None, Any | None]:
    """Split a ring by one barrier and measure the portion disconnected from the site."""

    if barrier_geom.is_empty:
        return None, None
    splitter = barrier_geom.boundary if barrier_geom.geom_type in {"Polygon", "MultiPolygon"} else barrier_geom
    try:
        pieces = split(ring_geom, splitter)
    except Exception:
        return None, None
    if len(pieces.geoms) <= 1:
        return 0.0, None
    site_piece = None
    for piece in pieces.geoms:
        if piece.buffer(1e-6).contains(site_point):
            site_piece = piece
            break
    if site_piece is None:
        site_piece = max(pieces.geoms, key=lambda geom: geom.area)
    far_side = [piece for piece in pieces.geoms if piece != site_piece]
    far_side_geom = unary_union(far_side)
    share = float(far_side_geom.area / ring_geom.area) if ring_geom.area else None
    return share, far_side_geom


def _compute_cumulative_weighted_population(market_id: str, weight_table: pd.DataFrame, ring_order: list[int]) -> pd.DataFrame:
    """Combine latest tract population, tract geometry, and cumulative D1 weights for severance reads."""

    con = get_connection()
    try:
        pop_rows = con.execute(
            """
            WITH latest_year AS (
                SELECT MAX(year) AS year
                FROM patterns_in_place.gold.population_demographics
                WHERE geo_level = 'tract'
            )
            SELECT
                p.geo_id AS tract_geoid,
                p.pop_total,
                g.geom_wkb
            FROM patterns_in_place.gold.population_demographics p
            INNER JOIN patterns_in_place.geo.tracts_all_us g
                ON p.geo_id = g.tract_geoid
            INNER JOIN patterns_in_place.silver.xwalk_cbsa_county c
                ON g.county_geoid = c.county_geoid
            WHERE p.geo_level = 'tract'
              AND p.year = (SELECT year FROM latest_year)
              AND c.cbsa_code = ?
            """,
            [str(market_id)],
        ).fetchdf()
    finally:
        con.close()

    weight_rows = weight_table[["tract_geoid", "ring_mi", "weight"]].copy()
    cumulative: list[dict[str, Any]] = []
    for ring_mi in sorted(ring_order):
        rows = (
            weight_rows.loc[weight_rows["ring_mi"] <= ring_mi]
            .groupby("tract_geoid", as_index=False)["weight"]
            .sum()
            .rename(columns={"weight": "cumulative_weight"})
        )
        rows["ring_mi"] = int(ring_mi)
        cumulative.append(rows)
    weights = pd.concat(cumulative, ignore_index=True) if cumulative else pd.DataFrame(columns=["tract_geoid", "cumulative_weight", "ring_mi"])
    merged = weights.merge(pop_rows, on="tract_geoid", how="left")
    geometry = merged["geom_wkb"].apply(lambda value: wkb.loads(bytes(value)) if value is not None else None)
    return gpd.GeoDataFrame(merged.drop(columns=["geom_wkb"]), geometry=geometry, crs="EPSG:4326").dropna(subset=["geometry"])


def _compute_severed_population_share(ring_mi: int, far_side_geom, ring_population: gpd.GeoDataFrame) -> float | None:
    """Estimate the share of cumulative ring population that falls on the far side of a barrier."""

    if far_side_geom is None or ring_population.empty:
        return None
    rows = ring_population.loc[ring_population["ring_mi"] == ring_mi].copy()
    if rows.empty:
        return None
    weighted_pop = rows["pop_total"] * rows["cumulative_weight"]
    total_pop = float(weighted_pop.sum())
    if total_pop <= 0:
        return None
    projected = rows.to_crs("EPSG:3857")
    far_side = gpd.GeoSeries([far_side_geom], crs=projected.crs).iloc[0]
    tract_areas = projected.geometry.area.replace(0, np.nan)
    overlap_area = projected.geometry.intersection(far_side).area
    overlap_share = (overlap_area / tract_areas).fillna(0.0).clip(lower=0.0, upper=1.0)
    severed_pop = float((weighted_pop.reset_index(drop=True) * overlap_share.reset_index(drop=True)).sum())
    return severed_pop / total_pop


def _build_barrier_summary(barrier_type: str, feature_name: str, crossing_count: int, spacing_mi: float | None) -> str:
    """Write one short barrier summary line for the D3 appendix and site card."""

    if crossing_count == 0:
        crossing_text = "no detected crossings"
    elif spacing_mi is None or spacing_mi == float("inf"):
        crossing_text = f"{crossing_count} crossing" if crossing_count == 1 else f"{crossing_count} crossings"
    else:
        crossing_text = f"{crossing_count} crossings, mean spacing {spacing_mi:.2f} mi"
    feature_label = feature_name if feature_name and feature_name != "nan" else barrier_type.title()
    return f"{feature_label} ({barrier_type}) — {crossing_text}"


def _build_typology_input(daytime: pd.DataFrame, poi_counts: pd.DataFrame, road_context: dict[str, Any]) -> dict[str, Any]:
    """Collapse D3 metrics into the heuristic inputs used by the v0 node typology."""

    primary_daytime = daytime.loc[daytime["ring_mi"] == daytime["ring_mi"].min()].iloc[0] if not daytime.empty else {}
    poi_by_class = poi_counts.groupby("poi_class")["count"].sum().to_dict() if not poi_counts.empty else {}
    dominant_sector_id = "mixed"
    if isinstance(primary_daytime, pd.Series):
        breakout = {
            "retail": float(primary_daytime.get("jobs_retail", 0.0) or 0.0),
            "arts_accomm_food": float(primary_daytime.get("jobs_accommodation_food", 0.0) or 0.0),
            "educ_health": float(primary_daytime.get("jobs_health_care", 0.0) or 0.0),
            "professional": float(primary_daytime.get("jobs_professional_scientific", 0.0) or 0.0),
        }
        dominant_sector_id = max(breakout, key=breakout.get) if breakout else "mixed"
    return {
        "highways_present": road_context.get("highways_present", False),
        "rail_present": road_context.get("rail_present", False),
        "airports_present": False,
        "ports_present": False,
        "warehouses_logistics_count": int(poi_by_class.get("anchor", 0)),
        "hospitals_count": int(poi_by_class.get("anchor", 0)),
        "universities_count": 0,
        "schools_count": 0,
        "dominant_sector_id": dominant_sector_id,
    }


def _read_site_yaml(path: str) -> dict[str, Any]:
    """Read the site payload from disk and ensure we are validating a mapping."""

    file_path = Path(path)
    payload = yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"Site config at {file_path} must be a YAML mapping.")
    return payload


def _assert_required_fields(payload: dict[str, Any], required_fields: list[str]) -> None:
    """Fail early with the missing field name so bad configs are easy to fix."""

    missing_fields = [field for field in required_fields if field not in payload]
    if missing_fields:
        missing_field = missing_fields[0]
        raise ValueError(f"Missing required field: {missing_field}")


def _parse_required_string(value: Any, field_name: str) -> str:
    """Require a non-empty string for human-authored identifier fields."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Field '{field_name}' must be a non-empty string.")
    return value.strip()


def _parse_optional_float(value: Any, field_name: str) -> float | None:
    """Allow blank coordinates now so Milestone 1 can populate them later."""

    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise ValueError(f"Field '{field_name}' must be a float or blank.")
    if isinstance(value, (int, float)):
        return float(value)
    raise ValueError(f"Field '{field_name}' must be a float or blank.")


def _parse_asset_type(value: Any) -> str:
    """Validate the v0 asset-type enum so render paths can branch safely later."""

    asset_type = _parse_required_string(value, "asset_type")
    if asset_type not in VALID_ASSET_TYPES:
        allowed = ", ".join(sorted(VALID_ASSET_TYPES))
        raise ValueError(f"Field 'asset_type' must be one of: {allowed}.")
    return asset_type


def _parse_rings(value: Any) -> list[int]:
    """Normalize ring distances to positive integer miles in authored order."""

    if not isinstance(value, list) or not value:
        raise ValueError("Field 'rings_mi' must be a non-empty list of positive integers.")
    rings: list[int] = []
    for ring in value:
        if isinstance(ring, bool) or not isinstance(ring, int) or ring <= 0:
            raise ValueError("Field 'rings_mi' must be a non-empty list of positive integers.")
        rings.append(ring)
    return rings


def _parse_primary_ring(value: Any, rings_mi: list[int]) -> int:
    """Keep the primary ring aligned with the configured gradient distances."""

    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError("Field 'primary_ring_mi' must be a positive integer.")
    if value not in rings_mi:
        raise ValueError("Field 'primary_ring_mi' must be one of the configured ring distances.")
    return value
