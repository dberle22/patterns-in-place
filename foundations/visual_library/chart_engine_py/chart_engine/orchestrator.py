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
    spec = apply_overrides(
        spec,
        {
            "column_mapping": request.column_mapping,
            "runtime_config": request.field_values,
        },
    )

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

    if hasattr(chart, "savefig") and not hasattr(chart, "save"):
        default_format = request.output.format if request.output.format in {"png", "svg"} else "png"
    else:
        default_format = request.output.format
    path = request.output.path or Path(f"{request.chart_type}_output.{default_format}")
    # Altair charts need an explicit static-image backend for PNG/SVG export.
    # We use vl-convert directly here rather than the older altair_saver path
    # so the package stays current while keeping the validated Altair 4 pin.
    if hasattr(chart, "save"):
        if path.suffix.lower() in {".png", ".svg", ".pdf"}:
            _persist_altair_image(chart, path, request.output.scale_factor)
        else:
            chart.save(str(path))
    elif hasattr(chart, "savefig"):
        chart.savefig(str(path), dpi=96 * request.output.scale_factor)
    else:
        raise TypeError(f"Don't know how to persist chart of type {type(chart)}")
    return path


def _persist_altair_image(chart: Any, path: "Path", scale_factor: float) -> None:
    try:
        import altair as alt
    except ImportError as exc:  # pragma: no cover - package dependency guard
        raise ImportError("Altair is required to persist Altair chart objects.") from exc

    if not isinstance(chart, alt.TopLevelMixin):
        chart.save(str(path))
        return

    try:
        import vl_convert as vlc
    except ImportError as exc:
        raise ImportError(
            "Saving Altair charts as static images requires vl-convert-python. "
            "Install it in the active environment to enable PNG/SVG/PDF export."
        ) from exc

    vl_spec = chart.to_json()
    vl_version = _vegalite_version_for_altair()
    suffix = path.suffix.lower()

    if suffix == ".png":
        image_bytes = vlc.vegalite_to_png(
            vl_spec,
            vl_version=vl_version,
            scale=scale_factor,
        )
        path.write_bytes(image_bytes)
        return

    if suffix == ".svg":
        svg_text = vlc.vegalite_to_svg(vl_spec, vl_version=vl_version)
        path.write_text(svg_text, encoding="utf-8")
        return

    if suffix == ".pdf" and hasattr(vlc, "vegalite_to_pdf"):
        pdf_bytes = vlc.vegalite_to_pdf(
            vl_spec,
            vl_version=vl_version,
            scale=scale_factor,
        )
        path.write_bytes(pdf_bytes)
        return

    chart.save(str(path))


def _vegalite_version_for_altair() -> str | None:
    """
    Pick the vl-convert runtime version that can actually render our chart specs.

    vl-convert no longer ships Vega-Lite 4 runtimes, so our current Altair 4
    chart specs need to be rendered through the oldest supported Vega-Lite 5
    runtime. For the current chart surface this is a pragmatic compatibility
    bridge that keeps CE moving without forcing an Altair major upgrade.
    """
    import vl_convert as vlc

    supported = vlc.get_vegalite_versions()
    if not supported:
        return None

    for candidate in supported:
        if candidate.startswith("5."):
            return candidate
    return supported[0]


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
