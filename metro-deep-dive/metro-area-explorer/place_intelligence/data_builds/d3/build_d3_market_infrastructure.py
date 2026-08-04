"""Build the market-scoped staged infrastructure layers for D3 roads and barriers."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_market_artifact_dir, record_manifest_step, resolve_site_config_paths, time_step, write_geojson
from data_builds.d3.shared import build_market_infrastructure_frames
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_d3_market_infrastructure(site_config_path: str):
    """Stage market-wide infrastructure once so roads and barriers can build per site."""

    site = load_site(site_config_path)
    artifact_dir = ensure_market_artifact_dir(site.market_id)
    frames, elapsed = time_step(site.site_id, "d3.market_infrastructure", lambda: build_market_infrastructure_frames(site))
    lines, points, polygons = frames
    write_geojson(artifact_dir / "d3_market_lines.geojson", lines)
    write_geojson(artifact_dir / "d3_market_points.geojson", points)
    write_geojson(artifact_dir / "d3_market_polygons.geojson", polygons)
    record_manifest_step(site, artifact_dir, site_config_path, "d3_market_infrastructure", elapsed)
    return artifact_dir, elapsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence D3 market infrastructure artifacts.")
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
        artifact_dir, _ = build_d3_market_infrastructure(site_config)
        print(f"Built D3 market infrastructure artifact for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
