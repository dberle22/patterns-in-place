import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This notebook is deliberately a thin, read-only consumer of the promoted
    # framework marts and governed benchmarking API.  It does not recreate
    # scores, comparison memberships, or benchmark percentiles locally.
    import os
    from pathlib import Path

    import altair as alt
    import duckdb
    import marimo as mo
    import pandas as pd
    from pip_benchmarking import (
        benchmark_metric_bundle,
        get_target_metric_surface,
        list_comparison_sets,
    )

    return (
        Path,
        alt,
        benchmark_metric_bundle,
        duckdb,
        get_target_metric_surface,
        list_comparison_sets,
        mo,
        os,
        pd,
    )


@app.cell
def _(Path):
    # Resolve every local resource from this file so Marimo works from VS Code,
    # `marimo edit`, and any shell working directory without local path edits.
    analysis_dir = Path(__file__).resolve().parent
    repo_root = analysis_dir.parents[3]
    query_paths = {
        "identity": analysis_dir / "queries" / "profile_identity.sql",
        "percentiles": analysis_dir / "queries" / "profile_percentiles.sql",
        "topic_scores": analysis_dir / "queries" / "profile_topic_scores.sql",
        "raw_kpis": analysis_dir / "queries" / "profile_raw_kpis.sql",
    }
    return analysis_dir, query_paths, repo_root


@app.cell
def _(os, repo_root):
    # Keep DB_PATH resolution consistent with the headless QA runner while
    # never writing a local absolute path into the notebook or project docs.
    def load_db_path_notebook() -> str:
        db_path = os.environ.get("DB_PATH", "").strip()
        if db_path:
            return db_path

        renviron_path = repo_root / ".Renviron"
        if renviron_path.exists():
            for raw_line in renviron_path.read_text().splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key.strip() == "DB_PATH":
                    return value.strip()

        raise RuntimeError("DB_PATH is not set and could not be found in .Renviron.")

    return (load_db_path_notebook,)


@app.cell
def _(duckdb, load_db_path_notebook):
    # Read-only access is intentional: this exploratory notebook must leave
    # DuckDB as the canonical data layer and never materialize a profile mart.
    def query_profile_surface(query_path, cbsa_code):
        sql = query_path.read_text().replace("'__CBSA_CODE__'", f"'{cbsa_code}'")
        with duckdb.connect(load_db_path_notebook(), read_only=True) as query_con:
            return query_con.sql(sql).df()

    def load_cbsa_options():
        with duckdb.connect(load_db_path_notebook(), read_only=True) as options_con:
            options_df = options_con.sql(
                """
                SELECT cbsa_code, cbsa_name
                FROM mart_intelligence.intelligence_cross_frame
                ORDER BY cbsa_name
                """
            ).df()
        return {
            f"{row.cbsa_name} ({row.cbsa_code})": row.cbsa_code
            for row in options_df.itertuples(index=False)
        }

    return load_cbsa_options, query_profile_surface


@app.cell
def _(mo):
    mo.md("""
    # Position Profile

    Explore the Intelligence Framework's current profile for one of the
    promoted 396-CBSA framework markets. This is an inspection surface: it
    helps trace labels, modeled scores, raw KPI candidates, source vintages,
    and governed benchmarks before any Act 1 issue selection.

    It does not choose a final fingerprint, assemble an issue, or establish
    publication claims. Framework scores and labels remain upstream modeled
    outputs, and public use remains subject to the program's similarity and
    universe review.
    """)
    return


@app.cell
def _(load_cbsa_options):
    cbsa_options = load_cbsa_options()
    return (cbsa_options,)


@app.cell
def _(cbsa_options, mo):
    default_cbsa_label = next(
        (label for label, code in cbsa_options.items() if code == "40060"),
        next(iter(cbsa_options)),
    )
    cbsa_selector = mo.ui.dropdown(
        options=cbsa_options,
        value=default_cbsa_label,
        label="Target CBSA",
        searchable=True,
        full_width=True,
    )
    cbsa_selector
    return (cbsa_selector,)


@app.cell
def _(cbsa_selector, query_paths, query_profile_surface):
    selected_cbsa_code = cbsa_selector.value
    identity_df = query_profile_surface(query_paths["identity"], selected_cbsa_code)
    percentiles_df = query_profile_surface(query_paths["percentiles"], selected_cbsa_code)
    topic_scores_df = query_profile_surface(query_paths["topic_scores"], selected_cbsa_code)
    raw_kpis_df = query_profile_surface(query_paths["raw_kpis"], selected_cbsa_code)
    return identity_df, percentiles_df, raw_kpis_df, selected_cbsa_code, topic_scores_df


