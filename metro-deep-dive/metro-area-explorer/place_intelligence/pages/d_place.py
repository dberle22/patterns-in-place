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
    load_context_map_payload,
    load_place_payload,
    render_chart_result,
    render_context_map,
    render_html_table,
)


def render_page(site_config_path: str) -> None:
    """Render the physical-context page."""

    payload = load_place_payload(site_config_path)
    frontage = pd.DataFrame(payload.get("frontage_segments", []))
    trend = pd.DataFrame(payload.get("frontage_trend", []))
    d4_meta = payload.get("d4_meta", {})
    zone = pd.DataFrame(payload.get("nfhl_site_zone", []))
    shares = pd.DataFrame(payload.get("nfhl_ring_shares", []))
    nri = pd.DataFrame(payload.get("nri_catchment_scores", []))
    d5_meta = payload.get("d5_meta", {})

    st.header("3. Place")

    st.subheader("Context map")
    render_context_map(
        site_config_path,
        default_layers={"tract_fill": False, "rings": True, "pois": True, "roads": True, "flood": False, "severed": False},
        map_key="place_map",
        allow_flood_layer=False,
    )

    st.subheader("POI mix")
    map_payload = load_context_map_payload(site_config_path, "pop_total", False)
    poi_rows = map_payload["poi_rows"] if "poi_rows" in map_payload else pd.DataFrame()
    if poi_rows.empty:
        st.info("Overture POI rows are unavailable for this site.")
    else:
        selected_ring = st.selectbox("POI ring", options=sorted(poi_rows["ring_mi"].drop_duplicates().tolist()), key="place_poi_ring")
        ring_counts = (
            poi_rows.loc[poi_rows["ring_mi"] == selected_ring]
            .groupby("display_category", as_index=False)
            .size()
            .rename(columns={"size": "count", "display_category": "category"})
            .sort_values("count", ascending=False, kind="mergesort")
            .head(12)
        )
        render_chart_result(
            build_simple_bar_chart(
                ring_counts,
                entity_col="category",
                value_col="count",
                title=f"Overture POI categories within {selected_ring} miles",
                subtitle="Direct point-in-ring counts from Overture standard categories",
                unit="count",
                decimals=0,
            )
        )
        ring_counts["count"] = ring_counts["count"].map(format_count_cell)
        render_html_table(ring_counts.rename(columns={"category": "Category", "count": "Count"}))

    st.subheader("Road hierarchy and corridor traffic")
    if frontage.empty and trend.empty:
        st.info("AADT corridor context is unavailable for this site.")
    else:
        st.caption(d4_meta.get("copy_note"))
        if not frontage.empty:
            display = frontage[["roadway", "aadt", "distance_mi"]].copy()
            display = display.rename(columns={"roadway": "Frontage roadway", "aadt": "AADT", "distance_mi": "Distance (mi)"})
            display["AADT"] = display["AADT"].map(format_count_cell)
            display["Distance (mi)"] = display["Distance (mi)"].map(lambda value: f"{float(value):.2f}")
            render_html_table(display)
        if not trend.empty:
            trend = trend.copy()
            trend["series"] = trend["series_role"].fillna("frontage").astype(str).str.replace("_", " ").str.title()
            chart = build_simple_line_chart(
                trend,
                period_col="year",
                value_col="aadt",
                series_col="series",
                title="Frontage AADT trend",
                subtitle="Multi-year FDOT frontage series",
                unit="count",
                decimals=0,
            )
            if chart is None:
                st.info("Frontage trend is unavailable for the currently selected frontage segments.")
            else:
                render_chart_result(chart)

    st.subheader("Environmental risk")
    st.caption(d5_meta.get("copy_note"))
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
