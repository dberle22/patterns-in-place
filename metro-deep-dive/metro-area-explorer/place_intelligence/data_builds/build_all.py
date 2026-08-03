"""Build the full app-facing artifact bundle by chaining product-scoped build scripts."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[1]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.build_base import build_base_for_site
from data_builds.d2.build_d2_bundle import build_d2_for_site
from data_builds.d3.build_d3_bundle import build_d3_for_site
from data_builds.d4.build_d4_bundle import build_d4_for_site
from data_builds.d5.build_d5_bundle import build_d5_for_site
from data_builds.market.build_market_bundle import build_market_for_site
from data_builds.maps.build_context_map_assets import build_context_map_for_site
from data_builds.pages.build_market_page import build_market_page_for_site
from data_builds.pages.build_methods_page import build_methods_for_site
from data_builds.pages.build_overview_page import build_overview_for_site
from data_builds.pages.build_people_page import build_people_for_site
from data_builds.pages.build_place_page import build_place_for_site
from site_prep import get_default_site_config_path, list_site_configs


def build_all_for_site(site_config_path: str) -> Path:
    """Build the full app-facing artifact bundle for one site."""

    artifact_dir = build_base_for_site(site_config_path)
    build_d2_for_site(site_config_path)
    build_d3_for_site(site_config_path)
    build_d4_for_site(site_config_path)
    build_d5_for_site(site_config_path)
    build_overview_for_site(site_config_path)
    build_market_for_site(site_config_path)
    build_context_map_for_site(site_config_path)
    build_people_for_site(site_config_path)
    build_place_for_site(site_config_path)
    build_market_page_for_site(site_config_path)
    build_methods_for_site(site_config_path)
    return artifact_dir


def parse_args() -> argparse.Namespace:
    """Parse the small CLI surface for full builds."""

    parser = argparse.ArgumentParser(description="Build the full Place Intelligence artifact bundle.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    """Build the full artifact bundle for the requested sites."""

    args = parse_args()
    if args.all_sites:
        site_configs = [str(path) for path in list_site_configs()]
    elif args.site_configs:
        site_configs = args.site_configs
    else:
        site_configs = [str(get_default_site_config_path())]

    for site_config in site_configs:
        artifact_dir = build_all_for_site(site_config)
        print(f"Built all artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
