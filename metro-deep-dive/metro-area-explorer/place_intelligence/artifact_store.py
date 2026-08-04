"""Read-only artifact accessors for the Place Intelligence app."""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Any

import pandas as pd


SECTION_ROOT = Path(__file__).resolve().parent
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import (
    deserialize_resolved_site,
    deserialize_site,
    get_site_artifact_dir,
    read_dataframe,
    read_json,
)
from site_prep import D6_TRACT_FILL_METRICS, Site, load_site


CLOUD_BUNDLE_DIRNAME = "cloud_bundle"
PUBLISHED_SITE_ARTIFACTS_DIRNAME = "site_artifacts"


def build_site_artifacts(site_config_path: str) -> Path:
    """Compatibility wrapper that delegates full builds to the new data-build package."""

    from data_builds.build_all import build_all_for_site

    return build_all_for_site(site_config_path)


def artifacts_exist(site_config_path: str) -> bool:
    """Return whether the full app-facing artifact bundle exists for one site."""

    site = load_site(site_config_path)
    return (_resolve_artifact_dir(site) / "manifest.json").exists()


def load_artifact_base_payload(site_config_path: str) -> dict[str, Any]:
    """Load the built base payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    built_site = deserialize_site(read_json(artifact_dir / "site.json"))
    return {
        "site": built_site,
        "resolved_site": deserialize_resolved_site(read_json(artifact_dir / "resolved_site.json"), built_site),
        "weight_table": read_dataframe(artifact_dir / "base_weight_table.csv"),
        "coverage_diagnostic": read_dataframe(artifact_dir / "base_coverage_diagnostic.csv"),
    }


def load_artifact_overview_payload(site_config_path: str) -> dict[str, Any]:
    """Load the compact Overview-page payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    return read_json(artifact_dir / "overview.json")


def load_artifact_people_payload(site_config_path: str) -> dict[str, Any]:
    """Load the compact People-page payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    return read_json(artifact_dir / "people.json")


def load_artifact_place_payload(site_config_path: str) -> dict[str, Any]:
    """Load the compact Place-page payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    return read_json(artifact_dir / "place.json")


def load_artifact_market_page_payload(site_config_path: str) -> dict[str, Any]:
    """Load the compact Market-page payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    return read_json(artifact_dir / "market_page.json")


def load_artifact_methods_payload(site_config_path: str) -> dict[str, Any]:
    """Load the compact Methods-page payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    return read_json(artifact_dir / "methods.json")


def load_artifact_d2_payload(site_config_path: str) -> dict[str, Any]:
    """Load the built D2 payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    return {
        "metric_long": read_dataframe(artifact_dir / "d2_metric_long.csv"),
        "metric_summary": read_dataframe(artifact_dir / "d2_metric_summary.csv"),
        "catchment_profile": read_dataframe(artifact_dir / "d2_catchment_profile.csv"),
        "benchmark_table": read_dataframe(artifact_dir / "d2_benchmark_table.csv"),
        "skip_reasons": read_dataframe(artifact_dir / "d2_skip_reasons.csv"),
    }


def load_artifact_d3_payload(site_config_path: str) -> dict[str, Any]:
    """Load the built D3 payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    meta = read_json(artifact_dir / "d3_meta.json")
    return {
        "daytime_population": read_dataframe(artifact_dir / "d3_daytime_population.csv"),
        "poi_counts": read_dataframe(artifact_dir / "d3_poi_counts.csv"),
        "road_context": read_json(artifact_dir / "d3_road_context.json"),
        "barrier_summary": read_dataframe(artifact_dir / "d3_barrier_summary.csv"),
        "ring_variants": {
            "comparison_table": read_dataframe(artifact_dir / "d3_ring_variants_comparison.csv"),
        },
        "node_typology_label": meta["node_typology_label"],
        "node_typology_rationale": meta["node_typology_rationale"],
        "copy_note": meta["copy_note"],
    }


