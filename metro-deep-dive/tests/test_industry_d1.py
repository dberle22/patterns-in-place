"""Smoke tests for Metro Area Explorer Industry D1."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "metro-area-explorer"
    / "industry"
    / "data_prep.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("industry_d1_data_prep", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def d1():
    return _load_module()


@pytest.fixture(scope="module")
def richmond_surface(d1):
    return d1.get_d1_surface("40060")


def test_richmond_surface_has_expected_latest_years(d1, richmond_surface):
    assert d1.get_latest_year(richmond_surface, "employment_share") == 2024
    assert d1.get_latest_year(richmond_surface, "gdp_share") == 2023


def test_share_values_sum_to_one_within_basis_and_year(richmond_surface):
    grouped = (
        richmond_surface.groupby(["basis", "year"], as_index=False)["share_value"]
        .sum()
        .sort_values(["basis", "year"])
    )
    for _, row in grouped.iterrows():
        assert row["share_value"] == pytest.approx(1.0, abs=0.02)


def test_current_mix_chart_renders_for_both_bases(d1, richmond_surface):
    employment_chart = d1.build_current_mix_chart(richmond_surface, "employment_share", 2024)
    gdp_chart = d1.build_current_mix_chart(richmond_surface, "gdp_share", 2023)

    assert employment_chart is not None
    assert gdp_chart is not None
    assert employment_chart.chart is not None
    assert gdp_chart.chart is not None


def test_bump_chart_renders_when_history_is_sufficient(d1, richmond_surface):
    assert d1.has_sufficient_bump_history(richmond_surface, "employment_share")
    assert d1.has_sufficient_bump_history(richmond_surface, "gdp_share")

    employment_chart = d1.build_change_chart(richmond_surface, "employment_share")
    gdp_chart = d1.build_change_chart(richmond_surface, "gdp_share")

    assert employment_chart is not None
    assert gdp_chart is not None
    assert employment_chart.chart is not None
    assert gdp_chart.chart is not None


def test_takeaway_is_generated_from_measured_deltas(d1, richmond_surface):
    takeaway = d1.get_takeaway(richmond_surface, "employment_share")
    assert takeaway is not None
    assert "gained the most share" in takeaway
    assert "lost the most" in takeaway


def test_benchmark_frames_and_table_build(d1):
    frames = d1.get_d1_basis_frames("40060")
    benchmarks = d1.get_benchmark_basis_frames("40060")
    employment_rows = frames["employment_share"]
    benchmark_rows = benchmarks["employment_share"]
    table = d1.build_benchmark_table_for_basis_rows(employment_rows, benchmark_rows, 2024)

    assert not benchmark_rows["us"].empty
    assert not benchmark_rows["division"].empty
    assert not table.empty
    assert {"market_share", "us_share", "division_share", "us_delta", "division_delta"} <= set(table.columns)


def test_specialization_payload_uses_scatter_mode_for_richmond(d1):
    payload = d1.get_d1_specialization_payload("40060")

    assert payload["mode"] == "scatter"
    assert payload["latest_lq_year"] == 2024
    assert payload["growth_year_start"] == 2023
    assert payload["growth_year_end"] == 2024
    assert not payload["rows"].empty
    assert {"sector_id", "sector_label", "lq_value", "growth_value", "latest_share"} <= set(payload["rows"].columns)
    assert payload["rows"]["growth_value"].notna().any()


def test_specialization_payload_falls_back_to_ranked_table_without_growth_pair(d1):
    market_rows = d1.get_market_surface("40060").copy()
    market_rows["qcew_private_emp_total"] = None

    for sector_id, _ in d1.EMPLOYMENT_SECTORS:
        market_rows[f"qcew_private_emp_{sector_id}"] = None

    payload = d1.build_d1_specialization_payload_from_market_rows(
        market_rows,
        market_id="40060",
    )

    assert payload["mode"] == "table"
    assert payload["latest_lq_year"] == 2024
    assert payload["growth_year_start"] is None
    assert payload["growth_year_end"] is None
    assert not payload["rows"].empty
    assert payload["rows"]["growth_value"].isna().all()
