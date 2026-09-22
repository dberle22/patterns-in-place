import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This notebook is a read-only presentation layer. The Q1 mart and named
    # readers own joins, field definitions, periods, and eligibility rules.
    import os
    from pathlib import Path

    import duckdb
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from shapely import wkb
    from shapely.geometry import mapping

    return Path, duckdb, go, mapping, mo, os, pd, plt, px, wkb


@app.cell
def _(Path, duckdb, os, pd):
    analysis_dir = Path(__file__).resolve().parent
    query_dir = analysis_dir / "queries"
    repo_root = analysis_dir.parents[3]

    def db_path() -> str:
        return os.environ.get("DB_PATH", "").strip() or str(
            repo_root / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
        )

    def read_query(connection: duckdb.DuckDBPyConnection, name: str) -> pd.DataFrame:
        """Read a named Q1 query without duplicating SQL in notebook cells."""

        return connection.sql((query_dir / name).read_text()).df()

    return db_path, read_query


@app.cell
def _(db_path, duckdb, read_query):
    with duckdb.connect(db_path(), read_only=True) as connection:
        coverage = read_query(connection, "q1_coverage.sql")
        metric_contract = read_query(connection, "q1_metric_contract.sql")
        components = read_query(connection, "q1_national_component_scatter.sql")
        candidate_index = read_query(connection, "q1_cbsa_index_sensitivity.sql")
        cbsa_map = read_query(connection, "q1_cbsa_map.sql")
        state_boundaries = read_query(connection, "q1_state_boundaries.sql")
    return candidate_index, cbsa_map, components, coverage, metric_contract, state_boundaries


@app.cell
def _(mo):
    mo.md("""
    # Explanation Q1 — National Supply and Demand

    **Question:** when housing access is better or worse, is the observable
    evidence more consistent with supply response, weak demand, or mixed
    conditions? The 2024 ACS snapshot establishes conditions first. The
    candidate index appears last and remains a diagnostic, not a conclusion.
    """)
    return


@app.cell
def _(mo):
    # Keep one primary comparison universe. Small CBSAs remain inspectable in
    # the mart but are not mixed into volatile percentage-change comparisons.
    universe_selector = mo.ui.dropdown(
        {"Major CBSAs (population 100,000+)": "major", "All CBSAs (context only)": "all"},
        value="Major CBSAs (population 100,000+)",
        label="National comparison universe",
    )
    mo.vstack([mo.md("## Scope and metric contract"), universe_selector])
    return (universe_selector,)


@app.cell
def _(components, universe_selector):
    national = components.loc[components.pop_total.ge(100000)].copy() if universe_selector.value == "major" else components.copy()
    return (national,)


@app.cell
def _(coverage, metric_contract, mo, national, universe_selector):
    universe_note = "major CBSAs are the primary comparison universe" if universe_selector.value == "major" else "all CBSAs are descriptive context; the candidate index remains major-CBSA only"
    mo.vstack([
        mo.md("All condition charts use the **2024 ACS snapshot** and five-year measures ending in 2024. " + universe_note + f" ({len(national):,} rows)."),
        mo.ui.table(coverage, page_size=10),
        mo.md("### Metric contract"),
        mo.ui.table(metric_contract, page_size=10),
    ])
    return


@app.cell
def _(mo):
    distribution_fields = {
        "Renter households burdened at 30%+": "pct_rent_burden_30plus",
        "Median-rent-to-all-household-income price proxy": "median_rent_to_all_hh_income_proxy",
        "Value-to-income market-entry proxy": "value_to_income",
        "Five-year FHFA home-price momentum": "hpi_5yr_pct",
        "Five-year ACS rent momentum": "rent_growth_5yr",
        "Five-year housing-stock growth": "housing_unit_growth_5yr",
        "Five-year permits per starting 1,000 units": "permits_5yr_per_1000_start_units",
        "Five-year population growth": "pop_growth_5yr",
        "Vacancy rate": "vacancy_rate",
    }
    distribution_selector = mo.ui.dropdown(distribution_fields, value="Renter households burdened at 30%+", label="Condition distribution")
    mo.vstack([mo.md("## National housing conditions"), mo.md("Each distribution is a condition, not an index component score."), distribution_selector])
    return distribution_fields, distribution_selector


@app.cell
def _(distribution_fields, distribution_selector, national, plt):
    column = distribution_selector.value
    label = next(name for name, field in distribution_fields.items() if field == column)
    condition_figure, _axis = plt.subplots(figsize=(9, 4.8))
    _axis.hist(national[column].dropna(), bins=32, color="#2b6cb0", alpha=0.8)
    if column == "pct_rent_burden_30plus":
        _axis.axvline(0.30, color="black", linestyle="--", label="30% of renter households")
        _axis.legend()
    _axis.set(title=label, xlabel=label, ylabel="CBSAs")
    condition_figure.tight_layout()
    return (condition_figure,)


