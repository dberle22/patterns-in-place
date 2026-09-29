import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This notebook only reads Q3's analysis-owned mart. Geography supplies
    # relationships and display geometry; it does not own ACS growth results.
    from pathlib import Path
    import duckdb
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    from shapely import wkb
    from shapely.geometry import mapping
    return Path, duckdb, mapping, mo, pd, px, wkb


@app.cell
def _(Path):
    root = Path(__file__).resolve().parents[4]
    query_dir = Path(__file__).resolve().parent / "queries"
    return query_dir, root


@app.cell
def _(duckdb, query_dir, root):
    # The selector reads a tested query surface rather than reconstructing
    # geographic labels from an unrelated housing fact table.
    with duckdb.connect(str(root / "foundations/etl/data/duckdb/patterns_in_place.duckdb"), read_only=True) as options_con:
        options = options_con.execute((query_dir / "cbsa_options.sql").read_text()).fetchdf()
    return (options,)


@app.cell
def _(mo, options):
    market_options = {f"{row.cbsa_name} ({row.cbsa_code})": row.cbsa_code for row in options.itertuples(index=False)}
    market = mo.ui.dropdown(market_options, value="Richmond, VA (40060)", label="CBSA")
    horizon = mo.ui.dropdown({"10 years (interpretive core)": 10, "5 years (interpretive core)": 5, "3 years (watchlist)": 3, "1 year (watchlist)": 1}, value="10 years (interpretive core)", label="Horizon")
    mo.vstack([mo.md("# Explanation Q3 — Where Growth Lands\nThe primary result is observed population and housing-unit change—not an infill/greenfield classification."), mo.hstack([market, horizon], justify="start")])
    return horizon, market


@app.cell
def _(duckdb, horizon, market, query_dir, root):
    query_requests = [
        ("metro_growth_ledger.sql", [market.value]),
        ("tract_growth_status.sql", [market.value, horizon.value]),
        ("growth_concentration.sql", [market.value, horizon.value]),
        ("county_growth_horizons.sql", [market.value, horizon.value]),
        ("place_growth_horizons.sql", [market.value, horizon.value]),
        ("tract_harmonization_qa.sql", []),
        ("national_growth_coverage.sql", []),
    ]
    with duckdb.connect(str(root / "foundations/etl/data/duckdb/patterns_in_place.duckdb"), read_only=True) as query_con:
        frames = [
            query_con.execute((query_dir / filename).read_text(), parameters).fetchdf()
            for filename, parameters in query_requests
        ]
    # This mirrors query_requests, keeping each output connected to a specific,
    # independently testable SQL surface.
    ledger, tracts, concentration, counties, places, qa, coverage = frames
    return concentration, counties, coverage, ledger, places, qa, tracts


@app.cell
def _(ledger, mo):
    mo.vstack([mo.md("## Method and coverage\nFive- and ten-year comparisons are interpretive core evidence. One- and three-year ACS 5-year-release differences are descriptive watchlist signals, not independent annual growth estimates."), mo.ui.table(ledger, page_size=10)])
    return


@app.cell
def _(ledger, mo, px):
    chart = px.bar(ledger, x="horizon_years", y=["usable_population_change", "usable_housing_units_change"], barmode="group", labels={"value":"Change", "horizon_years":"Horizon (years)"}, title="Metro change at a glance — usable harmonized tract totals")
    mo.ui.plotly(chart)
    return


@app.cell
def _(mapping, mo, px, tracts, wkb):
    def tract_map(column, title):
        frame = tracts.loc[tracts.comparison_status.str.startswith("usable")].dropna(subset=[column]).copy()
        frame["geometry"] = frame.geom_wkb.map(lambda value: wkb.loads(bytes(value)))
        geojson = {"type":"FeatureCollection", "features":[{"type":"Feature", "properties":{"tract_geoid":r.tract_geoid}, "geometry":mapping(r.geometry)} for r in frame.itertuples()]}
        figure = px.choropleth(frame, geojson=geojson, locations="tract_geoid", featureidkey="properties.tract_geoid", color=column, color_continuous_scale="RdBu", color_continuous_midpoint=0, hover_data=["population_change", "housing_units_change", "low_confidence_flag"], title=title)
        figure.update_geos(fitbounds="locations", visible=False)
        return figure
    mo.vstack([mo.md("## Where the change lands\nMaps show absolute contribution. Flagged tracts remain available in the table but are not interpreted as core evidence."), mo.ui.plotly(tract_map("population_change", "Population change by 2020 tract")), mo.ui.plotly(tract_map("housing_units_change", "Housing-unit change by 2020 tract"))])
    return


@app.cell
def _(concentration, mo, px):
    figure = px.line(concentration, x="cumulative_positive_tract_share", y="cumulative_positive_change_share", color="measure", hover_data=["tract_geoid", "tract_rank", "change_value"], title="Positive growth concentration")
    figure.add_hline(y=0.5, line_dash="dot"); figure.add_hline(y=0.8, line_dash="dot")
    mo.ui.plotly(figure)
    return


@app.cell
def _(counties, mo, places, px):
    county_view = counties.sort_values("housing_units_change", ascending=False)
    place_view = places.sort_values("housing_units_change", ascending=False)
    county_chart = px.bar(county_view, x="housing_units_change", y="county_name", orientation="h", title="County housing-unit contribution")
    mo.vstack([mo.md("## County and Census Place lenses\nCounties are exact CBSA components. Places are direct ACS values and never sum into the metro ledger; split or partial rows require allocation or a whole-Place caveat."), mo.md("### County growth and native-grain permit context"), mo.ui.plotly(county_chart), mo.ui.table(county_view, page_size=30), mo.md("### Named Place growth and native-grain permit context"), mo.ui.table(place_view, page_size=30)])
    return


@app.cell
def _(coverage, mo, qa):
    mo.vstack([mo.md("## National calibration and harmonization QA\nNational output is method coverage, not a metro ranking. Allocation error and low-confidence sources remain visible."), mo.ui.table(coverage, page_size=20), mo.ui.table(qa, page_size=20)])
    return


if __name__ == "__main__":
    app.run()
