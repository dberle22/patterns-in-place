import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This notebook is analytical rather than exploratory. It reads Q2's
    # published candidate/proximity marts and Q1's housing surface; it never
    # recalculates job-center selection or alters a center rule with UI state.
    import json
    import os
    from pathlib import Path

    import duckdb
    import marimo as mo
    import numpy as np
    import pandas as pd
    import plotly.express as px
    from shapely import wkb

    return Path, duckdb, json, mo, np, os, pd, px, wkb


@app.cell
def _(Path, os, pd):
    analysis_dir = Path(__file__).resolve().parent
    repo_root = analysis_dir.parents[3]
    query_dir = analysis_dir / "queries"

    def resolve_db_path() -> str:
        """Use DB_PATH when supplied, otherwise use the repository-local DB."""

        return os.environ.get("DB_PATH", "").strip() or str(
            repo_root / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
        )

    def read_query(con, name: str, market_id: str | None = None) -> pd.DataFrame:
        """Read named analysis SQL without recreating joins in notebook cells."""

        query = (query_dir / name).read_text()
        if market_id is not None:
            query = query.replace("__CBSA_CODE__", market_id)
        return con.sql(query).df()

    return read_query, resolve_db_path


@app.cell
def _(duckdb, read_query, resolve_db_path):
    with duckdb.connect(resolve_db_path(), read_only=True) as _con:
        market_options_raw = read_query(_con, "q2_job_center_outcomes_cbsa_options.sql")
    return (market_options_raw,)


@app.cell
def _(market_options_raw, mo, os):
    market_options = {
        f"{row.cbsa_name} ({row.cbsa_code})": row.cbsa_code
        for row in market_options_raw.itertuples(index=False)
    }
    default_code = os.environ.get("Q2_CBSA_CODE", "40060").strip()
    default_label = next(
        (label for label, code in market_options.items() if code == default_code),
        next(iter(market_options)),
    )
    market_selector = mo.ui.dropdown(
        market_options,
        value=default_label,
        label="Market",
        full_width=True,
    )
    mo.vstack([
        mo.md(
            "# Explanation Q2 — Job-Center Outcomes\n"
            "This notebook analyzes 2024 tract housing/cost outcomes against the "
            "published 2023 job-center proximity surfaces. It does not choose job centers."
        ),
        market_selector,
    ])
    return (market_selector,)


@app.cell
def _(duckdb, market_selector, read_query, resolve_db_path):
    market_id = market_selector.value
    with duckdb.connect(resolve_db_path(), read_only=True) as _con:
        outcomes_raw = read_query(_con, "q2_job_center_outcomes_tracts.sql", market_id)
        center_earnings = read_query(_con, "q2_job_center_outcomes_earnings.sql", market_id)
        concentration_context = read_query(
            _con, "q2_job_concentration_market_context.sql", market_id
        )
    if outcomes_raw.empty:
        raise ValueError(f"No published Q2/Q1 outcomes rows are available for CBSA {market_id}.")
    return center_earnings, concentration_context, outcomes_raw


@app.cell
def _(mo):
    version_selector = mo.ui.dropdown(
        {
            "Recommended: core plus one-hop extension": "recommended_core_one_hop",
            "Sensitivity: strict core only": "strict_core",
            "Sensitivity: no market-share gate": "no_share_sensitivity",
        },
        value="Recommended: core plus one-hop extension",
        label="Published center version",
        full_width=True,
    )
    mo.vstack([
        mo.md(
            "## Center-version sensitivity\n"
            "Lead with the recommended construction. The strict-core and no-share "
            "versions are published sensitivity surfaces, not competing hidden defaults."
        ),
        version_selector,
    ])
    return (version_selector,)


@app.cell
def _(outcomes_raw, version_selector, wkb):
    selected_version = version_selector.value
    outcomes = outcomes_raw.loc[
        outcomes_raw.center_version == selected_version
    ].copy()
    outcomes["geometry"] = outcomes.geom_wkb.map(lambda value: wkb.loads(bytes(value)))
    outcomes["centroid_lon"] = outcomes.geometry.map(lambda shape: shape.centroid.x)
    outcomes["centroid_lat"] = outcomes.geometry.map(lambda shape: shape.centroid.y)
    if not outcomes.has_center_candidate.any():
        raise ValueError(
            "This CBSA has no candidate centers for the selected published version. "
            "Use a different sensitivity version or return to the method review."
        )
    return outcomes, selected_version


