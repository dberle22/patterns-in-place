import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This is a read-only review surface over stored engine outputs. All trend,
    # percentile, salience, label, and turn fields remain engine-owned.
    import os
    from pathlib import Path

    import altair as alt
    import duckdb
    import marimo as mo
    import pandas as pd

    return Path, alt, duckdb, mo, os, pd


@app.cell
def _(Path):
    trajectory_dir = Path(__file__).resolve().parent
    trajectory_repo_root = trajectory_dir.parents[3]
    trajectory_query_paths = {
        "run_inventory": trajectory_dir / "queries" / "trajectory_run_inventory.sql",
        "frame_context": trajectory_dir / "queries" / "trajectory_frame_context.sql",
        "turn_signals": trajectory_dir / "queries" / "trajectory_turn_signals.sql",
    }
    return trajectory_dir, trajectory_query_paths, trajectory_repo_root


@app.cell
def _(os, trajectory_repo_root):
    def load_trajectory_db_path():
        configured_path = os.environ.get("DB_PATH", "").strip()
        if configured_path:
            return configured_path
        for raw_line in (trajectory_repo_root / ".Renviron").read_text().splitlines():
            line = raw_line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if key.strip() == "DB_PATH":
                    return value.strip()
        raise RuntimeError("DB_PATH is not set and could not be found in the repo .Renviron.")

    return (load_trajectory_db_path,)


@app.cell
def _(duckdb, load_trajectory_db_path, trajectory_query_paths):
    # Query files provide the reusable all-market consumer surfaces. The two
    # selected-market tables are loaded once for reactive metric drill-through.
    with duckdb.connect(load_trajectory_db_path(), read_only=True) as trajectory_load_con:
        trajectory_series_all_df = trajectory_load_con.sql("SELECT * FROM mart_intelligence.intelligence_trajectory_series").df()
        trajectory_metric_all_df = trajectory_load_con.sql("SELECT * FROM mart_intelligence.intelligence_trajectory_metric").df()
        trajectory_inventory_df = trajectory_load_con.sql(trajectory_query_paths["run_inventory"].read_text()).df()
        trajectory_frame_all_df = trajectory_load_con.sql(trajectory_query_paths["frame_context"].read_text()).df()
        trajectory_turn_all_df = trajectory_load_con.sql(trajectory_query_paths["turn_signals"].read_text()).df()
    return trajectory_frame_all_df, trajectory_inventory_df, trajectory_metric_all_df, trajectory_series_all_df, trajectory_turn_all_df


@app.cell
def _(mo):
    mo.md("""
    # Position Trajectory — pilot review

    This notebook reviews the stored `trajectory_pilot_v1` direct recurring
    panel: 50 KPIs across a stable 396-CBSA universe with a common 2023 end
    vintage. It is an internal method-review surface, not a publication-ready
    Act 3 conclusion or a complete trend candidate pool.

    Starting/ending position, absolute movement, relative momentum, and
    salience are distinct stored concepts. Character is descriptive and
    magnitude-oriented, not a better/worse frame judgment.
    """)
    return


@app.cell
def _(mo, trajectory_inventory_df):
    # Inventory grounds every control in materialized combinations, preventing
    # nonexistent frame/window choices such as a one-year Character view.
    mo.vstack([mo.md("## Run inventory"), mo.ui.dataframe(trajectory_inventory_df, page_size=15)])
    return


@app.cell
def _(trajectory_frame_all_df):
    trajectory_cbsa_options = {f"{row.cbsa_name} ({row.cbsa_code})": row.cbsa_code for row in trajectory_frame_all_df[["cbsa_code", "cbsa_name"]].drop_duplicates().sort_values("cbsa_name").itertuples(index=False)}
    trajectory_method_options = {value: value for value in sorted(trajectory_frame_all_df.method_version.dropna().unique())}
    return trajectory_cbsa_options, trajectory_method_options


@app.cell
def _(mo, trajectory_cbsa_options, trajectory_method_options):
    trajectory_default_cbsa_label = next((label for label, code in trajectory_cbsa_options.items() if code == "40060"), next(iter(trajectory_cbsa_options)))
    trajectory_cbsa_selector = mo.ui.dropdown(trajectory_cbsa_options, value=trajectory_default_cbsa_label, label="Target CBSA", searchable=True, full_width=True)
    trajectory_method_selector = mo.ui.dropdown(trajectory_method_options, value=next(iter(trajectory_method_options)), label="Method version")
    mo.vstack([trajectory_cbsa_selector, trajectory_method_selector])
    return trajectory_cbsa_selector, trajectory_method_selector


