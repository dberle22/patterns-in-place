"""Map panel component for CBSA explorer surfaces."""

from __future__ import annotations

from typing import Any

import plotly.express as px
import streamlit as st

from shared.geo_utils import load_county_geojson


def render_cbsa_map(
    metric_df,
    geojson: dict[str, Any],
    color_scale_mode: str,
    height: int = 520,
) -> None:
    """Render the CBSA choropleth with a light-touch color scaling control."""
    color_kwargs: dict[str, Any] = {}
    if color_scale_mode == "Quantile" and not metric_df.empty:
        color_kwargs["color_continuous_scale"] = "Viridis"
        color_kwargs["range_color"] = (
            float(metric_df["metric_value"].quantile(0.05)),
            float(metric_df["metric_value"].quantile(0.95)),
        )
    elif color_scale_mode == "Raw":
        color_kwargs["color_continuous_scale"] = "Viridis"

    choropleth = px.choropleth_mapbox(
        metric_df,
        geojson=geojson,
        locations="geo_id",
        featureidkey="properties.cbsa_code",
        color="metric_value",
        hover_name="geo_name",
        hover_data={
            "metric_value": False,
            "state_name": True,
            "division_name": True,
            "national_pct_rank": ":.1f",
            "division_pct_rank": ":.1f",
        },
        mapbox_style="carto-positron",
        center={"lat": 38.5, "lon": -96.0},
        zoom=2.7,
        opacity=0.75,
        height=height,
        **color_kwargs,
    )
    # A light county outline layer helps orient the eye within larger CBSAs
    # without turning the map into a county-grain explorer.
    choropleth.update_layout(
        mapbox_layers=[
            {
                "sourcetype": "geojson",
                "source": load_county_geojson(),
                "type": "line",
                "color": "rgba(90, 90, 90, 0.18)",
                "line": {"width": 0.4},
            }
        ]
    )
    choropleth.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(choropleth, use_container_width=True)
