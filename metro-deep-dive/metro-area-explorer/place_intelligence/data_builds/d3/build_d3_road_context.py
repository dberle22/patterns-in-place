"""Build the D3 site-level road context output from staged market infrastructure."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_market_artifact_dir, ensure_site_artifact_dir, record_manifest_step, require_artifact_files, resolve_site_config_paths, time_step, write_json
from data_builds.d3.shared import build_road_context_payload, read_geojson_frame
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_d3_road_context(site_config_path: str, artifact_dir: Path):
    """Summarize road context for one site from staged market infrastructure."""

    site = load_site(site_config_path)
    market_dir = ensure_market_artifact_dir(site.market_id)
    require_artifact_files(market_dir, ["d3_market_lines.geojson"], "d3.road_context")
    market_lines = read_geojson_frame(market_dir / "d3_market_lines.geojson")
    payload, elapsed = time_step(site.site_id, "d3.road_context", lambda: build_road_context_payload(site, market_lines))
    write_json(artifact_dir / "d3_road_context.json", payload)
    record_manifest_step(site, artifact_dir, site_config_path, "d3_road_context", elapsed)
    return payload, elapsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence D3 road context artifacts.")
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
        build_d3_road_context(site_config, artifact_dir)
        print(f"Built D3 road context artifact for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
