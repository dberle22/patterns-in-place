from __future__ import annotations

import altair as alt
import pandas as pd

from ..request import ChartRequest
from ..specs import ChartSpec


def render_bar_chart(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    default_title = spec.docs.split("\n")[0].lstrip("#").strip() if spec.docs else spec.chart_type
    title = request.title or default_title
    subtitle = request.subtitle or (df["subtitle"].iloc[0] if "subtitle" in df.columns and len(df) else None)

    dims = request.dimensions
    width = dims.width if dims and dims.width else theme.width()
    height = dims.height if dims and dims.height else theme.height()

    title_params = {"text": title, "fontSize": theme.title_size()}
    if subtitle:
        title_params["subtitle"] = subtitle

    bars = (
        alt.Chart(df)
        .mark_bar(color=theme.color("primary", "#1a4d7a"))
        .encode(
            x=alt.X("value:Q", title=None),
            y=alt.Y("entity:N", sort="-x", title=None),
            tooltip=["entity", "value"],
        )
    )

    layers = [bars]
    if request.benchmark and request.benchmark.value is not None:
        bench_df = pd.DataFrame({"value": [request.benchmark.value]})
        bench_rule = (
            alt.Chart(bench_df)
            .mark_rule(color=theme.color("benchmark", "#999999"), strokeDash=[4, 4])
            .encode(x="value:Q")
        )
        layers.append(bench_rule)

    chart = (
        alt.layer(*layers)
        .properties(
            width=width,
            height=height,
            title=alt.TitleParams(**title_params),
        )
        .configure_axis(labelFont=theme.font_family(), titleFont=theme.font_family())
        .configure_title(font=theme.font_family())
    )
    return chart
