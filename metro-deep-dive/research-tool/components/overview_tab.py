"""Overview tab — three-frame scorecard + L/O scatter + key stats + CBSA map."""

from __future__ import annotations

import json
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import FRAME_COLORS
from dd_db import get_cbsa_key_stats, get_overlap_row, get_scatter_surface, get_trajectory_row
from components.ui_helpers import pct_rank, percentile_gauge

REPO_ROOT = Path(__file__).resolve().parents[3]
CBSA_GEOJSON = REPO_ROOT / "area-explorer" / "data" / "cbsa_boundaries.geojson"
COUNTY_GEOJSON = REPO_ROOT / "area-explorer" / "data" / "county_boundaries.geojson"

DIRECTION_HELP = {
    "diverging-improving": "Moving away from the national median in a positive direction — outperforming and gaining ground.",
    "converging-improving": "Moving toward the national median from below — improving but closing a gap.",
    "converging-declining": "Moving toward the national median from above — declining but from a strong position.",
    "diverging-declining": "Moving away from the national median in a negative direction — underperforming and losing ground.",
}


def render_overview(cbsa_code: str, cbsa_name: str, profile: dict) -> None:
    liv = profile.get("livability", {})
    opp = profile.get("opportunity", {})
    char = profile.get("character", {})
    cf = profile.get("cross_frame", {})

    # ------------------------------------------------------------------
    # Three-frame scorecard
    # ------------------------------------------------------------------
    st.subheader("Frame Scorecard")
    c1, c2, c3 = st.columns(3)

    with c1:
        pct = liv.get("livability_percentile") or liv.get("livability_percentile_rank")
        st.plotly_chart(
            percentile_gauge(pct, "Livability", FRAME_COLORS["livability"]),
            use_container_width=True,
        )
        cluster = liv.get("livability_cluster_name") or liv.get("livability_cluster", "—")
        top_s = (liv.get("top_subject") or "").replace("_", " ").title()
        bot_s = (liv.get("bottom_subject") or "").replace("_", " ").title()
        st.markdown(f"**{cluster}**")
        if top_s:
            st.caption(f"Strongest: {top_s}  |  Weakest: {bot_s}")

    with c2:
        pct = opp.get("opportunity_percentile") or opp.get("opportunity_percentile_rank")
        st.plotly_chart(
            percentile_gauge(pct, "Opportunity", FRAME_COLORS["opportunity"]),
            use_container_width=True,
        )
        cluster = opp.get("opportunity_cluster_name") or opp.get("opportunity_cluster", "—")
        top_s = (opp.get("top_subject") or "").replace("_", " ").title()
        bot_s = (opp.get("bottom_subject") or "").replace("_", " ").title()
        st.markdown(f"**{cluster}**")
        if top_s:
            st.caption(f"Strongest: {top_s}  |  Weakest: {bot_s}")

    with c3:
        pct = char.get("character_percentile") or char.get("character_percentile_rank")
        st.plotly_chart(
            percentile_gauge(pct, "Character", FRAME_COLORS["character"]),
            use_container_width=True,
        )
        cluster = char.get("character_cluster_name") or char.get("character_cluster", "—")
        st.markdown(f"**{cluster}**")

    st.divider()

    # ------------------------------------------------------------------
    # Cross-frame divergence flag
    # ------------------------------------------------------------------
    overlap = get_overlap_row(cbsa_code)
    if overlap:
        top_frame = (overlap.get("top_frame") or "—").title()
        top_pct = overlap.get("top_frame_percentile")
        bot_frame = (overlap.get("bottom_frame") or "—").title()
        bot_pct = overlap.get("bottom_frame_percentile")
        gap = overlap.get("frame_percentile_gap")
        signature = overlap.get("signature", "—")

        if gap and gap > 20:
            st.warning(
                f"**Cross-frame divergence:** Ranks **{pct_rank(top_pct)}** on {top_frame} "
                f"but **{pct_rank(bot_pct)}** on {bot_frame}. "
                f"Gap: {gap:.0f} pts · Signature: `{signature}`"
            )
        else:
            profile_label = (overlap.get("overlap_profile") or "—").replace("_", " ").title()
            st.info(
                f"**Frame alignment:** {profile_label} · Signature: `{signature}` · "
                f"Largest frame gap: {gap:.0f} pts"
            )

    # ------------------------------------------------------------------
    # Key Statistics
    # ------------------------------------------------------------------
    st.subheader("Key Statistics")
    stats = get_cbsa_key_stats(cbsa_code)

    pop = stats.get("pop_total")
    med_age = stats.get("median_age")
    pop_growth = stats.get("pop_growth_5yr")
    med_income = stats.get("median_hh_income")
    vti = stats.get("value_to_income")
    division = stats.get("division_name", "—")

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Population", f"{pop:,.0f}" if pop else "—")
    with k2:
        st.metric("Median Age", f"{med_age:.1f}" if med_age else "—")
    with k3:
        growth_str = f"+{pop_growth*100:.1f}%" if pop_growth and pop_growth >= 0 else (f"{pop_growth*100:.1f}%" if pop_growth else "—")
        st.metric("5yr Pop Growth", growth_str)
    with k4:
        st.metric("Median HH Income", f"${med_income:,.0f}" if med_income else "—")
    with k5:
        st.metric("Home Value / Income", f"{vti:.1f}×" if vti else "—")

    st.caption(f"Census Division: {division}")

    st.divider()

    # ------------------------------------------------------------------
    # CBSA boundary + county map
    # ------------------------------------------------------------------
    st.subheader("Geography")
    _render_cbsa_map(cbsa_code, cbsa_name)

    st.divider()

    # ------------------------------------------------------------------
    # L/O four-quadrant scatter
    # ------------------------------------------------------------------
    st.subheader("Livability vs. Opportunity — All Metros")
    scatter_df = get_scatter_surface()

    if not scatter_df.empty:
        fig = px.scatter(
            scatter_df,
            x="livability__livability_percentile",
            y="opportunity__opportunity_percentile",
            color="cross_frame_cluster_name",
            hover_name="cbsa_name",
            hover_data={
                "livability__livability_percentile": ":.0f",
                "opportunity__opportunity_percentile": ":.0f",
            },
            labels={
                "livability__livability_percentile": "Livability Percentile",
                "opportunity__opportunity_percentile": "Opportunity Percentile",
            },
            title="All 401 CBSAs",
        )

        sel_row = scatter_df[scatter_df["cbsa_code"] == cbsa_code]
        if not sel_row.empty:
            fig.add_trace(go.Scatter(
                x=sel_row["livability__livability_percentile"],
                y=sel_row["opportunity__opportunity_percentile"],
                mode="markers+text",
                marker=dict(size=16, color="black", symbol="star"),
                text=[cbsa_name],
                textposition="top center",
                name=cbsa_name,
                showlegend=True,
            ))

        fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.4)
        fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.4)
        fig.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ------------------------------------------------------------------
    # Trajectory Summary
    # ------------------------------------------------------------------
    st.subheader("Trajectory Summary")

    with st.expander("What do these directions mean?"):
        for direction, explanation in DIRECTION_HELP.items():
            icon = {"diverging-improving": "🟢", "converging-improving": "🟡",
                    "converging-declining": "🟠", "diverging-declining": "🔴"}.get(direction, "⚪")
            st.markdown(f"**{icon} {direction.replace('-', ' ').title()}** — {explanation}")

    traj = get_trajectory_row(cbsa_code)
    if traj:
        t1, t2, t3 = st.columns(3)
        for col, frame in [(t1, "livability"), (t2, "opportunity"), (t3, "character")]:
            with col:
                d = traj.get(f"{frame}_direction") or ""
                icon = {"diverging-improving": "🟢", "converging-improving": "🟡",
                        "converging-declining": "🟠", "diverging-declining": "🔴"}.get(d, "⚪")
                st.metric(frame.title(), f"{icon} {d.replace('-', ' ').title()}" if d else "—")


