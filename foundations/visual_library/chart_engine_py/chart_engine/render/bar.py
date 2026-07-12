from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_altair_title_params, build_data_caption
from ..formatters import format_value_for_request
from ..request import ChartRequest
from ..render_helpers import horizontal_benchmark_layers, resolve_variant
from ..specs import ChartSpec


def render_bar_chart(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = theme.chart_defaults_for(request.chart_type)
    default_title = spec.docs.split("\n")[0].lstrip("#").strip() if spec.docs else spec.chart_type
    title = request.title or _default_title(df, default_title)
    subtitle = request.subtitle or _default_subtitle(df)
    caption = build_data_caption(df)

    dims = request.dimensions
    width = dims.width if dims and dims.width else theme.width(request.chart_type)
    base_height = dims.height if dims and dims.height else theme.height(request.chart_type)
    height = max(base_height, len(df.index) * 22)

    plot_df = df.copy()
    plot_df["entity_label"] = plot_df.get("entity_label", plot_df["entity"]).astype(str)
    plot_df["entity_axis_label"] = plot_df["entity_label"].apply(lambda value: _truncate_label(value, 28))
    if "display_order" not in plot_df.columns:
        plot_df["display_order"] = range(1, len(plot_df.index) + 1)

    benchmark_value, benchmark_label = _resolve_benchmark(plot_df, request)
    variant = _resolve_bar_variant(plot_df, request)
    title_params = build_altair_title_params(
        title,
        subtitle=subtitle,
        caption=caption,
        title_size=theme.title_size(),
        subtitle_wrap_width=90,
        caption_wrap_width=105,
    )

    if variant == "diverging":
        bar_panel = _render_diverging_bar(plot_df, request, theme, cfg, width, height, benchmark_label)
    elif variant in {"stacked", "stacked_100"}:
        bar_panel = _render_stacked_bar(plot_df, request, theme, cfg, width, height, variant)
    else:
        bar_panel = _render_ranked_bar(plot_df, request, theme, cfg, width, height, benchmark_value, benchmark_label)

    chart = (
        bar_panel.properties(title=alt.TitleParams(**title_params))
        .configure_title(
            font=theme.font_family(),
            color=theme.color("neutral.text", "#1F2933"),
            subtitleColor=theme.color("neutral.text_muted", "#52606D"),
            subtitleFont=theme.font_family(),
        )
        .configure_axis(
            labelFont=theme.font_family(),
            titleFont=theme.font_family(),
            labelColor=theme.color("neutral.axis", "#5B6770"),
            titleColor=theme.color("neutral.text_muted", "#52606D"),
            gridColor=theme.color("neutral.grid_major", "#D9E2EC"),
            tickColor=theme.color("neutral.border", "#CBD2D9"),
        )
        .configure_view(stroke=None)
    )
    chart.usermeta = {"caption": caption} if caption else {}
    return chart


def _default_title(df: pd.DataFrame, fallback: str) -> str:
    if "metric_label" not in df.columns or df["metric_label"].dropna().empty:
        return fallback
    metric_label = str(df["metric_label"].dropna().iloc[0]).strip()
    if not metric_label:
        return fallback
    return metric_label


def _default_subtitle(df: pd.DataFrame) -> str | None:
    parts: list[str] = []
    if "time_window" in df.columns:
        time_values = [str(v).strip() for v in df["time_window"].dropna().unique() if str(v).strip()]
        if time_values:
            parts.append(time_values[0])
    if "group" in df.columns:
        group_values = [str(v).strip() for v in df["group"].dropna().unique() if str(v).strip()]
        if len(group_values) == 1:
            parts.append(group_values[0])
    return " | ".join(parts) if parts else None


def _resolve_fill_colors(df: pd.DataFrame, theme, cfg: dict) -> pd.Series:
    if "highlight_flag" in df.columns and df["highlight_flag"].fillna(False).astype(bool).any():
        return df["highlight_flag"].fillna(False).astype(bool).map(
            {
                True: theme.color("highlight.selection", cfg.get("highlight_color", "#2C7FB8")),
                False: theme.color("comparison.neutral", cfg.get("neutral_color", "#A7B4C2")),
            }
        )
    return pd.Series(
        [theme.color("highlight.selection", cfg.get("base_color", "#2C7FB8"))] * len(df.index),
        index=df.index,
    )


def _resolve_bar_variant(df: pd.DataFrame, request: ChartRequest) -> str:
    requested = resolve_variant(request, keys=("bar_variant", "variant"))
    if requested in {"ranked_horizontal", "stacked", "stacked_100", "diverging"}:
        return requested

    has_series = "series" in df.columns and df["series"].dropna().nunique() > 1
    repeated_entities = "entity" in df.columns and df["entity"].astype(str).duplicated().any()
    if has_series and repeated_entities:
        if "share_value" in df.columns and pd.to_numeric(df["share_value"], errors="coerce").notna().any():
            return "stacked_100"
        return "stacked"

    if request.field_values.get("sort_by") == "benchmark_delta":
        return "diverging"
    if "benchmark_value" in df.columns and request.field_values.get("use_benchmark_delta"):
        return "diverging"

    return "ranked_horizontal"


def _render_ranked_bar(
    plot_df: pd.DataFrame,
    request: ChartRequest,
    theme,
    cfg: dict,
    width: int,
    height: int,
    benchmark_value: float | None,
    benchmark_label: str | None,
) -> alt.Chart:
    plot_df = plot_df.copy()
    plot_df["value_label"] = plot_df["value"].apply(lambda value: _format_bar_value(value, request))
    plot_df["fill_color"] = _resolve_fill_colors(plot_df, theme, cfg)
    domain_min, domain_max = _x_domain(plot_df["value"], benchmark_value)

    y_encoding = _bar_y_encoding(plot_df, theme)
    x_encoding = alt.X(
        "value:Q",
        title=_axis_title(plot_df),
        axis=_base_x_axis(theme, request),
        scale=alt.Scale(domain=[domain_min, domain_max], nice=True, zero=domain_min <= 0 <= domain_max),
    )

    tooltips = _ranked_tooltips(theme, request, plot_df)
    bars = alt.Chart(plot_df).mark_bar().encode(
        x=x_encoding,
        y=y_encoding,
        color=alt.Color("fill_color:N", scale=None, legend=None),
        tooltip=tooltips,
    )

    layers: list[alt.Chart] = [bars]
    if benchmark_value is not None:
        layers.extend(horizontal_benchmark_layers(theme, cfg, benchmark_value, benchmark_label))

    if bool(cfg.get("show_end_labels", True)):
        layers.append(
            alt.Chart(plot_df)
            .mark_text(
                align="left",
                baseline="middle",
                dx=6,
                color=theme.color("neutral.text", "#1F2933"),
                font=theme.font_family(),
                fontSize=theme.font_size("base_size", 12),
            )
            .encode(x="value:Q", y=y_encoding, text="value_label:N")
        )

    return alt.layer(*layers).properties(width=width, height=height)


def _render_diverging_bar(
    plot_df: pd.DataFrame,
    request: ChartRequest,
    theme,
    cfg: dict,
    width: int,
    height: int,
    benchmark_label: str | None,
) -> alt.Chart:
    data = plot_df.copy()
    data["benchmark_delta"] = pd.to_numeric(data["value"], errors="coerce") - pd.to_numeric(data["benchmark_value"], errors="coerce")
    data = data.loc[data["benchmark_delta"].notna()].copy()
    data = data.sort_values("benchmark_delta", key=lambda series: series.abs(), ascending=False, kind="mergesort")
    data["display_order"] = range(1, len(data.index) + 1)
    data["delta_label"] = data["benchmark_delta"].apply(lambda value: _format_delta_value(value, request))
    data["delta_direction"] = data["benchmark_delta"].apply(lambda value: "Above benchmark" if value >= 0 else "Below benchmark")

    domain_min, domain_max = _x_domain(data["benchmark_delta"], 0.0)
    y_encoding = _bar_y_encoding(data, theme)
    x_encoding = alt.X(
        "benchmark_delta:Q",
        title=_delta_axis_title(plot_df, benchmark_label),
        axis=_base_x_axis(theme, request),
        scale=alt.Scale(domain=[domain_min, domain_max], nice=True, zero=True),
    )
    color_scale = alt.Scale(
        domain=["Above benchmark", "Below benchmark"],
        range=[
            theme.color("comparison.positive", "#2A9D8F"),
            theme.color("comparison.negative", "#C44536"),
        ],
    )

    bars = alt.Chart(data).mark_bar().encode(
        x=x_encoding,
        y=y_encoding,
        color=alt.Color("delta_direction:N", scale=color_scale, legend=alt.Legend(title=None)),
        tooltip=[
            alt.Tooltip("entity:N", title="Entity"),
            alt.Tooltip("benchmark_delta:Q", title="Delta", format=theme.d3_format(request.number_format)),
            alt.Tooltip("benchmark_value:Q", title="Benchmark", format=theme.d3_format(request.number_format)),
        ],
    )
    zero_rule = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(
        color=theme.color("comparison.benchmark", cfg.get("benchmark_color", "#52606D")),
        strokeDash=cfg.get("benchmark_linetype", [4, 4]),
        strokeWidth=cfg.get("benchmark_linewidth", 1),
    ).encode(x="x:Q")
    positive_labels = alt.Chart(data[data["benchmark_delta"] >= 0]).mark_text(
        align="left",
        baseline="middle",
        dx=6,
        color=theme.color("neutral.text", "#1F2933"),
        font=theme.font_family(),
        fontSize=theme.font_size("base_size", 12),
    ).encode(x="benchmark_delta:Q", y=y_encoding, text="delta_label:N")
    negative_labels = alt.Chart(data[data["benchmark_delta"] < 0]).mark_text(
        align="right",
        baseline="middle",
        dx=-6,
        color=theme.color("neutral.text", "#1F2933"),
        font=theme.font_family(),
        fontSize=theme.font_size("base_size", 12),
    ).encode(x="benchmark_delta:Q", y=y_encoding, text="delta_label:N")
    return alt.layer(bars, zero_rule, positive_labels, negative_labels).properties(width=width, height=height)


def _render_stacked_bar(
    plot_df: pd.DataFrame,
    request: ChartRequest,
    theme,
    cfg: dict,
    width: int,
    height: int,
    variant: str,
) -> alt.Chart:
    data = plot_df.copy()
    value_field = "share_value" if variant == "stacked_100" and "share_value" in data.columns else "value"
    data[value_field] = pd.to_numeric(data[value_field], errors="coerce")
    if variant == "stacked_100" and value_field == "value":
        totals = data.groupby("entity")["value"].transform("sum")
        data["share_value"] = data["value"] / totals.where(totals != 0)
        value_field = "share_value"
    data = data.loc[data[value_field].notna()].copy()

    entity_order = (
        data.groupby(["entity", "entity_axis_label"], as_index=False)[value_field]
        .sum()
        .sort_values(value_field, ascending=False, kind="mergesort")
    )
    order_lookup = {entity: idx for idx, entity in enumerate(entity_order["entity"], start=1)}
    data["display_order"] = data["entity"].map(order_lookup).fillna(len(order_lookup) + 1)

    series_levels = [str(value) for value in pd.unique(data["series"].dropna())]
    if not series_levels:
        series_levels = ["Series"]
        data["series"] = "Series"
    palette = [
        theme.color("comparison.peers.0", "#AEBECD"),
        theme.color("comparison.peers.1", "#6E859E"),
        theme.color("comparison.peers.2", "#8C9472"),
        theme.color("comparison.peers.3", "#9A7F6B"),
        theme.color("highlight.selection", "#2C7FB8"),
    ]
    color_scale = alt.Scale(domain=series_levels, range=palette[: len(series_levels)])

    x_encoding = alt.X(
        f"{value_field}:Q",
        stack="zero",
        title=_stacked_axis_title(plot_df, variant),
        axis=_base_x_axis(theme, request if variant != "stacked_100" else _percent_like_request(request)),
    )
    y_encoding = _bar_y_encoding(data, theme)
    chart = alt.Chart(data).mark_bar().encode(
        x=x_encoding,
        y=y_encoding,
        color=alt.Color("series:N", scale=color_scale, legend=alt.Legend(title=None)),
        order=alt.Order("series:N"),
        tooltip=[
            alt.Tooltip("entity:N", title="Entity"),
            alt.Tooltip("series:N", title="Series"),
            alt.Tooltip(f"{value_field}:Q", title="Value", format=theme.d3_format(_percent_like_request(request).number_format if variant == "stacked_100" else request.number_format)),
        ],
    )
    return chart.properties(width=width, height=height)


def _bar_y_encoding(df: pd.DataFrame, theme) -> alt.Y:
    return alt.Y(
        "entity_axis_label:N",
        sort=alt.SortField(field="display_order", order="ascending"),
        axis=alt.Axis(
            title=None,
            labelLimit=220,
            labelFont=theme.font_family(),
            labelFontSize=theme.font_size("base_size", 12),
            labelColor=theme.color("neutral.text", "#1F2933"),
            ticks=False,
            domain=False,
        ),
    )


def _base_x_axis(theme, request: ChartRequest) -> alt.Axis:
    return alt.Axis(
        format=theme.d3_format(request.number_format),
        labelFont=theme.font_family(),
        titleFont=theme.font_family(),
        labelColor=theme.color("neutral.axis", "#5B6770"),
        titleColor=theme.color("neutral.text_muted", "#52606D"),
        gridColor=theme.color("neutral.grid_major", "#D9E2EC"),
        tickColor=theme.color("neutral.border", "#CBD2D9"),
    )


def _ranked_tooltips(theme, request: ChartRequest, plot_df: pd.DataFrame) -> list[alt.Tooltip]:
    tooltips = [
        alt.Tooltip("entity:N", title="Entity"),
        alt.Tooltip("value:Q", title="Value", format=theme.d3_format(request.number_format)),
    ]
    if "rank" in plot_df.columns:
        tooltips.append(alt.Tooltip("rank:Q", title="Rank"))
    return tooltips


def _resolve_benchmark(df: pd.DataFrame, request: ChartRequest) -> tuple[float | None, str | None]:
    if request.benchmark and request.benchmark.value is not None:
        label = request.benchmark.label or f"Benchmark: {_format_bar_value(request.benchmark.value, request)}"
        return request.benchmark.value, label
    if "benchmark_value" not in df.columns:
        return None, None
    values = pd.to_numeric(df["benchmark_value"], errors="coerce").dropna().unique()
    if len(values) != 1:
        return None, None
    benchmark_value = float(values[0])
    return benchmark_value, f"Benchmark: {_format_bar_value(benchmark_value, request)}"


def _x_domain(values: pd.Series, benchmark_value: float | None) -> tuple[float, float]:
    numeric_values = pd.to_numeric(values, errors="coerce").dropna().tolist()
    if benchmark_value is not None:
        numeric_values.append(float(benchmark_value))
    if not numeric_values:
        return 0.0, 1.0
    data_min = min(numeric_values)
    data_max = max(numeric_values)
    span = data_max - data_min
    padding = span * 0.14 if span > 0 else max(abs(data_max) * 0.08, 1.0)
    domain_min = min(0.0, data_min - padding * 0.15)
    domain_max = data_max + padding
    return domain_min, domain_max


def _axis_title(df: pd.DataFrame) -> str | None:
    if "metric_label" not in df.columns:
        return None
    labels = [str(value).strip() for value in df["metric_label"].dropna().unique() if str(value).strip()]
    return labels[0] if labels else None


def _delta_axis_title(df: pd.DataFrame, benchmark_label: str | None) -> str | None:
    label = _axis_title(df)
    if label and benchmark_label:
        return f"{label} vs {benchmark_label}"
    if label:
        return f"{label} benchmark delta"
    return benchmark_label or "Benchmark delta"


def _stacked_axis_title(df: pd.DataFrame, variant: str) -> str | None:
    if variant == "stacked_100":
        return "Share of total"
    return _axis_title(df)


def _format_bar_value(value: float | int | None, request: ChartRequest) -> str:
    formatted = format_value_for_request(value, request.number_format)
    return formatted or ""


def _format_delta_value(value: float | int | None, request: ChartRequest) -> str:
    formatted = _format_bar_value(value, request)
    if value is None or formatted == "":
        return ""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return formatted
    return formatted if numeric < 0 else f"+{formatted}"


def _percent_like_request(request: ChartRequest) -> ChartRequest:
    if request.number_format is not None and request.number_format.unit == "percent":
        return request
    cloned = ChartRequest(
        data=request.data,
        chart_type=request.chart_type,
        theme=request.theme,
        column_mapping=request.column_mapping,
        field_values=request.field_values,
        title=request.title,
        subtitle=request.subtitle,
        alt_text=request.alt_text,
        benchmark=request.benchmark,
        annotations=request.annotations,
        facet=request.facet,
        dimensions=request.dimensions,
        number_format=request.number_format,
        output=request.output,
        run_context=request.run_context,
        interactive=request.interactive,
        validate_only=request.validate_only,
        return_prepped_data=request.return_prepped_data,
    )
    if cloned.number_format is None:
        from ..request import NumberFormat

        cloned.number_format = NumberFormat(unit="percent", decimals=1)
    else:
        cloned.number_format = type(cloned.number_format)(unit="percent", decimals=max(cloned.number_format.decimals, 1), compact=False)
    return cloned


def _truncate_label(label: str, max_chars: int) -> str:
    if len(label) <= max_chars:
        return label
    return f"{label[: max_chars - 1].rstrip()}…"
