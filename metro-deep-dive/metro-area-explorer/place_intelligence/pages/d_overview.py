"""Overview tab for the Place Intelligence brief."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st


SECTION_ROOT = Path(__file__).resolve().parents[1]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from shared_ui import (
    format_count_cell,
    format_currency_cell,
    format_percent_cell,
    load_d2_payload,
    load_d3_payload,
    load_d5_payload,
    load_site_base_payload,
    render_context_map,
    render_html_table,
)


def render_page(site_config_path: str) -> None:
    """Render the orientation-first overview page."""

    base = load_site_base_payload(site_config_path)
    d2_payload = load_d2_payload(site_config_path)
    d3_payload = load_d3_payload(site_config_path)
    d5_payload = load_d5_payload(site_config_path)
    site = base["site"]
    resolved = base["resolved_site"]

    st.header("1. Overview")
    st.caption("Primary-ring summary metrics are apportioned from tract-grain data unless noted otherwise.")

    summary = d2_payload.get("metric_summary", pd.DataFrame())
    profile = d2_payload["catchment_profile"]
    has_profile_schema = {"ring_mi", "metric", "metric_label", "value"}.issubset(profile.columns)
    primary = profile.loc[profile["ring_mi"] == site.primary_ring_mi].copy() if has_profile_schema and not profile.empty else pd.DataFrame()
    summary_lookup = summary.set_index("metric") if not summary.empty and "metric" in summary.columns else None
    population_primary = primary.loc[primary["metric"] == "pop_total"] if has_profile_schema and not primary.empty else pd.DataFrame()
    income_primary = primary.loc[primary["metric"] == "median_hh_income"] if has_profile_schema and not primary.empty else pd.DataFrame()
    barrier_flags = d3_payload["barrier_summary"].loc[d3_payload["barrier_summary"]["site_card_flag"]].copy()
    flood_zone = d5_payload["nfhl_site_zone"].head(1)

    metrics = st.columns(5)
    with metrics[0]:
        st.metric("Site", site.address)
    with metrics[1]:
        st.metric("Node typology", d3_payload["node_typology_label"])
    with metrics[2]:
        value = summary_lookup.loc["pop_total", "primary_value"] if summary_lookup is not None and "pop_total" in summary_lookup.index else (population_primary["value"].iloc[0] if not population_primary.empty else None)
        pct = summary_lookup.loc["pop_total", "primary_cbsa_percentile"] if summary_lookup is not None and "pop_total" in summary_lookup.index else (population_primary["cbsa_percentile"].iloc[0] if not population_primary.empty else None)
        st.metric("3-mile population", format_count_cell(value), None if pd.isna(pct) else f"{pct:.0f}th pct")
    with metrics[3]:
        value = summary_lookup.loc["median_hh_income", "primary_value"] if summary_lookup is not None and "median_hh_income" in summary_lookup.index else (income_primary["value"].iloc[0] if not income_primary.empty else None)
        change = summary_lookup.loc["median_hh_income", "primary_change_5yr"] if summary_lookup is not None and "median_hh_income" in summary_lookup.index else (income_primary["change_5yr"].iloc[0] if not income_primary.empty else None)
        st.metric("3-mile HH income", format_currency_cell(value), format_currency_cell(change))
    with metrics[4]:
        zone = None if flood_zone.empty else flood_zone["flood_zone"].iloc[0]
        st.metric("Site flood zone", "Unavailable" if pd.isna(zone) else zone)

    st.caption(
        f"Resolved coordinates: {resolved.lat:.6f}, {resolved.lon:.6f} | "
        f"Geocode: {resolved.geocode_source} ({resolved.match_type})"
    )

    st.subheader("Context map")
    render_context_map(
        site_config_path,
        default_layers={"tract_fill": True, "rings": True, "pois": False, "roads": False, "flood": False, "severed": False},
        map_key="overview_map",
    )

    st.subheader("Primary-ring headline table")
    if not summary.empty:
        display = summary.loc[
            summary["metric"].isin(["pop_total", "households", "median_hh_income", "pct_ba_plus", "median_home_value"])
        ][["metric_label", "primary_value", "primary_cbsa_percentile", "primary_change_5yr", "primary_year", "source_table"]].copy()
        display = display.rename(
            columns={
                "metric_label": "Metric",
                "primary_value": "Primary ring value",
                "primary_cbsa_percentile": "CBSA percentile",
                "primary_change_5yr": "5-year change",
                "primary_year": "Year",
                "source_table": "Source",
            }
        )
        display["Primary ring value"] = display.apply(
            lambda row: format_percent_cell(row["Primary ring value"])
            if "share" in str(row["Metric"]).lower()
            else format_currency_cell(row["Primary ring value"])
            if "income" in str(row["Metric"]).lower() or "value" in str(row["Metric"]).lower()
            else format_count_cell(row["Primary ring value"]),
            axis=1,
        )
        display["CBSA percentile"] = display["CBSA percentile"].map(lambda value: "—" if pd.isna(value) else f"{float(value):.0f}th")
        display["5-year change"] = display["5-year change"].map(
            lambda value: "—" if pd.isna(value) else f"{float(value):,.1f}"
        )
        render_html_table(display)
    elif primary.empty:
        st.info("Primary-ring catchment metrics are unavailable for this site.")
    else:
        display = primary.loc[
            primary["metric"].isin(["pop_total", "households", "median_hh_income", "pct_ba_plus", "median_home_value"])
        ][["metric_label", "value", "cbsa_percentile", "change_5yr", "year", "source_table"]].copy()
        display = display.rename(
            columns={
                "metric_label": "Metric",
                "value": "Primary ring value",
                "cbsa_percentile": "CBSA percentile",
                "change_5yr": "5-year change",
                "year": "Year",
                "source_table": "Source",
            }
        )
        display["Primary ring value"] = display.apply(
            lambda row: format_percent_cell(row["Primary ring value"])
            if "share" in str(row["Metric"]).lower()
            else format_currency_cell(row["Primary ring value"])
            if "income" in str(row["Metric"]).lower() or "value" in str(row["Metric"]).lower()
            else format_count_cell(row["Primary ring value"]),
            axis=1,
        )
        display["CBSA percentile"] = display["CBSA percentile"].map(lambda value: "—" if pd.isna(value) else f"{float(value):.0f}th")
        display["5-year change"] = display["5-year change"].map(
            lambda value: "—" if pd.isna(value) else f"{float(value):,.1f}"
        )
        render_html_table(display)

    st.subheader("Flags and caveats")
    if barrier_flags.empty and flood_zone.empty:
        st.info("No primary-ring barrier flag or site flood-zone note surfaced to the site card.")
    else:
        rows = []
        for _, row in barrier_flags.iterrows():
            rows.append({"Flag": "Barrier screen", "Detail": row["summary"]})
        if not flood_zone.empty:
            rows.append(
                {
                    "Flag": "Flood zone",
                    "Detail": f"Zone {flood_zone['flood_zone'].iloc[0]} | panel date {flood_zone['panel_effective_date'].iloc[0]}",
                }
            )
        render_html_table(pd.DataFrame(rows))
