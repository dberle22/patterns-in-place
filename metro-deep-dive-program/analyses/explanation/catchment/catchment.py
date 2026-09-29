"""Reusable V1 Catchment helpers for property-level exploration.

The module deliberately stays analysis-local.  It opens the governed DuckDB in
read-only mode, creates Euclidean bands, and exposes the contribution tables
that make every downstream estimate inspectable.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
from typing import Callable, Iterable, Sequence
from urllib.parse import urlencode
from urllib.request import urlopen

import duckdb
import geopandas as gpd
import pandas as pd
from shapely import Point, wkb


METERS_PER_MILE = 1609.344
WGS84_CRS = "EPSG:4326"
GEOMETRY_ROLE = "legacy_unclassified"
GEOMETRY_VINTAGE = "unknown_legacy_vintage"
DEFAULT_REACHES_MI = (1, 3, 5)
GEOCODER_ROOT = "https://geocoding.geo.census.gov/geocoder"


@dataclass(frozen=True)
class PropertyInput:
    """Analyst-supplied property inputs; coordinates override address geocoding."""

    property_id: str
    label: str
    address: str
    market_id: str
    lat: float | None = None
    lon: float | None = None
    reach_distances_mi: tuple[int, ...] = DEFAULT_REACHES_MI


@dataclass(frozen=True)
class ResolvedPoint:
    """A point plus the provenance needed to interpret its catchment."""

    property_id: str
    label: str
    address: str
    market_id: str
    lat: float
    lon: float
    matched_address: str
    match_type: str
    tract_geoid: str
    geocode_source: str


@dataclass(frozen=True)
class MetricDefinition:
    """Aggregation contract for a standard profile metric."""

    metric_id: str
    label: str
    aggregation: str
    numerator_column: str
    denominator_column: str | None
    unit: str
    source_relation: str
    benchmark_relation: str | None = None
    benchmark_column: str | None = None


# Counts are additive; every rate is rebuilt from its source numerator and
# denominator.  The income proxy is population-weighted per-capita income.
STANDARD_METRICS = (
    MetricDefinition("population", "Population", "count", "pop_total", None, "people", "silver.age_kpi"),
    MetricDefinition("households", "Households", "count", "occ_occupied", None, "households", "silver.housing_kpi"),
    MetricDefinition("share_under_18", "Under 18", "ratio", "under_18_count", "pop_total", "share", "silver.age_kpi", "gold.population_demographics", "pct_age_under_18"),
    MetricDefinition("share_65_plus", "65 and older", "ratio", "age_65_plus_count", "pop_total", "share", "silver.age_kpi", "gold.population_demographics", "pct_age_over_64"),
    MetricDefinition("share_white_nh", "White, non-Hispanic", "ratio", "race_white_nh", "race_total", "share", "silver.race_kpi", "gold.population_demographics", "pct_white_nh"),
    MetricDefinition("share_black_nh", "Black, non-Hispanic", "ratio", "race_black_nh", "race_total", "share", "silver.race_kpi", "gold.population_demographics", "pct_black_nh"),
    MetricDefinition("share_hispanic", "Hispanic", "ratio", "race_hispanic", "race_total", "share", "silver.race_kpi", "gold.population_demographics", "pct_hispanic"),
    MetricDefinition("share_ba_plus", "Bachelor's degree or higher", "ratio", "ba_plus_count", "edu_total_25p", "share", "silver.education_kpi", "gold.population_demographics", "pct_ba_plus"),
    MetricDefinition("per_capita_income", "Per-capita income", "ratio", "income_total_proxy", "pop_total", "dollars", "silver.income_kpi + silver.age_kpi", "gold.economics_income_wide", "acs_income_pc"),
    MetricDefinition("poverty_rate", "Poverty rate", "ratio", "pov_below", "pov_universe", "share", "silver.income_kpi", "gold.economics_income_wide", "pov_rate"),
    MetricDefinition("owner_occupied_share", "Owner-occupied households", "ratio", "owner_occupied", "tenure_total", "share", "silver.housing_kpi", "gold.housing_core_wide", "owner_occ_rate"),
    MetricDefinition("renter_occupied_share", "Renter-occupied households", "ratio", "renter_occupied", "tenure_total", "share", "silver.housing_kpi", "gold.housing_core_wide", "renter_occ_rate"),
    MetricDefinition("vacancy_rate", "Vacancy rate", "ratio", "occ_vacant", "occ_total", "share", "silver.housing_kpi", "gold.housing_core_wide", "vacancy_rate"),
    MetricDefinition("multifamily_share", "Multifamily structures", "ratio", "multifamily_count", "struct_total", "share", "silver.housing_kpi", "gold.housing_core_wide", "pct_struct_multifam"),
    MetricDefinition("drive_alone_share", "Drive alone", "ratio", "commute_drove_alone", "commute_workers_total", "share", "silver.transport_kpi", "gold.transport_built_form_wide", "pct_commute_drive_alone"),
    MetricDefinition("work_from_home_share", "Work from home", "ratio", "commute_worked_home", "commute_workers_total", "share", "silver.transport_kpi", "gold.transport_built_form_wide", "pct_commute_wfh"),
    MetricDefinition("zero_vehicle_household_share", "Zero-vehicle households", "ratio", "veh_0", "veh_total_hh", "share", "silver.transport_kpi", "gold.transport_built_form_wide", "pct_hh_0_vehicles"),
)


def resolve_db_path() -> Path:
    """Read ``DB_PATH`` from the environment or the repository's .Renviron file."""

    configured = os.getenv("DB_PATH")
    if configured:
        return Path(configured).expanduser()

    repo_root = Path(__file__).resolve().parents[4]
    renviron = repo_root / ".Renviron"
    if renviron.exists():
        match = re.search(r"^DB_PATH=(.+)$", renviron.read_text(), re.MULTILINE)
        if match:
            return Path(match.group(1).strip().strip('"').strip("'")).expanduser()
    raise ValueError("DB_PATH is not configured in the environment or repository .Renviron.")


