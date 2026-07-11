from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_caption
from ..request import ChartRequest
from ..specs import ChartSpec


def render_strength_strip(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    rows = pd.DataFrame({"metric_display_label": pd.unique(df["metric_display_label"]), "x_start": 0, "x_end": 100})
    strips = alt.Chart(rows).mark_rule(strokeWidth=6, color=theme.color("comparison.neutral", "#A7B4C2")).encode(
        x="x_start:Q", x2="x_end:Q", y=alt.Y("metric_display_label:N", title=None)
    )
    points = alt.Chart(df).mark_point(filled=True, size=80).encode(
        x=alt.X("normalized_value:Q", title="Percentile", scale=alt.Scale(domain=[0, 100])),
        y=alt.Y("metric_display_label:N", title=None),
        color=alt.Color("geo_name:N", legend=alt.Legend(title=None)),
        tooltip=["geo_name:N", "metric_label:N", alt.Tooltip("normalized_value:Q", format=".1f")],
    )
    out = alt.layer(strips, points).properties(width=theme.width("strength_strip"), height=theme.height("strength_strip"), title="Strength Strip / Scorecard Bars").configure_axis(labelFont=theme.font_family(), titleFont=theme.font_family()).configure_title(font=theme.font_family()).configure_view(stroke=None)
    out.usermeta = {"caption": build_caption(source=df["source"].iloc[0], vintage=df["vintage"].iloc[0])} if len(df) else {}
    return out
