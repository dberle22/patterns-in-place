"""Shared UI helpers for the Place Intelligence section."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import altair as alt
from matplotlib import pyplot as plt
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
    load_artifact_market_page_payload,
    load_artifact_methods_payload,
    load_artifact_overview_payload,
    load_artifact_people_payload,
    load_artifact_place_payload,
)
from chart_engine import ChartRequest, NumberFormat, Theme, render
from site_prep import (
    D6_TRACT_FILL_METRICS,
    get_default_site_config_path,
    list_site_configs,
    load_site,
)


MAP_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
SOURCE_LABELS = {
    "population_demographics": "ACS 5-year / Census demographics",
    "economics_income_wide": "ACS 5-year income",
    "housing_core_wide": "ACS 5-year housing",
    "transport_built_form_wide": "ACS 5-year commute / built form",
    "gold.economics_industry_wide": "ACS / BEA industry mix",
    "LEHD": "LEHD",
    "FEMA NFHL": "FEMA NFHL",
    "FDOT": "FDOT AADT",
}


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
def load_overview_payload(site_config_path: str) -> dict[str, Any]:
    """Cache the compact Overview-page payload for one configured site."""

    return load_artifact_overview_payload(site_config_path)


@st.cache_data(show_spinner=False)
def load_d2_payload(site_config_path: str) -> dict[str, Any]:
    """Cache the built D2 catchment surface for one configured site."""

    return load_artifact_d2_payload(site_config_path)


@st.cache_data(show_spinner=False)
def load_people_payload(site_config_path: str) -> dict[str, Any]:
    """Cache the compact People-page payload for one configured site."""

    return load_artifact_people_payload(site_config_path)


@st.cache_data(show_spinner=False)
def load_place_payload(site_config_path: str) -> dict[str, Any]:
    """Cache the compact Place-page payload for one configured site."""

    return load_artifact_place_payload(site_config_path)


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


@st.cache_data(show_spinner=False)
def load_market_page_payload(site_config_path: str) -> dict[str, Any]:
    """Cache the compact Market-page payload for one configured site."""

    return load_artifact_market_page_payload(site_config_path)


@st.cache_data(show_spinner=False)
def load_methods_payload(site_config_path: str) -> dict[str, Any]:
    """Cache the compact Methods-page payload for one configured site."""

    return load_artifact_methods_payload(site_config_path)


def render_context_map(
    site_config_path: str,
    default_layers: dict[str, bool],
    map_key: str,
    *,
    allow_flood_layer: bool = True,
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
    show_flood = (
        st.checkbox("Show flood zones", value=default_layers.get("flood", False), key=f"{map_key}_flood")
        if allow_flood_layer
        else False
    )
    show_severed = st.checkbox("Show severed area", value=default_layers.get("severed", False), key=f"{map_key}_severed")

    payload = load_context_map_payload(
        site_config_path,
        fill_metric,
        bool(show_flood),
    )
    poi_rows = _prepare_poi_rows(payload["poi_rows"])
    available_poi_categories = sorted(poi_rows["display_category"].dropna().unique().tolist()) if not poi_rows.empty and "display_category" in poi_rows.columns else []
    selected_poi_categories = available_poi_categories
    if show_pois and available_poi_categories:
        selected_poi_categories = st.multiselect(
            "POI categories",
            options=available_poi_categories,
            default=available_poi_categories,
            key=f"{map_key}_poi_categories",
        )
        poi_rows = poi_rows.loc[poi_rows["display_category"].isin(selected_poi_categories)].copy()
    flood_geojson = _prepare_flood_geojson(payload["flood_geojson"])
    layers: list[pdk.Layer] = []
    tract_fill_geojson = _prepare_tract_fill_geojson(payload["tract_fill"]["features"])
    rings_geojson = _prepare_ring_geojson(payload["rings_geojson"])
    road_geojson = _prepare_road_geojson(payload["road_geojson"])
    severed_geojson = _prepare_severed_geojson(payload["severed_area_geojson"])
    site_points = _prepare_site_points(payload["site_point"])
    if show_tract_fill and tract_fill_geojson["features"]:
        layers.append(
            pdk.Layer(
                "GeoJsonLayer",
                tract_fill_geojson,
                id=f"{map_key}-tract-fill",
                stroked=True,
                filled=True,
                get_fill_color="properties.fill_color",
                get_line_color=[92, 92, 92, 110],
                line_width_min_pixels=0.6,
                opacity=0.75,
                pickable=True,
                auto_highlight=True,
            )
        )
    if show_rings:
        layers.append(
            pdk.Layer(
                "GeoJsonLayer",
                rings_geojson,
                id=f"{map_key}-rings",
                stroked=True,
                filled=False,
                get_line_color=[37, 99, 235, 180],
                line_width_min_pixels=2,
                pickable=True,
                auto_highlight=True,
            )
        )
    if show_roads and road_geojson["features"]:
        layers.append(
            pdk.Layer(
                "GeoJsonLayer",
                road_geojson,
                id=f"{map_key}-roads",
                stroked=True,
                filled=False,
                get_line_color=[203, 88, 54, 190],
                line_width_min_pixels=1.5,
                pickable=True,
                auto_highlight=True,
            )
        )
    if show_flood and flood_geojson["features"]:
        layers.append(
            pdk.Layer(
                "GeoJsonLayer",
                flood_geojson,
                id=f"{map_key}-flood",
                stroked=True,
                filled=True,
                get_fill_color="properties.fill_color",
                get_line_color=[30, 64, 175, 110],
                line_width_min_pixels=0.7,
                pickable=True,
                auto_highlight=True,
            )
        )
    if show_severed and severed_geojson["features"]:
        layers.append(
            pdk.Layer(
                "GeoJsonLayer",
                severed_geojson,
                id=f"{map_key}-severed",
                stroked=False,
                filled=True,
                get_fill_color=[220, 38, 38, 90],
                pickable=True,
                auto_highlight=True,
            )
        )
    if show_pois and not poi_rows.empty:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                poi_rows.to_dict("records"),
                id=f"{map_key}-pois",
                get_position="[lon, lat]",
                get_fill_color="fill_color",
                get_radius=55,
                radius_min_pixels=2,
                pickable=True,
                auto_highlight=True,
            )
        )
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            site_points,
            id=f"{map_key}-site",
            get_position="[lon, lat]",
            get_fill_color=[17, 24, 39, 255],
            get_radius=150,
            radius_min_pixels=6,
            pickable=True,
            auto_highlight=True,
        )
    )

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=pdk.ViewState(**payload["view_state"]),
        map_style=MAP_STYLE,
        tooltip={
            "html": (
                "<b>{tooltip_title}</b><br/>"
                "{tooltip_line_1}<br/>"
                "{tooltip_line_2}<br/>"
                "{tooltip_line_3}"
            ),
            "style": {"backgroundColor": "rgba(255,255,255,0.96)", "color": "#111827", "fontSize": "12px"},
        },
    )
    st.pydeck_chart(deck, width="stretch")
    if allow_flood_layer and payload["nfhl_service_status"] != "ok":
        st.caption(f"Flood layer unavailable right now: {payload['nfhl_service_error']}")


def _prepare_poi_rows(poi_rows: pd.DataFrame) -> pd.DataFrame:
    """Add category colors and clean tooltip fields to the POI scatter layer."""

    if poi_rows.empty:
        return poi_rows.copy()
    prepared = poi_rows.copy()
    prepared["display_category"] = prepared.get("display_category", prepared["poi_class"]).fillna("unknown").astype(str).str.replace("_", " ").str.title()
    prepared["fill_color"] = prepared["display_category"].map(_poi_category_color)
    prepared["tooltip_title"] = prepared["name"].fillna("").replace("", "Point of interest")
    prepared["tooltip_line_1"] = "Category: " + prepared["display_category"]
    prepared["tooltip_line_2"] = (
        "Coordinates: "
        + prepared["lat"].map(lambda value: f"{float(value):.5f}")
        + ", "
        + prepared["lon"].map(lambda value: f"{float(value):.5f}")
    )
    prepared["tooltip_line_3"] = ""
    return prepared


def _poi_category_color(category: object) -> list[int]:
    """Assign a stable but taxonomy-facing color to each Overture display category."""

    text = "unknown" if category is None else str(category)
    palette = [
        [37, 99, 235, 180],
        [22, 163, 74, 180],
        [234, 88, 12, 180],
        [168, 85, 247, 180],
        [236, 72, 153, 180],
        [14, 165, 233, 180],
        [245, 158, 11, 180],
        [99, 102, 241, 180],
        [16, 185, 129, 180],
        [239, 68, 68, 180],
    ]
    stable_index = sum((index + 1) * ord(char) for index, char in enumerate(text.lower()))
    return palette[stable_index % len(palette)]


def _prepare_tract_fill_geojson(features: list[dict[str, Any]]) -> dict[str, Any]:
    """Attach consistent tooltip fields to tract-fill polygons."""

    prepared_features: list[dict[str, Any]] = []
    for feature in features:
        prepared = dict(feature)
        props = dict(prepared.get("properties") or {})
        props["tooltip_title"] = props.get("tract_name") or "Census tract"
        metric_label = props.get("metric_label") or "Metric"
        metric_value = props.get("metric_value")
        props["tooltip_line_1"] = f"{metric_label}: {metric_value}"
        props["tooltip_line_2"] = props.get("tract_geoid") or ""
        props["tooltip_line_3"] = props.get("county_name") or ""
        prepared["properties"] = props
        prepared_features.append(prepared)
    return {"type": "FeatureCollection", "features": prepared_features}


def _prepare_ring_geojson(rings_geojson: dict[str, Any]) -> dict[str, Any]:
    """Attach tooltip text to ring outlines."""

    features = rings_geojson.get("features", [])
    prepared_features: list[dict[str, Any]] = []
    for feature in features:
        prepared = dict(feature)
        props = dict(prepared.get("properties") or {})
        ring_mi = props.get("ring_mi")
        props["tooltip_title"] = f"{ring_mi}-mile ring" if ring_mi is not None else "Ring"
        props["tooltip_line_1"] = "Straight-line cumulative catchment"
        props["tooltip_line_2"] = ""
        props["tooltip_line_3"] = ""
        prepared["properties"] = props
        prepared_features.append(prepared)
    return {"type": rings_geojson.get("type", "FeatureCollection"), "features": prepared_features}


def _prepare_road_geojson(road_geojson: dict[str, Any]) -> dict[str, Any]:
    """Attach tooltip text to road features."""

    features = road_geojson.get("features", [])
    prepared_features: list[dict[str, Any]] = []
    for feature in features:
        prepared = dict(feature)
        props = dict(prepared.get("properties") or {})
        props["tooltip_title"] = props.get("label") or "Road segment"
        aadt = props.get("aadt")
        props["tooltip_line_1"] = "" if aadt in (None, "") else f"AADT: {format_count_cell(aadt)}"
        props["tooltip_line_2"] = f"Year: {props.get('year')}" if props.get("year") else ""
        props["tooltip_line_3"] = props.get("county") or ""
        prepared["properties"] = props
        prepared_features.append(prepared)
    return {"type": road_geojson.get("type", "FeatureCollection"), "features": prepared_features}


def _prepare_severed_geojson(severed_geojson: dict[str, Any]) -> dict[str, Any]:
    """Attach tooltip text to severed-area polygons."""

    features = severed_geojson.get("features", [])
    prepared_features: list[dict[str, Any]] = []
    for feature in features:
        prepared = dict(feature)
        props = dict(prepared.get("properties") or {})
        ring_mi = props.get("ring_mi")
        props["tooltip_title"] = "Severed area"
        props["tooltip_line_1"] = f"Removed from {ring_mi}-mile ring" if ring_mi is not None else "Water-adjusted removal"
        props["tooltip_line_2"] = ""
        props["tooltip_line_3"] = ""
        prepared["properties"] = props
        prepared_features.append(prepared)
    return {"type": severed_geojson.get("type", "FeatureCollection"), "features": prepared_features}


def _prepare_site_points(site_points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Attach tooltip text to the site marker."""

    prepared_points: list[dict[str, Any]] = []
    for row in site_points:
        prepared = dict(row)
        prepared["tooltip_title"] = prepared.get("name") or "Site"
        prepared["tooltip_line_1"] = f"Match: {prepared.get('match_type') or 'unknown'}"
        prepared["tooltip_line_2"] = f"Source: {prepared.get('geocode_source') or 'unknown'}"
        prepared["tooltip_line_3"] = ""
        prepared_points.append(prepared)
    return prepared_points


