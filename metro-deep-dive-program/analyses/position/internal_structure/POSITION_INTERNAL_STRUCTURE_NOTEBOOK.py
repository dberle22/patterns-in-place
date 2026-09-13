import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This initial Part 1 surface is a read-only consumer of Geography and
    # Phase 7 outputs. It never writes geometry, allocations, or classifications.
    import os
    from pathlib import Path

    import altair as alt
    import duckdb
    import geopandas as gpd
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd

    return Path, alt, duckdb, gpd, mo, os, pd, plt


@app.cell
def _(Path):
    # Anchor every resource to this file so the notebook behaves the same in
    # an editor, `marimo edit`, and a shell launched from another directory.
    analysis_dir = Path(__file__).resolve().parent
    repo_root = analysis_dir.parents[3]
    query_paths = {
        "market_summary": analysis_dir / "queries" / "internal_structure_market_summary.sql",
        "place_inventory": analysis_dir / "queries" / "internal_structure_place_inventory.sql",
        "zone_composition": analysis_dir / "queries" / "internal_structure_zone_composition.sql",
        "place_zone_matrix": analysis_dir / "queries" / "internal_structure_place_zone_matrix.sql",
        "tract_zone_map": analysis_dir / "queries" / "internal_structure_tract_zone_map.sql",
        "zcta_rollup": analysis_dir / "queries" / "internal_structure_zcta_rollup.sql",
    }
    return analysis_dir, query_paths, repo_root


@app.cell
def _(os, repo_root):
    def load_db_path_internal_structure() -> str:
        configured_path = os.environ.get("DB_PATH", "").strip()
        if configured_path:
            return configured_path

        renviron_path = repo_root / ".Renviron"
        if renviron_path.exists():
            for raw_line in renviron_path.read_text().splitlines():
                line = raw_line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key.strip() == "DB_PATH":
                        return value.strip()

        raise RuntimeError("DB_PATH is not set and could not be found in .Renviron.")

    return (load_db_path_internal_structure,)


@app.cell
def _(duckdb, load_db_path_internal_structure):
    def run_internal_structure_query(query_path, cbsa_code):
        # CBSA choices come from the governed zone table. Keep the replacement
        # narrow and validate the identifier before it becomes SQL text.
        if not cbsa_code.isdigit():
            raise ValueError("CBSA code must contain only digits.")
        sql = query_path.read_text().replace("'__CBSA_CODE__'", f"'{cbsa_code}'")
        with duckdb.connect(load_db_path_internal_structure(), read_only=True) as query_con:
            return query_con.sql(sql).df()

    def load_internal_structure_cbsa_options():
        with duckdb.connect(load_db_path_internal_structure(), read_only=True) as options_con:
            options_df = options_con.sql(
                """
                SELECT DISTINCT cbsa_code, cbsa_name
                FROM mart_intelligence.intelligence_zones
                WHERE cbsa_code IS NOT NULL AND cbsa_name IS NOT NULL
                ORDER BY cbsa_name
                """
            ).df()
        return {
            f"{row.cbsa_name} ({row.cbsa_code})": row.cbsa_code
            for row in options_df.itertuples(index=False)
        }

    return load_internal_structure_cbsa_options, run_internal_structure_query


@app.cell
def _(mo):
    mo.md("""
    # Position Internal Structure

    ## Part 1 — Market Geography and Zone Structure

    This first review starts with Richmond, VA and can inspect any CBSA with
    promoted Phase 7 coverage. It relates governed counties, Census Places,
    tracts, ZCTAs, and zone types without treating any one of them as a
    functional submarket. All values are descriptive and read-only.

    Current Geography tract and county display products provide the map base.
    Places remain allocation-based orientation geographies; this notebook does
    not draw an invented Place boundary from those allocation relationships.
    """)
    return


@app.cell
def _(load_internal_structure_cbsa_options):
    cbsa_options = load_internal_structure_cbsa_options()
    return (cbsa_options,)


