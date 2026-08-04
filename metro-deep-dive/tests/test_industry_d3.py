"""Smoke tests for Metro Area Explorer Industry D3."""

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
    spec = importlib.util.spec_from_file_location("industry_d3_data_prep", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def d3():
    return _load_module()


def test_cbsa_summary_builds_for_richmond(d3):
    summary = d3.get_d3_cbsa_summary("40060")

    assert summary
    assert summary["market_id"] == "40060"
    assert summary["jobs_total"] >= 0
    assert summary["workers_total"] >= 0
    assert summary["jobs_to_workers_ratio"] > 0


def test_tract_job_centers_respect_minimum_jobs_floor(d3):
    payload = d3.get_d3_tract_job_centers("40060", min_jobs_total=2500, selected_sector="professional")

    assert not payload["all_rows"].empty
    assert not payload["top_jobs"].empty
    assert payload["top_jobs"]["jobs_total"].ge(2500).all()
    assert payload["top_ratio"]["jobs_total"].ge(2500).all()


def test_selected_sector_job_center_surface_builds(d3):
    payload = d3.get_d3_tract_job_centers("40060", min_jobs_total=2500, selected_sector="professional")
    rows = payload["top_selected_sector"]
    share_column = payload["selected_sector_share_column"]
    jobs_column = payload["selected_sector_jobs_column"]

    assert not rows.empty
    assert rows[jobs_column].dropna().ge(0).all()
    assert rows[share_column].dropna().between(0, 1).all()


def test_industry_imbalance_surface_contains_share_gaps(d3):
    rows = d3.get_d3_industry_imbalance("40060")

    assert not rows.empty
    assert {"industry_label", "jobs_total", "workers_total", "share_gap"} <= set(rows.columns)
    assert rows["share_gap"].notna().any()
    assert rows["share_gap"].gt(0).any()
    assert rows["share_gap"].lt(0).any()


def test_d3_map_payload_builds_for_top_job_centers(d3):
    payload = d3.get_d3_map_payload("40060", min_jobs_total=2500, selected_sector="professional", mode="top_jobs")

    assert payload["features"]
    assert not payload["highlight_rows"].empty
    assert payload["title"] == "Largest tract job centers"
    assert {"longitude", "latitude", "zoom"} <= set(payload["view_state"])

    first = payload["features"][0]["properties"]
    assert first["tract_name"]
    assert first["jobs_total"]
    assert "fill_color" in first
