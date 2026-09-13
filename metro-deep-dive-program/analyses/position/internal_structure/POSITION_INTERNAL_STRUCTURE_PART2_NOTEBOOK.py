import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # Part 2 reads declared engine outputs only. It neither writes a mart nor
    # rebuilds POI taxonomy, Phase 7 zones, Infrastructure, or job-center logic.
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
    analysis_dir = Path(__file__).resolve().parent
    repo_root = analysis_dir.parents[3]
    query_paths = {
        "category_inventory": analysis_dir / "queries" / "internal_structure_poi_category_inventory.sql",
        "coverage": analysis_dir / "queries" / "internal_structure_poi_coverage.sql",
        "d3_job_centers": analysis_dir / "queries" / "internal_structure_d3_job_centers.sql",
        "points": analysis_dir / "queries" / "internal_structure_poi_points.sql",
        "tract_map": analysis_dir / "queries" / "internal_structure_tract_zone_map.sql",
        "zone": analysis_dir / "queries" / "internal_structure_poi_zone.sql",
        "cross_market": analysis_dir / "queries" / "internal_structure_cross_market_summary.sql",
    }
    return analysis_dir, query_paths, repo_root


@app.cell
def _(os, repo_root):
    def load_part2_db_path() -> str:
        configured_path = os.environ.get("DB_PATH", "").strip()
        if configured_path:
            return configured_path
        for raw_line in (repo_root / ".Renviron").read_text().splitlines():
            line = raw_line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if key.strip() == "DB_PATH":
                    return value.strip()
        raise RuntimeError("DB_PATH is not set and could not be found in .Renviron.")

    return (load_part2_db_path,)


@app.cell
def _(duckdb, load_part2_db_path):
    def run_part2_query(query_path, cbsa_code):
        if not cbsa_code.isdigit():
            raise ValueError("CBSA code must contain only digits.")
        sql = query_path.read_text().replace("'__CBSA_CODE__'", f"'{cbsa_code}'")
        with duckdb.connect(load_part2_db_path(), read_only=True) as con:
            return con.sql(sql).df()

    def load_part2_cbsa_options():
        with duckdb.connect(load_part2_db_path(), read_only=True) as con:
            rows = con.sql("SELECT DISTINCT cbsa_code, cbsa_name FROM mart_intelligence.intelligence_zones ORDER BY cbsa_name").df()
        return {f"{row.cbsa_name} ({row.cbsa_code})": row.cbsa_code for row in rows.itertuples(index=False)}

    return load_part2_cbsa_options, run_part2_query


@app.cell
def _(mo):
    mo.md("""
    # Position Internal Structure — Part 2

    ## Activity, Infrastructure, and Structural Patterns

    This is a read-only exploratory surface for governed POI, D3-derived tract
    workplace context, Infrastructure, and stored tract clusters. It does not
    establish access, commuting integration, causation, barriers, or investment
    opportunity.
    """)
    return


@app.cell
def _(load_part2_cbsa_options, mo):
    part2_cbsa_options = load_part2_cbsa_options()
    default_label = next((label for label, code in part2_cbsa_options.items() if code == "40060"), next(iter(part2_cbsa_options)))
    part2_cbsa_selector = mo.ui.dropdown(part2_cbsa_options, value=default_label, label="Target CBSA", searchable=True, full_width=True)
    part2_cbsa_selector
    return part2_cbsa_options, part2_cbsa_selector


@app.cell
def _(part2_cbsa_selector, query_paths, run_part2_query):
    selected_part2_cbsa_code = part2_cbsa_selector.value
    poi_category_inventory_df = run_part2_query(query_paths["category_inventory"], selected_part2_cbsa_code)
    poi_coverage_df = run_part2_query(query_paths["coverage"], selected_part2_cbsa_code)
    d3_job_centers_df = run_part2_query(query_paths["d3_job_centers"], selected_part2_cbsa_code)
    poi_points_df = run_part2_query(query_paths["points"], selected_part2_cbsa_code)
    poi_zone_df = run_part2_query(query_paths["zone"], selected_part2_cbsa_code)
    tract_zone_map_df = run_part2_query(query_paths["tract_map"], selected_part2_cbsa_code)
    cross_market_summary_df = run_part2_query(query_paths["cross_market"], selected_part2_cbsa_code)
    return cross_market_summary_df, d3_job_centers_df, poi_category_inventory_df, poi_coverage_df, poi_points_df, poi_zone_df, selected_part2_cbsa_code, tract_zone_map_df


