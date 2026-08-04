"""Convenience orchestrator that runs the independently-buildable Market products in order."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_site_artifact_dir, record_manifest_step, resolve_site_config_paths
from data_builds.market.build_market_employment_mix import build_market_employment_mix
from data_builds.market.build_market_gdp_mix import build_market_gdp_mix
from data_builds.market.build_market_housing_context import build_market_housing_context
from data_builds.market.build_market_meta import build_market_meta
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_market_for_site(site_config_path: str) -> Path:
    """Build the Market product family for one site in explicit dependency order."""

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    _, employment_elapsed = build_market_employment_mix(site_config_path, artifact_dir)
    _, gdp_elapsed = build_market_gdp_mix(site_config_path, artifact_dir)
    _, housing_elapsed = build_market_housing_context(site_config_path, artifact_dir)
    _, meta_elapsed = build_market_meta(site_config_path, artifact_dir)
    elapsed = employment_elapsed + gdp_elapsed + housing_elapsed + meta_elapsed
    record_manifest_step(site, artifact_dir, site_config_path, "market", elapsed)
    return artifact_dir


def parse_args() -> argparse.Namespace:
    """Parse the small CLI surface for Market builds."""

    parser = argparse.ArgumentParser(description="Build Place Intelligence market artifacts.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    """Build Market artifacts for the requested sites."""

    args = parse_args()
    site_configs = resolve_site_config_paths(
        args.site_configs,
        all_sites=args.all_sites,
        default_site_config_path=str(get_default_site_config_path()),
        discovered_site_configs=[str(path) for path in list_site_configs()],
    )

    for site_config in site_configs:
        artifact_dir = build_market_for_site(site_config)
        print(f"Built market artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