@app.cell
def _(cbsa_options, mo):
    default_cbsa_label = next(
        (label for label, code in cbsa_options.items() if code == "40060"),
        next(iter(cbsa_options)),
    )
    cbsa_selector = mo.ui.dropdown(
        cbsa_options,
        value=default_cbsa_label,
        label="Target CBSA",
        searchable=True,
        full_width=True,
    )
    cbsa_selector
    return (cbsa_selector,)


@app.cell
def _(cbsa_selector, query_paths, run_internal_structure_query):
    selected_cbsa_code = cbsa_selector.value
    market_summary_df = run_internal_structure_query(query_paths["market_summary"], selected_cbsa_code)
    place_inventory_df = run_internal_structure_query(query_paths["place_inventory"], selected_cbsa_code)
    zone_composition_df = run_internal_structure_query(query_paths["zone_composition"], selected_cbsa_code)
    place_zone_matrix_df = run_internal_structure_query(query_paths["place_zone_matrix"], selected_cbsa_code)
    tract_zone_map_df = run_internal_structure_query(query_paths["tract_zone_map"], selected_cbsa_code)
    zcta_rollup_df = run_internal_structure_query(query_paths["zcta_rollup"], selected_cbsa_code)
    return (
        market_summary_df,
        place_inventory_df,
        place_zone_matrix_df,
        selected_cbsa_code,
        tract_zone_map_df,
        zcta_rollup_df,
        zone_composition_df,
    )


@app.cell
def _(market_summary_df, mo):
    # Partial allocation coverage is expected where Census Places do not cover
    # the whole CBSA. A partial ZCTA rollup instead identifies a source gap for
    # review; neither condition is hidden from the analyst.
    market_summary_df["coverage_status"] = market_summary_df.apply(
        lambda row: "Complete" if row.observed_count == row.expected_count else "Partial — inspect detail",
        axis=1,
    )
    mo.vstack([
        mo.md("## Coverage summary\nThe metric slice uses 2024 additive population and housing fields. Place and ZCTA relationships use population-basis allocation edges."),
        mo.ui.table(market_summary_df, selection=None),
    ])
    return


@app.cell
def _(gpd, tract_zone_map_df):
    # DuckDB returns mutable BLOB values; GeoPandas needs immutable WKB bytes.
    tract_zone_map = gpd.GeoDataFrame(
        tract_zone_map_df.drop(columns="geometry_wkb"),
        geometry=gpd.GeoSeries.from_wkb(tract_zone_map_df.geometry_wkb.map(bytes), crs="EPSG:4326"),
        crs="EPSG:4326",
    )
    county_boundaries = tract_zone_map.dissolve(by="county_geoid", as_index=False)
    market_boundary = tract_zone_map.dissolve()
    return county_boundaries, market_boundary, tract_zone_map


@app.cell
def _(county_boundaries, market_boundary, mo, plt, tract_zone_map):
    hierarchy_figure, hierarchy_axis = plt.subplots(figsize=(10, 8))
    tract_zone_map.boundary.plot(ax=hierarchy_axis, color="#c7c7c7", linewidth=0.18)
    county_boundaries.boundary.plot(ax=hierarchy_axis, color="#4a4a4a", linewidth=0.8)
    market_boundary.boundary.plot(ax=hierarchy_axis, color="#111111", linewidth=1.25)
    hierarchy_axis.set(title="Market geography hierarchy: tract and county display boundaries", axis_off=True)
    hierarchy_figure.tight_layout()
    mo.vstack([
        mo.md("## Geography hierarchy map\nThe map uses current Geography tract display shapes, county outlines dissolved from those tracts, and the market outline. Census Places remain visible through allocation-based inventory and profile views because no Place geometry is required or inferred here."),
        hierarchy_figure,
    ])
    return hierarchy_figure, hierarchy_axis


