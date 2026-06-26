"""Distribution tab renderer for the selected metric."""

from __future__ import annotations

import plotly.express as px
import streamlit as st


def render_distribution_tab(metric_df, selected_value: float, metric_display_name: str) -> None:
    """Render the distribution histogram with the selected CBSA pinned."""
    distribution_plot = px.histogram(
        metric_df,
        x="metric_value",
        nbins=30,
        height=420,
        title=f"Distribution of {metric_display_name} across CBSAs",
    )
    distribution_plot.add_vline(
        x=float(selected_value),
        line_color="#d94801",
        line_width=3,
    )
    st.plotly_chart(distribution_plot, use_container_width=True)
