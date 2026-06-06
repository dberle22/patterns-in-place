"""Reference Streamlit dashboard for inspecting Gold-layer data."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import pandas as pd
import streamlit as st

CURRENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = CURRENT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from reference_dashboard import explorer_utils


st.set_page_config(layout="wide", page_title="Data Explorer")

GEO_LEVEL_OPTIONS = ["State", "Region", "Division", "County", "CBSA"]
SUBJECT_AREA_OPTIONS = ["Population", "Housing", "Income"]
STATE_FILTER_GEO_LEVELS = {"county", "cbsa"}
COLOR_SCALING_OPTIONS = ["Auto", "Raw", "Quantile"]
MAP_CENTER = {"lat": 38.5, "lon": -96}
MAP_ZOOM = 3
QUANTILE_COLOR_SEQUENCE = [
    "#f7fcf0",
    "#ccebc5",
    "#a8ddb5",
    "#7bccc4",
    "#4eb3d3",
    "#2b8cbe",
    "#08589e",
]

KPI_OPTIONS = {
    "population": [
        ("Total Population", "pop_total"),
        ("Pop Growth 1yr", "pop_growth_1yr"),
        ("Pop Growth 3yr", "pop_growth_3yr"),
        ("Pop Growth 5yr", "pop_growth_5yr"),
        ("Median Age", "median_age"),
        ("Share Under 18", "pct_age_under_18"),
        ("Share Age 65+", "pct_age_over_64"),
        ("Dependents Per Worker", "dependents_per_worker"),
        ("Hispanic Share", "pct_hispanic"),
        ("Diversity Index", "diversity_index"),
        ("Share With Bachelor's Degree Or Higher", "pct_ba_plus"),
    ],
    "housing": [
        ("Total Housing Units", "hu_total"),
        ("Vacancy Rate", "vacancy_rate"),
        ("Owner Occupancy Rate", "owner_occ_rate"),
        ("Renter Occupancy Rate", "renter_occ_rate"),
        ("Median Gross Rent", "median_gross_rent"),
        ("Annualized Median Rent", "annualized_median_rent"),
        ("Median Home Value", "median_home_value"),
        ("Share Rent Burdened 30%+", "pct_rent_burden_30plus"),
        ("Rent To Income Ratio", "rent_to_income"),
        ("Home Value To Income Ratio", "value_to_income"),
        ("Permits Per 1,000 Housing Units", "permits_per_1000_housing_units"),
    ],
    "income": [
        ("Median Household Income", "median_hh_income"),
        ("ACS Per Capita Income", "acs_income_pc"),
        ("Poverty Rate", "pov_rate"),
        ("Gini Index", "gini_index"),
        ("Total Personal Income", "pi_total"),
        ("BEA Per Capita Personal Income", "calc_income_pc"),
        ("Per Capita Income Growth 1yr", "income_pc_growth_1yr"),
        ("Per Capita Income Growth 5yr", "income_pc_growth_5yr"),
        ("Per Capita Income CAGR 5yr", "income_pc_cagr_5yr"),
        ("Wage Share Of Personal Income", "pi_wage_share"),
    ],
}


@st.cache_data(ttl=3600)
def load_state_options() -> list[tuple[str, str]]:
    valid_fips = explorer_utils.get_valid_state_fips()
    connection = explorer_utils.get_connection()
    try:
        rows = connection.execute(
            """
            SELECT state_name, state_fips
            FROM geo.states
            WHERE state_fips IN ({valid_states})
            ORDER BY state_name
            """.format(valid_states=explorer_utils._quoted_sql_list(tuple(sorted(valid_fips))))
        ).fetchall()
    finally:
        connection.close()

    return [(state_name, state_fips) for state_name, state_fips in rows]


@st.cache_data(ttl=3600)
def load_available_years(subject_area: str, geo_level: str) -> list[int]:
    normalized_subject_area = subject_area.strip().lower()
    normalized_geo_level = geo_level.strip().lower()
    table_name = explorer_utils.SUBJECT_AREA_TABLES[normalized_subject_area]

    connection = explorer_utils.get_connection()
    try:
        rows = connection.execute(
            f"""
            SELECT DISTINCT year
            FROM {table_name}
            WHERE lower(geo_level) = ?
            ORDER BY year DESC
            """,
            [normalized_geo_level],
        ).fetchall()
    finally:
        connection.close()

    return [int(year) for (year,) in rows]


def get_kpi_mappings(subject_area: str) -> tuple[dict[str, str], dict[str, str]]:
    normalized_subject_area = subject_area.strip().lower()
    display_to_column = {display: column for display, column in KPI_OPTIONS[normalized_subject_area]}
    column_to_display = {column: display for display, column in KPI_OPTIONS[normalized_subject_area]}
    return display_to_column, column_to_display


def get_available_kpi_pairs(subject_area: str, geo_level: str) -> list[tuple[str, str]]:
    normalized_subject_area = subject_area.strip().lower()
    normalized_geo_level = geo_level.strip().lower()
    metric_lookup = explorer_utils.get_metric_metadata(normalized_subject_area)
    available_pairs: list[tuple[str, str]] = []
    for display_name, column_name in KPI_OPTIONS[normalized_subject_area]:
        metric_meta = metric_lookup.get(column_name)
        valid_geo_levels = metric_meta.get("valid_geo_levels", []) if metric_meta else []
        if normalized_geo_level in valid_geo_levels:
            available_pairs.append((display_name, column_name))
    return available_pairs


def reset_kpi_state() -> None:
    subject_area = st.session_state["subject_area_display"].lower()
    geo_level = st.session_state.get("geo_level_display", GEO_LEVEL_OPTIONS[0]).lower()
    options = [display for display, _ in get_available_kpi_pairs(subject_area, geo_level)]
    if not options:
        st.session_state["map_kpi_display"] = ""
        st.session_state["table_kpis_display"] = []
        return
    st.session_state["map_kpi_display"] = options[0]
    st.session_state["table_kpis_display"] = options


def initialize_session_state() -> None:
    st.session_state.setdefault("geo_level_display", GEO_LEVEL_OPTIONS[0])
    st.session_state.setdefault("subject_area_display", SUBJECT_AREA_OPTIONS[0])
    if "map_kpi_display" not in st.session_state or "table_kpis_display" not in st.session_state:
        reset_kpi_state()
    st.session_state.setdefault("state_filter_names", [])
    st.session_state.setdefault("color_scaling_mode", COLOR_SCALING_OPTIONS[0])


def sync_kpi_state_with_geo(subject_area: str, geo_level: str) -> list[str]:
    available_options = [display for display, _ in get_available_kpi_pairs(subject_area, geo_level)]
    if not available_options:
        st.session_state["map_kpi_display"] = ""
        st.session_state["table_kpis_display"] = []
        return []

    current_map = st.session_state.get("map_kpi_display")
    if current_map not in available_options:
        st.session_state["map_kpi_display"] = available_options[0]

    current_table = st.session_state.get("table_kpis_display", [])
    filtered_table = [label for label in current_table if label in available_options]
    if not filtered_table:
        filtered_table = available_options
    st.session_state["table_kpis_display"] = filtered_table
    return available_options


def get_income_geo_warning(subject_area: str, geo_level: str, available_kpis: list[str]) -> str | None:
    if subject_area != "income":
        return None
    if geo_level not in {"state", "county", "cbsa"} and not available_kpis:
        return "Income metrics are only available at the state, county, and CBSA levels in the current Gold layer."
    return None


def should_use_diverging_scale(column_name: str, metric_meta: dict[str, Any] | None) -> bool:
    if column_name.startswith("pop_growth_") or column_name.startswith("hu_growth_") or column_name.startswith("income_pc_growth_"):
        return True
    if column_name.endswith("_cagr_5yr"):
        return True
    if metric_meta is None:
        return False
    return metric_meta.get("unit_format") == "ratio"


def should_use_quantile_scale(metric_meta: dict[str, Any] | None, values: pd.Series) -> bool:
    if metric_meta is None:
        return False

    if metric_meta.get("unit_format") not in {"integer", "currency"}:
        return False

    non_null = values.dropna()
    if len(non_null) < 10 or (non_null < 0).any():
        return False

    median_value = float(non_null.quantile(0.5))
    p99_value = float(non_null.quantile(0.99))
    if median_value <= 0:
        return False

    return (p99_value / median_value) >= 8


def resolve_color_scaling_mode(
    selected_mode: str,
    metric_meta: dict[str, Any] | None,
    values: pd.Series,
) -> str:
    normalized_mode = selected_mode.strip().lower()
    if normalized_mode == "raw":
        return "raw"
    if normalized_mode == "quantile":
        return "quantile"
    return "quantile" if should_use_quantile_scale(metric_meta, values) else "raw"


def assign_quantile_buckets(values: pd.Series) -> pd.Series:
    quantile_breaks = [0.0, 0.2, 0.4, 0.6, 0.8, 0.95, 0.99, 1.0]
    labels = [
        "0-20th pct",
        "20-40th pct",
        "40-60th pct",
        "60-80th pct",
        "80-95th pct",
        "95-99th pct",
        "99-100th pct",
    ]

    ranked = values.rank(method="average", pct=True)
    bucketed = pd.cut(
        ranked,
        bins=quantile_breaks,
        labels=labels,
        include_lowest=True,
    )
    return bucketed.astype("object")


def build_map_rows(
    merged_geojson: dict[str, Any],
    map_kpi_column: str,
    map_kpi_display: str,
    metric_meta: dict[str, Any] | None,
) -> pd.DataFrame:
    rows = []
    unit_format = metric_meta.get("unit_format", "integer") if metric_meta else "integer"
    for feature in merged_geojson.get("features", []):
        properties = feature.get("properties", {})
        value = properties.get("kpi_value")
        rows.append(
            {
                "geo_id": properties.get("geo_id"),
                "geo_name": properties.get("geo_name"),
                map_kpi_column: value,
                "formatted_value": explorer_utils.format_value(value, unit_format),
                "kpi_label": map_kpi_display,
            }
        )
    return pd.DataFrame(rows)


def prepare_map_dataframe(
    map_rows: pd.DataFrame,
    map_kpi_column: str,
    metric_meta: dict[str, Any] | None,
    selected_mode: str,
) -> tuple[pd.DataFrame, str]:
    prepared = map_rows.copy()
    resolved_mode = resolve_color_scaling_mode(
        selected_mode=selected_mode,
        metric_meta=metric_meta,
        values=prepared[map_kpi_column],
    )
    if resolved_mode != "quantile":
        return prepared, resolved_mode

    non_null_mask = prepared[map_kpi_column].notna()
    prepared["color_bucket"] = None
    prepared.loc[non_null_mask, "color_bucket"] = assign_quantile_buckets(
        prepared.loc[non_null_mask, map_kpi_column]
    )
    return prepared, resolved_mode


def filter_table_rows(
    df: pd.DataFrame,
    map_kpi_column: str,
    slider_bounds: tuple[float, float] | None,
    default_bounds: tuple[float, float] | None,
) -> pd.DataFrame:
    filtered = df.copy()
    if slider_bounds is not None and default_bounds is not None and slider_bounds != default_bounds:
        min_value, max_value = slider_bounds
        filtered = filtered.loc[
            filtered[map_kpi_column].notna()
            & filtered[map_kpi_column].between(min_value, max_value, inclusive="both")
        ].copy()
    return filtered


def build_display_dataframe(
    df: pd.DataFrame,
    selected_kpis: list[str],
    subject_area: str,
    metric_lookup: dict[str, dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    growth_columns = [
        column for column in explorer_utils.GROWTH_COLUMNS[subject_area] if column in df.columns
    ]
    ordered_columns = ["geo_name", "geo_id"]
    ordered_columns.extend(column for column in selected_kpis if column in df.columns and column not in ordered_columns)
    ordered_columns.extend(column for column in growth_columns if column not in ordered_columns)

    raw_display = df.loc[:, [column for column in ordered_columns if column in df.columns]].copy()
    metric_meta = [
        metric_lookup[column]
        for column in raw_display.columns
        if column in metric_lookup
    ]
    formatted_display = explorer_utils.format_dataframe(raw_display, metric_meta)

    rename_map = {"geo_name": "Geography", "geo_id": "Geo ID"}
    for column_name, metric in metric_lookup.items():
        if column_name in formatted_display.columns:
            rename_map[column_name] = metric.get("display_name", column_name)

    return raw_display, formatted_display.rename(columns=rename_map)


def render_map(
    merged_geojson: dict[str, Any],
    map_rows: pd.DataFrame,
    map_kpi_column: str,
    map_kpi_display: str,
    diverging_scale: bool,
    metric_meta: dict[str, Any] | None,
    selected_color_scaling_mode: str,
) -> str:
    try:
        import plotly.express as px
        import plotly.graph_objects as go
    except ImportError:
        st.error("Plotly is required to render the choropleth map. Install dependencies from `requirements.txt` to enable Sprint 3.")
        return False

    prepared_rows, use_quantiles = prepare_map_dataframe(
        map_rows=map_rows,
        map_kpi_column=map_kpi_column,
        metric_meta=metric_meta,
        selected_mode=selected_color_scaling_mode,
    )
    non_null_rows = prepared_rows.loc[prepared_rows[map_kpi_column].notna()].copy()
    null_rows = prepared_rows.loc[prepared_rows[map_kpi_column].isna()].copy()

    color_scale = "RdBu" if diverging_scale else "Viridis"

    if non_null_rows.empty:
        fig = go.Figure()
    elif use_quantiles:
        try:
            fig = px.choropleth_mapbox(
                non_null_rows,
                geojson=merged_geojson,
                locations="geo_id",
                color="color_bucket",
                featureidkey="properties.geo_id",
                mapbox_style="carto-positron",
                center=MAP_CENTER,
                zoom=MAP_ZOOM,
                color_discrete_sequence=QUANTILE_COLOR_SEQUENCE,
                category_orders={
                    "color_bucket": [
                        "0-20th pct",
                        "20-40th pct",
                        "40-60th pct",
                        "60-80th pct",
                        "80-95th pct",
                        "95-99th pct",
                        "99-100th pct",
                    ]
                },
                height=450,
                custom_data=["geo_name", "formatted_value", "color_bucket"],
            )
            fig.update_traces(
                hovertemplate=(
                    f"<b>%{{customdata[0]}}</b><br>{map_kpi_display}: %{{customdata[1]}}"
                    "<br>Quantile: %{customdata[2]}<extra></extra>"
                ),
                marker_line_width=0.2,
            )
        except ValueError:
            use_quantiles = "raw"
            fig = px.choropleth_mapbox(
                non_null_rows,
                geojson=merged_geojson,
                locations="geo_id",
                color=map_kpi_column,
                featureidkey="properties.geo_id",
                mapbox_style="carto-positron",
                center=MAP_CENTER,
                zoom=MAP_ZOOM,
                color_continuous_scale=color_scale,
                height=450,
                custom_data=["geo_name", "formatted_value"],
            )
            fig.update_traces(
                hovertemplate=f"<b>%{{customdata[0]}}</b><br>{map_kpi_display}: %{{customdata[1]}}<extra></extra>",
                marker_line_width=0.2,
            )
    else:
        fig = px.choropleth_mapbox(
            non_null_rows,
            geojson=merged_geojson,
            locations="geo_id",
            color=map_kpi_column,
            featureidkey="properties.geo_id",
            mapbox_style="carto-positron",
            center=MAP_CENTER,
            zoom=MAP_ZOOM,
            color_continuous_scale=color_scale,
            height=450,
            custom_data=["geo_name", "formatted_value"],
        )
        fig.update_traces(
            hovertemplate=f"<b>%{{customdata[0]}}</b><br>{map_kpi_display}: %{{customdata[1]}}<extra></extra>",
            marker_line_width=0.2,
        )

    if not null_rows.empty:
        fig.add_trace(
            go.Choroplethmapbox(
                geojson=merged_geojson,
                locations=null_rows["geo_id"],
                z=[0] * len(null_rows),
                featureidkey="properties.geo_id",
                colorscale=[[0, "#d0d0d0"], [1, "#d0d0d0"]],
                showscale=False,
                marker_opacity=0.5,
                marker_line_width=0.2,
                customdata=null_rows[["geo_name"]].to_numpy(),
                hovertemplate=f"<b>%{{customdata[0]}}</b><br>{map_kpi_display}: N/A<extra></extra>",
            )
        )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)
    return use_quantiles


def main() -> None:
    initialize_session_state()

    st.title("Data Explorer")
    st.caption(
        "Reference dashboard for validating Gold-layer geography, KPI, and year outputs used by the Demographics Chatbot."
    )

    state_options = load_state_options()
    state_name_to_fips = {state_name: state_fips for state_name, state_fips in state_options}

    with st.sidebar:
        st.header("Geography")
        geo_level_display = st.radio(
            "Geo Level",
            options=GEO_LEVEL_OPTIONS,
            key="geo_level_display",
        )
        normalized_geo_level = geo_level_display.lower()

        selected_state_names: list[str] = []
        if normalized_geo_level in STATE_FILTER_GEO_LEVELS:
            selected_state_names = st.multiselect(
                "State Filter",
                options=[state_name for state_name, _ in state_options],
                key="state_filter_names",
                help="Leave empty to include all contiguous states and DC.",
            )
        else:
            st.session_state["state_filter_names"] = []

        st.header("KPIs")
        subject_area_display = st.selectbox(
            "Subject Area",
            options=SUBJECT_AREA_OPTIONS,
            key="subject_area_display",
            on_change=reset_kpi_state,
        )
        normalized_subject_area = subject_area_display.lower()
        kpi_display_options = sync_kpi_state_with_geo(normalized_subject_area, normalized_geo_level)
        income_geo_warning = get_income_geo_warning(
            normalized_subject_area,
            normalized_geo_level,
            kpi_display_options,
        )

        if income_geo_warning:
            st.warning(income_geo_warning)

        if kpi_display_options:
            map_kpi_display = st.selectbox(
                "Map KPI",
                options=kpi_display_options,
                key="map_kpi_display",
            )
            table_kpis_display = st.multiselect(
                "Table KPIs",
                options=kpi_display_options,
                default=st.session_state.get("table_kpis_display", kpi_display_options),
                key="table_kpis_display",
            )
        else:
            st.selectbox(
                "Map KPI",
                options=["No KPI available for this geography"],
                index=0,
                disabled=True,
            )
            st.multiselect(
                "Table KPIs",
                options=[],
                default=[],
                disabled=True,
            )
            map_kpi_display = ""
            table_kpis_display = []

        st.header("Filters")
        available_years = load_available_years(normalized_subject_area, normalized_geo_level)
        if available_years:
            default_year = 2024 if 2024 in available_years else available_years[0]
            default_year_index = available_years.index(default_year)
            year = st.selectbox(
                "Year",
                options=available_years,
                index=default_year_index,
                key="selected_year",
            )
        else:
            st.selectbox(
                "Year",
                options=["No years available"],
                index=0,
                key="selected_year_placeholder",
                disabled=True,
            )
            year = None

        st.header("Map Settings")
        color_scaling_mode = st.selectbox(
            "Color Scaling",
            options=COLOR_SCALING_OPTIONS,
            key="color_scaling_mode",
            help="Auto uses quantile buckets only for heavily skewed absolute metrics.",
        )

    selected_state_fips = [state_name_to_fips[state_name] for state_name in selected_state_names]
    display_to_column, _ = get_kpi_mappings(normalized_subject_area)
    map_kpi_column = display_to_column.get(map_kpi_display)
    selected_table_kpis = [
        display_to_column[label]
        for label in table_kpis_display
        if label in display_to_column
    ]

    st.session_state["geo_level"] = normalized_geo_level
    st.session_state["state_filter"] = selected_state_fips
    st.session_state["subject_area"] = normalized_subject_area
    st.session_state["map_kpi"] = map_kpi_column
    st.session_state["table_kpis"] = selected_table_kpis
    st.session_state["year"] = year
    st.session_state["resolved_color_scaling_mode"] = color_scaling_mode.lower()

    if not map_kpi_column:
        st.warning(
            "No KPI is available for the current subject area and geography combination."
        )
        return

    if year is None:
        st.warning("No rows are available for the selected subject area and geography level.")
        return

    metric_lookup = explorer_utils.get_metric_metadata(normalized_subject_area)
    map_metric_meta = metric_lookup.get(map_kpi_column)

    df = explorer_utils.query_gold(
        geo_level=normalized_geo_level,
        subject_area=normalized_subject_area,
        year=year,
        state_filter=selected_state_fips or None,
    )

    if df.empty:
        if normalized_geo_level in STATE_FILTER_GEO_LEVELS and selected_state_fips:
            st.info("The selected state filter did not return any matching geographies.")
        else:
            st.warning("No data returned for the selected geography, KPI family, and year.")
        return

    slider_bounds: tuple[float, float] | None = None
    default_bounds: tuple[float, float] | None = None
    if map_kpi_column in df.columns:
        non_null_kpis = df[map_kpi_column].dropna()
        if not non_null_kpis.empty:
            lower_bound = float(non_null_kpis.quantile(0.01))
            upper_bound = float(non_null_kpis.quantile(0.99))
            if lower_bound > upper_bound:
                lower_bound, upper_bound = upper_bound, lower_bound
            default_bounds = (lower_bound, upper_bound)
            slider_key = f"kpi_range::{normalized_subject_area}::{normalized_geo_level}::{year}::{map_kpi_column}"
            slider_bounds = st.sidebar.slider(
                map_kpi_display,
                min_value=lower_bound,
                max_value=upper_bound,
                value=default_bounds,
                key=slider_key,
            )
        else:
            st.sidebar.slider(
                map_kpi_display,
                min_value=0.0,
                max_value=1.0,
                value=(0.0, 1.0),
                disabled=True,
                key=f"kpi_range_disabled::{normalized_subject_area}::{normalized_geo_level}::{year}::{map_kpi_column}",
            )
            st.sidebar.caption(f"{map_kpi_display}: all values are missing for this selection.")
    else:
        st.sidebar.slider(
            map_kpi_display,
            min_value=0.0,
            max_value=1.0,
            value=(0.0, 1.0),
            disabled=True,
            key=f"kpi_range_missing::{normalized_subject_area}::{normalized_geo_level}::{year}",
        )
        st.sidebar.caption(f"{map_kpi_display}: KPI column not available for this selection.")

    with st.spinner("Loading..."):
        geojson = explorer_utils.build_geojson(normalized_geo_level, selected_state_fips or None)
        merged_geojson = explorer_utils.merge_for_map(geojson, df, map_kpi_column)
        map_rows = build_map_rows(merged_geojson, map_kpi_column, map_kpi_display, map_metric_meta)

    st.subheader("Choropleth Map")
    resolved_color_scaling_mode = "raw"
    if map_rows[map_kpi_column].notna().any():
        with st.spinner("Loading..."):
            resolved_color_scaling_mode = render_map(
                merged_geojson=merged_geojson,
                map_rows=map_rows,
                map_kpi_column=map_kpi_column,
                map_kpi_display=map_kpi_display,
                diverging_scale=should_use_diverging_scale(map_kpi_column, map_metric_meta),
                metric_meta=map_metric_meta,
                selected_color_scaling_mode=color_scaling_mode,
            )
    else:
        st.warning("All geographies are missing data for the selected KPI and year.")

    st.caption("Gray areas indicate missing data for the selected KPI and year.")
    if resolved_color_scaling_mode == "quantile":
        st.caption("Colors are normalized by quantile buckets to reduce the impact of extreme outliers.")
    else:
        st.caption("Color scale: raw values.")
    st.caption(
        f"Showing {map_kpi_display} at the {geo_level_display.lower()} level • Year: {year} • {len(map_rows):,} geographies • Color scaling: {resolved_color_scaling_mode.title()}"
    )

    table_source = filter_table_rows(df, map_kpi_column, slider_bounds, default_bounds)
    table_source = table_source.sort_values(
        [map_kpi_column, "geo_name"],
        ascending=[False, True],
        na_position="last",
    ).reset_index(drop=True)
    with st.spinner("Loading..."):
        raw_display_df, display_df = build_display_dataframe(
            df=table_source,
            selected_kpis=selected_table_kpis,
            subject_area=normalized_subject_area,
            metric_lookup=metric_lookup,
        )

    st.subheader("Data Table")
    st.caption(f"{len(display_df):,} geographies")
    st.dataframe(display_df, use_container_width=True, height=400)
    st.download_button(
        "Download CSV",
        data=raw_display_df.to_csv(index=False).encode("utf-8"),
        file_name=f"data_explorer_{normalized_subject_area}_{normalized_geo_level}_{year}.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
