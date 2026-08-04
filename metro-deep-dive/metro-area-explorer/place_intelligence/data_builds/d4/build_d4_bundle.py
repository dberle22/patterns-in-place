"""Convenience orchestrator that runs the independently-buildable D4 products in order."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_site_artifact_dir, record_manifest_step, resolve_site_config_paths
from data_builds.d4.build_d4_frontage_segments import build_d4_frontage_segments
from data_builds.d4.build_d4_frontage_trend import build_d4_frontage_trend
from data_builds.d4.build_d4_market_current_segments import build_d4_market_current_segments
from data_builds.d4.build_d4_market_historical_segments import build_d4_market_historical_segments
from data_builds.d4.build_d4_meta import build_d4_meta_artifact
from data_builds.d4.build_d4_ranked_segments import build_d4_ranked_segments
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_d4_for_site(site_config_path: str) -> Path:
    """Build the D4 product family for one site in explicit dependency order."""

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    _, current_elapsed = build_d4_market_current_segments(site_config_path)
    _, historical_elapsed = build_d4_market_historical_segments(site_config_path)
    _, frontage_elapsed = build_d4_frontage_segments(site_config_path, artifact_dir)
    _, trend_elapsed = build_d4_frontage_trend(site_config_path, artifact_dir)
    _, ranked_elapsed = build_d4_ranked_segments(site_config_path, artifact_dir)
    _, meta_elapsed = build_d4_meta_artifact(site_config_path, artifact_dir)
    elapsed = current_elapsed + historical_elapsed + frontage_elapsed + trend_elapsed + ranked_elapsed + meta_elapsed
    record_manifest_step(site, artifact_dir, site_config_path, "d4", elapsed)
    return artifact_dir


def parse_args() -> argparse.Namespace:
    """Parse the small CLI surface for D4 builds."""

    parser = argparse.ArgumentParser(description="Build Place Intelligence D4 artifacts.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    """Build D4 artifacts for the requested sites."""

    args = parse_args()
    site_configs = resolve_site_config_paths(
        args.site_configs,
        all_sites=args.all_sites,
        default_site_config_path=str(get_default_site_config_path()),
        discovered_site_configs=[str(path) for path in list_site_configs()],
    )

    for site_config in site_configs:
        artifact_dir = build_d4_for_site(site_config)
        print(f"Built D4 artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
