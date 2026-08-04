"""Build the market-scoped staged NRI surface for D5."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_market_artifact_dir, record_manifest_step, resolve_site_config_paths, time_step, write_dataframe
from data_builds.d5.shared import build_market_nri_inputs
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_d5_market_nri_inputs(site_config_path: str):
    """Stage market-wide NRI rows once so site-level D5 products can reuse them."""

    site = load_site(site_config_path)
    artifact_dir = ensure_market_artifact_dir(site.market_id)
    frame, elapsed = time_step(site.site_id, "d5.market_nri_inputs", lambda: build_market_nri_inputs(site))
    write_dataframe(artifact_dir / "d5_market_nri_inputs.csv", frame)
    record_manifest_step(site, artifact_dir, site_config_path, "d5_market_nri_inputs", elapsed)
    return artifact_dir, elapsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence D5 market NRI artifacts.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    site_configs = resolve_site_config_paths(
        args.site_configs,
        all_sites=args.all_sites,
        default_site_config_path=str(get_default_site_config_path()),
        discovered_site_configs=[str(path) for path in list_site_configs()],
    )
    for site_config in site_configs:
        artifact_dir, _ = build_d5_market_nri_inputs(site_config)
        print(f"Built D5 market NRI artifact for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