@app.cell
def _(concentration_context, mo, outcomes, selected_version):
    coverage_rows = []
    for _column, _label in {
        "annualized_median_rent": "Annualized median gross rent",
        "median_home_value": "Median home value",
        "housing_units": "Housing units",
        "median_hh_income": "Median household income",
        "pct_rent_burden_30plus": "Rent burden (30%+)",
    }.items():
        coverage_rows.append({
            "outcome": _label,
            "tract_rows": len(outcomes),
            "nonmissing_rows": int(outcomes[_column].notna().sum()),
            "coverage": outcomes[_column].notna().mean(),
        })
    center_count = int(outcomes.center_count.max())
    has_center = bool(outcomes.has_center_candidate.any())
    _context = concentration_context.iloc[0]
    mo.vstack([
        mo.md(
            "## Method and coverage\n"
            f"Selected version: `{selected_version}`. This market has "
            f"{center_count:,} candidate center tracts under that version. "
            "Distance is centroid-to-centroid Haversine miles from the published mart; "
            "it is not travel time or a 15-minute measure."
            if has_center
            else "## Method and coverage\nNo candidate center exists for this published version; distance-based results are unavailable."
        ),
        mo.md(
            "National-concentration context: "
            f"**{_context.cbsa_name}** has {_context.tract_count:,.0f} WAC tracts; "
            f"the top {_context.tract_share_to_50pct_jobs:.1%} hold half of 2023 workplace jobs "
            f"and the top {_context.tract_share_to_80pct_jobs:.1%} hold 80%."
        ),
        mo.ui.table(coverage_rows, page_size=10),
    ])
    return


@app.cell
def _(mo, outcomes, selected_version):
    # `center_role` describes the recommended construction, so select against
    # the version-specific published flag when the reader changes sensitivity.
    _center_flag = {
        "strict_core": "is_strict_core_seed",
        "recommended_core_one_hop": "is_recommended_center",
        "no_share_sensitivity": "is_no_share_sensitivity",
    }[selected_version]
    center_inventory = outcomes.loc[
        outcomes[_center_flag],
        [
            "tract_geoid", "center_role", "recommended_cluster_id", "jobs_total",
            "workers_total", "market_job_share", "jobs_to_workers_ratio",
        ],
    ].sort_values(["jobs_total", "tract_geoid"], ascending=[False, True])
    mo.vstack([
        mo.md("## Selected-version center inventory\nThis table is read from the published candidate mart; it is not recalculated here."),
        mo.ui.table(center_inventory, page_size=25),
    ])
    return


@app.cell
def _(json, mo, outcomes, px, selected_version):
    # The map makes the selected version's tract origins visible without
    # re-running the method notebook's gate logic.
    _map_center_flag = {
        "strict_core": "is_strict_core_seed",
        "recommended_core_one_hop": "is_recommended_center",
        "no_share_sensitivity": "is_no_share_sensitivity",
    }[selected_version]
    _center_map_rows = outcomes.copy()
    _center_map_rows["selected_center"] = _center_map_rows[_map_center_flag].map(
        {True: "Candidate center", False: "Not a candidate center"}
    )
    _center_geojson = json.loads(json.dumps({
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": row.tract_geoid,
                "properties": {},
                "geometry": row.geometry.__geo_interface__,
            }
            for row in _center_map_rows.itertuples(index=False)
        ],
    }))
    _center_figure = px.choropleth_map(
        _center_map_rows,
        geojson=_center_geojson,
        locations="tract_geoid",
        featureidkey="id",
        color="selected_center",
        color_discrete_map={
            "Candidate center": "#b2182b",
            "Not a candidate center": "#d9d9d9",
        },
        hover_name="tract_geoid",
        hover_data={
            "jobs_total": ":,.0f",
            "market_job_share": ".2%",
            "jobs_to_workers_ratio": ".2f",
        },
        center={"lat": _center_map_rows.centroid_lat.median(), "lon": _center_map_rows.centroid_lon.median()},
        zoom=8.1,
        opacity=0.72,
        map_style="carto-positron",
        labels={"selected_center": "Published status"},
    )
    _center_figure.update_layout(
        title="Published candidate-center tracts for the selected version",
        margin={"l": 0, "r": 0, "t": 42, "b": 0},
    )
    mo.vstack([mo.md("## Candidate-center map"), mo.ui.plotly(_center_figure)])
    return


