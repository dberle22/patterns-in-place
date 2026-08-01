"""Built-artifact storage for the Place Intelligence app."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from time import perf_counter
from typing import Any

import pandas as pd

SECTION_ROOT = Path(__file__).resolve().parent
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from site_prep import (
    D6_TRACT_FILL_METRICS,
    ResolvedSite,
    Site,
    build_context_map_payload,
    build_context_tract_fill,
    build_market_context_payload,
    build_site_base_payload,
    build_d2_profile_payload,
    get_d3_context_payload,
    get_d4_traffic_payload,
    get_d5_flood_payload,
    get_spatial_output_dir,
    load_site,
)


ARTIFACTS_DIRNAME = "site_artifacts"


def get_site_artifact_dir(site: Site) -> Path:
    """Return the artifact directory for one configured site."""

    return get_spatial_output_dir(site.market_id) / ARTIFACTS_DIRNAME / site.site_id


def build_site_artifacts(site_config_path: str) -> Path:
    """Build and persist all app-facing payloads for one site config."""

    site = load_site(site_config_path)
    artifact_dir = get_site_artifact_dir(site)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    timings: dict[str, float] = {}

    base = _time_logged_step(site.site_id, "base_payload", lambda: build_site_base_payload(site), timings)
    d2_payload = _time_logged_step(site.site_id, "d2_payload", lambda: build_d2_profile_payload(site, base["weight_table"]), timings)
    d3_payload = _time_logged_step(site.site_id, "d3_payload", lambda: get_d3_context_payload(site, base["weight_table"]), timings)
    d4_payload = _time_logged_step(site.site_id, "d4_payload", lambda: get_d4_traffic_payload(site, cumulative_rings=base["cumulative_rings"]), timings)
    d5_payload = _time_logged_step(site.site_id, "d5_payload", lambda: get_d5_flood_payload(site, base["weight_table"], cumulative_rings=base["cumulative_rings"]), timings)
    market_payload = _time_logged_step(site.site_id, "market_payload", lambda: build_market_context_payload(site), timings)

    _write_json(artifact_dir / "site.json", _serialize_site(site))
    _write_json(artifact_dir / "resolved_site.json", _serialize_resolved_site(base["resolved_site"]))

    _write_dataframe(artifact_dir / "base_weight_table.csv", base["weight_table"])
    _write_dataframe(artifact_dir / "base_coverage_diagnostic.csv", base["coverage_diagnostic"])

    _write_dataframe(artifact_dir / "d2_metric_long.csv", d2_payload["metric_long"])
    _write_dataframe(artifact_dir / "d2_metric_summary.csv", d2_payload["metric_summary"])
    _write_dataframe(artifact_dir / "d2_catchment_profile.csv", d2_payload["catchment_profile"])
    _write_dataframe(artifact_dir / "d2_benchmark_table.csv", d2_payload["benchmark_table"])
    _write_dataframe(artifact_dir / "d2_skip_reasons.csv", d2_payload["skip_reasons"])

    _write_dataframe(artifact_dir / "d3_daytime_population.csv", d3_payload["daytime_population"])
    _write_dataframe(artifact_dir / "d3_poi_counts.csv", d3_payload["poi_counts"])
    _write_json(artifact_dir / "d3_road_context.json", d3_payload["road_context"])
    _write_dataframe(artifact_dir / "d3_barrier_summary.csv", d3_payload["barrier_summary"])
    _write_dataframe(artifact_dir / "d3_ring_variants_comparison.csv", d3_payload["ring_variants"]["comparison_table"])
    _write_json(
        artifact_dir / "d3_meta.json",
        {
            "node_typology_label": d3_payload["node_typology_label"],
            "node_typology_rationale": d3_payload["node_typology_rationale"],
            "copy_note": d3_payload["copy_note"],
        },
    )

    _write_dataframe(artifact_dir / "d4_frontage_segments.csv", d4_payload["frontage_segments"])
    _write_dataframe(artifact_dir / "d4_frontage_trend.csv", d4_payload["frontage_trend"])
    _write_dataframe(artifact_dir / "d4_ranked_segments_1mi.csv", d4_payload["ranked_segments_1mi"])
    _write_json(
        artifact_dir / "d4_meta.json",
        {"count_year": d4_payload["count_year"], "copy_note": d4_payload["copy_note"]},
    )

    _write_dataframe(artifact_dir / "d5_nri_catchment_scores.csv", d5_payload["nri_catchment_scores"])
    _write_dataframe(artifact_dir / "d5_nri_catchment_top_hazards.csv", d5_payload["nri_catchment_top_hazards"])
    _write_dataframe(artifact_dir / "d5_nri_cbsa_benchmark.csv", d5_payload["nri_cbsa_benchmark"])
    _write_dataframe(artifact_dir / "d5_nri_cbsa_top_hazards.csv", d5_payload["nri_cbsa_top_hazards"])
    _write_dataframe(artifact_dir / "d5_nfhl_site_zone.csv", d5_payload["nfhl_site_zone"])
    _write_dataframe(artifact_dir / "d5_nfhl_ring_shares.csv", d5_payload["nfhl_ring_shares"])
    _write_json(
        artifact_dir / "d5_meta.json",
        {
            "nfhl_service_status": d5_payload["nfhl_service_status"],
            "nfhl_service_error": d5_payload["nfhl_service_error"],
            "copy_note": d5_payload["copy_note"],
        },
    )

    _write_dataframe(artifact_dir / "market_employment_mix.csv", market_payload["industry_context"]["employment_mix"])
    _write_dataframe(artifact_dir / "market_gdp_mix.csv", market_payload["industry_context"]["gdp_mix"])
    _write_dataframe(artifact_dir / "market_housing_context.csv", market_payload["housing_context"])
    _write_json(artifact_dir / "market_meta.json", {"candidate_note": market_payload["candidate_note"]})

    _time_logged_step(
        site.site_id,
        "context_map_artifacts",
        lambda: _build_context_map_artifacts(site, base["weight_table"], artifact_dir),
        timings,
    )
    _write_json(
        artifact_dir / "manifest.json",
        {
            "site_id": site.site_id,
            "market_id": site.market_id,
            "built_at_utc": datetime.now(timezone.utc).isoformat(),
            "site_config_filename": Path(site_config_path).name,
            "step_timings_seconds": timings,
        },
    )
    return artifact_dir


def artifacts_exist(site_config_path: str) -> bool:
    """Return whether the required built artifacts exist for one site."""

    site = load_site(site_config_path)
    return (get_site_artifact_dir(site) / "manifest.json").exists()


def load_artifact_base_payload(site_config_path: str) -> dict[str, Any]:
    """Load the built base payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    built_site = _deserialize_site(_read_json(artifact_dir / "site.json"))
    return {
        "site": built_site,
        "resolved_site": _deserialize_resolved_site(_read_json(artifact_dir / "resolved_site.json"), built_site),
        "weight_table": _read_dataframe(artifact_dir / "base_weight_table.csv"),
        "coverage_diagnostic": _read_dataframe(artifact_dir / "base_coverage_diagnostic.csv"),
    }


