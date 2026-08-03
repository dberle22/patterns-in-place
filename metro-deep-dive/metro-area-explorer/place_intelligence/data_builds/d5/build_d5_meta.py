"""Build the D5 metadata contract from NFHL service status."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_site_artifact_dir, read_json, record_manifest_step, require_artifact_files, resolve_site_config_paths, time_step, write_json
from data_builds.d5.shared import build_d5_meta
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_d5_meta_artifact(site_config_path: str, artifact_dir: Path):
    """Build the small D5 meta contract from the NFHL service status artifact."""

    site = load_site(site_config_path)
    require_artifact_files(artifact_dir, ["d5_nfhl_status.json"], "d5.meta")
    nfhl_status = read_json(artifact_dir / "d5_nfhl_status.json")
    payload, elapsed = time_step(site.site_id, "d5.meta", lambda: build_d5_meta(nfhl_status))
    write_json(artifact_dir / "d5_meta.json", payload)
    record_manifest_step(site, artifact_dir, site_config_path, "d5_meta", elapsed)
    return payload, elapsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence D5 meta artifacts.")
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
        build_d5_meta_artifact(site_config, artifact_dir)
        print(f"Built D5 meta artifact for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
