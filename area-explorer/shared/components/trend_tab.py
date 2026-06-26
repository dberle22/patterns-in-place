"""Trend tab renderer for time-series comparisons."""

from __future__ import annotations

import plotly.express as px
import streamlit as st


def render_trend_tab(
    comparison_options: list[tuple[str, str]],
    comparison_lookup: dict[str, str],
    selected_geo_id: str,
    metric_display_name: str,
    build_trend_frame,
) -> tuple[str, ...]:
    """Render the time-series chart and return the selected comparison CBSAs."""
    comparison_geo_ids = st.multiselect(
        "Comparison CBSAs",
        [geo_id for geo_id, _ in comparison_options if geo_id != selected_geo_id],
        format_func=lambda geo_id: comparison_lookup[geo_id],
        default=[],
        max_selections=3,
        key="trend_comparisons",
    )
    trend_df = build_trend_frame(tuple([selected_geo_id, *comparison_geo_ids]))

    trend_plot = px.line(
        trend_df,
        x="year",
        y="metric_value",
        color="geo_name",
        markers=True,
        title=f"{comparison_lookup[selected_geo_id]} — {metric_display_name}",
        height=420,
    )
    st.plotly_chart(trend_plot, use_container_width=True)
    return tuple(comparison_geo_ids)
