import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # The notebook consumes named mart readers only. It deliberately does not
    # recreate geographic membership, affordability definitions, or crosswalks.
    import os
    from pathlib import Path

    import duckdb
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd
    import plotly.express as px
    from shapely import wkb
    from shapely.geometry import mapping

    return Path, duckdb, mapping, mo, os, pd, plt, px, wkb


@app.cell
def _(Path, duckdb, os, pd):
    analysis_dir = Path(__file__).resolve().parent
    query_dir = analysis_dir / "queries"
    repo_root = analysis_dir.parents[3]

    def db_path() -> str:
        return os.environ.get("DB_PATH", "").strip() or str(
            repo_root / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
        )

    def read_market_query(connection: duckdb.DuckDBPyConnection, name: str, cbsa_code: str) -> pd.DataFrame:
        """Bind a selected canonical CBSA code into a named, scoped reader."""

        sql = (query_dir / name).read_text().replace("__CBSA_CODE__", cbsa_code)
        return connection.sql(sql).df()

    return analysis_dir, db_path, query_dir, read_market_query


@app.cell
def _(pd):
    def conditions_matrix(data, id_column, name_column):
        """Create a transparent, within-market descriptive conditions screen."""

        fields = ["pct_rent_burden_30plus", "vacancy_rate", "pop_growth_5yr"]
        matrix = data.copy()
        burden_midpoint = matrix.pct_rent_burden_30plus.median()
        vacancy_midpoint = matrix.vacancy_rate.median()
        matrix["initial_label"] = "mixed conditions"
        matrix.loc[matrix[fields].isna().any(axis=1), "initial_label"] = "no clear signal"
        matrix.loc[(matrix.pct_rent_burden_30plus <= burden_midpoint) & (matrix.vacancy_rate >= vacancy_midpoint) & matrix[fields].notna().all(axis=1), "initial_label"] = "lower burden / higher vacancy"
        matrix.loc[(matrix.pct_rent_burden_30plus <= burden_midpoint) & (matrix.pop_growth_5yr <= 0) & matrix[fields].notna().all(axis=1), "initial_label"] = "lower burden / non-growth"
        matrix.loc[(matrix.pct_rent_burden_30plus > burden_midpoint) & (matrix.pop_growth_5yr > 0) & (matrix.vacancy_rate < vacancy_midpoint), "initial_label"] = "higher burden / growth / lower vacancy"
        columns = [id_column, name_column, "initial_label", "pct_rent_burden_30plus", "median_rent_to_all_hh_income_proxy", "vacancy_rate", "pop_growth_5yr"]
        return matrix[columns].sort_values(["initial_label", name_column])

    return (conditions_matrix,)


@app.cell
def _(db_path, duckdb, query_dir):
    with duckdb.connect(db_path(), read_only=True) as _connection:
        cbsa_options = _connection.sql((query_dir / "q1_cbsa_options.sql").read_text()).df()
    return (cbsa_options,)


@app.cell
def _(cbsa_options, mo):
    # This uses the project-standard name-plus-code pattern and defaults to the
    # first reviewed market. The code remains the query key, never free text.
    option_labels = dict(zip(cbsa_options.display_name, cbsa_options.cbsa_code))
    market_selector = mo.ui.dropdown(
        option_labels,
        value="Richmond, VA (40060)",
        label="CBSA",
        searchable=True,
    )
    mo.vstack([
        mo.md("# Explanation Q1 — Market Supply and Demand"),
        mo.md("Start with broad-market conditions, then inspect direct tract evidence. ZCTA prices and Place permits remain separate context lenses."),
        market_selector,
    ])
    return (market_selector,)


