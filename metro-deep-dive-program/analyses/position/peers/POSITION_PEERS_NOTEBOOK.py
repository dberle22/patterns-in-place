import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # The notebook only reads promoted peer fields and governed benchmark
    # surfaces. It never recreates similarity, peer membership, or rankings.
    import os
    from pathlib import Path

    import altair as alt
    import duckdb
    import marimo as mo
    import pandas as pd
    from pip_benchmarking import get_target_metric_surface, list_comparison_sets

    return Path, alt, duckdb, get_target_metric_surface, list_comparison_sets, mo, os, pd


@app.cell
def _(Path):
    analysis_dir = Path(__file__).resolve().parent
    repo_root = analysis_dir.parents[3]
    peer_query_path = analysis_dir / "queries" / "peer_list.sql"
    peer_position_query_path = analysis_dir / "queries" / "peer_benchmark_top5.sql"
    profile_query_dir = analysis_dir.parent / "profile" / "queries"
    return analysis_dir, peer_position_query_path, peer_query_path, profile_query_dir, repo_root


@app.cell
def _(os, repo_root):
    # Resolve the project configuration without relying on Marimo's working directory.
    def load_db_path_peers():
        configured_path = os.environ.get("DB_PATH", "").strip()
        if configured_path:
            return configured_path
        for raw_line in (repo_root / ".Renviron").read_text().splitlines():
            line = raw_line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if key.strip() == "DB_PATH":
                    return value.strip()
        raise RuntimeError("DB_PATH is not set and could not be found in the repo .Renviron.")

    return (load_db_path_peers,)


@app.cell
def _(duckdb, load_db_path_peers):
    def run_peer_query(query_path, cbsa_code):
        sql = query_path.read_text().replace("'__CBSA_CODE__'", f"'{cbsa_code}'")
        with duckdb.connect(load_db_path_peers(), read_only=True) as peer_con:
            return peer_con.sql(sql).df()

    def load_peer_cbsa_options():
        with duckdb.connect(load_db_path_peers(), read_only=True) as options_con:
            options_df = options_con.sql(
                "SELECT cbsa_code, cbsa_name FROM mart_intelligence.intelligence_cross_frame ORDER BY cbsa_name"
            ).df()
        return {f"{row.cbsa_name} ({row.cbsa_code})": row.cbsa_code for row in options_df.itertuples(index=False)}

    return load_peer_cbsa_options, run_peer_query


@app.cell
def _(mo):
    mo.md("""
    # Position Peers

    Cross-frame peers are the primary identity lens; Character, Livability,
    and Opportunity peers are supporting lenses. Similarity is an upstream
    modeled-feature-space result—not causal, geographic, or editorial
    equivalence—and this notebook is for internal exploration only.

    Every view is capped at the engine's promoted top 10 peers. Selecting a
    featured peer only changes the inspection comparison; it does not generate
    or endorse a final issue comparison.
    """)
    return


@app.cell
def _(load_peer_cbsa_options):
    peer_cbsa_options = load_peer_cbsa_options()
    return (peer_cbsa_options,)


@app.cell
def _(mo, peer_cbsa_options):
    default_peer_cbsa_label = next((label for label, code in peer_cbsa_options.items() if code == "40060"), next(iter(peer_cbsa_options)))
    peer_cbsa_selector = mo.ui.dropdown(peer_cbsa_options, value=default_peer_cbsa_label, label="Target CBSA", searchable=True, full_width=True)
    peer_type_selector = mo.ui.dropdown(
        {"Cross-frame (primary)": "cross_frame", "Character": "character", "Livability": "livability", "Opportunity": "opportunity"},
        value="Cross-frame (primary)", label="Peer lens",
    )
    peer_count_selector = mo.ui.slider(1, 10, value=5, label="Visible peers")
    mo.vstack([peer_cbsa_selector, mo.hstack([peer_type_selector, peer_count_selector], justify="start")])
    return peer_cbsa_selector, peer_count_selector, peer_type_selector


