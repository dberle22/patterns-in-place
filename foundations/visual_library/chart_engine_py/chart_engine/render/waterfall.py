from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_altair_title_params, build_data_caption
from ..request import ChartRequest
from ..specs import ChartSpec


def _waterfall_panel(df: pd.DataFrame, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = df.attrs.get("chart_config", {})
    color_scale = alt.Scale(
        domain=["positive", "negative", "total"],
        range=[
            theme.color("diverging.better", "#0C7C78"),
            theme.color("diverging.worse", "#D66A4E"),
            theme.color("neutral.text", "#36454F"),
        ],
    )

    bars_df = df.copy()
    bars_df["bar_ymin"] = bars_df[["cumulative_start", "cumulative_end"]].min(axis=1)
    bars_df["bar_ymax"] = bars_df[["cumulative_start", "cumulative_end"]].max(axis=1)
    bars_df["value_label"] = bars_df["plot_value"].map(lambda value: theme.format(value, request.number_format) or str(value))
    label_offset = (bars_df["bar_ymax"].max() - bars_df["bar_ymin"].min()) * 0.025 if len(bars_df) else 0
    label_offset = label_offset or max(abs(bars_df["plot_value"]).max(), 1) * 0.04
    bars_df["label_y"] = bars_df["bar_ymax"] + bars_df["plot_value"].apply(lambda value: label_offset if value >= 0 else -label_offset)

    base = alt.Chart(bars_df)
    bars = base.mark_bar().encode(
        x=alt.X("component_label:N", sort=alt.SortField(field="waterfall_position"), title=None),
        y=alt.Y("bar_ymax:Q", title=bars_df["total_label"].iloc[0] if "total_label" in bars_df.columns and len(bars_df) else None),
        y2="bar_ymin:Q",
        color=alt.Color("direction:N", scale=color_scale, legend=alt.Legend(title=None)),
        tooltip=[
            "component_label:N",
            alt.Tooltip("plot_value:Q", format=theme.d3_format(request.number_format)),
            "row_type:N",
        ],
    )

    layers: list[alt.Chart] = [
        alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(color=theme.color("neutral.axis", "#5B6770")).encode(y="y:Q"),
        bars,
    ]

    if cfg.get("show_connector_lines", True):
        connector_df = bars_df[bars_df["row_type"] != str(cfg.get("total_row_type", "total"))].copy()
        if len(connector_df) > 1:
            connector_df["x"] = connector_df["waterfall_position"]
            connector_df["x2"] = connector_df["waterfall_position"] + 1
            connector_df["y"] = connector_df["cumulative_end"]
            connector_df = connector_df.loc[connector_df["x2"] <= bars_df["waterfall_position"].max()].copy()
            layers.append(
                alt.Chart(connector_df).mark_rule(
                    color=theme.color("neutral.text_muted", "#8A96A3"),
                    strokeDash=[3, 3],
                    strokeWidth=1,
                ).encode(
                    x="x:Q",
                    x2="x2:Q",
                    y="y:Q",
                )
            )

    if cfg.get("show_value_labels", True):
        layers.append(
            alt.Chart(bars_df).mark_text(
                font=theme.font_family(),
                color=theme.color("neutral.text", "#24313F"),
                dy=-6,
            ).encode(
                x=alt.X("component_label:N", sort=alt.SortField(field="waterfall_position")),
                y="label_y:Q",
                text="value_label:N",
            )
        )

    return alt.layer(*layers).properties(width=theme.width("waterfall"), height=theme.height("waterfall"))


def render_waterfall(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = df.attrs.get("chart_config", {})
    title = request.title or "Waterfall Chart"
    subtitle = request.subtitle or (df["time_window"].iloc[0] if "time_window" in df.columns and len(df) else None)
    caption = build_data_caption(df)
    title_params = build_altair_title_params(title, subtitle=subtitle, caption=caption, title_size=theme.title_size())

    facet_by = str(cfg.get("facet_by") or request.field_values.get("facet_by") or "").strip()
    if not facet_by and "benchmark_label" in df.columns and df["benchmark_label"].nunique(dropna=True) > 1:
        facet_by = "benchmark_label"

    if facet_by and facet_by in df.columns:
        panels: list[alt.Chart] = []
        for facet_value in df[facet_by].dropna().astype(str).unique().tolist():
            panel_df = df.loc[df[facet_by].astype(str) == facet_value].copy()
            panels.append(_waterfall_panel(panel_df, request).properties(title=facet_value))
        out = alt.vconcat(*panels).properties(title=alt.TitleParams(**title_params))
    else:
        out = _waterfall_panel(df, request).properties(title=alt.TitleParams(**title_params))

    out = out.configure_axis(labelFont=theme.font_family(), titleFont=theme.font_family()).configure_title(
        font=theme.font_family()
    ).configure_view(stroke=None)
    out.usermeta = {"caption": caption} if caption else {}
    return out