@app.cell
def _(db_path, duckdb, market_selector, read_market_query):
    market_id = market_selector.value
    with duckdb.connect(db_path(), read_only=True) as _connection:
        cbsa_county_context = read_market_query(_connection, "q1_market_cbsa_county_context.sql", market_id)
        tracts = read_market_query(_connection, "q1_market_tracts.sql", market_id)
        tract_map = read_market_query(_connection, "q1_market_tract_map.sql", market_id)
        zctas = read_market_query(_connection, "q1_market_zcta_context.sql", market_id)
        places = read_market_query(_connection, "q1_market_place_context.sql", market_id)
        national_benchmark = read_market_query(_connection, "q1_market_national_benchmark.sql", market_id)
        zcta_map = read_market_query(_connection, "q1_market_zcta_map.sql", market_id)
        place_map = read_market_query(_connection, "q1_market_place_map.sql", market_id)
    if cbsa_county_context.empty:
        raise ValueError(f"No Q1 evidence exists for selected CBSA {market_id}.")
    market_name = cbsa_county_context.loc[cbsa_county_context.geo_level.eq("cbsa"), "geo_name"].iloc[0]
    return cbsa_county_context, market_id, market_name, national_benchmark, place_map, places, tract_map, tracts, zcta_map, zctas


@app.cell
def _(mo):
    mo.md("""
    ## Metric definitions

    **Renter burden** is the ACS share of renter households spending 30% or
    more of income on rent. **Median-rent-to-all-household-income** is a local
    market-price proxy, not a household burden test. Owner costs describe
    existing owners by mortgage status; they are not current-buyer payments.
    """)
    return


@app.cell
def _(cbsa_county_context, market_name, mo, national_benchmark, plt):
    # Native units are deliberately separated. A shared axis would hide the
    # vacancy percentage beneath permits per 1,000 units and invite comparison
    # of unlike quantities.
    cbsa = cbsa_county_context.loc[cbsa_county_context.geo_level.eq("cbsa")].copy()
    _figure, _axes = plt.subplots(2, 2, figsize=(13, 8), sharex=True)
    for _axis, _field, _mean, _p25, _p75, _title, _ylabel, _color in [
        (_axes[0, 0], "pct_rent_burden_30plus", "renter_burden_weighted_mean", "renter_burden_p25", "renter_burden_p75", "Renter households burdened at 30%+", "Share of renter households", "#2b6cb0"),
        (_axes[0, 1], "value_to_income", "value_to_income_weighted_mean", "value_to_income_p25", "value_to_income_p75", "Value-to-income market-entry proxy", "Ratio", "#b03a2e"),
        (_axes[1, 0], "vacancy_rate", "vacancy_weighted_mean", "vacancy_p25", "vacancy_p75", "Vacancy context", "Vacancy rate", "#2f855a"),
        (_axes[1, 1], "permits_per_1000_housing_units", "permits_weighted_mean", "permits_p25", "permits_p75", "Annual construction response", "Permits per 1,000 units", "#805ad5"),
    ]:
        _axis.fill_between(national_benchmark.year, national_benchmark[_p25], national_benchmark[_p75], color="0.75", alpha=0.25, label="Major-CBSA 25th–75th percentile")
        _axis.plot(national_benchmark.year, national_benchmark[_mean], color="0.35", linestyle="--", label="Population-weighted major-CBSA mean")
        _axis.plot(cbsa.year, cbsa[_field], color=_color, linewidth=2, label=market_name)
        _axis.set(title=_title, ylabel=_ylabel)
        _axis.legend(fontsize=7, loc="best")
    _axes[1, 0].set(xlabel="Year")
    _axes[1, 1].set(xlabel="Year")
    _figure.suptitle(f"{market_name}: broad-market conditions in native units", y=1.02)
    _figure.tight_layout()
    latest_counties = cbsa_county_context.loc[(cbsa_county_context.geo_level.eq("county")) & (cbsa_county_context.year.eq(2024)), ["geo_name", "pct_rent_burden_30plus", "vacancy_rate", "permits_per_1000_housing_units", "housing_unit_growth_5yr", "pop_growth_5yr"]].sort_values("permits_per_1000_housing_units", ascending=False)
    mo.vstack([mo.md("## Broad-market and county context"), mo.md("Solid line: selected CBSA. Dashed line: population-weighted major-CBSA benchmark. Band: unweighted major-CBSA 25th–75th percentile."), _figure, mo.ui.table(latest_counties, page_size=20)])
    return cbsa, latest_counties


