import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import plotly.express as px
    from pathlib import Path

    from duckdb_helpers import connect_duckdb, get_cbsa_options, run_param_query

    return Path, connect_duckdb, get_cbsa_options, mo, px, run_param_query


@app.cell
def _(Path):
    # Keep the notebook wired directly to the reusable analysis query surfaces
    # so Act 1 assembly does not fork the underlying logic.
    notebook_dir = Path(__file__).resolve().parent
    program_root = notebook_dir.parents[2]
    profile_query_dir = program_root / "analyses" / "position" / "profile" / "queries"
    peers_query_dir = program_root / "analyses" / "position" / "peers" / "queries"

    query_paths = {
        "identity": profile_query_dir / "profile_identity.sql",
        "percentiles": profile_query_dir / "profile_percentiles.sql",
        "topic_scores": profile_query_dir / "profile_topic_scores.sql",
        "raw_kpis": profile_query_dir / "profile_raw_kpis.sql",
        "peer_list": peers_query_dir / "peer_list.sql",
        "peer_benchmark_top5": peers_query_dir / "peer_benchmark_top5.sql",
    }
    return (query_paths,)


@app.cell
def _(connect_duckdb, get_cbsa_options):
    with connect_duckdb(read_only=True) as cbsa_options_con:
        cbsa_options = get_cbsa_options(cbsa_options_con)
    return (cbsa_options,)


@app.cell
def _(cbsa_options, mo):
    default_cbsa_label = next(
        (
            label
            for label, cbsa_code in cbsa_options.items()
            if cbsa_code == "40060"
        ),
        next(iter(cbsa_options)),
    )
    cbsa_selector = mo.ui.dropdown(
        options=cbsa_options,
        value=default_cbsa_label,
        label="Target CBSA",
        searchable=True,
    )
    cbsa_selector
    return (cbsa_selector,)


@app.cell
def _(mo):
    mo.md("""
    # Act 1 Position Notebook

    Shared inspection notebook for the first Act 1 surfaces:

    - identity labels
    - frame percentiles
    - topic and subject score patterns
    - raw KPI candidate pool
    - peer set and top-5 peer benchmark surface

    This notebook reads from DuckDB through the reusable `analyses/position`
    query surfaces rather than from exported files.
    """)
    return


@app.cell
def _(cbsa_selector, connect_duckdb, query_paths, run_param_query):
    selected_cbsa_code = cbsa_selector.value
    with connect_duckdb(read_only=True) as profile_query_con:
        identity_df = run_param_query(profile_query_con, query_paths["identity"], selected_cbsa_code)
        percentiles_df = run_param_query(profile_query_con, query_paths["percentiles"], selected_cbsa_code)
        topic_scores_df = run_param_query(profile_query_con, query_paths["topic_scores"], selected_cbsa_code)
        raw_kpis_df = run_param_query(profile_query_con, query_paths["raw_kpis"], selected_cbsa_code)
        peer_list_df = run_param_query(profile_query_con, query_paths["peer_list"], selected_cbsa_code)
        peer_benchmark_df = run_param_query(
            profile_query_con, query_paths["peer_benchmark_top5"], selected_cbsa_code
        )
    return (
        identity_df,
        peer_benchmark_df,
        peer_list_df,
        percentiles_df,
        raw_kpis_df,
        selected_cbsa_code,
        topic_scores_df,
    )


@app.cell
def _(identity_df, mo, selected_cbsa_code):
    if identity_df.empty:
        mo.md(f"No Act 1 identity row found for `{selected_cbsa_code}`.")
    else:
        row = identity_df.iloc[0]
        mo.md(
            f"""
            ## Identity

            **{row["cbsa_name"]}**

            - Character cluster: `{row["character_cluster"]}`
            - Livability cluster: `{row["livability_cluster"]}`
            - Opportunity cluster: `{row["opportunity_cluster"]}`
            - Cross-frame cluster: `{row["cross_frame_cluster"]}`
            - Top frame: `{row["top_frame"]}`
            - Bottom frame: `{row["bottom_frame"]}`
            - Overlap profile: `{row["overlap_profile"]}`
            - Signature: `{row["signature"]}`
            """
        )
    return


