import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # The notebook only inspects Q1-owned reader surfaces; the component mart
    # remains the source of calculation logic and component definitions.
    import os
    from pathlib import Path

    import duckdb
    import geopandas as gpd
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd
    from shapely import wkb

    return Path, duckdb, gpd, mo, os, pd, plt, wkb


@app.cell
def _(Path, duckdb, os, pd):
    # Resolve all local assets from this file, independent of the editor cwd.
    q1_analysis_dir = Path(__file__).resolve().parent
    q1_repo_root = q1_analysis_dir.parents[3]
    q1_query_dir = q1_analysis_dir / "queries"
    q1_output_dir = q1_analysis_dir / "outputs" / "national"

    def resolve_q1_db_path() -> str:
        configured_path = os.environ.get("DB_PATH", "").strip()
        if configured_path:
            return configured_path
        return str(q1_repo_root / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb")

    def read_q1_query(q1_connection: duckdb.DuckDBPyConnection, query_name: str) -> pd.DataFrame:
        return q1_connection.sql((q1_query_dir / query_name).read_text()).df()

    return q1_output_dir, read_q1_query, resolve_q1_db_path


@app.cell
def _(duckdb, read_q1_query, resolve_q1_db_path):
    # Load the eligible CBSA universe and supporting geometries once, read-only.
    with duckdb.connect(resolve_q1_db_path(), read_only=True) as q1_load_connection:
        q1_coverage_df = read_q1_query(q1_load_connection, "q1_coverage.sql")
        q1_component_inputs_df = read_q1_query(q1_load_connection, "q1_national_component_scatter.sql")
        q1_sensitivity_df = read_q1_query(q1_load_connection, "q1_cbsa_index_sensitivity.sql")
        q1_cbsa_map_df = read_q1_query(q1_load_connection, "q1_cbsa_map.sql")
        q1_state_boundaries_df = read_q1_query(q1_load_connection, "q1_state_boundaries.sql")
    return q1_cbsa_map_df, q1_component_inputs_df, q1_coverage_df, q1_sensitivity_df, q1_state_boundaries_df


@app.cell
def _(mo):
    mo.md("""
    # Explanation Q1 — National Supply or Demand Review

    Explore whether affordability aligns more with supply support, weak demand,
    or a mixed condition. The diagnostic index appears last because it is a
    transparent sensitivity exercise—not a causal conclusion.
    """)
    return


@app.cell
def _(mo):
    # These controls define one cohort for every exploratory visual below.
    q1_cbsa_type_selector = mo.ui.dropdown(
        {
            "All CBSAs": "all",
            "Metropolitan Statistical Areas": "metro",
            "Micropolitan Statistical Areas": "micro",
        },
        value="All CBSAs",
        label="CBSA type",
    )
    mo.vstack([mo.md("## Cohort"), q1_cbsa_type_selector])
    return (q1_cbsa_type_selector,)


@app.cell
def _(q1_cbsa_type_selector, q1_component_inputs_df, q1_sensitivity_df):
    # Component scores retain their national-percentile basis. The cohort filter
    # changes which CBSAs appear, not how raw inputs were scored.
    q1_selected_cbsa_type = q1_cbsa_type_selector.value
    if q1_selected_cbsa_type == "all":
        q1_filtered_components_df = q1_component_inputs_df.copy()
        q1_filtered_sensitivity_df = q1_sensitivity_df.copy()
    else:
        q1_filtered_components_df = q1_component_inputs_df.loc[q1_component_inputs_df.cbsa_type_short.eq(q1_selected_cbsa_type)].copy()
        q1_filtered_sensitivity_df = q1_sensitivity_df.loc[q1_sensitivity_df.cbsa_type_short.eq(q1_selected_cbsa_type)].copy()
    return q1_filtered_components_df, q1_filtered_sensitivity_df, q1_selected_cbsa_type


@app.cell
def _(mo, q1_coverage_df, q1_filtered_components_df, q1_selected_cbsa_type):
    q1_cohort_label = "all CBSAs" if q1_selected_cbsa_type == "all" else f"{q1_selected_cbsa_type} CBSAs"
    q1_cohort_inventory_df = q1_filtered_components_df.groupby("cbsa_type_short", dropna=False).agg(cbsas=("cbsa_code", "size"), population=("pop_total", "sum")).reset_index()
    mo.vstack([mo.md(f"## Coverage and method inventory\nThe active cohort contains **{len(q1_filtered_components_df):,} {q1_cohort_label}** with the four required core inputs."), mo.ui.table(q1_coverage_df, selection=None), mo.ui.table(q1_cohort_inventory_df, selection=None)])
    return


@app.cell
def _(mo):
    # Supply, demand, and affordability inputs are intentionally separate from
    # price trends, which belong in the later market-context section.
    q1_component_variables = {
        "Renter cost to household income": "renter_cost_to_income",
        "Vacancy rate": "vacancy_rate",
        "Permits per 1,000 housing units": "permits_per_1000_housing_units",
        "Five-year population growth": "pop_growth_5yr",
        "Mobility rate": "mobility_rate",
    }
    q1_distribution_selector = mo.ui.dropdown(q1_component_variables, value="Renter cost to household income", label="Distribution measure")
    q1_scatter_x_selector = mo.ui.dropdown(q1_component_variables, value="Vacancy rate", label="X axis")
    q1_scatter_y_selector = mo.ui.dropdown(q1_component_variables, value="Five-year population growth", label="Y axis")
    q1_scatter_color_selector = mo.ui.dropdown({"None": "none", **q1_component_variables}, value="Renter cost to household income", label="Color")
    mo.vstack([mo.md("## Supply, demand, and affordability exploration"), q1_distribution_selector, mo.hstack([q1_scatter_x_selector, q1_scatter_y_selector, q1_scatter_color_selector], justify="start")])
    return q1_component_variables, q1_distribution_selector, q1_scatter_color_selector, q1_scatter_x_selector, q1_scatter_y_selector


@app.cell
def _(plt, q1_component_variables, q1_distribution_selector, q1_filtered_components_df, q1_output_dir):
    q1_output_dir.mkdir(parents=True, exist_ok=True)
    q1_distribution_column = q1_distribution_selector.value
    q1_distribution_label = next(label for label, column in q1_component_variables.items() if column == q1_distribution_column)
    q1_distribution_figure, q1_distribution_axis = plt.subplots(figsize=(9, 5))
    q1_distribution_axis.hist(q1_filtered_components_df[q1_distribution_column].dropna(), bins=35, color="#1f77b4", alpha=0.75)
    if q1_distribution_column == "renter_cost_to_income":
        q1_distribution_axis.axvline(0.30, color="black", linestyle="--", label="30% baseline")
        q1_distribution_axis.axvline(0.50, color="black", linestyle=":", label="50% stress test")
        q1_distribution_axis.legend()
    q1_distribution_axis.set(title=f"Distribution of {q1_distribution_label}", xlabel=q1_distribution_label, ylabel="CBSAs")
    q1_distribution_figure.tight_layout()
    q1_distribution_figure.savefig(q1_output_dir / "cbsa_selected_component_distribution.png", dpi=160)
    plt.show()
    return


@app.cell
def _(plt, q1_component_variables, q1_filtered_components_df, q1_scatter_color_selector, q1_scatter_x_selector, q1_scatter_y_selector):
    q1_scatter_x = q1_scatter_x_selector.value
    q1_scatter_y = q1_scatter_y_selector.value
    q1_scatter_color = q1_scatter_color_selector.value
    q1_scatter_x_label = next(label for label, column in q1_component_variables.items() if column == q1_scatter_x)
    q1_scatter_y_label = next(label for label, column in q1_component_variables.items() if column == q1_scatter_y)
    q1_exploration_figure, q1_exploration_axis = plt.subplots(figsize=(9, 6))
    if q1_scatter_color == "none":
        q1_exploration_axis.scatter(q1_filtered_components_df[q1_scatter_x], q1_filtered_components_df[q1_scatter_y], alpha=0.65, s=26, color="#1f77b4")
    else:
        q1_scatter_color_label = next(label for label, column in q1_component_variables.items() if column == q1_scatter_color)
        q1_exploration_points = q1_exploration_axis.scatter(q1_filtered_components_df[q1_scatter_x], q1_filtered_components_df[q1_scatter_y], c=q1_filtered_components_df[q1_scatter_color], cmap="viridis", alpha=0.7, s=28)
        q1_exploration_figure.colorbar(q1_exploration_points, ax=q1_exploration_axis, label=q1_scatter_color_label)
    q1_exploration_axis.set(title=f"{q1_scatter_y_label} versus {q1_scatter_x_label}", xlabel=q1_scatter_x_label, ylabel=q1_scatter_y_label)
    q1_exploration_figure.tight_layout()
    plt.show()
    return


@app.cell
def _(mo):
    q1_price_variables = {
        "FHFA house-price growth, five years": "hpi_5yr_pct",
        "Zillow home-value growth, annual average YoY": "zhvi_annual_avg_yoy_pct",
        "Zillow rent growth, annual average YoY": "zori_annual_avg_yoy_pct",
    }
    q1_price_selector = mo.ui.dropdown(q1_price_variables, value="FHFA house-price growth, five years", label="Price-trend measure")
    q1_price_comparison_selector = mo.ui.dropdown({"Renter cost to household income": "renter_cost_to_income", "Vacancy rate": "vacancy_rate", "Permits per 1,000 housing units": "permits_per_1000_housing_units", "Five-year population growth": "pop_growth_5yr", "Mobility rate": "mobility_rate"}, value="Five-year population growth", label="Compare with")
    mo.vstack([mo.md("## Housing-price trend context\nPrice growth is a contextual outcome, not a supply or demand component."), mo.hstack([q1_price_selector, q1_price_comparison_selector], justify="start")])
    return q1_price_selector, q1_price_variables, q1_price_comparison_selector


@app.cell
def _(plt, q1_component_variables, q1_filtered_components_df, q1_price_comparison_selector, q1_price_selector, q1_price_variables):
    q1_price_column = q1_price_selector.value
    q1_price_label = next(label for label, column in q1_price_variables.items() if column == q1_price_column)
    q1_price_comparison_column = q1_price_comparison_selector.value
    q1_price_comparison_label = next(label for label, column in q1_component_variables.items() if column == q1_price_comparison_column)
    q1_price_figure, (q1_price_distribution_axis, q1_price_scatter_axis) = plt.subplots(1, 2, figsize=(13, 5))
    q1_price_distribution_axis.hist(q1_filtered_components_df[q1_price_column].dropna(), bins=35, color="#9467bd", alpha=0.75)
    q1_price_distribution_axis.set(title=f"Distribution of {q1_price_label}", xlabel=q1_price_label, ylabel="CBSAs")
    q1_price_scatter_axis.scatter(q1_filtered_components_df[q1_price_comparison_column], q1_filtered_components_df[q1_price_column], alpha=0.65, s=26, color="#9467bd")
    q1_price_scatter_axis.set(title=f"Price trend versus {q1_price_comparison_label}", xlabel=q1_price_comparison_label, ylabel=q1_price_label)
    q1_price_figure.tight_layout()
    plt.show()
    return


@app.cell
def _(mo, plt, q1_filtered_sensitivity_df):
    # This is the proposed core relationship: price/rent momentum is compared
    # with constrained supply response as separate normalized components. It is
    # intentionally not an unstable raw price-growth / unit-growth ratio.
    q1_imbalance_figure, q1_imbalance_axis = plt.subplots(figsize=(9, 6))
    q1_imbalance_points = q1_imbalance_axis.scatter(
        q1_filtered_sensitivity_df.supply_constraint_component_score,
        q1_filtered_sensitivity_df.momentum_component_score,
        c=q1_filtered_sensitivity_df.affordability_deterioration_component_score,
        cmap="magma_r", alpha=0.75, s=30,
    )
    q1_imbalance_axis.axvline(0.5, color="0.5", linewidth=0.8)
    q1_imbalance_axis.axhline(0.5, color="0.5", linewidth=0.8)
    q1_imbalance_axis.set(
        title="Momentum versus constrained supply response",
        xlabel="Supply constraint (higher = weaker response / tighter market)",
        ylabel="Price and rent momentum",
    )
    q1_imbalance_figure.colorbar(q1_imbalance_points, ax=q1_imbalance_axis, label="Affordability deterioration")
    q1_imbalance_figure.tight_layout()
    mo.vstack([
        mo.md("## Overheating relationship\n"
              "The upper-right quadrant is the candidate overheating pattern: high price/rent momentum alongside weak supply response. Color shows whether cost-to-income is also worsening."),
        q1_imbalance_figure,
    ])
    return


@app.cell
def _(mo, plt, q1_filtered_sensitivity_df):
    # Renter and owner-accessibility change are preserved separately in the
    # mart. This view pairs rent and value ratios without treating either as a
    # replacement for the other.
    q1_ratio_figure, q1_ratio_axis = plt.subplots(figsize=(9, 6))
    q1_ratio_axis.scatter(
        q1_filtered_sensitivity_df.rent_to_income_change_5yr,
        q1_filtered_sensitivity_df.value_to_income_change_5yr,
        alpha=0.7, s=28, color="#b03a2e",
    )
    q1_ratio_axis.axvline(0, color="0.5", linewidth=0.8)
    q1_ratio_axis.axhline(0, color="0.5", linewidth=0.8)
    q1_ratio_axis.set(
        title="Five-year affordability deterioration",
        xlabel="Rent-to-income change",
        ylabel="Value-to-income change",
    )
    q1_ratio_figure.tight_layout()
    mo.vstack([mo.md("## Cost-to-income outcomes"), q1_ratio_figure])
    return


@app.cell
def _(mo):
    q1_map_metric_selector = mo.ui.dropdown({"Balanced diagnostic index": "balanced_index", "Momentum component": "momentum_component_score", "Affordability deterioration": "affordability_deterioration_component_score", "Demand component": "demand_component_score", "Supply constraint": "supply_constraint_component_score"}, value="Balanced diagnostic index", label="Map measure")
    mo.vstack([mo.md("## National map"), q1_map_metric_selector])
    return (q1_map_metric_selector,)


@app.cell
def _(gpd, plt, q1_cbsa_map_df, q1_filtered_sensitivity_df, q1_map_metric_selector, q1_state_boundaries_df, wkb):
    # State outlines establish geographic context; coordinate limits exclude
    # Alaska, Hawaii, and territories from the centroid-based national view.
    q1_state_geometries = gpd.GeoDataFrame(q1_state_boundaries_df.drop(columns="geom_wkb"), geometry=q1_state_boundaries_df.geom_wkb.map(lambda value: wkb.loads(bytes(value))), crs="EPSG:4326")
    q1_cbsa_geometries_df = q1_cbsa_map_df.copy()
    q1_cbsa_geometries_df["centroid"] = q1_cbsa_geometries_df.geom_wkb.map(lambda value: wkb.loads(bytes(value)).centroid)
    q1_cbsa_geometries_df["longitude"] = q1_cbsa_geometries_df.centroid.map(lambda geometry: geometry.x)
    q1_cbsa_geometries_df["latitude"] = q1_cbsa_geometries_df.centroid.map(lambda geometry: geometry.y)
    q1_map_values_df = q1_cbsa_geometries_df.merge(q1_filtered_sensitivity_df, on="cbsa_code", how="inner")
    q1_map_values_df = q1_map_values_df.loc[q1_map_values_df.longitude.between(-125, -66) & q1_map_values_df.latitude.between(24, 50)].copy()
    q1_map_column = q1_map_metric_selector.value
    q1_map_figure, q1_map_axis = plt.subplots(figsize=(12, 7))
    q1_state_geometries.boundary.plot(ax=q1_map_axis, color="#9aa0a6", linewidth=0.45)
    q1_map_scatter = q1_map_axis.scatter(q1_map_values_df.longitude, q1_map_values_df.latitude, c=q1_map_values_df[q1_map_column], s=10 + 70 * (q1_map_values_df.pop_total / q1_map_values_df.pop_total.max()) ** 0.4, cmap="RdYlBu_r", alpha=0.78, linewidths=0)
    q1_map_axis.set(xlim=(-125, -66), ylim=(24, 50), title="Lower-48 CBSA context", xlabel="Longitude", ylabel="Latitude")
    q1_map_figure.colorbar(q1_map_scatter, ax=q1_map_axis, label=q1_map_column.replace("_", " ").title())
    q1_map_figure.tight_layout()
    plt.show()
    return (q1_map_values_df,)


@app.cell
def _(q1_filtered_sensitivity_df):
    # Rerank selected cohorts while retaining component scores calculated in the
    # full eligible national universe, making cohort comparisons explicit.
    q1_index_sensitivity_df = q1_filtered_sensitivity_df.copy()
    q1_index_sensitivity_df["max_rank_shift"] = q1_index_sensitivity_df[["balanced_rank", "momentum_demand_rank", "affordability_supply_rank"]].max(axis=1) - q1_index_sensitivity_df[["balanced_rank", "momentum_demand_rank", "affordability_supply_rank"]].min(axis=1)
    q1_index_rank_shift_df = q1_index_sensitivity_df.sort_values("max_rank_shift", ascending=False).head(20).copy()
    return q1_index_rank_shift_df, q1_index_sensitivity_df


@app.cell
def _(mo, q1_index_rank_shift_df):
    mo.vstack([mo.md("## Index sensitivity\nAll scenarios use the complete four-family major-CBSA universe. The alternatives respectively emphasize momentum/demand or affordability deterioration/supply constraint; `max_rank_shift` shows sensitivity to that choice."), mo.ui.dataframe(q1_index_rank_shift_df, page_size=20)])
    return


@app.cell
def _(mo):
    # This uses executed Markdown headers, so it remains the canonical notebook
    # navigation surface even where VS Code's generic Outline pane is limited.
    mo.outline(label="Notebook sections")
    return


if __name__ == "__main__":
    app.run()
