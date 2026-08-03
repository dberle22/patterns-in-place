"""Build the D5 NRI top-hazard site outputs from staged market NRI rows."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_market_artifact_dir, ensure_site_artifact_dir, read_dataframe, record_manifest_step, require_artifact_files, resolve_site_config_paths, time_step, write_dataframe
from data_builds.d5.shared import build_nri_scores_payload, normalize_weight_table
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_d5_nri_top_hazards(site_config_path: str, artifact_dir: Path):
    """Build the NRI top hazard tables from staged market NRI rows."""

    site = load_site(site_config_path)
    market_dir = ensure_market_artifact_dir(site.market_id)
    require_artifact_files(market_dir, ["d5_market_nri_inputs.csv"], "d5.nri_top_hazards")
    require_artifact_files(artifact_dir, ["base_weight_table.csv"], "d5.nri_top_hazards")
    nri_surface = read_dataframe(market_dir / "d5_market_nri_inputs.csv")
    weight_table = normalize_weight_table(read_dataframe(artifact_dir / "base_weight_table.csv"))
    payload, elapsed = time_step(site.site_id, "d5.nri_top_hazards", lambda: build_nri_scores_payload(site, weight_table, nri_surface))
    write_dataframe(artifact_dir / "d5_nri_catchment_top_hazards.csv", payload["catchment_top_hazards"])
    write_dataframe(artifact_dir / "d5_nri_cbsa_top_hazards.csv", payload["cbsa_top_hazards"])
    record_manifest_step(site, artifact_dir, site_config_path, "d5_nri_top_hazards", elapsed)
    return payload, elapsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence D5 NRI top hazard artifacts.")
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
        site = load_site(site_config)
        artifact_dir = ensure_site_artifact_dir(site)
        build_d5_nri_top_hazards(site_config, artifact_dir)
        print(f"Built D5 NRI top hazard artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
