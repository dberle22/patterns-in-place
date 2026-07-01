"""Shared renderer for a single Intelligence frame tab."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from config import (
    FRAME_COLORS, KPI_LABELS, KPI_UNITS,
    LIVABILITY_TOPIC_KPIS, OPPORTUNITY_TOPIC_KPIS, CHARACTER_TOPIC_KPIS,
)
from dd_db import get_frame_peers, get_kpi_zscore_params
from components.ui_helpers import label, pct_rank, subject_label, topic_label, fmt_num

FRAME_TOPIC_MAP = {
    "livability": LIVABILITY_TOPIC_KPIS,
    "opportunity": OPPORTUNITY_TOPIC_KPIS,
    "character": CHARACTER_TOPIC_KPIS,
}


def _subject_bars(subjects: dict[str, float | None], color: str) -> go.Figure:
    names = [subject_label(k) for k in subjects.keys()]
    values = [v if v is not None else 0.0 for v in subjects.values()]
    fig = go.Figure(go.Bar(
        x=values, y=names, orientation="h",
        marker_color=color,
        text=[f"{v:.2f}" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        height=max(150, len(names) * 50 + 60),
        margin=dict(l=0, r=50, t=20, b=10),
        xaxis_title="Score (standardized)",
    )
    return fig


def _render_topic_kpi_groups(
    frame: str,
    topics: dict[str, float | None],
    kpis: dict[str, dict],
    color: str,
) -> None:
    """Render topics as section headers with their KPIs grouped underneath."""
    topic_map = FRAME_TOPIC_MAP.get(frame, {})

    # Track which KPIs appear in the topic map (to catch any orphans)
    seen_kpis: set[str] = set()

    for topic_key, topic_score in topics.items():
        kpi_keys = topic_map.get(topic_key, [])
        topic_kpis = [(k, kpis[k]) for k in kpi_keys if k in kpis]
        seen_kpis.update(k for k, _ in topic_kpis)

        score_str = f"{topic_score:.2f}" if topic_score is not None else "—"
        header = f"**{topic_label(topic_key)}** — score: `{score_str}`"

        with st.expander(header, expanded=False):
            if not topic_kpis:
                st.caption("No KPIs mapped to this topic.")
                continue

            zscore_params = get_kpi_zscore_params()
            rows = []
            for col, info in topic_kpis:
                unit = KPI_UNITS.get(col, "")
                raw_num = info.get("_raw_num")
                raw = info.get("raw", "—")

                # Format raw value: percent KPIs stored as decimals → multiply by 100
                if unit == "%" and raw_num is not None:
                    raw_display = f"{raw_num * 100:.1f}%"
                elif raw != "—" and unit == "$":
                    raw_display = f"${raw}"
                elif raw != "—" and unit and unit not in ("%", "$", "ratio", "LQ", "index", "HHI"):
                    raw_display = f"{raw} {unit}"
                else:
                    raw_display = raw

                # Compute z-score from polarity-adjusted value and population stats
                scored = info.get("scored")
                scored_col = f"scored_{col}"
                p = zscore_params.get(scored_col)
                if p and scored is not None:
                    z = (scored - p["mean"]) / p["std"]
                    zscore_display = f"{z:+.2f}"
                else:
                    zscore_display = "—"

                imputed = "⚠" if info.get("imputed_flag") else ""
                rows.append({
                    "KPI": label(col) + (" " + imputed if imputed else ""),
                    "Raw Value": raw_display,
                    "Z-Score": zscore_display,
                })

            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Render any KPIs not covered by the topic map
    orphan_kpis = [(k, v) for k, v in kpis.items() if k not in seen_kpis]
    if orphan_kpis:
        with st.expander("Other KPIs", expanded=False):
            rows = []
            for col, info in orphan_kpis:
                raw = info.get("raw", "—")
                scored = info.get("scored")
                rows.append({
                    "KPI": label(col),
                    "Raw Value": raw,
                    "Score": f"{scored:.2f}" if scored is not None else "—",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_frame_tab(
    cbsa_code: str,
    cbsa_name: str,
    frame: str,
    profile: dict,
    subjects: dict[str, float | None],
    topics: dict[str, float | None],
    kpis: dict[str, dict],
    gmm_probs: dict[str, float | None] | None = None,
    extra_section: callable | None = None,
) -> None:
    color = FRAME_COLORS.get(frame, "#607D8B")

    # Percentile + cluster header
    pct_field = f"{frame}_percentile"
    pct_rank_field = f"{frame}_percentile_rank"
    pct = profile.get(pct_field) or profile.get(pct_rank_field)
    cluster = profile.get(f"{frame}_cluster_name") or profile.get(f"{frame}_cluster", "—")
    interp = profile.get("cluster_interpretation", "")

    h1, h2 = st.columns([1, 3])
    with h1:
        st.metric(f"{frame.title()} Percentile", pct_rank(pct))
        st.markdown(f"**Cluster**")
        st.markdown(cluster or "—")
    with h2:
        if interp:
            st.info(interp)

    st.divider()

    # Subject score bars
    st.subheader("Subject Scores")
    st.plotly_chart(_subject_bars(subjects, color), use_container_width=True)

    st.divider()

    # Topic-grouped KPI detail
    st.subheader("Topics & KPIs")
    st.caption(
        "Each topic shows its composite score. Expand to see the KPIs that drive it. "
        "**Z-Score** = standard deviations from the mean across all 396 CBSAs (negative KPIs are sign-flipped "
        "so positive = better than average). ⚠ = imputed value."
    )
    _render_topic_kpi_groups(frame, topics, kpis, color)

    # GMM soft membership (Character only)
    if gmm_probs is not None:
        st.divider()
        st.subheader("Cluster Soft Memberships")
        labels_g = list(gmm_probs.keys())
        values_g = [v if v is not None else 0.0 for v in gmm_probs.values()]
        fig = go.Figure(go.Bar(
            x=values_g, y=labels_g, orientation="h",
            marker_color=color,
            text=[f"{v:.1%}" for v in values_g],
            textposition="outside",
        ))
        fig.update_layout(
            height=max(150, len(labels_g) * 40 + 60),
            xaxis=dict(tickformat=".0%"),
            margin=dict(l=0, r=60, t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Extra frame-specific section
    if extra_section is not None:
        extra_section()

    st.divider()

    # Peer panel
    st.subheader(f"Top {frame.title()} Peers")
    peers = get_frame_peers(cbsa_code, frame)
    if not peers.empty:
        display = peers[["peer_rank", "cbsa_name", "similarity"]].copy()
        display.columns = ["Rank", "Metro", "Cosine Similarity"]
        display["Cosine Similarity"] = display["Cosine Similarity"].map(
            lambda x: f"{x:.3f}" if x is not None else "—"
        )
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.caption("Peer data unavailable.")
