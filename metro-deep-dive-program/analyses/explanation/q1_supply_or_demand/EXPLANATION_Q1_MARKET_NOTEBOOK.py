import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # Keep this notebook a read-only consumer of the Q1 mart and its named SQL
    # readers. It never recreates joins, metric definitions, or crosswalks.
    import os
    from pathlib import Path

    import duckdb
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd
    from shapely import wkb

    return Path, duckdb, mo, os, pd, plt, wkb


@app.cell
def _(Path, os):
    analysis_dir = Path(__file__).resolve().parent
    repo_root = analysis_dir.parents[3]
    query_dir = analysis_dir / "queries"

    def resolve_db_path() -> str:
        """Use DB_PATH when supplied, otherwise use the repository-local DB."""

        return os.environ.get("DB_PATH", "").strip() or str(
            repo_root / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
        )

    return analysis_dir, query_dir, resolve_db_path


@app.cell
def _(mo, os):
    # Richmond is the first Epic 4 market. A numeric CBSA field keeps the same
    # notebook reusable for the next reviewed market without embedding a list.
    market_selector = mo.ui.text(
        value=os.environ.get("Q1_CBSA_CODE", "40060").strip(),
        label="CBSA code",
        full_width=False,
    )
    mo.vstack([
        mo.md("# Explanation Q1 — Market Supply or Demand Review\n"
              "Tracts, ZCTAs, Places, counties, and the CBSA are separate evidence lenses."),
        market_selector,
    ])
    return market_selector,


@app.cell
def _(duckdb, market_selector, query_dir, resolve_db_path):
    market_id = market_selector.value.strip()
    if not market_id.isdigit():
        raise ValueError("CBSA code must contain digits only.")

    def read_market_query(con, name: str):
        """Safely bind the validated CBSA token in a named market reader."""

        return con.sql((query_dir / name).read_text().replace("__CBSA_CODE__", market_id)).df()

    with duckdb.connect(resolve_db_path(), read_only=True) as con:
        cbsa_county_context = read_market_query(con, "q1_market_cbsa_county_context.sql")
        tracts = read_market_query(con, "q1_market_tracts.sql")
        tract_map = read_market_query(con, "q1_market_tract_map.sql")
        zctas = read_market_query(con, "q1_market_zcta_context.sql")
        places = read_market_query(con, "q1_market_place_context.sql")

    if cbsa_county_context.empty:
        raise ValueError(f"No Q1 market evidence exists for CBSA {market_id}.")
    market_name = cbsa_county_context.loc[
        cbsa_county_context.geo_level.eq("cbsa"), "geo_name"
    ].iloc[0]
    return cbsa_county_context, market_id, market_name, places, tract_map, tracts, zctas


@app.cell
def _(cbsa_county_context, market_name, mo, plt):
    cbsa_context = cbsa_county_context.loc[cbsa_county_context.geo_level.eq("cbsa")]
    county_context = cbsa_county_context.loc[cbsa_county_context.geo_level.eq("county")]

    fig_context, axes = plt.subplots(1, 2, figsize=(13, 4.5))
    axes[0].plot(cbsa_context.year, cbsa_context.renter_cost_to_income, label="Renter cost to income", color="#1f77b4")
    axes[0].plot(cbsa_context.year, cbsa_context.owner_cost_to_income_mortgage, label="Owner cost with mortgage", color="#ff7f0e")
    axes[0].axhline(0.30, color="black", linestyle="--", linewidth=0.8)
    axes[0].set(title=f"{market_name}: local cost-to-income", xlabel="Year", ylabel="Ratio")
    axes[0].legend()
    axes[1].plot(cbsa_context.year, cbsa_context.vacancy_rate, label="Vacancy rate", color="#2ca02c")
    axes[1].plot(cbsa_context.year, cbsa_context.permits_per_1000_housing_units, label="Permits per 1,000 units", color="#9467bd")
    axes[1].set(title="CBSA supply context", xlabel="Year", ylabel="Rate")
    axes[1].legend()
    fig_context.tight_layout()

    latest_counties = county_context.loc[county_context.year.eq(2024), [
        "geo_name", "permits_per_1000_housing_units", "vacancy_rate", "renter_cost_to_income"
    ]].sort_values("permits_per_1000_housing_units", ascending=False)
    mo.vstack([mo.md("## Broad-market and county context"), fig_context, mo.ui.table(latest_counties, page_size=20)])
    return cbsa_context, fig_context, latest_counties


