"""Build the base coverage-diagnostic artifacts for one or more Place Intelligence sites."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import (
    ensure_site_artifact_dir,
    read_dataframe,
    record_manifest_step,
    require_artifact_files,
    resolve_site_config_paths,
    time_step,
    write_dataframe,
)
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_base_diagnostics_for_site(site_config_path: str) -> Path:
    """Build the D1 coverage diagnostics for one site."""

    from apportion import coverage_diagnostic

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    require_artifact_files(artifact_dir, ["base_weight_table.csv"], "base_diagnostics")

    weight_table = read_dataframe(artifact_dir / "base_weight_table.csv")
    diagnostics, elapsed = time_step(site.site_id, "base_diagnostics", lambda: coverage_diagnostic(weight_table))

    write_dataframe(artifact_dir / "base_coverage_diagnostic.csv", diagnostics)
    record_manifest_step(site, artifact_dir, site_config_path, "base_diagnostics", elapsed)
    return artifact_dir


def parse_args() -> argparse.Namespace:
    """Parse the small CLI surface for diagnostic builds."""

    parser = argparse.ArgumentParser(description="Build Place Intelligence base diagnostic artifacts.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    """Build base diagnostic artifacts for the requested sites."""

    args = parse_args()
    site_configs = resolve_site_config_paths(
        args.site_configs,
        all_sites=args.all_sites,
        default_site_config_path=str(get_default_site_config_path()),
        discovered_site_configs=[str(path) for path in list_site_configs()],
    )

    for site_config in site_configs:
        artifact_dir = build_base_diagnostics_for_site(site_config)
        print(f"Built base diagnostics for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

