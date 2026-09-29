import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # Epic 2 is a read-only method-discovery surface. It profiles workplace-job
    # concentration and does not select centers, districts, or market rankings.
    import os
    from pathlib import Path

    import duckdb
    import marimo as mo
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go

    return Path, duckdb, go, mo, np, os, pd, px


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

    def read_query(con, name: str) -> pd.DataFrame:
        """Read a named, analysis-owned SQL surface without duplicating joins."""

        return con.sql((query_dir / name).read_text()).df()

    return read_query, resolve_db_path


@app.cell
def _(duckdb, read_query, resolve_db_path):
    # Load the national tract surface once. The coverage reader remains separate
    # so the notebook can state exclusions before calculating any concentration.
    with duckdb.connect(resolve_db_path(), read_only=True) as con:
        concentration_tracts_raw = read_query(con, "q2_job_concentration_tracts.sql")
        concentration_coverage = read_query(con, "q2_job_concentration_coverage.sql")
    return concentration_coverage, concentration_tracts_raw


@app.cell
def _(mo):
    mo.md("""
    # Explanation Q2 — National Employment Concentration

    This notebook asks how workplace jobs are distributed among tracts within
    each CBSA. It is a method-discovery surface, not a market ranking, a
    commute-flow analysis, or a center-selection rule.
    """)
    return


@app.cell
def _(mo):
    # This threshold is visible because the 2023 WAC release has known missing
    # coverage. It governs the national cohort, not an employment-center cutoff.
    coverage_threshold = mo.ui.slider(
        start=0.80,
        stop=1.00,
        step=0.01,
        value=0.95,
        label="Minimum WAC tract coverage against governed CBSA tracts",
        full_width=False,
    )
    mo.vstack([
        mo.md(
            "## Coverage and cohort\n"
            "A CBSA enters the exploratory cohort only when its 2023 WAC tract "
            "coverage meets this visible threshold. RAC is shown separately because "
            "it is resident-worker context, not a substitute for WAC coverage."
        ),
        coverage_threshold,
    ])
    return (coverage_threshold,)


@app.cell
def _(concentration_coverage, concentration_tracts_raw, coverage_threshold, np, pd):
    coverage = concentration_coverage.copy()
    coverage["eligible"] = coverage.wac_geometry_coverage >= coverage_threshold.value
    eligible_codes = set(coverage.loc[coverage.eligible, "cbsa_code"])
    concentration_tracts = concentration_tracts_raw.loc[
        concentration_tracts_raw.cbsa_code.isin(eligible_codes)
    ].copy()
    concentration_tracts = concentration_tracts.sort_values(
        ["cbsa_code", "jobs_total", "tract_geoid"],
        ascending=[True, False, True],
        kind="mergesort",
    )

    # All shares below are within-CBSA shares. Job share is the Pareto input;
    # worker share is intentionally retained as a distinct residence-side lens.
    concentration_tracts["tract_rank"] = concentration_tracts.groupby("cbsa_code").cumcount() + 1
    concentration_tracts["market_tract_count"] = concentration_tracts.groupby("cbsa_code")["tract_geoid"].transform("size")
    concentration_tracts["market_jobs_total"] = concentration_tracts.groupby("cbsa_code")["jobs_total"].transform("sum")
    concentration_tracts["market_workers_total"] = concentration_tracts.groupby("cbsa_code")["workers_total"].transform("sum")
    concentration_tracts["tract_job_share"] = concentration_tracts.jobs_total / concentration_tracts.market_jobs_total
    concentration_tracts["cumulative_job_share"] = concentration_tracts.groupby("cbsa_code")["tract_job_share"].cumsum()
    concentration_tracts["cumulative_tract_share"] = concentration_tracts.tract_rank / concentration_tracts.market_tract_count
    concentration_tracts["tract_worker_share"] = concentration_tracts.workers_total / concentration_tracts.market_workers_total.where(concentration_tracts.market_workers_total > 0)
    concentration_tracts["jobs_to_workers_ratio"] = concentration_tracts.jobs_total / concentration_tracts.workers_total.where(concentration_tracts.workers_total > 0)
    concentration_tracts["job_share_to_worker_share"] = concentration_tracts.tract_job_share / concentration_tracts.tract_worker_share.where(concentration_tracts.tract_worker_share > 0)

    def summarize_market(group: pd.DataFrame) -> pd.Series:
        def cutoff_row(cutoff: float) -> pd.Series:
            return group.loc[group.cumulative_job_share >= cutoff].iloc[0]

        cutoff_50 = cutoff_row(0.50)
        cutoff_80 = cutoff_row(0.80)
        top_20_count = max(1, int(np.ceil(group.market_tract_count.iloc[0] * 0.20)))
        top_20_job_share = group.loc[group.tract_rank <= top_20_count, "tract_job_share"].sum()
        return pd.Series({
            "cbsa_name": group.cbsa_name.iloc[0],
            "tract_count": group.market_tract_count.iloc[0],
            "workplace_jobs": group.market_jobs_total.iloc[0],
            "resident_workers": group.market_workers_total.iloc[0],
            "tract_share_to_50pct_jobs": cutoff_50.cumulative_tract_share,
            "tracts_to_50pct_jobs": cutoff_50.tract_rank,
            "tract_share_to_80pct_jobs": cutoff_80.cumulative_tract_share,
            "tracts_to_80pct_jobs": cutoff_80.tract_rank,
            "top_20pct_tract_job_share": top_20_job_share,
        })

    market_concentration = (
        concentration_tracts.groupby("cbsa_code", group_keys=False)
        .apply(summarize_market, include_groups=False)
        .reset_index()
        .merge(
            coverage[["cbsa_code", "wac_geometry_coverage", "rac_geometry_coverage", "eligible"]],
            on="cbsa_code",
            how="left",
        )
    )
    coverage_summary = pd.DataFrame([{
        "WAC vintage": int(concentration_tracts.wac_year.max()),
        "CBSAs in coverage reader": len(coverage),
        "eligible CBSAs": int(coverage.eligible.sum()),
        "excluded CBSAs": int((~coverage.eligible).sum()),
        "eligible tract rows": len(concentration_tracts),
        "coverage threshold": coverage_threshold.value,
    }])
    return concentration_tracts, coverage, coverage_summary, market_concentration