@app.cell
def _(peer_cbsa_selector, peer_position_query_path, peer_query_path, run_peer_query):
    selected_peer_cbsa_code = peer_cbsa_selector.value
    peer_list_df = run_peer_query(peer_query_path, selected_peer_cbsa_code)
    peer_position_df = run_peer_query(peer_position_query_path, selected_peer_cbsa_code)
    return peer_list_df, peer_position_df, selected_peer_cbsa_code


@app.cell
def _(duckdb, list_comparison_sets, load_db_path_peers, selected_peer_cbsa_code):
    with duckdb.connect(load_db_path_peers(), read_only=True) as peer_benchmark_setup_con:
        available_peer_comparison_sets_df = list_comparison_sets(peer_benchmark_setup_con, selected_peer_cbsa_code)
    return (available_peer_comparison_sets_df,)


@app.cell
def _(available_peer_comparison_sets_df, mo, peer_list_df, pd):
    peer_run_summary_df = (
        peer_list_df.groupby("peer_type", dropna=False)
        .agg(peer_rows=("peer_cbsa_code", "size"), missing_codes=("peer_cbsa_code", lambda value: value.isna().sum()), duplicate_peers=("peer_cbsa_code", lambda value: value.duplicated().sum()))
        .reset_index()
    )
    peer_run_summary_df["comparison_sets_available"] = len(available_peer_comparison_sets_df)
    mo.vstack([mo.md("## Run summary"), mo.ui.table(peer_run_summary_df, selection=None)])
    return (peer_run_summary_df,)


@app.cell
def _(peer_count_selector, peer_list_df, peer_type_selector):
    active_peer_df = peer_list_df.loc[peer_list_df["peer_type"].eq(peer_type_selector.value)].copy()
    visible_peer_df = active_peer_df.loc[active_peer_df["peer_rank"].le(peer_count_selector.value)].sort_values("peer_rank")
    return active_peer_df, visible_peer_df


@app.cell
def _(alt, mo, visible_peer_df):
    peer_similarity_chart = (
        alt.Chart(visible_peer_df, title="Promoted peer similarity ranking")
        .mark_bar()
        .encode(
            x=alt.X("similarity:Q", title="Upstream cosine similarity"),
            y=alt.Y("peer_cbsa_name:N", title=None, sort="-x"),
            tooltip=["peer_rank:Q", "peer_cbsa_name:N", "peer_cbsa_code:N", "similarity:Q"],
        )
    )
    mo.vstack([mo.md("## Ranked peer inventory"), peer_similarity_chart, mo.ui.dataframe(visible_peer_df, page_size=10)])
    return (peer_similarity_chart,)


@app.cell
def _(alt, mo, peer_list_df, pd):
    # This transparent pivot preserves the separately promoted rank and similarity
    # fields; it deliberately does not construct another composite peer score.
    peer_overlap_df = peer_list_df.pivot_table(
        index=["peer_cbsa_code", "peer_cbsa_name"], columns="peer_type", values="peer_rank", aggfunc="first"
    ).reset_index()
    peer_overlap_df["peer_type_count"] = peer_overlap_df[["cross_frame", "character", "livability", "opportunity"]].notna().sum(axis=1)
    peer_overlap_df["best_rank"] = peer_overlap_df[["cross_frame", "character", "livability", "opportunity"]].min(axis=1)
    peer_overlap_df["mean_available_rank"] = peer_overlap_df[["cross_frame", "character", "livability", "opportunity"]].mean(axis=1)
    peer_overlap_df = peer_overlap_df.sort_values(["peer_type_count", "best_rank"], ascending=[False, True])
    peer_overlap_long_df = peer_overlap_df.melt(id_vars=["peer_cbsa_code", "peer_cbsa_name"], value_vars=["cross_frame", "character", "livability", "opportunity"], var_name="peer_type", value_name="peer_rank").dropna()
    peer_overlap_chart = (
        alt.Chart(peer_overlap_long_df, title="Peer rank across promoted peer lenses")
        .mark_rect()
        .encode(x=alt.X("peer_type:N", title=None), y=alt.Y("peer_cbsa_name:N", title=None, sort=None), color=alt.Color("peer_rank:Q", scale=alt.Scale(reverse=True), title="Rank"), tooltip=["peer_cbsa_name:N", "peer_type:N", "peer_rank:Q"])
    )
    mo.vstack([mo.md("## Peer overlap"), peer_overlap_chart, mo.ui.dataframe(peer_overlap_df, page_size=15)])
    return peer_overlap_df, peer_overlap_long_df