@app.cell
def _(cbsa, market_name, mo, national_benchmark, plt):
    # An indexed view is optional and only supports co-movement inspection. It
    # does not replace the native-unit panels above or imply common units.
    indexed = cbsa.merge(national_benchmark, on="year", how="left")
    for column, mean, p25, p75 in [("vacancy_rate", "vacancy_weighted_mean", "vacancy_p25", "vacancy_p75"), ("permits_per_1000_housing_units", "permits_weighted_mean", "permits_p25", "permits_p75"), ("housing_unit_growth_5yr", "housing_growth_weighted_mean", "housing_growth_p25", "housing_growth_p75"), ("pop_growth_5yr", "population_growth_weighted_mean", "population_growth_p25", "population_growth_p75")]:
        indexed[f"{column}_relative_iqr"] = (indexed[column] - indexed[mean]) / (indexed[p75] - indexed[p25])
    _figure, _axis = plt.subplots(figsize=(10, 4))
    _axis.plot(indexed.year, indexed.vacancy_rate_relative_iqr, label="Vacancy (looser when higher)", color="#2f855a")
    _axis.plot(indexed.year, indexed.permits_per_1000_housing_units_relative_iqr, label="Permits (more response when higher)", color="#805ad5")
    _axis.plot(indexed.year, indexed.housing_unit_growth_5yr_relative_iqr, label="Housing-stock growth (more response when higher)", color="#dd6b20")
    _axis.plot(indexed.year, indexed.pop_growth_5yr_relative_iqr, label="Population growth (more demand when higher)", color="#2b6cb0", linestyle="--")
    _axis.axhline(0, color="0.65", linewidth=0.8)
    _axis.set(title=f"{market_name}: national-relative supply and demand position", xlabel="Year", ylabel="Difference from weighted mean, in CBSA IQR units")
    _axis.legend()
    _figure.tight_layout()
    mo.vstack([mo.md("### National-relative supply and demand context"), mo.md("Each line is the local value minus the population-weighted major-CBSA mean, scaled by that year’s major-CBSA interquartile range. It compares relative position, not raw units."), _figure])
    return


@app.cell
def _(mo):
    tract_metric_options = {
        "Renter households burdened at 30%+": "pct_rent_burden_30plus",
        "Median-rent-to-all-household-income price proxy": "median_rent_to_all_hh_income_proxy",
        "Vacancy rate": "vacancy_rate",
        "Five-year population growth": "pop_growth_5yr",
        "Annualized median gross rent": "annualized_median_rent",
    }
    tract_metric_selector = mo.ui.dropdown(tract_metric_options, value="Renter households burdened at 30%+", label="Tract map measure")
    mo.vstack([mo.md("## Direct tract evidence"), mo.md("All selections are direct tract measures. The map does not assign county permits or ZCTA prices to tracts."), tract_metric_selector])
    return tract_metric_options, tract_metric_selector


