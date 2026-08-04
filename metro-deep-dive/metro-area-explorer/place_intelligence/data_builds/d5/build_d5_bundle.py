"""Convenience orchestrator that runs the independently-buildable D5 products in order."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import (
    ensure_site_artifact_dir,
    record_manifest_step,
    resolve_site_config_paths,
)
from data_builds.d5.build_d5_market_nri_inputs import build_d5_market_nri_inputs
from data_builds.d5.build_d5_meta import build_d5_meta_artifact
from data_builds.d5.build_d5_nfhl_ring_shares import build_d5_nfhl_ring_shares
from data_builds.d5.build_d5_nfhl_site_zone import build_d5_nfhl_site_zone
from data_builds.d5.build_d5_nri_scores import build_d5_nri_scores
from data_builds.d5.build_d5_nri_top_hazards import build_d5_nri_top_hazards
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_d5_for_site(site_config_path: str) -> Path:
    """Build the D5 product family for one site in explicit dependency order."""

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    _, market_elapsed = build_d5_market_nri_inputs(site_config_path)
    _, nri_scores_elapsed = build_d5_nri_scores(site_config_path, artifact_dir)
    _, nri_hazards_elapsed = build_d5_nri_top_hazards(site_config_path, artifact_dir)
    _, nfhl_site_elapsed = build_d5_nfhl_site_zone(site_config_path, artifact_dir)
    _, nfhl_ring_elapsed = build_d5_nfhl_ring_shares(site_config_path, artifact_dir)
    _, meta_elapsed = build_d5_meta_artifact(site_config_path, artifact_dir)
    elapsed = market_elapsed + nri_scores_elapsed + nri_hazards_elapsed + nfhl_site_elapsed + nfhl_ring_elapsed + meta_elapsed
    record_manifest_step(site, artifact_dir, site_config_path, "d5", elapsed)
    return artifact_dir


def parse_args() -> argparse.Namespace:
    """Parse the small CLI surface for D5 builds."""

    parser = argparse.ArgumentParser(description="Build Place Intelligence D5 artifacts.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    """Build D5 artifacts for the requested sites."""

    args = parse_args()
    site_configs = resolve_site_config_paths(
        args.site_configs,
        all_sites=args.all_sites,
        default_site_config_path=str(get_default_site_config_path()),
        discovered_site_configs=[str(path) for path in list_site_configs()],
    )

    for site_config in site_configs:
        artifact_dir = build_d5_for_site(site_config)
        print(f"Built D5 artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
