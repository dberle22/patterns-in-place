"""Shared helpers for product-scoped Place Intelligence data builds."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from time import perf_counter
from typing import Any, Callable

import pandas as pd


SECTION_ROOT = Path(__file__).resolve().parents[1]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from site_prep import ResolvedSite, Site, get_spatial_output_dir, load_site


ARTIFACTS_DIRNAME = "site_artifacts"
MARKET_ARTIFACTS_DIRNAME = "market_artifacts"
REQUIRED_APP_STEPS = (
    "base",
    "d2",
    "d3",
    "d4",
    "d5",
    "overview",
    "market",
    "context_map",
)


def resolve_site_config_paths(
    site_configs: list[str],
    *,
    all_sites: bool,
    default_site_config_path: str,
    discovered_site_configs: list[str],
) -> list[str]:
    """Resolve the requested site config list for a build CLI."""

    if all_sites:
        return discovered_site_configs
    if site_configs:
        return site_configs
    return [default_site_config_path]


def get_site_artifact_dir(site: Site) -> Path:
    """Return the artifact directory for one configured site."""

    return get_spatial_output_dir(site.market_id) / ARTIFACTS_DIRNAME / site.site_id


def ensure_site_artifact_dir(site: Site) -> Path:
    """Create and return the artifact directory for one configured site."""

    artifact_dir = get_site_artifact_dir(site)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    return artifact_dir


def get_market_artifact_dir(market_id: str) -> Path:
    """Return the market-scoped artifact directory for shared source products."""

    return get_spatial_output_dir(market_id) / MARKET_ARTIFACTS_DIRNAME


def ensure_market_artifact_dir(market_id: str) -> Path:
    """Create and return the market-scoped artifact directory for shared source products."""

    artifact_dir = get_market_artifact_dir(market_id)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    return artifact_dir


def build_completed_for_app(site_config_path: str) -> bool:
    """Return whether the full app-facing artifact bundle exists for one site."""

    site = load_site(site_config_path)
    artifact_dir = get_site_artifact_dir(site)
    manifest_path = artifact_dir / "manifest.json"
    if not manifest_path.exists():
        return False
    manifest = read_json(manifest_path)
    completed_steps = set(manifest.get("completed_steps", []))
    return set(REQUIRED_APP_STEPS).issubset(completed_steps)


def serialize_site(site: Site) -> dict[str, Any]:
    """Convert a Site dataclass into JSON-safe metadata."""

    return asdict(site)


def serialize_resolved_site(resolved_site: ResolvedSite) -> dict[str, Any]:
    """Convert a ResolvedSite dataclass into JSON-safe metadata."""

    return {
        "lat": resolved_site.lat,
        "lon": resolved_site.lon,
        "tract_geoid": resolved_site.tract_geoid,
        "matched_address": resolved_site.matched_address,
        "match_type": resolved_site.match_type,
        "geocode_source": resolved_site.geocode_source,
    }


def deserialize_site(payload: dict[str, Any]) -> Site:
    """Rebuild a Site dataclass from JSON metadata."""

    return Site(**payload)


def deserialize_resolved_site(payload: dict[str, Any], site: Site) -> ResolvedSite:
    """Rebuild a ResolvedSite dataclass from JSON metadata."""

    return ResolvedSite(site=site, **payload)


def write_dataframe(path: Path, frame: pd.DataFrame) -> None:
    """Write one DataFrame to CSV with a small schema sidecar."""

    frame.to_csv(path, index=False)
    write_json(
        schema_path(path),
        {
            "columns": list(frame.columns),
            "dtypes": {column: str(dtype) for column, dtype in frame.dtypes.items()},
        },
    )


def read_dataframe(path: Path) -> pd.DataFrame:
    """Read one CSV DataFrame artifact, preserving empty schemas when possible."""

    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        schema = read_json(schema_path(path))
        return pd.DataFrame(columns=schema.get("columns", []))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write one JSON artifact with deterministic indentation."""

    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    """Read one JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def schema_path(path: Path) -> Path:
    """Return the schema sidecar path for one CSV artifact."""

    return path.with_suffix(f"{path.suffix}.schema.json")


def require_artifact_files(artifact_dir: Path, filenames: list[str], step_name: str) -> None:
    """Fail clearly when a build step's prerequisite artifacts are missing."""

    missing = [name for name in filenames if not (artifact_dir / name).exists()]
    if missing:
        raise FileNotFoundError(
            f"Cannot build '{step_name}' because required artifacts are missing: {', '.join(missing)}."
        )


def write_geojson(path: Path, frame) -> None:
    """Write one GeoDataFrame-like object to GeoJSON."""

    write_json(path, json.loads(frame.to_json()))


def time_step(site_id: str, label: str, fn: Callable[[], Any]) -> tuple[Any, float]:
    """Run one build step, print timing, and return both value and elapsed seconds."""

    start = perf_counter()
    value = fn()
    elapsed = perf_counter() - start
    print(f"[{site_id}] {label}: {elapsed:.2f}s", flush=True)
    return value, elapsed


def record_manifest_step(site: Site, artifact_dir: Path, site_config_path: str, step_name: str, elapsed_seconds: float) -> None:
    """Update the manifest after one product-scoped build step."""

    manifest_path = artifact_dir / "manifest.json"
    if manifest_path.exists():
        manifest = read_json(manifest_path)
    else:
        manifest = {
            "site_id": site.site_id,
            "market_id": site.market_id,
            "site_config_filename": Path(site_config_path).name,
            "built_at_utc": None,
            "completed_steps": [],
            "step_timings_seconds": {},
        }

    completed_steps = set(manifest.get("completed_steps", []))
    completed_steps.add(step_name)
    timings = dict(manifest.get("step_timings_seconds", {}))
    timings[step_name] = round(float(elapsed_seconds), 3)

    manifest.update(
        {
            "site_id": site.site_id,
            "market_id": site.market_id,
            "site_config_filename": Path(site_config_path).name,
            "built_at_utc": datetime.now(timezone.utc).isoformat(),
            "completed_steps": sorted(completed_steps),
            "step_timings_seconds": timings,
        }
    )
    write_json(manifest_path, manifest)