@app.cell
def _(duckdb, list_comparison_sets, load_db_path_notebook, selected_cbsa_code):
    # Comparison-set discovery and metric availability come from the shared
    # package rather than local SQL, keeping registry behavior governed.
    with duckdb.connect(load_db_path_notebook(), read_only=True) as benchmark_setup_con:
        comparison_sets_df = list_comparison_sets(benchmark_setup_con, selected_cbsa_code)
        target_metric_surface_df = get_target_metric_surface(
            benchmark_setup_con, selected_cbsa_code
        )
    return comparison_sets_df, target_metric_surface_df


@app.cell
def _(comparison_sets_df, mo):
    comparison_set_options = {
        row.comparison_label: row.comparison_set_type
        for row in comparison_sets_df.itertuples(index=False)
    }
    comparison_set_default = next(
        (
            label
            for label, comparison_set_type in comparison_set_options.items()
            if comparison_set_type == "national"
        ),
        next(iter(comparison_set_options), None),
    )
    comparison_set_selector = mo.ui.dropdown(
        options=comparison_set_options,
        value=comparison_set_default,
        label="Benchmark comparison set",
        searchable=True,
        full_width=True,
    )
    comparison_set_selector
    return comparison_set_selector, comparison_set_options


@app.cell
def _(mo, raw_kpis_df, target_metric_surface_df):
    # The raw candidate pool is the governed default. Intersection with the
    # benchmark surface prevents calls for candidate IDs not currently exposed
    # by mart_benchmarking for this selected CBSA.
    benchmarkable_ids = set(target_metric_surface_df["metric_id"].dropna())
    metric_catalog_df = (
        raw_kpis_df.loc[raw_kpis_df["metric_id"].isin(benchmarkable_ids)]
        .drop_duplicates(subset=["metric_id"])
        .sort_values(["frame_id", "metric_label"])
    )
    fingerprint_metric_options = {
        f"{row.frame_id.replace('_', ' ').title()} | {row.metric_label} ({row.metric_id})": row.metric_id
        for row in metric_catalog_df.itertuples(index=False)
    }
    fingerprint_metric_selector = mo.ui.multiselect(
        options=fingerprint_metric_options,
        value=list(fingerprint_metric_options),
        label="Fingerprint KPI candidates (optional smaller comparison view)",
        full_width=True,
    )
    fingerprint_metric_selector
    return fingerprint_metric_options, fingerprint_metric_selector, metric_catalog_df


@app.cell
def _(comparison_sets_df, identity_df, mo, pd, percentiles_df, raw_kpis_df, topic_scores_df):
    source_years = pd.to_numeric(raw_kpis_df["source_year"], errors="coerce")
    run_summary_df = pd.DataFrame(
        [
            {"check": "Identity rows", "value": len(identity_df)},
            {"check": "Frame percentile rows", "value": len(percentiles_df)},
            {"check": "Topic/subject rows", "value": len(topic_scores_df)},
            {"check": "Raw KPI rows", "value": len(raw_kpis_df)},
            {"check": "Available comparison sets", "value": len(comparison_sets_df)},
            {
                "check": "Raw KPI source-year range",
                "value": (
                    f"{int(source_years.min())}–{int(source_years.max())}"
                    if source_years.notna().any()
                    else "No source years available"
                ),
            },
        ]
    )
    mo.vstack([mo.md("## Run summary"), mo.ui.table(run_summary_df, selection=None)])
    return (run_summary_df,)


@app.cell
def _(identity_df, mo, selected_cbsa_code):
    if len(identity_df) != 1:
        identity_section = mo.callout(
            mo.md(
                f"Expected one identity row for `{selected_cbsa_code}`; found `{len(identity_df)}`."
            ),
            kind="warn",
        )
    else:
        identity_display_df = identity_df.T.reset_index()
        identity_display_df.columns = ["identity field", "value"]
        identity_section = mo.vstack(
            [mo.md("## Identity"), mo.ui.table(identity_display_df, selection=None)]
        )
    identity_section
    return


@app.cell
def _(alt, percentiles_df):
    percentile_chart_df = percentiles_df.copy()
    percentile_chart_df["frame_label"] = (
        percentile_chart_df["frame_id"].str.replace("_", " ").str.title()
    )
    frame_position_fig = (
        alt.Chart(percentile_chart_df, title="Frame position (upstream percentile ranks)")
        .mark_bar()
        .encode(
            x=alt.X("frame_label:N", title=None, sort=None),
            y=alt.Y("percentile_rank:Q", scale=alt.Scale(domain=[0, 100]), title="Percentile rank"),
            color=alt.Color("frame_label:N", legend=None),
            tooltip=["frame_label:N", "percentile_rank:Q"],
        )
    )
    return frame_position_fig, percentile_chart_df


