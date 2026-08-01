"""Site configuration loading and D2 prep helpers for Place Intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
import json
from pathlib import Path
import sys
from typing import Any, Literal
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import duckdb
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import LinearRing, MultiPolygon, Point, Polygon, shape
from shapely import wkb
from shapely.ops import linemerge, split, unary_union
import yaml


VALID_ASSET_TYPES = {"retail", "residential", "mixed"}
DEFAULT_RINGS_MI = [1, 3, 5]
DEFAULT_PRIMARY_RING_MI = 3
DEFAULT_SITE_CONFIG_PATH = Path(__file__).resolve().parent / "site_jacksonville_v0.yaml"
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
D5_NFHL_MAPSERVER_URL = "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer"
D5_NFHL_ZONE_LAYER_ID = 28
D5_NFHL_PANEL_LAYER_ID = 3
D5_NFHL_BATCH_SIZE = 200
D5_NFHL_TIMEOUT_SECONDS = 8
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
D5_NRI_HAZARD_LABELS = {
    "avalanche_risk_score": "Avalanche",
    "coastal_flooding_risk_score": "Coastal flooding",
    "cold_wave_risk_score": "Cold wave",
    "drought_risk_score": "Drought",
    "earthquake_risk_score": "Earthquake",
    "hail_risk_score": "Hail",
    "heat_wave_risk_score": "Heat wave",
    "hurricane_risk_score": "Hurricane",
    "ice_storm_risk_score": "Ice storm",
    "inland_flooding_risk_score": "Inland flooding",
    "landslide_risk_score": "Landslide",
    "lightning_risk_score": "Lightning",
    "strong_wind_risk_score": "Strong wind",
    "tornado_risk_score": "Tornado",
    "tsunami_risk_score": "Tsunami",
    "volcanic_activity_risk_score": "Volcanic activity",
    "wildfire_risk_score": "Wildfire",
    "winter_weather_risk_score": "Winter weather",
}
D5_NRI_CORE_COLUMNS = [
    "risk_score",
    "eal_score",
    "social_vulnerability_score",
    "community_resilience_score",
    "coastal_flooding_risk_score",
    "inland_flooding_risk_score",
    "hurricane_risk_score",
]
D6_TRACT_FILL_METRICS = {
    "pop_total": "Population",
    "median_hh_income": "Median household income",
    "median_home_value": "Median home value",
    "pct_ba_plus": "BA+ share",
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


@dataclass(frozen=True)
class ResolvedSite:
    """Site config plus the resolved coordinates and tract used for D6 rendering."""

    site: Site
    lat: float
    lon: float
    tract_geoid: str
    matched_address: str
    match_type: str
    geocode_source: str


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


def list_site_configs() -> list[Path]:
    """Discover site YAML files so the D6 app can stay config-driven."""

    return sorted(SECTION_ROOT.glob("site*.yaml"))


def get_default_site_config_path() -> Path:
    """Return the default spotlight site config path for the D6 app shell."""

    return DEFAULT_SITE_CONFIG_PATH


def resolve_site(site: Site) -> ResolvedSite:
    """Resolve one site to stable coordinates and tract provenance for downstream prep."""

    from geocode import resolve_site_geocode

    geocode_result = resolve_site_geocode(site)
    return ResolvedSite(
        site=site,
        lat=float(geocode_result.lat),
        lon=float(geocode_result.lon),
        tract_geoid=str(geocode_result.tract_geoid),
        matched_address=str(geocode_result.matched_address),
        match_type=str(geocode_result.match_type),
        geocode_source=str(geocode_result.geocode_source),
    )


def build_site_weight_table(site: Site) -> pd.DataFrame:
    """Compute the D1 tract weight table for one configured site."""

    from apportion import apportion_weights, build_rings

    resolved_site = resolve_site(site)
    rings = build_rings(lat=resolved_site.lat, lon=resolved_site.lon, rings_mi=site.rings_mi).copy()
    rings["site_id"] = site.site_id
    weights = apportion_weights(rings, market_id=site.market_id)
    if weights.empty:
        return weights
    weights["site_id"] = site.site_id
    return weights


def build_site_base_payload(site: Site) -> dict[str, Any]:
    """Build the shared D1 foundation the D6 tabs all sit on top of."""

    from apportion import coverage_diagnostic

    resolved_site = resolve_site(site)
    weight_table = build_site_weight_table(site)
    coverage = coverage_diagnostic(weight_table)
    cumulative_rings = _build_cumulative_rings(resolved_site.lat, resolved_site.lon, site.rings_mi)
    return {
        "site": site,
        "resolved_site": resolved_site,
        "weight_table": weight_table,
        "coverage_diagnostic": coverage,
        "cumulative_rings": cumulative_rings,
    }


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
        benchmark_rows.extend(
            _build_metric_benchmark_rows(
                site,
                metric,
                metric_surface,
                county_geoid=county_geoid,
                state_fips=state_fips,
            )
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
    """Assemble D2 as one canonical long table plus app-facing aggregated views."""

    metric_long_rows: list[dict[str, Any]] = []
    skip_reasons: list[MetricSkipReason] = []
    county_geoid, state_fips = _get_site_county_and_state(site)
    for metric in METRIC_DEFINITIONS:
        metric_surface = _query_metric_surface(metric, site.market_id)
        metric_rows = _build_metric_catchment_rows(
            site,
            weight_table,
            metric,
            metric_surface=metric_surface,
        )
        if metric_rows.empty:
            skip_reasons.append(
                MetricSkipReason(
                    metric=metric.metric_id,
                    reason="No tract-grain values available for the configured market/rings.",
                    table_name=metric.table_name,
                )
            )
            continue

        for row in metric_rows.to_dict("records"):
            metric_long_rows.append(
                {
                    "site_id": row["site_id"],
                    "market_id": site.market_id,
                    "record_type": "catchment",
                    "metric": row["metric"],
                    "metric_label": row["metric_label"],
                    "topic": row["topic"],
                    "ring_mi": row["ring_mi"],
                    "benchmark_level": None,
                    "benchmark_geo_id": None,
                    "benchmark_geo_name": None,
                    "value": row["value"],
                    "year": row["year"],
                    "source_table": row["source_table"],
                    "change_5yr": row["change_5yr"],
                    "change_5yr_period": row["change_5yr_period"],
                    "cbsa_percentile": row["cbsa_percentile"],
                    "cbsa_percentile_denominator": row["cbsa_percentile_denominator"],
                }
            )

        for row in _build_metric_benchmark_rows(
            site,
            metric,
            metric_surface,
            county_geoid=county_geoid,
            state_fips=state_fips,
        ):
            metric_long_rows.append(
                {
                    "site_id": row["site_id"],
                    "market_id": site.market_id,
                    "record_type": "benchmark",
                    "metric": row["metric"],
                    "metric_label": row["metric_label"],
                    "topic": row["topic"],
                    "ring_mi": row["ring_mi"],
                    "benchmark_level": row["benchmark_level"],
                    "benchmark_geo_id": row["benchmark_geo_id"],
                    "benchmark_geo_name": row["benchmark_geo_name"],
                    "value": row["value"],
                    "year": row["year"],
                    "source_table": row["source_table"],
                    "change_5yr": None,
                    "change_5yr_period": None,
                    "cbsa_percentile": None,
                    "cbsa_percentile_denominator": None,
                }
            )

    metric_long = pd.DataFrame(metric_long_rows).sort_values(
        ["metric", "record_type", "ring_mi", "benchmark_level"],
        kind="mergesort",
        na_position="last",
    ).reset_index(drop=True) if metric_long_rows else _empty_d2_metric_long()
    catchment_profile = (
        metric_long.loc[metric_long["record_type"] == "catchment"]
        .drop(columns=["record_type", "market_id"])
        .reset_index(drop=True)
        if not metric_long.empty
        else pd.DataFrame()
    )
    benchmark_table = (
        metric_long.loc[metric_long["record_type"] == "benchmark"]
        .drop(
            columns=[
                "record_type",
                "market_id",
                "change_5yr",
                "change_5yr_period",
                "cbsa_percentile",
                "cbsa_percentile_denominator",
            ]
        )
        .reset_index(drop=True)
        if not metric_long.empty
        else _empty_benchmark_table()
    )

    return {
        "metric_long": metric_long,
        "metric_summary": _build_d2_metric_summary(metric_long, site),
        "catchment_profile": catchment_profile,
        "benchmark_table": benchmark_table,
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


def get_d5_flood_payload(
    site: Site,
    weight_table: pd.DataFrame,
    cumulative_rings: gpd.GeoDataFrame | None = None,
) -> dict[str, Any]:
    """Build the D5 flood payload from tract NRI and live FEMA NFHL lookups."""

    lat, lon = _resolve_site_coordinates(site)
    rings = cumulative_rings if cumulative_rings is not None else _build_cumulative_rings(lat, lon, site.rings_mi)
    nri_payload = build_nri_flood_risk_payload(site, weight_table)

    nfhl_status = "ok"
    nfhl_error = None
    try:
        site_zone = lookup_nfhl_site_flood_zone(site)
        ring_shares = build_nfhl_ring_share_table(site, rings)
    except Exception as exc:
        nfhl_status = "unavailable"
        nfhl_error = str(exc)
        site_zone = _empty_nfhl_site_lookup(site)
        ring_shares = _empty_nfhl_ring_share_table(site)

    return {
        "site_id": site.site_id,
        "nri_catchment_scores": nri_payload["catchment_scores"],
        "nri_catchment_top_hazards": nri_payload["catchment_top_hazards"],
        "nri_cbsa_benchmark": nri_payload["cbsa_benchmark"],
        "nri_cbsa_top_hazards": nri_payload["cbsa_top_hazards"],
        "nfhl_site_zone": site_zone,
        "nfhl_ring_shares": ring_shares,
        "nfhl_service_status": nfhl_status,
        "nfhl_service_error": nfhl_error,
        "copy_note": (
            "NFHL answers the parcel-level map question: which FEMA flood zone the site sits in today. "
            "NRI answers the broader catchment-risk question by summarizing modeled hazard scores across nearby tracts. "
            "This is a screening-level read from published FEMA mapping, not a flood determination, elevation certificate, or insurance rating."
        ),
    }


def build_nri_flood_risk_payload(site: Site, weight_table: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Apportion tract-grain FEMA NRI rows into cumulative rings and pair them with the CBSA row."""

    catchment_score_columns = [
        "site_id",
        "ring_mi",
        "year",
        "risk_score",
        "eal_score",
        "social_vulnerability_score",
        "community_resilience_score",
        "coastal_flooding_risk_score",
        "inland_flooding_risk_score",
        "hurricane_risk_score",
    ]
    if weight_table.empty:
        return {
            "catchment_scores": pd.DataFrame(columns=catchment_score_columns),
            "catchment_top_hazards": _empty_nri_top_hazards(),
            "cbsa_benchmark": pd.DataFrame(columns=["site_id", "market_id", "geo_name", "year", *D5_NRI_CORE_COLUMNS]),
            "cbsa_top_hazards": _empty_nri_top_hazards(),
        }

    nri = _query_nri_surface(site.market_id)
    tract_rows = nri.loc[nri["geo_level"] == "tract"].copy()
    cbsa_rows = nri.loc[(nri["geo_level"] == "cbsa") & (nri["geo_id"] == str(site.market_id))].copy()
    if tract_rows.empty:
        return {
            "catchment_scores": pd.DataFrame(columns=catchment_score_columns),
            "catchment_top_hazards": _empty_nri_top_hazards(),
            "cbsa_benchmark": pd.DataFrame(columns=["site_id", "market_id", "geo_name", "year", *D5_NRI_CORE_COLUMNS]),
            "cbsa_top_hazards": _empty_nri_top_hazards(),
        }

    cumulative_weights = _build_cumulative_weight_table(weight_table, site.rings_mi)
    hazard_columns = [column for column in D5_NRI_HAZARD_LABELS if column in tract_rows.columns]
    metric_columns = [column for column in D5_NRI_CORE_COLUMNS if column in tract_rows.columns]

    metric_results: dict[str, pd.Series] = {}
    for column in [*metric_columns, *hazard_columns]:
        metric_values = tract_rows[["geo_id", column]].dropna()
        if metric_values.empty:
            continue
        metric_results[column] = _apportion_metric_series(
            column,
            "intensive",
            metric_values.set_index("geo_id")[column],
            cumulative_weights,
        )

    catchment_rows: list[dict[str, Any]] = []
    catchment_top_hazards: list[dict[str, Any]] = []
    catchment_year = int(tract_rows["year"].max())
    for ring_mi in sorted(site.rings_mi):
        row = {
            "site_id": site.site_id,
            "ring_mi": int(ring_mi),
            "year": catchment_year,
        }
        for column in metric_columns:
            result = metric_results.get(column)
            row[column] = float(result.loc[ring_mi]) if result is not None and ring_mi in result.index else None
        catchment_rows.append(row)

        top_scores = {
            column: float(result.loc[ring_mi])
            for column, result in metric_results.items()
            if column in hazard_columns and ring_mi in result.index and pd.notna(result.loc[ring_mi])
        }
        for rank, (hazard_id, score) in enumerate(
            sorted(top_scores.items(), key=lambda item: item[1], reverse=True)[:3],
            start=1,
        ):
            catchment_top_hazards.append(
                {
                    "site_id": site.site_id,
                    "geography": f"{ring_mi}-mile ring",
                    "ring_mi": int(ring_mi),
                    "rank": rank,
                    "hazard_id": hazard_id,
                    "hazard_label": D5_NRI_HAZARD_LABELS.get(hazard_id, hazard_id),
                    "risk_score": score,
                }
            )

    cbsa_benchmark = pd.DataFrame(columns=["site_id", "market_id", "geo_name", "year", *D5_NRI_CORE_COLUMNS])
    cbsa_top_hazards = _empty_nri_top_hazards()
    if not cbsa_rows.empty:
        cbsa_row = cbsa_rows.sort_values("year", ascending=False, kind="mergesort").iloc[0]
        benchmark_row = {
            "site_id": site.site_id,
            "market_id": str(site.market_id),
            "geo_name": cbsa_row.get("geo_name"),
            "year": int(cbsa_row["year"]),
        }
        for column in metric_columns:
            benchmark_row[column] = float(cbsa_row[column]) if pd.notna(cbsa_row[column]) else None
        cbsa_benchmark = pd.DataFrame([benchmark_row])

        cbsa_scores = {
            column: float(cbsa_row[column])
            for column in hazard_columns
            if pd.notna(cbsa_row.get(column))
        }
        cbsa_top_hazards = pd.DataFrame(
            [
                {
                    "site_id": site.site_id,
                    "geography": str(cbsa_row.get("geo_name") or site.market_id),
                    "ring_mi": None,
                    "rank": rank,
                    "hazard_id": hazard_id,
                    "hazard_label": D5_NRI_HAZARD_LABELS.get(hazard_id, hazard_id),
                    "risk_score": score,
                }
                for rank, (hazard_id, score) in enumerate(
                    sorted(cbsa_scores.items(), key=lambda item: item[1], reverse=True)[:3],
                    start=1,
                )
            ]
        )

    return {
        "catchment_scores": pd.DataFrame(catchment_rows),
        "catchment_top_hazards": pd.DataFrame(catchment_top_hazards) if catchment_top_hazards else _empty_nri_top_hazards(),
        "cbsa_benchmark": cbsa_benchmark,
        "cbsa_top_hazards": cbsa_top_hazards,
    }