@app.cell
def _(trajectory_frame_all_df, trajectory_method_selector):
    selected_method_inventory_df = trajectory_frame_all_df.loc[trajectory_frame_all_df.method_version.eq(trajectory_method_selector.value)].copy()
    trajectory_window_options = {value.replace("_", " ").title(): value for value in sorted(selected_method_inventory_df.window_name.dropna().unique())}
    return selected_method_inventory_df, trajectory_window_options


@app.cell
def _(mo, trajectory_window_options):
    trajectory_window_selector = mo.ui.dropdown(trajectory_window_options, value=next((label for label, value in trajectory_window_options.items() if value == "five_year"), next(iter(trajectory_window_options))), label="Window")
    trajectory_window_selector
    return (trajectory_window_selector,)


@app.cell
def _(selected_method_inventory_df, trajectory_window_selector):
    selected_window_inventory_df = selected_method_inventory_df.loc[selected_method_inventory_df.window_name.eq(trajectory_window_selector.value)].copy()
    trajectory_frame_options = {value.title(): value for value in sorted(selected_window_inventory_df.frame_id.dropna().unique())}
    return selected_window_inventory_df, trajectory_frame_options


@app.cell
def _(mo, trajectory_frame_options):
    trajectory_frame_selector = mo.ui.dropdown(trajectory_frame_options, value=next((label for label, value in trajectory_frame_options.items() if value == "opportunity"), next(iter(trajectory_frame_options))), label="Frame")
    trajectory_threshold_selector = mo.ui.dropdown({"Production p80": "signal_p80", "p90": "signal_p90", "p95": "signal_p95"}, value="Production p80", label="Persisted salience gate")
    mo.hstack([trajectory_frame_selector, trajectory_threshold_selector], justify="start")
    return trajectory_frame_selector, trajectory_threshold_selector


@app.cell
def _(trajectory_frame_selector, trajectory_method_selector, trajectory_metric_all_df, trajectory_window_selector):
    eligible_metric_catalog_df = trajectory_metric_all_df.loc[(trajectory_metric_all_df.method_version.eq(trajectory_method_selector.value)) & (trajectory_metric_all_df.frame_id.eq(trajectory_frame_selector.value)) & (trajectory_metric_all_df.window_name.eq(trajectory_window_selector.value))].copy()
    trajectory_metric_options = {f"{row.metric_label} ({row.metric_id})": row.metric_id for row in eligible_metric_catalog_df[["metric_id", "metric_label"]].drop_duplicates().sort_values("metric_label").itertuples(index=False)}
    return eligible_metric_catalog_df, trajectory_metric_options


@app.cell
def _(mo, trajectory_metric_options):
    trajectory_metric_selector = mo.ui.dropdown(trajectory_metric_options, value=next(iter(trajectory_metric_options), None), label="Annual drill-through metric", searchable=True, full_width=True)
    trajectory_metric_selector
    return (trajectory_metric_selector,)


@app.cell
def _(trajectory_cbsa_selector, trajectory_frame_all_df, trajectory_method_selector, trajectory_window_selector):
    selected_trajectory_cbsa_code = trajectory_cbsa_selector.value
    selected_market_frames_df = trajectory_frame_all_df.loc[(trajectory_frame_all_df.cbsa_code.eq(selected_trajectory_cbsa_code)) & (trajectory_frame_all_df.method_version.eq(trajectory_method_selector.value)) & (trajectory_frame_all_df.window_name.eq(trajectory_window_selector.value))].copy()
    return selected_market_frames_df, selected_trajectory_cbsa_code


@app.cell
def _(mo, selected_market_frames_df):
    frame_summary_columns = ["frame_id", "window_name", "start_year", "end_year", "topic_count", "metric_count", "coverage_status", "start_position_percentile", "end_position_percentile", "percentile_point_change", "frame_momentum_score", "trajectory_salience_percentile", "signal_tier", "trajectory_label"]
    mo.vstack([mo.md("## Selected-market frame summary"), mo.ui.table(selected_market_frames_df[frame_summary_columns], selection=None)])
    return


@app.cell
def _(alt, mo, selected_market_frames_df, pd):
    frame_path_long_df = selected_market_frames_df.melt(id_vars=["frame_id", "window_name", "start_year", "end_year"], value_vars=["start_position_percentile", "end_position_percentile"], var_name="position_point", value_name="position_percentile")
    frame_path_long_df["year_label"] = frame_path_long_df.apply(lambda row: str(row.start_year) if row.position_point == "start_position_percentile" else str(row.end_year), axis=1)
    frame_path_chart = alt.Chart(frame_path_long_df, title="Selected-market start and end national position").mark_line(point=True).encode(x=alt.X("year_label:O", title="Year"), y=alt.Y("position_percentile:Q", scale=alt.Scale(domain=[0, 100]), title="National percentile"), color=alt.Color("frame_id:N", title="Frame"), detail="frame_id:N", tooltip=["frame_id:N", "window_name:N", "year_label:N", "position_percentile:Q"])
    mo.vstack([mo.md("## Position path"), frame_path_chart])
    return frame_path_chart, frame_path_long_df