def _prepare_flood_geojson(flood_geojson: dict[str, Any]) -> dict[str, Any]:
    """Normalize flood hover fields so the shared tooltip renders useful content."""

    features = flood_geojson.get("features", [])
    if not features:
        return flood_geojson
    prepared_features: list[dict[str, Any]] = []
    for feature in features:
        prepared = dict(feature)
        props = dict(prepared.get("properties") or {})
        zone = props.get("flood_zone") or props.get("ZONE_SUBTY") or props.get("FLD_ZONE") or "Flood zone"
        subtype = props.get("zone_subtype") or props.get("ZONE_SUBTY") or ""
        sfha = props.get("sfha_flag")
        props["fill_color"] = [59, 130, 246, 70]
        props["tooltip_title"] = f"Flood zone {zone}"
        props["tooltip_line_1"] = subtype or "FEMA National Flood Hazard Layer"
        props["tooltip_line_2"] = "" if sfha in (None, "") else f"SFHA: {sfha}"
        props["tooltip_line_3"] = ""
        prepared["properties"] = props
        prepared_features.append(prepared)
    return {"type": flood_geojson.get("type", "FeatureCollection"), "features": prepared_features}


def render_chart_result(chart_result) -> None:
    """Render one chart-engine result through the appropriate Streamlit element."""

    if chart_result is None or chart_result.chart is None:
        st.info("Chart unavailable for this selection.")
        return
    chart = chart_result.chart
    if hasattr(chart, "to_dict"):
        st.altair_chart(chart, use_container_width=True)
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
    """Build a small Matplotlib line chart for simple annual trend displays.

    These charts are intentionally plain. For Streamlit review surfaces we want
    the most reliable possible renderer, not the most abstract one.
    """

    if rows.empty:
        return None
    data = rows.copy()
    data["period"] = pd.to_numeric(data[period_col], errors="coerce")
    data["value"] = pd.to_numeric(data[value_col], errors="coerce")
    data["series"] = data[series_col].astype(str)
    data = data.dropna(subset=["period", "value", "series"])
    if data.empty:
        return None

    data = data.sort_values(["series", "period"], kind="mergesort")
    fig, ax = plt.subplots(figsize=(10, 4.4))
    palette = ["#2C7FB8", "#E67E22", "#2CA25F", "#7C3AED", "#D9485F"]

    for idx, (series_name, group) in enumerate(data.groupby("series", sort=False)):
        color = palette[idx % len(palette)]
        ax.plot(
            group["period"],
            group["value"],
            marker="o",
            linewidth=2.5,
            markersize=5,
            color=color,
            label=series_name,
        )

    ax.set_title(title, loc="left", fontsize=18, fontweight="bold", color="#1F2933", pad=18)
    if subtitle:
        ax.text(0.0, 1.02, subtitle, transform=ax.transAxes, ha="left", va="bottom", fontsize=10.5, color="#52606D")
    ax.grid(axis="y", color="#D9E2EC", linewidth=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#D9E2EC")
    ax.spines["bottom"].set_color("#D9E2EC")
    ax.tick_params(axis="x", colors="#52606D")
    ax.tick_params(axis="y", colors="#52606D")
    ax.set_xlabel("")
    ax.set_ylabel("")

    if unit == "currency":
        ax.yaxis.set_major_formatter(lambda value, _pos: f"${value:,.0f}")
    elif unit == "percent":
        ax.yaxis.set_major_formatter(lambda value, _pos: f"{value:.{decimals}%}")
    elif unit == "ratio":
        ax.yaxis.set_major_formatter(lambda value, _pos: f"{value:.{decimals}f}x")
    else:
        ax.yaxis.set_major_formatter(lambda value, _pos: f"{value:,.{decimals}f}" if decimals > 0 else f"{value:,.0f}")

    periods = sorted(data["period"].unique().tolist())
    ax.set_xticks(periods)
    ax.set_xticklabels([str(int(period)) for period in periods])

    if data["series"].nunique() > 1:
        ax.legend(frameon=False, loc="upper left")

    fig.tight_layout()
    return fig


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


def source_label(value: object) -> str:
    """Translate internal table identifiers into reader-facing source labels."""

    text = "" if value is None else str(value)
    return SOURCE_LABELS.get(text, text)


def format_ratio_cell(value) -> str:
    """Format ratio metrics consistently across D3/D4 summaries."""

    numeric_value = pd.to_numeric(value, errors="coerce")
    if pd.isna(numeric_value):
        return "—"
    return f"{float(numeric_value):.2f}x"
