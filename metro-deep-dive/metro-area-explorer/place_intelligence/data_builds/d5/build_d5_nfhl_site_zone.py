"""Build the D5 NFHL site-zone output."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_site_artifact_dir, record_manifest_step, resolve_site_config_paths, time_step, write_dataframe, write_json
from data_builds.d5.shared import build_nfhl_site_zone_payload
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_d5_nfhl_site_zone(site_config_path: str, artifact_dir: Path):
    """Build the parcel-level NFHL zone output for one site."""

    site = load_site(site_config_path)
    result, elapsed = time_step(site.site_id, "d5.nfhl_site_zone", lambda: build_nfhl_site_zone_payload(site))
    frame, status = result
    write_dataframe(artifact_dir / "d5_nfhl_site_zone.csv", frame)
    write_json(artifact_dir / "d5_nfhl_status.json", status)
    record_manifest_step(site, artifact_dir, site_config_path, "d5_nfhl_site_zone", elapsed)
    return result, elapsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence D5 NFHL site zone artifacts.")
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
        build_d5_nfhl_site_zone(site_config, artifact_dir)
        print(f"Built D5 NFHL site zone artifact for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