@app.cell
def _(selected_trajectory_cbsa_code, trajectory_frame_all_df, trajectory_frame_selector, trajectory_method_selector, trajectory_window_selector):
    national_frame_context_df = trajectory_frame_all_df.loc[(trajectory_frame_all_df.method_version.eq(trajectory_method_selector.value)) & (trajectory_frame_all_df.frame_id.eq(trajectory_frame_selector.value)) & (trajectory_frame_all_df.window_name.eq(trajectory_window_selector.value))].copy()
    national_frame_context_df["is_target"] = national_frame_context_df.cbsa_code.eq(selected_trajectory_cbsa_code)
    return (national_frame_context_df,)


@app.cell
def _(alt, mo, national_frame_context_df):
    national_context_chart = alt.Chart(national_frame_context_df, title="National ending-position and momentum context").mark_circle(opacity=0.55).encode(x=alt.X("end_position_percentile:Q", scale=alt.Scale(domain=[0, 100]), title="Ending position percentile"), y=alt.Y("frame_momentum_score:Q", title="Stored frame momentum"), color=alt.condition("datum.is_target", alt.value("#d62728"), alt.value("#9aa0a6")), size=alt.condition("datum.is_target", alt.value(110), alt.value(35)), tooltip=["cbsa_name:N", "end_position_percentile:Q", "frame_momentum_score:Q", "trajectory_salience_percentile:Q", "trajectory_label:N", "coverage_status:N"])
    mo.vstack([mo.md("## National trajectory context"), national_context_chart])
    return (national_context_chart,)


@app.cell
def _(selected_trajectory_cbsa_code, trajectory_frame_selector, trajectory_method_selector, trajectory_metric_all_df, trajectory_window_selector):
    selected_metric_evidence_df = trajectory_metric_all_df.loc[(trajectory_metric_all_df.cbsa_code.eq(selected_trajectory_cbsa_code)) & (trajectory_metric_all_df.method_version.eq(trajectory_method_selector.value)) & (trajectory_metric_all_df.frame_id.eq(trajectory_frame_selector.value)) & (trajectory_metric_all_df.window_name.eq(trajectory_window_selector.value))].copy()
    return (selected_metric_evidence_df,)


@app.cell
def _(alt, mo, pd, selected_metric_evidence_df):
    metric_endpoint_long_df = selected_metric_evidence_df.melt(id_vars=["metric_id", "metric_label", "topic_id", "start_year", "end_year", "coverage_status", "absolute_direction", "relative_momentum_score", "metric_salience_percentile"], value_vars=["start_percentile", "end_percentile"], var_name="endpoint", value_name="national_percentile")
    metric_endpoint_chart = alt.Chart(metric_endpoint_long_df, title="Metric evidence: start and end national percentile").mark_point(filled=True).encode(x=alt.X("national_percentile:Q", scale=alt.Scale(domain=[0, 100]), title="National percentile"), y=alt.Y("metric_label:N", title=None, sort=None), color=alt.Color("endpoint:N", title=None), tooltip=["metric_label:N", "endpoint:N", "national_percentile:Q", "absolute_direction:N", "relative_momentum_score:Q", "coverage_status:N"])
    mo.vstack([mo.md("## Metric evidence"), metric_endpoint_chart, mo.ui.dataframe(selected_metric_evidence_df, page_size=15)])
    return metric_endpoint_chart, metric_endpoint_long_df


@app.cell
def _(selected_trajectory_cbsa_code, trajectory_metric_selector, trajectory_method_selector, trajectory_series_all_df):
    annual_metric_series_df = trajectory_series_all_df.loc[(trajectory_series_all_df.cbsa_code.eq(selected_trajectory_cbsa_code)) & (trajectory_series_all_df.method_version.eq(trajectory_method_selector.value)) & (trajectory_series_all_df.metric_id.eq(trajectory_metric_selector.value))].sort_values("year").copy()
    return (annual_metric_series_df,)


