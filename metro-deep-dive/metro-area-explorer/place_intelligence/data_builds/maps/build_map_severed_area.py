"""Build the severed-area overlay map product."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_market_artifact_dir, ensure_site_artifact_dir, record_manifest_step, require_artifact_files, resolve_site_config_paths, time_step, write_json
from data_builds.maps.shared import build_severed_area_geojson
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_map_severed_area(site_config_path: str, artifact_dir: Path):
    """Build `map/severed_area.geojson` for one site."""

    site = load_site(site_config_path)
    market_dir = ensure_market_artifact_dir(site.market_id)
    require_artifact_files(artifact_dir, ["base_cumulative_rings.geojson", "d3_barrier_summary.csv"], "map.severed_area")
    require_artifact_files(market_dir, ["d3_market_lines.geojson", "d3_market_polygons.geojson"], "map.severed_area")
    geojson, elapsed = time_step(site.site_id, "map.severed_area", lambda: build_severed_area_geojson(site, artifact_dir, market_dir))
    map_dir = artifact_dir / "map"
    map_dir.mkdir(parents=True, exist_ok=True)
    write_json(map_dir / "severed_area.geojson", geojson)
    record_manifest_step(site, artifact_dir, site_config_path, "map_severed_area", elapsed)
    return geojson, elapsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence severed-area map artifacts.")
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
        build_map_severed_area(site_config, artifact_dir)
        print(f"Built map severed area for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
