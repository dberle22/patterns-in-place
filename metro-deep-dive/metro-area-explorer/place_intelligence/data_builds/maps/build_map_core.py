"""Build the core context-map geometry and view-state products."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_market_artifact_dir, ensure_site_artifact_dir, record_manifest_step, require_artifact_files, resolve_site_config_paths, time_step, write_json
from data_builds.maps.shared import build_adjusted_rings, build_site_point_and_view_state, read_base_rings
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_map_core(site_config_path: str, artifact_dir: Path):
    """Build the core map geometry and small core metadata products."""

    site = load_site(site_config_path)
    market_dir = ensure_market_artifact_dir(site.market_id)
    require_artifact_files(
        artifact_dir,
        ["site.json", "resolved_site.json", "base_cumulative_rings.geojson", "d3_barrier_summary.csv"],
        "map.core",
    )
    require_artifact_files(market_dir, ["d3_market_lines.geojson", "d3_market_polygons.geojson"], "map.core")
    payload, elapsed = time_step(
        site.site_id,
        "map.core",
        lambda: {
            "site_point": build_site_point_and_view_state(artifact_dir)[0],
            "view_state": build_site_point_and_view_state(artifact_dir)[1],
            "baseline_rings": read_base_rings(artifact_dir).to_crs("EPSG:4326"),
            "adjusted_payload": build_adjusted_rings(site, artifact_dir, market_dir),
        },
    )
    map_dir = artifact_dir / "map"
    map_dir.mkdir(parents=True, exist_ok=True)
    write_json(map_dir / "rings.geojson", json.loads(payload["baseline_rings"].to_json()))
    write_json(map_dir / "water_adjusted_rings.geojson", _water_adjusted_geojson(payload["adjusted_payload"]))
    write_json(
        map_dir / "core.json",
        {
            "site_point": payload["site_point"],
            "view_state": payload["view_state"],
            "nfhl_service_status": "ok",
            "nfhl_service_error": None,
        },
    )
    record_manifest_step(site, artifact_dir, site_config_path, "map_core", elapsed)
    return payload, elapsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence map core artifacts.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    site_configs = resolve_site_config_paths(
        args.site_configs,
        all_sites=args.all_sites,
        default_site_config_path=str(get_default_site_config_path()),
        discovered_site_configs=[str(path) for path in list_site_configs()],
    )
    for site_config in site_configs:
        site = load_site(site_config)
        artifact_dir = ensure_site_artifact_dir(site)
        build_map_core(site_config, artifact_dir)
        print(f"Built map core for {Path(site_config).name} -> {artifact_dir}")
    return 0


def _water_adjusted_geojson(adjusted_payload: dict) -> dict:
    """Convert the water-adjusted ring GeoDataFrame into a FeatureCollection."""

    adjusted = adjusted_payload["water_adjusted_rings"].to_crs("EPSG:4326")
    return json.loads(adjusted.to_json())


if __name__ == "__main__":
    raise SystemExit(main())
