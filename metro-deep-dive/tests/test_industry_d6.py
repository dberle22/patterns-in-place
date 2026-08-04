"""Smoke tests for Metro Area Explorer Industry D6."""

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
    spec = importlib.util.spec_from_file_location("industry_d6_data_prep", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def d6():
    return _load_module()


def test_felten_appendices_load_from_section_owned_workbook(d6):
    appendix_a = d6.get_felten_appendix_a()
    appendix_b = d6.get_felten_appendix_b()

    assert not appendix_a.empty
    assert not appendix_b.empty
    assert {"soc_code", "soc_title_felten", "aioe_score"} <= set(appendix_a.columns)
    assert {"industry_code", "industry_title_felten", "aiie_score"} <= set(appendix_b.columns)
    assert appendix_a["soc_code"].iloc[0] == "11-1011"
    assert appendix_b["industry_code"].iloc[0] == "1133"


def test_final_felten_crosswalks_load_from_review_outputs(d6):
    soc_crosswalk = d6.get_felten_soc_crosswalk_final()
    naics_crosswalk = d6.get_felten_naics_crosswalk_final()

    assert not soc_crosswalk.empty
    assert not naics_crosswalk.empty
    assert {"our_soc_code", "felten_soc_code", "match_basis"} <= set(soc_crosswalk.columns)
    assert {"our_naics_code", "felten_naics_code", "match_basis"} <= set(naics_crosswalk.columns)
    assert "manual_override" in set(soc_crosswalk["match_basis"].dropna())
    assert "manual_override" in set(naics_crosswalk["match_basis"].dropna())


def test_d6_sector_payload_builds_from_4digit_qcew_rollup(d6):
    payload = d6.get_d6_sector_scorecard_payload("40060")

    assert payload["selected_year"] == 2024
    assert not payload["scorecard_rows"].empty
    assert not payload["detail_rows"].empty
    assert {"sector_id", "employment_share", "lq_value", "ai_exposure_score"} <= set(payload["scorecard_rows"].columns)
    assert payload["detail_rows"]["industry_code"].str.fullmatch(r"\d{4}").all()
    assert "match_basis" in set(payload["detail_rows"].columns)
    assert payload["coverage"]["matched_share_total"] is not None
    assert payload["coverage"]["matched_share_total"] > 0.75


def test_d6_occupation_payload_builds_from_detailed_oews(d6):
    payload = d6.get_d6_occupation_companion_payload("40060")

    assert payload["selected_year"] == 2025
    assert not payload["detail_rows"].empty
    assert not payload["family_rows"].empty
    assert {"soc_code", "aioe_score", "employment_share", "occupation_bucket_label"} <= set(payload["detail_rows"].columns)
    assert "match_basis" in set(payload["detail_rows"].columns)
    assert payload["coverage"]["matched_share_total"] is not None
    assert payload["coverage"]["matched_share_total"] > 0.75


def test_d6_page_payload_connects_sector_and_d4_context(d6):
    payload = d6.get_d6_page_payload("40060")

    assert "sector_payload" in payload
    assert "occupation_payload" in payload
    assert payload["sector_payload"]["selected_year"] == 2024
    assert payload["occupation_payload"]["selected_year"] == 2025
