"""Zone Explorer — Surface 1: cluster zone and tract map with demographics and scoring."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC_PATH = _REPO_ROOT / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

import pandas as pd
import pydeck as pdk
import streamlit as st
import duckdb

from retail_opportunity_finder.utils.config import get_db_path, load_settings
from retail_opportunity_finder.utils.geo import add_polygon_coords
from retail_opportunity_finder.app.zone_map import (
    apply_color_ramp,
    build_label_layer,
    build_metric_options,
    build_tooltip,
    build_tract_layer,
    build_zone_layer,
    load_cluster_tract_data,
    load_tract_data,
    load_zone_data,
)

st.set_page_config(page_title="Zone Explorer", layout="wide")

_settings = load_settings()
_market_key = _settings.get("default_market_key", "jacksonville_fl")
_market = _settings["markets"][_market_key]

# Carto Positron — no API key required.
_MAP_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"


@st.cache_resource
def _get_con():
    return duckdb.connect(str(get_db_path()), read_only=True)


@st.cache_data
def _load_tracts(_con, cbsa_code: str) -> pd.DataFrame:
    return load_tract_data(_con, cbsa_code)


@st.cache_data
def _load_zones(_con, market_key: str, zone_system: str) -> pd.DataFrame:
    return load_zone_data(_con, market_key, zone_system)


@st.cache_data
def _load_cluster_tracts(_con, market_key: str) -> pd.DataFrame:
    return load_cluster_tract_data(_con, market_key)


@st.cache_data
def _load_boundaries(_con, cbsa_code: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    cbsa_df = _con.execute(
        "SELECT cbsa_code, geom_wkt FROM rof_gold.cbsa_geometry WHERE cbsa_code = ?",
        [cbsa_code],
    ).df()
    county_df = _con.execute(
        "SELECT county_geoid, geom_wkt FROM rof_gold.county_geometry WHERE cbsa_code = ?",
        [cbsa_code],
    ).df()
    return cbsa_df, county_df


con = _get_con()
cbsa_code = _market["cbsa_code"]

# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("Zone Explorer")
    st.markdown(f"**Market:** {_market['label']}")
    st.divider()

    layer_mode = st.radio(
        "Layer Mode",
        options=["Tracts", "Cluster Zones"],
        horizontal=True,
    )

    st.caption(
        "Clusters group nearby tracts into practical retail search zones using tract "
        "scores plus supporting demographic and housing signals."
    )

    metric_options = build_metric_options()
    st.markdown("**Metric**")
    metric_label = st.selectbox(
        "Metric",
        options=list(metric_options.keys()),
        label_visibility="collapsed",
    )
    metric_col = metric_options[metric_label]

    st.divider()
    show_eligibility = st.toggle("Dim ineligible tracts", value=False)


def _unique_columns(columns: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for col in columns:
        if col not in seen:
            seen.add(col)
            unique.append(col)
    return unique


if "selected_zone_label" not in st.session_state:
    st.session_state["selected_zone_label"] = None

# ── Load data ─────────────────────────────────────────────────────────────────

tract_df = _load_tracts(con, cbsa_code)
zone_df = _load_zones(con, _market_key, "cluster")
cluster_tract_df = _load_cluster_tracts(con, _market_key)
cbsa_df, county_df = _load_boundaries(con, cbsa_code)

# ── Color ramp ────────────────────────────────────────────────────────────────

colored_df = apply_color_ramp(tract_df, metric_col)

if show_eligibility:
    ineligible = colored_df["eligible_v1"].fillna(0) == 0
    colored_df.loc[ineligible, "fill_color"] = colored_df.loc[ineligible, "fill_color"].apply(
        lambda c: [c[0], c[1], c[2], 60]  # 60 keeps hover events firing; 30 suppresses them
    )

selected_zone_label = st.session_state["selected_zone_label"] if layer_mode != "Tracts" else None
selected_zone_tracts: set[str] = set()
if selected_zone_label:
    selected_zone_tracts = set(
        cluster_tract_df.loc[
            cluster_tract_df["zone_label"] == selected_zone_label, "tract_geoid"
        ].dropna()
    )
    if selected_zone_tracts:
        colored_df["fill_color"] = colored_df.apply(
            lambda row: (
                row["fill_color"]
                if row["tract_geoid"] in selected_zone_tracts
                else [row["fill_color"][0], row["fill_color"][1], row["fill_color"][2], 35]
            ),
            axis=1,
        )

# ── Build layers ──────────────────────────────────────────────────────────────

layers: list[pdk.Layer] = [build_tract_layer(colored_df, pickable=True)]

cbsa_coords = add_polygon_coords(cbsa_df)
cbsa_valid = cbsa_coords[cbsa_coords["polygon_coords"].notna()]
if not cbsa_valid.empty:
    layers.append(pdk.Layer(
        "PolygonLayer",
        cbsa_valid,
        id="cbsa",
        get_polygon="polygon_coords",
        get_fill_color=[0, 0, 0, 0],
        get_line_color=[0, 0, 0, 210],
        line_width_min_pixels=2,
        stroked=True,
        filled=False,
    ))

county_coords = add_polygon_coords(county_df)
county_valid = county_coords[county_coords["polygon_coords"].notna()]
if not county_valid.empty:
    layers.append(pdk.Layer(
        "PolygonLayer",
        county_valid,
        id="counties",
        get_polygon="polygon_coords",
        get_fill_color=[0, 0, 0, 0],
        get_line_color=[80, 80, 80, 180],
        line_width_min_pixels=1.5,
        stroked=True,
        filled=False,
    ))

if layer_mode != "Tracts":
    if selected_zone_label:
        dim_zone_df = add_polygon_coords(zone_df.copy())
        dim_zone_df = dim_zone_df[dim_zone_df["polygon_coords"].notna()]
        layers.append(pdk.Layer(
            "PolygonLayer",
            dim_zone_df,
            id="zones_dim",
            get_polygon="polygon_coords",
            get_fill_color=[0, 0, 0, 0],
            get_line_color=[160, 160, 160, 110],
            line_width_min_pixels=1.5,
            pickable=False,
            stroked=True,
            filled=False,
        ))

        selected_zone_df = add_polygon_coords(zone_df[zone_df["zone_label"] == selected_zone_label].copy())
        selected_zone_df = selected_zone_df[selected_zone_df["polygon_coords"].notna()]
        if not selected_zone_df.empty:
            layers.append(pdk.Layer(
                "PolygonLayer",
                selected_zone_df,
                id="zones_selected",
                get_polygon="polygon_coords",
                get_fill_color=[0, 0, 0, 0],
                get_line_color=[220, 80, 0, 240],
                line_width_min_pixels=4,
                pickable=False,
                stroked=True,
                filled=False,
            ))
    else:
        layers.append(build_zone_layer(zone_df, pickable=False))
    layers.append(build_label_layer(zone_df))

# ── Render map ────────────────────────────────────────────────────────────────

view_state = pdk.ViewState(
    latitude=_market["default_map_center"]["lat"],
    longitude=_market["default_map_center"]["lon"],
    zoom=_market["default_map_zoom"],
)

deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    tooltip=build_tooltip("tract"),
    map_style=_MAP_STYLE,
)

st.pydeck_chart(deck, use_container_width=True)

# ── Below-map table ───────────────────────────────────────────────────────────

st.divider()

if layer_mode != "Tracts":
    st.subheader("Zones")
    zone_cols = _unique_columns([
        c for c in [
            "zone_label",
            "tracts",
            "total_population",
            "pop_growth_3yr_wtd",
            "pop_density_median",
            "units_per_1k_3yr_wtd",
            "price_proxy_pctl_median",
            "mean_tract_score",
        ]
        if c in zone_df.columns
    ])
    zone_table = zone_df[zone_cols].sort_values("mean_tract_score", ascending=False).reset_index(drop=True)
    zone_event = st.dataframe(
        zone_table,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="zone_table",
    )

    selected_zone = None
    if zone_event.selection.rows:
        selected_zone = zone_table.iloc[zone_event.selection.rows[0]]
        selected_label = selected_zone["zone_label"]
        if st.session_state["selected_zone_label"] != selected_label:
            st.session_state["selected_zone_label"] = selected_label
            st.rerun()
    else:
        selected_label = st.session_state["selected_zone_label"]
        if selected_label is not None:
            selected_matches = zone_table[zone_table["zone_label"] == selected_label]
            if not selected_matches.empty:
                selected_zone = selected_matches.iloc[0]

    if selected_zone is not None:
        if st.button("Clear Zone Focus", use_container_width=False):
            st.session_state["selected_zone_label"] = None
            st.rerun()
        st.subheader(f"Zone Tracts — {selected_zone['zone_label']}")
        zone_tracts = cluster_tract_df[cluster_tract_df["zone_label"] == selected_zone["zone_label"]].copy()
        tract_display_cols = _unique_columns([
            c for c in [
                "tract_geoid",
                "county_geoid",
                "pop_total",
                "pop_growth_3yr",
                "median_hh_income",
                "per_capita_income",
                "pov_rate",
                "median_gross_rent",
                "median_home_value",
                "pop_density",
                "units_per_1k_3yr",
                "retail_parcel_count",
                "retail_area_density",
                "local_retail_context_score",
                "tract_score",
                "eligible_v1",
            ]
            if c in zone_tracts.columns
        ])
        if metric_col in zone_tracts.columns:
            zone_tracts = zone_tracts.sort_values(metric_col, ascending=False, na_position="last")
        st.dataframe(
            zone_tracts[tract_display_cols],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Select a zone row to inspect the tracts inside that cluster.")
        st.session_state["selected_zone_label"] = None
else:
    st.session_state["selected_zone_label"] = None
    st.subheader(f"Top Tracts — {metric_label}")
    if metric_col in tract_df.columns:
        display_cols = _unique_columns([
            c for c in [
                "tract_geoid",
                "county_geoid",
                metric_col,
                "pop_total",
                "pop_growth_3yr",
                "median_hh_income",
                "per_capita_income",
                "pov_rate",
                "median_gross_rent",
                "median_home_value",
                "pop_density",
                "units_per_1k_3yr",
                "retail_parcel_count",
                "retail_area_density",
                "local_retail_context_score",
                "tract_score",
                "eligible_v1",
            ]
            if c in tract_df.columns
        ])
        top_tracts = tract_df[display_cols].dropna(subset=[metric_col]).sort_values(
            metric_col, ascending=False
        ).head(15)
        st.dataframe(top_tracts, use_container_width=True, hide_index=True)
