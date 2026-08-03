"""Build the compact People page contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_site_artifact_dir, read_dataframe, read_json, record_manifest_step, require_artifact_files, resolve_site_config_paths, time_step, write_json
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_people_for_site(site_config_path: str) -> Path:
    """Build `people.json` for one site."""

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    require_artifact_files(
        artifact_dir,
        ["site.json", "d2_metric_summary.csv", "d2_catchment_profile.csv", "d3_daytime_population.csv"],
        "people",
    )
    payload, elapsed = time_step(
        site.site_id,
        "people",
        lambda: {
            "site": read_json(artifact_dir / "site.json"),
            "metric_summary": read_dataframe(artifact_dir / "d2_metric_summary.csv").to_dict("records"),
            "catchment_profile": read_dataframe(artifact_dir / "d2_catchment_profile.csv").to_dict("records"),
            "daytime_population": read_dataframe(artifact_dir / "d3_daytime_population.csv").to_dict("records"),
        },
    )
    write_json(artifact_dir / "people.json", payload)
    record_manifest_step(site, artifact_dir, site_config_path, "people", elapsed)
    return artifact_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence people page artifacts.")
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
        artifact_dir = build_people_for_site(site_config)
        print(f"Built people page artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