def _render_cbsa_map(cbsa_code: str, cbsa_name: str) -> None:
    if not CBSA_GEOJSON.exists() or not COUNTY_GEOJSON.exists():
        st.caption("Boundary files not found.")
        return

    try:
        with open(CBSA_GEOJSON) as f:
            cbsa_gj = json.load(f)
        with open(COUNTY_GEOJSON) as f:
            county_gj = json.load(f)
    except Exception as e:
        st.caption(f"Could not load boundary files: {e}")
        return

    # Filter to selected CBSA
    cbsa_feat = [f for f in cbsa_gj["features"] if f["properties"].get("cbsa_code") == cbsa_code]
    if not cbsa_feat:
        st.caption(f"No boundary found for CBSA {cbsa_code}.")
        return

    # Get county FIPS codes for this CBSA from xwalk
    from shared.db import get_connection
    con = get_connection()
    try:
        county_fips = con.execute(
            "SELECT county_geoid FROM silver.xwalk_cbsa_county WHERE cbsa_code = ?",
            [cbsa_code]
        ).fetchdf()["county_geoid"].tolist()
    finally:
        con.close()

    county_feats = [
        f for f in county_gj["features"]
        if f["properties"].get("county_fips") in county_fips
    ]

    if not county_feats:
        st.caption("County boundaries not found for this CBSA.")
        return

    # Compute centroid from CBSA boundary
    coords = []
    geom = cbsa_feat[0]["geometry"]
    if geom["type"] == "Polygon":
        coords = geom["coordinates"][0]
    elif geom["type"] == "MultiPolygon":
        coords = geom["coordinates"][0][0]
    if coords:
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        center = {"lat": sum(lats) / len(lats), "lon": sum(lons) / len(lons)}
    else:
        center = {"lat": 39.5, "lon": -98.35}

    # Build county choropleth (single color, outline only)
    county_df_rows = [
        {"county_geoid": f["properties"]["county_fips"], "val": 1}
        for f in county_feats
    ]
    import pandas as pd
    county_df = pd.DataFrame(county_df_rows)

    fig = px.choropleth_mapbox(
        county_df,
        geojson={"type": "FeatureCollection", "features": county_feats},
        locations="county_geoid",
        featureidkey="properties.county_fips",
        color="val",
        color_continuous_scale=[[0, "#BBDEFB"], [1, "#BBDEFB"]],
        mapbox_style="carto-positron",
        zoom=7,
        center=center,
        opacity=0.4,
    )

    # Overlay CBSA boundary as a line
    cbsa_geojson_single = {"type": "FeatureCollection", "features": cbsa_feat}
    cbsa_df = pd.DataFrame([{"cbsa_code": cbsa_code, "val": 1}])
    fig.add_trace(
        px.choropleth_mapbox(
            cbsa_df,
            geojson=cbsa_geojson_single,
            locations="cbsa_code",
            featureidkey="properties.cbsa_code",
            color="val",
            color_continuous_scale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
            opacity=0,
        ).data[0]
    )

    fig.update_layout(
        height=380,
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_showscale=False,
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"{cbsa_name} · {len(county_feats)} {'county' if len(county_feats) == 1 else 'counties'}")