@app.cell
def _(duckdb, repo_root, selected_part2_cbsa_code):
    # The Infrastructure Engine publishes a versioned artifact rather than a
    # warehouse table. Discover the latest validated artifact for this market.
    artifacts = sorted((repo_root / "metro-deep-dive-program" / "engines" / "infrastructure" / "outputs").glob(f"**/*-{selected_part2_cbsa_code}-*/validated/osm_core_v1/infrastructure_feature.parquet"))
    infrastructure_artifact = artifacts[-1] if artifacts else None
    if infrastructure_artifact is None:
        infrastructure_features_df = None
    else:
        escaped_path = str(infrastructure_artifact).replace("'", "''")
        with duckdb.connect() as con:
            infrastructure_features_df = con.sql(f"SELECT source_record_key, source_name, feature_group, feature_type, analytical_crs, geometry_status, market_id, market_boundary_vintage, source_run_id, geometry FROM read_parquet('{escaped_path}') WHERE record_status = 'retained' AND mapping_status IN ('mapped', 'overridden')").df()
    return infrastructure_artifact, infrastructure_features_df


@app.cell
def _(mo, poi_category_inventory_df, poi_coverage_df):
    category_totals_df = poi_category_inventory_df.loc[poi_category_inventory_df.mapping_status.isin(["mapped", "overridden"])].groupby("category", dropna=False).place_count.sum().sort_values(ascending=False).reset_index()
    poi_category_options = {f"{row.category} ({int(row.place_count):,})": row.category for row in category_totals_df.itertuples(index=False) if row.category is not None}
    poi_category_selector = mo.ui.multiselect(poi_category_options, value=list(poi_category_options.values())[:5], label="Governed POI categories", full_width=True)
    mo.vstack([mo.md("## POI coverage\nRetained, mapping, and tract-assignment states remain visible before area comparison."), mo.ui.table(poi_coverage_df, selection=None), poi_category_selector, mo.ui.dataframe(poi_category_inventory_df, page_size=25)])
    return poi_category_selector, poi_category_options


@app.cell
def _(poi_category_selector, poi_zone_df):
    selected_poi_zone_df = poi_zone_df.loc[poi_zone_df.category.isin(poi_category_selector.value)].copy()
    selected_poi_zone_df["category_zone_share"] = selected_poi_zone_df.place_count / selected_poi_zone_df.groupby("category").place_count.transform("sum")
    return (selected_poi_zone_df,)


@app.cell
def _(alt, mo, selected_poi_zone_df):
    poi_zone_chart = alt.Chart(selected_poi_zone_df, title="Selected governed POI categories by Phase 7 tract zone").mark_bar().encode(x=alt.X("place_count:Q", title="Assigned retained POI records"), y=alt.Y("zone_type:N", title=None, sort="-x"), color=alt.Color("category:N", title="Governed category"), tooltip=["category:N", "sub_category:N", "zone_type:N", "place_count:Q", "category_zone_share:Q", "zone_population:Q", "places_per_10000_residents:Q"])
    mo.vstack([mo.md("## POI by zone\nRaw counts, category shares, and population-normalized counts are distinct. The per-10,000-resident value is descriptive, not an access score."), poi_zone_chart, mo.ui.dataframe(selected_poi_zone_df, page_size=30)])
    return (poi_zone_chart,)


@app.cell
def _(d3_job_centers_df, mo):
    mo.vstack([mo.md("## D3-derived tract workplace context\nThe existing D3 minimum of 2,500 workplace jobs is applied to latest LODES tract workplace rows. It is descriptive concentration evidence, not a commuting-flow or job-proximity result."), mo.ui.dataframe(d3_job_centers_df, page_size=15), mo.md("## POI by Census Place\nUnavailable until Geography publishes a direct point-to-Place assignment. Point counts are not allocated using tract weights.")])
    return


@app.cell
def _(infrastructure_artifact, infrastructure_features_df, mo):
    if infrastructure_features_df is None:
        infrastructure_group_selector = mo.ui.multiselect({}, value=[], label="Infrastructure groups")
        infrastructure_view = mo.md("## Infrastructure skeleton\nNo validated consumer artifact is available for this market.")
    else:
        counts = infrastructure_features_df.feature_group.value_counts().sort_index()
        infrastructure_group_options = {f"{group} ({int(count):,})": group for group, count in counts.items()}
        infrastructure_group_selector = mo.ui.multiselect(infrastructure_group_options, value=list(infrastructure_group_options.values()), label="Infrastructure groups", full_width=True)
        infrastructure_view = mo.vstack([mo.md(f"## Infrastructure skeleton\nValidated artifact: `{infrastructure_artifact.name}`. It retains source-run and geometry-status provenance; display is orientation only."), infrastructure_group_selector, mo.ui.table(infrastructure_features_df.groupby(["feature_group", "feature_type"]).size().reset_index(name="feature_count"), selection=None)])
    infrastructure_view
    return (infrastructure_group_selector,)


