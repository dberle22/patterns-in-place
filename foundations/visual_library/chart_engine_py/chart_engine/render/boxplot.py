from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_caption, wrap_text
from ..request import ChartRequest
from ..specs import ChartSpec


def render_boxplot(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    default_title = spec.docs.split("\n")[0].lstrip("#").strip() if spec.docs else spec.chart_type
    title = request.title or default_title
    subtitle = request.subtitle or (df["time_window"].iloc[0] if "time_window" in df.columns and len(df) else None)

    base = alt.Chart(df)
    boxes = base.mark_boxplot(size=28, color=theme.color("neutral.text_muted", "#52606D")).encode(
        x=alt.X("box_group:N", title=None),
        y=alt.Y("metric_value:Q", title=df["metric_label"].iloc[0] if "metric_label" in df.columns and len(df) else None,
                axis=alt.Axis(format=theme.d3_format(request.number_format))),
        tooltip=["geo_name:N", "box_group:N", alt.Tooltip("metric_value:Q", format=theme.d3_format(request.number_format))],
    )

    layers = [boxes]
    if "highlight_flag" in df.columns and df["highlight_flag"].any():
        highlights = alt.Chart(df[df["highlight_flag"]]).mark_point(
            filled=True, size=70, color=theme.color("highlight.selection", "#2C7FB8")
        ).encode(x="box_group:N", y="metric_value:Q", tooltip=["geo_name:N"])
        layers.append(highlights)

    title_params = {"text": title, "fontSize": theme.title_size()}
    if subtitle:
        title_params["subtitle"] = wrap_text(subtitle, 120)

    out = alt.layer(*layers).properties(
        width=theme.width("boxplot"), height=theme.height("boxplot"), title=alt.TitleParams(**title_params)
    ).configure_axis(labelFont=theme.font_family(), titleFont=theme.font_family()).configure_title(font=theme.font_family()).configure_view(stroke=None)
    out.usermeta = {"caption": build_caption(source=df["source"].iloc[0], vintage=df["vintage"].iloc[0])} if len(df) else {}
    return out