@app.cell
def _(frame_position_fig, mo, percentile_chart_df):
    mo.vstack(
        [
            mo.md("## Frame position\nThe fixed 0–100 scale supports direct comparison across the four modeled frames."),
            frame_position_fig,
            mo.ui.table(percentile_chart_df, selection=None),
        ]
    )
    return


@app.cell
def _(mo):
    metric_type_selector = mo.ui.dropdown(
        options={"Topic scores": "topic_score", "Subject scores": "subject_score"},
        value="Topic scores",
        label="Score type",
    )
    frame_selector = mo.ui.dropdown(
        options={
            "All frames": "all",
            "Character": "character",
            "Livability": "livability",
            "Opportunity": "opportunity",
        },
        value="All frames",
        label="Frame focus",
    )
    mo.hstack([metric_type_selector, frame_selector], justify="start")
    return frame_selector, metric_type_selector


@app.cell
def _(frame_selector, metric_type_selector, topic_scores_df):
    filtered_scores_df = topic_scores_df.loc[
        topic_scores_df["metric_type"].eq(metric_type_selector.value)
    ].copy()
    if frame_selector.value != "all":
        filtered_scores_df = filtered_scores_df.loc[
            filtered_scores_df["frame_id"].eq(frame_selector.value)
        ].copy()
    filtered_scores_df = filtered_scores_df.sort_values("metric_value", ascending=False)
    return (filtered_scores_df,)


@app.cell
def _(alt, filtered_scores_df, pd):
    # Showing both tails keeps this exploratory view from implying that only
    # high modeled scores deserve attention.
    score_tail_df = pd.concat(
        [filtered_scores_df.head(6), filtered_scores_df.tail(6)]
    ).drop_duplicates(subset=["frame_id", "metric_id"])
    score_tail_df["chart_label"] = (
        score_tail_df["frame_id"].str.title() + " | " + score_tail_df["metric_label"]
    )
    topic_structure_fig = (
        alt.Chart(
            score_tail_df.sort_values("metric_value"),
            title="Strongest and weakest selected modeled dimensions",
        )
        .mark_bar()
        .encode(
            x=alt.X("metric_value:Q", title="Modeled score"),
            y=alt.Y("chart_label:N", title=None, sort="-x"),
            color=alt.Color("theme_group:N", title="Theme group"),
            tooltip=["frame_id:N", "theme_group:N", "metric_label:N", "metric_value:Q"],
        )
    )
    return score_tail_df, topic_structure_fig


@app.cell
def _(filtered_scores_df, mo, topic_structure_fig):
    mo.vstack(
        [
            mo.md("## Topic and subject structure"),
            topic_structure_fig,
            mo.ui.dataframe(filtered_scores_df, page_size=15),
        ]
    )
    return


@app.cell
def _(mo, raw_kpis_df):
    vintage_coverage_df = (
        raw_kpis_df.groupby(["frame_id", "source_year"], dropna=False)
        .size()
        .reset_index(name="metric_count")
        .sort_values(["frame_id", "source_year"])
    )
    mo.vstack(
        [
            mo.md("## Raw KPI candidate pool and vintage coverage"),
            mo.ui.dataframe(raw_kpis_df, page_size=15),
            mo.md("### Source-year coverage"),
            mo.ui.table(vintage_coverage_df, selection=None),
        ]
    )
    return (vintage_coverage_df,)


@app.cell
def _(
    benchmark_metric_bundle,
    comparison_set_selector,
    duckdb,
    fingerprint_metric_options,
    fingerprint_metric_selector,
    load_db_path_notebook,
    pd,
    selected_cbsa_code,
):
    selected_metric_ids = fingerprint_metric_selector.value or list(
        fingerprint_metric_options.values()
    )
    if comparison_set_selector.value is None or not selected_metric_ids:
        benchmark_results_df = pd.DataFrame()
    else:
        with duckdb.connect(load_db_path_notebook(), read_only=True) as benchmark_query_con:
            benchmark_results_df = benchmark_metric_bundle(
                benchmark_query_con,
                selected_cbsa_code,
                selected_metric_ids,
                [comparison_set_selector.value],
            )
    return benchmark_results_df, selected_metric_ids


