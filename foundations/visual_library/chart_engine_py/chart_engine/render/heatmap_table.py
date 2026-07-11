from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_caption
from ..request import ChartRequest
from ..specs import ChartSpec


def render_heatmap_table(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    base = alt.Chart(df)
    rects = base.mark_rect().encode(
        x=alt.X("column_label:N", title=None),
        y=alt.Y("row_label:N", title=None),
        color=alt.Color("fill_value:Q", scale=alt.Scale(scheme="blues"), legend=alt.Legend(title=None)),
        tooltip=["row_label:N", "column_label:N", "cell_label:N"],
    )
    text = base.mark_text(font=theme.font_family(), color=theme.color("neutral.text", "#1F2933")).encode(
        x="column_label:N", y="row_label:N", text="cell_label:N"
    )
    out = alt.layer(rects, text).properties(
        width=theme.width("heatmap_table"),
        height=theme.height("heatmap_table"),
        title=spec.docs.split("\n")[0].lstrip("#").strip() if spec.docs else spec.chart_type,
    ).configure_axis(labelFont=theme.font_family(), titleFont=theme.font_family()).configure_title(font=theme.font_family()).configure_view(stroke=None)
    out.usermeta = {"caption": build_caption(source=df["source"].iloc[0], vintage=df["vintage"].iloc[0])} if len(df) else {}
    return out
