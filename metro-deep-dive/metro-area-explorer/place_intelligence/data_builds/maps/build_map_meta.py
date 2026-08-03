"""Build the context-map metadata product."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_site_artifact_dir, read_json, record_manifest_step, require_artifact_files, resolve_site_config_paths, time_step, write_json
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_map_meta(site_config_path: str, artifact_dir: Path):
    """Build `map/meta.json` by assembling previously-built map products."""

    site = load_site(site_config_path)
    map_dir = artifact_dir / "map"
    require_artifact_files(map_dir, ["core.json", "tract_fill_catalog.json"], "map.meta")
    core = read_json(map_dir / "core.json")
    tract_fill_catalog = read_json(map_dir / "tract_fill_catalog.json")
    payload, elapsed = time_step(
        site.site_id,
        "map.meta",
        lambda: {
            "site_point": core["site_point"],
            "view_state": core["view_state"],
            "tract_fill_years": {metric: values.get("year") for metric, values in tract_fill_catalog.items()},
            "tract_fill_sources": {metric: values.get("source_table") for metric, values in tract_fill_catalog.items()},
            "nfhl_service_status": core.get("nfhl_service_status"),
            "nfhl_service_error": core.get("nfhl_service_error"),
        },
    )
    write_json(map_dir / "meta.json", payload)
    record_manifest_step(site, artifact_dir, site_config_path, "map_meta", elapsed)
    return payload, elapsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence map meta artifacts.")
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
        build_map_meta(site_config, artifact_dir)
        print(f"Built map meta for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