@app.cell
def _(mo, np, outcomes, pd, px):
    # Fixed bins make all three center versions comparable. The final open bin
    # keeps distant tracts visible without implying equal-width geography.
    bin_edges = [-0.001, 1, 2, 3, 5, 10, np.inf]
    bin_labels = ["0–1", "1–2", "2–3", "3–5", "5–10", "10+"]
    binned = outcomes.loc[outcomes.has_center_candidate].copy()
    binned["distance_bin"] = pd.cut(
        binned.distance_to_nearest_center_miles,
        bins=bin_edges,
        labels=bin_labels,
    )
    outcomes_to_plot = {
        "annualized_median_rent": "Annualized median gross rent ($)",
        "median_home_value": "Median home value ($)",
        "housing_units": "Housing units",
    }
    figures = []
    for _plot_column, _plot_label in outcomes_to_plot.items():
        _summary = (
            binned.dropna(subset=[_plot_column])
            .groupby("distance_bin", observed=False)
            .agg(median_value=(_plot_column, "median"), tract_count=(_plot_column, "size"))
            .reset_index()
        )
        _curve_figure = px.line(
            _summary,
            x="distance_bin",
            y="median_value",
            markers=True,
            template="plotly_white",
            labels={"distance_bin": "Distance to nearest candidate job center (miles)", "median_value": _plot_label},
            title=_plot_label + " by job-center proximity bin",
            hover_data={"tract_count": True},
        )
        figures.append(mo.ui.plotly(_curve_figure))
    mo.vstack([
        mo.md("## Observed distance gradients\nEach point is the tract median within a fixed distance bin. Counts remain visible because missing ACS values differ by outcome."),
        *figures,
    ])
    return


@app.cell
def _(np, outcomes, pd):
    # A disclosed log-outcome versus distance model is descriptive only. It does
    # not control for sorting, tenure, land use, or other causal confounders.
    model_rows = []
    model_data: dict[str, pd.DataFrame] = {}
    for _model_column, _model_label in {
        "annualized_median_rent": "Annualized median gross rent",
        "median_home_value": "Median home value",
        "housing_units": "Housing units",
    }.items():
        frame = outcomes.loc[
            outcomes.has_center_candidate
            & outcomes.distance_to_nearest_center_miles.notna()
            & outcomes[_model_column].gt(0),
            ["tract_geoid", "distance_to_nearest_center_miles", _model_column, "geometry"],
        ].copy()
        if len(frame) < 2:
            # A tiny eligible market cannot support even this descriptive fit;
            # retain an explicit no-result row rather than implying a gradient.
            model_data[_model_column] = frame.assign(log_residual=np.nan)
            model_rows.append({
                "outcome": _model_label,
                "model": "Insufficient complete cases for descriptive model",
                "tracts": len(frame),
                "distance_coefficient": np.nan,
                "r_squared": np.nan,
            })
            continue
        x = frame.distance_to_nearest_center_miles.to_numpy()
        y = np.log(frame[_model_column].to_numpy())
        design = np.column_stack([np.ones(len(frame)), x])
        coefficients, _, _, _ = np.linalg.lstsq(design, y, rcond=None)
        fitted = design @ coefficients
        residual = y - fitted
        total_sum_squares = ((y - y.mean()) ** 2).sum()
        r_squared = 1 - (residual**2).sum() / total_sum_squares if total_sum_squares else np.nan
        frame["log_residual"] = residual
        model_data[_model_column] = frame
        model_rows.append({
            "outcome": _model_label,
            "model": "log(outcome) = intercept + distance miles",
            "tracts": len(frame),
            "distance_coefficient": coefficients[1],
            "r_squared": r_squared,
        })
    return model_data, model_rows


