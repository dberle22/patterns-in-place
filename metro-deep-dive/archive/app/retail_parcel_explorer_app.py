"""Retail Parcel Explorer — Surface 2: parcel candidate browser with scoring."""

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
from retail_opportunity_finder.app.parcel_explorer import (
    SORT_OPTIONS,
    SUBTYPE_COLORS,
    apply_filters,
    apply_sort,
    build_out_of_zone_layer,
    build_parcel_layer,
    build_parcel_scatter_layer,
    build_selected_layer,
    load_out_of_shortlist,
    load_shortlist,
    score_status,
)
from retail_opportunity_finder.app.zone_map import (
    apply_color_ramp,
    build_metric_options,
    build_tooltip,
    build_zone_layer,
    load_tract_data,
    load_zone_data,
)

st.set_page_config(page_title="Retail Parcel Explorer", layout="wide")

_settings = load_settings()
_market_key = _settings.get("default_market_key", "jacksonville_fl")
_market = _settings["markets"][_market_key]

_MAP_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"


@st.cache_resource
def _get_con():
    return duckdb.connect(str(get_db_path()), read_only=False)


@st.cache_data
def _load_shortlist(_con, market_key: str, zone_system: str) -> pd.DataFrame:
    return load_shortlist(_con, market_key, zone_system)


@st.cache_data
def _load_out_of_shortlist(_con, market_key: str, zone_system: str) -> pd.DataFrame:
    return load_out_of_shortlist(_con, market_key, zone_system)


@st.cache_data
def _load_zones(_con, market_key: str, zone_system: str) -> pd.DataFrame:
    return load_zone_data(_con, market_key, zone_system)


@st.cache_data
def _load_tracts(_con, cbsa_code: str) -> pd.DataFrame:
    return load_tract_data(_con, cbsa_code)


@st.cache_data
def _load_cbsa_boundary(_con, cbsa_code: str) -> pd.DataFrame:
    return _con.execute(
        "SELECT cbsa_code, geom_wkt FROM rof_gold.cbsa_geometry WHERE cbsa_code = ?",
        [cbsa_code],
    ).df()


def _score_badge_html(label: str, value, status: str) -> str:
    colors = {"scored": "#28a745", "partial": "#e6a817", "unavailable": "#6c757d"}
    bg = colors.get(status, "#6c757d")
    val_str = f"{value:.3f}" if pd.notna(value) else "—"
    return (
        f'<span style="background:{bg};color:white;padding:1px 5px;'
        f'border-radius:3px;font-size:0.75em;vertical-align:middle">{status}</span>'
        f" **{label}:** {val_str}"
    )


def _subtype_legend_html() -> str:
    lines = []
    for subtype, color in SUBTYPE_COLORS.items():
        r, g, b = color[0], color[1], color[2]
        label = subtype.replace("_", " ").title()
        lines.append(
            f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:3px">'
            f'<div style="width:12px;height:12px;border-radius:2px;flex-shrink:0;'
            f'background:rgb({r},{g},{b})"></div>'
            f'<span style="font-size:0.82em">{label}</span></div>'
        )
    return "".join(lines)


con = _get_con()
cbsa_code = _market["cbsa_code"]

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("Parcel Explorer")
    st.markdown(f"**Market:** {_market['label']}")
    st.divider()

    # — View controls —
    st.markdown("**View**")
    zone_system = "cluster"
    st.caption("This view uses the cluster-based zone system only.")

    color_by = st.radio("Color by", ["Retail Subtype", "Opportunity Score"], horizontal=True)
    color_by_key = "subtype" if color_by == "Retail Subtype" else "score"

    show_out_of_zone = st.toggle("Show out-of-zone retail", value=False)

    show_tracts = st.toggle("Show tract demographics", value=False)
    tract_metric_col: str | None = None
    hover_focus = "Parcel Details"
    if show_tracts:
        metric_options = build_metric_options()
        tract_metric_label = st.selectbox(
            "Tract metric",
            options=list(metric_options.keys()),
            label_visibility="collapsed",
        )
        tract_metric_col = metric_options[tract_metric_label]
        hover_focus = st.radio(
            "Hover shows",
            ["Parcel Details", "Tract Demographics"],
            horizontal=True,
        )

    st.divider()

    # — Filters —
    st.markdown("**Filters**")

    base_df = _load_shortlist(con, _market_key, zone_system)
    zone_df = _load_zones(con, _market_key, zone_system)

    counties = st.multiselect(
        "County",
        options=sorted(base_df["county_name"].dropna().unique()),
    )

    zone_options = zone_df[["zone_id", "zone_label"]].drop_duplicates().sort_values("zone_id")
    zone_labels_map = dict(zip(zone_options["zone_label"], zone_options["zone_id"]))
    selected_zone_labels = st.multiselect("Zone", options=list(zone_labels_map.keys()))
    zone_ids = [zone_labels_map[lbl] for lbl in selected_zone_labels]

    subtypes = st.multiselect(
        "Retail Subtype",
        options=sorted(base_df["retail_subtype"].dropna().unique()),
    )

    val_p95 = float(base_df["just_value"].quantile(0.95))
    val_max_cap = round(val_p95 / 1_000_000 + 1) * 1_000_000
    val_range = st.slider(
        "Assessed Value ($)",
        min_value=0,
        max_value=int(val_max_cap),
        value=(0, int(val_max_cap)),
        step=100_000,
        format="$%d",
    )

    area_p95 = float(base_df["parcel_area_sqmi"].quantile(0.95))
    area_max_cap = round(area_p95 * 1000) / 1000 + 0.005
    area_range = st.slider(
        "Parcel Area (sq mi)",
        min_value=0.0,
        max_value=float(round(area_max_cap, 3)),
        value=(0.0, float(round(area_max_cap, 3))),
        step=0.001,
        format="%.3f",
    )

    with st.expander("Score Thresholds"):
        min_shortlist = st.slider("Min Opportunity Score", 0.0, 1.0, 0.0, 0.05)
        min_zone_quality = st.slider("Min Zone Quality", 0.0, 1.0, 0.0, 0.05)
        min_parcel_chars = st.slider("Min Parcel Characteristics", 0.0, 1.0, 0.0, 0.05)

    st.divider()
    sort_key = st.selectbox("Sort By", SORT_OPTIONS)

    st.divider()

    st.markdown("**Zone Details**")
    st.caption("Open `app/zone_explorer_app.py` for clustering details and full zone metrics.")

    # — Subtype legend —
    if color_by_key == "subtype":
        with st.expander("Subtype Legend"):
            st.markdown(_subtype_legend_html(), unsafe_allow_html=True)

