from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import wrap_text
from ..request import ChartRequest
from ..specs import ChartSpec


def render_line_chart(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = theme.chart_defaults_for(request.chart_type)
    default_title = spec.docs.split("\n")[0].lstrip("#").strip() if spec.docs else spec.chart_type
    title = request.title or default_title
    subtitle = request.subtitle or (df["subtitle"].iloc[0] if "subtitle" in df.columns and len(df) else None)

    dims = request.dimensions
    width = dims.width if dims and dims.width else theme.width(request.chart_type)
    height = dims.height if dims and dims.height else theme.height(request.chart_type)

    series_order = list(dict.fromkeys(df["series"]))
    primary = series_order[0] if series_order else None
    color_scale = alt.Scale(
        domain=series_order,
        range=[
            theme.color("highlight.selection", cfg.get("base_color", "#2C7FB8"))
            if s == primary else theme.color("comparison.benchmark", cfg.get("benchmark_color", "#52606D"))
            for s in series_order
        ],
    )

    title_params = {"text": title, "fontSize": theme.title_size()}
    if subtitle:
        title_params["subtitle"] = wrap_text(subtitle, int(cfg.get("subtitle_wrap_width", 120)))

    lines = (
        alt.Chart(df)
        .mark_line(point=bool(cfg.get("show_points", True)))
        .encode(
            x=alt.X("period:O", title=None),
            y=alt.Y("value:Q", title=None, axis=alt.Axis(format=theme.d3_format(request.number_format))),
            color=alt.Color("series:N", scale=color_scale, legend=alt.Legend(title=None)),
            tooltip=[
                alt.Tooltip("series:N", title="Series"),
                alt.Tooltip("period:O", title="Period"),
                alt.Tooltip("value:Q", title="Value", format=theme.d3_format(request.number_format)),
            ],
        )
    )

    layers = [lines]

    # Annotations: vertical rule + text label per Annotation(kind="vline")
    # e.g. marking an inflection point per Section 6 of the Deep Dive template.
    for ann in request.annotations:
        if ann.kind == "vline":
            ann_df = pd.DataFrame({"period": [ann.x]})
            rule = alt.Chart(ann_df).mark_rule(
                color=theme.color("highlight.risk", "#C44536"), strokeDash=[2, 2]
            ).encode(x="period:O")
            layers.append(rule)
            if ann.label:
                label_df = pd.DataFrame({"period": [ann.x], "value": [df["value"].max()], "label": [ann.label]})
                text = alt.Chart(label_df).mark_text(
                    align="left", dx=5, color=theme.color("highlight.risk", "#C44536")
                ).encode(x="period:O", y="value:Q", text="label:N")
                layers.append(text)

    chart = (
        alt.layer(*layers)
        .properties(
            width=width,
            height=height,
            title=alt.TitleParams(**title_params),
        )
        .configure_axis(
            labelFont=theme.font_family(),
            titleFont=theme.font_family(),
            labelColor=theme.color("neutral.axis", "#5B6770"),
            gridColor=theme.color("neutral.grid_major", "#D9E2EC"),
        )
        .configure_title(
            font=theme.font_family(),
            color=theme.color("neutral.text", "#1F2933"),
            subtitleColor=theme.color("neutral.text_muted", "#52606D"),
        )
        .configure_legend(
            labelFont=theme.font_family(),
            labelColor=theme.color("neutral.text_muted", "#52606D"),
        )
        .configure_view(stroke=None)
    )
    return chart