def lookup_nfhl_site_flood_zone(site: Site) -> pd.DataFrame:
    """Look up the site's FEMA flood zone and matching FIRM panel metadata."""

    lat, lon = _resolve_site_coordinates(site)
    zone_features = _query_nfhl_features(
        layer_id=D5_NFHL_ZONE_LAYER_ID,
        geometry_text=f"{lon},{lat}",
        geometry_type="esriGeometryPoint",
        out_fields=["FLD_ZONE", "ZONE_SUBTY", "SFHA_TF", "STATIC_BFE", "DEPTH", "SOURCE_CIT"],
        return_geometry=False,
    )
    panel_features = _query_nfhl_features(
        layer_id=D5_NFHL_PANEL_LAYER_ID,
        geometry_text=f"{lon},{lat}",
        geometry_type="esriGeometryPoint",
        out_fields=["FIRM_PAN", "EFF_DATE", "PANEL", "SUFFIX", "DFIRM_ID"],
        return_geometry=False,
    )

    zone_attributes = (zone_features[0].get("attributes") or {}) if zone_features else {}
    panel_attributes = (panel_features[0].get("attributes") or {}) if panel_features else {}
    zone_code = zone_attributes.get("FLD_ZONE")
    zone_subtype = zone_attributes.get("ZONE_SUBTY")
    sfha_value = zone_attributes.get("SFHA_TF")

    return pd.DataFrame(
        [
            {
                "site_id": site.site_id,
                "flood_zone": None if zone_code in (None, "") else str(zone_code),
                "zone_subtype": None if zone_subtype in (None, "") else str(zone_subtype),
                "sfha_flag": True if sfha_value == "T" else False if sfha_value == "F" else None,
                "static_bfe": _normalize_fema_numeric(zone_attributes.get("STATIC_BFE")),
                "depth": _normalize_fema_numeric(zone_attributes.get("DEPTH")),
                "source_citation": zone_attributes.get("SOURCE_CIT"),
                "firm_panel": panel_attributes.get("FIRM_PAN"),
                "panel_effective_date": _format_arcgis_epoch_ms(panel_attributes.get("EFF_DATE")),
                "panel_number": panel_attributes.get("PANEL"),
                "panel_suffix": panel_attributes.get("SUFFIX"),
                "dfirm_id": panel_attributes.get("DFIRM_ID"),
            }
        ]
    )