def open_connection(db_path: Path | str | None = None) -> duckdb.DuckDBPyConnection:
    """Open the governed warehouse read-only and enable its spatial extension."""

    con = duckdb.connect(str(db_path or resolve_db_path()), read_only=True)
    con.execute("LOAD spatial;")
    return con


def normalize_reach_distances(reaches_mi: Sequence[int]) -> tuple[int, ...]:
    """Require positive integer outer distances and return sorted unique values."""

    if not reaches_mi:
        raise ValueError("reach_distances_mi must contain at least one positive integer.")
    if any(isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in reaches_mi):
        raise ValueError("reach_distances_mi must contain only positive integers.")
    return tuple(sorted(set(reaches_mi)))


def validate_property_input(property_input: PropertyInput) -> PropertyInput:
    """Check the notebook-facing contract before a geocoder or database is used."""

    for field in ("property_id", "label", "address", "market_id"):
        if not str(getattr(property_input, field)).strip():
            raise ValueError(f"{field} must be non-empty.")
    if (property_input.lat is None) != (property_input.lon is None):
        raise ValueError("manual latitude and longitude must be supplied together.")
    if property_input.lat is not None and not -90 <= float(property_input.lat) <= 90:
        raise ValueError("manual latitude must be between -90 and 90.")
    if property_input.lon is not None and not -180 <= float(property_input.lon) <= 180:
        raise ValueError("manual longitude must be between -180 and 180.")
    normalize_reach_distances(property_input.reach_distances_mi)
    return property_input


def geocode_address(address: str) -> dict[str, object]:
    """Call the Census one-line geocoder and retain its own address provenance."""

    if not address.strip():
        raise ValueError("address must be non-empty.")
    params = {"address": address.strip(), "benchmark": "4", "vintage": "4", "format": "json"}
    with urlopen(f"{GEOCODER_ROOT}/geographies/onelineaddress?{urlencode(params)}") as response:  # noqa: S310
        payload = json.loads(response.read().decode("utf-8"))
    matches = ((payload.get("result") or {}).get("addressMatches") or [])
    if not matches:
        raise ValueError(f"Census geocoder returned no match for address: {address}")
    match = matches[0]
    tracts = ((match.get("geographies") or {}).get("Census Tracts") or [])
    if not tracts or not tracts[0].get("GEOID"):
        raise ValueError("Census geocoder response did not include a tract GEOID.")
    coordinates = match.get("coordinates") or {}
    return {
        "lat": float(coordinates["y"]), "lon": float(coordinates["x"]),
        "matched_address": str(match["matchedAddress"]), "tract_geoid": str(tracts[0]["GEOID"]),
        "match_type": "address_range", "geocode_source": "census_geocoder:current",
    }