# ── Data loading and filtering ────────────────────────────────────────────────

parcel_df = base_df.copy()

filters = {
    "counties": counties,
    "zone_ids": zone_ids,
    "subtypes": subtypes,
    "val_range": val_range,
    "area_range": area_range,
    "min_shortlist_score": min_shortlist,
    "min_zone_quality_score": min_zone_quality,
    "min_parcel_chars_score": min_parcel_chars,
}

filtered_df = apply_sort(apply_filters(parcel_df, filters), sort_key)

# ── Resolve selection ─────────────────────────────────────────────────────────

if "selected_parcel_uid" not in st.session_state:
    st.session_state["selected_parcel_uid"] = None

# ── Build map layers ──────────────────────────────────────────────────────────

layers: list[pdk.Layer] = []
show_tract_tooltip = show_tracts and hover_focus == "Tract Demographics"

if show_tracts and tract_metric_col:
    tract_df = _load_tracts(con, cbsa_code)
    colored_tract_df = apply_color_ramp(tract_df, tract_metric_col)
    colored_tract_df["fill_color"] = colored_tract_df["fill_color"].apply(
        lambda c: [c[0], c[1], c[2], min(c[3], 130)]
    )
    colored_tract_df = add_polygon_coords(colored_tract_df)
    colored_tract_df = colored_tract_df[colored_tract_df["polygon_coords"].notna()]
    layers.append(pdk.Layer(
        "PolygonLayer",
        colored_tract_df,
        id="tracts",
        get_polygon="polygon_coords",
        get_fill_color="fill_color",
        get_line_color=[100, 100, 100, 60],
        line_width_min_pixels=0.5,
        pickable=show_tract_tooltip,
        opacity=1.0,
    ))

if show_out_of_zone:
    oos_df = _load_out_of_shortlist(con, _market_key, zone_system)
    layers.append(build_out_of_zone_layer(oos_df, pickable=not show_tract_tooltip))

parcel_scatter_layer = build_parcel_scatter_layer(filtered_df)
parcel_scatter_layer.pickable = not show_tract_tooltip
layers.append(parcel_scatter_layer)

parcel_layer = build_parcel_layer(filtered_df, color_by=color_by_key)
parcel_layer.pickable = not show_tract_tooltip
layers.append(parcel_layer)
layers.append(build_zone_layer(zone_df, pickable=False))

cbsa_df = _load_cbsa_boundary(con, cbsa_code)
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
        pickable=False,
    ))

selected_row = None
if st.session_state["selected_parcel_uid"] is not None:
    selected_matches = filtered_df[filtered_df["parcel_uid"] == st.session_state["selected_parcel_uid"]]
    if not selected_matches.empty:
        selected_row = selected_matches.iloc[0]
    else:
        st.session_state["selected_parcel_uid"] = None

if selected_row is not None:
    sel_layer = build_selected_layer(selected_row)
    if sel_layer:
        layers.append(sel_layer)

view_state = pdk.ViewState(
    latitude=_market["default_map_center"]["lat"],
    longitude=_market["default_map_center"]["lon"],
    zoom=_market["default_map_zoom"],
)

deck = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    tooltip=(
        build_tooltip("tract")
        if show_tract_tooltip
        else {
            "html": (
                "<b>{site_addr}</b><br/>"
                "<span style='opacity:0.75'>{retail_subtype} &bull; {county_name}</span><br/>"
                "Zone: {zone_label} &nbsp; Opportunity Score: {shortlist_score}"
            ),
            "style": {"backgroundColor": "white", "color": "#333",
                      "padding": "8px", "maxWidth": "220px"},
        }
    ),
    map_style=_MAP_STYLE,
)

