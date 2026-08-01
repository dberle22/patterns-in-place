"""Tests for Place Intelligence D4 traffic-count helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import LineString


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "metro-area-explorer"
    / "place_intelligence"
    / "site_prep.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("place_intelligence_site_prep_d4", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def pi_d4():
    return _load_module()


@pytest.fixture
def synthetic_site(pi_d4):
    return pi_d4.Site(
        site_id="traffic_test_site",
        address="Synthetic",
        lat=30.0,
        lon=-81.0,
        geocode_source="manual_override",
        market_id="27260",
        asset_type="retail",
        rings_mi=[1, 3, 5],
        primary_ring_mi=3,
    )


def _synthetic_segments() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        [
            {
                "source_id": "1",
                "year": 2025,
                "roadway": "A",
                "county": "Duval",
                "aadt": 22000,
                "begin_post": 0.0,
                "end_post": 0.5,
                "desc_frm": "From A",
                "desc_to": "To A",
                "geometry": LineString([(-81.0001, 29.9995), (-81.0001, 30.0005)]),
            },
            {
                "source_id": "2",
                "year": 2025,
                "roadway": "B",
                "county": "Duval",
                "aadt": 14000,
                "begin_post": 0.0,
                "end_post": 0.8,
                "desc_frm": "From B",
                "desc_to": "To B",
                "geometry": LineString([(-81.003, 29.999), (-81.003, 30.001)]),
            },
            {
                "source_id": "3",
                "year": 2025,
                "roadway": "C",
                "county": "Duval",
                "aadt": 7000,
                "begin_post": 0.0,
                "end_post": 0.7,
                "desc_frm": "From C",
                "desc_to": "To C",
                "geometry": LineString([(-81.02, 29.999), (-81.02, 30.001)]),
            },
        ],
        geometry="geometry",
        crs="EPSG:4326",
    )


def test_snap_frontage_aadt_returns_nearest_segments_within_tolerance(pi_d4, synthetic_site):
    result = pi_d4.snap_frontage_aadt(
        synthetic_site,
        segments=_synthetic_segments(),
        target_crs="EPSG:3857",
        snap_tolerance_mi=0.3,
        max_segments=2,
    )

    assert result["source_id"].tolist() == ["1", "2"]
    assert result["aadt"].tolist() == [22000, 14000]
    assert result["distance_mi"].iloc[0] < result["distance_mi"].iloc[1]


def test_snap_frontage_aadt_fails_loudly_when_no_segment_is_close_enough(pi_d4, synthetic_site):
    with pytest.raises(ValueError, match="No FDOT AADT segment was found within"):
        pi_d4.snap_frontage_aadt(
            synthetic_site,
            segments=_synthetic_segments(),
            target_crs="EPSG:3857",
            snap_tolerance_mi=0.001,
            max_segments=1,
        )


def test_rank_aadt_segments_in_ring_orders_by_aadt(pi_d4, synthetic_site):
    cumulative_rings = pi_d4._build_cumulative_rings(synthetic_site.lat, synthetic_site.lon, synthetic_site.rings_mi)
    ranked = pi_d4.rank_aadt_segments_in_ring(
        synthetic_site,
        segments=_synthetic_segments(),
        cumulative_rings=cumulative_rings,
        ring_mi=1,
    )

    assert ranked["source_id"].tolist()[:2] == ["1", "2"]
    assert ranked["aadt"].tolist()[:2] == [22000, 14000]
    assert (ranked["segment_length_mi_in_ring"] > 0).all()


def test_get_d4_traffic_payload_reports_year_and_copy_note(pi_d4, synthetic_site, monkeypatch):
    cumulative_rings = pi_d4._build_cumulative_rings(synthetic_site.lat, synthetic_site.lon, synthetic_site.rings_mi)
    monkeypatch.setattr(pi_d4, "_load_fdot_aadt_segments", lambda market_id: _synthetic_segments())
    monkeypatch.setattr(
        pi_d4,
        "_load_fdot_aadt_historical_segments",
        lambda market_id: gpd.GeoDataFrame(
            [
                {"market_id": market_id, "roadway": "A", "year": 2021, "aadt": 18000, "geometry": LineString([(-81.0001, 29.9995), (-81.0001, 30.0005)])},
                {"market_id": market_id, "roadway": "A", "year": 2025, "aadt": 22000, "geometry": LineString([(-81.0001, 29.9995), (-81.0001, 30.0005)])},
                {"market_id": market_id, "roadway": "B", "year": 2022, "aadt": 12000, "geometry": LineString([(-81.003, 29.999), (-81.003, 30.001)])},
            ],
            geometry="geometry",
            crs="EPSG:4326",
        ),
    )

    payload = pi_d4.get_d4_traffic_payload(
        synthetic_site,
        cumulative_rings=cumulative_rings,
        snap_tolerance_mi=0.3,
        max_frontage_segments=2,
    )

    assert payload["count_year"] == 2025
    assert "annual average daily traffic" in payload["copy_note"]
    assert not payload["frontage_segments"].empty
    assert not payload["frontage_trend"].empty
    assert not payload["ranked_segments_1mi"].empty


def test_build_frontage_aadt_trend_uses_snapped_frontage_roadways(pi_d4, synthetic_site):
    frontage = pd.DataFrame(
        [
            {"market_id": synthetic_site.market_id, "roadway": "A"},
            {"market_id": synthetic_site.market_id, "roadway": "B"},
        ]
    )
    history = gpd.GeoDataFrame(
        [
            {"market_id": synthetic_site.market_id, "roadway": "A", "year": 2021, "aadt": 18000, "geometry": LineString([(-81.0001, 29.9995), (-81.0001, 30.0005)])},
            {"market_id": synthetic_site.market_id, "roadway": "A", "year": 2025, "aadt": 22000, "geometry": LineString([(-81.0001, 29.9995), (-81.0001, 30.0005)])},
            {"market_id": synthetic_site.market_id, "roadway": "A", "year": 2025, "aadt": 21000, "geometry": LineString([(-81.0005, 29.9995), (-81.0005, 30.0005)])},
            {"market_id": synthetic_site.market_id, "roadway": "B", "year": 2022, "aadt": 12000, "geometry": LineString([(-81.003, 29.999), (-81.003, 30.001)])},
            {"market_id": synthetic_site.market_id, "roadway": "Z", "year": 2025, "aadt": 99999, "geometry": LineString([(-81.03, 29.999), (-81.03, 30.001)])},
        ],
        geometry="geometry",
        crs="EPSG:4326",
    )

    trend = pi_d4.build_frontage_aadt_trend(synthetic_site, frontage_segments=frontage, historical_segments=history)

    assert trend["roadway"].tolist() == ["A", "A"]
    assert trend["year"].tolist() == [2021, 2025]
    assert trend["aadt"].tolist() == [18000.0, 22000.0]
    assert trend["series_role"].tolist() == ["primary_frontage", "primary_frontage"]