@app.cell
def _(mo, percentiles_df, px):
    chart_df = percentiles_df.copy()
    chart_df["frame_label"] = chart_df["frame_id"].str.replace("_", " ").str.title()
    percentile_fig = px.bar(
        chart_df,
        x="frame_label",
        y="percentile_rank",
        text="percentile_rank",
        color="frame_label",
        title="Frame percentile ranks",
    )
    percentile_fig.update_yaxes(range=[0, 100], title="Percentile rank")
    percentile_fig.update_layout(
        template="plotly_white",
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    mo.vstack([mo.md("## Percentiles"), percentile_fig])
    return


@app.cell
def _(mo, px, topic_scores_df):
    topic_chart_df = (
        topic_scores_df.sort_values("metric_value", ascending=False)
        .head(8)
        .copy()
    )
    topic_chart_df["label"] = (
        topic_chart_df["frame_id"].str.title()
        + " | "
        + topic_chart_df["metric_label"]
    )
    topic_fig = px.bar(
        topic_chart_df,
        x="metric_value",
        y="label",
        color="theme_group",
        orientation="h",
        title="Top scored topic and subject signals",
    )
    topic_fig.update_layout(
        template="plotly_white",
        yaxis_title="",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    mo.vstack([mo.md("## Topic Scores"), topic_fig])
    return


@app.cell
def _(mo, peer_list_df, px):
    cross_frame_peers_df = (
        peer_list_df.loc[peer_list_df["peer_type"] == "cross_frame"]
        .sort_values("peer_rank")
        .head(10)
        .copy()
    )
    peer_fig = px.bar(
        cross_frame_peers_df,
        x="similarity",
        y="peer_cbsa_name",
        text="peer_rank",
        orientation="h",
        title="Cross-frame peer ranking",
    )
    peer_fig.update_layout(
        template="plotly_white",
        yaxis_title="",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    mo.vstack([mo.md("## Peers"), peer_fig])
    return


@app.cell
def _(mo, peer_benchmark_df, px):
    benchmark_long_df = peer_benchmark_df.melt(
        id_vars=[
            "cbsa_code",
            "cbsa_name",
            "entity_role",
            "peer_rank",
            "character_cluster",
            "livability_cluster",
            "opportunity_cluster",
            "combined_cluster",
        ],
        value_vars=[
            "character_percentile_rank",
            "livability_percentile_rank",
            "opportunity_percentile_rank",
            "cross_frame_percentile_rank",
        ],
        var_name="metric_id",
        value_name="metric_value",
    )
    benchmark_long_df["metric_label"] = (
        benchmark_long_df["metric_id"].str.replace("_percentile_rank", "", regex=False)
        .str.replace("_", " ")
        .str.title()
    )
    benchmark_long_df["row_label"] = benchmark_long_df.apply(
        lambda row: (
            f'Target | {row["cbsa_name"]}'
            if row["entity_role"] == "target"
            else f'Peer {int(row["peer_rank"])} | {row["cbsa_name"]}'
        ),
        axis=1,
    )
    benchmark_fig = px.density_heatmap(
        benchmark_long_df,
        x="metric_label",
        y="row_label",
        z="metric_value",
        text_auto=True,
        color_continuous_scale="Blues",
        title="Target metro versus top 5 cross-frame peers",
    )
    benchmark_fig.update_layout(
        template="plotly_white",
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    mo.vstack([mo.md("## Peer Benchmark"), benchmark_fig])
    return


@app.cell
def _(mo, raw_kpis_df, topic_scores_df):
    mo.md(f"""
    ## Tables

    - Topic and subject score rows loaded: `{len(topic_scores_df)}`
    - Raw KPI rows loaded: `{len(raw_kpis_df)}`

    The notebook keeps the fuller query surfaces available so the issue
    layer can later choose what to display instead of relying on a thin
    preselection.
    """)
    return


@app.cell
def _(mo, raw_kpis_df):
    mo.vstack(
        [
            mo.md("### Raw KPI Candidate Pool"),
            raw_kpis_df,
        ]
    )
    return


@app.cell
def _(mo, topic_scores_df):
    mo.vstack(
        [
            mo.md("### Topic And Subject Score Surface"),
            topic_scores_df,
        ]
    )
    return


@app.cell
def _(mo, peer_list_df):
    mo.vstack(
        [
            mo.md("### Full Peer Surface"),
            peer_list_df,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
