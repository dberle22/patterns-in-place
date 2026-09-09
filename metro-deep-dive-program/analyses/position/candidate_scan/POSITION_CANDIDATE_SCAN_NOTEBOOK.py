import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # Candidate Scan is a thin, read-only consumer of current Profile and
    # Time-Series marts. The local score only prioritizes which market to
    # inspect next; it never replaces engine-owned trajectory evidence.
    import os
    from pathlib import Path

    import altair as alt
    import duckdb
    import marimo as mo
    import pandas as pd

    return Path, alt, duckdb, mo, os, pd


@app.cell
def _(Path):
    # Resolve paths from the notebook file so the notebook works from Marimo,
    # VS Code, or any shell working directory without local path edits.
    candidate_scan_dir = Path(__file__).resolve().parent
    candidate_scan_repo_root = candidate_scan_dir.parents[3]
    legacy_candidate_path = (
        candidate_scan_repo_root
        / "exploration/intelligence_framework/phase_6_trajectory/outputs/phase6_candidate_list.csv"
    )
    return candidate_scan_dir, candidate_scan_repo_root, legacy_candidate_path


@app.cell
def _(candidate_scan_repo_root, os):
    # Match the Position notebooks' DB_PATH lookup while keeping the notebook
    # portable and DuckDB reads explicitly separate from any materialization.
    def load_candidate_scan_db_path() -> str:
        configured_path = os.environ.get("DB_PATH", "").strip()
        if configured_path:
            return configured_path

        renviron_path = candidate_scan_repo_root / ".Renviron"
        if renviron_path.exists():
            for raw_line in renviron_path.read_text().splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key.strip() == "DB_PATH":
                    return value.strip()

        raise RuntimeError("DB_PATH is not set and could not be found in .Renviron.")

    return (load_candidate_scan_db_path,)


@app.cell
def _(duckdb, load_candidate_scan_db_path, pd):
    # Profile fields and governed filter attributes are loaded at CBSA grain.
    # The current Profile universe remains the base universe even when a
    # market is later ineligible for a trajectory-based candidate score.
    with duckdb.connect(load_candidate_scan_db_path(), read_only=True) as candidate_profile_con:
        candidate_profile_df = candidate_profile_con.sql(
            """
            WITH latest_cbsa_profile AS (
                SELECT
                    cbsa_code,
                    year AS profile_year,
                    state_name_primary,
                    state_abbr_primary,
                    division_name,
                    region_name,
                    pop_total,
                    ROW_NUMBER() OVER (
                        PARTITION BY cbsa_code
                        ORDER BY year DESC
                    ) AS profile_row_number
                FROM mart_area_explorer.cbsa_profile_year
                WHERE is_metro
            )
            SELECT
                cf.cbsa_code,
                cf.cbsa_name,
                cf.frame_percentile_gap,
                cf.frame_percentile_sd,
                cf.overlap_profile,
                cf.half_alignment,
                cf.signature,
                cf.top_frame,
                cf.bottom_frame,
                cbsa.profile_year,
                cbsa.state_name_primary,
                cbsa.state_abbr_primary,
                cbsa.division_name,
                cbsa.region_name,
                cbsa.pop_total
            FROM mart_intelligence.intelligence_cross_frame AS cf
            LEFT JOIN latest_cbsa_profile AS cbsa
                ON cf.cbsa_code = cbsa.cbsa_code
                AND cbsa.profile_row_number = 1
            ORDER BY cf.cbsa_name
            """
        ).df()
        candidate_trajectory_long_df = candidate_profile_con.sql(
            """
            SELECT
                method_version,
                cbsa_code,
                cbsa_name,
                frame_id,
                coverage_status,
                trajectory_salience_percentile,
                signal_tier,
                trajectory_label
            FROM mart_intelligence.intelligence_trajectory_frame
            WHERE window_name = 'five_year'
              AND frame_id IN ('character', 'livability', 'opportunity')
            """
        ).df()
        candidate_turn_df = candidate_profile_con.sql(
            """
            SELECT
                method_version,
                cbsa_code,
                turn_status
            FROM mart_intelligence.intelligence_trajectory_turn_signals
            WHERE method_window_pair = 'five_year_vs_one_year'
              AND frame_id = 'opportunity'
            """
        ).df()

    for candidate_code_frame in (
        candidate_profile_df,
        candidate_trajectory_long_df,
        candidate_turn_df,
    ):
        candidate_code_frame["cbsa_code"] = candidate_code_frame["cbsa_code"].astype(str).str.zfill(5)

    candidate_method_versions = sorted(
        candidate_trajectory_long_df["method_version"].dropna().unique().tolist()
    )
    if len(candidate_method_versions) != 1:
        raise RuntimeError(
            "Candidate Scan requires exactly one current five-year trajectory method; "
            f"found {candidate_method_versions}."
        )
    candidate_method_version = candidate_method_versions[0]
    candidate_trajectory_long_df = candidate_trajectory_long_df.loc[
        candidate_trajectory_long_df["method_version"].eq(candidate_method_version)
    ].copy()
    candidate_turn_df = candidate_turn_df.loc[
        candidate_turn_df["method_version"].eq(candidate_method_version)
    ].copy()
    return (
        candidate_method_version,
        candidate_profile_df,
        candidate_trajectory_long_df,
        candidate_turn_df,
    )


