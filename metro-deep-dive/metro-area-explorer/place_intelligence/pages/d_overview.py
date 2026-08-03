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
    load_overview_payload,
    render_context_map,
    render_html_table,
    source_label,
)


def render_page(site_config_path: str) -> None:
    """Render the orientation-first overview page."""

    overview = load_overview_payload(site_config_path)
    site = overview["site"]
    resolved = overview["resolved_site"]
    page_meta = overview["page_meta"]
    headline_rows = pd.DataFrame(overview["headline_table"])
    flags = pd.DataFrame(overview["flags"])
    population_card = overview["site_cards"]["population"]
    income_card = overview["site_cards"]["income"]
    flood_zone_card = overview["site_cards"]["flood_zone"]

    st.header("1. Overview")
    st.caption(page_meta["summary_note"])

    metrics = st.columns(4)
    _render_overview_card(metrics[0], "Site", site["address"], "")
    value = None if population_card is None else population_card["value"]
    _render_overview_card(
        metrics[1],
        f"{page_meta['primary_ring_mi']}-mile population",
        format_count_cell(value),
        "Ring total; no tract percentile shown for this aggregate.",
    )
    value = None if income_card is None else income_card["value"]
    change = None if income_card is None else income_card["delta"]
    _render_overview_card(
        metrics[2],
        f"{page_meta['primary_ring_mi']}-mile HH income",
        format_currency_cell(value),
        format_currency_cell(change),
    )
    zone = None if flood_zone_card is None else flood_zone_card.get("flood_zone")
    subtype = None if flood_zone_card is None else flood_zone_card.get("zone_subtype")
    flood_detail = "Minimal hazard" if zone == "X" else subtype or ""
    _render_overview_card(metrics[3], "Site flood zone", "Unavailable" if pd.isna(zone) else str(zone), flood_detail)

    st.caption(
        f"Resolved coordinates: {float(resolved['lat']):.6f}, {float(resolved['lon']):.6f} | "
        f"Geocode: {resolved['geocode_source']} ({resolved['match_type']})"
    )

    st.subheader("Context map")
    render_context_map(
        site_config_path,
        default_layers={"tract_fill": False, "rings": True, "pois": True, "roads": True, "flood": False, "severed": False},
        map_key="overview_map",
        allow_flood_layer=False,
    )
    st.caption("Road overlays use FDOT AADT segments where available. AADT means annual average daily traffic.")

    st.subheader("Primary-ring headline table")
    if headline_rows.empty:
        st.info("Primary-ring catchment metrics are unavailable for this site.")
    else:
        display = headline_rows.copy()
        display = display.rename(
            columns={
                "metric": "metric",
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
            if str(row["metric"]).startswith("pct_")
            else format_currency_cell(row["Primary ring value"])
            if str(row["metric"]) in {"median_hh_income", "median_home_value"}
            else format_count_cell(row["Primary ring value"]),
            axis=1,
        )
        display["CBSA percentile"] = display["CBSA percentile"].map(lambda value: "—" if pd.isna(value) else f"{float(value):.0f}th")
        display["5-year change"] = display.apply(
            lambda row: _format_change_cell(row["metric"], row["5-year change"]),
            axis=1,
        )
        display["Source"] = display["Source"].map(source_label)
        render_html_table(display.drop(columns=["metric"]))
    if not flags.empty:
        flood_rows = flags.loc[flags["flag"] == "Flood zone"].copy()
        if not flood_rows.empty:
            st.caption(str(flood_rows["detail"].iloc[0]))


def _format_change_cell(metric: str, value: object) -> str:
    """Format Overview change values in the same unit family as the headline metric."""

    if pd.isna(value):
        return "—"
    if str(metric).startswith("pct_"):
        return f"{float(value) * 100:+.1f} pp"
    if str(metric) in {"median_hh_income", "median_home_value"}:
        return format_currency_cell(value)
    return format_count_cell(value)


def _render_overview_card(container, label: str, value: str, detail: str) -> None:
    """Render one compact overview card with smaller typography than Streamlit metrics."""

    container.markdown(
        f"""
        <div style="padding:0.35rem 0.2rem 0.6rem 0.2rem;">
          <div style="font-size:0.78rem;color:#6b7280;line-height:1.1;">{label}</div>
          <div style="font-size:1.05rem;font-weight:600;line-height:1.2;word-break:break-word;">{value}</div>
          <div style="font-size:0.72rem;color:#4b5563;line-height:1.15;min-height:1.4rem;">{detail or ''}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
