"""Smoke tests for Metro Area Explorer Industry D2 map surfaces."""

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
    spec = importlib.util.spec_from_file_location("industry_d2_data_prep", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def d2():
    return _load_module()


def test_tract_payload_builds_for_top_industry_view(d2):
    payload = d2.get_d2_tract_map_payload("40060", mode="top_industry", selected_sector="professional")

    assert payload["features"]
    assert payload["rows"].shape[0] > 0
    assert payload["title"] == "Dominant industry by tract"
    assert {"longitude", "latitude", "zoom"} <= set(payload["view_state"])

    first = payload["features"][0]["properties"]
    assert first["dominant_sector_label"]
    assert first["selected_share_pct"].endswith("%")


def test_tract_payload_builds_for_selected_industry_view(d2):
    payload = d2.get_d2_tract_map_payload("40060", mode="selected_industry", selected_sector="professional")

    assert payload["features"]
    assert "Professional Services" in payload["title"]

    first = payload["features"][0]["properties"]
    assert first["sector_label"] == "Professional Services"
    assert first["selected_share_pct"].endswith("%")


def test_harmonized_tract_shares_are_bounded(d2):
    payload = d2.get_d2_tract_map_payload("40060", mode="selected_industry", selected_sector="professional")
    rows = payload["rows"]

    share_columns = [column for column in rows.columns if column.startswith("d2_share_")]
    for column in share_columns:
        assert rows[column].dropna().between(0, 1).all()


def test_tract_jobs_intensity_fields_are_present_and_non_negative(d2):
    payload = d2.get_d2_tract_map_payload("40060", mode="top_industry", selected_sector="professional")
    rows = payload["rows"]

    assert {"pop_total", "land_area_sqmi", "jobs_per_resident", "jobs_per_sqmi"} <= set(rows.columns)
    assert rows["jobs_per_resident"].dropna().ge(0).all()
    assert rows["jobs_per_sqmi"].dropna().ge(0).all()


def test_county_payload_builds_for_selected_sector(d2):
    payload = d2.get_d2_county_gdp_map_payload("40060", selected_sector="professional")

    assert payload["features"]
    assert payload["rows"].shape[0] > 0
    assert "county GDP share" in payload["title"]

    first = payload["features"][0]["properties"]
    assert first["sector_label"] == "Professional Services"
    assert first["selected_gdp_share_pct"].endswith("%")