@app.cell
def _(legacy_candidate_path, pd):
    # Legacy scores remain comparison evidence only. No current calculation
    # reads a legacy field or recreates the retired Phase 6 pattern logic.
    legacy_candidate_df = pd.read_csv(legacy_candidate_path, dtype={"cbsa_code": str})
    legacy_candidate_df["cbsa_code"] = legacy_candidate_df["cbsa_code"].str.zfill(5)
    legacy_comparison_df = legacy_candidate_df[
        ["cbsa_code", "candidate_rank", "candidate_score", "pattern_count"]
    ].rename(
        columns={
            "candidate_rank": "legacy_candidate_rank",
            "candidate_score": "legacy_candidate_score",
            "pattern_count": "legacy_pattern_count",
        }
    )
    return legacy_candidate_df, legacy_comparison_df


@app.cell
def _(candidate_profile_df, candidate_trajectory_long_df, candidate_turn_df, pd):
    # Pivot only stored five-year frame fields into the all-market scan. The
    # mean below is a local aggregation of engine-owned salience values, not a
    # replacement trajectory score or label.
    trajectory_wide_df = candidate_trajectory_long_df.pivot(
        index="cbsa_code",
        columns="frame_id",
        values=[
            "coverage_status",
            "trajectory_salience_percentile",
            "signal_tier",
            "trajectory_label",
        ],
    )
    trajectory_wide_df.columns = [
        f"{frame_id}_{field_name}"
        for field_name, frame_id in trajectory_wide_df.columns.to_flat_index()
    ]
    trajectory_wide_df = trajectory_wide_df.reset_index()
    candidate_base_df = candidate_profile_df.merge(
        trajectory_wide_df, on="cbsa_code", how="left", validate="one_to_one"
    ).merge(
        candidate_turn_df[["cbsa_code", "turn_status"]],
        on="cbsa_code",
        how="left",
        validate="one_to_one",
    )
    candidate_base_df["eligible_frame_count"] = (
        candidate_base_df[
            [
                "character_coverage_status",
                "livability_coverage_status",
                "opportunity_coverage_status",
            ]
        ]
        .eq("eligible")
        .sum(axis=1)
    )
    candidate_base_df["eligibility_status"] = candidate_base_df[
        "eligible_frame_count"
    ].map({3: "eligible"}).fillna("ineligible_five_year_coverage")
    salience_columns = [
        "character_trajectory_salience_percentile",
        "livability_trajectory_salience_percentile",
        "opportunity_trajectory_salience_percentile",
    ]
    candidate_base_df["trajectory_salience_mean"] = candidate_base_df[
        salience_columns
    ].mean(axis=1, skipna=False)
    return candidate_base_df, salience_columns