def resolve_tract_from_coordinates(con: duckdb.DuckDBPyConnection, lon: float, lat: float) -> str:
    """Return the governed V1 tract containing a longitude/latitude point."""

    row = con.execute(
        """SELECT tract_geoid FROM patterns_in_place.geo.tracts_all_us
           WHERE ST_Contains(geom, ST_Point(CAST(? AS DOUBLE), CAST(? AS DOUBLE))) LIMIT 1""",
        [float(lon), float(lat)],
    ).fetchone()
    if row is None:
        raise ValueError(f"No containing tract found for lon={lon}, lat={lat}.")
    return str(row[0])


def resolve_property_point(
    con: duckdb.DuckDBPyConnection,
    property_input: PropertyInput,
    geocoder: Callable[[str], dict[str, object]] = geocode_address,
) -> ResolvedPoint:
    """Resolve a property, with manual coordinates taking explicit precedence."""

    validate_property_input(property_input)
    if property_input.lat is not None:
        tract_geoid = resolve_tract_from_coordinates(con, float(property_input.lon), float(property_input.lat))
        return ResolvedPoint(property_input.property_id, property_input.label, property_input.address,
            str(property_input.market_id), float(property_input.lat), float(property_input.lon),
            property_input.address, "manual_override", tract_geoid, "manual_override")
    result = geocoder(property_input.address)
    spatial_tract = resolve_tract_from_coordinates(con, float(result["lon"]), float(result["lat"]))
    source = str(result["geocode_source"])
    if spatial_tract != str(result["tract_geoid"]):
        source = f"{source}:tract_corrected_by_spatial_join"
    return ResolvedPoint(property_input.property_id, property_input.label, property_input.address,
        str(property_input.market_id), float(result["lat"]), float(result["lon"]),
        str(result["matched_address"]), str(result["match_type"]), spatial_tract, source)


def validate_point_market(con: duckdb.DuckDBPyConnection, resolved_point: ResolvedPoint) -> None:
    """Make an address/market mismatch explicit before geometry is allocated."""

    found = con.execute(
        "SELECT 1 FROM patterns_in_place.mart_geography.rollup_tract_to_cbsa WHERE tract_geoid = ? AND cbsa_code = ? LIMIT 1",
        [resolved_point.tract_geoid, resolved_point.market_id],
    ).fetchone()
    if found is None:
        raise ValueError(
            f"Resolved tract {resolved_point.tract_geoid} does not belong to market {resolved_point.market_id}."
        )


def load_market_tracts(con: duckdb.DuckDBPyConnection, market_id: str) -> gpd.GeoDataFrame:
    """Load one market's V1 geometry with identity and geometry provenance."""

    membership_count = con.execute(
        "SELECT COUNT(DISTINCT tract_geoid) FROM patterns_in_place.mart_geography.rollup_tract_to_cbsa WHERE cbsa_code = ?",
        [str(market_id)],
    ).fetchone()[0]
    rows = con.execute(
        """SELECT DISTINCT r.tract_geoid, r.tract_boundary_vintage, r.cbsa_boundary_vintage,
                  r.tract_county_source, r.county_cbsa_source, ST_AsWKB(g.geom) AS geom_wkb
           FROM patterns_in_place.mart_geography.rollup_tract_to_cbsa r
           JOIN patterns_in_place.geo.tracts_all_us g ON g.tract_geoid = r.tract_geoid
           WHERE r.cbsa_code = ? ORDER BY r.tract_geoid""", [str(market_id)]
    ).fetchall()
    if not rows:
        raise ValueError(f"No tract geometry found for market_id={market_id}.")
    records = []
    geometries = []
    for tract, tract_vintage, cbsa_vintage, tract_source, cbsa_source, geometry in rows:
        records.append({"tract_geoid": str(tract), "tract_boundary_vintage": tract_vintage,
            "cbsa_boundary_vintage": cbsa_vintage, "tract_county_source": tract_source,
            "county_cbsa_source": cbsa_source, "geometry_role": GEOMETRY_ROLE,
            "geometry_vintage": GEOMETRY_VINTAGE})
        geometries.append(wkb.loads(bytes(geometry)))
    result = gpd.GeoDataFrame(records, geometry=geometries, crs=WGS84_CRS)
    # Membership and usable V1 geometry are separately reported: legacy
    # geometry can be incomplete even when the governed identity rollup is not.
    result.attrs["market_membership_tract_count"] = int(membership_count)
    result.attrs["market_geometry_tract_count"] = len(result)
    result.attrs["missing_market_geometry_tract_count"] = int(membership_count) - len(result)
    return result


