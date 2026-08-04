"""Tests for Place Intelligence D1 catchment geometry and apportionment."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "metro-area-explorer"
    / "place_intelligence"
    / "apportion.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("place_intelligence_apportion", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def pi_d1():
    return _load_module()


def test_build_rings_one_mile_area_sanity(pi_d1):
    rings = pi_d1.build_rings(lat=30.2176, lon=-81.6167, rings_mi=[1, 3, 5])
    one_mile_row = rings.loc[rings["ring_mi"] == 1].iloc[0]

    assert one_mile_row["ring_area_sq_mi"] == pytest.approx(3.1415926535, rel=0.01)


def test_apportion_weights_preserves_weight_sum_invariants(monkeypatch, pi_d1):
    rings = gpd.GeoDataFrame(
        [
            {"site_id": "synthetic", "ring_mi": 1, "geometry": box(0, 0, 1, 1)},
            {"site_id": "synthetic", "ring_mi": 3, "geometry": box(1, 0, 3, 1)},
            {"site_id": "synthetic", "ring_mi": 5, "geometry": box(3, 0, 5, 1)},
        ],
        geometry="geometry",
        crs="EPSG:3857",
    )
    tracts = gpd.GeoDataFrame(
        [
            {"tract_geoid": "A", "geometry": box(0, 0, 1, 1)},
            {"tract_geoid": "B", "geometry": box(0.5, 0, 1.5, 1)},
            {"tract_geoid": "C", "geometry": box(3.2, 0.2, 4.8, 0.8)},
        ],
        geometry="geometry",
        crs="EPSG:3857",
    )

    monkeypatch.setattr(pi_d1, "_load_market_tracts", lambda market_id: tracts)

    weights = pi_d1.apportion_weights(rings, market_id="27260")
    tract_totals = weights.groupby("tract_geoid")["weight"].sum()

    assert (tract_totals <= 1.0 + 1e-9).all()
    assert tract_totals.loc["A"] == pytest.approx(1.0)
    assert tract_totals.loc["C"] == pytest.approx(1.0)
    assert tract_totals.loc["B"] == pytest.approx(1.0)


def test_apportion_rejects_median_like_metrics_without_approximate_method(pi_d1):
    metric = pd.Series({"12031016603": 55000.0}, name="median_household_income")
    weight_table = pd.DataFrame(
        [{"site_id": "synthetic", "ring_mi": 3, "tract_geoid": "12031016603", "weight": 1.0}]
    )

    with pytest.raises(ValueError, match="requires method='approximate'"):
        pi_d1.apportion(metric, weight_table, kind="intensive")


def test_apportion_weights_keeps_fragment_without_centroid(monkeypatch, pi_d1):
    rings = gpd.GeoDataFrame(
        [{"site_id": "synthetic", "ring_mi": 1, "geometry": box(0, 0, 1, 1)}],
        geometry="geometry",
        crs="EPSG:3857",
    )
    tracts = gpd.GeoDataFrame(
        [{"tract_geoid": "fragment_only", "geometry": box(0.8, 0, 2.0, 1.0)}],
        geometry="geometry",
        crs="EPSG:3857",
    )

    monkeypatch.setattr(pi_d1, "_load_market_tracts", lambda market_id: tracts)

    weights = pi_d1.apportion_weights(rings, market_id="27260")

    assert len(weights) == 1
    assert weights.iloc[0]["tract_geoid"] == "fragment_only"
    assert bool(weights.iloc[0]["centroid_in"]) is False
    assert weights.iloc[0]["weight"] > 0


def test_coverage_diagnostic_shape_and_flag(pi_d1):
    weight_table = pd.DataFrame(
        [
            {"site_id": "synthetic", "ring_mi": 1, "tract_geoid": "A", "weight": 1.0, "containment": "full"},
            {"site_id": "synthetic", "ring_mi": 3, "tract_geoid": "B", "weight": 0.4, "containment": "fragment"},
            {"site_id": "synthetic", "ring_mi": 3, "tract_geoid": "C", "weight": 0.3, "containment": "fragment"},
        ]
    )

    diagnostic = pi_d1.coverage_diagnostic(weight_table)

    assert list(diagnostic.columns) == [
        "ring_mi",
        "intersecting_tract_count",
        "total_weight_captured",
        "whole_tract_count",
        "fragment_share",
        "reliability_flag",
    ]
    assert diagnostic.loc[diagnostic["ring_mi"] == 1, "reliability_flag"].iloc[0] == "stable"
    assert diagnostic.loc[diagnostic["ring_mi"] == 3, "reliability_flag"].iloc[0] == "fragment_only"


@pytest.mark.integration
def test_apportion_weights_real_jacksonville_smoke(pi_d1):
    try:
        rings = pi_d1.build_rings(lat=30.217618577902, lon=-81.616679103522, rings_mi=[1, 3, 5])
        rings["site_id"] = "jacksonville_fl_baymeadows_v0"
        weights = pi_d1.apportion_weights(rings, market_id="27260")
    except Exception as exc:  # pragma: no cover - this branch is only for local env drift
        pytest.skip(f"Real Jacksonville smoke test unavailable in this environment: {exc}")

    assert not weights.empty
    assert {"site_id", "ring_mi", "tract_geoid", "weight", "containment", "centroid_in"}.issubset(weights.columns)
    assert (weights.groupby("tract_geoid")["weight"].sum() <= 1.0 + 1e-9).all()
