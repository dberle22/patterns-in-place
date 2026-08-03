"""Build the compact Overview page contract for one or more Place Intelligence sites."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

import pandas as pd


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.common import (
    deserialize_resolved_site,
    deserialize_site,
    ensure_site_artifact_dir,
    read_dataframe,
    read_json,
    record_manifest_step,
    require_artifact_files,
    resolve_site_config_paths,
    time_step,
    write_json,
)
from site_prep import get_default_site_config_path, list_site_configs, load_site


def build_overview_for_site(site_config_path: str) -> Path:
    """Build the compact Overview artifact for one site."""

    site = load_site(site_config_path)
    artifact_dir = ensure_site_artifact_dir(site)
    require_artifact_files(
        artifact_dir,
        ["site.json", "resolved_site.json", "d2_metric_summary.csv", "d3_barrier_summary.csv", "d3_meta.json", "d5_nfhl_site_zone.csv"],
        "overview",
    )

    built_site = deserialize_site(read_json(artifact_dir / "site.json"))
    resolved_site = deserialize_resolved_site(read_json(artifact_dir / "resolved_site.json"), built_site)
    summary = read_dataframe(artifact_dir / "d2_metric_summary.csv")
    barrier_summary = read_dataframe(artifact_dir / "d3_barrier_summary.csv")
    d3_meta = read_json(artifact_dir / "d3_meta.json")
    flood_zone = read_dataframe(artifact_dir / "d5_nfhl_site_zone.csv").head(1)

    payload, elapsed = time_step(
        site.site_id,
        "overview",
        lambda: _build_overview_payload(built_site, resolved_site, summary, barrier_summary, d3_meta, flood_zone),
    )
    write_json(artifact_dir / "overview.json", payload)
    record_manifest_step(site, artifact_dir, site_config_path, "overview", elapsed)
    return artifact_dir


def _build_overview_payload(
    site,
    resolved_site,
    summary: pd.DataFrame,
    barrier_summary: pd.DataFrame,
    d3_meta: dict[str, Any],
    flood_zone: pd.DataFrame,
) -> dict[str, Any]:
    """Build the compact artifact contract used only by the Overview page."""

    headline_metrics = [
        "pop_total",
        "households",
        "median_hh_income",
        "pct_ba_plus",
        "median_home_value",
    ]
    headline_rows: list[dict[str, Any]] = []
    for metric in headline_metrics:
        metric_row = _lookup_summary_row(summary, metric)
        if metric_row is None:
            continue
        headline_rows.append(
            {
                "metric": metric,
                "metric_label": metric_row.get("metric_label"),
                "primary_value": metric_row.get("primary_value"),
                "primary_cbsa_percentile": metric_row.get("primary_cbsa_percentile"),
                "primary_change_5yr": metric_row.get("primary_change_5yr"),
                "primary_year": metric_row.get("primary_year"),
                "source_table": metric_row.get("source_table"),
            }
        )

    barrier_flags = pd.DataFrame()
    if not barrier_summary.empty and "site_card_flag" in barrier_summary.columns:
        barrier_flags = barrier_summary.loc[barrier_summary["site_card_flag"]].copy()
    flag_rows = [{"flag": "Barrier screen", "detail": str(row["summary"])} for _, row in barrier_flags.iterrows()]
    if not flood_zone.empty:
        flood_zone_row = flood_zone.iloc[0]
        zone = flood_zone_row.get("flood_zone")
        subtype = flood_zone_row.get("zone_subtype")
        panel_date = flood_zone_row.get("panel_effective_date")
        detail = "Unavailable" if pd.isna(zone) else f"Zone {zone}"
        if pd.notna(subtype):
            detail = f"{detail} | {subtype}"
        if pd.notna(panel_date):
            detail = f"{detail} | panel date {panel_date}"
        flag_rows.append({"flag": "Flood zone", "detail": detail})

    return _json_safe(
        {
        "site": {
            "site_id": site.site_id,
            "address": site.address,
            "primary_ring_mi": int(site.primary_ring_mi),
        },
        "resolved_site": {
            "lat": resolved_site.lat,
            "lon": resolved_site.lon,
            "tract_geoid": resolved_site.tract_geoid,
            "matched_address": resolved_site.matched_address,
            "match_type": resolved_site.match_type,
            "geocode_source": resolved_site.geocode_source,
        },
        "page_meta": {
            "primary_ring_mi": int(site.primary_ring_mi),
            "node_typology_label": d3_meta.get("node_typology_label"),
            "summary_note": "Primary-ring summary metrics are apportioned from tract-grain data unless noted otherwise.",
        },
        "site_cards": {
            "population": _build_overview_card(summary, "pop_total", value_key="primary_value", delta_key="primary_cbsa_percentile"),
            "income": _build_overview_card(summary, "median_hh_income", value_key="primary_value", delta_key="primary_change_5yr"),
            "flood_zone": None if flood_zone.empty else flood_zone.iloc[0].to_dict(),
        },
        "headline_table": headline_rows,
        "flags": flag_rows,
        }
    )


def _build_overview_card(
    summary: pd.DataFrame,
    metric: str,
    *,
    value_key: str,
    delta_key: str,
) -> dict[str, Any] | None:
    """Return one small summary-card record from the D2 metric summary."""

    metric_row = _lookup_summary_row(summary, metric)
    if metric_row is None:
        return None
    return {
        "metric": metric,
        "metric_label": metric_row.get("metric_label"),
        "value": metric_row.get(value_key),
        "delta": metric_row.get(delta_key),
    }


def _lookup_summary_row(summary: pd.DataFrame, metric: str) -> dict[str, Any] | None:
    """Return one summary row as a plain dict when the metric exists."""

    if summary.empty or "metric" not in summary.columns:
        return None
    match = summary.loc[summary["metric"] == metric].head(1)
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def _json_safe(value: Any) -> Any:
    """Convert pandas and NaN-heavy payload fragments into strict JSON-safe values."""

    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if pd.isna(value):
        return None
    return value


def parse_args() -> argparse.Namespace:
    """Parse the small CLI surface for Overview builds."""

    parser = argparse.ArgumentParser(description="Build Place Intelligence overview page artifacts.")
    parser.add_argument("site_configs", nargs="*", help="Optional site YAML paths.")
    parser.add_argument("--all-sites", action="store_true", help="Build every discovered site YAML.")
    return parser.parse_args()


def main() -> int:
    """Build Overview artifacts for the requested sites."""

    args = parse_args()
    site_configs = resolve_site_config_paths(
        args.site_configs,
        all_sites=args.all_sites,
        default_site_config_path=str(get_default_site_config_path()),
        discovered_site_configs=[str(path) for path in list_site_configs()],
    )

    for site_config in site_configs:
        artifact_dir = build_overview_for_site(site_config)
        print(f"Built overview page artifacts for {Path(site_config).name} -> {artifact_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
