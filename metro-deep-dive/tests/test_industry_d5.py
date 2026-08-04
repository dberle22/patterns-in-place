"""Smoke tests for Metro Area Explorer Industry D5."""

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
    spec = importlib.util.spec_from_file_location("industry_d5_data_prep", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def d5():
    return _load_module()


def test_d5_default_peers_resolve_from_cross_frame_mart(d5):
    peers = d5.get_d5_peer_defaults("40060", peer_count=5)

    assert not peers.empty
    assert len(peers) == 5
    assert {"peer_rank", "peer_market_id", "peer_geo_name", "similarity"} <= set(peers.columns)
    assert peers["peer_rank"].tolist() == [1, 2, 3, 4, 5]
    assert peers["similarity"].dropna().between(0, 1).all()


def test_d5_mix_payload_includes_market_peers_and_benchmarks(d5):
    payload = d5.get_d5_mix_comparison_payload("40060", basis="employment_share")
    chart_rows = payload["chart_rows"]

    assert not chart_rows.empty
    assert payload["selected_year"] == 2024
    assert {"market", "peer", "benchmark"} <= set(chart_rows["entity_type"])
    assert "United States" in set(chart_rows["entity"])
    assert any(entity.startswith("South Atlantic") for entity in chart_rows["entity"].unique())


def test_d5_lodes_surface_uses_its_own_latest_year(d5):
    payload = d5.get_d5_lodes_benchmark_surface("40060")
    rows = payload["rows"]

    assert not rows.empty
    assert payload["selected_year"] == 2023
    assert {"market", "peer", "benchmark"} <= set(rows["entity_type"])
    assert rows.loc[rows["entity_type"] == "market", "jobs_to_workers_ratio"].iloc[0] > 0
    assert "United States" in set(rows["entity"])
    assert "South Atlantic" in set(rows["entity"])


def test_d5_page_payload_builds_for_richmond(d5):
    payload = d5.get_d5_page_payload("40060", basis="employment_share")

    assert payload["mix_payload"]["selected_year"] == 2024
    assert payload["lodes_payload"]["selected_year"] == 2023
    assert payload["takeaway"] is not None
    assert "In 2024" in payload["takeaway"]
    assert "In 2023" in payload["takeaway"]