def load_artifact_d2_payload(site_config_path: str) -> dict[str, Any]:
    """Load the built D2 payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    return {
        "metric_long": _read_dataframe(artifact_dir / "d2_metric_long.csv"),
        "metric_summary": _read_dataframe(artifact_dir / "d2_metric_summary.csv"),
        "catchment_profile": _read_dataframe(artifact_dir / "d2_catchment_profile.csv"),
        "benchmark_table": _read_dataframe(artifact_dir / "d2_benchmark_table.csv"),
        "skip_reasons": _read_dataframe(artifact_dir / "d2_skip_reasons.csv"),
    }


def load_artifact_d3_payload(site_config_path: str) -> dict[str, Any]:
    """Load the built D3 payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    meta = _read_json(artifact_dir / "d3_meta.json")
    return {
        "daytime_population": _read_dataframe(artifact_dir / "d3_daytime_population.csv"),
        "poi_counts": _read_dataframe(artifact_dir / "d3_poi_counts.csv"),
        "road_context": _read_json(artifact_dir / "d3_road_context.json"),
        "barrier_summary": _read_dataframe(artifact_dir / "d3_barrier_summary.csv"),
        "ring_variants": {
            "comparison_table": _read_dataframe(artifact_dir / "d3_ring_variants_comparison.csv"),
        },
        "node_typology_label": meta["node_typology_label"],
        "node_typology_rationale": meta["node_typology_rationale"],
        "copy_note": meta["copy_note"],
    }


