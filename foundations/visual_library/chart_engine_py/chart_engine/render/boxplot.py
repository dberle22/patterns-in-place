from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_altair_title_params, build_data_caption
from ..render_helpers import horizontal_benchmark_layers
from ..request import ChartRequest
from ..specs import ChartSpec


def _boxplot_subtitle(df: pd.DataFrame, request: ChartRequest) -> str | None:
    if request.subtitle:
        return request.subtitle

    cfg = df.attrs.get("chart_config", {})
    parts: list[str] = []
    if "time_window" in df.columns and len(df):
        parts.append(f"{df['time_window'].iloc[0]} snapshot")
    group_count = int(df["box_group"].nunique()) if "box_group" in df.columns else 0
    if group_count > 1:
        parts.append(f"Grouped by {cfg.get('group_label', cfg.get('group_field', 'group'))}")
        if str(cfg.get("order_groups", "median_desc")).lower() in {"median_desc", "median_asc"}:
            parts.append("Groups ordered by median")
    if cfg.get("winsorize_display") and cfg.get("trim_quantiles"):
        parts.append("Displayed values are winsorized for readability")
    return " | ".join(parts) if parts else None


def _build_boxplot_panel(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = df.attrs.get("chart_config", {})
    group_count = int(df["box_group"].nunique()) if "box_group" in df.columns else 0
    explicit_flip = cfg.get("flip")
    if explicit_flip is None and not request.field_values.get("flip") and not request.field_values.get("horizontal"):
        explicit_flip = group_count <= 1
    flip = bool(explicit_flip or request.field_values.get("flip") or request.field_values.get("horizontal"))
    metric_title = df["metric_label"].iloc[0] if "metric_label" in df.columns and len(df) else None
    value_axis = alt.Axis(format=theme.d3_format(request.number_format))
    category_sort = list(df["box_group"].cat.categories) if hasattr(df["box_group"], "cat") else None

    x_encoding = alt.X("box_group:N", title=None, sort=category_sort, axis=alt.Axis(labelAngle=0))
    y_encoding = alt.Y("plot_value:Q", title=metric_title, axis=value_axis)
    if flip:
        x_encoding, y_encoding = (
            alt.X("plot_value:Q", title=metric_title, axis=value_axis),
            alt.Y("box_group:N", title=None, sort=category_sort, axis=alt.Axis(labelLimit=220)),
        )

    base = alt.Chart(df)
    boxes = base.mark_boxplot(
        size=28,
        color=theme.color("neutral.text_muted", "#52606D"),
        extent=1.5,
    ).encode(x=x_encoding, y=y_encoding)

    layers: list[alt.Chart] = [boxes]

    if cfg.get("show_jitter"):
        jitter_x = alt.X("jitter:Q", axis=None) if not flip else alt.X("plot_value:Q", title=metric_title, axis=value_axis)
        jitter_y = alt.Y("plot_value:Q", title=metric_title, axis=value_axis) if not flip else alt.Y("jitter:Q", axis=None)
        jitter_data = df.copy()
        jitter_data["jitter"] = (pd.Series(range(len(jitter_data))) % 9 - 4) / 18
        layers.append(
            alt.Chart(jitter_data).mark_circle(
                color=theme.color("neutral.text_muted", "#52606D"),
                opacity=0.35,
                size=34,
            ).encode(
                x=jitter_x if not flip else alt.X("plot_value:Q", title=metric_title, axis=value_axis),
                y=alt.Y("box_group:N", title=None, sort=category_sort) if flip else alt.Y("plot_value:Q", title=metric_title, axis=value_axis),
                detail="geo_id:N",
                tooltip=["geo_name:N", "box_group:N", alt.Tooltip("plot_value:Q", format=theme.d3_format(request.number_format))],
            )
        )

    if "highlight_flag" in df.columns and df["highlight_flag"].any():
        highlights = alt.Chart(df[df["highlight_flag"]]).mark_point(
            filled=True,
            size=78,
            color=theme.color("highlight.selection", "#2C7FB8"),
            stroke=theme.color("neutral.background_white", "#FFFFFF"),
            strokeWidth=1,
        ).encode(
            x=alt.X("box_group:N", title=None, sort=category_sort) if not flip else alt.X("plot_value:Q", title=metric_title, axis=value_axis),
            y=alt.Y("plot_value:Q", title=metric_title, axis=value_axis) if not flip else alt.Y("box_group:N", title=None, sort=category_sort),
            tooltip=["geo_name:N", "box_group:N", alt.Tooltip("plot_value:Q", format=theme.d3_format(request.number_format))],
        )
        layers.append(highlights)

        label_df = df[df["label_flag"]].copy() if "label_flag" in df.columns else df[df["highlight_flag"]].copy()
        if not label_df.empty:
            layers.append(
                alt.Chart(label_df).mark_text(
                    align="left",
                    baseline="middle",
                    dx=8,
                    dy=-8 if not flip else 0,
                    font=theme.font_family(),
                    color=theme.color("neutral.text", "#1F2933"),
                ).encode(
                    x=alt.X("box_group:N", title=None, sort=category_sort) if not flip else alt.X("plot_value:Q", title=metric_title, axis=value_axis),
                    y=alt.Y("plot_value:Q", title=metric_title, axis=value_axis) if not flip else alt.Y("box_group:N", title=None, sort=category_sort),
                    text="geo_name:N",
                )
            )

    benchmark_value = None
    benchmark_label = None
    if request.benchmark and request.benchmark.value is not None:
        benchmark_value = float(request.benchmark.value)
        benchmark_label = request.benchmark.label
    elif cfg.get("show_benchmark") and "benchmark_value" in df.columns and df["benchmark_value"].notna().any():
        benchmark_value = float(df["benchmark_value"].dropna().median())
        benchmark_label = str(cfg.get("benchmark_label") or "Reference")
    if benchmark_value is not None and not flip:
        layers.extend(horizontal_benchmark_layers(theme, cfg, benchmark_value, benchmark_label))

    width = theme.width("boxplot")
    height = theme.height("boxplot")
    if flip and group_count <= 1:
        width = max(width, 720)
        height = min(height, 220)

    return alt.layer(*layers, data=df).properties(width=width, height=height)


def render_boxplot(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = df.attrs.get("chart_config", {})
    default_title = spec.docs.split("\n")[0].lstrip("#").strip() if spec.docs else spec.chart_type
    title = request.title or default_title
    subtitle = _boxplot_subtitle(df, request)
    caption = build_data_caption(df)

    title_params = build_altair_title_params(
        title,
        subtitle=subtitle,
        caption=caption,
        title_size=theme.title_size(),
    )

    facet_by = str(cfg.get("facet_by") or request.field_values.get("facet_by") or "").strip()
    if facet_by and facet_by in df.columns:
        panel = _build_boxplot_panel(df, spec, request)
        out = panel.facet(
            facet=alt.Facet(f"{facet_by}:N", title=None),
            columns=int(cfg.get("facet_ncol") or request.field_values.get("facet_ncol") or 2),
        ).properties(title=alt.TitleParams(**title_params))
    else:
        out = _build_boxplot_panel(df, spec, request).properties(title=alt.TitleParams(**title_params))

    out = (
        out.configure_axis(
            labelFont=theme.font_family(),
            titleFont=theme.font_family(),
            labelColor=theme.color("neutral.axis", "#5B6770"),
            gridColor=theme.color("neutral.grid_major", "#D9E2EC"),
        )
        .configure_title(
            font=theme.font_family(),
            color=theme.color("neutral.text", "#1F2933"),
            subtitleColor=theme.color("neutral.text_muted", "#52606D"),
            subtitleFont=theme.font_family(),
        )
        .configure_view(stroke=None)
    )
    out.usermeta = {"caption": caption} if caption else {}
    return out