@app.cell
def _(market_name, mo, plt, tract_map, tracts, wkb):
    tract_summary = {
        "tract_count": len(tracts),
        "tracts_with_5yr_population_growth": int(tracts.pop_growth_5yr.notna().sum()),
        "tracts_inexpensive_30pct": int((tracts.renter_cost_to_income <= 0.30).sum()),
        "median_renter_cost_to_income": tracts.renter_cost_to_income.median(),
        "median_vacancy_rate": tracts.vacancy_rate.median(),
    }
    map_points = tract_map.copy()
    map_points["centroid"] = map_points.geom_wkb.map(lambda value: wkb.loads(bytes(value)).centroid)
    map_points["longitude"] = map_points.centroid.map(lambda geometry: geometry.x)
    map_points["latitude"] = map_points.centroid.map(lambda geometry: geometry.y)

    fig_tract_map, _axis_tract = plt.subplots(figsize=(8, 8))
    scatter = _axis_tract.scatter(map_points.longitude, map_points.latitude, c=map_points.renter_cost_to_income, cmap="RdYlBu_r", s=18, linewidths=0)
    fig_tract_map.colorbar(scatter, ax=_axis_tract, label="Annualized gross rent / median household income")
    _axis_tract.set(title=f"{market_name}: tract renter affordability, 2024", xlabel="Longitude", ylabel="Latitude")
    fig_tract_map.tight_layout()

    tract_table = tracts.sort_values("renter_cost_to_income")[[
        "tract_geoid", "tract_name", "pop_total", "renter_cost_to_income",
        "owner_cost_to_income_mortgage", "vacancy_rate", "pop_growth_5yr",
        "pct_rent_burden_30plus", "pct_struct_multifam",
    ]]
    mo.vstack([
        mo.md("## Tract evidence\n"
              "This map contains direct tract observations only; county permits and ZCTA prices are not assigned to tracts."),
        mo.md(str(tract_summary)), fig_tract_map, mo.ui.table(tract_table.head(20), page_size=20),
    ])
    return fig_tract_map, map_points, tract_summary, tract_table


@app.cell
def _(mo, pd, tracts):
    # This minimal screen preserves a no-signal result where five-year demand
    # evidence is absent. It is a sensitivity aid, not the Epic 5 index.
    vacancy_median = tracts.vacancy_rate.median()

    def classify_tracts(cost_threshold: float):
        classification = pd.Series("mixed", index=tracts.index, dtype="object")
        classification.loc[tracts.renter_cost_to_income.isna() | tracts.pop_growth_5yr.isna()] = "no clear signal"
        classification.loc[(tracts.renter_cost_to_income <= cost_threshold) & (tracts.vacancy_rate >= vacancy_median) & tracts.pop_growth_5yr.notna()] = "supply-supported affordability"
        classification.loc[(tracts.renter_cost_to_income <= cost_threshold) & (tracts.pop_growth_5yr <= 0) & tracts.pop_growth_5yr.notna()] = "weak-demand affordability"
        classification.loc[(tracts.renter_cost_to_income > cost_threshold) & (tracts.pop_growth_5yr > 0) & (tracts.vacancy_rate < vacancy_median)] = "pressure/shortage"
        return classification

    tract_sensitivity = pd.concat([
        pd.DataFrame({"cost_threshold": threshold, "classification": classify_tracts(threshold)}).value_counts().rename("tract_count").reset_index()
        for threshold in (0.30, 0.50)
    ], ignore_index=True)
    mo.vstack([mo.md("## Tract classification sensitivity"), mo.ui.table(tract_sensitivity, page_size=12)])
    return tract_sensitivity,


@app.cell
def _(market_name, mo, places, plt, zctas):
    zcta_plot = zctas.dropna(subset=["renter_cost_to_income", "zhvi_annual_avg_yoy_pct"])
    fig_zcta, _axis_zcta = plt.subplots(figsize=(8, 6))
    _axis_zcta.scatter(zcta_plot.renter_cost_to_income, zcta_plot.zhvi_annual_avg_yoy_pct, s=20 + 50 * zcta_plot.rel_weight_pop, alpha=0.65)
    _axis_zcta.axvline(0.30, color="black", linestyle="--", linewidth=0.8)
    _axis_zcta.set(title=f"{market_name}: ZCTA price-response context", xlabel="Renter cost to household income", ylabel="ZHVI annual growth")
    fig_zcta.tight_layout()

    place_summary = {
        "place_count": len(places),
        "places_with_permits": int(places.permits_total_units.notna().sum()),
        "national_weighted_place_permit_coverage": "77.3%",
        "note": "Richmond Place memberships overlap and are context, not a CBSA population partition.",
    }
    mo.vstack([mo.md("## ZCTA price and Place permit context"), fig, mo.md(str(place_summary)), mo.ui.table(places, page_size=20)])
    return fig_zcta, place_summary


@app.cell
def _(analysis_dir, cbsa_county_context, fig_context, fig_tract_map, fig_zcta, map_points, market_id, pd, places, tract_sensitivity, tract_summary, tract_table, tracts, zctas):
    # Persist the same inspectable artifacts as the headless review run. Each
    # export comes from the displayed data frame or figure, avoiding a hidden
    # alternate calculation path.
    output_dir = analysis_dir / "outputs" / f"market_{market_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    fig_context.savefig(output_dir / "cbsa_context_trends.png", dpi=160)
    fig_tract_map.savefig(output_dir / "tract_renter_affordability_map.png", dpi=160)
    fig_zcta.savefig(output_dir / "zcta_price_context.png", dpi=160)
    cbsa_county_context.to_csv(output_dir / "cbsa_county_context.csv", index=False)
    tracts.to_csv(output_dir / "tract_evidence.csv", index=False)
    map_points.drop(columns=["geom_wkb", "centroid"]).to_csv(output_dir / "tract_map_points.csv", index=False)
    tract_table.to_csv(output_dir / "tract_table.csv", index=False)
    pd.DataFrame([tract_summary]).to_csv(output_dir / "tract_summary.csv", index=False)
    tract_sensitivity.to_csv(output_dir / "tract_classification_sensitivity.csv", index=False)
    zctas.to_csv(output_dir / "zcta_price_context.csv", index=False)
    places.to_csv(output_dir / "place_context.csv", index=False)
    return output_dir,


if __name__ == "__main__":
    app.run()
