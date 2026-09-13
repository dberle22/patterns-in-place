"""Focused V1 Catchment tests using the reusable Jacksonville Baymeadows case."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pandas as pd
import pytest


MODULE_PATH = Path(__file__).with_name("catchment.py")
SPEC = importlib.util.spec_from_file_location("explanation_catchment", MODULE_PATH)
assert SPEC and SPEC.loader
catchment = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = catchment
SPEC.loader.exec_module(catchment)

JACKSONVILLE = catchment.PropertyInput(
    property_id="jacksonville_fl_baymeadows_v0",
    label="Jacksonville Baymeadows",
    address="3832 Baymeadows Road, Jacksonville, FL 32217",
    market_id="27260",
    lat=30.217618577902,
    lon=-81.616679103522,
)
RICHMOND = catchment.PropertyInput(
    property_id="richmond_va_carter_st_v0",
    label="Richmond Carter Street",
    address="1814 Carter St, Richmond, VA 23220",
    market_id="40060",
)
RICHMOND_CENSUS_MATCH = {
    # Captured from the Census current geographies response on 2026-09-11.
    # The fixture keeps the regression suite deterministic while exercising the
    # address-geocoding branch rather than the manual-coordinate override.
    "lat": 37.5327565895,
    "lon": -77.470500800813,
    "matched_address": "1814 CARTER ST, RICHMOND, VA, 23220",
    "tract_geoid": "51760041300",
    "match_type": "address_range",
    "geocode_source": "census_geocoder:Public_AR_Current:Current_Current",
}
LEGACY_WEIGHTS = (
    Path(__file__).resolve().parents[4]
    / "metro-deep-dive/metro-area-explorer/place_intelligence/outputs/jacksonville_fl/site_artifacts"
    / "jacksonville_fl_baymeadows_v0/base_weight_table.csv"
)


@pytest.fixture(scope="module")
def baymeadows_core():
    """Run the shared manual-coordinate fixture through the new core path once."""

    with catchment.open_connection() as con:
        point = catchment.resolve_property_point(con, JACKSONVILLE)
        catchment.validate_point_market(con, point)
        tracts = catchment.load_market_tracts(con, JACKSONVILLE.market_id)
        bands = catchment.build_band_geometries(point, JACKSONVILLE.reach_distances_mi)
        contributions = catchment.build_band_contributions(bands, tracts)
        inputs = catchment.load_standard_metric_inputs(con, JACKSONVILLE.market_id)
    return point, tracts, bands, contributions, inputs


def test_baymeadows_bands_reproduce_legacy_weights_and_keep_provenance(baymeadows_core):
    """The selective port keeps the tested areal calculation while clarifying fields."""

    point, _tracts, bands, contributions, _inputs = baymeadows_core
    legacy = pd.read_csv(LEGACY_WEIGHTS, dtype={"tract_geoid": str})
    actual = contributions.rename(columns={"band_outer_mi": "ring_mi", "tract_share": "weight"})
    joined = legacy.merge(actual[["ring_mi", "tract_geoid", "weight"]], on=["ring_mi", "tract_geoid"], suffixes=("_legacy", "_new"), validate="one_to_one")

    assert point.match_type == "manual_override"
    assert point.geocode_source == "manual_override"
    assert len(joined) == len(legacy) == 75
    assert _tracts.attrs["market_membership_tract_count"] == 343
    assert _tracts.attrs["market_geometry_tract_count"] == 340
    assert _tracts.attrs["missing_market_geometry_tract_count"] == 3
    assert (joined.weight_legacy - joined.weight_new).abs().max() < 1e-10
    assert set(contributions.geometry_role) == {"legacy_unclassified"}
    assert set(contributions.geometry_vintage) == {"unknown_legacy_vintage"}
    assert bands.band_area_sq_mi.tolist() == pytest.approx([3.14159, 25.1327, 50.2655], rel=0.002)


def test_bands_are_nonoverlapping_and_cumulative_reaches_sum_them(baymeadows_core):
    """A 1--3 mile band cannot be confused with a 0--3 mile cumulative reach."""

    _point, _tracts, bands, contributions, _inputs = baymeadows_core
    reaches = catchment.derive_cumulative_reach_contributions(contributions)
    reach_geometries = catchment.derive_cumulative_reach_geometries(bands)

    assert bands[["band_inner_mi", "band_outer_mi"]].values.tolist() == [[0, 1], [1, 3], [3, 5]]
    assert bands.geometry.iloc[0].intersection(bands.geometry.iloc[1]).area == pytest.approx(0, abs=1e-4)
    assert (contributions.tract_share > 0).all() and (contributions.tract_share <= 1).all()
    expected = contributions.loc[contributions.band_outer_mi <= 3].groupby("tract_geoid").tract_share.sum()
    actual = reaches.loc[reaches.reach_outer_mi == 3].set_index("tract_geoid").tract_share
    assert actual.sort_index().equals(expected.sort_index())
    assert reach_geometries.reach_area_sq_mi.tolist() == pytest.approx([3.14159, 28.2743, 78.5398], rel=0.002)


def test_market_validation_rejects_the_wrong_market(baymeadows_core):
    """A resolved point must be in the market used to load contributing tracts."""

    point, _tracts, _bands, _contributions, _inputs = baymeadows_core
    wrong_market = catchment.ResolvedPoint(**{**point.__dict__, "market_id": "12060"})
    with catchment.open_connection() as con, pytest.raises(ValueError, match="does not belong"):
        catchment.validate_point_market(con, wrong_market)


def test_profile_uses_occupied_households_not_the_legacy_bad_alias(baymeadows_core):
    """Households are occupied units, and all standard metrics expose contracts."""

    _point, _tracts, _bands, contributions, inputs = baymeadows_core
    reaches = catchment.derive_cumulative_reach_contributions(contributions)
    profile = catchment.aggregate_profile(reaches, inputs)
    household_row = profile.loc[(profile.reach_outer_mi == 3) & (profile.metric_id == "households")].iloc[0]
    expected = reaches.loc[reaches.reach_outer_mi == 3].merge(inputs[["tract_geoid", "occ_occupied"]], on="tract_geoid")

    assert household_row.value == pytest.approx((expected.tract_share * expected.occ_occupied).sum())
    assert "median_age" not in set(profile.metric_id)
    assert profile.weighted_denominator.notna().sum() == 15 * 3
    assert set(profile.aggregation) == {"count", "ratio"}


def test_rate_aggregation_uses_source_numerator_and_denominator():
    """A generic rate must not be calculated as an areal-weighted tract rate."""

    contributions = pd.DataFrame({"property_id": ["p", "p"], "market_id": ["m", "m"],
        "reach_outer_mi": [1, 1], "tract_geoid": ["a", "b"], "tract_share": [0.5, 0.5]})
    inputs = pd.DataFrame({"tract_geoid": ["a", "b"], "year": [2024, 2024], "numerator": [1.0, 90.0], "denominator": [10.0, 100.0]})
    contract = catchment.MetricDefinition("test_rate", "Test rate", "ratio", "numerator", "denominator", "share", "test")
    result = catchment.aggregate_profile(contributions, inputs, (contract,)).iloc[0]

    assert result.value == pytest.approx((1 * 0.5 + 90 * 0.5) / (10 * 0.5 + 100 * 0.5))
    assert result.value != pytest.approx((0.1 + 0.9) / 2)


def test_profile_qa_benchmarks_and_median_evidence_are_inspectable(baymeadows_core):
    """QA reports measured coverage; medians stay tract evidence; benchmarks are comparable."""

    point, _tracts, bands, contributions, inputs = baymeadows_core
    reaches = catchment.derive_cumulative_reach_contributions(contributions)
    qa = catchment.contribution_qa(contributions, bands)
    metric_qa = catchment.metric_join_qa(reaches, inputs)
    medians = catchment.contributing_tract_medians(reaches, inputs)
    with catchment.open_connection() as con:
        benchmarks = catchment.load_compatible_benchmarks(con, point, int(inputs.year.iloc[0]))

    assert "reliability_flag" not in qa.columns
    assert (metric_qa.contribution_weight_coverage_share == 1).all()
    assert {"median_age", "median_hh_income", "median_home_value", "median_gross_rent"} == set(medians.metric_id)
    assert "population" not in set(benchmarks.metric_id)
    assert set(benchmarks.benchmark_level) == {"cbsa", "county", "state"}


def test_richmond_address_geocoding_reuses_the_full_helper_path():
    """A second market uses the address-geocoded path with no market-specific code."""

    with catchment.open_connection() as con:
        point = catchment.resolve_property_point(con, RICHMOND, geocoder=lambda _address: RICHMOND_CENSUS_MATCH)
        catchment.validate_point_market(con, point)
        tracts = catchment.load_market_tracts(con, RICHMOND.market_id)
        bands = catchment.build_band_geometries(point, RICHMOND.reach_distances_mi)
        contributions = catchment.build_band_contributions(bands, tracts)
        reaches = catchment.derive_cumulative_reach_contributions(contributions)
        inputs = catchment.load_standard_metric_inputs(con, RICHMOND.market_id)
        profile = catchment.aggregate_profile(reaches, inputs)

    assert point.match_type == "address_range"
    assert point.tract_geoid == "51760041300"
    assert len(tracts) == 332
    assert tracts.attrs["missing_market_geometry_tract_count"] == 0
    assert contributions.groupby("band_outer_mi").size().to_dict() == {1: 9, 3: 59, 5: 80}
    assert profile.shape == (51, 12)
    assert set(profile.year) == {2024}
