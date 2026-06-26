"""Scatter tab renderer for ad hoc metric comparisons."""

from __future__ import annotations

import plotly.express as px
import streamlit as st


def render_scatter_tab(
    metric_pool: list[dict],
    metric_meta_lookup,
    default_x: str,
    default_y: str,
    selected_geo_id: str,
    find_metric_index,
    build_scatter_frame,
) -> tuple[str, str]:
    """Render the metric-vs-metric scatter with the selected CBSA highlighted."""
    scatter_metric_ids = [metric["metric_id"] for metric in metric_pool]
    x_metric_id = st.selectbox(
        "X-Axis Metric",
        scatter_metric_ids,
        index=find_metric_index(default_x, metric_pool),
        format_func=lambda metric_id: metric_meta_lookup(metric_id)["display_name"],
        key="scatter_x_metric",
    )
    y_metric_id = st.selectbox(
        "Y-Axis Metric",
        scatter_metric_ids,
        index=find_metric_index(default_y, metric_pool),
        format_func=lambda metric_id: metric_meta_lookup(metric_id)["display_name"],
        key="scatter_y_metric",
    )

    scatter_df = build_scatter_frame(x_metric_id, y_metric_id)
    scatter_df["selected"] = scatter_df["geo_id"] == selected_geo_id

    scatter_plot = px.scatter(
        scatter_df,
        x="x_value",
        y="y_value",
        hover_name="geo_name",
        color="selected",
        color_discrete_map={True: "#d94801", False: "#2b8cbe"},
        height=460,
    )
    scatter_plot.update_traces(marker=dict(size=9), selector=dict(mode="markers"))
    st.plotly_chart(scatter_plot, use_container_width=True)
    return x_metric_id, y_metric_id
