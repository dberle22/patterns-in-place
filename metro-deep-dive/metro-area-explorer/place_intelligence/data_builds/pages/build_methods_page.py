"""Build the compact Methods page contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import ensure_site_artifact_dir, read_dataframe, read_json, record_manifest_step, require_artifact_files, resolve_site_config_paths, time_step, write_json
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_methods_for_site(site_config_path: str) -> Path:
    """Build `methods.json` for one site."""

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    require_artifact_files(
        artifact_dir,
        ["site.json", "resolved_site.json", "base_coverage_diagnostic.csv", "d2_skip_reasons.csv", "d2_metric_long.csv"],
        "methods",
    )
    payload, elapsed = time_step(
        site.site_id,
        "methods",
        lambda: _build_methods_payload(
            read_json(artifact_dir / "site.json"),
            read_json(artifact_dir / "resolved_site.json"),
            read_dataframe(artifact_dir / "base_coverage_diagnostic.csv"),
            read_dataframe(artifact_dir / "d2_skip_reasons.csv"),
            read_dataframe(artifact_dir / "d2_metric_long.csv"),
        ),
    )
    write_json(artifact_dir / "methods.json", payload)
    record_manifest_step(site, artifact_dir, site_config_path, "methods", elapsed)
    return artifact_dir


def _build_methods_payload(site: dict, resolved_site: dict, coverage: pd.DataFrame, skip_reasons: pd.DataFrame, metric_long: pd.DataFrame) -> dict:
    """Assemble a compact Methods contract from already-built artifacts."""

    catchment = metric_long.loc[metric_long["record_type"] == "catchment"].copy() if not metric_long.empty and "record_type" in metric_long.columns else pd.DataFrame()
    source_vintages = catchment[["metric_label", "year", "source_table"]].drop_duplicates().sort_values(["source_table", "metric_label"]) if not catchment.empty else pd.DataFrame()
    return {
        "site": site,
        "resolved_site": resolved_site,
        "coverage_diagnostic": coverage.to_dict("records"),
        "skip_reasons": skip_reasons.to_dict("records"),
        "source_vintages": source_vintages.to_dict("records"),
        "method_notes": [
            "Catchment numbers are tract-apportioned using areal weights rather than centroid inclusion.",
            "Straight-line rings remain the baseline context surface; the barrier screen is a heuristic, not a routing model.",
            "D4 traffic counts and D5 FEMA layers stay fail-soft, so temporary source outages do not break the rest of the brief.",
            "The Market tab is intentionally compact and is a candidate for a reusable Metro Deep Dive summary component.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Place Intelligence methods page artifacts.")
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
        artifact_dir = build_methods_for_site(site_config)
        print(f"Built methods page artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
