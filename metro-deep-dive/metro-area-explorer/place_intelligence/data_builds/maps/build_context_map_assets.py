"""Convenience orchestrator that runs the independently-buildable context-map products in order."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_site_artifact_dir, record_manifest_step, resolve_site_config_paths
from data_builds.maps.build_map_core import build_map_core
from data_builds.maps.build_map_flood import build_map_flood
from data_builds.maps.build_map_meta import build_map_meta
from data_builds.maps.build_map_pois import build_map_pois
from data_builds.maps.build_map_roads import build_map_roads
from data_builds.maps.build_map_severed_area import build_map_severed_area
from data_builds.maps.build_map_tract_fill import build_map_tract_fill
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_context_map_for_site(site_config_path: str) -> Path:
    """Build the context-map product family for one site in explicit dependency order."""

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    _, core_elapsed = build_map_core(site_config_path, artifact_dir)
    _, tract_elapsed = build_map_tract_fill(site_config_path, artifact_dir)
    _, poi_elapsed = build_map_pois(site_config_path, artifact_dir)
    _, road_elapsed = build_map_roads(site_config_path, artifact_dir)
    _, flood_elapsed = build_map_flood(site_config_path, artifact_dir)
    _, severed_elapsed = build_map_severed_area(site_config_path, artifact_dir)
    _, meta_elapsed = build_map_meta(site_config_path, artifact_dir)
    elapsed = core_elapsed + tract_elapsed + poi_elapsed + road_elapsed + flood_elapsed + severed_elapsed + meta_elapsed
    record_manifest_step(site, artifact_dir, site_config_path, "context_map", elapsed)
    return artifact_dir


def parse_args() -> argparse.Namespace:
    """Parse the small CLI surface for context-map builds."""

    parser = argparse.ArgumentParser(description="Build Place Intelligence context-map artifacts.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    """Build context-map artifacts for the requested sites."""

    args = parse_args()
    site_configs = resolve_site_config_paths(
        args.site_configs,
        all_sites=args.all_sites,
        default_site_config_path=str(get_default_site_config_path()),
        discovered_site_configs=[str(path) for path in list_site_configs()],
    )

    for site_config in site_configs:
        artifact_dir = build_context_map_for_site(site_config)
        print(f"Built context-map artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
