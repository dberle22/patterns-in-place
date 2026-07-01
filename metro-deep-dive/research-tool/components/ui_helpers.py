"""Shared UI helpers used across all Deep Dive tabs."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from config import KPI_LABELS, SUBJECT_DISPLAY, TOPIC_DISPLAY


def label(col: str) -> str:
    """Return a human-readable label for a KPI column name."""
    return KPI_LABELS.get(col, col.replace("_", " ").title())


def subject_label(s: str) -> str:
    return SUBJECT_DISPLAY.get(s, s.replace("_", " ").title())


def topic_label(t: str) -> str:
    return TOPIC_DISPLAY.get(t, t.replace("_", " ").title())


def pct_rank(v: float | None) -> str:
    if v is None:
        return "—"
    return f"{int(round(v))}th"


def fmt_pct(v: float | None, decimals: int = 1) -> str:
    if v is None:
        return "—"
    return f"{v * 100:.{decimals}f}%"


def fmt_num(v: float | None, decimals: int = 1) -> str:
    if v is None:
        return "—"
    return f"{v:,.{decimals}f}"


def score_bar_chart(subjects: dict[str, float | None], title: str, color: str) -> go.Figure:
    """Horizontal bar chart for subject scores (0–100 scale)."""
    names = [subject_label(k) for k in subjects]
    values = [v if v is not None else 0.0 for v in subjects.values()]
    # Scores are z-score based — normalize to 0–100 display using percentile
    fig = go.Figure(go.Bar(
        x=values,
        y=names,
        orientation="h",
        marker_color=color,
        text=[f"{v:.1f}" for v in values],
        textposition="outside",
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Score",
        height=max(180, len(names) * 45 + 80),
        margin=dict(l=0, r=40, t=40, b=20),
        showlegend=False,
    )
    return fig


def percentile_gauge(percentile: float | None, label_text: str, color: str) -> go.Figure:
    """Single-value gauge indicator for a percentile."""
    val = percentile if percentile is not None else 0
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        number={"suffix": "th", "font": {"size": 28}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": color},
            "bgcolor": "white",
            "steps": [
                {"range": [0, 33], "color": "#FFEBEE"},
                {"range": [33, 67], "color": "#FFF9C4"},
                {"range": [67, 100], "color": "#E8F5E9"},
            ],
        },
        title={"text": label_text, "font": {"size": 16}},
        domain={"y": [0, 0.85]},
    ))
    # Extra top margin so the title doesn't clip
    fig.update_layout(height=220, margin=dict(l=10, r=10, t=50, b=10))
    return fig


def kpi_table(rows: list[dict], columns: list[str], rename: dict[str, str] | None = None) -> None:
    """Render a styled DataFrame as a KPI table."""
    import pandas as pd
    df = pd.DataFrame(rows, columns=columns)
    if rename:
        df = df.rename(columns=rename)
    st.dataframe(df, use_container_width=True, hide_index=True)


def peer_mini_table(peers_df, frame_percentile_col: str | None = None) -> None:
    """Render a compact peer comparison table."""
    import pandas as pd
    if peers_df.empty:
        st.caption("No peer data available.")
        return

    display = peers_df[["peer_rank", "cbsa_name", "similarity"]].copy()
    display.columns = ["Rank", "Metro", "Similarity"]
    display["Similarity"] = display["Similarity"].map(lambda x: f"{x:.3f}" if x is not None else "—")
    st.dataframe(display, use_container_width=True, hide_index=True)
