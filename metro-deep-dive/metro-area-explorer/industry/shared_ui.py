"""Shared UI helpers for the Industry Streamlit apps."""

from __future__ import annotations

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
