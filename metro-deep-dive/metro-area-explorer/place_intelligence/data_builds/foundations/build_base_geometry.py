"""Build the base geometry artifacts for one or more Place Intelligence sites."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import (
    deserialize_site,
    deserialize_resolved_site,
    ensure_site_artifact_dir,
    read_json,
    record_manifest_step,
    require_artifact_files,
    resolve_site_config_paths,
    time_step,
    write_geojson,
)
from site_prep import build_cumulative_rings_for_site, get_default_site_config_path, list_site_configs, load_site


def build_base_geometry_for_site(site_config_path: str) -> Path:
    """Build cumulative ring geometry for one site."""

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    require_artifact_files(artifact_dir, ["site.json", "resolved_site.json"], "base_geometry")

    built_site = deserialize_site(read_json(artifact_dir / "site.json"))
    resolved_site = deserialize_resolved_site(read_json(artifact_dir / "resolved_site.json"), built_site)
    cumulative_rings, elapsed = time_step(
        built_site.site_id,
        "base_geometry",
        lambda: build_cumulative_rings_for_site(built_site, resolved_site=resolved_site),
    )

    write_geojson(artifact_dir / "base_cumulative_rings.geojson", cumulative_rings.to_crs("EPSG:4326"))
    record_manifest_step(site, artifact_dir, site_config_path, "base_geometry", elapsed)
    return artifact_dir


def parse_args() -> argparse.Namespace:
    """Parse the small CLI surface for geometry builds."""

    parser = argparse.ArgumentParser(description="Build Place Intelligence base geometry artifacts.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    """Build base geometry artifacts for the requested sites."""

    args = parse_args()
    site_configs = resolve_site_config_paths(
        args.site_configs,
        all_sites=args.all_sites,
        default_site_config_path=str(get_default_site_config_path()),
        discovered_site_configs=[str(path) for path in list_site_configs()],
    )

    for site_config in site_configs:
        artifact_dir = build_base_geometry_for_site(site_config)
        print(f"Built base geometry artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