def build_band_geometries(resolved_point: ResolvedPoint, reaches_mi: Sequence[int]) -> gpd.GeoDataFrame:
    """Build projected, non-overlapping Euclidean bands with explicit edges."""

    distances = normalize_reach_distances(reaches_mi)
    point = gpd.GeoSeries([Point(resolved_point.lon, resolved_point.lat)], crs=WGS84_CRS)
    projected_crs = point.estimate_utm_crs()
    if projected_crs is None:
        raise ValueError("Could not estimate a projected CRS for the property point.")
    projected_point = point.to_crs(projected_crs).iloc[0]
    previous = None
    rows = []
    for outer in distances:
        circle = projected_point.buffer(outer * METERS_PER_MILE)
        geometry = circle if previous is None else circle.difference(previous)
        rows.append({"property_id": resolved_point.property_id, "market_id": resolved_point.market_id,
            "band_inner_mi": 0 if previous is None else previous_outer, "band_outer_mi": outer,
            "band_area_sq_mi": geometry.area / METERS_PER_MILE ** 2, "geometry": geometry})
        previous, previous_outer = circle, outer
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=projected_crs)


def build_band_contributions(
    bands: gpd.GeoDataFrame, market_tracts: gpd.GeoDataFrame,
) -> pd.DataFrame:
    """Intersect market tracts with bands and return canonical areal contributions."""

    if bands.empty:
        return pd.DataFrame()
    if bands.crs is None or market_tracts.crs is None:
        raise ValueError("bands and market_tracts must carry CRS metadata.")
    tracts = market_tracts.to_crs(bands.crs)
    rows: list[dict[str, object]] = []
    for band in bands.itertuples(index=False):
        candidates = tracts.loc[tracts.geometry.intersects(band.geometry)].copy()
        for tract in candidates.itertuples(index=False):
            intersection_area = tract.geometry.intersection(band.geometry).area
            tract_area = tract.geometry.area
            if intersection_area <= 0 or tract_area <= 0:
                continue
            # Floating-point overlay can make complete containment fractionally
            # exceed one; the physical tract-share contract is closed at one.
            share = min(1.0, max(0.0, intersection_area / tract_area))
            rows.append({"property_id": band.property_id, "market_id": band.market_id,
                "band_inner_mi": band.band_inner_mi, "band_outer_mi": band.band_outer_mi,
                "tract_geoid": tract.tract_geoid, "tract_share": float(share),
                "intersection_area_sq_m": float(intersection_area), "tract_area_sq_m": float(tract_area),
                "containment": "full" if abs(share - 1) <= 1e-9 else "fragment",
                "centroid_in_band": bool(tract.geometry.centroid.within(band.geometry)),
                "weight_method": "areal", "geometry_role": tract.geometry_role,
                "geometry_vintage": tract.geometry_vintage,
                "tract_boundary_vintage": tract.tract_boundary_vintage,
                "cbsa_boundary_vintage": tract.cbsa_boundary_vintage})
    return pd.DataFrame(rows).sort_values(["band_outer_mi", "tract_geoid"]).reset_index(drop=True)


