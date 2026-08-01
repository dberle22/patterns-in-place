"""D5 page for the Industry explorer."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

SECTION_ROOT = Path(__file__).resolve().parents[1]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_prep import D5_DEFAULT_PEER_COUNT, build_d5_mix_chart, get_d5_page_payload
from shared_ui import format_jobs_cell, format_ratio_cell


def _render_chart(chart_result) -> None:
    """Render chart-engine output through Streamlit Vega-Lite."""
    spec = chart_result.chart.to_dict()
    st.vega_lite_chart(spec, width="stretch")


def _render_html_table(df: pd.DataFrame) -> None:
    """Render compact HTML tables for dense review surfaces."""
    st.markdown(df.fillna("—").to_html(index=False), unsafe_allow_html=True)


def _build_lodes_chart(rows: pd.DataFrame):
    """Render the D5 jobs-to-workers benchmark as a horizontal comparison bar chart."""
    if rows.empty:
        return None

    plot_rows = rows.copy().sort_values(
        ["jobs_to_workers_ratio", "entity"],
        ascending=[False, True],
        kind="mergesort",
        na_position="last",
    )
    fig = px.bar(
        plot_rows,
        x="jobs_to_workers_ratio",
        y="entity",
        orientation="h",
        color="entity_type",
        color_discrete_map={
            "market": "#1D4ED8",
            "peer": "#64748B",
            "benchmark": "#B45309",
        },
        hover_data={
            "jobs_to_workers_ratio": ":.2f",
            "jobs_minus_workers": ":,.0f",
            "jobs_total": ":,.0f",
            "workers_total": ":,.0f",
            "entity_type": False,
        },
        labels={
            "jobs_to_workers_ratio": "Jobs / resident workers",
            "entity": "",
        },
        title="Regional labor-pull benchmark",
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=55, b=20),
        legend_title_text="Entity type",
        yaxis={"categoryorder": "total ascending"},
    )
    return fig


def _format_lodes_table(rows: pd.DataFrame) -> pd.DataFrame:
    """Format the D5 LODES benchmark rows for compact display."""
    if rows.empty:
        return rows

    display = rows[
        [
            "entity",
            "entity_type",
            "jobs_to_workers_ratio",
            "jobs_minus_workers_label",
            "jobs_total",
            "workers_total",
        ]
    ].copy()
    display = display.rename(
        columns={
            "entity": "Entity",
            "entity_type": "Type",
            "jobs_to_workers_ratio": "Jobs / workers",
            "jobs_minus_workers_label": "Jobs minus workers",
            "jobs_total": "Workplace jobs",
            "workers_total": "Resident workers",
        }
    )
    display["Type"] = display["Type"].map(
        {
            "market": "Market",
            "peer": "Peer",
            "benchmark": "Benchmark",
        }
    )
    display["Jobs / workers"] = display["Jobs / workers"].map(format_ratio_cell)
    display["Workplace jobs"] = display["Workplace jobs"].map(format_jobs_cell)
    display["Resident workers"] = display["Resident workers"].map(format_jobs_cell)
    return display


def _format_peer_table(rows: pd.DataFrame) -> pd.DataFrame:
    """Format the selected peer list and cosine similarities for review."""
    if rows.empty:
        return rows

    display = rows.rename(
        columns={
            "peer_rank": "Rank",
            "peer_geo_name": "Peer",
            "similarity": "Cosine similarity",
        }
    )[["Rank", "Peer", "Cosine similarity"]].copy()
    display["Cosine similarity"] = display["Cosine similarity"].map(
        lambda value: "—" if pd.isna(value) else f"{float(value):.3f}"
    )
    return display


def render_page(market_id: str) -> None:
    """Render the D5 regional-fit page for one market."""
    initial_payload = get_d5_page_payload(market_id, basis="employment_share")
    available_peer_rows = initial_payload["available_peer_rows"]
    peer_label_to_id = {
        f"{row['peer_geo_name']} ({row['peer_market_id']})": str(row["peer_market_id"])
        for _, row in available_peer_rows.iterrows()
    }
    peer_labels = list(peer_label_to_id)
    default_labels = peer_labels[:D5_DEFAULT_PEER_COUNT]

    with st.sidebar:
        basis = st.radio(
            "D5 basis",
            options=["employment_share", "gdp_share"],
            format_func=lambda value: "Employment share" if value == "employment_share" else "GDP share",
        )
        selected_peer_labels = st.multiselect(
            "D5 peers",
            peer_labels,
            default=default_labels,
        )

    selected_peer_ids = [peer_label_to_id[label] for label in selected_peer_labels]
    payload = get_d5_page_payload(market_id, basis=basis, peer_market_ids=selected_peer_ids)
    mix_payload = payload["mix_payload"]
    lodes_payload = payload["lodes_payload"]

    st.header("D5 — Regional Fit and Peer Benchmarking")

    metric_cols = st.columns(3)
    with metric_cols[0]:
        st.metric("Mix panel latest year", mix_payload["selected_year"] if mix_payload["selected_year"] is not None else "—")
    with metric_cols[1]:
        st.metric("LODES panel latest year", lodes_payload["selected_year"] if lodes_payload["selected_year"] is not None else "—")
    with metric_cols[2]:
        st.metric("Selected peers", len(payload["peer_rows"]))

    if payload["takeaway"]:
        st.caption(payload["takeaway"])

    st.subheader(payload["mix_title"])
    st.caption(payload["mix_subtitle"])
    mix_chart = build_d5_mix_chart(
        mix_payload["chart_rows"],
        payload["mix_title"],
        payload["mix_subtitle"],
    )
    if mix_chart is None:
        st.info("The D5 industry/GDP comparison panel is unavailable for this selection.")
    else:
        _render_chart(mix_chart)

    st.subheader(payload["lodes_title"])
    st.caption(payload["lodes_subtitle"])
    lodes_chart = _build_lodes_chart(lodes_payload["rows"])
    if lodes_chart is None:
        st.info("The D5 jobs-to-workers benchmark panel is unavailable for this selection.")
    else:
        st.plotly_chart(lodes_chart, width="stretch")

    lower_cols = st.columns([0.9, 1.1])
    with lower_cols[0]:
        st.markdown("**Selected peers**")
        peer_table = _format_peer_table(payload["peer_rows"])
        if peer_table.empty:
            st.info("No Cross-Frame peer defaults were available for this market.")
        else:
            _render_html_table(peer_table)

    with lower_cols[1]:
        st.markdown("**Jobs-to-workers benchmark table**")
        lodes_table = _format_lodes_table(lodes_payload["rows"])
        if lodes_table.empty:
            st.info("No LODES benchmark rows were available for this selection.")
        else:
            _render_html_table(lodes_table)

    with st.expander("Data notes"):
        for note in mix_payload["notes"]:
            st.markdown(f"- {note}")
        for note in lodes_payload["notes"]:
            st.markdown(f"- {note}")
        st.markdown("- Peer defaults come from the promoted Cross-Frame Intelligence similarity bundle in `mart_intelligence.intelligence_cross_frame`.")
