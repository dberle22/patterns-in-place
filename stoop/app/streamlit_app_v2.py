"""Stoop Explore Streamlit app for neighborhood and place discovery."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from nyc_property_finder.app.base_map import (
    DEFAULT_PUBLIC_POI_CATEGORIES,
    DEFAULT_PUBLIC_POI_SELECTION,
    BaseGeographyData,
    PoiMapData,
    available_poi_categories,
    available_poi_subcategories,
    build_base_map_data_from_loaded,
    build_base_map_deck,
    filter_poi_points_by_categories,
    filter_points_to_supported_geography,
    filter_public_poi_points_by_categories,
    format_metric_value,
    load_base_geography_data,
    load_poi_map_data,
    load_public_poi_map_data,
    metric_options,
    poi_color_legend_rows,
)
from nyc_property_finder.app.stoop_explore import (
    ExploreCategoryOption,
    load_all_nta_character_profiles,
    load_explore_category_options,
    load_explore_rankings,
    load_nta_character_profile,
)
from nyc_property_finder.services.config import PROJECT_ROOT, load_config


st.set_page_config(page_title="Stoop Explore", layout="wide")


@st.cache_data(show_spinner="Loading geography and demographic layers...")
def cached_load_base_geography_data(
    database_path: str,
    tract_path: str,
    tract_id_col: str,
 ) -> BaseGeographyData:
    """Cached wrapper around metric-independent geography assembly."""

    return load_base_geography_data(
        database_path=database_path,
        tract_path=tract_path,
        tract_id_col=tract_id_col,
    )


@st.cache_data(show_spinner="Loading points of interest...")
def cached_load_poi_map_data(database_path: str) -> PoiMapData:
    """Cached wrapper around POI map-layer assembly."""

    return load_poi_map_data(database_path=database_path)


@st.cache_data(show_spinner="Loading public baseline POIs...")
def cached_load_public_poi_map_data(
    database_path: str,
    selected_categories: tuple[str, ...],
) -> PoiMapData:
    """Cached wrapper around public baseline POI loading."""

    return load_public_poi_map_data(
        database_path=database_path,
        selected_categories=selected_categories,
    )


def _format_explore_category_name(value: str) -> str:
    return str(value).replace("_", " ").title()


def _category_option_lookup(options: list[ExploreCategoryOption]) -> dict[str, ExploreCategoryOption]:
    return {option.category: option for option in options}


def _ranked_nta_options(rankings: pd.DataFrame, profiles: pd.DataFrame) -> list[tuple[str, str]]:
    options: list[tuple[str, str]] = []
    seen: set[str] = set()

    for _, row in rankings.iterrows():
        nta_id = str(row.get("nta_id", "")).strip()
        nta_name = str(row.get("nta_name", "")).strip()
        borough = str(row.get("borough", "")).strip()
        if not nta_id or nta_id in seen:
            continue
        label = nta_name or nta_id
        if borough:
            label = f"{label} ({borough})"
        options.append((nta_id, label))
        seen.add(nta_id)

    for _, row in profiles.iterrows():
        nta_id = str(row.get("nta_id", "")).strip()
        nta_name = str(row.get("nta_name", "")).strip()
        borough = str(row.get("borough", "")).strip()
        if not nta_id or nta_id in seen:
            continue
        label = nta_name or nta_id
        if borough:
            label = f"{label} ({borough})"
        options.append((nta_id, label))
        seen.add(nta_id)

    return options


def _render_ranking_panel(rankings: pd.DataFrame, category_label: str) -> None:
    st.markdown(f"**Top neighborhoods for {category_label}**")
    if rankings.empty:
        st.caption(
            "This category is still too sparse to rank confidently. The map can still show places, "
            "but Explore will wait to claim neighborhood leaders until the coverage is stronger."
        )
        return

    ranking_rows = rankings.copy()
    ranking_rows["Rank"] = range(1, len(ranking_rows) + 1)
    ranking_rows["Neighborhood"] = ranking_rows["nta_name"]
    ranking_rows["Borough"] = ranking_rows["borough"]
    ranking_rows["Places"] = pd.to_numeric(ranking_rows["poi_count"], errors="coerce").fillna(0).astype(int)
    ranking_rows["Tier"] = ranking_rows["concentration_tier"].fillna("present").astype(str).str.title()
    ranking_rows["Pct"] = (
        pd.to_numeric(ranking_rows["nyc_percentile"], errors="coerce")
        .fillna(0)
        .mul(100)
        .round(0)
        .astype(int)
        .astype(str)
        + "th pct"
    )
    st.dataframe(
        ranking_rows[["Rank", "Neighborhood", "Borough", "Places", "Tier", "Pct"]],
        use_container_width=True,
        hide_index=True,
    )


def _render_character_panel(profile: dict[str, object] | None, category_label: str) -> None:
    st.markdown("**What this neighborhood is known for**")
    if profile is None:
        st.caption(
            "Choose a neighborhood from the ranking or dropdown to see its current Explore character profile."
        )
        return

    neighborhood_name = str(profile.get("nta_name") or "Selected neighborhood")
    borough = str(profile.get("borough") or "")
    destination_categories = [
        _format_explore_category_name(value)
        for value in profile.get("destination_category_list", [])
    ]
    strong_categories = [
        _format_explore_category_name(value)
        for value in profile.get("strong_category_list", [])
    ]
    top_category = _format_explore_category_name(profile.get("top_category") or "")
    raw_top_subcategory = str(profile.get("top_subcategory") or "").strip()
    if raw_top_subcategory in {"mixed_restaurants", "restaurants", "__unknown__"}:
        top_subcategory = "Broad Neighborhood Mix" if str(profile.get("top_category") or "") == "restaurants" else ""
    else:
        top_subcategory = _format_explore_category_name(raw_top_subcategory)

    st.write(f"**{neighborhood_name}**" + (f" in {borough}" if borough else ""))
    if destination_categories:
        st.caption("Known for: " + ", ".join(destination_categories))
    elif strong_categories:
        st.caption(
            "No full 'known for' claim yet. Current stronger signals: " + ", ".join(strong_categories)
        )
    else:
        st.caption(
            f"{neighborhood_name} does not yet have enough concentrated coverage for a strong "
            f"{category_label.lower()}-led claim."
        )

    if top_category:
        supporting_line = f"Top category: {top_category}"
        if top_subcategory:
            supporting_line += f" | leading subcategory: {top_subcategory}"
        st.write(supporting_line)

    def _safe_int(value: object) -> int:
        numeric = pd.to_numeric(value, errors="coerce")
        return 0 if pd.isna(numeric) else int(numeric)

    total_curated = _safe_int(profile.get("total_curated_poi_count"))
    subway_count = _safe_int(profile.get("subway_station_count"))
    grocery_count = _safe_int(profile.get("grocery_store_count"))
    park_count = _safe_int(profile.get("park_count"))
    st.write(
        f"Curated places: {total_curated} | Subway stations: {subway_count} | "
        f"Grocery stores: {grocery_count} | Parks: {park_count}"
    )


def _render_poi_color_legend(legend: pd.DataFrame) -> None:
    """Render a user-facing POI legend with visible color swatches."""

    rows: list[str] = []
    for _, row in legend.iterrows():
        category = str(row.get("Category", "")).strip()
        subcategory = str(row.get("Sub Category", "")).strip()
        color = str(row.get("Color", "")).strip() or "#666666"
        label = category if not subcategory else f"{category} | {subcategory}"
        rows.append(
            "<div style='display:flex;align-items:center;gap:0.6rem;padding:0.2rem 0;'>"
            f"<span style='display:inline-block;width:0.9rem;height:0.9rem;border-radius:999px;"
            f"background:{color};border:1px solid rgba(0,0,0,0.18);flex:0 0 auto;'></span>"
            f"<span>{label}</span>"
            "</div>"
        )

    st.markdown("".join(rows), unsafe_allow_html=True)


def main() -> None:
    """Render the Stoop Explore application."""

    config = load_config()
    settings = config["settings"]
    data_sources = config["data_sources"]["sources"]
    database_path = str(PROJECT_ROOT / settings["database_path"])
    tract_source = data_sources["census_tracts"]
    tract_path = str(PROJECT_ROOT / tract_source["path"])
    tract_id_col = tract_source.get("id_column", "GEOID")
    center = settings.get("default_map_center", {"lat": 40.7128, "lon": -74.0060})
    explore_categories = load_explore_category_options(database_path)
    category_lookup = _category_option_lookup(explore_categories)
    all_profiles = load_all_nta_character_profiles(database_path)

    available_category_keys = [option.category for option in explore_categories]
    default_category = "restaurants" if "restaurants" in available_category_keys else (
        available_category_keys[0] if available_category_keys else None
    )
    if default_category and st.session_state.get("explore_selected_category") not in available_category_keys:
        st.session_state["explore_selected_category"] = default_category
    metric_labels = metric_options()
    default_metric_label = list(metric_labels.values())[0]
    selected_metric_label = st.session_state.get("explore_context_metric_label", default_metric_label)
    if selected_metric_label not in metric_labels.values():
        selected_metric_label = default_metric_label
        st.session_state["explore_context_metric_label"] = default_metric_label
    metric = next(key for key, label in metric_labels.items() if label == selected_metric_label)

    st.title("Stoop Explore")
    st.markdown(
        "### Explore your favorite NYC neighborhoods through the lens of your favorite activities, whether that's restaurants, museums, or pastries."
    )
    st.markdown(
        "Start with **Curated POIs** to choose the kinds of places you want to explore on the map. "
        "Use **Top neighborhoods for** when you want a quick neighborhood ranking for one activity, "
        "then layer in **Public POIs** for practical context like transit or groceries. "
        "If you want a little more neighborhood background, turn on a **Context metric** last."
    )

    selected_category = st.session_state.get("explore_selected_category", default_category)
    rankings = load_explore_rankings(database_path, selected_category) if selected_category else pd.DataFrame()

    if selected_category != st.session_state.get("explore_last_category"):
        st.session_state["explore_last_category"] = selected_category
        if not rankings.empty:
            st.session_state["explore_selected_nta_id"] = str(rankings.iloc[0]["nta_id"])

    nta_options = _ranked_nta_options(rankings, all_profiles)
    nta_id_values = [value for value, _ in nta_options]
    if nta_id_values and st.session_state.get("explore_selected_nta_id") not in nta_id_values:
        st.session_state["explore_selected_nta_id"] = nta_id_values[0]
    selected_nta_id = st.session_state.get("explore_selected_nta_id")

    with st.sidebar:
        st.header("Explore Intelligence Filter")
        if explore_categories:
            selected_category = st.selectbox(
                "Top neighborhoods for",
                available_category_keys,
                index=available_category_keys.index(selected_category) if selected_category in available_category_keys else 0,
                format_func=lambda value: category_lookup.get(
                    value,
                    ExploreCategoryOption(value, value, False, None, ""),
                ).display_label,
                key="explore_selected_category",
            )
            rankings = load_explore_rankings(database_path, selected_category)
            if selected_category != st.session_state.get("explore_last_category"):
                st.session_state["explore_last_category"] = selected_category
                if not rankings.empty:
                    st.session_state["explore_selected_nta_id"] = str(rankings.iloc[0]["nta_id"])
            nta_options = _ranked_nta_options(rankings, all_profiles)
            nta_id_values = [value for value, _ in nta_options]
            if nta_id_values and st.session_state.get("explore_selected_nta_id") not in nta_id_values:
                st.session_state["explore_selected_nta_id"] = nta_id_values[0]
            selected_nta_id = st.session_state.get("explore_selected_nta_id")

        st.header("Map Geography")
        st.segmented_control(
            "Map geography",
            ["Neighborhoods"],
            default="Neighborhoods",
            disabled=True,
        )

    geography_data = cached_load_base_geography_data(
        database_path=database_path,
        tract_path=tract_path,
        tract_id_col=tract_id_col,
    )
    map_data = build_base_map_data_from_loaded(geography_data, metric=metric)
    poi_data = cached_load_poi_map_data(database_path)
    poi_categories = available_poi_categories(poi_data.points)
    public_poi_categories = list(DEFAULT_PUBLIC_POI_CATEGORIES)

    with st.sidebar:
        st.header("Curated POIs")
        show_pois = st.toggle("Show curated layer", value=not poi_data.points.empty)
        selected_category_label = (
            category_lookup[selected_category].display_label
            if selected_category and selected_category in category_lookup
            else None
        )
        existing_curated_defaults = st.session_state.get("curated_category_selection")
        if not existing_curated_defaults:
            if selected_category_label and selected_category_label in poi_categories:
                existing_curated_defaults = [selected_category_label]
            else:
                existing_curated_defaults = poi_categories
        elif selected_category_label and selected_category_label in poi_categories and selected_category_label not in existing_curated_defaults:
            existing_curated_defaults = [*existing_curated_defaults, selected_category_label]
        selected_poi_categories = st.multiselect(
            "Curated categories",
            poi_categories,
            default=[category for category in existing_curated_defaults if category in poi_categories],
            disabled=not show_pois or poi_data.points.empty,
            key="curated_category_selection",
        )
        focus_category_selection = (
            (selected_category_label,) if selected_category_label else tuple(selected_poi_categories)
        )
        visible_subcategory_candidates = filter_poi_points_by_categories(
            poi_data.points,
            focus_category_selection,
        )
        poi_subcategories = available_poi_subcategories(visible_subcategory_candidates)
        selected_poi_subcategories = st.multiselect(
            "Sub Categories",
            poi_subcategories,
            default=poi_subcategories,
            disabled=not show_pois or not poi_subcategories,
            key="curated_subcategory_selection",
        )
        if poi_data.points.empty:
            st.caption("No curated places with coordinates are available yet.")
        elif show_pois:
            st.caption(f"{len(poi_data.points):,} curated places loaded from {poi_data.source}.")
            if selected_category_label:
                st.caption(
                    f"Map is focused on `{selected_category_label}` places to match the Explore panel."
                )

        st.header("Public POIs")
        show_public_pois = st.toggle(
            "Show public layer",
            value=False,
        )
        selected_public_poi_categories = st.multiselect(
            "Public categories",
            public_poi_categories,
            default=list(DEFAULT_PUBLIC_POI_SELECTION),
            disabled=not show_public_pois,
            format_func=lambda value: value.replace("_", " ").title(),
        )

        st.header("Context Metric")
        show_demographics = st.toggle("Show context colors", value=False)
        selected_label = st.selectbox(
            "Context metric",
            list(metric_labels.values()),
            index=list(metric_labels.values()).index(selected_metric_label),
            disabled=not show_demographics,
            key="explore_context_metric_label",
        )
        metric = next(key for key, label in metric_labels.items() if label == selected_label)

    public_poi_data = (
        cached_load_public_poi_map_data(
            database_path,
            tuple(selected_public_poi_categories),
        )
        if show_public_pois and selected_public_poi_categories
        else PoiMapData(
            points=pd.DataFrame(),
            source="not_loaded",
            stats={"poi_count": 0, "category_count": 0, "configured_category_count": 0},
        )
    )

    with st.sidebar:
        if show_public_pois and not selected_public_poi_categories:
            st.caption("Choose at least one public category to load public POIs.")
        elif show_public_pois and public_poi_data.points.empty:
            st.caption("No public baseline POIs are available for the selected public categories.")
        elif show_public_pois:
            st.caption(
                f"{len(public_poi_data.points):,} public POIs loaded across "
                f"{public_poi_data.stats['category_count']} selected categories."
            )

    effective_poi_categories = (
        (selected_category_label,)
        if show_pois and selected_category_label
        else tuple(selected_poi_categories)
    )

    filtered_poi_points = filter_poi_points_by_categories(
        poi_data.points,
        effective_poi_categories,
        tuple(selected_poi_subcategories),
    )
    filtered_public_poi_points = filter_public_poi_points_by_categories(
        public_poi_data.points,
        tuple(selected_public_poi_categories),
    )
    filtered_poi_points = filter_points_to_supported_geography(filtered_poi_points, map_data.tracts)
    filtered_public_poi_points = filter_points_to_supported_geography(
        filtered_public_poi_points,
        map_data.tracts,
    )

    st.pydeck_chart(
        build_base_map_deck(
            map_data,
            layer_mode="Neighborhoods",
            show_demographics=show_demographics,
            poi_points=filtered_poi_points,
            show_pois=show_pois,
            public_poi_points=filtered_public_poi_points,
            show_public_pois=show_public_pois,
            selected_nta_id=selected_nta_id,
            center_lat=float(center["lat"]),
            center_lon=float(center["lon"]),
            zoom=int(settings.get("default_map_zoom", 10)),
        ),
        use_container_width=True,
    )

    if show_pois and not poi_data.points.empty:
        st.caption(
            f"Showing {len(filtered_poi_points):,} of {len(poi_data.points):,} curated places "
            "for the selected category filters."
        )
        legend = poi_color_legend_rows(filtered_poi_points)
        if not legend.empty:
            with st.expander("POI Color Legend", expanded=False):
                _render_poi_color_legend(legend)
    if show_public_pois and not public_poi_data.points.empty:
        st.caption(
            f"Showing {len(filtered_public_poi_points):,} of "
            f"{len(public_poi_data.points):,} public POIs for the selected category filters."
        )

    intelligence_left, intelligence_right = st.columns([1.1, 1], vertical_alignment="top")
    with intelligence_left:
        st.subheader("Top Neighborhoods")
        if explore_categories and selected_category:
            category_label = category_lookup[selected_category].display_label
            _render_ranking_panel(rankings, category_label)
        else:
            st.caption(
                "Explore intelligence categories are not available yet. Rebuild the "
                "`neighborhood_character_mart` to unlock this panel."
            )
    with intelligence_right:
        st.subheader("Neighborhood Character")
        if explore_categories and selected_category:
            category_label = category_lookup[selected_category].display_label
            if nta_options:
                label_lookup = dict(nta_options)
                selected_nta_id = st.selectbox(
                    "Selected neighborhood",
                    nta_id_values,
                    index=nta_id_values.index(selected_nta_id) if selected_nta_id in nta_id_values else 0,
                    format_func=lambda value: label_lookup.get(value, value),
                    key="explore_selected_nta_id",
                )
            else:
                st.caption(
                    "No ranked neighborhoods are ready for this category yet. You can still browse the map and POIs."
                )
            _render_character_panel(
                load_nta_character_profile(database_path, selected_nta_id) if selected_nta_id else None,
                category_label,
            )
        else:
            st.caption(
                "Choose an Explore category to see what a selected neighborhood is known for."
            )

    if show_demographics:
        st.caption(f"Context colors are currently mapped to {metric_labels[metric]}.")


if __name__ == "__main__":
    main()