@app.cell
def _(mapping, market_name, mo, pd, px, tract_map, tract_metric_options, tract_metric_selector, tracts, wkb):
    selected_metric = tract_metric_selector.value
    selected_label = next(label for label, field in tract_metric_options.items() if field == selected_metric)
    _mapped = tract_map.dropna(subset=[selected_metric]).copy()
    _mapped["geometry"] = _mapped.geom_wkb.map(lambda value: wkb.loads(bytes(value)))
    _geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"tract_geoid": row.tract_geoid}, "geometry": mapping(row.geometry)}
        for row in _mapped.itertuples()
    ]}
    _figure = px.choropleth(_mapped, geojson=_geojson, locations="tract_geoid", featureidkey="properties.tract_geoid", color=selected_metric, hover_data={"tract_geoid": True, selected_metric: ":.3f", "vacancy_rate": ":.3f", "pop_growth_5yr": ":.3f"}, color_continuous_scale="RdYlBu_r", projection="mercator", title=f"{market_name}: {selected_label}, 2024")
    _figure.update_geos(fitbounds="locations", visible=False)
    _figure.update_layout(margin={"r": 0, "t": 45, "l": 0, "b": 0}, coloraxis_colorbar_title=selected_label)
    tract_table = tracts.sort_values(selected_metric, na_position="last")[["tract_geoid", "tract_name", "pop_total", "pct_rent_burden_30plus", "median_rent_to_all_hh_income_proxy", "vacancy_rate", "pop_growth_5yr", "annualized_median_rent"]]
    mo.vstack([mo.ui.plotly(_figure), mo.ui.table(tract_table, page_size=20)])
    return tract_table,


@app.cell
def _(conditions_matrix, mo, tracts):
    tract_classification = conditions_matrix(tracts, "tract_geoid", "tract_name")
    mo.vstack([mo.md("## Tract conditions matrix"), mo.md("Initial labels are descriptive, not causal: they use the selected CBSA’s median renter burden and vacancy, plus the sign of five-year population growth. Missing any of those inputs yields `no clear signal`. The raw columns remain the evidence."), mo.ui.table(tract_classification, page_size=20)])
    return (tract_classification,)


@app.cell
def _(mo):
    zcta_metric_options = {"Renter burden at 30%+": "pct_rent_burden_30plus", "Rent-price proxy": "median_rent_to_all_hh_income_proxy", "Vacancy rate": "vacancy_rate", "Zillow home-value growth": "zhvi_annual_avg_yoy_pct", "Zillow rent growth": "zori_annual_avg_yoy_pct"}
    place_metric_options = {"Renter burden at 30%+": "pct_rent_burden_30plus", "Rent-price proxy": "median_rent_to_all_hh_income_proxy", "Vacancy rate": "vacancy_rate", "Permits per 1,000 units": "permits_per_1000_housing_units"}
    zcta_metric_selector = mo.ui.dropdown(zcta_metric_options, value="Zillow home-value growth", label="ZCTA map measure")
    place_metric_selector = mo.ui.dropdown(place_metric_options, value="Permits per 1,000 units", label="Place map measure")
    return place_metric_options, place_metric_selector, zcta_metric_options, zcta_metric_selector


@app.cell
def _(conditions_matrix, mapping, market_name, mo, px, wkb, zcta_map, zcta_metric_options, zcta_metric_selector, zctas):
    _selected = zcta_metric_selector.value
    _label = next(name for name, field in zcta_metric_options.items() if field == _selected)
    _mapped = zcta_map.dropna(subset=[_selected]).copy()
    _mapped["geometry"] = _mapped.geom_wkb.map(lambda value: wkb.loads(bytes(value)).simplify(0.001, preserve_topology=True))
    _geojson = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"zcta": row.zcta}, "geometry": mapping(row.geometry)} for row in _mapped.itertuples()]}
    _figure = px.choropleth(_mapped, geojson=_geojson, locations="zcta", featureidkey="properties.zcta", color=_selected, hover_data={"zcta": True, "pct_rent_burden_30plus": ":.3f", "median_rent_to_all_hh_income_proxy": ":.3f", "vacancy_rate": ":.3f"}, color_continuous_scale="RdYlBu_r", projection="mercator", title=f"{market_name}: ZCTA market-price and conditions geography")
    _figure.update_geos(fitbounds="locations", visible=False)
    _figure.update_layout(margin={"r": 0, "t": 45, "l": 0, "b": 0}, coloraxis_colorbar_title=_label)
    zcta_matrix = conditions_matrix(zctas, "zcta", "geo_name")
    mo.vstack([mo.md("## ZCTA market-price and conditions geography"), mo.md("ZCTAs provide the price/appreciation companion where no managed tract price series exists; they also retain direct renter burden, rent-price proxy, and vacancy context."), zcta_metric_selector, mo.ui.plotly(_figure), mo.md("### ZCTA conditions matrix"), mo.ui.table(zcta_matrix, page_size=20)])
    return (zcta_matrix,)


