"""Smoke tests for the Place Intelligence D6 page modules."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import pandas as pd
import pytest


PAGES_ROOT = (
    Path(__file__).resolve().parents[1]
    / "metro-area-explorer"
    / "place_intelligence"
    / "pages"
)


def _load_page_module(filename: str):
    module_path = PAGES_ROOT / filename
    spec = importlib.util.spec_from_file_location(f"pi_d6_{filename.replace('.py', '')}", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class _DummyColumn:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def metric(self, *args, **kwargs):
        return None

    def write(self, *args, **kwargs):
        return None

    def markdown(self, *args, **kwargs):
        return None


class DummyStreamlit:
    def header(self, *args, **kwargs):
        return None

    def caption(self, *args, **kwargs):
        return None

    def subheader(self, *args, **kwargs):
        return None

    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def metric(self, *args, **kwargs):
        return None

    def write(self, *args, **kwargs):
        return None

    def markdown(self, *args, **kwargs):
        return None

    def selectbox(self, _label, options, index=0, **kwargs):
        return list(options)[index if index < len(options) else 0]

    def radio(self, _label, options, index=0, **kwargs):
        return list(options)[index if index < len(options) else 0]

    def columns(self, spec, **kwargs):
        count = spec if isinstance(spec, int) else len(spec)
        return [_DummyColumn() for _ in range(count)]


@pytest.fixture
def dummy_streamlit():
    return DummyStreamlit()


@pytest.fixture
def synthetic_site():
    return SimpleNamespace(
        site_id="jacksonville_fl_baymeadows_v0",
        address="3832 Baymeadows Road, Jacksonville, FL 32217",
        primary_ring_mi=3,
        rings_mi=[1, 3, 5],
    )


@pytest.fixture
def base_payload(synthetic_site):
    return {
        "site": synthetic_site,
        "resolved_site": SimpleNamespace(
            lat=30.217618577902,
            lon=-81.616679103522,
            tract_geoid="12031001502",
            matched_address=synthetic_site.address,
            match_type="manual_override",
            geocode_source="manual_override",
        ),
        "weight_table": pd.DataFrame(),
        "coverage_diagnostic": pd.DataFrame(
            [{"ring_mi": 1, "intersecting_tract_count": 3, "total_weight_captured": 0.7, "whole_tract_count": 0, "fragment_share": 1.0, "reliability_flag": "fragment_only"}]
        ),
        "cumulative_rings": pd.DataFrame(),
    }


def _patch_common(monkeypatch, module, dummy_streamlit):
    monkeypatch.setattr(module, "st", dummy_streamlit)
    if hasattr(module, "render_context_map"):
        monkeypatch.setattr(module, "render_context_map", lambda *args, **kwargs: None)
    if hasattr(module, "render_html_table"):
        monkeypatch.setattr(module, "render_html_table", lambda *args, **kwargs: None)
    if hasattr(module, "render_chart_result"):
        monkeypatch.setattr(module, "render_chart_result", lambda *args, **kwargs: None)
    if hasattr(module, "build_simple_bar_chart"):
        monkeypatch.setattr(module, "build_simple_bar_chart", lambda *args, **kwargs: None)
    if hasattr(module, "build_simple_line_chart"):
        monkeypatch.setattr(module, "build_simple_line_chart", lambda *args, **kwargs: None)


def test_d6_overview_page_handles_populated_and_incomplete_payloads(monkeypatch, dummy_streamlit, base_payload):
    module = _load_page_module("d_overview.py")
    _patch_common(monkeypatch, module, dummy_streamlit)
    populated_d2 = {
        "catchment_profile": pd.DataFrame(
            [
                {"ring_mi": 3, "metric": "pop_total", "metric_label": "Population", "value": 12000, "cbsa_percentile": 82.0, "change_5yr": 600, "year": 2024, "source_table": "population_demographics"},
                {"ring_mi": 3, "metric": "median_hh_income", "metric_label": "Median household income", "value": 72000, "cbsa_percentile": 75.0, "change_5yr": 4200, "year": 2024, "source_table": "economics_income_wide"},
                {"ring_mi": 3, "metric": "pct_ba_plus", "metric_label": "BA+ share", "value": 0.39, "cbsa_percentile": 68.0, "change_5yr": 0.03, "year": 2024, "source_table": "population_demographics"},
            ]
        )
    }
    populated_d3 = {
        "node_typology_label": "Mixed",
        "barrier_summary": pd.DataFrame([{"site_card_flag": True, "summary": "St. Johns River (water) — 2 crossings"}]),
    }
    populated_d5 = {
        "nfhl_site_zone": pd.DataFrame([{"flood_zone": "X", "panel_effective_date": "2022-06-17"}]),
    }
    monkeypatch.setattr(module, "load_site_base_payload", lambda _: base_payload)
    monkeypatch.setattr(module, "load_d2_payload", lambda _: populated_d2)
    monkeypatch.setattr(module, "load_d3_payload", lambda _: populated_d3)
    monkeypatch.setattr(module, "load_d5_payload", lambda _: populated_d5)
    module.render_page("synthetic.yaml")

    monkeypatch.setattr(module, "load_d2_payload", lambda _: {"catchment_profile": pd.DataFrame()})
    monkeypatch.setattr(module, "load_d3_payload", lambda _: {"node_typology_label": "Mixed", "barrier_summary": pd.DataFrame(columns=["site_card_flag", "summary"])})
    monkeypatch.setattr(module, "load_d5_payload", lambda _: {"nfhl_site_zone": pd.DataFrame()})
    module.render_page("synthetic.yaml")


def test_d6_people_page_handles_populated_and_incomplete_payloads(monkeypatch, dummy_streamlit, base_payload):
    module = _load_page_module("d_people.py")
    _patch_common(monkeypatch, module, dummy_streamlit)
    monkeypatch.setattr(module, "load_site_base_payload", lambda _: base_payload)
    monkeypatch.setattr(
        module,
        "load_d2_payload",
        lambda _: {
            "catchment_profile": pd.DataFrame(
                [
                    {"ring_mi": 1, "metric": "pop_total", "metric_label": "Population", "value": 3500, "change_5yr": 120, "change_5yr_period": "2019-2024", "source_table": "population_demographics", "year": 2024, "cbsa_percentile": None, "cbsa_percentile_denominator": None},
                    {"ring_mi": 3, "metric": "pop_total", "metric_label": "Population", "value": 12000, "change_5yr": 600, "change_5yr_period": "2019-2024", "source_table": "population_demographics", "year": 2024, "cbsa_percentile": 82.0, "cbsa_percentile_denominator": 152},
                ]
            )
        },
    )
    monkeypatch.setattr(
        module,
        "load_d3_payload",
        lambda _: {
            "daytime_population": pd.DataFrame(
                [
                    {"ring_mi": 1, "year": 2023, "jobs_total": 4400, "workers_total": 3100, "jobs_to_workers_ratio": 1.42, "daytime_net_change": 1300, "jobs_retail": 700, "jobs_accommodation_food": 500, "jobs_health_care": 600, "jobs_professional_scientific": 800},
                    {"ring_mi": 3, "year": 2023, "jobs_total": 12000, "workers_total": 9800, "jobs_to_workers_ratio": 1.22, "daytime_net_change": 2200, "jobs_retail": 1800, "jobs_accommodation_food": 1200, "jobs_health_care": 2100, "jobs_professional_scientific": 2600},
                ]
            )
        },
    )
    module.render_page("synthetic.yaml")

    monkeypatch.setattr(module, "load_d2_payload", lambda _: {"catchment_profile": pd.DataFrame()})
    monkeypatch.setattr(module, "load_d3_payload", lambda _: {"daytime_population": pd.DataFrame()})
    module.render_page("synthetic.yaml")


def test_d6_place_page_handles_populated_and_incomplete_payloads(monkeypatch, dummy_streamlit):
    module = _load_page_module("d_place.py")
    _patch_common(monkeypatch, module, dummy_streamlit)
    monkeypatch.setattr(
        module,
        "load_d3_payload",
        lambda _: {
            "poi_counts": pd.DataFrame([{"ring_mi": 1, "poi_class": "competitive", "count": 12}]),
            "barrier_summary": pd.DataFrame([{"ring_mi": 3, "barrier_type": "water", "feature_name": "St. Johns River", "crossing_count": 2, "mean_crossing_spacing_mi": 1.4, "severed_area_share": 0.18, "severed_population_share": 0.11, "summary": "St. Johns River (water) — 2 crossings"}]),
            "ring_variants": {"comparison_table": pd.DataFrame([{"ring_mi": 3, "baseline_area_sqmi": 28.2, "water_adjusted_area_sqmi": 24.6, "removed_area_share": 0.13}])},
        },
    )
    monkeypatch.setattr(
        module,
        "load_d4_payload",
        lambda _: {
            "frontage_segments": pd.DataFrame([{"roadway": "Baymeadows Rd", "aadt": 22000, "distance_mi": 0.02}]),
            "ranked_segments_1mi": pd.DataFrame([{"roadway": "I-95", "aadt": 145000}]),
            "frontage_trend": pd.DataFrame([{"year": 2021, "roadway": "Baymeadows Rd", "aadt": 20000, "series": "Baymeadows Rd"}, {"year": 2025, "roadway": "Baymeadows Rd", "aadt": 22000, "series": "Baymeadows Rd"}]),
            "count_year": 2025,
            "copy_note": "AADT is an annual average daily traffic statistic, not a peak-hour observed count.",
        },
    )
    monkeypatch.setattr(
        module,
        "load_d5_payload",
        lambda _: {
            "copy_note": "NFHL answers the parcel-level map question.",
            "nfhl_site_zone": pd.DataFrame([{"flood_zone": "X"}]),
            "nfhl_ring_shares": pd.DataFrame([{"ring_mi": 1, "flood_zone": "X", "area_share": 0.8}]),
            "nri_catchment_scores": pd.DataFrame([{"ring_mi": 3, "risk_score": 22.0}]),
        },
    )
    module.render_page("synthetic.yaml")

    monkeypatch.setattr(module, "load_d3_payload", lambda _: {"poi_counts": pd.DataFrame(), "barrier_summary": pd.DataFrame(), "ring_variants": {"comparison_table": pd.DataFrame()}})
    monkeypatch.setattr(module, "load_d4_payload", lambda _: {"frontage_segments": pd.DataFrame(), "ranked_segments_1mi": pd.DataFrame(), "frontage_trend": pd.DataFrame(), "count_year": None, "copy_note": ""})
    monkeypatch.setattr(module, "load_d5_payload", lambda _: {"copy_note": "", "nfhl_site_zone": pd.DataFrame(), "nfhl_ring_shares": pd.DataFrame(), "nri_catchment_scores": pd.DataFrame()})
    module.render_page("synthetic.yaml")


def test_d6_market_page_handles_populated_and_incomplete_payloads(monkeypatch, dummy_streamlit):
    module = _load_page_module("d_market.py")
    _patch_common(monkeypatch, module, dummy_streamlit)
    monkeypatch.setattr(
        module,
        "load_market_payload",
        lambda _: {
            "industry_context": {
                "employment_mix": pd.DataFrame([{"sector_label": "Professional", "share_value": 0.12, "raw_value": 54000, "year": 2024, "source": "qcew"}]),
                "gdp_mix": pd.DataFrame([{"sector_label": "Professional", "share_value": 0.14, "raw_value": 1200000000, "year": 2024, "source": "bea"}]),
            },
            "housing_context": pd.DataFrame([{"year": 2023, "zhvi_annual_avg": 310000, "zori_annual_avg": 1850, "hpi_yoy_pct": 0.06, "zori_annual_avg_yoy_pct": 0.04}]),
            "candidate_note": "Reusable market summary candidate.",
        },
    )
    module.render_page("synthetic.yaml")

    monkeypatch.setattr(
        module,
        "load_market_payload",
        lambda _: {"industry_context": {"employment_mix": pd.DataFrame(), "gdp_mix": pd.DataFrame()}, "housing_context": pd.DataFrame(), "candidate_note": "Reusable market summary candidate."},
    )
    module.render_page("synthetic.yaml")


def test_d6_methods_page_handles_populated_and_incomplete_payloads(monkeypatch, dummy_streamlit, base_payload):
    module = _load_page_module("d_methods.py")
    _patch_common(monkeypatch, module, dummy_streamlit)
    monkeypatch.setattr(module, "load_site_base_payload", lambda _: base_payload)
    monkeypatch.setattr(
        module,
        "load_d2_payload",
        lambda _: {
            "skip_reasons": pd.DataFrame([{"metric": "median_hh_income", "reason": "No tract rows", "table_name": "economics_income_wide"}]),
            "catchment_profile": pd.DataFrame([{"metric_label": "Population", "year": 2024, "source_table": "population_demographics"}]),
        },
    )
    module.render_page("synthetic.yaml")

    monkeypatch.setattr(module, "load_d2_payload", lambda _: {"skip_reasons": pd.DataFrame(), "catchment_profile": pd.DataFrame()})
    module.render_page("synthetic.yaml")
