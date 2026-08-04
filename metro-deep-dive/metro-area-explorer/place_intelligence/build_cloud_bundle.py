"""Build a slim publish-ready artifact bundle for Streamlit Cloud."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import shutil
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parent
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from artifact_store import CLOUD_BUNDLE_DIRNAME, PUBLISHED_SITE_ARTIFACTS_DIRNAME
from data_builds.common import get_site_artifact_dir, read_json, resolve_site_config_paths, write_json
from site_prep import D6_TRACT_FILL_METRICS, get_default_site_config_path, list_site_configs, load_site


CLOUD_BUNDLE_ROOT = SECTION_ROOT / CLOUD_BUNDLE_DIRNAME
SITE_CONFIGS_DIRNAME = "site_configs"
STATIC_RELATIVE_PATHS = [
    "manifest.json",
    "overview.json",
    "people.json",
    "place.json",
    "market_page.json",
    "methods.json",
    "site.json",
    "resolved_site.json",
    "map/meta.json",
    "map/rings.geojson",
    "map/roads.geojson",
    "map/poi_rows.csv",
    "map/severed_area.geojson",
    "map/water_adjusted_rings.geojson",
]


def build_cloud_bundle(site_config_path: str) -> Path:
    """Copy the smallest app-facing artifact set for one site into `cloud_bundle/`."""

    site = load_site(site_config_path)
    source_dir = get_site_artifact_dir(site)
    if not (source_dir / "manifest.json").exists():
        raise FileNotFoundError(
            f"Cannot build a cloud bundle for '{site.site_id}' because local built artifacts are missing at {source_dir}."
        )

    bundle_site_dir = CLOUD_BUNDLE_ROOT / PUBLISHED_SITE_ARTIFACTS_DIRNAME / site.site_id
    if bundle_site_dir.exists():
        shutil.rmtree(bundle_site_dir)
    bundle_site_dir.mkdir(parents=True, exist_ok=True)

    copied_files: list[str] = []
    for rel_path in _bundle_relative_paths():
        source_path = source_dir / rel_path
        if not source_path.exists():
            continue
        target_path = bundle_site_dir / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        copied_files.append(rel_path)

    config_dir = CLOUD_BUNDLE_ROOT / SITE_CONFIGS_DIRNAME
    config_dir.mkdir(parents=True, exist_ok=True)
    copied_site_config = config_dir / Path(site_config_path).name
    shutil.copy2(site_config_path, copied_site_config)

    bundle_manifest = {
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "site_id": site.site_id,
        "market_id": site.market_id,
        "source_site_config": Path(site_config_path).name,
        "source_artifact_dir": str(source_dir.relative_to(SECTION_ROOT)),
        "copied_files": copied_files,
        "excluded_files": [
            "map/flood.geojson",
            "intermediate build CSVs not required by the Streamlit app",
        ],
    }
    write_json(bundle_site_dir / "cloud_bundle_manifest.json", bundle_manifest)
    return bundle_site_dir


def _bundle_relative_paths() -> list[str]:
    """Return the app-facing files that belong in the Streamlit Cloud bundle."""

    tract_fill_paths = [f"map/tract_fill_{metric}.geojson" for metric in D6_TRACT_FILL_METRICS]
    return STATIC_RELATIVE_PATHS + tract_fill_paths


def parse_args() -> argparse.Namespace:
    """Parse the small CLI surface for cloud-bundle builds."""

    parser = argparse.ArgumentParser(description="Build a slim Place Intelligence cloud bundle.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build cloud bundles for every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    """Materialize one or more cloud bundles under `cloud_bundle/`."""

    args = parse_args()
    site_configs = resolve_site_config_paths(
        args.site_configs,
        all_sites=args.all_sites,
        default_site_config_path=str(get_default_site_config_path()),
        discovered_site_configs=[str(path) for path in list_site_configs()],
    )

    for site_config in site_configs:
        bundle_site_dir = build_cloud_bundle(site_config)
        manifest = read_json(bundle_site_dir / "cloud_bundle_manifest.json")
        print(
            f"Built cloud bundle for {Path(site_config).name} -> {bundle_site_dir} "
            f"({len(manifest['copied_files'])} files)",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