@app.cell
def _(alt, mo, peer_position_df, pd):
    position_long_df = peer_position_df.melt(
        id_vars=["cbsa_code", "cbsa_name", "entity_role", "peer_rank"],
        value_vars=["character_percentile_rank", "livability_percentile_rank", "opportunity_percentile_rank", "cross_frame_percentile_rank"],
        var_name="frame_id", value_name="percentile_rank",
    )
    position_long_df["frame_label"] = position_long_df["frame_id"].str.replace("_percentile_rank", "", regex=False).str.replace("_", " ").str.title()
    position_long_df["metro_label"] = position_long_df.apply(lambda row: f"Target | {row.cbsa_name}" if row.entity_role == "target" else f"Peer {int(row.peer_rank)} | {row.cbsa_name}", axis=1)
    position_heatmap = (
        alt.Chart(position_long_df, title="Target and top-five cross-frame peer position")
        .mark_rect()
        .encode(x=alt.X("frame_label:N", title=None), y=alt.Y("metro_label:N", title=None, sort=None), color=alt.Color("percentile_rank:Q", scale=alt.Scale(domain=[0, 100]), title="Percentile"), tooltip=["metro_label:N", "frame_label:N", "percentile_rank:Q"])
    )
    mo.vstack([mo.md("## Cross-frame position comparison"), position_heatmap])
    return position_long_df, position_heatmap


@app.cell
def _(active_peer_df, mo):
    featured_peer_options = {f"Rank {row.peer_rank} | {row.peer_cbsa_name} ({row.peer_cbsa_code})": row.peer_cbsa_code for row in active_peer_df.itertuples(index=False)}
    featured_peer_selector = mo.ui.dropdown(featured_peer_options, value=next(iter(featured_peer_options), None), label="Featured peer candidate", searchable=True, full_width=True)
    featured_peer_selector
    return featured_peer_options, featured_peer_selector


@app.cell
def _(duckdb, featured_peer_selector, get_target_metric_surface, load_db_path_peers, selected_peer_cbsa_code):
    selected_featured_peer_code = featured_peer_selector.value
    with duckdb.connect(load_db_path_peers(), read_only=True) as head_to_head_con:
        target_profile_metrics_df = get_target_metric_surface(head_to_head_con, selected_peer_cbsa_code)
        featured_profile_metrics_df = get_target_metric_surface(head_to_head_con, selected_featured_peer_code)
    return featured_profile_metrics_df, selected_featured_peer_code, target_profile_metrics_df


@app.cell
def _(mo, target_profile_metrics_df):
    candidate_metric_options = {f"{row.frame_id.title()} | {row.metric_label} ({row.metric_id})": row.metric_id for row in target_profile_metrics_df.drop_duplicates("metric_id").sort_values(["frame_id", "metric_label"]).itertuples(index=False)}
    comparison_metric_selector = mo.ui.multiselect(candidate_metric_options, value=list(candidate_metric_options)[:8], label="Head-to-head metrics", full_width=True)
    comparison_metric_selector
    return comparison_metric_selector, candidate_metric_options


