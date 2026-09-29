import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This workbench is read-only. Named SQL files own all warehouse reads so
    # the notebook never creates a Q6 mart or recreates Q2 center selection.
    from pathlib import Path

    import duckdb
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    from shapely import wkb

    return Path, duckdb, mo, pd, px, wkb


@app.cell
def _(Path, duckdb):
    analysis_dir = Path(__file__).resolve().parent
    # The notebook sits four levels below the repository root:
    # metro-deep-dive-program/analyses/explanation/q6_one_metro.
    root = analysis_dir.parents[3]
    db = str(root / "foundations/etl/data/duckdb/patterns_in_place.duckdb")
    sql_dir = analysis_dir / "sql"

    def read_sql(con, name, cbsa_code=None, infrastructure_path=None):
        """Run a named Q6 query after substituting declared query controls."""

        query = (sql_dir / name).read_text()
        if cbsa_code is not None:
            query = query.replace("__CBSA_CODE__", cbsa_code)
        if infrastructure_path is not None:
            query = query.replace("__INFRASTRUCTURE_PATH__", str(infrastructure_path))
        return con.sql(query).df()

    with duckdb.connect(db, read_only=True) as _con:
        markets = read_sql(_con, "q6_market_options.sql")
    return analysis_dir, db, markets, read_sql


@app.cell
def _(markets, mo):
    options = {f"{row.cbsa_name} ({row.cbsa_code})": row.cbsa_code for row in markets.itertuples(index=False)}
    market = mo.ui.dropdown(options, value="Richmond, VA (40060)", label="CBSA")
    mo.vstack([
        mo.md("# Explanation Q6 — One Metro?\nDirect ACS Place measures, allocated workplace jobs, Q2 physical proximity, and relationship evidence remain separate layers."),
        market,
    ])
    return (market,)


@app.cell
def _(analysis_dir, db, duckdb, market, pd, read_sql):
    with duckdb.connect(db, read_only=True) as _con:
        county = read_sql(_con, "q6_county_context.sql", market.value)
        places = read_sql(_con, "q6_place_profile.sql", market.value)
        candidates = read_sql(_con, "q6_candidate_evidence.sql", market.value)
        od_links = read_sql(_con, "q6_od_links.sql", market.value)
        od_coverage = read_sql(_con, "q6_od_coverage.sql")
        poi_context = read_sql(_con, "q6_poi_context.sql", market.value)
        poi_coverage = read_sql(_con, "q6_poi_coverage.sql", market.value)
        place_geometry = read_sql(_con, "q6_place_display.sql", market.value)
        centers = read_sql(_con, "q6_centers.sql", market.value)
        # Infrastructure artifacts belong to the metro-deep-dive-program tree,
        # two levels above this analysis directory.
        artifacts = sorted((analysis_dir.parents[2] / "engines/infrastructure/outputs").glob("**/infrastructure_place_summary.parquet"))
        infrastructure = read_sql(_con, "q6_infrastructure_context.sql", market.value, artifacts[0]) if artifacts else pd.DataFrame()
    return candidates, centers, county, infrastructure, od_coverage, od_links, place_geometry, places, poi_context, poi_coverage


@app.cell
def _(candidates, pd):
    # The two materiality rules are shown together. This is a transparent
    # sensitivity check, not a score or an automatic editorial selection.
    initial = candidates.loc[candidates.candidate_status == "candidate_for_review"]
    high = candidates.loc[(candidates.direct_population >= 10000) & (candidates.metro_population_share >= 0.02) & candidates.associated_q2_component.notna()]
    initial_components = initial.associated_q2_component.nunique()
    high_components = high.associated_q2_component.nunique()
    decision = pd.DataFrame([{
        "candidate_place_count": len(initial),
        "distinct_component_count": initial_components,
        "high_materiality_component_count": high_components,
        "distance_sensitivity_visible": bool(((initial.recommended_distance_miles - initial.strict_distance_miles).abs() > 0.001).any() or ((initial.recommended_distance_miles - initial.no_share_distance_miles).abs() > 0.001).any()),
        "materiality_sensitivity_visible": initial_components != high_components,
        "provisional_anchor_result": "insufficient structure evidence" if initial_components == 0 else ("mixed" if initial_components != high_components else ("one supported anchor" if initial_components == 1 else "multiple supported anchors")),
        "decision_caveat": "Initial rule is 5,000 residents and 1% of CBSA population; 10,000 residents and 2% is shown as sensitivity.",
    }])
    return (decision,)


@app.cell
def _(county, mo, places):
    mo.vstack([
        mo.md("## Coverage and sourced county context\nCounty flags are OMB context, not a Q6 classification. Direct Place ACS values do not sum to a CBSA where Places split boundaries."),
        mo.ui.table(county, page_size=25), mo.ui.table(places, page_size=30),
    ])
    return


@app.cell
def _(mo, places, px):
    chart = px.scatter(places, x="direct_population", y="allocated_workplace_jobs", hover_name="place_name", hover_data=["direct_median_hh_income", "membership_status", "workplace_jobs_provenance"], title="Place role comparison: direct population × allocated workplace jobs")
    mo.ui.plotly(chart)
    return


@app.cell
def _(centers, mo, place_geometry, px, wkb):
    # Display centroids orient the map only; Geography allocation edges define
    # the Place-to-component association in the candidate query.
    place_marks = place_geometry.copy()
    place_marks["geometry"] = place_marks.geom_wkb.map(lambda value: wkb.loads(bytes(value)))
    place_marks["longitude"] = place_marks.geometry.map(lambda shape: shape.centroid.x)
    place_marks["latitude"] = place_marks.geometry.map(lambda shape: shape.centroid.y)
    center_marks = centers.copy()
    center_marks["geometry"] = center_marks.geom_wkb.map(lambda value: wkb.loads(bytes(value)))
    center_marks["longitude"] = center_marks.geometry.map(lambda shape: shape.centroid.x)
    center_marks["latitude"] = center_marks.geometry.map(lambda shape: shape.centroid.y)
    figure = px.scatter_map(place_marks, lat="latitude", lon="longitude", size="direct_population", hover_name="place_name", title="Orientation map: Place display centroids and reviewed Q2 center tracts")
    figure.add_traces(px.scatter_map(center_marks, lat="latitude", lon="longitude", color="component_id", hover_name="tract_geoid").data)
    mo.vstack([mo.md("## Spatial anchor context\nDisplay geometry is never used to calculate Place-component membership."), mo.ui.plotly(figure)])
    return


@app.cell
def _(candidates, decision, mo):
    mo.vstack([
        mo.md("## Anchor decision\nQ2 miles are physical proximity, never travel time or access. The table retains all covered Places before the declared materiality review."),
        mo.ui.table(candidates, page_size=30), mo.ui.table(decision, page_size=10),
    ])
    return


@app.cell
def _(infrastructure, mo, od_coverage, od_links, poi_context, poi_coverage):
    mo.vstack([
        mo.md("## Relationship evidence\nOD is directional home-Place → work-Place evidence, not an anchor score. Ranked links precede any possible flow map; endpoint status and coverage remain visible."),
        mo.md("### Ranked Place work links — 2023 LODES JT00"), mo.ui.table(od_links, page_size=30), mo.ui.table(od_coverage, page_size=30),
        mo.md("### Direct POI-to-Place activity context"), mo.ui.table(poi_context, page_size=30), mo.ui.table(poi_coverage, page_size=10),
        mo.md("### Infrastructure-to-Place physical context\nLine length and surface area remain distinct measures."), mo.ui.table(infrastructure, page_size=30),
    ])
    return


if __name__ == "__main__":
    app.run()
