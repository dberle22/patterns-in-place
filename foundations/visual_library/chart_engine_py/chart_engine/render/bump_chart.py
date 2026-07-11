from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_caption
from ..request import ChartRequest
from ..specs import ChartSpec


def render_bump_chart(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    data = df.copy()
    data["line_type"] = data["highlight_flag"].map(lambda x: "highlight" if x else "comparison")
    color_scale = alt.Scale(domain=["comparison", "highlight"], range=[theme.color("comparison.neutral", "#A7B4C2"), theme.color("highlight.selection", "#2C7FB8")])
    chart = alt.Chart(data).mark_line(point=True).encode(
        x=alt.X("period:N", title=None),
        y=alt.Y("rank:Q", sort="descending", title="Rank"),
        detail="geo_id:N",
        color=alt.Color("line_type:N", scale=color_scale, legend=None),
        tooltip=["geo_name:N", "period:N", alt.Tooltip("rank:Q", format=",d")],
    )
    labels = alt.Chart(data.sort_values("period").drop_duplicates("geo_id", keep="last")).mark_text(
        align="left", dx=6, font=theme.font_family(), color=theme.color("neutral.text", "#1F2933")
    ).encode(x="period:N", y="rank:Q", text="geo_name:N")
    out = alt.layer(chart, labels).properties(width=theme.width("bump_chart"), height=theme.height("bump_chart"), title="Bump Chart").configure_axis(labelFont=theme.font_family(), titleFont=theme.font_family()).configure_title(font=theme.font_family()).configure_view(stroke=None)
    out.usermeta = {"caption": build_caption(source=df["source"].iloc[0], vintage=df["vintage"].iloc[0])} if len(df) else {}
    return out
