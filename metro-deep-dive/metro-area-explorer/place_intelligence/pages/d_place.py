"""Place tab for the Place Intelligence brief."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st


SECTION_ROOT = Path(__file__).resolve().parents[1]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from shared_ui import (
    build_simple_bar_chart,
    build_simple_line_chart,
    format_count_cell,
    format_percent_cell,
    load_d3_payload,
    load_d4_payload,
    load_d5_payload,
    render_chart_result,
    render_context_map,
    render_html_table,
)


def render_page(site_config_path: str) -> None:
    """Render the physical-context page."""

    d3_payload = load_d3_payload(site_config_path)
    d4_payload = load_d4_payload(site_config_path)
    d5_payload = load_d5_payload(site_config_path)

    st.header("3. Place")

    st.subheader("Context map")
    render_context_map(
        site_config_path,
        default_layers={"tract_fill": False, "rings": True, "pois": True, "roads": True, "flood": True, "severed": True},
        map_key="place_map",
    )

    st.subheader("POI mix")
    poi_counts = d3_payload["poi_counts"]
    if poi_counts.empty:
        st.info("Competitive / complementary / anchor POI counts are unavailable for this site.")
    else:
        selected_ring = st.selectbox("POI ring", options=poi_counts["ring_mi"].drop_duplicates().tolist(), key="place_poi_ring")
        ring_counts = poi_counts.loc[poi_counts["ring_mi"] == selected_ring].copy()
        render_chart_result(
            build_simple_bar_chart(
                ring_counts,
                entity_col="poi_class",
                value_col="count",
                title=f"POI classes within {selected_ring} miles",
                subtitle="Direct point-in-ring counts from Overture",
                unit="count",
                decimals=0,
            )
        )
        ring_counts["count"] = ring_counts["count"].map(format_count_cell)
        render_html_table(ring_counts.rename(columns={"poi_class": "POI class", "count": "Count"}))

    st.subheader("Road hierarchy and corridor traffic")
    frontage = d4_payload["frontage_segments"]
    ranked = d4_payload["ranked_segments_1mi"]
    trend = d4_payload["frontage_trend"]
    if frontage.empty and ranked.empty:
        st.info("AADT corridor context is unavailable for this site.")
    else:
        st.caption(d4_payload["copy_note"])
        if not frontage.empty:
            display = frontage[["roadway", "aadt", "distance_mi"]].copy()
            display = display.rename(columns={"roadway": "Frontage roadway", "aadt": "AADT", "distance_mi": "Distance (mi)"})
            display["AADT"] = display["AADT"].map(format_count_cell)
            display["Distance (mi)"] = display["Distance (mi)"].map(lambda value: f"{float(value):.2f}")
            render_html_table(display)
        if not ranked.empty:
            render_chart_result(
                build_simple_bar_chart(
                    ranked.head(10),
                    entity_col="roadway",
                    value_col="aadt",
                    title="Top 1-mile corridor segments by AADT",
                    subtitle=f"Count year {d4_payload['count_year']}",
                    unit="count",
                    decimals=0,
                )
            )
        if not trend.empty:
            trend = trend.copy()
            trend["series"] = trend["roadway"]
            render_chart_result(
                build_simple_line_chart(
                    trend,
                    period_col="year",
                    value_col="aadt",
                    series_col="series",
                    title="Frontage AADT trend",
                    subtitle="Multi-year FDOT frontage series",
                    unit="count",
                    decimals=0,
                )
            )

    st.subheader("Barrier and severance detail")
    barrier_summary = d3_payload["barrier_summary"]
    ring_variants = d3_payload["ring_variants"]["comparison_table"]
    if barrier_summary.empty:
        st.info("No qualifying barrier features were returned for this site.")
    else:
        display = barrier_summary[
            ["ring_mi", "barrier_type", "feature_name", "crossing_count", "mean_crossing_spacing_mi", "severed_area_share", "severed_population_share", "summary"]
        ].copy()
        display = display.rename(
            columns={
                "ring_mi": "Ring (mi)",
                "barrier_type": "Barrier type",
                "feature_name": "Feature",
                "crossing_count": "Crossings",
                "mean_crossing_spacing_mi": "Mean spacing (mi)",
                "severed_area_share": "Severed area share",
                "severed_population_share": "Severed population share",
                "summary": "Summary",
            }
        )
        display["Severed area share"] = display["Severed area share"].map(format_percent_cell)
        display["Severed population share"] = display["Severed population share"].map(format_percent_cell)
        render_html_table(display)
    if not ring_variants.empty:
        render_html_table(
            ring_variants.rename(
                columns={
                    "ring_mi": "Ring (mi)",
                    "baseline_area_sqmi": "Baseline sq mi",
                    "water_adjusted_area_sqmi": "Water-adjusted sq mi",
                    "removed_area_share": "Removed area share",
                }
            )[["Ring (mi)", "Baseline sq mi", "Water-adjusted sq mi", "Removed area share"]]
        )

    st.subheader("Flood screening")
    zone = d5_payload["nfhl_site_zone"]
    shares = d5_payload["nfhl_ring_shares"]
    nri = d5_payload["nri_catchment_scores"]
    st.caption(d5_payload["copy_note"])
    if zone.empty and shares.empty and nri.empty:
        st.info("Flood screening data is unavailable for this site.")
    else:
        if not zone.empty:
            render_html_table(zone)
        if not shares.empty:
            share_chart_rows = shares.copy()
            share_chart_rows["entity"] = share_chart_rows["ring_mi"].astype(str) + " mi - " + share_chart_rows["flood_zone"].fillna("Unknown")
            render_chart_result(
                build_simple_bar_chart(
                    share_chart_rows,
                    entity_col="entity",
                    value_col="area_share",
                    title="Flood-zone area shares by ring",
                    subtitle="Projected NFHL polygon overlap",
                    unit="percent",
                    decimals=1,
                )
            )
        if not nri.empty:
            render_html_table(nri)
