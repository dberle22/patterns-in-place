"""Trajectory tab — Phase 6 signals, pattern flags, KPI movement."""

from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd

from config import PATTERN_LABELS, TRAJECTORY_DIRECTION_COLORS
from dd_db import get_kpi_timeseries, get_kpi_trajectory, get_trajectory_row
from components.ui_helpers import label, pct_rank


def _direction_badge(direction: str | None) -> str:
    if not direction:
        return "—"
    colors = {
        "diverging-improving": "🟢",
        "converging-improving": "🟡",
        "converging-declining": "🟠",
        "diverging-declining": "🔴",
    }
    icon = colors.get(direction, "⚪")
    return f"{icon} {direction.replace('-', ' ').title()}"


def render_trajectory(cbsa_code: str, cbsa_name: str) -> None:
    t = get_trajectory_row(cbsa_code)

    if not t:
        st.warning("No trajectory data found for this metro.")
        return

    # Per-frame direction badges
    st.subheader("Trajectory Direction")
    c1, c2, c3 = st.columns(3)
    with c1:
        d = t.get("livability_direction")
        st.metric("Livability", _direction_badge(d))
        strength_pct = t.get("livability_strength_pct")
        if strength_pct is not None:
            st.caption(f"Strength: {pct_rank(strength_pct * 100)} percentile")
    with c2:
        d = t.get("opportunity_direction")
        st.metric("Opportunity", _direction_badge(d))
        strength_pct = t.get("opportunity_strength_pct")
        if strength_pct is not None:
            st.caption(f"Strength: {pct_rank(strength_pct * 100)} percentile")
    with c3:
        d = t.get("character_direction")
        st.metric("Character", _direction_badge(d))
        strength_pct = t.get("character_strength_pct")
        if strength_pct is not None:
            st.caption(f"Strength: {pct_rank(strength_pct * 100)} percentile")

    st.divider()

    # Opportunity turn signal
    opp_turn = t.get("opp_turn_signal")
    opp_turn_type = t.get("opp_turn_signal_type", "")
    if opp_turn:
        st.warning(
            f"**Opportunity Turn Signal:** This metro's short-run direction contradicts "
            f"its medium-term trend. Type: `{opp_turn_type}`"
        )

    # Trajectory disagreement
    disagree_pct = t.get("trajectory_disagreement_pct")
    improving = t.get("improving_frame_count", 0)
    declining = t.get("declining_frame_count", 0)
    st.metric(
        "Cross-Frame Disagreement",
        f"{pct_rank(disagree_pct * 100) if disagree_pct is not None else '—'} percentile",
        help=f"{improving} improving / {declining} declining frames"
    )

    st.divider()

    # Pattern flags
    st.subheader("Pattern Flags")
    with st.expander("What are Pattern Flags?", expanded=False):
        st.markdown(
            "Pattern flags identify metros in the **top decile nationally** for a specific behavioral signal "
            "based on their trajectory data. A metro with no flags is not unusual — most metros (roughly 90%) "
            "won't qualify for any given flag. Flags are additive signals, not scores.\n\n"
            "- **Bounce-Back** — strong recent trajectory reversal after prior decline\n"
            "- **Hidden Livability Winner** — high livability trajectory despite low current percentile\n"
            "- **Diverging From Themselves** — frames moving in opposite directions (e.g. livability improving, opportunity declining)\n"
            "- **Fast Demographic Changer** — character frame metrics shifting faster than national average\n"
            "- **Environmental Risk Outlier** — AQI and/or FEMA risk worsening faster than peers"
        )
    active_patterns = [
        PATTERN_LABELS[col]
        for col in PATTERN_LABELS
        if t.get(col)
    ]
    if active_patterns:
        for p_label in active_patterns:
            st.success(f"**{p_label}**")
    else:
        st.info("No top-decile pattern flags for this metro.")

    # Environmental risk detail if flagged
    if t.get("is_environmental_risk_outlier"):
        aqi_rank = t.get("worsening_rank_pct_aqi_median")
        fema_rank = t.get("worsening_rank_pct_fema_risk_score")
        st.caption(
            f"AQI worsening: {pct_rank(aqi_rank * 100) if aqi_rank else '—'} percentile | "
            f"FEMA risk worsening: {pct_rank(fema_rank * 100) if fema_rank else '—'} percentile"
        )

    st.divider()

    # Candidate score
    st.subheader("Candidate Score")
    st.caption(
        "The Candidate Score is a composite of two signals: (1) **cross-frame divergence** — how different "
        "this metro's Livability, Opportunity, and Character percentiles are from each other (high divergence = "
        "analytically interesting contrast); and (2) **trajectory strength** — how strongly and consistently "
        "the metro is moving in any direction across frames. High-scoring metros are the best candidates for "
        "deep-dive research because they have both interesting structure and detectable momentum."
    )
    cand_score = t.get("candidate_score")
    cand_rank = t.get("candidate_rank")
    phase5_rank = t.get("phase5_overlap_rank")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Candidate Score", f"{cand_score:.1f}" if cand_score is not None else "—")
    with c2:
        st.metric("Candidate Rank", f"#{int(cand_rank)}" if cand_rank is not None else "—",
                  help="Rank among all 401 CBSAs. Lower = stronger candidate for deep-dive research.")
    with c3:
        st.metric("Cross-Frame Overlap Rank", f"#{int(phase5_rank)}" if phase5_rank is not None else "—",
                  help="Rank on cross-frame divergence alone (Phase 5). Lower = more structurally interesting.")

    st.divider()

    # KPI trajectory line chart
    st.subheader("KPI Movement — Position & Change")
    st.caption(
        "**Position Z** = where this metro stands today vs. all peers (standard deviations from mean). "
        "**Change Z** = how much it has moved over the window vs. peers. "
        "Use the filters to focus on a frame or window length."
    )

    kpi_df = get_kpi_trajectory(cbsa_code)
    if kpi_df.empty:
        st.caption("KPI trajectory data not available.")
        return

    required = {"metric_id", "frame_id", "position_z", "change_z", "metric_direction",
                "current_value", "lag_value", "current_year", "lag_year", "window_years"}
    if not required.issubset(kpi_df.columns):
        st.caption(f"Unexpected trajectory format. Columns: {kpi_df.columns.tolist()}")
        return

    # Filter controls
    fc1, fc2 = st.columns(2)
    with fc1:
        frame_opts = ["All frames"] + sorted(kpi_df["frame_id"].dropna().unique().tolist())
        selected_frame = st.selectbox("Frame", frame_opts, key="traj_frame")
    with fc2:
        window_opts = sorted(kpi_df["window_years"].dropna().unique().tolist())
        selected_window = st.selectbox(
            "Window",
            window_opts,
            index=window_opts.index(5) if 5 in window_opts else 0,
            format_func=lambda x: f"{int(x)}-year",
            key="traj_window",
        )

    display = kpi_df[kpi_df["window_years"] == selected_window].copy()
    if selected_frame != "All frames":
        display = display[display["frame_id"] == selected_frame]

    if display.empty:
        st.caption("No data for this selection.")
        return

    display["KPI"] = display["metric_id"].map(lambda x: label(x))
    display["Direction"] = display["metric_direction"].fillna("unknown")

    direction_colors = {
        "diverging-improving": "#2E7D32",
        "converging-improving": "#66BB6A",
        "converging-declining": "#EF9A9A",
        "diverging-declining": "#C62828",
        "unknown": "#9E9E9E",
    }

    # --- Scatter: Position Z vs Change Z (the primary view) ---
    st.markdown("#### Position vs. Change")
    st.caption("Each dot is a KPI. X = where the metro stands today. Y = how much it's moved. Color = trajectory direction.")

    fig_scatter = go.Figure()
    for direction, grp in display.groupby("Direction"):
        color = direction_colors.get(direction, "#9E9E9E")
        fig_scatter.add_trace(go.Scatter(
            x=grp["position_z"],
            y=grp["change_z"],
            mode="markers+text",
            marker=dict(size=10, color=color, opacity=0.85),
            text=grp["KPI"],
            textposition="top center",
            textfont=dict(size=9),
            name=direction.replace("-", " ").title(),
            customdata=grp[["KPI", "current_value", "lag_value", "current_year", "lag_year"]].values,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Position Z: %{x:.2f}<br>"
                "Change Z: %{y:.2f}<br>"
                "Current (%{customdata[3]:.0f}): %{customdata[1]:.3g}<br>"
                "Prior (%{customdata[4]:.0f}): %{customdata[2]:.3g}<extra></extra>"
            ),
        ))

    fig_scatter.add_hline(y=0, line_dash="dot", line_color="gray", opacity=0.5)
    fig_scatter.add_vline(x=0, line_dash="dot", line_color="gray", opacity=0.5)
    fig_scatter.update_layout(
        height=500,
        xaxis_title="Position Z (current standing vs. peers)",
        yaxis_title="Change Z (momentum vs. peers)",
        margin=dict(l=0, r=0, t=20, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # --- Multi-year line chart from gold tables ---
    st.markdown("#### Annual Trends vs. National Median")
    st.caption(
        "Solid line = this metro. Dashed line = national median across all CBSAs. "
        "Select up to 6 KPIs — each gets its own panel so scales don't interfere."
    )

    kpi_id_to_label = {r["metric_id"]: r["KPI"] for _, r in display.iterrows()}
    all_metric_ids = sorted(kpi_id_to_label.keys(), key=lambda x: kpi_id_to_label[x])

    selected_metric_ids = st.multiselect(
        "KPIs to chart (up to 6 recommended)",
        options=all_metric_ids,
        default=all_metric_ids[:4],
        format_func=lambda x: kpi_id_to_label.get(x, x),
        key="traj_kpi_ts_select",
    )
    selected_metric_ids = selected_metric_ids[:6]  # cap silently; max_selections not in Streamlit 1.12

    if selected_metric_ids:
        ts_df = get_kpi_timeseries(cbsa_code, tuple(selected_metric_ids))

        if ts_df.empty:
            st.caption("Annual time series not available for the selected KPIs.")
        else:
            n = len(selected_metric_ids)
            ncols = min(2, n)
            nrows = (n + 1) // 2
            subplot_titles = [kpi_id_to_label.get(m, m) for m in selected_metric_ids]

            fig_ts = make_subplots(
                rows=nrows, cols=ncols,
                subplot_titles=subplot_titles,
                vertical_spacing=0.12,
                horizontal_spacing=0.08,
            )

            palette = ["#1565C0", "#2E7D32", "#6A1B9A", "#E65100", "#00838F", "#AD1457"]

            for idx, metric_id in enumerate(selected_metric_ids):
                mdf = ts_df[ts_df["metric_id"] == metric_id].sort_values("year")
                if mdf.empty:
                    continue
                row = idx // ncols + 1
                col = idx % ncols + 1
                color = palette[idx % len(palette)]
                kpi_name = kpi_id_to_label.get(metric_id, metric_id)

                # Metro line
                fig_ts.add_trace(go.Scatter(
                    x=mdf["year"], y=mdf["cbsa_value"],
                    mode="lines+markers",
                    name=f"{cbsa_name.split(',')[0]}",
                    line=dict(color=color, width=2),
                    marker=dict(size=6),
                    legendgroup=f"metro_{idx}",
                    showlegend=(idx == 0),
                    hovertemplate=f"<b>{kpi_name}</b><br>%{{x}}: %{{y:.3g}}<extra>{cbsa_name.split(',')[0]}</extra>",
                ), row=row, col=col)

                # National median line
                fig_ts.add_trace(go.Scatter(
                    x=mdf["year"], y=mdf["national_median"],
                    mode="lines",
                    name="National median",
                    line=dict(color=color, width=1.5, dash="dash"),
                    opacity=0.55,
                    legendgroup=f"nat_{idx}",
                    showlegend=(idx == 0),
                    hovertemplate=f"<b>{kpi_name}</b><br>%{{x}}: %{{y:.3g}}<extra>National median</extra>",
                ), row=row, col=col)

            fig_ts.update_layout(
                height=280 * nrows,
                margin=dict(l=0, r=0, t=40, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.08),
            )
            st.plotly_chart(fig_ts, use_container_width=True)
            st.caption("National median computed across all 396 CBSAs with intelligence profiles.")
