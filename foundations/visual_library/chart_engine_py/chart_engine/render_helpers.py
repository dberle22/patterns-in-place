from __future__ import annotations

import altair as alt
import pandas as pd

from .request import ChartRequest


def resolve_variant(request: ChartRequest, *, keys: tuple[str, ...] = ("variant",), default: str | None = None) -> str | None:
    for key in keys:
        value = request.field_values.get(key)
        if value is None:
            continue
        text = str(value).strip().lower()
        if text:
            return text
    return default


def horizontal_benchmark_layers(theme, cfg: dict, benchmark_value: float, benchmark_label: str | None) -> list[alt.Chart]:
    bench_df = pd.DataFrame({"value": [benchmark_value], "label": [benchmark_label]})
    layers: list[alt.Chart] = [
        alt.Chart(bench_df)
        .mark_rule(
            color=theme.color("comparison.benchmark", cfg.get("benchmark_color", "#52606D")),
            strokeDash=cfg.get("benchmark_linetype", [4, 4]),
            strokeWidth=cfg.get("benchmark_linewidth", 1),
        )
        .encode(x="value:Q")
    ]
    if benchmark_label:
        layers.append(
            alt.Chart(bench_df)
            .mark_text(
                align="left",
                baseline="top",
                dx=6,
                dy=4,
                color=theme.color("comparison.benchmark", cfg.get("benchmark_color", "#52606D")),
                font=theme.font_family(),
                fontSize=theme.font_size("caption_size", 9),
                fontStyle="italic",
            )
            .encode(x="value:Q", y=alt.value(0), text="label:N")
        )
    return layers


def identity_reference_line(df: pd.DataFrame, theme) -> alt.Chart:
    numeric = pd.concat([df["x_value"], df["y_value"]], ignore_index=True).dropna()
    if numeric.empty:
        domain = [0.0, 1.0]
    else:
        domain = [float(numeric.min()), float(numeric.max())]
    return (
        alt.Chart(pd.DataFrame({"x_value": domain, "y_value": domain}))
        .mark_line(
            color=theme.color("neutral.text_muted", "#52606D"),
            opacity=0.65,
            strokeDash=[3, 3],
        )
        .encode(x="x_value:Q", y="y_value:Q")
    )


def median_quadrant_layers(df: pd.DataFrame, theme) -> list[alt.Chart]:
    if df.empty:
        return []
    x_mid = float(df["x_value"].median())
    y_mid = float(df["y_value"].median())
    return [
        alt.Chart(pd.DataFrame({"x_value": [x_mid]}))
        .mark_rule(color=theme.color("neutral.text_muted", "#52606D"), strokeDash=[2, 2], opacity=0.7)
        .encode(x="x_value:Q"),
        alt.Chart(pd.DataFrame({"y_value": [y_mid]}))
        .mark_rule(color=theme.color("neutral.text_muted", "#52606D"), strokeDash=[2, 2], opacity=0.7)
        .encode(y="y_value:Q"),
    ]