@app.cell
def _(conditions_matrix, mapping, market_name, mo, pd, place_map, place_metric_options, place_metric_selector, places, px, wkb):
    _selected = place_metric_selector.value
    _label = next(name for name, field in place_metric_options.items() if field == _selected)
    _mapped = place_map.dropna(subset=[_selected]).copy()
    _mapped["geometry"] = _mapped.geom_wkb.map(lambda value: wkb.loads(bytes(value)).simplify(0.001, preserve_topology=True))
    _geojson = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"place_id": row.place_id}, "geometry": mapping(row.geometry)} for row in _mapped.itertuples()]}
    _figure = px.choropleth(_mapped, geojson=_geojson, locations="place_id", featureidkey="properties.place_id", color=_selected, hover_data={"geo_name": True, "pct_rent_burden_30plus": ":.3f", "median_rent_to_all_hh_income_proxy": ":.3f", "vacancy_rate": ":.3f", "permits_per_1000_housing_units": ":.2f"}, color_continuous_scale="RdYlBu_r", projection="mercator", title=f"{market_name}: Place municipal context")
    _figure.update_geos(fitbounds="locations", visible=False)
    _figure.update_layout(margin={"r": 0, "t": 45, "l": 0, "b": 0}, coloraxis_colorbar_title=_label)
    place_matrix = conditions_matrix(places, "place_id", "geo_name")
    place_summary = pd.DataFrame([{
        "place_count": len(places),
        "places_with_permits": int(places.permits_total_units.notna().sum()),
        "national_population_weighted_place_permit_coverage": "77.3%",
        "interpretation": "Place memberships overlap; they are context, not a CBSA population partition.",
    }])
    mo.vstack([mo.md("## Place municipal supply and conditions context"), mo.md("Places are an overlapping context lens, not a CBSA partition. Permits are shown only where available; affordability and vacancy remain direct Place observations."), place_metric_selector, mo.ui.plotly(_figure), mo.md("### Place conditions matrix"), mo.ui.table(place_matrix, page_size=20), mo.ui.table(place_summary)])
    return place_matrix, place_summary


@app.cell
def _(analysis_dir, cbsa_county_context, market_id, place_matrix, place_summary, places, tract_classification, tract_table, tracts, zcta_matrix, zctas):
    # Persist displayed tabular evidence only; figures remain interactive in
    # Marimo and have no hidden alternate calculation/export path.
    output_dir = analysis_dir / "outputs" / f"market_{market_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    cbsa_county_context.to_csv(output_dir / "cbsa_county_context.csv", index=False)
    tracts.to_csv(output_dir / "tract_evidence.csv", index=False)
    tract_table.to_csv(output_dir / "tract_selected_metric_table.csv", index=False)
    tract_classification.to_csv(output_dir / "tract_classification.csv", index=False)
    zcta_matrix.to_csv(output_dir / "zcta_conditions_matrix.csv", index=False)
    place_matrix.to_csv(output_dir / "place_conditions_matrix.csv", index=False)
    zctas.to_csv(output_dir / "zcta_price_context.csv", index=False)
    places.to_csv(output_dir / "place_context.csv", index=False)
    place_summary.to_csv(output_dir / "place_summary.csv", index=False)
    return


@app.cell
def _(mo):
    mo.outline(label="Notebook sections")
    return


if __name__ == "__main__":
    app.run()