@app.cell
def _(coverage, coverage_summary, mo):
    excluded_coverage = coverage.loc[~coverage.eligible, [
        "cbsa_code", "cbsa_name", "governed_tract_count", "wac_tract_count",
        "rac_tract_count", "wac_geometry_coverage", "rac_geometry_coverage",
    ]].sort_values("wac_geometry_coverage")
    mo.vstack([
        mo.ui.table(coverage_summary, page_size=5),
        mo.md("### Excluded CBSAs\nThese rows are excluded from the concentration cohort at the active coverage threshold; they are not zero-job markets."),
        mo.ui.table(excluded_coverage, page_size=20),
    ])
    return (excluded_coverage,)


@app.cell
def _(market_concentration, mo):
    market_options = {
        f"{row.cbsa_name} ({row.cbsa_code})": row.cbsa_code
        for row in market_concentration.sort_values("cbsa_name").itertuples(index=False)
    }
    richmond_label = next(
        (label for label, code in market_options.items() if code == "40060"),
        next(iter(market_options)),
    )
    contrast_code = market_concentration.sort_values("tract_share_to_50pct_jobs").iloc[0].cbsa_code
    contrast_label = next(label for label, code in market_options.items() if code == contrast_code)
    pareto_market = mo.ui.dropdown(market_options, value=richmond_label, label="Primary market")
    contrast_market = mo.ui.dropdown(market_options, value=contrast_label, label="Comparison market")
    mo.vstack([
        mo.md("## Pareto concentration\nA curve reaches 50% or 80% where the cumulative job-share line crosses that horizontal reference. The pooled eligible-CBSA reference ranks every tract in the active national cohort together; it is not an average-market curve and is not population weighted. The x-axis is the cumulative share of ranked tracts, not geographic distance."),
        mo.hstack([pareto_market, contrast_market], justify="start"),
    ])
    return contrast_market, pareto_market


