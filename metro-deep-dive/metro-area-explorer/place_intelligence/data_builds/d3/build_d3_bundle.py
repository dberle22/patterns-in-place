"""Convenience orchestrator that runs the independently-buildable D3 products in order."""

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
from data_builds.d3.build_d3_barrier_summary import build_d3_barrier_summary
from data_builds.d3.build_d3_daytime_population import build_d3_daytime_population
from data_builds.d3.build_d3_daytime_tract_inputs import build_d3_daytime_tract_inputs
from data_builds.d3.build_d3_market_infrastructure import build_d3_market_infrastructure
from data_builds.d3.build_d3_market_pois import build_d3_market_pois
from data_builds.d3.build_d3_node_typology import build_d3_node_typology
from data_builds.d3.build_d3_poi_counts import build_d3_poi_counts
from data_builds.d3.build_d3_ring_variants import build_d3_ring_variants
from data_builds.d3.build_d3_road_context import build_d3_road_context
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_d3_for_site(site_config_path: str) -> Path:
    """Build the D3 product family for one site in explicit dependency order."""

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    _, _, market_pois_elapsed = build_d3_market_pois(site_config_path)
    _, market_infrastructure_elapsed = build_d3_market_infrastructure(site_config_path)
    _, daytime_inputs_elapsed = build_d3_daytime_tract_inputs(site_config_path, artifact_dir)
    _, daytime_elapsed = build_d3_daytime_population(site_config_path, artifact_dir)
    _, poi_counts_elapsed = build_d3_poi_counts(site_config_path, artifact_dir)
    _, road_elapsed = build_d3_road_context(site_config_path, artifact_dir)
    _, barrier_elapsed = build_d3_barrier_summary(site_config_path, artifact_dir)
    _, ring_variants_elapsed = build_d3_ring_variants(site_config_path, artifact_dir)
    _, node_elapsed = build_d3_node_typology(site_config_path, artifact_dir)
    elapsed = (
        market_pois_elapsed
        + market_infrastructure_elapsed
        + daytime_inputs_elapsed
        + daytime_elapsed
        + poi_counts_elapsed
        + road_elapsed
        + barrier_elapsed
        + ring_variants_elapsed
        + node_elapsed
    )
    record_manifest_step(site, artifact_dir, site_config_path, "d3", elapsed)
    return artifact_dir


def parse_args() -> argparse.Namespace:
    """Parse the small CLI surface for D3 builds."""

    parser = argparse.ArgumentParser(description="Build Place Intelligence D3 artifacts.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    """Build D3 artifacts for the requested sites."""

    args = parse_args()
    site_configs = resolve_site_config_paths(
        args.site_configs,
        all_sites=args.all_sites,
        default_site_config_path=str(get_default_site_config_path()),
        discovered_site_configs=[str(path) for path in list_site_configs()],
    )

    for site_config in site_configs:
        artifact_dir = build_d3_for_site(site_config)
        print(f"Built D3 artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