@app.cell
def _(candidate_base_df, legacy_comparison_df, pd):
    # This function keeps every rank contribution inspectable. Percentile ranks
    # use the current Profile universe, while only fully covered markets enter
    # the final candidate ordering.
    def percentile_rank_0_to_100(values):
        value_count = values.notna().sum()
        if value_count <= 1:
            return pd.Series(0.0, index=values.index)
        return (values.rank(method="min") - 1) / (value_count - 1) * 100

    def build_candidate_scores(divergence_weight, salience_weight, turn_weight):
        scored_df = candidate_base_df.copy()
        scored_df["divergence_percentile"] = percentile_rank_0_to_100(
            scored_df["frame_percentile_gap"]
        )
        scored_df["turn_signal_value"] = scored_df["turn_status"].map(
            {"confirmed_turn": 100.0, "emerging_turn_watch": 50.0}
        ).fillna(0.0)
        scored_df["turn_score_contribution"] = turn_weight * scored_df[
            "turn_signal_value"
        ]
        scored_df["candidate_score"] = (
            divergence_weight * scored_df["divergence_percentile"]
            + salience_weight * scored_df["trajectory_salience_mean"]
            + scored_df["turn_score_contribution"]
        )
        scored_df.loc[
            scored_df["eligibility_status"].ne("eligible"), "candidate_score"
        ] = pd.NA
        eligible_rank_order = scored_df.loc[
            scored_df["eligibility_status"].eq("eligible")
        ].sort_values(
            ["candidate_score", "frame_percentile_gap", "cbsa_name"],
            ascending=[False, False, True],
        )
        scored_df["candidate_rank"] = pd.NA
        scored_df.loc[eligible_rank_order.index, "candidate_rank"] = range(
            1, len(eligible_rank_order) + 1
        )
        return scored_df

    default_candidate_df = build_candidate_scores(0.45, 0.45, 0.10).merge(
        legacy_comparison_df, on="cbsa_code", how="left", validate="one_to_one"
    )
    return build_candidate_scores, default_candidate_df


@app.cell
def _(mo):
    mo.md("""
    # Position Candidate Scan

    This internal all-market surface prioritizes metros for analyst review.
    `candidate_scan_v1` combines current cross-frame divergence, stored
    five-year trajectory salience, and the stored Opportunity turn status.
    It is not a ranking of market quality, opportunity, or editorial
    importance, and it does not create an issue schedule.

    The retired Phase 6 Candidate List appears only as a comparison baseline.
    Current coverage, labels, and turn statuses always come from DuckDB.
    """)
    return


@app.cell
def _(mo):
    # The detailed scan is intentionally an analyst workbench, so this short
    # guide establishes a repeatable reading order before the dense tables.
    mo.md("""
    ## How to use this notebook

    1. **Narrow a plausible review pool** with the geography, population, and
       signal filters below. A rank is review priority under this method—not a
       verdict on market quality or opportunity.
    2. **Read the three visible inputs** in the ranked table: cross-frame
       divergence (unusual profile), trajectory salience (strength of recent
       movement, not always improvement), and the small Opportunity-turn
       contribution.
    3. **Select a market** in “Why this market surfaced” to see its stored
       frame evidence and compare a small shortlist.
    4. **Check weight sensitivity** before relying on a close call. Markets
       that remain near the top under reasonable alternatives are sturdier
       leads; large moves deserve more caution.

    Use legacy rank only to understand why the old and current methods differ.
    For a lighter first-look surface, open
    `POSITION_CANDIDATE_DISCOVERY_NOTEBOOK.py` in this folder.
    """)
    return


@app.cell
def _(candidate_method_version, candidate_profile_df, default_candidate_df, mo):
    # Coverage is shown before ranking so an analyst can see exactly which
    # markets were excluded from the score and why.
    coverage_summary_df = pd.DataFrame(
        [
            {"check": "Profile-universe markets", "value": len(candidate_profile_df)},
            {
                "check": "Eligible for candidate rank",
                "value": int(default_candidate_df["eligibility_status"].eq("eligible").sum()),
            },
            {
                "check": "Ineligible five-year coverage",
                "value": int(default_candidate_df["eligibility_status"].ne("eligible").sum()),
            },
            {"check": "Trajectory method", "value": candidate_method_version},
            {
                "check": "Latest population-profile year",
                "value": int(default_candidate_df["profile_year"].max()),
            },
        ]
    )
    mo.vstack(
        [
            mo.md("## Coverage and method"),
            mo.ui.table(coverage_summary_df, selection=None),
            mo.md(
                "A market without all three eligible five-year frame rows stays visible "
                "in coverage reporting but receives no candidate score or rank."
            ),
        ]
    )
    return coverage_summary_df


