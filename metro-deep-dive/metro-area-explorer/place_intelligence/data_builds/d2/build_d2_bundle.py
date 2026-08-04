"""Convenience orchestrator that runs the independently-buildable D2 products in order."""

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
    time_step,
)
from data_builds.d2.build_d2_benchmarks import build_d2_benchmarks
from data_builds.d2.build_d2_catchment_profile import build_d2_catchment_profile
from data_builds.d2.build_d2_tract_inputs import build_d2_tract_inputs
from data_builds.d2.build_d2_metric_long import build_d2_metric_long
from data_builds.d2.build_d2_metric_summary import build_d2_metric_summary
from data_builds.d2.build_d2_skip_reasons import build_d2_skip_reasons
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_d2_for_site(site_config_path: str) -> Path:
    """Build the D2 product family for one site in explicit dependency order."""

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    _, tract_inputs_elapsed = build_d2_tract_inputs(site_config_path, artifact_dir)
    _, metric_long_elapsed = build_d2_metric_long(site_config_path, artifact_dir)
    _, catchment_elapsed = build_d2_catchment_profile(site_config_path, artifact_dir)
    _, benchmarks_elapsed = build_d2_benchmarks(site_config_path, artifact_dir)
    _, summary_elapsed = build_d2_metric_summary(site_config_path, artifact_dir)
    _, skip_elapsed = build_d2_skip_reasons(site_config_path, artifact_dir)
    elapsed = tract_inputs_elapsed + metric_long_elapsed + catchment_elapsed + benchmarks_elapsed + summary_elapsed + skip_elapsed
    record_manifest_step(site, artifact_dir, site_config_path, "d2", elapsed)
    return artifact_dir


def parse_args() -> argparse.Namespace:
    """Parse the small CLI surface for D2 builds."""

    parser = argparse.ArgumentParser(description="Build Place Intelligence D2 artifacts.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    """Build D2 artifacts for the requested sites."""

    args = parse_args()
    site_configs = resolve_site_config_paths(
        args.site_configs,
        all_sites=args.all_sites,
        default_site_config_path=str(get_default_site_config_path()),
        discovered_site_configs=[str(path) for path in list_site_configs()],
    )

    for site_config in site_configs:
        artifact_dir = build_d2_for_site(site_config)
        print(f"Built D2 artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