def load_artifact_d4_payload(site_config_path: str) -> dict[str, Any]:
    """Load the built D4 payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    meta = read_json(artifact_dir / "d4_meta.json")
    return {
        "frontage_segments": read_dataframe(artifact_dir / "d4_frontage_segments.csv"),
        "frontage_trend": read_dataframe(artifact_dir / "d4_frontage_trend.csv"),
        "ranked_segments_1mi": read_dataframe(artifact_dir / "d4_ranked_segments_1mi.csv"),
        "count_year": meta["count_year"],
        "copy_note": meta["copy_note"],
    }


def load_artifact_d5_payload(site_config_path: str) -> dict[str, Any]:
    """Load the built D5 payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    meta = read_json(artifact_dir / "d5_meta.json")
    return {
        "nri_catchment_scores": read_dataframe(artifact_dir / "d5_nri_catchment_scores.csv"),
        "nri_catchment_top_hazards": read_dataframe(artifact_dir / "d5_nri_catchment_top_hazards.csv"),
        "nri_cbsa_benchmark": read_dataframe(artifact_dir / "d5_nri_cbsa_benchmark.csv"),
        "nri_cbsa_top_hazards": read_dataframe(artifact_dir / "d5_nri_cbsa_top_hazards.csv"),
        "nfhl_site_zone": read_dataframe(artifact_dir / "d5_nfhl_site_zone.csv"),
        "nfhl_ring_shares": read_dataframe(artifact_dir / "d5_nfhl_ring_shares.csv"),
        "nfhl_service_status": meta["nfhl_service_status"],
        "nfhl_service_error": meta["nfhl_service_error"],
        "copy_note": meta["copy_note"],
    }


def load_artifact_market_payload(site_config_path: str) -> dict[str, Any]:
    """Load the built Market-tab payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    meta = read_json(artifact_dir / "market_meta.json")
    return {
        "industry_context": {
            "employment_mix": read_dataframe(artifact_dir / "market_employment_mix.csv"),
            "gdp_mix": read_dataframe(artifact_dir / "market_gdp_mix.csv"),
        },
        "housing_context": read_dataframe(artifact_dir / "market_housing_context.csv"),
        "candidate_note": meta["candidate_note"],
    }


def load_artifact_context_map_payload(
    site_config_path: str,
    fill_metric: str,
    include_flood_context: bool,
) -> dict[str, Any]:
    """Load the built D6 context-map payload for one metric and flood setting."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    map_dir = artifact_dir / "map"
    meta = read_json(map_dir / "meta.json")
    return {
        "site_point": meta["site_point"],
        "view_state": meta["view_state"],
        "available_fill_metrics": D6_TRACT_FILL_METRICS,
        "tract_fill": {
            "features": read_json(map_dir / f"tract_fill_{fill_metric}.geojson")["features"],
            "metric": fill_metric,
            "metric_label": D6_TRACT_FILL_METRICS[fill_metric],
            "year": meta["tract_fill_years"].get(fill_metric),
            "source_table": meta["tract_fill_sources"].get(fill_metric),
        },
        "rings_geojson": read_json(map_dir / "rings.geojson"),
        "water_adjusted_rings_geojson": read_json(map_dir / "water_adjusted_rings.geojson"),
        "severed_area_geojson": read_json(map_dir / "severed_area.geojson"),
        "poi_rows": read_dataframe(map_dir / "poi_rows.csv"),
        "road_geojson": read_json(map_dir / "roads.geojson"),
        "flood_geojson": read_json(map_dir / "flood.geojson") if include_flood_context else {"type": "FeatureCollection", "features": []},
        "barrier_summary": read_dataframe(artifact_dir / "d3_barrier_summary.csv"),
        "nfhl_service_status": meta["nfhl_service_status"],
        "nfhl_service_error": meta["nfhl_service_error"],
    }


def _require_artifact_dir(site: Site) -> Path:
    """Return one artifact dir or fail with a clear build-step message."""

    artifact_dir = _resolve_artifact_dir(site)
    if not (artifact_dir / "manifest.json").exists():
        raise FileNotFoundError(
            f"Built artifacts were not found for site '{site.site_id}'. "
            "Run a data build from the `data_builds/` folder or materialize a publish-ready `cloud_bundle/` before launching the app."
        )
    return artifact_dir


def _resolve_artifact_dir(site: Site) -> Path:
    """Prefer a publish-ready cloud bundle when present, then fall back to local build outputs."""

    for candidate in _candidate_artifact_dirs(site):
        if (candidate / "manifest.json").exists():
            return candidate
    return _candidate_artifact_dirs(site)[0]


def _candidate_artifact_dirs(site: Site) -> list[Path]:
    """Return read-side artifact locations in precedence order."""

    candidates: list[Path] = []
    env_root = os.environ.get("PLACE_INTELLIGENCE_ARTIFACT_ROOT", "").strip()
    if env_root:
        candidates.append(Path(env_root).expanduser().resolve() / site.site_id)
    candidates.append(SECTION_ROOT / CLOUD_BUNDLE_DIRNAME / PUBLISHED_SITE_ARTIFACTS_DIRNAME / site.site_id)
    candidates.append(get_site_artifact_dir(site))
    return candidates
