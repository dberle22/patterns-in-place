"""Build the canonical D2 fact table for one Place Intelligence site."""

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
from data_builds.d2.shared import build_metric_long_frame, normalize_weight_table
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_d2_metric_long(site_config_path: str, artifact_dir: Path):
    """Materialize the canonical long D2 table from tract staging plus base ring weights."""

    site = load_site(site_config_path)
    require_artifact_files(artifact_dir, ["base_weight_table.csv", "d2_tract_inputs.csv"], "d2.metric_long")
    weight_table = normalize_weight_table(read_dataframe(artifact_dir / "base_weight_table.csv"))
    tract_inputs = read_dataframe(artifact_dir / "d2_tract_inputs.csv")
    metric_long, elapsed = time_step(
        site.site_id,
        "d2.metric_long",
        lambda: build_metric_long_frame(site, weight_table, tract_inputs),
    )
    write_dataframe(artifact_dir / "d2_metric_long.csv", metric_long)
    record_manifest_step(site, artifact_dir, site_config_path, "d2_metric_long", elapsed)
    return metric_long, elapsed


def parse_args() -> argparse.Namespace:
    """Parse the CLI surface for the D2 metric-long product."""

    parser = argparse.ArgumentParser(description="Build Place Intelligence D2 metric-long artifacts.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    """Build `d2_metric_long.csv` for the requested sites."""

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
        build_d2_metric_long(site_config, artifact_dir)
        print(f"Built D2 metric-long artifact for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