def load_artifact_d4_payload(site_config_path: str) -> dict[str, Any]:
    """Load the built D4 payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    meta = _read_json(artifact_dir / "d4_meta.json")
    return {
        "frontage_segments": _read_dataframe(artifact_dir / "d4_frontage_segments.csv"),
        "frontage_trend": _read_dataframe(artifact_dir / "d4_frontage_trend.csv"),
        "ranked_segments_1mi": _read_dataframe(artifact_dir / "d4_ranked_segments_1mi.csv"),
        "count_year": meta["count_year"],
        "copy_note": meta["copy_note"],
    }


def load_artifact_d5_payload(site_config_path: str) -> dict[str, Any]:
    """Load the built D5 payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    meta = _read_json(artifact_dir / "d5_meta.json")
    return {
        "nri_catchment_scores": _read_dataframe(artifact_dir / "d5_nri_catchment_scores.csv"),
        "nri_catchment_top_hazards": _read_dataframe(artifact_dir / "d5_nri_catchment_top_hazards.csv"),
        "nri_cbsa_benchmark": _read_dataframe(artifact_dir / "d5_nri_cbsa_benchmark.csv"),
        "nri_cbsa_top_hazards": _read_dataframe(artifact_dir / "d5_nri_cbsa_top_hazards.csv"),
        "nfhl_site_zone": _read_dataframe(artifact_dir / "d5_nfhl_site_zone.csv"),
        "nfhl_ring_shares": _read_dataframe(artifact_dir / "d5_nfhl_ring_shares.csv"),
        "nfhl_service_status": meta["nfhl_service_status"],
        "nfhl_service_error": meta["nfhl_service_error"],
        "copy_note": meta["copy_note"],
    }


