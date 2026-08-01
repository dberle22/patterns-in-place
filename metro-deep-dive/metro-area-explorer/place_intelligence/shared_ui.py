"""Shared UI helpers for the Place Intelligence section."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd
import pydeck as pdk
import streamlit as st


SECTION_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SECTION_ROOT.parents[2]
CHART_ENGINE_ROOT = REPO_ROOT / "foundations" / "visual_library" / "chart_engine_py"
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))
if str(CHART_ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(CHART_ENGINE_ROOT))

from artifact_store import (
    artifacts_exist,
    load_artifact_base_payload,
    load_artifact_context_map_payload,
    load_artifact_d2_payload,
    load_artifact_d3_payload,
    load_artifact_d4_payload,
    load_artifact_d5_payload,
    load_artifact_market_payload,
)
from chart_engine import ChartRequest, NumberFormat, Theme, render
from site_prep import (
    D6_TRACT_FILL_METRICS,
    get_default_site_config_path,
    list_site_configs,
    load_site,
)


MAP_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"


def site_label(path: Path) -> str:
    """Build a stable site selector label from one YAML config."""

    site = load_site(str(path))
    return f"{site.address} ({site.site_id})"


def render_site_selector() -> Path:
    """Render the shared site selector and return the chosen YAML path."""

    config_paths = list_site_configs()
    labels = {site_label(path): path for path in config_paths}
    ordered_labels = list(labels)
    default_path = get_default_site_config_path()
    default_index = next(
        (idx for idx, label in enumerate(ordered_labels) if labels[label] == default_path),
        0,
    )
    chosen_label = st.selectbox("Site", ordered_labels, index=default_index)
    return labels[chosen_label]


def require_built_artifacts(site_config_path: str) -> None:
    """Stop the app with a clear message when the read-only artifacts are missing."""

    if artifacts_exist(site_config_path):
        return
    st.error(
        "Built site artifacts are missing for this site. Run "
        "`.venv312/bin/python metro-deep-dive/metro-area-explorer/place_intelligence/build_site_artifacts.py` "
        "before launching the app."
    )
    st.stop()


@st.cache_data(show_spinner=False)
def load_site_base_payload(site_config_path: str) -> dict[str, Any]:
    """Cache the built D1 base payload shared across all D6 tabs."""

    return load_artifact_base_payload(site_config_path)


@st.cache_data(show_spinner=False)
def load_d2_payload(site_config_path: str) -> dict[str, Any]:
    """Cache the built D2 catchment surface for one configured site."""

    return load_artifact_d2_payload(site_config_path)


@st.cache_data(show_spinner=False)
def load_d3_payload(site_config_path: str) -> dict[str, Any]:
    """Cache the built D3 context payload for one configured site."""

    return load_artifact_d3_payload(site_config_path)


@st.cache_data(show_spinner=False)
def load_d4_payload(site_config_path: str) -> dict[str, Any]:
    """Cache the built D4 traffic payload for one configured site."""

    return load_artifact_d4_payload(site_config_path)


@st.cache_data(show_spinner=False)
def load_d5_payload(site_config_path: str) -> dict[str, Any]:
    """Cache the built D5 flood payload for one configured site."""

    return load_artifact_d5_payload(site_config_path)


@st.cache_data(show_spinner=False)
def load_market_payload(site_config_path: str) -> dict[str, Any]:
    """Cache the built D6 Market-tab payload for one configured site."""

    return load_artifact_market_payload(site_config_path)


@st.cache_data(show_spinner=False)
def load_context_map_payload(site_config_path: str, fill_metric: str, include_flood_context: bool) -> dict[str, Any]:
    """Cache the built D6 context-map payload, including optional flood context."""

    return load_artifact_context_map_payload(site_config_path, fill_metric, include_flood_context)


def render_context_map(
    site_config_path: str,
    default_layers: dict[str, bool],
    map_key: str,
) -> None:
    """Render the single reusable D6 context map with per-tab default layer states."""

    fill_metric = st.selectbox(
        "Tract fill metric",
        options=list(D6_TRACT_FILL_METRICS.keys()),
        format_func=lambda value: D6_TRACT_FILL_METRICS[value],
        key=f"{map_key}_fill_metric",
    )
    show_tract_fill = st.checkbox("Show tract fill", value=default_layers.get("tract_fill", True), key=f"{map_key}_tract")
    show_rings = st.checkbox("Show rings", value=default_layers.get("rings", True), key=f"{map_key}_rings")
    show_pois = st.checkbox("Show POIs", value=default_layers.get("pois", False), key=f"{map_key}_pois")
    show_roads = st.checkbox("Show roads", value=default_layers.get("roads", False), key=f"{map_key}_roads")
    show_flood = st.checkbox("Show flood zones", value=default_layers.get("flood", False), key=f"{map_key}_flood")
    show_severed = st.checkbox("Show severed area", value=default_layers.get("severed", False), key=f"{map_key}_severed")

    payload = load_context_map_payload(
        site_config_path,
        fill_metric,
        bool(default_layers.get("flood", False)),
    )
    layers: list[pdk.Layer] = []
    if show_tract_fill and payload["tract_fill"]["features"]:
        layers.append(
            pdk.Layer(
                "GeoJsonLayer",
                {"type": "FeatureCollection", "features": payload["tract_fill"]["features"]},
                id=f"{map_key}-tract-fill",
                stroked=True,
                filled=True,
                get_fill_color="properties.fill_color",
                get_line_color=[92, 92, 92, 110],
                line_width_min_pixels=0.6,
                opacity=0.75,
                pickable=True,
            )
        )
    if show_rings:
        layers.append(
            pdk.Layer(
                "GeoJsonLayer",
                payload["rings_geojson"],
                id=f"{map_key}-rings",
                stroked=True,
                filled=False,
                get_line_color=[37, 99, 235, 180],
                line_width_min_pixels=2,
                pickable=True,
            )
        )
    if show_roads and payload["road_geojson"]["features"]:
        layers.append(
            pdk.Layer(
                "GeoJsonLayer",
                payload["road_geojson"],
                id=f"{map_key}-roads",
                stroked=True,
                filled=False,
                get_line_color=[203, 88, 54, 190],
                line_width_min_pixels=1.5,
                pickable=True,
            )
        )
    if show_flood and payload["flood_geojson"]["features"]:
        layers.append(
            pdk.Layer(
                "GeoJsonLayer",
                payload["flood_geojson"],
                id=f"{map_key}-flood",
                stroked=True,
                filled=True,
                get_fill_color=[59, 130, 246, 70],
                get_line_color=[30, 64, 175, 110],
                line_width_min_pixels=0.7,
                pickable=True,
            )
        )
    if show_severed and payload["severed_area_geojson"]["features"]:
        layers.append(
            pdk.Layer(
                "GeoJsonLayer",
                payload["severed_area_geojson"],
                id=f"{map_key}-severed",
                stroked=False,
                filled=True,
                get_fill_color=[220, 38, 38, 90],
                pickable=True,
            )
        )
    if show_pois and not payload["poi_rows"].empty:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                payload["poi_rows"].to_dict("records"),
                id=f"{map_key}-pois",
                get_position="[lon, lat]",
                get_fill_color=[22, 163, 74, 190],
                get_radius=95,
                radius_min_pixels=3,
                pickable=True,
            )
        )
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            payload["site_point"],
            id=f"{map_key}-site",
            get_position="[lon, lat]",
            get_fill_color=[17, 24, 39, 255],
            get_radius=150,
            radius_min_pixels=6,
            pickable=True,
        )
    )

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(**payload["view_state"]),
        map_style=MAP_STYLE,
        tooltip={
            "html": (
                "<b>{tract_name}</b><br/>"
                "{metric_label}: {metric_value}<br/>"
                "{label}<br/>"
                "{flood_zone}"
            ),
            "style": {"backgroundColor": "rgba(255,255,255,0.96)", "color": "#111827", "fontSize": "12px"},
        },
    )
    st.pydeck_chart(deck, width="stretch")
    if payload["nfhl_service_status"] != "ok":
        st.caption(f"Flood layer unavailable right now: {payload['nfhl_service_error']}")


def render_chart_result(chart_result) -> None:
    """Render one chart-engine result through the appropriate Streamlit element."""

    if chart_result is None or chart_result.chart is None:
        st.info("Chart unavailable for this selection.")
        return
    chart = chart_result.chart
    if hasattr(chart, "to_dict"):
        st.vega_lite_chart(chart.to_dict(), width="stretch")
        return
    if hasattr(chart, "savefig"):
        st.pyplot(chart, clear_figure=False, width="stretch")
        return
    st.write(chart)


def build_simple_bar_chart(
    rows: pd.DataFrame,
    entity_col: str,
    value_col: str,
    title: str,
    subtitle: str,
    unit: str = "count",
    decimals: int = 0,
) -> Any:
    """Build a small orchestrator-backed bar chart from already prepared rows."""

    if rows.empty:
        return None
    data = rows.copy()
    data["entity"] = data[entity_col]
    data["value"] = pd.to_numeric(data[value_col], errors="coerce")
    data = data.dropna(subset=["entity", "value"])
    if data.empty:
        return None
    request = ChartRequest(
        data=data,
        chart_type="bar_chart",
        theme=Theme.default(),
        column_mapping={"entity": "entity", "value": "value"},
        title=title,
        subtitle=subtitle,
        number_format=NumberFormat(unit=unit, decimals=decimals),
    )
    return render(request)


def build_simple_line_chart(
    rows: pd.DataFrame,
    period_col: str,
    value_col: str,
    series_col: str,
    title: str,
    subtitle: str,
    unit: str = "count",
    decimals: int = 0,
) -> Any:
    """Build a small orchestrator-backed line chart from already prepared rows."""

    if rows.empty:
        return None
    data = rows.copy()
    data["period"] = data[period_col]
    data["value"] = pd.to_numeric(data[value_col], errors="coerce")
    data["series"] = data[series_col]
    data = data.dropna(subset=["period", "value", "series"])
    if data.empty:
        return None
    request = ChartRequest(
        data=data,
        chart_type="line_chart",
        theme=Theme.default(),
        column_mapping={"period": "period", "value": "value", "series": "series"},
        title=title,
        subtitle=subtitle,
        number_format=NumberFormat(unit=unit, decimals=decimals),
    )
    return render(request)


def render_html_table(df: pd.DataFrame) -> None:
    """Render small review tables without depending on Arrow conversion."""

    st.markdown(df.fillna("—").to_html(index=False), unsafe_allow_html=True)


def format_percent_cell(value) -> str:
    """Format percent-like cells defensively."""

    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return "—"
    return f"{float(numeric_value):.1%}"


def format_count_cell(value) -> str:
    """Format integer-like values for compact summaries."""

    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return "—"
    return f"{int(round(float(numeric_value))):,}"


def format_currency_cell(value) -> str:
    """Format currency-like values for compact summaries."""

    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return "—"
    return f"${float(numeric_value):,.0f}"


def format_ratio_cell(value) -> str:
    """Format ratio metrics consistently across D3/D4 summaries."""

    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return "—"
    return f"{float(numeric_value):.2f}x"
