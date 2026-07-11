from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_caption
from ..request import ChartRequest
from ..specs import ChartSpec


def render_correlation_heatmap(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    base = alt.Chart(df)
    rects = base.mark_rect().encode(
        x=alt.X("metric_x:N", title=None),
        y=alt.Y("metric_y:N", title=None),
        color=alt.Color("correlation:Q", scale=alt.Scale(domain=[-1, 1], scheme="redblue"), legend=alt.Legend(title="Correlation")),
        tooltip=["metric_x:N", "metric_y:N", alt.Tooltip("correlation:Q", format=".2f")],
    )
    text = base.mark_text(font=theme.font_family(), color=theme.color("neutral.text", "#1F2933")).encode(
        x="metric_x:N", y="metric_y:N", text="label:N"
    )
    out = alt.layer(rects, text).properties(width=theme.width("correlation_heatmap"), height=theme.height("correlation_heatmap"), title="Correlation Heatmap").configure_axis(labelFont=theme.font_family(), titleFont=theme.font_family()).configure_title(font=theme.font_family()).configure_view(stroke=None)
    out.usermeta = {"caption": build_caption(source=df["source"].iloc[0] if "source" in df.columns and len(df) else None, vintage=df["vintage"].iloc[0] if "vintage" in df.columns and len(df) else None)} if len(df) else {}
    return out
