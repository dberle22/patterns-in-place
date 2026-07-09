"""
render() is the real entry point and takes a ChartRequest — the full
input surface (theme, benchmark, annotations, facet, output config,
run context). This is deliberately not a flat function signature; see
request.py for why.

render_chart() is kept as convenience sugar for the common case (a
caller who just wants a chart back, no output config, no benchmark,
no annotations) — it builds a ChartRequest under the hood and delegates.
Both paths go through the same validation and registry lookup, so
there's exactly one place chart logic lives, not two.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .contracts import validate_contract
from .registry import CHART_REGISTRY
from .request import ChartRequest, ChartResult
from .specs import apply_overrides, load_spec
from .theme import Theme


def render(request: ChartRequest) -> ChartResult:
    if request.chart_type not in CHART_REGISTRY:
        available = ", ".join(sorted(CHART_REGISTRY))
        raise KeyError(f"Unknown chart_type '{request.chart_type}'. Available: {available}")

    reg = CHART_REGISTRY[request.chart_type]
    spec = load_spec(reg.spec_path)
    spec = apply_overrides(spec, {
        "column_mapping": request.column_mapping,
        **request.field_values,
    })

    prepped = reg.prep_fn(request.data, spec)
    validate_contract(prepped, spec)

    warnings: list[str] = []

    if request.facet and len(prepped.get(request.facet.facet_field, pd.Series(dtype=object)).unique()) > request.facet.max_panels:
        warnings.append(
            f"facet field '{request.facet.facet_field}' has more distinct values than "
            f"facet.max_panels ({request.facet.max_panels}); render_fn should truncate or the "
            f"caller should pre-filter."
        )

    if request.validate_only:
        return ChartResult(
            chart=None,
            chart_type=request.chart_type,
            output_path=None,
            prepped_data=prepped if request.return_prepped_data else None,
            alt_text=request.alt_text,
            warnings=warnings,
        )

    # render_fn receives the full request, not just (data, spec, theme) —
    # this is what lets an individual render function opt into benchmark/
    # annotation/facet support without changing the orchestrator's signature.
    chart = reg.render_fn(prepped, spec, request)

    output_path = None
    if request.output.save:
        output_path = _persist(chart, request)

    return ChartResult(
        chart=chart,
        chart_type=request.chart_type,
        output_path=output_path,
        prepped_data=prepped if request.return_prepped_data else None,
        alt_text=request.alt_text,
        warnings=warnings,
    )


def _persist(chart: Any, request: ChartRequest) -> "Path":
    from pathlib import Path

    path = request.output.path or Path(f"{request.chart_type}_output.{request.output.format}")
    # Altair charts: .save() dispatches on file extension already.
    # matplotlib figures: .savefig(). Dispatch here so render_fn stays
    # backend-agnostic and doesn't need to know about persistence at all.
    if hasattr(chart, "save"):
        chart.save(str(path))
    elif hasattr(chart, "savefig"):
        chart.savefig(str(path), dpi=96 * request.output.scale_factor)
    else:
        raise TypeError(f"Don't know how to persist chart of type {type(chart)}")
    return path


def render_chart(
    data: pd.DataFrame,
    chart_type: str,
    theme: Theme,
    **overrides: Any,
) -> Any:
    """
    Convenience wrapper for the common case. Returns the chart object
    directly (not a ChartResult) to match the earlier, simpler examples.
    For anything involving benchmarks, annotations, facets, or output
    persistence, build a ChartRequest and call render() instead.
    """
    known_request_fields = {"title", "subtitle", "field_values"}
    request_kwargs = {k: v for k, v in overrides.items() if k in known_request_fields}
    column_mapping = overrides.get("column_mapping", {})
    field_values = {
        k: v for k, v in overrides.items()
        if k not in known_request_fields and k != "column_mapping"
    }

    request = ChartRequest(
        data=data,
        chart_type=chart_type,
        theme=theme,
        column_mapping=column_mapping,
        field_values={**field_values, **request_kwargs.get("field_values", {})},
        title=request_kwargs.get("title"),
        subtitle=request_kwargs.get("subtitle"),
    )
    result = render(request)
    return result.chart