@app.cell
def _(comparison_metric_selector, featured_profile_metrics_df, pd, target_profile_metrics_df):
    selected_comparison_metric_ids = comparison_metric_selector.value
    target_selected_metrics_df = target_profile_metrics_df.loc[target_profile_metrics_df.metric_id.isin(selected_comparison_metric_ids)].copy()
    featured_selected_metrics_df = featured_profile_metrics_df.loc[featured_profile_metrics_df.metric_id.isin(selected_comparison_metric_ids)].copy()
    head_to_head_metrics_df = target_selected_metrics_df.merge(featured_selected_metrics_df, on=["metric_id", "year"], suffixes=("_target", "_peer"))
    head_to_head_metrics_df["value_gap_target_minus_peer"] = head_to_head_metrics_df["value_target"] - head_to_head_metrics_df["value_peer"]
    return (head_to_head_metrics_df,)


@app.cell
def _(alt, head_to_head_metrics_df, mo, pd):
    head_to_head_long_df = head_to_head_metrics_df.melt(id_vars=["metric_id", "metric_label_target", "frame_id_target", "year", "value_gap_target_minus_peer"], value_vars=["value_target", "value_peer"], var_name="metro_role", value_name="metric_value")
    head_to_head_chart = (
        alt.Chart(head_to_head_long_df, title="Featured-peer metric comparison")
        .mark_point(filled=True, size=70)
        .encode(x=alt.X("metric_value:Q", title="Metric value (native units)"), y=alt.Y("metric_label_target:N", title=None, sort=None), color=alt.Color("metro_role:N", title=None), tooltip=["metric_label_target:N", "metro_role:N", "metric_value:Q", "year:Q", "value_gap_target_minus_peer:Q"])
    )
    mo.vstack([mo.md("## Head-to-head profile\nValues retain their native units. Compare target and peer within a metric, not across metrics."), head_to_head_chart, mo.ui.dataframe(head_to_head_metrics_df, page_size=15)])
    return head_to_head_chart, head_to_head_long_df


@app.cell
def _(active_peer_df, head_to_head_metrics_df, mo, peer_overlap_df, selected_featured_peer_code):
    featured_peer_note_df = active_peer_df.loc[active_peer_df.peer_cbsa_code.eq(selected_featured_peer_code)].merge(peer_overlap_df, on=["peer_cbsa_code", "peer_cbsa_name"], how="left")
    largest_gap_df = head_to_head_metrics_df.assign(absolute_gap=head_to_head_metrics_df.value_gap_target_minus_peer.abs()).sort_values("absolute_gap", ascending=False).head(10)
    mo.vstack([mo.md("## Candidate notes\nThese transparent cues support analyst review; they do not choose an editorial featured peer."), mo.ui.table(featured_peer_note_df, selection=None), mo.ui.table(largest_gap_df[["metric_label_target", "year", "value_target", "value_peer", "value_gap_target_minus_peer"]], selection=None)])
    return featured_peer_note_df, largest_gap_df


@app.cell
def _(active_peer_df, mo, pd, selected_peer_cbsa_code):
    expected_ranks = set(range(1, len(active_peer_df) + 1))
    qa_peer_df = pd.DataFrame([
        {"check": "Peer ranks unique", "result": not active_peer_df.peer_rank.duplicated().any()},
        {"check": "Peer ranks contiguous", "result": set(active_peer_df.peer_rank) == expected_ranks},
        {"check": "Target is not a peer", "result": not active_peer_df.peer_cbsa_code.eq(selected_peer_cbsa_code).any()},
        {"check": "Peer code/name present together", "result": active_peer_df[["peer_cbsa_code", "peer_cbsa_name"]].isna().all(axis=1).equals(active_peer_df[["peer_cbsa_code", "peer_cbsa_name"]].isna().any(axis=1))},
        {"check": "Similarity descends with rank", "result": active_peer_df.sort_values("peer_rank").similarity.is_monotonic_decreasing},
    ])
    mo.vstack([mo.md("## QA appendix"), mo.ui.table(qa_peer_df, selection=None)])
    return (qa_peer_df,)


if __name__ == "__main__":
    app.run()