def build_nfhl_ring_share_table(
    site: Site,
    cumulative_rings: gpd.GeoDataFrame,
    zone_features: gpd.GeoDataFrame | None = None,
) -> pd.DataFrame:
    """Compute projected ring-area shares by FEMA flood zone from NFHL polygons."""

    zones = zone_features if zone_features is not None else _load_nfhl_zone_geometries(cumulative_rings)
    if zones.empty:
        return _empty_nfhl_ring_share_table(site)

    projected_zones = zones.to_crs(cumulative_rings.crs)
    rows: list[dict[str, Any]] = []
    for ring in cumulative_rings.itertuples(index=False):
        ring_area_sqmi = float(ring.geometry.area / 2_589_988.110336)
        ring_features = projected_zones.loc[projected_zones.geometry.intersects(ring.geometry)].copy()
        if ring_features.empty:
            continue

        ring_features["intersection_area_sqmi"] = (
            ring_features.geometry.intersection(ring.geometry).area / 2_589_988.110336
        )
        ring_features = ring_features.loc[ring_features["intersection_area_sqmi"] > 0].copy()
        if ring_features.empty:
            continue

        grouped = (
            ring_features.groupby(["flood_zone", "zone_subtype", "sfha_flag"], dropna=False)["intersection_area_sqmi"]
            .sum()
            .reset_index()
        )
        grouped["ring_mi"] = int(ring.ring_mi)
        grouped["ring_area_sqmi"] = ring_area_sqmi
        grouped["area_share"] = grouped["intersection_area_sqmi"] / ring_area_sqmi if ring_area_sqmi else np.nan
        grouped["site_id"] = site.site_id
        rows.extend(grouped.to_dict("records"))

    if not rows:
        return _empty_nfhl_ring_share_table(site)
    return pd.DataFrame(rows)[
        [
            "site_id",
            "ring_mi",
            "flood_zone",
            "zone_subtype",
            "sfha_flag",
            "intersection_area_sqmi",
            "ring_area_sqmi",
            "area_share",
        ]
    ].sort_values(["ring_mi", "flood_zone", "zone_subtype"], kind="mergesort").reset_index(drop=True)


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
    metric_surface: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Aggregate one metric into ring rows and wire in vintages, percentiles, and change."""

    metric_surface = (
        metric_surface.copy()
        if metric_surface is not None
        else _query_metric_surface(metric, site.market_id)
    )
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


def _build_metric_benchmark_rows(
    site: Site,
    metric: MetricDefinition,
    metric_surface: pd.DataFrame,
    county_geoid: str,
    state_fips: str,
) -> list[dict[str, Any]]:
    """Project one metric's current benchmark rows from an already-loaded surface."""

    benchmark_frame = metric_surface.loc[
        metric_surface["geo_level_normalized"].isin({"cbsa", "county", "state", "us"})
    ].copy()
    if benchmark_frame.empty:
        return []

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
        return []

    rows: list[dict[str, Any]] = []
    for row in selected.itertuples(index=False):
        rows.append(
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
    return rows


def _build_d2_metric_summary(metric_long: pd.DataFrame, site: Site) -> pd.DataFrame:
    """Aggregate the canonical D2 long table into one app-friendly row per metric."""

    if metric_long.empty:
        return _empty_d2_metric_summary(site)

    catchment = metric_long.loc[metric_long["record_type"] == "catchment"].copy()
    if catchment.empty:
        return _empty_d2_metric_summary(site)
    benchmarks = metric_long.loc[metric_long["record_type"] == "benchmark"].copy()

    rows: list[dict[str, Any]] = []
    ring_values = sorted(int(ring) for ring in site.rings_mi)
    for metric, metric_rows in catchment.groupby("metric", sort=False):
        metric_rows = metric_rows.sort_values("ring_mi", kind="mergesort").copy()
        first_row = metric_rows.iloc[0]
        primary_row = metric_rows.loc[metric_rows["ring_mi"] == int(site.primary_ring_mi)].head(1)
        benchmark_rows = benchmarks.loc[benchmarks["metric"] == metric].copy()

        row: dict[str, Any] = {
            "site_id": site.site_id,
            "market_id": site.market_id,
            "metric": metric,
            "metric_label": first_row["metric_label"],
            "topic": first_row["topic"],
            "source_table": first_row["source_table"],
            "primary_ring_mi": int(site.primary_ring_mi),
        }

        for ring_mi in ring_values:
            ring_row = metric_rows.loc[metric_rows["ring_mi"] == int(ring_mi)].head(1)
            row[f"ring_{ring_mi}_value"] = None if ring_row.empty else float(ring_row["value"].iloc[0])
            row[f"ring_{ring_mi}_year"] = None if ring_row.empty else int(ring_row["year"].iloc[0])
            row[f"ring_{ring_mi}_change_5yr"] = None if ring_row.empty or pd.isna(ring_row["change_5yr"].iloc[0]) else float(ring_row["change_5yr"].iloc[0])
            row[f"ring_{ring_mi}_change_5yr_period"] = None if ring_row.empty else ring_row["change_5yr_period"].iloc[0]

        if primary_row.empty:
            row["primary_value"] = None
            row["primary_year"] = None
            row["primary_change_5yr"] = None
            row["primary_change_5yr_period"] = None
            row["primary_cbsa_percentile"] = None
            row["primary_cbsa_percentile_denominator"] = None
        else:
            row["primary_value"] = float(primary_row["value"].iloc[0])
            row["primary_year"] = int(primary_row["year"].iloc[0])
            row["primary_change_5yr"] = None if pd.isna(primary_row["change_5yr"].iloc[0]) else float(primary_row["change_5yr"].iloc[0])
            row["primary_change_5yr_period"] = primary_row["change_5yr_period"].iloc[0]
            row["primary_cbsa_percentile"] = None if pd.isna(primary_row["cbsa_percentile"].iloc[0]) else float(primary_row["cbsa_percentile"].iloc[0])
            row["primary_cbsa_percentile_denominator"] = None if pd.isna(primary_row["cbsa_percentile_denominator"].iloc[0]) else int(primary_row["cbsa_percentile_denominator"].iloc[0])

        for benchmark_level in ["cbsa", "county", "state", "national"]:
            benchmark_row = benchmark_rows.loc[benchmark_rows["benchmark_level"] == benchmark_level].head(1)
            row[f"benchmark_{benchmark_level}_value"] = None if benchmark_row.empty else float(benchmark_row["value"].iloc[0])
            row[f"benchmark_{benchmark_level}_year"] = None if benchmark_row.empty else int(benchmark_row["year"].iloc[0])
            row[f"benchmark_{benchmark_level}_geo_name"] = None if benchmark_row.empty else benchmark_row["benchmark_geo_name"].iloc[0]

        rows.append(row)

    return pd.DataFrame(rows).sort_values(["topic", "metric_label"], kind="mergesort").reset_index(drop=True)


def _empty_d2_metric_long() -> pd.DataFrame:
    """Return the canonical empty D2 long-record frame."""

    return pd.DataFrame(
        columns=[
            "site_id",
            "market_id",
            "record_type",
            "metric",
            "metric_label",
            "topic",
            "ring_mi",
            "benchmark_level",
            "benchmark_geo_id",
            "benchmark_geo_name",
            "value",
            "year",
            "source_table",
            "change_5yr",
            "change_5yr_period",
            "cbsa_percentile",
            "cbsa_percentile_denominator",
        ]
    )


def _empty_benchmark_table() -> pd.DataFrame:
    """Return the legacy empty D2 benchmark table shape."""

    return pd.DataFrame(
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


def _empty_d2_metric_summary(site: Site) -> pd.DataFrame:
    """Return the app-facing empty D2 summary shape."""

    columns = [
        "site_id",
        "market_id",
        "metric",
        "metric_label",
        "topic",
        "source_table",
        "primary_ring_mi",
        "primary_value",
        "primary_year",
        "primary_change_5yr",
        "primary_change_5yr_period",
        "primary_cbsa_percentile",
        "primary_cbsa_percentile_denominator",
        "benchmark_cbsa_value",
        "benchmark_cbsa_year",
        "benchmark_cbsa_geo_name",
        "benchmark_county_value",
        "benchmark_county_year",
        "benchmark_county_geo_name",
        "benchmark_state_value",
        "benchmark_state_year",
        "benchmark_state_geo_name",
        "benchmark_national_value",
        "benchmark_national_year",
        "benchmark_national_geo_name",
    ]
    for ring_mi in sorted(int(ring) for ring in site.rings_mi):
        columns.extend(
            [
                f"ring_{ring_mi}_value",
                f"ring_{ring_mi}_year",
                f"ring_{ring_mi}_change_5yr",
                f"ring_{ring_mi}_change_5yr_period",
            ]
        )
    return pd.DataFrame(columns=columns)


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
def _query_gold_table_surface(table_name: str, market_id: str) -> pd.DataFrame:
    """Read one Gold table once for a market so multiple metrics can share the same surface."""

    metric_columns = _metric_value_columns_for_table(table_name)
    select_metric_columns = ",\n                ".join(f"t.{column}" for column in metric_columns)
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
                {select_metric_columns}
            FROM patterns_in_place.gold.{table_name} t
            LEFT JOIN patterns_in_place.geo.tracts_all_us g
                ON t.geo_level = 'tract'
               AND t.geo_id = g.tract_geoid
            WHERE (
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


def _metric_value_columns_for_table(table_name: str) -> list[str]:
    """Return the D2 metric columns needed from one Gold table."""

    columns = sorted(
        {
            metric.value_column
            for metric in METRIC_DEFINITIONS
            if metric.table_name == table_name
        }
    )
    if not columns:
        raise ValueError(f"No D2 metric columns registered for table '{table_name}'.")
    return columns


def _query_metric_surface(metric: MetricDefinition, market_id: str) -> pd.DataFrame:
    """Project one metric's value column out of a shared cached Gold table surface."""

    table_rows = _query_gold_table_surface(metric.table_name, market_id)
    if metric.value_column not in table_rows.columns:
        return pd.DataFrame(
            columns=[
                "geo_level_normalized",
                "geo_level",
                "geo_id",
                "geo_name",
                "year",
                "metric_value",
            ]
        )

    metric_rows = table_rows.loc[table_rows[metric.value_column].notna()].copy()
    if metric_rows.empty:
        return pd.DataFrame(
            columns=[
                "geo_level_normalized",
                "geo_level",
                "geo_id",
                "geo_name",
                "year",
                "metric_value",
            ]
        )

    return metric_rows[
        ["geo_level_normalized", "geo_level", "geo_id", "geo_name", "year", metric.value_column]
    ].rename(columns={metric.value_column: "metric_value"})


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


def _build_cumulative_weight_table(weight_table: pd.DataFrame, ring_order: list[int]) -> pd.DataFrame:
    """Roll band weights up into cumulative circles for D3/D5 catchment summaries."""

    if weight_table.empty:
        return weight_table.copy()

    rows: list[pd.DataFrame] = []
    for ring_mi in sorted(ring_order):
        cumulative = (
            weight_table.loc[weight_table["ring_mi"] <= ring_mi]
            .groupby("tract_geoid", as_index=False)["weight"]
            .sum()
        )
        cumulative["site_id"] = weight_table["site_id"].iloc[0]
        cumulative["ring_mi"] = int(ring_mi)
        cumulative["weight_method"] = "cumulative_areal"
        cumulative["intersect_area"] = np.nan
        cumulative["tract_area"] = np.nan
        cumulative["containment"] = "cumulative"
        cumulative["centroid_in"] = np.nan
        rows.append(
            cumulative[
                [
                    "site_id",
                    "ring_mi",
                    "tract_geoid",
                    "weight",
                    "weight_method",
                    "intersect_area",
                    "tract_area",
                    "containment",
                    "centroid_in",
                ]
            ]
        )
    return pd.concat(rows, ignore_index=True)


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


@lru_cache(maxsize=None)
def _query_nri_surface(market_id: str) -> pd.DataFrame:
    """Read tract + CBSA FEMA NRI rows for one market from the existing Silver table."""

    con = get_connection()
    try:
        rows = con.execute(
            """
            WITH market_counties AS (
                SELECT DISTINCT county_geoid
                FROM patterns_in_place.silver.xwalk_cbsa_county
                WHERE cbsa_code = ?
            ),
            latest_year AS (
                SELECT MAX(year) AS year
                FROM patterns_in_place.silver.fema_nri
            )
            SELECT
                n.*
            FROM patterns_in_place.silver.fema_nri n
            LEFT JOIN patterns_in_place.geo.tracts_all_us g
                ON n.geo_level = 'tract'
               AND n.geo_id = g.tract_geoid
            WHERE n.year = (SELECT year FROM latest_year)
              AND (
                    (n.geo_level = 'tract' AND g.county_geoid IN (SELECT county_geoid FROM market_counties))
                 OR (n.geo_level = 'cbsa' AND n.geo_id = ?)
              )
            ORDER BY n.geo_level, n.geo_id
            """,
            [str(market_id), str(market_id)],
        ).fetchdf()
    finally:
        con.close()
    return rows


def _request_arcgis_json(url: str, params: dict[str, Any]) -> dict[str, Any]:
    """Call one ArcGIS REST endpoint and parse the JSON payload defensively."""

    request = Request(
        f"{url}?{urlencode(params)}",
        headers={"Accept": "application/json", "User-Agent": "patterns-in-place-codex/1.0"},
        method="GET",
    )
    with urlopen(request, timeout=D5_NFHL_TIMEOUT_SECONDS) as response:  # noqa: S310 - fixed FEMA endpoint
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("FEMA NFHL service returned a non-object JSON payload.")
    if "error" in payload:
        message = payload["error"].get("message") if isinstance(payload["error"], dict) else str(payload["error"])
        raise ValueError(f"FEMA NFHL service returned an error: {message}")
    return payload


def _query_nfhl_features(
    layer_id: int,
    geometry_text: str,
    geometry_type: str,
    out_fields: list[str],
    return_geometry: bool,
) -> list[dict[str, Any]]:
    """Query one NFHL layer for the supplied geometry filter."""

    payload = _request_arcgis_json(
        f"{D5_NFHL_MAPSERVER_URL}/{layer_id}/query",
        {
            "f": "json",
            "where": "1=1",
            "geometry": geometry_text,
            "geometryType": geometry_type,
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "returnGeometry": "true" if return_geometry else "false",
            "outFields": ",".join(out_fields),
            "outSR": "4326",
        },
    )
    features = payload.get("features") or []
    if not isinstance(features, list):
        raise ValueError("FEMA NFHL service returned an invalid feature collection.")
    return features


def _load_nfhl_zone_geometries(cumulative_rings: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Fetch the live NFHL zone polygons that intersect the site's largest ring envelope."""

    bounds = cumulative_rings.to_crs("EPSG:4326").total_bounds
    geometry_text = ",".join(str(value) for value in bounds.tolist())
    ids_payload = _request_arcgis_json(
        f"{D5_NFHL_MAPSERVER_URL}/{D5_NFHL_ZONE_LAYER_ID}/query",
        {
            "f": "json",
            "where": "1=1",
            "geometry": geometry_text,
            "geometryType": "esriGeometryEnvelope",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "returnIdsOnly": "true",
        },
    )
    object_ids = ids_payload.get("objectIds") or []
    if not object_ids:
        return gpd.GeoDataFrame(columns=["flood_zone", "zone_subtype", "sfha_flag", "geometry"], geometry="geometry", crs="EPSG:4269")

    rows: list[dict[str, Any]] = []
    for idx in range(0, len(object_ids), D5_NFHL_BATCH_SIZE):
        batch_ids = object_ids[idx : idx + D5_NFHL_BATCH_SIZE]
        payload = _request_arcgis_json(
            f"{D5_NFHL_MAPSERVER_URL}/{D5_NFHL_ZONE_LAYER_ID}/query",
            {
                "f": "json",
                "objectIds": ",".join(str(value) for value in batch_ids),
                "returnGeometry": "true",
                "outFields": "FLD_ZONE,ZONE_SUBTY,SFHA_TF,SOURCE_CIT",
                "outSR": "4326",
            },
        )
        for feature in payload.get("features") or []:
            attributes = feature.get("attributes") or {}
            geometry = _arcgis_polygon_to_shape(feature.get("geometry"))
            if geometry is None or geometry.is_empty:
                continue
            rows.append(
                {
                    "flood_zone": attributes.get("FLD_ZONE"),
                    "zone_subtype": attributes.get("ZONE_SUBTY"),
                    "sfha_flag": True if attributes.get("SFHA_TF") == "T" else False if attributes.get("SFHA_TF") == "F" else None,
                    "source_citation": attributes.get("SOURCE_CIT"),
                    "geometry": geometry,
                }
            )

    return gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326").dropna(subset=["geometry"]) if rows else gpd.GeoDataFrame(
        columns=["flood_zone", "zone_subtype", "sfha_flag", "source_citation", "geometry"],
        geometry="geometry",
        crs="EPSG:4326",
    )


def _arcgis_polygon_to_shape(geometry: dict[str, Any] | None):
    """Convert ArcGIS polygon JSON into a shapely polygon or multipolygon."""

    if geometry is None:
        return None
    if "rings" not in geometry:
        geojson = _geometry_to_geojson(geometry)
        return shape(geojson) if geojson is not None else None

    polygons: list[Polygon] = []
    current_shell: list[tuple[float, float]] | None = None
    current_holes: list[list[tuple[float, float]]] = []
    for ring in geometry["rings"]:
        if not ring or len(ring) < 4:
            continue
        ring_coords = [(float(x), float(y)) for x, y in ring]
        linear_ring = LinearRing(ring_coords)
        if linear_ring.is_ccw:
            if current_shell is not None:
                current_holes.append(ring_coords)
        else:
            if current_shell is not None:
                polygons.append(Polygon(current_shell, current_holes))
            current_shell = ring_coords
            current_holes = []

    if current_shell is not None:
        polygons.append(Polygon(current_shell, current_holes))

    polygons = [polygon for polygon in polygons if not polygon.is_empty]
    if not polygons:
        return None
    if len(polygons) == 1:
        return polygons[0]
    return MultiPolygon(polygons)


def _geometry_to_geojson(geometry: dict[str, Any] | None) -> dict[str, Any] | None:
    """Normalize ArcGIS JSON geometry into a GeoJSON-like dict when possible."""

    if geometry is None:
        return None
    if "type" in geometry:
        return geometry
    if "paths" in geometry:
        if len(geometry["paths"]) == 1:
            return {"type": "LineString", "coordinates": geometry["paths"][0]}
        return {"type": "MultiLineString", "coordinates": geometry["paths"]}
    if "x" in geometry and "y" in geometry:
        return {"type": "Point", "coordinates": [geometry["x"], geometry["y"]]}
    return None


def _normalize_fema_numeric(value: Any) -> float | None:
    """Treat FEMA sentinel values as missing rather than reportable numbers."""

    if value is None or pd.isna(value):
        return None
    number = float(value)
    if number <= -9999:
        return None
    return number


def _format_arcgis_epoch_ms(value: Any) -> str | None:
    """Convert ArcGIS epoch-millis dates into ISO calendar dates."""

    if value is None or pd.isna(value):
        return None
    return datetime.fromtimestamp(float(value) / 1000.0, tz=timezone.utc).date().isoformat()


def _empty_nri_top_hazards() -> pd.DataFrame:
    """Return the stable empty-frame shape for NRI top-hazard outputs."""

    return pd.DataFrame(columns=["site_id", "geography", "ring_mi", "rank", "hazard_id", "hazard_label", "risk_score"])


def _empty_nfhl_site_lookup(site: Site) -> pd.DataFrame:
    """Return the stable empty-frame shape for NFHL site-point outputs."""

    return pd.DataFrame(
        [
            {
                "site_id": site.site_id,
                "flood_zone": None,
                "zone_subtype": None,
                "sfha_flag": None,
                "static_bfe": None,
                "depth": None,
                "source_citation": None,
                "firm_panel": None,
                "panel_effective_date": None,
                "panel_number": None,
                "panel_suffix": None,
                "dfirm_id": None,
            }
        ]
    )


def _empty_nfhl_ring_share_table(site: Site) -> pd.DataFrame:
    """Return the stable empty-frame shape for NFHL ring-share outputs."""

    return pd.DataFrame(
        columns=[
            "site_id",
            "ring_mi",
            "flood_zone",
            "zone_subtype",
            "sfha_flag",
            "intersection_area_sqmi",
            "ring_area_sqmi",
            "area_share",
        ]
    )


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


def build_context_map_payload(
    site: Site,
    weight_table: pd.DataFrame,
    fill_metric: str = "pop_total",
    include_flood_context: bool = True,
) -> dict[str, Any]:
    """Build the shared D6 context-map payload once per site/metric combination."""

    resolved_site = resolve_site(site)
    cumulative_rings = _build_cumulative_rings(resolved_site.lat, resolved_site.lon, site.rings_mi)
    d3_payload = get_d3_context_payload(site, weight_table)
    d5_payload = (
        get_d5_flood_payload(site, weight_table, cumulative_rings=cumulative_rings)
        if include_flood_context
        else {"nfhl_service_status": "skipped", "nfhl_service_error": None}
    )

    baseline_rings = d3_payload["ring_variants"]["baseline_rings"].to_crs("EPSG:4326")
    adjusted_rings = d3_payload["ring_variants"]["water_adjusted_rings"].to_crs("EPSG:4326")
    tract_fill = build_context_tract_fill(site, fill_metric)

    return {
        "site_point": [
            {
                "name": site.address,
                "lat": resolved_site.lat,
                "lon": resolved_site.lon,
                "match_type": resolved_site.match_type,
                "geocode_source": resolved_site.geocode_source,
            }
        ],
        "view_state": {
            "latitude": float(resolved_site.lat),
            "longitude": float(resolved_site.lon),
            "zoom": 10.5,
        },
        "available_fill_metrics": D6_TRACT_FILL_METRICS,
        "tract_fill": tract_fill,
        "rings_geojson": _frame_to_feature_collection(baseline_rings),
        "water_adjusted_rings_geojson": _frame_to_feature_collection(adjusted_rings),
        "severed_area_geojson": _build_severed_area_features(baseline_rings, adjusted_rings),
        "poi_rows": _build_context_poi_layer(site),
        "road_geojson": _build_context_road_layer(site),
        "flood_geojson": _build_context_flood_layer(cumulative_rings) if include_flood_context else {"type": "FeatureCollection", "features": []},
        "barrier_summary": d3_payload["barrier_summary"],
        "nfhl_service_status": d5_payload["nfhl_service_status"],
        "nfhl_service_error": d5_payload["nfhl_service_error"],
    }


def build_context_tract_fill(site: Site, metric: str) -> dict[str, Any]:
    """Build the tract-fill layer beneath the shared D6 context map."""

    metric_def = _get_metric_definition(metric)
    metric_surface = _query_metric_surface(metric_def, site.market_id)
    tract_rows = metric_surface.loc[metric_surface["geo_level_normalized"] == "tract"].copy()
    if tract_rows.empty:
        return {
            "features": [],
            "metric": metric,
            "metric_label": metric_def.label,
            "year": None,
            "source_table": metric_def.table_name,
        }

    latest_year = int(tract_rows["year"].max())
    latest_rows = tract_rows.loc[tract_rows["year"] == latest_year, ["geo_id", "geo_name", "metric_value"]].copy()
    tract_geoms = _query_market_tract_geometries(site.market_id)
    merged = tract_geoms.merge(latest_rows, left_on="tract_geoid", right_on="geo_id", how="left")
    colors = _compute_fill_colors(merged["metric_value"])
    features: list[dict[str, Any]] = []
    geojson = json.loads(merged.to_json())
    for idx, feature in enumerate(geojson.get("features", [])):
        props = feature.setdefault("properties", {})
        props["fill_color"] = colors[idx]
        props["metric_label"] = metric_def.label
        props["metric_value"] = None if pd.isna(props.get("metric_value")) else float(props["metric_value"])
        props["tract_name"] = str(props.get("geo_name") or props.get("tract_geoid"))
        features.append(feature)
    return {
        "features": features,
        "metric": metric,
        "metric_label": metric_def.label,
        "year": latest_year,
        "source_table": metric_def.table_name,
    }


def build_market_context_payload(site: Site) -> dict[str, Any]:
    """Build the compact D6 Market-tab payload from existing Gold surfaces."""

    return {
        "industry_context": _query_market_industry_context(site.market_id),
        "housing_context": _query_market_housing_context(site.market_id),
        "candidate_note": (
            "This Market tab is intentionally small and is a candidate for a reusable Metro Deep Dive summary "
            "component rather than Place Intelligence-only UI."
        ),
    }


def _build_context_poi_layer(site: Site) -> pd.DataFrame:
    """Prepare point rows for the shared context map POI layer."""

    pois = _load_overture_pois(site.market_id)
    if pois.empty:
        return pd.DataFrame(columns=["name", "poi_class", "lon", "lat"])
    pois = pois.copy()
    pois["poi_class"] = pois.apply(classify_poi, axis=1)
    pois = pois.loc[pois["poi_class"].notna()].copy()
    if pois.empty:
        return pd.DataFrame(columns=["name", "poi_class", "lon", "lat"])
    pois = pois.to_crs("EPSG:4326")
    output = pd.DataFrame(
        {
            "name": pois["name"] if "name" in pois.columns else None,
            "poi_class": pois["poi_class"],
            "lon": pois.geometry.x,
            "lat": pois.geometry.y,
        }
    )
    return output.dropna(subset=["lon", "lat"]).reset_index(drop=True)


def _build_context_road_layer(site: Site) -> dict[str, Any]:
    """Prefer D4 AADT segments for the shared map road layer when they exist."""

    segments = _load_fdot_aadt_segments(site.market_id)
    if not segments.empty:
        segments = segments.to_crs("EPSG:4326")
        geojson = json.loads(segments.to_json())
        for feature in geojson.get("features", []):
            props = feature.setdefault("properties", {})
            props["label"] = str(props.get("roadway") or props.get("source_id") or "AADT segment")
            props["aadt"] = None if props.get("aadt") is None else float(props["aadt"])
        return geojson

    lines = _load_osm_lines(site.market_id)
    if lines.empty:
        return {"type": "FeatureCollection", "features": []}
    subset = lines.loc[lines["layer_group"].isin({"highways", "major_roads", "rail"})].to_crs("EPSG:4326")
    geojson = json.loads(subset.to_json())
    for feature in geojson.get("features", []):
        props = feature.setdefault("properties", {})
        props["label"] = str(props.get("layer_group") or "road")
        props["aadt"] = None
    return geojson


def _build_context_flood_layer(cumulative_rings: gpd.GeoDataFrame) -> dict[str, Any]:
    """Load one optional NFHL polygon layer for the D6 map and degrade cleanly on failure."""

    try:
        zones = _load_nfhl_zone_geometries(cumulative_rings)
    except Exception:
        return {"type": "FeatureCollection", "features": []}
    if zones.empty:
        return {"type": "FeatureCollection", "features": []}
    return _frame_to_feature_collection(zones.to_crs("EPSG:4326"))


def _build_severed_area_features(
    baseline_rings: gpd.GeoDataFrame,
    adjusted_rings: gpd.GeoDataFrame,
) -> dict[str, Any]:
    """Turn water-adjusted ring differences into a single shading layer."""

    features: list[dict[str, Any]] = []
    adjusted_lookup = adjusted_rings.set_index("ring_mi")
    for ring in baseline_rings.itertuples(index=False):
        if int(ring.ring_mi) not in adjusted_lookup.index:
            continue
        removed_geom = ring.geometry.difference(adjusted_lookup.loc[int(ring.ring_mi), "geometry"])
        if removed_geom.is_empty:
            continue
        feature = json.loads(gpd.GeoSeries([removed_geom], crs=baseline_rings.crs).to_json())["features"][0]
        feature.setdefault("properties", {})["ring_mi"] = int(ring.ring_mi)
        features.append(feature)
    return {"type": "FeatureCollection", "features": features}


@lru_cache(maxsize=None)
def _query_market_tract_geometries(market_id: str) -> gpd.GeoDataFrame:
    """Read tract geometry once for the D6 context map tract-fill layer."""

    con = get_connection()
    try:
        con.execute("LOAD spatial;")
        rows = con.execute(
            """
            WITH market_counties AS (
                SELECT DISTINCT county_geoid
                FROM patterns_in_place.silver.xwalk_cbsa_county
                WHERE cbsa_code = ?
            )
            SELECT
                tract_geoid,
                county_name,
                ST_AsWKB(geom) AS geom_wkb
            FROM patterns_in_place.geo.tracts_all_us
            WHERE county_geoid IN (SELECT county_geoid FROM market_counties)
            ORDER BY tract_geoid
            """,
            [str(market_id)],
        ).fetchall()
    finally:
        con.close()
    return gpd.GeoDataFrame(
        [{"tract_geoid": str(tract_geoid), "county_name": str(county_name)} for tract_geoid, county_name, _ in rows],
        geometry=[wkb.loads(bytes(geom)) for _, _, geom in rows],
        crs="EPSG:4326",
    )


@lru_cache(maxsize=None)
def _query_market_industry_context(market_id: str) -> dict[str, pd.DataFrame]:
    """Pull the latest-year CBSA employment and GDP mix from Gold."""

    con = get_connection()
    try:
        employment = con.execute(
            """
            WITH latest_year AS (
                SELECT MAX(year) AS year
                FROM patterns_in_place.gold.economics_industry_wide
                WHERE geo_level = 'cbsa'
                  AND geo_id = ?
            )
            SELECT
                year,
                sector_id,
                sector_label,
                emp_share AS share_value,
                total_emp AS raw_value,
                source
            FROM patterns_in_place.gold.economics_industry_wide
            WHERE geo_level = 'cbsa'
              AND geo_id = ?
              AND year = (SELECT year FROM latest_year)
            ORDER BY emp_share DESC NULLS LAST
            """,
            [str(market_id), str(market_id)],
        ).fetchdf()
        gdp = con.execute(
            """
            WITH latest_year AS (
                SELECT MAX(year) AS year
                FROM patterns_in_place.gold.economics_industry_wide
                WHERE geo_level = 'cbsa'
                  AND geo_id = ?
            )
            SELECT
                year,
                sector_id,
                sector_label,
                gdp_share AS share_value,
                real_gdp AS raw_value,
                source
            FROM patterns_in_place.gold.economics_industry_wide
            WHERE geo_level = 'cbsa'
              AND geo_id = ?
              AND year = (SELECT year FROM latest_year)
            ORDER BY gdp_share DESC NULLS LAST
            """,
            [str(market_id), str(market_id)],
        ).fetchdf()
    finally:
        con.close()
    return {"employment_mix": employment, "gdp_mix": gdp}


@lru_cache(maxsize=None)
def _query_market_housing_context(market_id: str) -> pd.DataFrame:
    """Read a small CBSA housing-market trend series for the Market tab."""

    con = get_connection()
    try:
        return con.execute(
            """
            SELECT
                year,
                geo_name,
                zhvi_annual_avg,
                zori_annual_avg,
                hpi_yoy_pct,
                zori_annual_avg_yoy_pct
            FROM patterns_in_place.gold.housing_market_wide
            WHERE geo_level = 'cbsa'
              AND geo_id = ?
            ORDER BY year
            """,
            [str(market_id)],
        ).fetchdf()
    finally:
        con.close()


def _compute_fill_colors(values: pd.Series) -> list[list[int]]:
    """Translate one numeric surface into a stable sequential fill ramp."""

    numeric = pd.to_numeric(values, errors="coerce")
    valid = numeric.dropna()
    if valid.empty:
        return [[229, 231, 235, 120] for _ in range(len(values))]
    low = float(valid.min())
    high = float(valid.max())
    span = high - low if high != low else 1.0
    colors: list[list[int]] = []
    for value in numeric:
        if pd.isna(value):
            colors.append([229, 231, 235, 120])
            continue
        ratio = (float(value) - low) / span
        colors.append(
            [
                int(241 + ratio * (44 - 241)),
                int(245 + ratio * (123 - 245)),
                int(255 + ratio * (182 - 255)),
                165,
            ]
        )
    return colors


def _frame_to_feature_collection(frame: gpd.GeoDataFrame) -> dict[str, Any]:
    """Convert one GeoDataFrame into a pydeck-ready FeatureCollection."""

    return json.loads(frame.to_json()) if not frame.empty else {"type": "FeatureCollection", "features": []}


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