@app.cell
def _(default_candidate_df, mo):
    # Filters preserve the all-market orientation while narrowing the review
    # queue. Empty multi-selects intentionally mean "all available values."
    division_filter = mo.ui.multiselect(
        sorted(default_candidate_df["division_name"].dropna().unique().tolist()),
        label="Census division",
        full_width=True,
    )
    state_filter = mo.ui.multiselect(
        sorted(default_candidate_df["state_abbr_primary"].dropna().unique().tolist()),
        label="Primary state",
        full_width=True,
    )
    population_limits = default_candidate_df["pop_total"].dropna()
    population_filter = mo.ui.range_slider(
        start=int(population_limits.min()),
        stop=int(population_limits.max()),
        step=50000,
        value=[int(population_limits.min()), int(population_limits.max())],
        label="Population range",
        show_value=True,
        full_width=True,
    )
    overlap_filter = mo.ui.multiselect(
        sorted(default_candidate_df["overlap_profile"].dropna().unique().tolist()),
        label="Cross-frame context",
        full_width=True,
    )
    turn_filter = mo.ui.multiselect(
        sorted(default_candidate_df["turn_status"].dropna().unique().tolist()),
        label="Opportunity turn status",
        full_width=True,
    )
    eligibility_filter = mo.ui.radio(
        {"Eligible ranked markets": "eligible", "Include coverage exceptions": "all"},
        value="Eligible ranked markets",
        label="Coverage",
    )
    mo.vstack(
        [
            mo.md("## Filters"),
            mo.hstack([division_filter, state_filter], widths="equal"),
            population_filter,
            mo.hstack([overlap_filter, turn_filter, eligibility_filter], widths="equal"),
        ]
    )
    return (
        division_filter,
        eligibility_filter,
        overlap_filter,
        population_filter,
        state_filter,
        turn_filter,
    )


@app.cell
def _(
    default_candidate_df,
    division_filter,
    eligibility_filter,
    overlap_filter,
    population_filter,
    state_filter,
    turn_filter,
):
    filtered_candidate_df = default_candidate_df.copy()
    if division_filter.value:
        filtered_candidate_df = filtered_candidate_df.loc[
            filtered_candidate_df["division_name"].isin(division_filter.value)
        ]
    if state_filter.value:
        filtered_candidate_df = filtered_candidate_df.loc[
            filtered_candidate_df["state_abbr_primary"].isin(state_filter.value)
        ]
    filtered_candidate_df = filtered_candidate_df.loc[
        filtered_candidate_df["pop_total"].between(*population_filter.value)
    ]
    if overlap_filter.value:
        filtered_candidate_df = filtered_candidate_df.loc[
            filtered_candidate_df["overlap_profile"].isin(overlap_filter.value)
        ]
    if turn_filter.value:
        filtered_candidate_df = filtered_candidate_df.loc[
            filtered_candidate_df["turn_status"].isin(turn_filter.value)
        ]
    if eligibility_filter.value == "eligible":
        filtered_candidate_df = filtered_candidate_df.loc[
            filtered_candidate_df["eligibility_status"].eq("eligible")
        ]
    filtered_candidate_df = filtered_candidate_df.sort_values(
        ["candidate_rank", "cbsa_name"], na_position="last"
    )
    return (filtered_candidate_df,)


@app.cell
def _(filtered_candidate_df, mo, pd):
    candidate_display_columns = [
        "candidate_rank",
        "cbsa_name",
        "state_abbr_primary",
        "division_name",
        "pop_total",
        "candidate_score",
        "divergence_percentile",
        "trajectory_salience_mean",
        "turn_status",
        "turn_score_contribution",
        "overlap_profile",
        "signature",
        "legacy_candidate_rank",
    ]
    candidate_display_df = filtered_candidate_df[candidate_display_columns].rename(
        columns={
            "candidate_rank": "Rank",
            "cbsa_name": "Metro",
            "state_abbr_primary": "State",
            "division_name": "Division",
            "pop_total": "Population",
            "candidate_score": "v1 score",
            "divergence_percentile": "Divergence",
            "trajectory_salience_mean": "Trajectory salience",
            "turn_status": "Opportunity turn",
            "turn_score_contribution": "Turn contribution",
            "overlap_profile": "Profile context",
            "signature": "Signature",
            "legacy_candidate_rank": "Legacy rank",
        }
    )
    for numeric_column in [
        "Rank",
        "Population",
        "v1 score",
        "Divergence",
        "Trajectory salience",
        "Turn contribution",
        "Legacy rank",
    ]:
        candidate_display_df[numeric_column] = pd.to_numeric(
            candidate_display_df[numeric_column], errors="coerce"
        )
    mo.vstack(
        [
            mo.md(f"## Ranked candidates ({len(candidate_display_df):,} shown)"),
            mo.ui.dataframe(candidate_display_df, page_size=20),
        ]
    )
    return candidate_display_df, candidate_display_columns


