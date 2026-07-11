from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_caption, wrap_text
from ..request import ChartRequest
from ..specs import ChartSpec


def render_slopegraph(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    default_title = spec.docs.split("\n")[0].lstrip("#").strip() if spec.docs else spec.chart_type
    title = request.title or default_title
    subtitle = request.subtitle

    periods = sorted(df["period_label"].unique() if "period_label" in df.columns else df["period"].astype(str).unique())
    data = df.copy()
    data["period_display"] = data["period_label"] if "period_label" in data.columns else data["period"].astype(str)
    data["line_type"] = "comparison"
    data.loc[data.get("highlight_flag", False).astype(bool), "line_type"] = "highlight"
    data.loc[data.get("benchmark_flag", False).astype(bool), "line_type"] = "benchmark"

    color_scale = alt.Scale(
        domain=["comparison", "highlight", "benchmark"],
        range=[
            theme.color("comparison.neutral", "#A7B4C2"),
            theme.color("highlight.selection", "#2C7FB8"),
            theme.color("comparison.benchmark", "#52606D"),
        ],
    )

    chart = alt.Chart(data).mark_line(point=True).encode(
        x=alt.X("period_display:N", sort=periods, title=None),
        y=alt.Y("plot_value:Q", title=df["metric_label"].iloc[0] if "metric_label" in df.columns and len(df) else None),
        detail="geo_id:N",
        color=alt.Color("line_type:N", scale=color_scale, legend=None),
        tooltip=["geo_name:N", "period_display:N", alt.Tooltip("plot_value:Q", format=theme.d3_format(request.number_format))],
    )

    labels = alt.Chart(data[data["period_display"] == periods[-1]]).mark_text(
        align="left", dx=6, font=theme.font_family(), color=theme.color("neutral.text", "#1F2933")
    ).encode(x="period_display:N", y="plot_value:Q", text="geo_name:N")

    title_params = {"text": title, "fontSize": theme.title_size()}
    if subtitle:
        title_params["subtitle"] = wrap_text(subtitle, 120)

    out = alt.layer(chart, labels).properties(
        width=theme.width("slopegraph"), height=theme.height("slopegraph"), title=alt.TitleParams(**title_params)
    ).configure_axis(
        labelFont=theme.font_family(), titleFont=theme.font_family(), labelColor=theme.color("neutral.axis", "#5B6770")
    ).configure_title(
        font=theme.font_family(), color=theme.color("neutral.text", "#1F2933"), subtitleColor=theme.color("neutral.text_muted", "#52606D")
    ).configure_view(stroke=None)
    out.usermeta = {"caption": build_caption(source=df["source"].iloc[0], vintage=df["vintage"].iloc[0])} if len(df) else {}
    return out