@app.cell
def _(condition_figure, mo):
    mo.vstack([condition_figure])
    return


@app.cell
def _(mo):
    # Raw supply inputs deliberately retain their observed direction. The
    # composite is separately direction-adjusted so larger means constraint.
    momentum_options = {
        "FHFA home-price momentum, five years": "hpi_5yr_pct",
        "ACS rent momentum, five years": "rent_growth_5yr",
        "Momentum composite (higher = stronger momentum)": "momentum_component_score",
    }
    supply_options = {
        "Housing-stock growth, five years (higher = stronger response)": "housing_unit_growth_5yr",
        "Permits per starting 1,000 units, five years (higher = stronger response)": "permits_5yr_per_1000_start_units",
        "Vacancy rate (higher = looser market)": "vacancy_rate",
        "Supply-constraint composite (higher = weaker response)": "supply_constraint_component_score",
    }
    color_options = {
        "Five-year population growth": "pop_growth_5yr",
        "Demand component score": "demand_component_score",
        "Renter-burden change, five years": "pct_rent_burden_30plus_change_5yr",
        "No color scale": "none",
    }
    momentum_selector = mo.ui.dropdown(momentum_options, value="Momentum composite (higher = stronger momentum)", label="Momentum measure")
    supply_selector = mo.ui.dropdown(supply_options, value="Supply-constraint composite (higher = weaker response)", label="Supply / constraint measure")
    pressure_color_selector = mo.ui.dropdown(color_options, value="Demand component score", label="Point color")
    mo.vstack([
        mo.md("## Pressure and supply response"),
        mo.md("Compare raw KPIs or composites directly. Read the axis direction: raw supply measures increase with response, while the supply-constraint composite increases with weaker response."),
        mo.hstack([momentum_selector, supply_selector, pressure_color_selector], justify="start"),
    ])
    return color_options, momentum_options, momentum_selector, pressure_color_selector, supply_options, supply_selector


@app.cell
def _(candidate_index, color_options, momentum_options, momentum_selector, mo, pressure_color_selector, px, supply_options, supply_selector):
    momentum_field = momentum_selector.value
    supply_field = supply_selector.value
    color_field = pressure_color_selector.value
    momentum_label = next(label for label, field in momentum_options.items() if field == momentum_field)
    supply_label = next(label for label, field in supply_options.items() if field == supply_field)
    plot_data = candidate_index.dropna(subset=[momentum_field, supply_field]).copy()
    hover_columns = ["cbsa_name", "pop_total", "hpi_5yr_pct", "rent_growth_5yr", "housing_unit_growth_5yr", "permits_5yr_per_1000_start_units", "vacancy_rate", "pop_growth_5yr"]
    if color_field == "none":
        pressure_figure = px.scatter(plot_data, x=supply_field, y=momentum_field, hover_data=hover_columns, title=f"{momentum_label} versus {supply_label}")
    else:
        color_label = next(label for label, field in color_options.items() if field == color_field)
        pressure_figure = px.scatter(plot_data, x=supply_field, y=momentum_field, color=color_field, hover_data=hover_columns, color_continuous_scale="Viridis", title=f"{momentum_label} versus {supply_label}", labels={color_field: color_label})
    pressure_figure.update_traces(marker={"size": 8, "opacity": 0.72})
    pressure_figure.update_layout(xaxis_title=supply_label, yaxis_title=momentum_label)
    mo.vstack([mo.md("The selected relationship is descriptive, not causal. Hover values preserve the component inputs behind each point."), mo.ui.plotly(pressure_figure)])
    return


@app.cell
def _(candidate_index, mo, plt):
    _points = candidate_index.dropna(subset=["pct_rent_burden_30plus_change_5yr", "value_to_income_change_5yr"])
    _figure, _axis = plt.subplots(figsize=(9, 6))
    _scatter = _axis.scatter(_points.pct_rent_burden_30plus_change_5yr, _points.value_to_income_change_5yr, c=_points.pop_growth_5yr, cmap="magma", alpha=0.75, s=30)
    _axis.axvline(0, color="0.55", linewidth=0.8)
    _axis.axhline(0, color="0.55", linewidth=0.8)
    _axis.set(title="Renter-burden change and buyer-access change", xlabel="Five-year change in renter households burdened at 30%+", ylabel="Five-year value-to-income change")
    _figure.colorbar(_scatter, ax=_axis, label="Five-year population growth")
    _figure.tight_layout()
    mo.vstack([mo.md("## Affordability conditions"), mo.md("Renter burden and buyer market access are separate outcomes. The plot does not convert either into a causal supply or demand claim."), _figure])
    return