def load_artifact_market_payload(site_config_path: str) -> dict[str, Any]:
    """Load the built Market-tab payload for one site."""

    site = load_site(site_config_path)
    artifact_dir = _require_artifact_dir(site)
    meta = _read_json(artifact_dir / "market_meta.json")
    return {
        "industry_context": {
            "employment_mix": _read_dataframe(artifact_dir / "market_employment_mix.csv"),
            "gdp_mix": _read_dataframe(artifact_dir / "market_gdp_mix.csv"),
        },
        "housing_context": _read_dataframe(artifact_dir / "market_housing_context.csv"),
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
    meta = _read_json(map_dir / "meta.json")
    return {
        "site_point": meta["site_point"],
        "view_state": meta["view_state"],
        "available_fill_metrics": D6_TRACT_FILL_METRICS,
        "tract_fill": {
            "features": _read_json(map_dir / f"tract_fill_{fill_metric}.geojson")["features"],
            "metric": fill_metric,
            "metric_label": D6_TRACT_FILL_METRICS[fill_metric],
            "year": meta["tract_fill_years"].get(fill_metric),
            "source_table": meta["tract_fill_sources"].get(fill_metric),
        },
        "rings_geojson": _read_json(map_dir / "rings.geojson"),
        "water_adjusted_rings_geojson": _read_json(map_dir / "water_adjusted_rings.geojson"),
        "severed_area_geojson": _read_json(map_dir / "severed_area.geojson"),
        "poi_rows": _read_dataframe(map_dir / "poi_rows.csv"),
        "road_geojson": _read_json(map_dir / "roads.geojson"),
        "flood_geojson": _read_json(map_dir / "flood.geojson") if include_flood_context else {"type": "FeatureCollection", "features": []},
        "barrier_summary": _read_dataframe(artifact_dir / "d3_barrier_summary.csv"),
        "nfhl_service_status": meta["nfhl_service_status"],
        "nfhl_service_error": meta["nfhl_service_error"],
    }


def _build_context_map_artifacts(site: Site, weight_table: pd.DataFrame, artifact_dir: Path) -> None:
    """Persist the shared D6 context-map assets once per site."""

    map_dir = artifact_dir / "map"
    map_dir.mkdir(parents=True, exist_ok=True)
    tract_fill_years: dict[str, int | None] = {}
    tract_fill_sources: dict[str, str | None] = {}
    metrics = list(D6_TRACT_FILL_METRICS)
    if not metrics:
        raise ValueError("D6_TRACT_FILL_METRICS must define at least one tract-fill layer.")

    first_metric = metrics[0]
    first_payload = build_context_map_payload(site, weight_table, fill_metric=first_metric, include_flood_context=True)
    _write_json(
        map_dir / f"tract_fill_{first_metric}.geojson",
        {"type": "FeatureCollection", "features": first_payload["tract_fill"]["features"]},
    )
    tract_fill_years[first_metric] = first_payload["tract_fill"]["year"]
    tract_fill_sources[first_metric] = first_payload["tract_fill"]["source_table"]

    for metric in metrics[1:]:
        tract_fill = build_context_tract_fill(site, metric)
        _write_json(
            map_dir / f"tract_fill_{metric}.geojson",
            {"type": "FeatureCollection", "features": tract_fill["features"]},
        )
        tract_fill_years[metric] = tract_fill["year"]
        tract_fill_sources[metric] = tract_fill["source_table"]

    _write_json(map_dir / "rings.geojson", first_payload["rings_geojson"])
    _write_json(map_dir / "water_adjusted_rings.geojson", first_payload["water_adjusted_rings_geojson"])
    _write_json(map_dir / "severed_area.geojson", first_payload["severed_area_geojson"])
    _write_json(map_dir / "roads.geojson", first_payload["road_geojson"])
    _write_json(map_dir / "flood.geojson", first_payload["flood_geojson"])
    _write_dataframe(map_dir / "poi_rows.csv", first_payload["poi_rows"])
    _write_json(
        map_dir / "meta.json",
        {
            "site_point": first_payload["site_point"],
            "view_state": first_payload["view_state"],
            "tract_fill_years": tract_fill_years,
            "tract_fill_sources": tract_fill_sources,
            "nfhl_service_status": first_payload["nfhl_service_status"],
            "nfhl_service_error": first_payload["nfhl_service_error"],
        },
    )


def _serialize_site(site: Site) -> dict[str, Any]:
    """Convert a Site dataclass into JSON-safe metadata."""

    return asdict(site)


def _serialize_resolved_site(resolved_site: ResolvedSite) -> dict[str, Any]:
    """Convert a ResolvedSite dataclass into JSON-safe metadata."""

    return {
        "lat": resolved_site.lat,
        "lon": resolved_site.lon,
        "tract_geoid": resolved_site.tract_geoid,
        "matched_address": resolved_site.matched_address,
        "match_type": resolved_site.match_type,
        "geocode_source": resolved_site.geocode_source,
    }


def _deserialize_site(payload: dict[str, Any]) -> Site:
    """Rebuild a Site dataclass from JSON metadata."""

    return Site(**payload)


def _deserialize_resolved_site(payload: dict[str, Any], site: Site) -> ResolvedSite:
    """Rebuild a ResolvedSite dataclass from JSON metadata."""

    return ResolvedSite(site=site, **payload)


def _require_artifact_dir(site: Site) -> Path:
    """Return one artifact dir or fail with a clear build-step message."""

    artifact_dir = get_site_artifact_dir(site)
    if not (artifact_dir / "manifest.json").exists():
        raise FileNotFoundError(
            f"Built artifacts were not found for site '{site.site_id}'. "
            "Run build_site_artifacts.py before launching the app."
        )
    return artifact_dir


def _write_dataframe(path: Path, frame: pd.DataFrame) -> None:
    """Write one DataFrame to CSV with a small sidecar schema for empty cases."""

    frame.to_csv(path, index=False)
    _write_json(
        _schema_path(path),
        {
            "columns": list(frame.columns),
            "dtypes": {column: str(dtype) for column, dtype in frame.dtypes.items()},
        },
    )


def _read_dataframe(path: Path) -> pd.DataFrame:
    """Read one CSV DataFrame artifact, preserving empty schemas when possible."""

    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        schema = _read_json(_schema_path(path))
        return pd.DataFrame(columns=schema.get("columns", []))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write one JSON artifact with deterministic indentation."""

    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    """Read one JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def _schema_path(path: Path) -> Path:
    """Return the lightweight schema sidecar path for one CSV artifact."""

    return path.with_suffix(f"{path.suffix}.schema.json")


def _time_logged_step(site_id: str, label: str, fn, timings: dict[str, float] | None = None):
    """Run one artifact-build step and print its elapsed time."""

    start = perf_counter()
    value = fn()
    elapsed = perf_counter() - start
    if timings is not None:
        timings[label] = round(elapsed, 3)
    print(f"[{site_id}] {label}: {elapsed:.2f}s", flush=True)
    return value