@app.cell
def _(gpd, infrastructure_features_df, infrastructure_group_selector, tract_zone_map_df):
    tract_zone_map = gpd.GeoDataFrame(tract_zone_map_df.drop(columns="geometry_wkb"), geometry=gpd.GeoSeries.from_wkb(tract_zone_map_df.geometry_wkb.map(bytes), crs="EPSG:4326"), crs="EPSG:4326")
    county_boundaries = tract_zone_map.dissolve(by="county_geoid", as_index=False)
    if infrastructure_features_df is None:
        selected_infrastructure_map = None
    else:
        rows = infrastructure_features_df.loc[infrastructure_features_df.feature_group.isin(infrastructure_group_selector.value)].copy()
        selected_infrastructure_map = gpd.GeoDataFrame(rows.drop(columns="geometry"), geometry=gpd.GeoSeries.from_wkb(rows.geometry.map(bytes), crs="EPSG:26918"), crs="EPSG:26918").to_crs("EPSG:4326")
    return county_boundaries, selected_infrastructure_map, tract_zone_map


@app.cell
def _(county_boundaries, mo, plt, poi_category_selector, poi_points_df, selected_infrastructure_map, tract_zone_map):
    integrated_figure, integrated_axis = plt.subplots(figsize=(11, 9))
    tract_zone_map.plot(column="zone_type", ax=integrated_axis, categorical=True, alpha=0.28, linewidth=0.03, edgecolor="#ffffff")
    if selected_infrastructure_map is not None and not selected_infrastructure_map.empty:
        selected_infrastructure_map.plot(ax=integrated_axis, column="feature_group", categorical=True, legend=True, linewidth=0.4, alpha=0.55)
    visible_points = poi_points_df.loc[poi_points_df.category.isin(poi_category_selector.value)]
    integrated_axis.scatter(visible_points.longitude, visible_points.latitude, s=2, color="#222222", alpha=0.22)
    county_boundaries.boundary.plot(ax=integrated_axis, color="#222222", linewidth=0.5)
    integrated_axis.set(title="Integrated structural orientation map", axis_off=True)
    integrated_figure.tight_layout()
    mo.vstack([mo.md("## Integrated market map\nStored tract clusters, selected Infrastructure groups, and selected POI source points are shown together for orientation. Overlap does not establish access, causation, or an activity-center classification."), integrated_figure])
    return integrated_axis, integrated_figure


@app.cell
def _(mo, part2_cbsa_options):
    review_market_options = {label: code for label, code in part2_cbsa_options.items() if code in {"40060", "27260"}}
    review_market_selector = mo.ui.multiselect(review_market_options, value=[code for code in ["40060", "27260"] if code in review_market_options.values()], label="Part 2 market review set", full_width=True)
    review_market_selector
    return (review_market_selector,)


@app.cell
def _(alt, cross_market_summary_df, mo, review_market_selector):
    reviewed_df = cross_market_summary_df.loc[cross_market_summary_df.cbsa_code.isin(review_market_selector.value)].copy()
    portability_chart = alt.Chart(reviewed_df, title="Part 2 input coverage across reviewed markets").mark_bar().encode(x=alt.X("cbsa_code:N", title="CBSA"), y=alt.Y("retained_poi_count:Q", title="Retained POI records"), color=alt.Color("mapped_poi_share:Q", scale=alt.Scale(domain=[0, 1]), title="Mapped share"), tooltip=["cbsa_code:N", "tract_count:Q", "zone_type_count:Q", "retained_poi_count:Q", "mapped_poi_count:Q", "mapped_poi_share:Q"])
    mo.vstack([mo.md("## Cross-market review and routing\nRichmond and Jacksonville are the first portability checks. This is input coverage and scale, not a market ranking. Route access to Q4, job proximity to Q2, polycentricity to Q6, and regional integration to Regional Role."), portability_chart, mo.ui.table(reviewed_df, selection=None)])
    return portability_chart, reviewed_df


@app.cell
def _(d3_job_centers_df, infrastructure_features_df, mo, pd, poi_coverage_df):
    part2_qa_df = pd.DataFrame([
        {"check": "POI assignment coverage visible", "result": not poi_coverage_df.empty, "detail": "Retained, mapping, and tract-assignment states are displayed."},
        {"check": "D3-derived workplace context visible", "result": not d3_job_centers_df.empty, "detail": "The existing D3 jobs threshold is applied to latest LODES workplace rows."},
        {"check": "Infrastructure handoff available", "result": infrastructure_features_df is not None, "detail": "A missing artifact is explicit; the notebook does not fall back to an unvalidated source."},
    ])
    mo.vstack([mo.md("## Part 2 QA appendix"), mo.ui.table(part2_qa_df, selection=None)])
    return (part2_qa_df,)


if __name__ == "__main__":
    app.run()
