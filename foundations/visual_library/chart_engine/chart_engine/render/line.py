from __future__ import annotations

import altair as alt
import pandas as pd

from ..request import ChartRequest
from ..specs import ChartSpec


def render_line_chart(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    default_title = spec.docs.split("\n")[0].lstrip("#").strip() if spec.docs else spec.chart_type
    title = request.title or default_title
    subtitle = request.subtitle or (df["subtitle"].iloc[0] if "subtitle" in df.columns and len(df) else None)

    dims = request.dimensions
    width = dims.width if dims and dims.width else theme.width()
    height = dims.height if dims and dims.height else theme.height()

    series_order = list(dict.fromkeys(df["series"]))
    primary = series_order[0] if series_order else None
    color_scale = alt.Scale(
        domain=series_order,
        range=[
            theme.color("primary", "#1a4d7a") if s == primary else theme.color("benchmark", "#999999")
            for s in series_order
        ],
    )

    title_params = {"text": title, "fontSize": theme.title_size()}
    if subtitle:
        title_params["subtitle"] = subtitle

    lines = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("period:O", title=None),
            y=alt.Y("value:Q", title=None),
            color=alt.Color("series:N", scale=color_scale, legend=alt.Legend(title=None)),
            tooltip=["series", "period", "value"],
        )
    )

    layers = [lines]

    # Annotations: vertical rule + text label per Annotation(kind="vline")
    # e.g. marking an inflection point per Section 6 of the Deep Dive template.
    for ann in request.annotations:
        if ann.kind == "vline":
            ann_df = pd.DataFrame({"period": [ann.x]})
            rule = alt.Chart(ann_df).mark_rule(
                color=theme.color("annotation", "#c0392b"), strokeDash=[2, 2]
            ).encode(x="period:O")
            layers.append(rule)
            if ann.label:
                label_df = pd.DataFrame({"period": [ann.x], "value": [df["value"].max()], "label": [ann.label]})
                text = alt.Chart(label_df).mark_text(
                    align="left", dx=5, color=theme.color("annotation", "#c0392b")
                ).encode(x="period:O", y="value:Q", text="label:N")
                layers.append(text)

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
