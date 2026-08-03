"""Compatibility wrapper for the foundation-level base build."""

from __future__ import annotations

from pathlib import Path
import sys
from time import perf_counter

SECTION_ROOT = Path(__file__).resolve().parents[1]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.foundations.build_base_diagnostics import build_base_diagnostics_for_site
from data_builds.foundations.build_base_geometry import build_base_geometry_for_site
from data_builds.foundations.build_base_weights import build_base_weights_for_site
from data_builds.foundations.build_site_identity import (
    build_site_identity_for_site,
)
from data_builds.common import ensure_site_artifact_dir, record_manifest_step
from site_prep import load_site


def build_base_for_site(site_config_path: str):
    """Build the base artifact bundle by chaining foundation-level steps."""

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    start = perf_counter()
    artifact_dir = build_site_identity_for_site(site_config_path)
    build_base_geometry_for_site(site_config_path)
    build_base_weights_for_site(site_config_path)
    build_base_diagnostics_for_site(site_config_path)
    record_manifest_step(site, artifact_dir, site_config_path, "base", perf_counter() - start)
    return artifact_dir


def main() -> int:
    """Delegate CLI argument handling to the identity builder and run the full base chain."""

    import argparse

    from data_builds.common import resolve_site_config_paths
    from site_prep import get_default_site_config_path, list_site_configs

    parser = argparse.ArgumentParser(description="Build the full Place Intelligence D1 base bundle.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    args = parser.parse_args()

    site_configs = resolve_site_config_paths(
        args.site_configs,
        all_sites=args.all_sites,
        default_site_config_path=str(get_default_site_config_path()),
        discovered_site_configs=[str(path) for path in list_site_configs()],
    )
    for site_config in site_configs:
        artifact_dir = build_base_for_site(site_config)
        print(f"Built base artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
