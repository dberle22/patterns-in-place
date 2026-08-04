"""Tests for Place Intelligence D3 POI classification and node typing."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import LineString, Point


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
def pi_d3():
    return _load_module()


def test_classify_poi_prefers_anchor_priority_over_lower_priority_matches(pi_d3):
    row = pd.Series(
        {
            "basic_category": "hospital",
            "taxonomy_primary": "grocery_store",
            "taxonomy_hierarchy": ["healthcare", "hospital"],
            "primary_category": "retail",
        }
    )

    assert pi_d3.classify_poi(row) == "anchor"


def test_classify_poi_uses_explicit_allowlists_not_substring_logic(pi_d3):
    row = pd.Series(
        {
            "basic_category": "food_and_beverage_store",
            "taxonomy_primary": "supermarket",
            "taxonomy_hierarchy": ["retail", "groceries"],
            "primary_category": "store",
        }
    )

    assert pi_d3.classify_poi(row) == "complementary"


def test_classify_poi_returns_none_for_unclassified_long_tail(pi_d3):
    row = pd.Series(
        {
            "basic_category": "pet_service",
            "taxonomy_primary": "animal_boarding_service",
            "taxonomy_hierarchy": ["services"],
            "primary_category": "pet_service",
        }
    )

    assert pi_d3.classify_poi(row) is None


def test_classify_node_typology_mirrors_industry_heuristic(pi_d3):
    label, rationale = pi_d3.classify_node_typology(
        pd.Series(
            {
                "highways_present": True,
                "rail_present": True,
                "airports_present": False,
                "ports_present": False,
                "warehouses_logistics_count": 2,
                "hospitals_count": 0,
                "universities_count": 0,
                "schools_count": 0,
                "dominant_sector_id": "transport_util",
            }
        )
    )

    assert label == "Infrastructure / logistics-led"
    assert "freight-oriented" in rationale


def test_compute_crossing_spacing_reports_mean_gap_for_synthetic_crossings(pi_d3):
    barrier = LineString([(0, 0), (1609.344 * 3, 0)])
    crossing_network = gpd.GeoDataFrame(
        {"geometry": [LineString([(0, -5), (0, 5)]), LineString([(1609.344 * 2, -5), (1609.344 * 2, 5)])]},
        geometry="geometry",
        crs="EPSG:3857",
    )

    crossing_count, spacing_mi = pi_d3._compute_crossing_spacing(barrier, "water", crossing_network)

    assert crossing_count == 2
    assert spacing_mi == pytest.approx(2.0, rel=1e-3)


def test_compute_barrier_flags_returns_empty_frame_when_no_spatial_barriers(pi_d3, monkeypatch):
    site = pi_d3.Site(
        site_id="synthetic_site",
        address="Synthetic",
        lat=30.0,
        lon=-81.0,
        geocode_source="manual_override",
        market_id="27260",
        asset_type="retail",
        rings_mi=[1],
        primary_ring_mi=1,
    )
    cumulative_rings = gpd.GeoDataFrame(
        [{"ring_mi": 1, "geometry": Point(0, 0).buffer(1609.344)}],
        geometry="geometry",
        crs="EPSG:3857",
    )
    empty = gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326")

    monkeypatch.setattr(pi_d3, "_load_osm_lines", lambda market_id: empty)
    monkeypatch.setattr(pi_d3, "_load_osm_polygons", lambda market_id: empty)

    result = pi_d3.compute_barrier_flags(site, pd.DataFrame(), cumulative_rings)

    assert result.empty
    assert list(result.columns) == [
        "site_id",
        "ring_mi",
        "barrier_type",
        "feature_name",
        "crossing_count",
        "mean_crossing_spacing_mi",
        "severed_area_share",
        "severed_population_share",
        "qualified_barrier",
        "site_card_flag",
        "summary",
    ]


def test_build_daytime_population_payload_includes_ratio_and_absolute_counts(pi_d3, monkeypatch):
    site = pi_d3.Site(
        site_id="synthetic_site",
        address="Synthetic",
        lat=30.0,
        lon=-81.0,
        geocode_source="manual_override",
        market_id="27260",
        asset_type="retail",
        rings_mi=[1, 3],
        primary_ring_mi=1,
    )

    monkeypatch.setattr(
        pi_d3,
        "_query_lodes_surface",
        lambda market_id: pd.DataFrame(
            {
                "tract_geoid": ["1", "2"],
                "year": [2024, 2024],
                "jobs_total": [100.0, 50.0],
                "jobs_ind_retail": [20.0, 10.0],
                "jobs_ind_accommodation_food": [5.0, 2.0],
                "jobs_ind_health_care_social_assistance": [7.0, 3.0],
                "jobs_ind_professional_scientific_technical": [11.0, 4.0],
                "workers_total": [80.0, 40.0],
            }
        ),
    )

    apportioned = {
        "jobs_total": pd.Series([100.0, 40.0], index=[1, 3]),
        "workers_total": pd.Series([80.0, 20.0], index=[1, 3]),
        "jobs_ind_retail": pd.Series([20.0, 5.0], index=[1, 3]),
        "jobs_ind_accommodation_food": pd.Series([5.0, 2.0], index=[1, 3]),
        "jobs_ind_health_care_social_assistance": pd.Series([7.0, 1.0], index=[1, 3]),
        "jobs_ind_professional_scientific_technical": pd.Series([11.0, 4.0], index=[1, 3]),
    }
    monkeypatch.setattr(pi_d3, "_apportion_metric_series", lambda metric, kind, metric_series, weight_table: apportioned[metric])

    payload = pi_d3.build_daytime_population_payload(site, pd.DataFrame())

    first_ring = payload.loc[payload["ring_mi"] == 1].iloc[0]
    third_ring = payload.loc[payload["ring_mi"] == 3].iloc[0]
    assert first_ring["jobs_total"] == pytest.approx(100.0)
    assert first_ring["workers_total"] == pytest.approx(80.0)
    assert first_ring["jobs_to_workers_ratio"] == pytest.approx(1.25)
    assert first_ring["daytime_net_change"] == pytest.approx(20.0)
    assert third_ring["jobs_total"] == pytest.approx(140.0)
    assert third_ring["workers_total"] == pytest.approx(100.0)
    assert third_ring["jobs_to_workers_ratio"] == pytest.approx(1.4)


def test_build_ring_variants_keeps_baseline_and_trims_water_severed_area(pi_d3, monkeypatch):
    site = pi_d3.Site(
        site_id="synthetic_site",
        address="Synthetic",
        lat=30.0,
        lon=-81.0,
        geocode_source="manual_override",
        market_id="27260",
        asset_type="retail",
        rings_mi=[1],
        primary_ring_mi=1,
    )
    ring_geom = Point(0, 0).buffer(1609.344)
    cumulative_rings = gpd.GeoDataFrame(
        [{"ring_mi": 1, "geometry": ring_geom}],
        geometry="geometry",
        crs="EPSG:3857",
    )
    barrier_summary = pd.DataFrame(
        [
            {
                "site_id": site.site_id,
                "ring_mi": 1,
                "barrier_type": "water",
                "feature_name": "Synthetic River",
                "qualified_barrier": True,
            }
        ]
    )
    water_line = LineString([(200, -2000), (200, 2000)])
    barrier_frame = gpd.GeoDataFrame(
        [{"barrier_type": "water", "feature_name": "Synthetic River", "geometry": water_line}],
        geometry="geometry",
        crs="EPSG:3857",
    )

    monkeypatch.setattr(pi_d3, "_load_osm_lines", lambda market_id: gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326"))
    monkeypatch.setattr(pi_d3, "_load_osm_polygons", lambda market_id: gpd.GeoDataFrame(columns=["geometry"], geometry="geometry", crs="EPSG:4326"))
    monkeypatch.setattr(pi_d3, "_prepare_barrier_features", lambda lines, polygons, target_crs: barrier_frame)

    variants = pi_d3.build_ring_variants(site, pd.DataFrame(), cumulative_rings, barrier_summary)
    comparison = variants["comparison_table"].iloc[0]
    baseline = variants["baseline_rings"].iloc[0].geometry
    adjusted = variants["water_adjusted_rings"].iloc[0].geometry

    assert adjusted.area < baseline.area
    assert bool(comparison["has_water_adjustment"]) is True
    assert comparison["removed_area_share"] > 0
    assert comparison["removed_water_features"] == ["Synthetic River"]