@app.cell
def _(mo, model_rows):
    mo.vstack([
        mo.md("## Descriptive distance models\nThese cross-sectional models describe association only; they are not causal housing-price estimates."),
        mo.ui.table(model_rows, page_size=10),
    ])
    return


@app.cell
def _(json, model_data, mo, outcomes, px):
    residual_outcome_selector = mo.ui.dropdown(
        {
            "Median home value": "median_home_value",
            "Annualized median gross rent": "annualized_median_rent",
            "Housing units": "housing_units",
        },
        value="Median home value",
        label="Residual-map outcome",
        full_width=True,
    )
    mo.vstack([mo.md("## Residual map"), residual_outcome_selector])
    return residual_outcome_selector,


@app.cell
def _(json, mo, model_data, outcomes, px, residual_outcome_selector):
    _residual_outcome = residual_outcome_selector.value
    _residuals = model_data[_residual_outcome][["tract_geoid", "log_residual"]]
    _residual_map_rows = outcomes.merge(_residuals, on="tract_geoid", how="left")
    _residual_geojson = json.loads(json.dumps({
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "id": row.tract_geoid,
                "properties": {},
                "geometry": row.geometry.__geo_interface__,
            }
            for row in _residual_map_rows.itertuples(index=False)
        ],
    }))
    _residual_figure = px.choropleth_map(
        _residual_map_rows,
        geojson=_residual_geojson,
        locations="tract_geoid",
        featureidkey="id",
        color="log_residual",
        color_continuous_scale="RdBu",
        color_continuous_midpoint=0,
        hover_name="tract_geoid",
        hover_data={
            "distance_to_nearest_center_miles": ".2f",
            "jobs_total": ":,.0f",
            "market_job_share": ".2%",
            "jobs_to_workers_ratio": ".2f",
            "log_residual": ".3f",
        },
        center={"lat": _residual_map_rows.centroid_lat.median(), "lon": _residual_map_rows.centroid_lon.median()},
        zoom=8.1,
        opacity=0.78,
        map_style="carto-positron",
        labels={"log_residual": "Log-outcome residual"},
    )
    _residual_figure.update_layout(
        title="Residuals after the descriptive distance model",
        margin={"l": 0, "r": 0, "t": 42, "b": 0},
    )
    mo.ui.plotly(_residual_figure)
    return


@app.cell
def _(mo, outcomes, pd):
    affordability = outcomes.loc[outcomes.has_center_candidate].copy()
    affordability["distance_band"] = pd.cut(
        affordability.distance_to_nearest_center_miles,
        bins=[-0.001, 2, 5, 10, float("inf")],
        labels=["0–2", "2–5", "5–10", "10+"],
    )
    affordability_summary = (
        affordability.groupby("distance_band", observed=False)
        .agg(
            tract_count=("tract_geoid", "size"),
            median_household_income=("median_hh_income", "median"),
            median_rent_to_all_hh_income_proxy=("median_rent_to_all_hh_income_proxy", "median"),
            median_rent_burden_30plus=("pct_rent_burden_30plus", "median"),
        )
        .reset_index()
    )
    mo.vstack([
        mo.md("## Resident affordability context\nHousehold income, the median-rent-to-all-household-income price proxy, and renter burden remain resident measures. They are not workplace earnings or a worker-household match."),
        mo.ui.table(affordability_summary, page_size=10),
    ])
    return


@app.cell
def _(center_earnings, mo, version_selector):
    earnings = center_earnings.loc[
        center_earnings.center_version == version_selector.value
    ]
    mo.vstack([
        mo.md("## Job-center earnings-band context\nLODES bands describe workers at the selected workplace tracts. They are shown beside—but never blended with—resident household affordability measures."),
        mo.ui.table(earnings, page_size=5),
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ## Readout and handoff

    Compare the recommended result with the two sensitivity versions before
    interpreting a gradient. A stable result may carry forward as Q2 evidence;
    a materially changing result is itself a method finding. This notebook does
    not establish routed travel time, commute behavior, or a causal effect of
    job-center proximity on housing outcomes.
    """)
    return


if __name__ == "__main__":
    app.run()