@app.cell
def _(concentration_tracts, contrast_market, market_concentration, mo, pareto_market, pd, px):
    selected_codes = {pareto_market.value, contrast_market.value}
    pareto_rows = concentration_tracts.loc[concentration_tracts.cbsa_code.isin(selected_codes)].copy()
    pareto_rows["market_label"] = pareto_rows.cbsa_name + " (" + pareto_rows.cbsa_code + ")"
    national_reference = concentration_tracts.sort_values(
        ["jobs_total", "tract_geoid"], ascending=[False, True], kind="mergesort"
    ).copy()
    national_reference["cumulative_tract_share"] = (
        national_reference.reset_index(drop=True).index + 1
    ) / len(national_reference)
    national_reference["cumulative_job_share"] = (
        national_reference.jobs_total.cumsum() / national_reference.jobs_total.sum()
    )
    national_reference["market_label"] = "Pooled eligible-CBSA tract reference"
    pareto_rows = pd.concat([pareto_rows, national_reference], ignore_index=True)
    pareto_figure = px.line(
        pareto_rows,
        x="cumulative_tract_share",
        y="cumulative_job_share",
        color="market_label",
        labels={
            "cumulative_tract_share": "Cumulative share of tracts, ranked by workplace jobs",
            "cumulative_job_share": "Cumulative share of workplace jobs",
            "market_label": "Market",
        },
        template="plotly_white",
    )
    for cutoff in (0.50, 0.80):
        pareto_figure.add_hline(y=cutoff, line_dash="dot", line_color="#555555", annotation_text=f"{int(cutoff * 100)}% of jobs")
    pareto_figure.update_layout(title="Workplace-job Pareto curves", yaxis_tickformat=".0%", xaxis_tickformat=".0%")
    selected_summary = market_concentration.loc[
        market_concentration.cbsa_code.isin(selected_codes),
        [
            "cbsa_name", "cbsa_code", "tract_count", "workplace_jobs",
            "tract_share_to_50pct_jobs", "tract_share_to_80pct_jobs",
            "top_20pct_tract_job_share", "wac_geometry_coverage",
        ],
    ].sort_values("cbsa_name")
    mo.vstack([mo.ui.plotly(pareto_figure), mo.ui.table(selected_summary, page_size=5)])
    return pareto_figure, selected_summary


@app.cell
def _(concentration_tracts, mo):
    top_tract_limit = mo.ui.slider(
        start=10,
        stop=100,
        step=10,
        value=30,
        label="National top tracts to display",
        full_width=False,
    )
    mo.vstack([
        mo.md("## National top-tract inventory\nThis is an inspectable input table, not a market ranking. It shows where the largest observed workplace-job counts sit and how their density and resident-worker context differ."),
        top_tract_limit,
    ])
    return (top_tract_limit,)


@app.cell
def _(concentration_tracts, mo, top_tract_limit):
    top_tracts = concentration_tracts.nlargest(top_tract_limit.value, "jobs_total")[[
        "cbsa_name", "cbsa_code", "tract_geoid", "jobs_total", "workers_total",
        "jobs_per_sqmi", "jobs_to_workers_ratio", "tract_job_share",
        "tract_worker_share", "job_share_to_worker_share",
    ]]
    mo.ui.table(top_tracts, page_size=top_tract_limit.value)
    return (top_tracts,)


@app.cell
def _(market_concentration, mo, px):
    # These distributions describe market concentration without ordering markets
    # into a league table. Each observation is one coverage-eligible CBSA.
    distribution_columns = {
        "Tract share needed for 50% of jobs": "tract_share_to_50pct_jobs",
        "Tract share needed for 80% of jobs": "tract_share_to_80pct_jobs",
        "Job share held by top 20% of tracts": "top_20pct_tract_job_share",
    }
    distribution_selector = mo.ui.dropdown(
        distribution_columns,
        value="Tract share needed for 50% of jobs",
        label="National concentration distribution",
    )
    mo.vstack([mo.md("## National concentration distributions"), distribution_selector])
    return distribution_columns, distribution_selector


@app.cell
def _(distribution_columns, distribution_selector, market_concentration, mo, px):
    distribution_column = distribution_selector.value
    distribution_label = next(
        label for label, column in distribution_columns.items() if column == distribution_column
    )
    distribution_figure = px.histogram(
        market_concentration,
        x=distribution_column,
        nbins=35,
        template="plotly_white",
        labels={distribution_column: distribution_label, "count": "CBSAs"},
    )
    distribution_figure.update_layout(title=distribution_label, xaxis_tickformat=".0%")
    mo.ui.plotly(distribution_figure)
    return distribution_figure,


@app.cell
def _(concentration_tracts, mo):
    maximum_slider = min(10000, int(concentration_tracts.jobs_total.max()))
    minimum_jobs_for_ratio = mo.ui.slider(
        start=0,
        stop=maximum_slider,
        step=100,
        value=min(250, maximum_slider),
        label="Minimum tract jobs for ratio and scatter views",
        full_width=False,
    )
    tract_metric_distribution = mo.ui.dropdown(
        {
            "Workplace jobs": "jobs_total",
            "Workplace jobs per square mile": "jobs_per_sqmi",
            "Jobs per resident worker": "jobs_to_workers_ratio",
        },
        value="Workplace jobs",
        label="Tract metric distribution",
    )
    mo.vstack([
        mo.md(
            "## Tract metric behavior\n"
            "This visible job-mass screen prevents small resident-worker denominators "
            "from dominating jobs-to-workers and job-share-to-worker-share views."
        ),
        mo.hstack([minimum_jobs_for_ratio, tract_metric_distribution], justify="start"),
    ])
    return minimum_jobs_for_ratio, tract_metric_distribution


