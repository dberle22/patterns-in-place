from __future__ import annotations

import altair as alt
import pandas as pd

from ..captions import build_altair_title_params, build_data_caption
from ..render_helpers import resolve_variant
from ..request import ChartRequest
from ..specs import ChartSpec


def render_slopegraph(df: pd.DataFrame, spec: ChartSpec, request: ChartRequest) -> alt.Chart:
    theme = request.theme
    cfg = theme.chart_defaults_for(request.chart_type)
    title = request.title or _default_title(df, spec.chart_type)
    subtitle = request.subtitle or _default_subtitle(df)
    caption = build_data_caption(df)

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

    base = alt.Chart(data).mark_line(point=bool(request.field_values.get("show_points", True))).encode(
        x=alt.X("period_display:N", sort=periods, title=None),
        y=alt.Y(
            "plot_value:Q",
            title=_y_axis_title(df),
            sort="descending" if _variant(df, request) == "rank" else None,
            axis=alt.Axis(format=theme.d3_format(request.number_format)),
        ),
        detail="geo_id:N",
        color=alt.Color("line_type:N", scale=color_scale, legend=None),
        tooltip=[
            alt.Tooltip("geo_name:N", title="Geography"),
            alt.Tooltip("period_display:N", title="Period"),
            alt.Tooltip("plot_value:Q", title="Value", format=theme.d3_format(request.number_format)),
        ],
    )

    labels_df = _build_label_rows(
        data,
        periods,
        label_mode=str(request.field_values.get("label_mode", "end")),
        show_delta_labels=bool(request.field_values.get("show_delta_labels", True)),
        label_max_chars=int(request.field_values.get("label_max_chars", 36)),
    )
    left_labels = alt.Chart(labels_df[labels_df["label_side"] == "left"]).mark_text(
        align="right",
        dx=-6,
        font=theme.font_family(),
        color=theme.color("neutral.text", "#1F2933"),
    ).encode(x="period_display:N", y="plot_value:Q", text="label_text:N")
    right_labels = alt.Chart(labels_df[labels_df["label_side"] == "right"]).mark_text(
        align="left",
        dx=6,
        font=theme.font_family(),
        color=theme.color("neutral.text", "#1F2933"),
    ).encode(x="period_display:N", y="plot_value:Q", text="label_text:N")

    title_params = build_altair_title_params(
        title,
        subtitle=subtitle,
        caption=caption,
        title_size=theme.title_size(),
        subtitle_wrap_width=int(cfg.get("subtitle_wrap_width", 120)),
        caption_wrap_width=int(cfg.get("caption_wrap_width", 135)),
    )

    out = (
        alt.layer(base, left_labels, right_labels)
        .properties(
            width=theme.width("slopegraph"),
            height=theme.height("slopegraph"),
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
    out.usermeta = {"caption": caption} if caption else {}
    return out


def _default_title(df: pd.DataFrame, fallback: str) -> str:
    metric_label = df["metric_label"].dropna().iloc[0] if "metric_label" in df.columns and df["metric_label"].dropna().any() else fallback
    geo_levels = [str(value).strip() for value in df["geo_level"].dropna().unique()] if "geo_level" in df.columns else []
    if len(geo_levels) == 1 and geo_levels[0]:
        return f"{metric_label} change across selected {geo_levels[0]}s"
    return f"{metric_label} change across selected geographies"


def _default_subtitle(df: pd.DataFrame) -> str | None:
    parts: list[str] = []
    periods = [str(value) for value in df["period_label"].dropna().unique()] if "period_label" in df.columns else []
    if len(periods) == 2:
        parts.append(f"Change window: {periods[0]}-{periods[1]}")

    variant = str(df["variant"].dropna().iloc[0]) if "variant" in df.columns and df["variant"].dropna().any() else "value"
    if variant == "indexed":
        base_period = df["index_base_period"].dropna().iloc[0] if "index_base_period" in df.columns and df["index_base_period"].dropna().any() else periods[0]
        parts.append(f"Indexed to {base_period} = 100")
    elif variant == "rank":
        parts.append("Rank view; lower rank is better")

    groups = [str(value).strip() for value in df["group"].dropna().unique()] if "group" in df.columns else []
    groups = [value for value in groups if value]
    if len(groups) == 1:
        parts.append(f"Scope: {groups[0]}")
    return " | ".join(parts) if parts else None


def _y_axis_title(df: pd.DataFrame) -> str | None:
    metric_label = df["metric_label"].dropna().iloc[0] if "metric_label" in df.columns and df["metric_label"].dropna().any() else None
    variant = str(df["variant"].dropna().iloc[0]) if "variant" in df.columns and df["variant"].dropna().any() else "value"
    if variant == "indexed":
        base_period = df["index_base_period"].dropna().iloc[0] if "index_base_period" in df.columns and df["index_base_period"].dropna().any() else None
        return f"{metric_label} ({base_period} = 100)" if metric_label and base_period is not None else "Index"
    if variant == "rank":
        return "Rank"
    return metric_label


def _variant(df: pd.DataFrame, request: ChartRequest) -> str | None:
    requested = resolve_variant(request, keys=("variant",), default=None)
    if requested:
        return requested
    if "variant" in df.columns and df["variant"].dropna().any():
        return str(df["variant"].dropna().iloc[0])
    return None


def _build_label_rows(
    data: pd.DataFrame,
    periods: list[str],
    label_mode: str,
    show_delta_labels: bool,
    label_max_chars: int,
) -> pd.DataFrame:
    label_data = data.copy()
    if label_mode == "end":
        label_data = label_data[label_data["period_display"] == periods[-1]].copy()
    elif label_mode == "highlight_end":
        label_data = label_data[
            (label_data["period_display"] == periods[-1]) & (label_data["highlight_flag"] | label_data["benchmark_flag"])
        ].copy()
    elif label_mode == "highlight_both":
        label_data = label_data[label_data["highlight_flag"] | label_data["benchmark_flag"]].copy()

    label_data["label_side"] = label_data["period_display"].eq(periods[0]).map({True: "left", False: "right"})
    label_data["label_name"] = label_data["geo_name"].astype(str).map(lambda value: _truncate_label(value, label_max_chars))
    if show_delta_labels and "delta_value" in label_data.columns:
        label_data["label_text"] = label_data.apply(
            lambda row: f"{row['label_name']} ({_signed_value_label(row['delta_value'])})"
            if row["label_side"] == "right" and pd.notna(row["delta_value"])
            else row["label_name"],
            axis=1,
        )
    else:
        label_data["label_text"] = label_data["label_name"]
    return label_data


def _truncate_label(value: str, max_chars: int) -> str:
    if max_chars <= 4 or len(value) <= max_chars:
        return value
    return f"{value[: max_chars - 3]}..."


def _signed_value_label(value) -> str:
    if pd.isna(value):
        return ""
    sign = "+" if float(value) > 0 else ""
    rounded = round(float(value), 1)
    return f"{sign}{rounded:.1f}".rstrip("0").rstrip(".")