@app.cell
def _(alt, benchmark_results_df, mo, pd):
    if benchmark_results_df.empty:
        benchmark_section = mo.callout(
            mo.md("No benchmark rows matched the selected candidate metrics and comparison set."),
            kind="warn",
        )
    else:
        benchmark_chart_df = benchmark_results_df.copy()
        benchmark_chart_df["metric_display"] = (
            benchmark_chart_df["frame_id"].str.title()
            + " | "
            + benchmark_chart_df["metric_label"]
        )
        benchmark_plot_df = benchmark_chart_df.melt(
            id_vars=[
                "metric_display",
                "percentile_rank",
                "comparison_n",
                "year",
                "membership_source",
            ],
            value_vars=["target_value", "comparison_median"],
            var_name="value_type",
            value_name="metric_value",
        )
        fingerprint_benchmark_fig = (
            alt.Chart(benchmark_plot_df, title="Target value and comparison median")
            .mark_point(filled=True, size=75)
            .encode(
                x=alt.X("metric_value:Q", title="Metric value (metric-specific units)"),
                y=alt.Y("metric_display:N", title=None, sort=None),
                color=alt.Color(
                    "value_type:N",
                    title=None,
                    scale=alt.Scale(
                        domain=["comparison_median", "target_value"],
                        range=["#6c757d", "#1f77b4"],
                    ),
                ),
                tooltip=[
                    "metric_display:N",
                    "value_type:N",
                    "metric_value:Q",
                    "percentile_rank:Q",
                    "comparison_n:Q",
                    "year:Q",
                    "membership_source:N",
                ],
            )
        )
        benchmark_section = mo.vstack(
            [
                mo.md("## Benchmark explorer\nGray dots are comparison medians; blue dots are the selected CBSA. Values retain each metric's native unit, so compare within—not across—rows."),
                fingerprint_benchmark_fig,
                mo.ui.dataframe(benchmark_chart_df, page_size=15),
            ]
        )
    benchmark_section
    return


@app.cell
def _(benchmark_results_df, filtered_scores_df, mo, pd):
    score_candidates_df = pd.concat(
        [filtered_scores_df.head(5), filtered_scores_df.tail(5)]
    ).drop_duplicates(subset=["frame_id", "metric_id"])[
        ["frame_id", "theme_group", "metric_label", "metric_type", "metric_value"]
    ]
    if benchmark_results_df.empty:
        benchmark_candidates_df = pd.DataFrame(
            columns=["frame_id", "metric_label", "target_value", "comparison_median", "z_score"]
        )
    else:
        benchmark_candidates_df = (
            benchmark_results_df.assign(absolute_z_score=benchmark_results_df["z_score"].abs())
            .sort_values("absolute_z_score", ascending=False)
            .head(10)[
                [
                    "frame_id",
                    "metric_label",
                    "target_value",
                    "comparison_median",
                    "percentile_rank",
                    "z_score",
                    "comparison_n",
                ]
            ]
        )
    mo.vstack(
        [
            mo.md("## Interpretation candidates\nThese are leads for review, not final issue claims or a selected fingerprint."),
            mo.md("### Strongest and weakest selected modeled dimensions"),
            mo.ui.table(score_candidates_df, selection=None),
            mo.md("### Largest standardized benchmark departures"),
            mo.ui.table(benchmark_candidates_df, selection=None),
        ]
    )
    return benchmark_candidates_df, score_candidates_df


@app.cell
def _(identity_df, mo, pd, percentiles_df, raw_kpis_df, topic_scores_df):
    required_frames = {"character", "livability", "opportunity", "cross_frame"}
    observed_frames = set(percentiles_df["frame_id"].dropna())
    qa_appendix_df = pd.DataFrame(
        [
            {"check": "Exactly one identity row", "result": len(identity_df) == 1, "detail": len(identity_df)},
            {
                "check": "Required percentile frames present",
                "result": required_frames.issubset(observed_frames),
                "detail": ", ".join(sorted(observed_frames)),
            },
            {
                "check": "Percentiles remain on 0–100 scale",
                "result": percentiles_df["percentile_rank"].between(0, 100).all(),
                "detail": f"min={percentiles_df['percentile_rank'].min()}, max={percentiles_df['percentile_rank'].max()}",
            },
            {
                "check": "Unique topic/subject keys",
                "result": not topic_scores_df.duplicated(["frame_id", "metric_type", "metric_id"]).any(),
                "detail": int(topic_scores_df.duplicated(["frame_id", "metric_type", "metric_id"]).sum()),
            },
            {
                "check": "Unique raw KPI keys",
                "result": not raw_kpis_df.duplicated(["frame_id", "metric_id"]).any(),
                "detail": int(raw_kpis_df.duplicated(["frame_id", "metric_id"]).sum()),
            },
            {
                "check": "Raw KPI missing values visible",
                "result": True,
                "detail": int(raw_kpis_df["metric_value"].isna().sum()),
            },
        ]
    )
    mo.vstack([mo.md("## QA appendix"), mo.ui.table(qa_appendix_df, selection=None)])
    return (qa_appendix_df,)


if __name__ == "__main__":
    app.run()
