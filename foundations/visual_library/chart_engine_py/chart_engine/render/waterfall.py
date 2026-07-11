from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_caption
from ..request import ChartRequest
from ..specs import ChartSpec


def render_waterfall(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    color_scale = alt.Scale(
        domain=["positive", "negative"],
        range=[theme.color("diverging.better", "#0C7C78"), theme.color("diverging.worse", "#D66A4E")],
    )
    bars = alt.Chart(df).mark_bar().encode(
        x=alt.X("component_label:N", sort=None, title=None),
        y=alt.Y("cumulative_end:Q", title=df["total_label"].iloc[0] if "total_label" in df.columns and len(df) else None),
        y2="cumulative_start:Q",
        color=alt.Color("direction:N", scale=color_scale, legend=None),
        tooltip=["component_label:N", alt.Tooltip("component_value:Q", format=theme.d3_format(request.number_format))],
    )
    rule = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=theme.color("neutral.axis", "#5B6770")).encode(y="y:Q")
    out = alt.layer(rule, bars).properties(width=theme.width("waterfall"), height=theme.height("waterfall"), title="Waterfall Chart").configure_axis(labelFont=theme.font_family(), titleFont=theme.font_family()).configure_title(font=theme.font_family()).configure_view(stroke=None)
    out.usermeta = {"caption": build_caption(source=df["source"].iloc[0], vintage=df["vintage"].iloc[0])} if len(df) else {}
    return out