@app.cell
def _(concentration_tracts, minimum_jobs_for_ratio):
    ratio_tracts = concentration_tracts.loc[
        (concentration_tracts.jobs_total >= minimum_jobs_for_ratio.value)
        & concentration_tracts.jobs_per_sqmi.gt(0)
        & concentration_tracts.jobs_to_workers_ratio.gt(0)
        & concentration_tracts.tract_worker_share.gt(0)
        & concentration_tracts.job_share_to_worker_share.gt(0)
    ].copy()
    # Plotting a deterministic sample keeps interactive browser payloads usable
    # while the distribution and market summaries retain the full cohort.
    scatter_tracts = ratio_tracts.sample(n=min(10000, len(ratio_tracts)), random_state=20260914)
    return ratio_tracts, scatter_tracts


@app.cell
def _(mo, np, pd, px, ratio_tracts, tract_metric_distribution):
    tract_distribution_column = tract_metric_distribution.value
    tract_distribution_label = {
        "jobs_total": "Workplace jobs",
        "jobs_per_sqmi": "Workplace jobs per square mile",
        "jobs_to_workers_ratio": "Jobs per resident worker",
    }[tract_distribution_column]
    tract_metric_values = ratio_tracts[tract_distribution_column].dropna()
    raw_bin_counts, raw_bin_edges = np.histogram(tract_metric_values, bins=60)
    raw_distribution_bins = pd.DataFrame({
        "bin_midpoint": (raw_bin_edges[:-1] + raw_bin_edges[1:]) / 2,
        "tract_count": raw_bin_counts,
    }).loc[lambda frame: frame.tract_count > 0]
    raw_tract_distribution_figure = px.bar(
        raw_distribution_bins,
        x="bin_midpoint",
        y="tract_count",
        template="plotly_white",
        labels={"bin_midpoint": tract_distribution_label, "tract_count": "Tracts"},
        title=f"Distribution of {tract_distribution_label.lower()} (raw scale)",
    )
    log_bin_counts, log_bin_edges = np.histogram(np.log10(tract_metric_values), bins=60)
    tract_distribution_bins = pd.DataFrame({
        "log10_bin_midpoint": (log_bin_edges[:-1] + log_bin_edges[1:]) / 2,
        "tract_count": log_bin_counts,
    }).loc[lambda frame: frame.tract_count > 0]
    # Plotly's direct log-x histogram can render an empty canvas in the current
    # Marimo/Plotly combination. Explicit log bins keep the heavy-tailed tract
    # distributions visible and make the transformation inspectable.
    tract_distribution_figure = px.bar(
        tract_distribution_bins,
        x="log10_bin_midpoint",
        y="tract_count",
        template="plotly_white",
        labels={"log10_bin_midpoint": f"log10({tract_distribution_label.lower()})", "tract_count": "Tracts"},
        title=f"Distribution of {tract_distribution_label.lower()} (log-binned)",
    )
    mo.vstack([
        mo.md("### Metric distributions\nRaw scale retains the absolute tail; log bins make the spread among lower-valued tracts visible."),
        mo.ui.plotly(raw_tract_distribution_figure),
        mo.ui.plotly(tract_distribution_figure),
    ])
    return raw_tract_distribution_figure, tract_distribution_figure