@app.cell
def _(mo):
    map_metric_options = {
        "Candidate composite (provisional)": "balanced_index",
        "Momentum composite": "momentum_component_score",
        "Supply-constraint composite": "supply_constraint_component_score",
        "Demand component": "demand_component_score",
        "Affordability-deterioration composite": "affordability_deterioration_component_score",
        "FHFA home-price momentum, five years": "hpi_5yr_pct",
        "ACS rent momentum, five years": "rent_growth_5yr",
        "Housing-stock growth, five years": "housing_unit_growth_5yr",
        "Five-year permits per starting 1,000 units": "permits_5yr_per_1000_start_units",
        "Five-year population growth": "pop_growth_5yr",
        "Renter-burden change, five years": "pct_rent_burden_30plus_change_5yr",
        "Value-to-income change, five years": "value_to_income_change_5yr",
    }
    map_metric_selector = mo.ui.dropdown(map_metric_options, value="Candidate composite (provisional)", label="Map coloring")
    mo.vstack([mo.md("## National KPI and component map"), mo.md("CBSA polygons and state outlines provide geographic context. Use the selector to compare the candidate composite with its inputs."), map_metric_selector])
    return map_metric_options, map_metric_selector


@app.cell
def _(candidate_index, cbsa_map, go, map_metric_options, map_metric_selector, mapping, mo, state_boundaries, wkb):
    # Render actual geography instead of centroids. National display does not
    # need survey-grade boundaries: simplifying at roughly 300 metres retains
    # recognizable CBSA/state shapes while avoiding an oversized Marimo payload.
    # The source WKB remains untouched in Geo; this is display-only geometry.
    display_simplify_degrees = 0.003
    map_field = map_metric_selector.value
    map_label = next(label for label, field in map_metric_options.items() if field == map_field)
    # Keep the geometry reader's canonical name and avoid a suffixed duplicate
    # when the scored component reader contributes the selected KPI fields.
    map_data = cbsa_map.merge(candidate_index.drop(columns="cbsa_name"), on="cbsa_code", how="inner").dropna(subset=[map_field]).copy()
    cbsa_geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"cbsa_code": row.cbsa_code}, "geometry": mapping(wkb.loads(bytes(row.geom_wkb)).simplify(display_simplify_degrees, preserve_topology=True))}
        for row in map_data.itertuples()
    ]}
    state_geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"state_abbr": row.state_abbr}, "geometry": mapping(wkb.loads(bytes(row.geom_wkb)).simplify(display_simplify_degrees, preserve_topology=True))}
        for row in state_boundaries.itertuples()
    ]}
    map_figure = go.Figure()
    map_figure.add_trace(go.Choropleth(
        geojson=state_geojson, locations=state_boundaries.state_abbr,
        featureidkey="properties.state_abbr", z=[0] * len(state_boundaries),
        colorscale=[[0, "rgba(255,255,255,0)"], [1, "rgba(255,255,255,0)"]],
        showscale=False, marker_line_color="#6b7280", marker_line_width=0.7,
        hoverinfo="skip",
    ))
    map_figure.add_trace(go.Choropleth(
        geojson=cbsa_geojson, locations=map_data.cbsa_code,
        featureidkey="properties.cbsa_code", z=map_data[map_field],
        colorscale="RdYlBu_r", marker_line_color="rgba(255,255,255,0.7)",
        marker_line_width=0.35, colorbar_title=map_label,
        customdata=map_data[["cbsa_name", "pop_total"]],
        hovertemplate="%{customdata[0]}<br>Population: %{customdata[1]:,.0f}<br>Value: %{z:.3f}<extra></extra>",
    ))
    map_figure.update_geos(scope="usa", projection_type="albers usa", showland=True, landcolor="#f8fafc", showlakes=False, showcoastlines=False, bgcolor="rgba(0,0,0,0)")
    map_figure.update_layout(title=f"{map_label} — major CBSAs", margin={"r": 0, "t": 50, "l": 0, "b": 0}, height=650)
    mo.vstack([mo.ui.plotly(map_figure)])
    return


@app.cell
def _(candidate_index, mo):
    # Alternative weights are shown explicitly so equal weights are never read
    # as a settled substantive choice. Epic 9 decides whether to retain it.
    sensitivity = candidate_index.copy()
    sensitivity["max_rank_shift"] = sensitivity[["balanced_rank", "momentum_demand_rank", "affordability_supply_rank"]].max(axis=1) - sensitivity[["balanced_rank", "momentum_demand_rank", "affordability_supply_rank"]].min(axis=1)
    columns = ["cbsa_name", "balanced_rank", "momentum_demand_rank", "affordability_supply_rank", "max_rank_shift", "component_classification"]
    mo.vstack([mo.md("## Candidate-index methodology and sensitivity"), mo.md("It uses complete major-CBSA families only: momentum, affordability deterioration, demand, and supply constraint."), mo.ui.table(sensitivity.sort_values("max_rank_shift", ascending=False)[columns], page_size=20)])
    return


@app.cell
def _(mo):
    mo.outline(label="Notebook sections")
    return


if __name__ == "__main__":
    app.run()
