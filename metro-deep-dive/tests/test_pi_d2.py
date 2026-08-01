"""Tests for Place Intelligence D2 catchment profiles and benchmarks."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pandas as pd
import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "metro-area-explorer"
    / "place_intelligence"
    / "site_prep.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("place_intelligence_site_prep", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def pi_d2():
    return _load_module()


@pytest.fixture
def synthetic_site(pi_d2):
    return pi_d2.Site(
        site_id="jacksonville_fl_baymeadows_v0",
        address="3832 Baymeadows Road, Jacksonville, FL 32217",
        lat=30.2176,
        lon=-81.6167,
        geocode_source="manual_override",
        market_id="27260",
        asset_type="retail",
        rings_mi=[1, 3, 5],
        primary_ring_mi=3,
    )


@pytest.fixture
def synthetic_weights():
    return pd.DataFrame(
        [
            {"site_id": "jacksonville_fl_baymeadows_v0", "ring_mi": 1, "tract_geoid": "12031000100", "weight": 1.0},
            {"site_id": "jacksonville_fl_baymeadows_v0", "ring_mi": 3, "tract_geoid": "12031000100", "weight": 0.25},
            {"site_id": "jacksonville_fl_baymeadows_v0", "ring_mi": 3, "tract_geoid": "12031000200", "weight": 0.75},
            {"site_id": "jacksonville_fl_baymeadows_v0", "ring_mi": 5, "tract_geoid": "12031000200", "weight": 0.4},
            {"site_id": "jacksonville_fl_baymeadows_v0", "ring_mi": 5, "tract_geoid": "12031000300", "weight": 0.6},
        ]
    )


def test_build_catchment_profile_carries_vintage_and_percentile_denominator(
    monkeypatch,
    pi_d2,
    synthetic_site,
    synthetic_weights,
):
    metric = pi_d2._get_metric_definition("pop_total")
    surface = pd.DataFrame(
        [
            {"geo_level_normalized": "tract", "geo_level": "tract", "geo_id": "12031000100", "geo_name": "T1", "year": 2019, "metric_value": 100.0},
            {"geo_level_normalized": "tract", "geo_level": "tract", "geo_id": "12031000200", "geo_name": "T2", "year": 2019, "metric_value": 200.0},
            {"geo_level_normalized": "tract", "geo_level": "tract", "geo_id": "12031000300", "geo_name": "T3", "year": 2019, "metric_value": 300.0},
            {"geo_level_normalized": "tract", "geo_level": "tract", "geo_id": "12031000100", "geo_name": "T1", "year": 2024, "metric_value": 110.0},
            {"geo_level_normalized": "tract", "geo_level": "tract", "geo_id": "12031000200", "geo_name": "T2", "year": 2024, "metric_value": 210.0},
            {"geo_level_normalized": "tract", "geo_level": "tract", "geo_id": "12031000300", "geo_name": "T3", "year": 2024, "metric_value": 310.0},
            {"geo_level_normalized": "cbsa", "geo_level": "cbsa", "geo_id": "27260", "geo_name": "Jacksonville, FL", "year": 2024, "metric_value": 999.0},
            {"geo_level_normalized": "county", "geo_level": "county", "geo_id": "12031", "geo_name": "Duval County", "year": 2024, "metric_value": 888.0},
            {"geo_level_normalized": "state", "geo_level": "state", "geo_id": "12", "geo_name": "Florida", "year": 2024, "metric_value": 777.0},
            {"geo_level_normalized": "us", "geo_level": "US", "geo_id": "1", "geo_name": "United States", "year": 2024, "metric_value": 666.0},
        ]
    )

    monkeypatch.setattr(pi_d2, "METRIC_DEFINITIONS", (metric,))
    monkeypatch.setattr(pi_d2, "METRIC_DEFINITION_MAP", {metric.metric_id: metric})
    monkeypatch.setattr(pi_d2, "_query_metric_surface", lambda _metric, _market_id: surface)
    monkeypatch.setattr(pi_d2, "_get_site_county_and_state", lambda site: ("12031", "12"))

    profile = pi_d2.build_catchment_profile(synthetic_site, synthetic_weights)

    assert set(profile["year"]) == {2024}
    primary_row = profile.loc[profile["ring_mi"] == 3].iloc[0]
    assert primary_row["cbsa_percentile_denominator"] == 3
    assert primary_row["cbsa_percentile"] == pytest.approx((1 / 3) * 100)
    assert primary_row["change_5yr_period"] == "2019-2024"


def test_build_d2_profile_payload_records_skip_reason_for_missing_metric(
    monkeypatch,
    pi_d2,
    synthetic_site,
    synthetic_weights,
):
    metric = pi_d2._get_metric_definition("median_hh_income")
    monkeypatch.setattr(pi_d2, "METRIC_DEFINITIONS", (metric,))
    monkeypatch.setattr(pi_d2, "METRIC_DEFINITION_MAP", {metric.metric_id: metric})
    monkeypatch.setattr(
        pi_d2,
        "_query_metric_surface",
        lambda _metric, _market_id: pd.DataFrame(
            columns=["geo_level_normalized", "geo_level", "geo_id", "geo_name", "year", "metric_value"]
        ),
    )
    monkeypatch.setattr(pi_d2, "_get_site_county_and_state", lambda site: ("12031", "12"))

    payload = pi_d2.build_d2_profile_payload(synthetic_site, synthetic_weights)

    assert payload["catchment_profile"].empty
    assert payload["skip_reasons"].iloc[0]["metric"] == "median_hh_income"
    assert "No tract-grain values available" in payload["skip_reasons"].iloc[0]["reason"]


def test_build_benchmark_table_uses_same_query_path_as_catchment(
    monkeypatch,
    pi_d2,
    synthetic_site,
    synthetic_weights,
):
    metric = pi_d2._get_metric_definition("pop_total")
    calls: list[tuple[str, str]] = []
    surface = pd.DataFrame(
        [
            {"geo_level_normalized": "tract", "geo_level": "tract", "geo_id": "12031000100", "geo_name": "T1", "year": 2024, "metric_value": 100.0},
            {"geo_level_normalized": "tract", "geo_level": "tract", "geo_id": "12031000200", "geo_name": "T2", "year": 2024, "metric_value": 200.0},
            {"geo_level_normalized": "cbsa", "geo_level": "cbsa", "geo_id": "27260", "geo_name": "Jacksonville, FL", "year": 2024, "metric_value": 999.0},
            {"geo_level_normalized": "county", "geo_level": "county", "geo_id": "12031", "geo_name": "Duval County", "year": 2024, "metric_value": 888.0},
            {"geo_level_normalized": "state", "geo_level": "state", "geo_id": "12", "geo_name": "Florida", "year": 2024, "metric_value": 777.0},
            {"geo_level_normalized": "us", "geo_level": "US", "geo_id": "1", "geo_name": "United States", "year": 2024, "metric_value": 666.0},
        ]
    )

    def _fake_query(metric_def, market_id):
        calls.append((metric_def.metric_id, market_id))
        return surface

    monkeypatch.setattr(pi_d2, "METRIC_DEFINITIONS", (metric,))
    monkeypatch.setattr(pi_d2, "METRIC_DEFINITION_MAP", {metric.metric_id: metric})
    monkeypatch.setattr(pi_d2, "_query_metric_surface", _fake_query)
    monkeypatch.setattr(pi_d2, "_get_site_county_and_state", lambda site: ("12031", "12"))

    pi_d2.build_catchment_profile(synthetic_site, synthetic_weights)
    pi_d2.build_benchmark_table(synthetic_site)

    assert calls.count(("pop_total", "27260")) >= 2


def test_compute_percentile_returns_denominator_from_cbsa_tract_distribution(monkeypatch, pi_d2):
    metric = pi_d2._get_metric_definition("pop_total")
    surface = pd.DataFrame(
        [
            {"geo_level_normalized": "tract", "geo_level": "tract", "geo_id": "1", "geo_name": "T1", "year": 2024, "metric_value": 100.0},
            {"geo_level_normalized": "tract", "geo_level": "tract", "geo_id": "2", "geo_name": "T2", "year": 2024, "metric_value": 200.0},
            {"geo_level_normalized": "tract", "geo_level": "tract", "geo_id": "3", "geo_name": "T3", "year": 2024, "metric_value": 300.0},
        ]
    )

    monkeypatch.setattr(pi_d2, "_query_metric_surface", lambda _metric, _market_id: surface)

    percentile, denominator = pi_d2.compute_percentile("pop_total", 200.0, "27260")

    assert denominator == 3
    assert percentile == pytest.approx((2 / 3) * 100)
