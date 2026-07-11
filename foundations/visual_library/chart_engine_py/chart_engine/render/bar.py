from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import wrap_text
from ..request import ChartRequest
from ..specs import ChartSpec


def render_bar_chart(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = theme.chart_defaults_for(request.chart_type)
    default_title = spec.docs.split("\n")[0].lstrip("#").strip() if spec.docs else spec.chart_type
    title = request.title or default_title
    subtitle = request.subtitle or (df["subtitle"].iloc[0] if "subtitle" in df.columns and len(df) else None)

    dims = request.dimensions
    width = dims.width if dims and dims.width else theme.width(request.chart_type)
    height = dims.height if dims and dims.height else theme.height(request.chart_type)

    title_params = {"text": title, "fontSize": theme.title_size()}
    if subtitle:
        title_params["subtitle"] = wrap_text(subtitle, int(cfg.get("subtitle_wrap_width", 120)))

    bars = (
        alt.Chart(df)
        .mark_bar(color=theme.color("highlight.selection", cfg.get("base_color", "#2C7FB8")))
        .encode(
            x=alt.X("value:Q", title=None, axis=alt.Axis(format=theme.d3_format(request.number_format))),
            y=alt.Y("entity:N", sort="-x", title=None),
            tooltip=[
                alt.Tooltip("entity:N", title="Entity"),
                alt.Tooltip("value:Q", title="Value", format=theme.d3_format(request.number_format)),
            ],
        )
    )

    layers = [bars]
    if request.benchmark and request.benchmark.value is not None:
        bench_df = pd.DataFrame({"value": [request.benchmark.value]})
        bench_rule = (
            alt.Chart(bench_df)
            .mark_rule(
                color=theme.color("comparison.benchmark", cfg.get("benchmark_color", "#52606D")),
                strokeDash=cfg.get("benchmark_linetype", [4, 4]),
                strokeWidth=cfg.get("benchmark_linewidth", 1),
            )
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
        .configure_view(stroke=None)
    )
    return chart
