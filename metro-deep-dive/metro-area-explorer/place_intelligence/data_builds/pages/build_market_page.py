"""Build the compact Market page contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_site_artifact_dir, read_dataframe, read_json, record_manifest_step, require_artifact_files, resolve_site_config_paths, time_step, write_json
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_market_page_for_site(site_config_path: str) -> Path:
    """Build `market_page.json` for one site."""

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    require_artifact_files(
        artifact_dir,
        ["market_employment_mix.csv", "market_gdp_mix.csv", "market_housing_context.csv", "market_meta.json"],
        "market_page",
    )
    payload, elapsed = time_step(
        site.site_id,
        "market_page",
        lambda: {
            "employment_mix": read_dataframe(artifact_dir / "market_employment_mix.csv").to_dict("records"),
            "gdp_mix": read_dataframe(artifact_dir / "market_gdp_mix.csv").to_dict("records"),
            "housing_context": read_dataframe(artifact_dir / "market_housing_context.csv").to_dict("records"),
            "meta": read_json(artifact_dir / "market_meta.json"),
        },
    )
    write_json(artifact_dir / "market_page.json", payload)
    record_manifest_step(site, artifact_dir, site_config_path, "market_page", elapsed)
    return artifact_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence market page artifacts.")
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
        artifact_dir = build_market_page_for_site(site_config)
        print(f"Built market page artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
