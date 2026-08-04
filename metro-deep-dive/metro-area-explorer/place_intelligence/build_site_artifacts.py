"""Compatibility wrapper that builds the full app-facing artifact bundle."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parent
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.build_all import build_all_for_site
from site_prep import get_default_site_config_path, list_site_configs


def parse_args() -> argparse.Namespace:
    """Parse the small CLI surface for artifact builds."""

    parser = argparse.ArgumentParser(description="Build the full Place Intelligence artifact bundle.")
    parser.add_argument(
        "site_configs",
        nargs="*",
        help="Optional site YAML paths. Defaults to the spotlight site when omitted.",
    )
    parser.add_argument(
        "--all-sites",
        action="store_true",
        help="Build artifacts for every discovered site YAML in this section.",
    )
    return parser.parse_args()


def main() -> int:
    """Build the requested site artifacts."""

    args = parse_args()
    if args.all_sites:
        site_configs = [str(path) for path in list_site_configs()]
    elif args.site_configs:
        site_configs = args.site_configs
    else:
        site_configs = [str(get_default_site_config_path())]

    for site_config in site_configs:
        artifact_dir = build_all_for_site(site_config)
        print(f"Built artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