@app.cell
def _(filtered_candidate_df, mo):
    selected_market_options = sorted(
        f"{row.cbsa_name} ({row.cbsa_code})"
        for row in filtered_candidate_df.itertuples(index=False)
    )
    selected_market_default = next(
        (label for label in selected_market_options if label.endswith("(40060)")),
        next(iter(selected_market_options), None),
    )
    selected_market_selector = mo.ui.dropdown(
        selected_market_options,
        value=selected_market_default,
        label="Why this market surfaced",
        searchable=True,
        full_width=True,
    )
    selected_market_selector
    return selected_market_selector, selected_market_options


@app.cell
def _(default_candidate_df, selected_market_selector):
    selected_candidate_code = selected_market_selector.value.rsplit("(", 1)[-1].rstrip(")")
    selected_candidate_df = default_candidate_df.loc[
        default_candidate_df["cbsa_code"].eq(selected_candidate_code)
    ].copy()
    return (selected_candidate_df,)


@app.cell
def _(mo, selected_candidate_df, pd):
    selected_candidate_row = selected_candidate_df.iloc[0]
    selected_explanation_df = pd.DataFrame(
        [
            {"signal": "Candidate rank", "value": selected_candidate_row["candidate_rank"]},
            {"signal": "v1 score", "value": selected_candidate_row["candidate_score"]},
            {
                "signal": "Cross-frame divergence percentile (45%)",
                "value": selected_candidate_row["divergence_percentile"],
            },
            {
                "signal": "Mean five-year salience percentile (45%)",
                "value": selected_candidate_row["trajectory_salience_mean"],
            },
            {
                "signal": "Opportunity turn contribution (10%)",
                "value": selected_candidate_row["turn_score_contribution"],
            },
            {"signal": "Stored Opportunity turn status", "value": selected_candidate_row["turn_status"]},
            {"signal": "Profile context", "value": selected_candidate_row["overlap_profile"]},
            {"signal": "Legacy rank (comparison only)", "value": selected_candidate_row["legacy_candidate_rank"]},
        ]
    )
    selected_frame_evidence_df = pd.DataFrame(
        [
            {
                "frame": frame_id.title(),
                "coverage": selected_candidate_row[f"{frame_id}_coverage_status"],
                "salience percentile": selected_candidate_row[
                    f"{frame_id}_trajectory_salience_percentile"
                ],
                "signal tier": selected_candidate_row[f"{frame_id}_signal_tier"],
                "trajectory label": selected_candidate_row[f"{frame_id}_trajectory_label"],
            }
            for frame_id in ["character", "livability", "opportunity"]
        ]
    )
    mo.vstack(
        [
            mo.md("## Why this market surfaced"),
            mo.ui.table(selected_explanation_df, selection=None),
            mo.md("### Stored five-year frame evidence"),
            mo.ui.table(selected_frame_evidence_df, selection=None),
        ]
    )
    return selected_explanation_df, selected_frame_evidence_df


@app.cell
def _(default_candidate_df, mo):
    shortlist_options = sorted(
        f"{row.cbsa_name} ({row.cbsa_code})"
        for row in default_candidate_df.loc[
            default_candidate_df["eligibility_status"].eq("eligible")
        ].sort_values("cbsa_name").itertuples(index=False)
    )
    shortlist_default = [
        label
        for label in shortlist_options
        if label.rsplit("(", 1)[-1].rstrip(")") in {"40060", "27260", "12060"}
    ]
    shortlist_selector = mo.ui.multiselect(
        shortlist_options,
        value=shortlist_default,
        label="Shortlist metros",
        max_selections=8,
        full_width=True,
    )
    shortlist_selector
    return shortlist_selector, shortlist_options


@app.cell
def _(default_candidate_df, mo, shortlist_selector):
    shortlist_codes = [
        selected_label.rsplit("(", 1)[-1].rstrip(")")
        for selected_label in shortlist_selector.value
    ]
    shortlist_df = default_candidate_df.loc[
        default_candidate_df["cbsa_code"].isin(shortlist_codes)
    ].sort_values("candidate_rank")
    shortlist_columns = [
        "candidate_rank",
        "cbsa_name",
        "candidate_score",
        "frame_percentile_gap",
        "trajectory_salience_mean",
        "turn_status",
        "overlap_profile",
        "signature",
        "legacy_candidate_rank",
    ]
    mo.vstack(
        [
            mo.md("## Shortlist comparison"),
            mo.ui.table(shortlist_df[shortlist_columns], selection=None),
        ]
    )
    return shortlist_df, shortlist_columns


