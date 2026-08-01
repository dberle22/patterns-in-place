"""Tests for Place Intelligence D5 flood-risk helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Polygon


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "metro-area-explorer"
    / "place_intelligence"
    / "site_prep.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("place_intelligence_site_prep_d5", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def pi_d5():
    return _load_module()


@pytest.fixture
def synthetic_site(pi_d5):
    return pi_d5.Site(
        site_id="flood_test_site",
        address="Synthetic",
        lat=30.0,
        lon=-81.0,
        geocode_source="manual_override",
        market_id="27260",
        asset_type="retail",
        rings_mi=[1, 3, 5],
        primary_ring_mi=3,
    )


@pytest.fixture
def synthetic_weight_table():
    return pd.DataFrame(
        [
            {
                "site_id": "flood_test_site",
                "ring_mi": 1,
                "tract_geoid": "12031000100",
                "weight": 0.4,
                "weight_method": "areal",
                "intersect_area": 1.0,
                "tract_area": 2.5,
                "containment": "fragment",
                "centroid_in": False,
            },
            {
                "site_id": "flood_test_site",
                "ring_mi": 1,
                "tract_geoid": "12031000200",
                "weight": 0.1,
                "weight_method": "areal",
                "intersect_area": 0.3,
                "tract_area": 3.0,
                "containment": "fragment",
                "centroid_in": False,
            },
            {
                "site_id": "flood_test_site",
                "ring_mi": 3,
                "tract_geoid": "12031000100",
                "weight": 0.6,
                "weight_method": "areal",
                "intersect_area": 1.5,
                "tract_area": 2.5,
                "containment": "fragment",
                "centroid_in": True,
            },
            {
                "site_id": "flood_test_site",
                "ring_mi": 3,
                "tract_geoid": "12031000200",
                "weight": 0.4,
                "weight_method": "areal",
                "intersect_area": 1.2,
                "tract_area": 3.0,
                "containment": "fragment",
                "centroid_in": True,
            },
            {
                "site_id": "flood_test_site",
                "ring_mi": 5,
                "tract_geoid": "12031000200",
                "weight": 0.5,
                "weight_method": "areal",
                "intersect_area": 1.5,
                "tract_area": 3.0,
                "containment": "fragment",
                "centroid_in": True,
            },
        ]
    )


def _synthetic_nri_surface() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "geo_level": "tract",
                "geo_id": "12031000100",
                "geo_name": "Tract 1",
                "year": 2025,
                "risk_score": 10.0,
                "eal_score": 11.0,
                "social_vulnerability_score": 20.0,
                "community_resilience_score": 70.0,
                "coastal_flooding_risk_score": 5.0,
                "inland_flooding_risk_score": 15.0,
                "hurricane_risk_score": 12.0,
                "wildfire_risk_score": 3.0,
            },
            {
                "geo_level": "tract",
                "geo_id": "12031000200",
                "geo_name": "Tract 2",
                "year": 2025,
                "risk_score": 30.0,
                "eal_score": 25.0,
                "social_vulnerability_score": 50.0,
                "community_resilience_score": 40.0,
                "coastal_flooding_risk_score": 40.0,
                "inland_flooding_risk_score": 35.0,
                "hurricane_risk_score": 25.0,
                "wildfire_risk_score": 2.0,
            },
            {
                "geo_level": "cbsa",
                "geo_id": "27260",
                "geo_name": "Jacksonville, FL",
                "year": 2025,
                "risk_score": 22.0,
                "eal_score": 24.0,
                "social_vulnerability_score": 47.0,
                "community_resilience_score": 55.0,
                "coastal_flooding_risk_score": 44.0,
                "inland_flooding_risk_score": 41.0,
                "hurricane_risk_score": 38.0,
                "wildfire_risk_score": 4.0,
            },
        ]
    )


def test_build_nri_flood_risk_payload_apportions_cumulative_ring_scores(
    pi_d5,
    synthetic_site,
    synthetic_weight_table,
    monkeypatch,
):
    monkeypatch.setattr(pi_d5, "_query_nri_surface", lambda market_id: _synthetic_nri_surface())

    payload = pi_d5.build_nri_flood_risk_payload(synthetic_site, synthetic_weight_table)
    catchment_scores = payload["catchment_scores"].sort_values("ring_mi").reset_index(drop=True)
    catchment_top_hazards = payload["catchment_top_hazards"]
    cbsa_benchmark = payload["cbsa_benchmark"]

    assert catchment_scores["ring_mi"].tolist() == [1, 3, 5]
    assert catchment_scores["risk_score"].round(3).tolist() == [14.0, 16.667, 20.0]
    assert catchment_scores["inland_flooding_risk_score"].round(3).tolist() == [19.0, 21.667, 25.0]
    assert catchment_top_hazards.loc[catchment_top_hazards["ring_mi"] == 1, "hazard_label"].tolist()[0] == "Inland flooding"
    assert cbsa_benchmark.iloc[0]["geo_name"] == "Jacksonville, FL"
    assert cbsa_benchmark.iloc[0]["coastal_flooding_risk_score"] == 44.0


def test_build_nfhl_ring_share_table_uses_projected_area_shares(pi_d5, synthetic_site):
    cumulative_rings = gpd.GeoDataFrame(
        [
            {"ring_mi": 1, "geometry": Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])},
            {"ring_mi": 3, "geometry": Polygon([(0, 0), (4, 0), (4, 2), (0, 2)])},
        ],
        geometry="geometry",
        crs="EPSG:3857",
    )
    zone_features = gpd.GeoDataFrame(
        [
            {
                "flood_zone": "AE",
                "zone_subtype": "FLOODWAY",
                "sfha_flag": True,
                "geometry": Polygon([(0, 0), (1, 0), (1, 2), (0, 2)]),
            },
            {
                "flood_zone": "X",
                "zone_subtype": "AREA OF MINIMAL FLOOD HAZARD",
                "sfha_flag": False,
                "geometry": Polygon([(1, 0), (4, 0), (4, 2), (1, 2)]),
            },
        ],
        geometry="geometry",
        crs="EPSG:3857",
    )

    shares = pi_d5.build_nfhl_ring_share_table(synthetic_site, cumulative_rings, zone_features=zone_features)

    ring1 = shares.loc[shares["ring_mi"] == 1].sort_values("flood_zone").reset_index(drop=True)
    ring3 = shares.loc[shares["ring_mi"] == 3].sort_values("flood_zone").reset_index(drop=True)
    assert ring1["area_share"].round(3).tolist() == [0.5, 0.5]
    assert ring3["area_share"].round(3).tolist() == [0.25, 0.75]


def test_get_d5_flood_payload_degrades_cleanly_when_nfhl_lookup_fails(
    pi_d5,
    synthetic_site,
    synthetic_weight_table,
    monkeypatch,
):
    monkeypatch.setattr(pi_d5, "_query_nri_surface", lambda market_id: _synthetic_nri_surface())
    monkeypatch.setattr(pi_d5, "lookup_nfhl_site_flood_zone", lambda site: (_ for _ in ()).throw(RuntimeError("NFHL unavailable")))
    monkeypatch.setattr(pi_d5, "build_nfhl_ring_share_table", lambda site, cumulative_rings: (_ for _ in ()).throw(RuntimeError("NFHL unavailable")))

    payload = pi_d5.get_d5_flood_payload(synthetic_site, synthetic_weight_table)

    assert payload["nfhl_service_status"] == "unavailable"
    assert "NFHL unavailable" in payload["nfhl_service_error"]
    assert payload["nfhl_site_zone"].iloc[0]["flood_zone"] is None
    assert payload["nfhl_ring_shares"].empty
    assert "screening-level read" in payload["copy_note"]