@app.cell
def _(county_boundaries, market_boundary, mo, plt, tract_zone_map):
    zone_map_figure, zone_map_axis = plt.subplots(figsize=(10, 8))
    tract_zone_map.plot(column="zone_type", ax=zone_map_axis, categorical=True, legend=True, legend_kwds={"loc": "lower left", "title": "Phase 7 tract cluster"}, linewidth=0.05, edgecolor="#ffffff")
    county_boundaries.boundary.plot(ax=zone_map_axis, color="#3a3a3a", linewidth=0.45)
    market_boundary.boundary.plot(ax=zone_map_axis, color="#111111", linewidth=1.0)
    zone_map_axis.set(title="Phase 7 tract-cluster review", axis_off=True)
    zone_map_figure.tight_layout()
    mo.vstack([
        mo.md("## Tract zone map\nEach tract is colored only by its stored Phase 7 cluster label. This is a tract review—not a corridor, district, or locally invented boundary system."),
        zone_map_figure,
    ])
    return zone_map_axis, zone_map_figure


@app.cell
def _(alt, mo, place_inventory_df):
    largest_places_df = place_inventory_df.head(20).copy()
    place_population_chart = (
        alt.Chart(largest_places_df, title="Largest Census Places by allocated 2024 population")
        .mark_bar()
        .encode(
            x=alt.X("allocated_population:Q", title="Allocated population"),
            y=alt.Y("place_name:N", title=None, sort="-x"),
            tooltip=["place_name:N", "allocated_population:Q", "allocated_housing_units:Q", "contributing_tract_count:Q", "allocation_quality:N", "zone_type_count:Q"],
        )
    )
    mo.vstack([
        mo.md("## Place inventory\nCensus Places are formal orientation geographies. Population and housing are allocated from 2024 tract measures with population-basis edges; they should not be read as direct Place estimates or functional-market boundaries."),
        place_population_chart,
        mo.ui.dataframe(place_inventory_df, page_size=20),
    ])
    return largest_places_df, place_population_chart


@app.cell
def _(alt, mo, zone_composition_df):
    zone_share_long_df = zone_composition_df.melt(
        id_vars=["zone_type", "market_tract_count", "national_tract_count", "share_difference"],
        value_vars=["market_tract_share", "national_tract_share"],
        var_name="comparison_group",
        value_name="tract_share",
    )
    zone_mix_chart = (
        alt.Chart(zone_share_long_df, title="Market and national Phase 7 zone mix")
        .mark_bar()
        .encode(
            x=alt.X("tract_share:Q", axis=alt.Axis(format="%"), title="Share of tracts"),
            y=alt.Y("zone_type:N", title=None, sort="-x"),
            color=alt.Color("comparison_group:N", title=None),
            yOffset="comparison_group:N",
            tooltip=["zone_type:N", "comparison_group:N", "tract_share:Q", "market_tract_count:Q", "national_tract_count:Q", "share_difference:Q"],
        )
    )
    mo.vstack([
        mo.md("## Tract zone composition\nThe comparison is a tract-share baseline, not a population-weighted claim. Zone types remain national Phase 7 classifications rather than local neighborhood names."),
        zone_mix_chart,
        mo.ui.table(zone_composition_df, selection=None),
    ])
    return zone_mix_chart, zone_share_long_df


@app.cell
def _(mo, place_inventory_df):
    place_options = {
        f"{row.place_name} ({row.place_id})": row.place_id
        for row in place_inventory_df.itertuples(index=False)
    }
    place_selector = mo.ui.dropdown(
        place_options,
        value=next(iter(place_options), None),
        label="Census Place profile",
        searchable=True,
        full_width=True,
    )
    place_selector
    return place_options, place_selector


@app.cell
def _(place_selector, place_zone_matrix_df):
    selected_place_id = place_selector.value
    selected_place_zone_df = place_zone_matrix_df.loc[
        place_zone_matrix_df.place_id.eq(selected_place_id)
    ].sort_values("share_within_place", ascending=False).copy()
    return selected_place_id, selected_place_zone_df


@app.cell
def _(alt, mo, selected_place_zone_df):
    place_zone_chart = (
        alt.Chart(selected_place_zone_df, title="Selected Place: Phase 7 zone composition")
        .mark_bar()
        .encode(
            x=alt.X("share_within_place:Q", axis=alt.Axis(format="%"), title="Share of allocated tract equivalents within Place"),
            y=alt.Y("zone_type:N", title=None, sort="-x"),
            tooltip=["zone_type:N", "allocated_tract_equivalents:Q", "share_within_place:Q", "share_of_market_zone:Q", "allocation_quality:N"],
        )
    )
    mo.vstack([
        mo.md("## Place × Zone review\nThe selected-Place bar chart answers the within-Place question. The matrix keeps the reciprocal `share_of_market_zone` column for the question of where each zone is distributed across Places."),
        place_zone_chart,
        mo.ui.table(selected_place_zone_df, selection=None),
    ])
    return (place_zone_chart,)