@app.cell
def _(alt, build_candidate_scores, default_candidate_df, mo, pd):
    # Alternatives change only the declared editorial weights. They reuse the
    # same stored evidence and are shown as rank movement, never as a hidden
    # replacement of the default candidate method.
    sensitivity_specs = {
        "Divergence-heavy": (0.60, 0.30, 0.10),
        "Trajectory-heavy": (0.30, 0.60, 0.10),
        "No-turn-bonus": (0.50, 0.50, 0.00),
    }
    sensitivity_frames = []
    for sensitivity_name, weights in sensitivity_specs.items():
        sensitivity_df = build_candidate_scores(*weights)[
            ["cbsa_code", "candidate_rank"]
        ].rename(columns={"candidate_rank": "alternative_rank"})
        sensitivity_df["scenario"] = sensitivity_name
        sensitivity_frames.append(sensitivity_df)
    sensitivity_rank_df = pd.concat(sensitivity_frames, ignore_index=True).merge(
        default_candidate_df[["cbsa_code", "cbsa_name", "candidate_rank"]].rename(
            columns={"candidate_rank": "default_rank"}
        ),
        on="cbsa_code",
        how="left",
        validate="many_to_one",
    )
    sensitivity_rank_df["rank_change"] = (
        sensitivity_rank_df["default_rank"] - sensitivity_rank_df["alternative_rank"]
    )
    sensitivity_summary_df = (
        sensitivity_rank_df.groupby("scenario", as_index=False)
        .agg(
            median_absolute_rank_change=("rank_change", lambda values: values.abs().median()),
            largest_absolute_rank_change=("rank_change", lambda values: values.abs().max()),
        )
        .sort_values("scenario")
    )
    sensitivity_chart = (
        alt.Chart(
            sensitivity_rank_df.dropna(subset=["default_rank", "alternative_rank"]),
            title="Default rank versus alternative rank",
        )
        .mark_point(opacity=0.45)
        .encode(
            x=alt.X("default_rank:Q", title="Default v1 rank", scale=alt.Scale(reverse=True)),
            y=alt.Y("alternative_rank:Q", title="Alternative rank", scale=alt.Scale(reverse=True)),
            color=alt.Color("scenario:N", title="Scenario"),
            tooltip=["cbsa_name:N", "scenario:N", "default_rank:Q", "alternative_rank:Q", "rank_change:Q"],
        )
    )
    mo.vstack(
        [
            mo.md("## Weight sensitivity"),
            mo.md(
                "Alternatives are divergence-heavy (60/30/10), trajectory-heavy "
                "(30/60/10), and no-turn-bonus (50/50/0). Positive rank change means "
                "the market rises under that alternative."
            ),
            sensitivity_chart,
            mo.ui.table(sensitivity_summary_df, selection=None),
        ]
    )
    return sensitivity_chart, sensitivity_rank_df, sensitivity_summary_df


@app.cell
def _(candidate_base_df, candidate_profile_df, default_candidate_df, mo):
    # Lightweight in-notebook QA catches the failure modes that could make a
    # ranking look more authoritative than its inputs: duplicate markets,
    # missing scores, and ranks assigned to incomplete trajectory evidence.
    eligible_candidate_df = default_candidate_df.loc[
        default_candidate_df["eligibility_status"].eq("eligible")
    ]
    candidate_qa_df = pd.DataFrame(
        [
            {"check": "Profile CBSA rows", "value": len(candidate_profile_df)},
            {
                "check": "Duplicate Profile CBSA codes",
                "value": int(candidate_profile_df["cbsa_code"].duplicated().sum()),
            },
            {
                "check": "Duplicate candidate-base CBSA codes",
                "value": int(candidate_base_df["cbsa_code"].duplicated().sum()),
            },
            {
                "check": "Eligible markets missing candidate score",
                "value": int(eligible_candidate_df["candidate_score"].isna().sum()),
            },
            {
                "check": "Ineligible markets assigned a candidate rank",
                "value": int(
                    default_candidate_df.loc[
                        default_candidate_df["eligibility_status"].ne("eligible"),
                        "candidate_rank",
                    ].notna().sum()
                ),
            },
            {
                "check": "Duplicate eligible candidate ranks",
                "value": int(eligible_candidate_df["candidate_rank"].duplicated().sum()),
            },
            {
                "check": "Legacy rows missing from current universe",
                "value": int(default_candidate_df["legacy_candidate_rank"].isna().sum()),
            },
        ]
    )
    mo.vstack([mo.md("## QA appendix"), mo.ui.table(candidate_qa_df, selection=None)])
    return candidate_qa_df


if __name__ == "__main__":
    app.run()
