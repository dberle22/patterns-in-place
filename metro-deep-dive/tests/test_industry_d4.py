"""Smoke tests for Metro Area Explorer Industry D4 cache-backed overlays."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import duckdb
import pandas as pd
import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "metro-area-explorer"
    / "industry"
    / "data_prep.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("industry_d4_data_prep", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_parquet(df: pd.DataFrame, path: Path) -> None:
    con = duckdb.connect()
    try:
        con.register("frame", df)
        escaped_path = str(path).replace("'", "''")
        con.execute(f"COPY frame TO '{escaped_path}' (FORMAT PARQUET)")
    finally:
        con.close()


@pytest.fixture(scope="module")
def d4():
    return _load_module()


def test_d4_overlay_reads_cached_layers(monkeypatch, tmp_path, d4):
    market_dir = tmp_path / "40060"
    market_dir.mkdir(parents=True)
    monkeypatch.setattr(d4, "SPATIAL_OUTPUTS_ROOT", tmp_path)
    monkeypatch.setattr(
        d4,
        "get_d4_base_map_payload",
        lambda market_id, base_surface, selected_sector: {
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[-77.5, 37.5], [-77.4, 37.5], [-77.4, 37.6], [-77.5, 37.6], [-77.5, 37.5]]],
                    },
                    "properties": {"fill_color": [10, 20, 30, 40]},
                }
            ],
            "rows": pd.DataFrame(
                [
                    {
                        "tract_geoid": "51087200100",
                        "tract_name": "Core Tract",
                        "centroid_lat": 37.55,
                        "centroid_lon": -77.45,
                        "pop_total": 5000,
                    }
                ]
            ),
            "view_state": {"latitude": 37.55, "longitude": -77.45, "zoom": 9.0},
            "title": "Total workplace jobs by tract",
            "subtitle": "Latest LODES tract workplace jobs (2024)",
            "base_surface": base_surface,
        },
    )
    monkeypatch.setattr(
        d4,
        "_build_job_center_markers",
        lambda market_id, top_n, selected_sector: pd.DataFrame(
            [
                {
                    "tract_geoid": "51087200100",
                    "tract_name": "Core Tract",
                    "centroid_lat": 37.55,
                    "centroid_lon": -77.45,
                    "jobs_total": 12000,
                    "dominant_sector_label": "Professional Services",
                    "label": "Core Tract",
                    "metric": "12,000",
                }
            ]
        ),
    )
    monkeypatch.setattr(
        d4,
        "get_d3_job_center_shortlist",
        lambda market_id, min_jobs_total, selected_sector, top_n: pd.DataFrame(
            [
                {
                    "tract_geoid": "51087200100",
                    "tract_name": "Core Tract",
                    "dominant_sector_id": "professional",
                    "dominant_sector_label": "Professional Services",
                    "jobs_total": 12000,
                    "jobs_to_workers_ratio": 1.8,
                    "centroid_lat": 37.55,
                    "centroid_lon": -77.45,
                    "selected_sector_label": "Professional Services",
                    "selected_sector_jobs": 5000,
                    "selected_sector_share": 0.42,
                    "shortlist_rank": 1,
                    "shortlist_basis": "largest_job_centers",
                    "shortlist_note": "Synthetic shortlist note.",
                }
            ]
        ),
    )

    line_rows = pd.DataFrame(
        [
            {
                "market_id": "40060",
                "source_system": "osm",
                "source_id": "osm:way:1",
                "feature_name": "I-95",
                "layer_group": "highways",
                "category": "infrastructure",
                "subcategory": "highway",
                "geometry_type": "LineString",
                "geometry": json.dumps({"type": "LineString", "coordinates": [[-77.5, 37.5], [-77.4, 37.6]]}),
                "centroid_lat": 37.55,
                "centroid_lon": -77.45,
                "attributes_json": json.dumps({"highway": "motorway"}),
                "extract_date": "2026-07-28T12:00:00+00:00",
            }
        ]
    )
    polygon_rows = pd.DataFrame(
        [
            {
                "market_id": "40060",
                "source_system": "osm",
                "source_id": "osm:way:2",
                "feature_name": "Port Example",
                "layer_group": "ports",
                "category": "infrastructure",
                "subcategory": "port",
                "geometry_type": "Polygon",
                "geometry": json.dumps(
                    {
                        "type": "Polygon",
                        "coordinates": [[[-77.45, 37.52], [-77.44, 37.52], [-77.44, 37.53], [-77.45, 37.53], [-77.45, 37.52]]],
                    }
                ),
                "centroid_lat": 37.525,
                "centroid_lon": -77.445,
                "attributes_json": json.dumps({"landuse": "port"}),
                "extract_date": "2026-07-28T12:00:00+00:00",
            }
        ]
    )
    point_rows = pd.DataFrame(
        [
            {
                "market_id": "40060",
                "source_system": "osm",
                "source_id": "osm:node:3",
                "feature_name": "Warehouse Example",
                "layer_group": "warehouses_logistics",
                "category": "infrastructure",
                "subcategory": "warehouse_logistics",
                "geometry_type": "Point",
                "geometry": json.dumps({"type": "Point", "coordinates": [-77.448, 37.542]}),
                "centroid_lat": 37.542,
                "centroid_lon": -77.448,
                "attributes_json": json.dumps({"building": "warehouse"}),
                "extract_date": "2026-07-28T12:00:00+00:00",
            }
        ]
    )
    overture_rows = pd.DataFrame(
        [
            {
                "market_id": "40060",
                "source_system": "overture",
                "source_id": "overture:place:1",
                "feature_name": "Airport Anchor",
                "layer_group": "overture_pois",
                "category": "infrastructure",
                "subcategory": "airport",
                "geometry_type": "Point",
                "geometry": json.dumps({"type": "Point", "coordinates": [-77.32, 37.51]}),
                "centroid_lat": 37.51,
                "centroid_lon": -77.32,
                "attributes_json": json.dumps({"primary_category": "airport"}),
                "extract_date": "2026-07-28T12:00:00+00:00",
            }
        ]
    )

    _write_parquet(line_rows, market_dir / "osm_infrastructure_lines.parquet")
    _write_parquet(polygon_rows, market_dir / "osm_infrastructure_polygons.parquet")
    _write_parquet(point_rows, market_dir / "osm_infrastructure_points.parquet")
    _write_parquet(overture_rows, market_dir / "overture_pois.parquet")

    manifest = {
        "market_id": "40060",
        "bbox": {"west": -77.9, "south": 37.2, "east": -76.8, "north": 38.0},
        "extract_date": "2026-07-28T12:00:00+00:00",
        "layers": [
            {"source": "osm", "layer_name": "highways", "geometry_type": "lines", "row_count": 1},
            {"source": "overture", "layer_name": "overture_pois", "geometry_type": "mixed", "row_count": 1},
        ],
        "notes": ["Synthetic manifest for D4 cache test."],
    }
    (market_dir / "spatial_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    payload = d4.get_d4_overlay_payload("40060", selected_sector="professional")

    assert payload["manifest"]["market_id"] == "40060"
    assert len(payload["osm_line_features"]) == 1
    assert len(payload["osm_polygon_features"]) == 1
    assert len(payload["osm_point_features"]) == 1
    assert len(payload["overture_pois"]) == 1
    assert payload["base_surface"] == "jobs_total"
    assert payload["interpretation"]["selected_detail"]["tract_name"] == "Core Tract"
    assert payload["interpretation"]["selected_detail"]["highways_count"] == 1
    assert payload["interpretation"]["selected_detail"]["ports_count"] == 1
    assert payload["interpretation"]["selected_detail"]["warehouses_logistics_count"] == 1
    assert payload["interpretation"]["selected_detail"]["interpretation_type"] == "Mixed"
    assert payload["layer_summary"]["row_count"].sum() == 3
    assert payload["base_payload"]["features"]


def test_d4_overlay_handles_missing_cache_gracefully(monkeypatch, tmp_path, d4):
    monkeypatch.setattr(d4, "SPATIAL_OUTPUTS_ROOT", tmp_path)
    monkeypatch.setattr(
        d4,
        "get_d4_base_map_payload",
        lambda market_id, base_surface, selected_sector: {"features": [], "rows": pd.DataFrame(), "view_state": {}},
    )
    monkeypatch.setattr(
        d4,
        "_build_job_center_markers",
        lambda market_id, top_n, selected_sector: pd.DataFrame(),
    )
    monkeypatch.setattr(
        d4,
        "get_d3_job_center_shortlist",
        lambda market_id, min_jobs_total, selected_sector, top_n: pd.DataFrame(),
    )

    payload = d4.get_d4_overlay_payload("40060", selected_sector="professional")

    assert payload["layer_summary"]["row_count"].sum() == 0
    assert payload["notes"]
    assert "No cached OSM or Overture records were found" in " ".join(payload["notes"])
    assert "No D3 shortlist was available for D4 interpretation." in " ".join(payload["notes"])
