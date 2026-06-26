"""Internal CBSA explorer entry point."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
AREA_EXPLORER_ROOT = APP_DIR.parents[1]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))
if str(AREA_EXPLORER_ROOT) not in sys.path:
    sys.path.insert(0, str(AREA_EXPLORER_ROOT))

from config import APP_TITLE
from shared.benchmark import format_metric_value
from shared.catalog import get_hierarchy, get_metric_meta, get_metrics_for_geo_level
from shared.components.distribution_tab import render_distribution_tab
from shared.components.intelligence_tab import render_intelligence_tab
from shared.components.map_panel import render_cbsa_map
from shared.components.profile_panel import render_profile_panel, render_similarity_peers
from shared.components.ranking_table import render_ranking_table
from shared.components.scatter_tab import render_scatter_tab
from shared.components.sidebar import render_metric_sidebar
from shared.components.trend_tab import render_trend_tab
from shared.db import (
    get_state_options,
    has_intelligence_datamart,
    query_available_years,
    query_intelligence_membership_table,
    query_intelligence_profile,
    query_intelligence_scatter,
    query_metric,
    query_metric_timeseries_batch,
    query_similarity_peers,
)
from shared.geo_utils import load_cbsa_geojson


st.set_page_config(layout="wide", page_title=APP_TITLE)


def _theme_lookup() -> dict[str, dict]:
    """Build the CBSA theme hierarchy map used by the sidebar."""
    hierarchy = get_hierarchy("cbsa")
    return {theme["theme_id"]: theme for theme in hierarchy["themes"]}


def _find_metric_index(metric_id: str, metrics: list[dict]) -> int:
    """Return the index for a metric id in the currently available metric pool."""
    for index, metric in enumerate(metrics):
        if metric["metric_id"] == metric_id:
            return index
    return 0


def _build_scatter_frame(x_metric_id: str, y_metric_id: str, year: int, state_filter: tuple[str, ...]) -> pd.DataFrame:
    """Build the scatter dataframe by merging two metric pulls on CBSA id."""
    x_df = query_metric(x_metric_id, year, state_filter)[["geo_id", "geo_name", "metric_value"]].rename(
        columns={"metric_value": "x_value"}
    )
    y_df = query_metric(y_metric_id, year, state_filter)[["geo_id", "metric_value"]].rename(
        columns={"metric_value": "y_value"}
    )
    return x_df.merge(y_df, on="geo_id", how="inner")


def main() -> None:
    """Render the internal CBSA explorer."""
    st.title(APP_TITLE)
    st.caption(
        "Phase 1 internal build: live CBSA metric explorer with Intelligence support from "
        "`mart_intelligence` when available and a parquet fallback otherwise."
    )

    theme_lookup = _theme_lookup()
    metric_pool = get_metrics_for_geo_level("cbsa")
    state_options = get_state_options()

    default_metric_id = metric_pool[0]["metric_id"] if metric_pool else None
    if default_metric_id is None:
        st.error("No CBSA-valid metrics were found in the semantic layer catalog.")
        return

    sidebar_state = render_metric_sidebar(
        theme_lookup=theme_lookup,
        state_options=state_options,
        metric_meta_lookup=get_metric_meta,
    )

    selected_metric_id = sidebar_state["metric_id"]
    metric_meta = get_metric_meta(selected_metric_id)
    if metric_meta is None:
        st.error(f"Metric metadata was not found for `{selected_metric_id}`.")
        return

    available_years = query_available_years(selected_metric_id)
    with st.sidebar:
        selected_year = st.select_slider("Year", options=available_years, value=available_years[0])
    selected_state_fips = sidebar_state["state_fips"]
    metric_df = query_metric(selected_metric_id, selected_year, selected_state_fips)
    if metric_df.empty:
        st.warning("No rows matched the current filter selection.")
        return

    selected_geo_id = st.selectbox(
        "Selected CBSA",
        metric_df["geo_id"].tolist(),
        format_func=lambda geo_id: metric_df.loc[metric_df["geo_id"] == geo_id, "geo_name"].iloc[0],
    )
    selected_row = metric_df.loc[metric_df["geo_id"] == selected_geo_id].iloc[0]
    intelligence_profile = query_intelligence_profile(selected_geo_id)
    similarity_peers = query_similarity_peers(selected_geo_id)

    with st.sidebar:
        st.caption(
            "Intelligence source: "
            + ("`mart_intelligence`" if has_intelligence_datamart() else "phase parquet fallback")
        )

    map_col, side_col = st.columns([2.1, 1.1])
    with map_col:
        st.subheader("Map")
        render_cbsa_map(
            metric_df=metric_df,
            geojson=load_cbsa_geojson(),
            color_scale_mode=sidebar_state["color_scale_mode"],
        )

    with side_col:
        st.subheader("Ranking")
        ranking_df = metric_df.copy()
        ranking_df.insert(0, "rank", range(1, len(ranking_df) + 1))
        ranking_df["display_value"] = ranking_df["metric_value"].apply(
            lambda value: format_metric_value(value, metric_meta.get("unit_format"))
        )
        render_ranking_table(ranking_df)
        render_profile_panel(metric_meta, selected_row, intelligence_profile)
        render_similarity_peers(similarity_peers)

    scatter_tab, trend_tab, distribution_tab, intelligence_tab = st.tabs(
        ["Scatter", "Trend", "Distribution", "Intelligence"]
    )

    with scatter_tab:
        default_x = "median_hh_income" if get_metric_meta("median_hh_income") else selected_metric_id
        default_y = "rent_to_income" if get_metric_meta("rent_to_income") else selected_metric_id
        render_scatter_tab(
            metric_pool=metric_pool,
            metric_meta_lookup=get_metric_meta,
            default_x=default_x,
            default_y=default_y,
            selected_geo_id=selected_geo_id,
            find_metric_index=_find_metric_index,
            build_scatter_frame=lambda x_metric_id, y_metric_id: _build_scatter_frame(
                x_metric_id,
                y_metric_id,
                selected_year,
                selected_state_fips,
            ),
        )

    with trend_tab:
        comparison_options = metric_df[["geo_id", "geo_name"]].drop_duplicates().sort_values("geo_name")
        comparison_lookup = dict(zip(comparison_options["geo_id"], comparison_options["geo_name"]))
        render_trend_tab(
            comparison_options=list(comparison_options.itertuples(index=False, name=None)),
            comparison_lookup=comparison_lookup,
            selected_geo_id=selected_geo_id,
            metric_display_name=metric_meta["display_name"],
            build_trend_frame=lambda geo_ids: query_metric_timeseries_batch(selected_metric_id, tuple(dict.fromkeys(geo_ids))),
        )

    with distribution_tab:
        render_distribution_tab(
            metric_df=metric_df,
            selected_value=float(selected_row["metric_value"]),
            metric_display_name=metric_meta["display_name"],
        )

    with intelligence_tab:
        try:
            intelligence_df = query_intelligence_scatter(selected_state_fips)
            membership_df = query_intelligence_membership_table(selected_state_fips)
        except FileNotFoundError:
            intelligence_df = pd.DataFrame()
            membership_df = pd.DataFrame()

        render_intelligence_tab(
            intelligence_df=intelligence_df,
            membership_df=membership_df,
            selected_geo_id=selected_geo_id,
            intelligence_profile=intelligence_profile,
        )


if __name__ == "__main__":
    main()
