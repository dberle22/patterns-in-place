"""Build the POI overlay map product."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_site_artifact_dir, record_manifest_step, resolve_site_config_paths, time_step, write_dataframe
from data_builds.maps.shared import build_poi_rows
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_map_pois(site_config_path: str, artifact_dir: Path):
    """Build `map/poi_rows.csv` for one site."""

    site = load_site(site_config_path)
    rows, elapsed = time_step(site.site_id, "map.pois", lambda: build_poi_rows(site))
    map_dir = artifact_dir / "map"
    map_dir.mkdir(parents=True, exist_ok=True)
    write_dataframe(map_dir / "poi_rows.csv", rows)
    record_manifest_step(site, artifact_dir, site_config_path, "map_pois", elapsed)
    return rows, elapsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence POI map artifacts.")
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
        build_map_pois(site_config, artifact_dir)
        print(f"Built map POIs for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
