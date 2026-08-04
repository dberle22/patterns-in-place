"""Build the site identity artifacts for one or more Place Intelligence sites."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import (
    ensure_site_artifact_dir,
    record_manifest_step,
    resolve_site_config_paths,
    serialize_resolved_site,
    serialize_site,
    time_step,
    write_json,
)
from site_prep import get_default_site_config_path, list_site_configs, load_site, resolve_site


def build_site_identity_for_site(site_config_path: str) -> Path:
    """Build site identity artifacts for one site."""

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    resolved_site, elapsed = time_step(site.site_id, "site_identity", lambda: resolve_site(site))

    write_json(artifact_dir / "site.json", serialize_site(site))
    write_json(artifact_dir / "resolved_site.json", serialize_resolved_site(resolved_site))
    record_manifest_step(site, artifact_dir, site_config_path, "site_identity", elapsed)
    return artifact_dir


def parse_args() -> argparse.Namespace:
    """Parse the small CLI surface for identity builds."""

    parser = argparse.ArgumentParser(description="Build Place Intelligence site identity artifacts.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    """Build site identity artifacts for the requested sites."""

    args = parse_args()
    site_configs = resolve_site_config_paths(
        args.site_configs,
        all_sites=args.all_sites,
        default_site_config_path=str(get_default_site_config_path()),
        discovered_site_configs=[str(path) for path in list_site_configs()],
    )

    for site_config in site_configs:
        artifact_dir = build_site_identity_for_site(site_config)
        print(f"Built site identity artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