def derive_cumulative_reach_geometries(bands: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Turn annular bands into separately labeled cumulative reach geometries."""

    rows = []
    union = None
    for band in bands.sort_values("band_outer_mi").itertuples(index=False):
        union = band.geometry if union is None else union.union(band.geometry)
        rows.append({"property_id": band.property_id, "market_id": band.market_id,
            "reach_inner_mi": 0, "reach_outer_mi": band.band_outer_mi,
            "reach_area_sq_mi": union.area / METERS_PER_MILE ** 2, "geometry": union})
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=bands.crs)


def derive_cumulative_reach_contributions(band_contributions: pd.DataFrame) -> pd.DataFrame:
    """Sum disjoint band shares to produce explicit 'within X miles' weights."""

    required = {"property_id", "market_id", "band_outer_mi", "tract_geoid", "tract_share"}
    if not required.issubset(band_contributions.columns):
        raise ValueError(f"band_contributions must include {sorted(required)}.")
    metadata = [column for column in band_contributions.columns if column not in {
        "band_inner_mi", "band_outer_mi", "tract_share", "intersection_area_sq_m", "containment", "centroid_in_band"}]
    rows = []
    ordered = band_contributions.sort_values("band_outer_mi")
    for outer in ordered["band_outer_mi"].unique():
        grouped = ordered.loc[ordered["band_outer_mi"] <= outer].groupby(
            ["property_id", "market_id", "tract_geoid"], as_index=False
        )["tract_share"].sum()
        grouped["reach_inner_mi"] = 0
        grouped["reach_outer_mi"] = outer
        for column in metadata:
            if column not in grouped.columns:
                lookup = ordered[["tract_geoid", column]].drop_duplicates("tract_geoid")
                grouped = grouped.merge(lookup, on="tract_geoid", how="left")
        rows.append(grouped)
    return pd.concat(rows, ignore_index=True).sort_values(["reach_outer_mi", "tract_geoid"]).reset_index(drop=True)


def contribution_qa(band_contributions: pd.DataFrame, bands: gpd.GeoDataFrame) -> pd.DataFrame:
    """Expose measured geometry and weight diagnostics without a reliability score."""

    rows = []
    for band in bands.itertuples(index=False):
        weights = band_contributions.loc[band_contributions.band_outer_mi == band.band_outer_mi]
        intersection_area = weights.intersection_area_sq_m.sum() if len(weights) else 0.0
        total_share = weights.tract_share.sum() if len(weights) else 0.0
        rows.append({"band_inner_mi": band.band_inner_mi, "band_outer_mi": band.band_outer_mi,
            "band_area_sq_mi": band.band_area_sq_mi, "contributing_tract_count": len(weights),
            "whole_tract_count": int((weights.containment == "full").sum()) if len(weights) else 0,
            "fragment_tract_count": int((weights.containment == "fragment").sum()) if len(weights) else 0,
            "min_tract_share": weights.tract_share.min() if len(weights) else None,
            "max_tract_share": weights.tract_share.max() if len(weights) else None,
            "sum_tract_shares": total_share,
            "market_geometry_coverage_share": intersection_area / (band.band_area_sq_mi * METERS_PER_MILE ** 2),
            "largest_contribution_share": weights.tract_share.max() / total_share if total_share else None,
            "weight_bounds_pass": bool(((weights.tract_share > 0) & (weights.tract_share <= 1)).all())})
    return pd.DataFrame(rows)


def latest_common_metric_year(con: duckdb.DuckDBPyConnection, market_id: str) -> int:
    """Use the latest year available across every raw standard-profile source."""

    tables = ("age_kpi", "race_kpi", "education_kpi", "income_kpi", "housing_kpi", "transport_kpi")
    years = []
    for table in tables:
        year = con.execute(
            f"""SELECT MAX(s.year) FROM patterns_in_place.silver.{table} s
                JOIN patterns_in_place.mart_geography.rollup_tract_to_cbsa r ON r.tract_geoid = s.geo_id
                WHERE s.geo_level = 'tract' AND r.cbsa_code = ?""", [str(market_id)]
        ).fetchone()[0]
        if year is None:
            raise ValueError(f"No tract metric data found for {table} in market {market_id}.")
        years.append(int(year))
    return min(years)


def load_standard_metric_inputs(con: duckdb.DuckDBPyConnection, market_id: str, year: int | None = None) -> pd.DataFrame:
    """Load raw tract counts needed by the metric registry at one common year."""

    metric_year = year or latest_common_metric_year(con, market_id)
    query = """
        WITH market AS (
          SELECT DISTINCT tract_geoid FROM patterns_in_place.mart_geography.rollup_tract_to_cbsa WHERE cbsa_code = ?
        )
        SELECT a.geo_id AS tract_geoid, a.year, a.pop_total, a.age_0_4, a.age_5_14, a.age_15_17,
          a.age_65_74, a.age_75_84, a.age_85p, a.median_age,
          r.race_total, r.race_white_nh, r.race_black_nh, r.race_hispanic,
          e.edu_total_25p, e.ba_25p, e.ma_plus_25p,
          i.per_capita_income, i.pov_universe, i.pov_below, i.median_hh_income,
          h.occ_occupied, h.occ_total, h.occ_vacant, h.tenure_total, h.owner_occupied, h.renter_occupied,
          h.struct_total, h.struct_small_mf, h.struct_mid_mf, h.struct_large_mf, h.median_home_value, h.median_gross_rent,
          t.commute_workers_total, t.commute_drove_alone, t.commute_worked_home, t.veh_total_hh, t.veh_0
        FROM market m
        JOIN patterns_in_place.silver.age_kpi a ON a.geo_id = m.tract_geoid AND a.geo_level = 'tract' AND a.year = ?
        JOIN patterns_in_place.silver.race_kpi r ON r.geo_id = m.tract_geoid AND r.geo_level = 'tract' AND r.year = a.year
        JOIN patterns_in_place.silver.education_kpi e ON e.geo_id = m.tract_geoid AND e.geo_level = 'tract' AND e.year = a.year
        JOIN patterns_in_place.silver.income_kpi i ON i.geo_id = m.tract_geoid AND i.geo_level = 'tract' AND i.year = a.year
        JOIN patterns_in_place.silver.housing_kpi h ON h.geo_id = m.tract_geoid AND h.geo_level = 'tract' AND h.year = a.year
        JOIN patterns_in_place.silver.transport_kpi t ON t.geo_id = m.tract_geoid AND t.geo_level = 'tract' AND t.year = a.year
    """
    inputs = con.execute(query, [str(market_id), metric_year]).fetchdf()
    if inputs.empty:
        raise ValueError(f"No complete tract metric inputs found for market {market_id}, year {metric_year}.")
    inputs["under_18_count"] = inputs.age_0_4 + inputs.age_5_14 + inputs.age_15_17
    inputs["age_65_plus_count"] = inputs.age_65_74 + inputs.age_75_84 + inputs.age_85p
    inputs["ba_plus_count"] = inputs.ba_25p + inputs.ma_plus_25p
    inputs["income_total_proxy"] = inputs.per_capita_income * inputs.pop_total
    inputs["multifamily_count"] = inputs.struct_small_mf + inputs.struct_mid_mf + inputs.struct_large_mf
    return inputs


def aggregate_profile(
    cumulative_contributions: pd.DataFrame, metric_inputs: pd.DataFrame,
    definitions: Iterable[MetricDefinition] = STANDARD_METRICS,
) -> pd.DataFrame:
    """Aggregate profile values from explicit contribution shares and contracts."""

    required = {"tract_geoid", "tract_share", "reach_outer_mi"}
    if not required.issubset(cumulative_contributions.columns):
        raise ValueError(f"cumulative_contributions must include {sorted(required)}.")
    merged = cumulative_contributions.merge(metric_inputs, on="tract_geoid", how="left", validate="many_to_one")
    records = []
    for definition in definitions:
        needed = [definition.numerator_column] + ([definition.denominator_column] if definition.denominator_column else [])
        for reach, values in merged.groupby("reach_outer_mi", sort=True):
            usable = values.dropna(subset=needed)
            numerator = (usable[definition.numerator_column] * usable.tract_share).sum()
            denominator = None
            value = numerator
            if definition.aggregation == "ratio":
                denominator = (usable[definition.denominator_column] * usable.tract_share).sum()
                value = numerator / denominator if denominator else None
            records.append({"property_id": values.property_id.iloc[0], "market_id": values.market_id.iloc[0],
                "reach_outer_mi": reach, "metric_id": definition.metric_id, "metric_label": definition.label,
                "aggregation": definition.aggregation, "value": value, "weighted_numerator": numerator,
                "weighted_denominator": denominator, "unit": definition.unit,
                "source_relation": definition.source_relation, "year": int(usable.year.iloc[0]) if len(usable) else None})
    return pd.DataFrame(records)


def metric_join_qa(cumulative_contributions: pd.DataFrame, metric_inputs: pd.DataFrame,
                   definitions: Iterable[MetricDefinition] = STANDARD_METRICS) -> pd.DataFrame:
    """Report the tract-share coverage supplying each metric, rather than a score."""

    merged = cumulative_contributions.merge(metric_inputs, on="tract_geoid", how="left", validate="many_to_one")
    rows = []
    for definition in definitions:
        columns = [definition.numerator_column] + ([definition.denominator_column] if definition.denominator_column else [])
        for reach, values in merged.groupby("reach_outer_mi", sort=True):
            total = values.tract_share.sum()
            available = values.dropna(subset=columns).tract_share.sum()
            rows.append({"reach_outer_mi": reach, "metric_id": definition.metric_id,
                "contribution_weight_coverage_share": available / total if total else None,
                "contributing_tract_count": len(values), "tracts_with_metric_count": len(values.dropna(subset=columns))})
    return pd.DataFrame(rows)


def contributing_tract_medians(cumulative_contributions: pd.DataFrame, metric_inputs: pd.DataFrame) -> pd.DataFrame:
    """Return tract-level median evidence without manufacturing a catchment median."""

    columns = {"median_age": "Median age", "median_hh_income": "Median household income",
               "median_home_value": "Median home value", "median_gross_rent": "Median gross rent"}
    values = cumulative_contributions.merge(metric_inputs[["tract_geoid", *columns]], on="tract_geoid", how="left")
    return values.melt(id_vars=["property_id", "market_id", "reach_outer_mi", "tract_geoid", "tract_share"],
                       value_vars=list(columns), var_name="metric_id", value_name="tract_value").assign(
                           metric_label=lambda frame: frame.metric_id.map(columns))


def load_compatible_benchmarks(con: duckdb.DuckDBPyConnection, resolved_point: ResolvedPoint,
                               year: int, definitions: Iterable[MetricDefinition] = STANDARD_METRICS) -> pd.DataFrame:
    """Load same-year CBSA, county, and state comparator rows for compatible metrics."""

    geography = con.execute(
        "SELECT county_geoid, state_fips FROM patterns_in_place.geo.tracts_all_us WHERE tract_geoid = ?",
        [resolved_point.tract_geoid],
    ).fetchone()
    if geography is None:
        raise ValueError(f"No geography metadata for tract {resolved_point.tract_geoid}.")
    geo_ids = {"cbsa": resolved_point.market_id, "county": str(geography[0]), "state": str(geography[1])}
    rows = []
    for definition in definitions:
        if not definition.benchmark_relation:
            continue
        query = f"SELECT geo_level, geo_id, geo_name, {definition.benchmark_column} AS value FROM patterns_in_place.{definition.benchmark_relation} WHERE year = ? AND geo_level IN ('cbsa', 'county', 'state')"
        for level, geo_id, geo_name, value in con.execute(query, [year]).fetchall():
            if str(geo_id) == geo_ids[str(level)]:
                rows.append({"property_id": resolved_point.property_id, "market_id": resolved_point.market_id,
                    "year": year, "metric_id": definition.metric_id, "benchmark_level": level,
                    "benchmark_geo_id": str(geo_id), "benchmark_geo_name": geo_name, "value": value,
                    "unit": definition.unit, "source_relation": definition.benchmark_relation})
    return pd.DataFrame(rows)
