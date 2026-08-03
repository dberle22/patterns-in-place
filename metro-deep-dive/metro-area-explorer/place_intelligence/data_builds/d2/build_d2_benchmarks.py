"""Build the benchmark-table D2 derivative from the canonical long table."""

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
from data_builds.d2.shared import build_benchmark_table_frame
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_d2_benchmarks(site_config_path: str, artifact_dir: Path):
    """Materialize the benchmark comparison table from `d2_metric_long.csv`."""

    site = load_site(site_config_path)
    require_artifact_files(artifact_dir, ["d2_metric_long.csv"], "d2.benchmarks")
    metric_long = read_dataframe(artifact_dir / "d2_metric_long.csv")
    benchmark_table, elapsed = time_step(
        site.site_id,
        "d2.benchmarks",
        lambda: build_benchmark_table_frame(metric_long),
    )
    write_dataframe(artifact_dir / "d2_benchmark_table.csv", benchmark_table)
    record_manifest_step(site, artifact_dir, site_config_path, "d2_benchmarks", elapsed)
    return benchmark_table, elapsed


def parse_args() -> argparse.Namespace:
    """Parse the CLI surface for the D2 benchmarks product."""

    parser = argparse.ArgumentParser(description="Build Place Intelligence D2 benchmark artifacts.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    """Build `d2_benchmark_table.csv` for the requested sites."""

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
        build_d2_benchmarks(site_config, artifact_dir)
        print(f"Built D2 benchmark artifact for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