# ── Layout: full-width map when no parcel selected, split when detail is shown ─

if selected_row is not None:
    col_map, col_detail = st.columns([2, 1])
    with col_map:
        st.pydeck_chart(deck, use_container_width=True)
else:
    st.pydeck_chart(deck, use_container_width=True)

# ── Detail panel (only rendered when a parcel is selected) ────────────────────

if selected_row is not None:
    with col_detail:
        r = selected_row

        if st.button("Clear Selection", use_container_width=True):
            st.session_state["selected_parcel_uid"] = None
            st.rerun()

        st.markdown("#### Identity")
        st.markdown(f"**Address:** {r.get('site_addr') or '—'}")
        st.markdown(f"**County:** {r.get('county_name') or '—'}")
        st.markdown(f"**Zone:** {r.get('zone_label') or '—'}")
        st.markdown(f"**Subtype:** {r.get('retail_subtype') or '—'}")
        st.markdown(f"**Land Use Code:** {r.get('land_use_code') or '—'}")
        st.markdown(f"**Owner:** {r.get('owner_name') or '—'}")

        st.divider()

        def _fmt_money(v) -> str:
            return f"${v:,.0f}" if pd.notna(v) and v > 0 else "—"

        def _fmt_date(v) -> str:
            if pd.isna(v):
                return "—"
            try:
                return pd.Timestamp(v).strftime("%Y-%m-%d")
            except Exception:
                return str(v)

        st.markdown("#### Parcel Facts")
        st.markdown(f"**Area:** {r['parcel_area_sqmi']:.4f} sq mi" if pd.notna(r.get("parcel_area_sqmi")) else "**Area:** —")
        st.markdown(f"**Assessed Value:** {_fmt_money(r.get('just_value'))}")
        st.markdown(f"**Land Value:** {_fmt_money(r.get('land_value'))}")
        st.markdown(f"**Improvement Value:** {_fmt_money(r.get('impro_value'))}")
        st.markdown(f"**Last Sale:** {_fmt_date(r.get('last_sale_date'))} &nbsp; {_fmt_money(r.get('last_sale_price'))}")

        st.divider()

        st.markdown("#### Scores")
        for label, val in [
            ("Opportunity Score", r.get("shortlist_score")),
            ("Zone Quality", r.get("zone_quality_score")),
            ("Parcel Characteristics", r.get("parcel_characteristics_score")),
            ("Local Retail Context", r.get("local_retail_context_score")),
            ("Mean Tract Score", r.get("mean_tract_score")),
        ]:
            st.markdown(
                _score_badge_html(label, val, score_status(val)),
                unsafe_allow_html=True,
            )

        st.divider()

        st.markdown("#### Zone Context")
        st.markdown(f"**Zone:** {r.get('zone_label') or '—'}")
        st.markdown(f"**Tracts:** {int(r['zone_tracts']) if pd.notna(r.get('zone_tracts')) else '—'}")
        st.markdown(f"**Population:** {int(r['zone_population']):,}" if pd.notna(r.get("zone_population")) else "**Population:** —")
        st.markdown(f"**Zone Mean Score:** {r['zone_mean_tract_score']:.3f}" if pd.notna(r.get("zone_mean_tract_score")) else "**Zone Mean Score:** —")

        st.divider()

        st.info("Zone-level methodology and full zone metrics live in the Zone Explorer.")

# ── Bottom: parcel list ───────────────────────────────────────────────────────

st.divider()
if selected_row is None:
    st.info("Select a row below to view parcel details.")
st.markdown(f"**{len(filtered_df):,} parcels**")

list_cols = ["shortlist_rank_system", "site_addr", "county_name", "zone_label",
             "retail_subtype", "parcel_area_sqmi", "just_value", "shortlist_score"]
list_display = filtered_df[list_cols].copy()
list_display.columns = ["#", "Address", "County", "Zone", "Type", "Area (sq mi)", "Value ($)", "Score"]
list_display["Score"] = list_display["Score"].map(lambda v: f"{v:.3f}" if pd.notna(v) else "—")
list_display["Value ($)"] = list_display["Value ($)"].map(lambda v: f"{v:,.0f}" if pd.notna(v) else "—")
list_display["Area (sq mi)"] = list_display["Area (sq mi)"].map(lambda v: f"{v:.4f}" if pd.notna(v) else "—")

event = st.dataframe(
    list_display,
    use_container_width=True,
    hide_index=True,
    height=320,
    on_select="rerun",
    selection_mode="single-row",
    key="parcel_table",
    column_config={
        "#": st.column_config.NumberColumn(width="small"),
        "Score": st.column_config.TextColumn(width="small"),
        "Area (sq mi)": st.column_config.TextColumn(width="small"),
    },
)

# Persist selection by parcel_uid so detail panel updates immediately and survives sorting/filtering
if event.selection.rows:
    selected_uid = filtered_df.iloc[event.selection.rows[0]]["parcel_uid"]
    if st.session_state["selected_parcel_uid"] != selected_uid:
        st.session_state["selected_parcel_uid"] = selected_uid
        st.rerun()
