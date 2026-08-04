"""Build the D4 site metadata contract from staged current segments."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_market_artifact_dir, ensure_site_artifact_dir, record_manifest_step, require_artifact_files, resolve_site_config_paths, time_step, write_json
from data_builds.d4.shared import build_d4_meta, read_geojson_frame
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_d4_meta_artifact(site_config_path: str, artifact_dir: Path):
    """Build the small D4 meta contract from the staged current segment layer."""

    site = load_site(site_config_path)
    market_dir = ensure_market_artifact_dir(site.market_id)
    require_artifact_files(market_dir, ["d4_market_current_segments.geojson"], "d4.meta")
    current_segments = read_geojson_frame(market_dir / "d4_market_current_segments.geojson")
    payload, elapsed = time_step(site.site_id, "d4.meta", lambda: build_d4_meta(site, current_segments))
    write_json(artifact_dir / "d4_meta.json", payload)
    record_manifest_step(site, artifact_dir, site_config_path, "d4_meta", elapsed)
    return payload, elapsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence D4 meta artifacts.")
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
        build_d4_meta_artifact(site_config, artifact_dir)
        print(f"Built D4 meta artifact for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
