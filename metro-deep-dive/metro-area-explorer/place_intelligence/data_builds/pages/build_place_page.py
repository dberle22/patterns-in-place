"""Build the compact Place page contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_site_artifact_dir, read_dataframe, read_json, record_manifest_step, require_artifact_files, resolve_site_config_paths, time_step, write_json
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_place_for_site(site_config_path: str) -> Path:
    """Build `place.json` for one site."""

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    require_artifact_files(
        artifact_dir,
        [
            "d3_poi_counts.csv",
            "d3_barrier_summary.csv",
            "d3_ring_variants_comparison.csv",
            "d4_frontage_segments.csv",
            "d4_frontage_trend.csv",
            "d4_ranked_segments_1mi.csv",
            "d4_meta.json",
            "d5_nri_catchment_scores.csv",
            "d5_nfhl_site_zone.csv",
            "d5_nfhl_ring_shares.csv",
            "d5_meta.json",
        ],
        "place",
    )
    payload, elapsed = time_step(
        site.site_id,
        "place",
        lambda: {
            "poi_counts": read_dataframe(artifact_dir / "d3_poi_counts.csv").to_dict("records"),
            "barrier_summary": read_dataframe(artifact_dir / "d3_barrier_summary.csv").to_dict("records"),
            "ring_variants": read_dataframe(artifact_dir / "d3_ring_variants_comparison.csv").to_dict("records"),
            "frontage_segments": read_dataframe(artifact_dir / "d4_frontage_segments.csv").to_dict("records"),
            "frontage_trend": read_dataframe(artifact_dir / "d4_frontage_trend.csv").to_dict("records"),
            "ranked_segments_1mi": read_dataframe(artifact_dir / "d4_ranked_segments_1mi.csv").to_dict("records"),
            "d4_meta": read_json(artifact_dir / "d4_meta.json"),
            "nri_catchment_scores": read_dataframe(artifact_dir / "d5_nri_catchment_scores.csv").to_dict("records"),
            "nfhl_site_zone": read_dataframe(artifact_dir / "d5_nfhl_site_zone.csv").to_dict("records"),
            "nfhl_ring_shares": read_dataframe(artifact_dir / "d5_nfhl_ring_shares.csv").to_dict("records"),
            "d5_meta": read_json(artifact_dir / "d5_meta.json"),
        },
    )
    write_json(artifact_dir / "place.json", payload)
    record_manifest_step(site, artifact_dir, site_config_path, "place", elapsed)
    return artifact_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence place page artifacts.")
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
        artifact_dir = build_place_for_site(site_config)
        print(f"Built place page artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
