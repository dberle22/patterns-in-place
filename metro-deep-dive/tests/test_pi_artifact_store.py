"""Tests for the Place Intelligence built-artifact contract."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import pandas as pd
import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "metro-area-explorer"
    / "place_intelligence"
    / "artifact_store.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("place_intelligence_artifact_store", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def artifact_store():
    return _load_module()


@pytest.fixture
def synthetic_site(artifact_store):
    return artifact_store.Site(
        site_id="artifact_test_site",
        address="Synthetic address",
        lat=30.0,
        lon=-81.0,
        geocode_source="manual_override",
        market_id="27260",
        asset_type="retail",
        rings_mi=[1, 3, 5],
        primary_ring_mi=3,
    )


def test_build_and_load_site_artifacts_round_trip(tmp_path, monkeypatch, artifact_store, synthetic_site):
    monkeypatch.setattr(artifact_store, "load_site", lambda path: synthetic_site)
    monkeypatch.setattr(artifact_store, "get_site_artifact_dir", lambda site: tmp_path / site.site_id)
    monkeypatch.setattr(
        artifact_store,
        "build_site_base_payload",
        lambda site: {
            "site": site,
            "resolved_site": artifact_store.ResolvedSite(
                site=site,
                lat=30.0,
                lon=-81.0,
                tract_geoid="12031000100",
                matched_address=site.address,
                match_type="manual_override",
                geocode_source="manual_override",
            ),
            "weight_table": pd.DataFrame([{"site_id": site.site_id, "ring_mi": 1, "tract_geoid": "12031000100", "weight": 1.0}]),
            "coverage_diagnostic": pd.DataFrame([{"ring_mi": 1, "reliability_flag": "stable"}]),
            "cumulative_rings": pd.DataFrame(),
        },
    )
    monkeypatch.setattr(
        artifact_store,
        "build_d2_profile_payload",
        lambda site, weight_table: {
            "metric_long": pd.DataFrame(
                [
                    {
                        "site_id": site.site_id,
                        "market_id": site.market_id,
                        "record_type": "catchment",
                        "metric": "pop_total",
                        "metric_label": "Population",
                        "topic": "population",
                        "ring_mi": 3,
                        "benchmark_level": None,
                        "benchmark_geo_id": None,
                        "benchmark_geo_name": None,
                        "value": 1000,
                        "year": 2024,
                        "source_table": "population_demographics",
                        "change_5yr": 50,
                        "change_5yr_period": "2019-2024",
                        "cbsa_percentile": 80.0,
                        "cbsa_percentile_denominator": 152,
                    }
                ]
            ),
            "metric_summary": pd.DataFrame(
                [
                    {
                        "site_id": site.site_id,
                        "market_id": site.market_id,
                        "metric": "pop_total",
                        "metric_label": "Population",
                        "topic": "population",
                        "source_table": "population_demographics",
                        "primary_ring_mi": 3,
                        "primary_value": 1000,
                        "primary_year": 2024,
                        "primary_change_5yr": 50,
                        "primary_change_5yr_period": "2019-2024",
                        "primary_cbsa_percentile": 80.0,
                        "primary_cbsa_percentile_denominator": 152,
                    }
                ]
            ),
            "catchment_profile": pd.DataFrame([{"ring_mi": 3, "metric": "pop_total", "value": 1000}]),
            "benchmark_table": pd.DataFrame([{"metric": "pop_total", "value": 900}]),
            "skip_reasons": pd.DataFrame([{"metric": "median_age", "reason": "missing"}]),
        },
    )
    monkeypatch.setattr(
        artifact_store,
        "get_d3_context_payload",
        lambda site, weight_table: {
            "daytime_population": pd.DataFrame([{"ring_mi": 3, "jobs_total": 500}]),
            "poi_counts": pd.DataFrame([{"ring_mi": 1, "poi_class": "competitive", "count": 3}]),
            "road_context": {"fronting_classes": ["major_roads"]},
            "barrier_summary": pd.DataFrame([{"ring_mi": 3, "summary": "No barrier"}]),
            "ring_variants": {"comparison_table": pd.DataFrame([{"ring_mi": 3, "removed_area_share": 0.0}])},
            "node_typology_label": "Mixed",
            "node_typology_rationale": "Synthetic rationale",
            "copy_note": "Synthetic copy note",
        },
    )
    monkeypatch.setattr(
        artifact_store,
        "get_d4_traffic_payload",
        lambda site, cumulative_rings: {
            "frontage_segments": pd.DataFrame([{"roadway": "A", "aadt": 1000}]),
            "frontage_trend": pd.DataFrame([{"year": 2025, "roadway": "A", "aadt": 1000}]),
            "ranked_segments_1mi": pd.DataFrame([{"roadway": "A", "aadt": 1000}]),
            "count_year": 2025,
            "copy_note": "AADT note",
        },
    )
    monkeypatch.setattr(
        artifact_store,
        "get_d5_flood_payload",
        lambda site, weight_table, cumulative_rings: {
            "nri_catchment_scores": pd.DataFrame([{"ring_mi": 3, "risk_score": 12.0}]),
            "nri_catchment_top_hazards": pd.DataFrame([{"hazard_label": "Flood"}]),
            "nri_cbsa_benchmark": pd.DataFrame([{"risk_score": 10.0}]),
            "nri_cbsa_top_hazards": pd.DataFrame([{"hazard_label": "Flood"}]),
            "nfhl_site_zone": pd.DataFrame([{"flood_zone": "X"}]),
            "nfhl_ring_shares": pd.DataFrame([{"ring_mi": 1, "flood_zone": "X", "area_share": 0.8}]),
            "nfhl_service_status": "ok",
            "nfhl_service_error": None,
            "copy_note": "Flood note",
        },
    )
    monkeypatch.setattr(
        artifact_store,
        "build_market_context_payload",
        lambda site: {
            "industry_context": {
                "employment_mix": pd.DataFrame([{"sector_label": "Professional", "share_value": 0.1}]),
                "gdp_mix": pd.DataFrame([{"sector_label": "Professional", "share_value": 0.2}]),
            },
            "housing_context": pd.DataFrame([{"year": 2025, "zhvi_annual_avg": 300000}]),
            "candidate_note": "Market note",
        },
    )
    monkeypatch.setattr(
        artifact_store,
        "build_context_map_payload",
        lambda site, weight_table, fill_metric, include_flood_context=True: {
            "site_point": [{"name": site.address, "lat": site.lat, "lon": site.lon}],
            "view_state": {"latitude": site.lat, "longitude": site.lon, "zoom": 10.0},
            "available_fill_metrics": artifact_store.D6_TRACT_FILL_METRICS,
            "tract_fill": {
                "features": [{"type": "Feature", "geometry": None, "properties": {"metric_label": fill_metric}}],
                "year": 2025,
                "source_table": "synthetic_table",
            },
            "rings_geojson": {"type": "FeatureCollection", "features": []},
            "water_adjusted_rings_geojson": {"type": "FeatureCollection", "features": []},
            "severed_area_geojson": {"type": "FeatureCollection", "features": []},
            "poi_rows": pd.DataFrame([{"name": "POI", "poi_class": "competitive", "lon": -81.0, "lat": 30.0}]),
            "road_geojson": {"type": "FeatureCollection", "features": []},
            "flood_geojson": {"type": "FeatureCollection", "features": []},
            "barrier_summary": pd.DataFrame([{"ring_mi": 3, "summary": "No barrier"}]),
            "nfhl_service_status": "ok",
            "nfhl_service_error": None,
        },
    )
    monkeypatch.setattr(
        artifact_store,
        "build_context_tract_fill",
        lambda site, metric: {
            "features": [{"type": "Feature", "geometry": None, "properties": {"metric_label": metric}}],
            "metric": metric,
            "metric_label": artifact_store.D6_TRACT_FILL_METRICS[metric],
            "year": 2025,
            "source_table": "synthetic_table",
        },
    )

    artifact_dir = artifact_store.build_site_artifacts("synthetic.yaml")
    assert (artifact_dir / "manifest.json").exists()
    assert (artifact_dir / "base_weight_table.csv").exists()
    assert (artifact_dir / "d2_metric_long.csv").exists()
    assert (artifact_dir / "d2_metric_summary.csv").exists()
    assert (artifact_dir / "d2_catchment_profile.csv").exists()
    assert (artifact_dir / "d3_road_context.json").exists()
    assert (artifact_dir / "map" / "tract_fill_pop_total.geojson").exists()
    assert (artifact_dir / "map" / "poi_rows.csv").exists()

    base = artifact_store.load_artifact_base_payload("synthetic.yaml")
    d2 = artifact_store.load_artifact_d2_payload("synthetic.yaml")
    d3 = artifact_store.load_artifact_d3_payload("synthetic.yaml")
    d4 = artifact_store.load_artifact_d4_payload("synthetic.yaml")
    d5 = artifact_store.load_artifact_d5_payload("synthetic.yaml")
    market = artifact_store.load_artifact_market_payload("synthetic.yaml")
    context = artifact_store.load_artifact_context_map_payload("synthetic.yaml", "pop_total", include_flood_context=False)

    assert base["site"].site_id == "artifact_test_site"
    assert base["resolved_site"].tract_geoid == "12031000100"
    assert not d2["metric_long"].empty
    assert not d2["metric_summary"].empty
    assert not d2["catchment_profile"].empty
    assert d3["node_typology_label"] == "Mixed"
    assert d4["count_year"] == 2025
    assert d5["nfhl_service_status"] == "ok"
    assert market["candidate_note"] == "Market note"
    assert context["tract_fill"]["metric_label"] == artifact_store.D6_TRACT_FILL_METRICS["pop_total"]

    manifest = artifact_store._read_json(artifact_dir / "manifest.json")
    assert "step_timings_seconds" in manifest
    assert "context_map_artifacts" in manifest["step_timings_seconds"]
