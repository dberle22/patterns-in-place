from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_caption
from ..request import ChartRequest
from ..specs import ChartSpec


def render_age_pyramid(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    color_scale = alt.Scale(domain=["Male", "Female"], range=["#4C78A8", "#2A9D8F"])
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X("plot_value:Q", title="Share of total population", axis=alt.Axis(format=".1%")),
        y=alt.Y("age_bin:N", sort=list(df["age_bin"].cat.categories) if hasattr(df["age_bin"], "cat") else None, title=None),
        color=alt.Color("sex:N", scale=color_scale, legend=alt.Legend(title=None)),
        tooltip=["age_bin:N", "sex:N", alt.Tooltip("plot_abs_value:Q", format=".1%")],
    )
    rule = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color=theme.color("neutral.axis", "#5B6770")).encode(x="x:Q")
    out = alt.layer(rule, chart).properties(width=theme.width("age_pyramid"), height=theme.height("age_pyramid"), title="Age Pyramid").configure_axis(labelFont=theme.font_family(), titleFont=theme.font_family()).configure_title(font=theme.font_family()).configure_view(stroke=None)
    out.usermeta = {"caption": build_caption(source=df["source"].iloc[0], vintage=df["vintage"].iloc[0])} if len(df) else {}
    return out