@app.cell
def _(go, mo, ratio_tracts):
    # px.box serializes every tract value into the browser even when points are
    # hidden. Build standard Tukey summaries from the full filtered cohort so
    # the two interactive figures stay small without turning into a sample.
    metric_labels = {
        "jobs_total": "Workplace jobs",
        "jobs_per_sqmi": "Workplace jobs per square mile",
        "jobs_to_workers_ratio": "Jobs per resident worker",
    }

    def tukey_summary(values):
        q1 = values.quantile(0.25)
        median = values.quantile(0.50)
        q3 = values.quantile(0.75)
        iqr = q3 - q1
        inlier_values = values.loc[
            values.between(q1 - 1.5 * iqr, q3 + 1.5 * iqr)
        ]
        return {
            "q1": q1,
            "median": median,
            "q3": q3,
            "lower_fence": inlier_values.min(),
            "upper_fence": inlier_values.max(),
        }

    box_summaries = {
        metric: tukey_summary(ratio_tracts[metric].dropna())
        for metric in metric_labels
    }

    def make_summary_boxplot(log_scale: bool):
        figure = go.Figure()
        for metric, label in metric_labels.items():
            summary = box_summaries[metric]
            figure.add_trace(go.Box(
                name=label,
                q1=[summary["q1"]],
                median=[summary["median"]],
                q3=[summary["q3"]],
                lowerfence=[summary["lower_fence"]],
                upperfence=[summary["upper_fence"]],
                boxpoints=False,
            ))
        figure.update_layout(
            template="plotly_white",
            title="Spread of tract employment metrics" + (" (log scale)" if log_scale else " (raw scale)"),
            yaxis_title="Value",
            showlegend=False,
        )
        if log_scale:
            figure.update_yaxes(type="log")
        return figure

    raw_tract_boxplot_figure = make_summary_boxplot(log_scale=False)
    log_tract_boxplot_figure = make_summary_boxplot(log_scale=True)
    mo.vstack([
        mo.md("### Metric boxplots\nThese exact Tukey summaries use the full filtered cohort but transmit only quartiles and whiskers, not every tract value. Raw scale retains tail magnitude; log scale makes the central spread visible across the three distinct units."),
        mo.ui.plotly(raw_tract_boxplot_figure),
        mo.ui.plotly(log_tract_boxplot_figure),
    ])
    return raw_tract_boxplot_figure, log_tract_boxplot_figure


@app.cell
def _(mo, px, scatter_tracts):
    jobs_density_figure = px.scatter(
        scatter_tracts,
        x="jobs_total",
        y="jobs_per_sqmi",
        log_x=True,
        log_y=True,
        opacity=0.35,
        hover_data={"cbsa_name": True, "tract_geoid": True, "workers_total": ":,.0f"},
        labels={"jobs_total": "Workplace jobs", "jobs_per_sqmi": "Workplace jobs per square mile"},
        title="Tract job mass and density",
        template="plotly_white",
    )
    mo.vstack([
        mo.md("### Job mass and density\nA deterministic sample of at most 10,000 tracts keeps this interactive view within Marimo's output limit."),
        mo.ui.plotly(jobs_density_figure),
    ])
    return jobs_density_figure,


@app.cell
def _(mo, px, scatter_tracts):
    jobs_workers_figure = px.scatter(
        scatter_tracts,
        x="jobs_total",
        y="jobs_to_workers_ratio",
        log_x=True,
        log_y=True,
        opacity=0.35,
        hover_data={"cbsa_name": True, "tract_geoid": True, "workers_total": ":,.0f"},
        labels={"jobs_total": "Workplace jobs", "jobs_to_workers_ratio": "Jobs per resident worker"},
        title="Tract job mass and workplace-heavy ratio",
        template="plotly_white",
    )
    mo.vstack([
        mo.md("### Job mass and jobs-to-workers\nThe active minimum-job screen remains in effect before this ratio is plotted."),
        mo.ui.plotly(jobs_workers_figure),
    ])
    return jobs_workers_figure,


@app.cell
def _(mo, px, ratio_tracts, scatter_tracts):
    share_comparison_figure = px.scatter(
        scatter_tracts,
        x="tract_worker_share",
        y="tract_job_share",
        log_x=True,
        log_y=True,
        opacity=0.35,
        hover_data={"cbsa_name": True, "tract_geoid": True, "jobs_total": ":,.0f"},
        labels={"tract_worker_share": "Tract share of resident workers", "tract_job_share": "Tract share of workplace jobs"},
        title="Workplace-job share versus resident-worker share",
        template="plotly_white",
    )
    share_comparison_figure.add_shape(type="line", x0=1e-5, y0=1e-5, x1=1, y1=1, line={"dash": "dot", "color": "#555555"})
    ratio_summary = {
        "tracts passing active job screen": len(ratio_tracts),
        "points rendered in scatters": len(scatter_tracts),
        "note": "Each point is a tract; the job and worker shares are calculated within its CBSA.",
    }
    mo.vstack([
        mo.md("### Job share versus resident-worker share\nBoth shares are calculated within the tract's CBSA. The dotted diagonal marks equal job and worker shares."),
        mo.ui.plotly(share_comparison_figure),
        mo.md(str(ratio_summary)),
    ])
    return share_comparison_figure,


@app.cell
def _(mo):
    mo.md("""
    ## Readout for the market-method review

    Use the Pareto curve, concentration cutoffs, and metric relationships to
    select contrasting local patterns worth mapping in Epic 3. Do not select a
    center threshold, combine tracts into a zone, infer a corridor, or infer
    worker origins here. The last requires LODES OD, not RAC.
    """)
    return


if __name__ == "__main__":
    app.run()