@app.cell
def _(alt, annual_metric_series_df, mo):
    annual_raw_chart = alt.Chart(annual_metric_series_df, title="Annual observed raw value").mark_line(point=True).encode(x=alt.X("year:O", title="Year"), y=alt.Y("raw_value:Q", title="Raw value (native unit)"), tooltip=["year:Q", "raw_value:Q", "source_table:N", "source_column:N", "eligibility_status:N"])
    annual_percentile_chart = alt.Chart(annual_metric_series_df, title="Annual national percentile").mark_line(point=True).encode(x=alt.X("year:O", title="Year"), y=alt.Y("national_percentile:Q", scale=alt.Scale(domain=[0, 100]), title="National percentile"), tooltip=["year:Q", "national_percentile:Q", "transformed_value:Q", "polarity:N"])
    mo.vstack([mo.md("## Annual metric drill-through"), mo.ui.table(annual_metric_series_df[["metric_label", "transform", "polarity", "source_table", "source_column", "eligibility_status"]].drop_duplicates(), selection=None), annual_raw_chart, annual_percentile_chart, mo.ui.table(annual_metric_series_df, selection=None)])
    return annual_percentile_chart, annual_raw_chart


@app.cell
def _(selected_trajectory_cbsa_code, trajectory_frame_selector, trajectory_method_selector, trajectory_turn_all_df):
    turn_context_df = trajectory_turn_all_df.loc[(trajectory_turn_all_df.method_version.eq(trajectory_method_selector.value)) & (trajectory_turn_all_df.frame_id.eq(trajectory_frame_selector.value))].copy()
    turn_context_df["is_target"] = turn_context_df.cbsa_code.eq(selected_trajectory_cbsa_code)
    selected_turn_df = turn_context_df.loc[turn_context_df.is_target].copy()
    return selected_turn_df, turn_context_df


@app.cell
def _(alt, mo, selected_turn_df, turn_context_df):
    turn_context_chart = alt.Chart(turn_context_df, title="Stored short- and medium-window turn context").mark_circle(opacity=0.55).encode(x=alt.X("frame_momentum_score_medium:Q", title="Medium-window stored momentum"), y=alt.Y("frame_momentum_score_short:Q", title="Short-window stored momentum"), color=alt.Color("turn_status:N", title="Stored turn status"), size=alt.condition("datum.is_target", alt.value(115), alt.value(35)), tooltip=["cbsa_name:N", "turn_status:N", "frame_momentum_score_short:Q", "frame_momentum_score_medium:Q", "supporting_metric_ids:N", "shared_metric_count:Q"])
    mo.vstack([mo.md("## Turn signals\n`no_turn_signal` is a valid stored result, not missing evidence."), mo.ui.table(selected_turn_df, selection=None), turn_context_chart])
    return (turn_context_chart,)


@app.cell
def _(mo, pd, selected_market_frames_df, trajectory_frame_all_df, trajectory_method_selector, trajectory_threshold_selector, trajectory_window_selector):
    threshold_columns = ["signal_p80", "signal_p90", "signal_p95"]
    threshold_sensitivity_df = selected_market_frames_df[["frame_id", "window_name", "trajectory_salience_percentile", *threshold_columns]].copy()
    threshold_sensitivity_df["selected_gate_member"] = threshold_sensitivity_df[trajectory_threshold_selector.value]
    threshold_context_df = trajectory_frame_all_df.loc[(trajectory_frame_all_df.method_version.eq(trajectory_method_selector.value)) & (trajectory_frame_all_df.window_name.eq(trajectory_window_selector.value))].groupby("frame_id", dropna=False)[threshold_columns].sum().reset_index()
    mo.vstack([mo.md("## Signal sensitivity\nFlags are persisted engine outputs; this control does not recompute a threshold."), mo.md("### Selected-market membership"), mo.ui.table(threshold_sensitivity_df, selection=None), mo.md("### National persisted-flag counts"), mo.ui.table(threshold_context_df, selection=None)])
    return threshold_context_df, threshold_sensitivity_df


@app.cell
def _(mo, pd, selected_market_frames_df, selected_metric_evidence_df, annual_metric_series_df):
    trajectory_qa_df = pd.DataFrame([
        {"check": "Selected frame rows unique", "result": not selected_market_frames_df.duplicated(["frame_id", "window_name", "end_year"]).any(), "detail": len(selected_market_frames_df)},
        {"check": "Selected metric rows unique", "result": not selected_metric_evidence_df.duplicated(["metric_id", "window_name", "end_year"]).any(), "detail": len(selected_metric_evidence_df)},
        {"check": "Annual rows unique", "result": not annual_metric_series_df.duplicated(["metric_id", "year"]).any(), "detail": len(annual_metric_series_df)},
        {"check": "Metric coverage remains visible", "result": True, "detail": int(selected_metric_evidence_df.coverage_status.isna().sum())},
        {"check": "Annual endpoints available", "result": annual_metric_series_df.raw_value.notna().any(), "detail": f"{annual_metric_series_df.year.min()}–{annual_metric_series_df.year.max()}"},
    ])
    mo.vstack([mo.md("## QA appendix"), mo.ui.table(trajectory_qa_df, selection=None)])
    return (trajectory_qa_df,)


if __name__ == "__main__":
    app.run()
