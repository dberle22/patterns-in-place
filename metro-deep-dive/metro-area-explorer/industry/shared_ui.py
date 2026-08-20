"""Shared UI helpers for the Industry Streamlit apps."""

from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from data_prep import DEFAULT_MARKET_ID, get_cbsa_options


def market_label(row) -> str:
    """Build a stable market label for selectors across the Industry apps."""
    return f"{row['geo_name']} ({row['market_id']})"


def render_market_selector() -> str:
    """Render the shared market selector and return the chosen market id."""
    cbsa_options = get_cbsa_options()
    label_to_market = {
        market_label(row): str(row["market_id"])
        for _, row in cbsa_options.iterrows()
    }
    labels = list(label_to_market)
    default_index = next(
        (
            idx
            for idx, label in enumerate(labels)
            if label.endswith(f"({DEFAULT_MARKET_ID})")
        ),
        0,
    )
    chosen_label = st.selectbox("Market", labels, index=default_index)
    return label_to_market[chosen_label]


def format_percent_cell(value) -> str:
    """Format percent-like cells defensively after merges or coercions."""
    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return "—"
    return f"{float(numeric_value):.1%}"


def format_jobs_cell(value) -> str:
    """Format job-count cells consistently in D2 review tables."""
    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return "—"
    return f"{int(round(float(numeric_value))):,}"


def format_gdp_total_cell(value) -> str:
    """Format raw GDP totals for compact display in review tables."""
    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return "—"
    if numeric_value >= 1_000_000_000:
        return f"${float(numeric_value) / 1_000_000_000:.1f}B"
    return f"${float(numeric_value) / 1_000_000:.1f}M"


def format_ratio_cell(value) -> str:
    """Format ratio metrics consistently across D3 summary cards and tables."""
    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return "—"
    return f"{float(numeric_value):.2f}x"


def render_color_legend(df: pd.DataFrame) -> None:
    """Render map legends with visible swatches instead of raw hex codes.

    D2 and D3 both carry legend data frames with one color column and one or
    more label columns. Streamlit's plain HTML table path shows the literal hex
    string, which is hard to scan during review. This helper turns the color
    field into a small swatch while preserving the text labels beside it.
    """
    if df.empty:
        return

    color_columns = [column for column in df.columns if column.lower() == "color"]
    if not color_columns:
        st.markdown(df.fillna("—").to_html(index=False), unsafe_allow_html=True)
        return

    color_column = color_columns[0]
    display = df.fillna("—").copy()

    def _swatch(value: object) -> str:
        color = str(value) if value not in (None, "—") else "#FFFFFF"
        safe_color = escape(color)
        return (
            "<div style='display:flex;align-items:center;gap:8px;'>"
            f"<span style='display:inline-block;width:14px;height:14px;border:1px solid #CBD2D9;"
            f"background:{safe_color};border-radius:3px;'></span>"
            f"<span>{safe_color}</span>"
            "</div>"
        )

    display[color_column] = display[color_column].map(_swatch)
    st.markdown(display.to_html(index=False, escape=False), unsafe_allow_html=True)