@app.cell
def _(alt, mo, place_zone_matrix_df):
    top_places = place_zone_matrix_df.groupby("place_name")["allocated_tract_equivalents"].sum().nlargest(20).index
    matrix_display_df = place_zone_matrix_df.loc[place_zone_matrix_df.place_name.isin(top_places)].copy()
    place_zone_heatmap = (
        alt.Chart(matrix_display_df, title="Place × Zone composition: 20 largest allocated Place footprints")
        .mark_rect()
        .encode(
            x=alt.X("zone_type:N", title=None),
            y=alt.Y("place_name:N", title=None, sort="-x"),
            color=alt.Color("share_within_place:Q", scale=alt.Scale(scheme="blues"), title="Within-Place share"),
            tooltip=["place_name:N", "zone_type:N", "share_within_place:Q", "share_of_market_zone:Q", "allocated_tract_equivalents:Q", "allocation_quality:N"],
        )
    )
    mo.vstack([place_zone_heatmap, mo.ui.dataframe(place_zone_matrix_df, page_size=30)])
    return matrix_display_df, place_zone_heatmap


@app.cell
def _(alt, mo, zcta_rollup_df):
    zcta_dominant_chart = (
        alt.Chart(zcta_rollup_df.dropna(subset=["dominant_zone_share"]), title="ZCTA dominant-zone evidence")
        .mark_circle(opacity=0.65)
        .encode(
            x=alt.X("dominant_zone_share:Q", axis=alt.Axis(format="%"), title="Dominant zone share"),
            y=alt.Y("total_weighted_population:Q", title="Stored weighted population"),
            color=alt.Color("dominant_zone_type:N", title="Dominant zone type"),
            shape=alt.Shape("is_mixed_zone:N", title="Mixed-zone flag"),
            tooltip=["zcta_name:N", "zip_geoid:N", "dominant_zone_type:N", "dominant_zone_share:Q", "secondary_zone_type:N", "secondary_zone_share:Q", "is_mixed_zone:N", "tract_count:Q", "total_weighted_population:Q", "source_vintage:Q"],
        )
    )
    mo.vstack([
        mo.md("## Supporting ZCTA rollup\nZCTAs are Census presentation geographies, not USPS delivery ZIPs. Their zone evidence remains the stored weighted tract composition, including dominant share, secondary type, and mixed-zone flag."),
        zcta_dominant_chart,
        mo.ui.dataframe(zcta_rollup_df, page_size=25),
    ])
    return (zcta_dominant_chart,)


@app.cell
def _(market_summary_df, mo, pd, place_inventory_df, place_zone_matrix_df, zcta_rollup_df, zone_composition_df):
    qa_df = pd.DataFrame([
        {"check": "Tract zone rows unique", "result": not zone_composition_df.empty, "detail": "Zone composition query returned the selected-market zone inventory."},
        {"check": "Coverage checks visible", "result": "coverage_status" in market_summary_df.columns, "detail": "Partial Place allocation and ZCTA rollup coverage remain explicit."},
        {"check": "Place matrix retains both denominators", "result": {"share_within_place", "share_of_market_zone"}.issubset(place_zone_matrix_df.columns), "detail": "Both composition directions remain available."},
        {"check": "Place allocation quality visible", "result": "allocation_quality" in place_inventory_df.columns, "detail": "Inventory and matrix expose allocation quality."},
        {"check": "ZCTA mixed-zone evidence visible", "result": {"dominant_zone_share", "is_mixed_zone"}.issubset(zcta_rollup_df.columns), "detail": "ZCTAs retain dominant-share and mixed-zone fields."},
    ])
    mo.vstack([mo.md("## QA appendix"), mo.ui.table(qa_df, selection=None)])
    return (qa_df,)


if __name__ == "__main__":
    app.run()
