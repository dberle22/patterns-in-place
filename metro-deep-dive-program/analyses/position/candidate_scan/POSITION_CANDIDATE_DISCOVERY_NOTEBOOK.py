import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    # This is the light first-look companion to Candidate Scan. It reads the
    # same current marts and candidate_scan_v1 evidence, but does not expose
    # legacy comparison or method sensitivity controls.
    import os
    from pathlib import Path

    import altair as alt
    import duckdb
    import marimo as mo
    import pandas as pd

    return Path, alt, duckdb, mo, os, pd


@app.cell
def _(Path):
    discovery_dir = Path(__file__).resolve().parent
    discovery_repo_root = discovery_dir.parents[3]
    return discovery_dir, discovery_repo_root


@app.cell
def _(discovery_repo_root, os):
    # Resolve DB_PATH exactly as the other Position notebooks do, allowing the
    # notebook to run from any working directory without machine-specific code.
    def load_discovery_db_path() -> str:
        configured_path = os.environ.get("DB_PATH", "").strip()
        if configured_path:
            return configured_path

        renviron_path = discovery_repo_root / ".Renviron"
        if renviron_path.exists():
            for raw_line in renviron_path.read_text().splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key.strip() == "DB_PATH":
                    return value.strip()
        raise RuntimeError("DB_PATH is not set and could not be found in .Renviron.")

    return (load_discovery_db_path,)


@app.cell
def _(duckdb, load_discovery_db_path):
    # Profile establishes the market universe and filters. Trajectory and turn
    # fields remain engine-owned evidence; this notebook only combines them in
    # the transparent candidate_scan_v1 review-priority method.
    with duckdb.connect(load_discovery_db_path(), read_only=True) as discovery_con:
        discovery_profile_df = discovery_con.sql(
            """
            WITH latest_cbsa_profile AS (
                SELECT
                    cbsa_code,
                    state_abbr_primary,
                    division_name,
                    pop_total,
                    ROW_NUMBER() OVER (PARTITION BY cbsa_code ORDER BY year DESC) AS row_number
                FROM mart_area_explorer.cbsa_profile_year
                WHERE is_metro
            )
            SELECT
                cf.cbsa_code,
                cf.cbsa_name,
                cf.frame_percentile_gap,
                cf.overlap_profile,
                cf.signature,
                cbsa.state_abbr_primary,
                cbsa.division_name,
                cbsa.pop_total
            FROM mart_intelligence.intelligence_cross_frame AS cf
            LEFT JOIN latest_cbsa_profile AS cbsa
                ON cf.cbsa_code = cbsa.cbsa_code
                AND cbsa.row_number = 1
            ORDER BY cf.cbsa_name
            """
        ).df()
        discovery_trajectory_df = discovery_con.sql(
            """
            SELECT
                method_version,
                cbsa_code,
                frame_id,
                coverage_status,
                trajectory_salience_percentile,
                trajectory_label
            FROM mart_intelligence.intelligence_trajectory_frame
            WHERE window_name = 'five_year'
              AND frame_id IN ('character', 'livability', 'opportunity')
            """
        ).df()
        discovery_turn_df = discovery_con.sql(
            """
            SELECT method_version, cbsa_code, turn_status
            FROM mart_intelligence.intelligence_trajectory_turn_signals
            WHERE method_window_pair = 'five_year_vs_one_year'
              AND frame_id = 'opportunity'
            """
        ).df()
    return discovery_profile_df, discovery_trajectory_df, discovery_turn_df


@app.cell
def _(discovery_profile_df, discovery_trajectory_df, discovery_turn_df, pd):
    for discovery_code_frame in (
        discovery_profile_df,
        discovery_trajectory_df,
        discovery_turn_df,
    ):
        discovery_code_frame["cbsa_code"] = discovery_code_frame["cbsa_code"].astype(str).str.zfill(5)

    discovery_method_versions = sorted(
        discovery_trajectory_df["method_version"].dropna().unique().tolist()
    )
    if discovery_method_versions != ["trajectory_pilot_v1"]:
        raise RuntimeError(
            "Discovery notebook expects the current trajectory_pilot_v1 five-year contract; "
            f"found {discovery_method_versions}."
        )
    current_discovery_trajectory_df = discovery_trajectory_df.loc[
        discovery_trajectory_df["method_version"].eq("trajectory_pilot_v1")
    ].copy()
    current_discovery_turn_df = discovery_turn_df.loc[
        discovery_turn_df["method_version"].eq("trajectory_pilot_v1")
    ].copy()
    discovery_wide_df = current_discovery_trajectory_df.pivot(
        index="cbsa_code",
        columns="frame_id",
        values=["coverage_status", "trajectory_salience_percentile", "trajectory_label"],
    )
    discovery_wide_df.columns = [
        f"{frame_id}_{field_name}"
        for field_name, frame_id in discovery_wide_df.columns.to_flat_index()
    ]
    discovery_base_df = discovery_profile_df.merge(
        discovery_wide_df.reset_index(), on="cbsa_code", how="left", validate="one_to_one"
    ).merge(
        current_discovery_turn_df[["cbsa_code", "turn_status"]],
        on="cbsa_code",
        how="left",
        validate="one_to_one",
    )
    discovery_coverage_columns = [
        "character_coverage_status",
        "livability_coverage_status",
        "opportunity_coverage_status",
    ]
    discovery_salience_columns = [
        "character_trajectory_salience_percentile",
        "livability_trajectory_salience_percentile",
        "opportunity_trajectory_salience_percentile",
    ]
    discovery_base_df["eligible"] = discovery_base_df[
        discovery_coverage_columns
    ].eq("eligible").sum(axis=1).eq(3)
    discovery_base_df["divergence_percentile"] = (
        discovery_base_df["frame_percentile_gap"].rank(method="min") - 1
    ) / (discovery_base_df["frame_percentile_gap"].notna().sum() - 1) * 100
    discovery_base_df["trajectory_salience_mean"] = discovery_base_df[
        discovery_salience_columns
    ].mean(axis=1, skipna=False)
    discovery_base_df["turn_signal_value"] = discovery_base_df["turn_status"].map(
        {"confirmed_turn": 100.0, "emerging_turn_watch": 50.0}
    ).fillna(0.0)
    discovery_base_df["turn_contribution"] = 0.10 * discovery_base_df[
        "turn_signal_value"
    ]
    discovery_base_df["candidate_score"] = (
        0.45 * discovery_base_df["divergence_percentile"]
        + 0.45 * discovery_base_df["trajectory_salience_mean"]
        + discovery_base_df["turn_contribution"]
    )
    discovery_base_df.loc[~discovery_base_df["eligible"], "candidate_score"] = pd.NA
    discovery_rank_order = discovery_base_df.loc[
        discovery_base_df["eligible"]
    ].sort_values(["candidate_score", "frame_percentile_gap", "cbsa_name"], ascending=[False, False, True])
    discovery_base_df["candidate_rank"] = pd.NA
    discovery_base_df.loc[discovery_rank_order.index, "candidate_rank"] = range(
        1, len(discovery_rank_order) + 1
    )
    return discovery_base_df


@app.cell
def _(mo):
    mo.md("""
    # Markets to Explore Next

    This is the short first-look surface for choosing a metro worth an analyst
    conversation. It uses the same `candidate_scan_v1` evidence as the detailed
    Candidate Scan, but answers one question: **which markets look interesting
    enough to explore further, and why?**

    A high result does not mean a market is better. It means it combines an
    unusual current profile, substantial recent movement, or current Opportunity
    turn evidence in a way that merits a closer look.
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## A five-minute workflow

    1. Pick a **discovery lens** below: balanced leads, strong movement,
       unusual profiles, or Opportunity turns.
    2. Narrow by geography or population only if you have a real planning
       constraint.
    3. Scan the first 25 markets and select one to see the plain-language
       reason it appears.
    4. Add a few markets to the discussion shortlist. The detailed Candidate
       Scan is where you test close calls, legacy differences, and sensitivity.
    """)
    return


@app.cell
def _(discovery_base_df, mo):
    discovery_lens_selector = mo.ui.dropdown(
        {
            "Balanced leads": "balanced",
            "Strong recent movement": "movement",
            "Most unusual current profiles": "unusual",
            "Opportunity turns to inspect": "turns",
        },
        value="Balanced leads",
        label="Discovery lens",
        full_width=True,
    )
    discovery_division_filter = mo.ui.multiselect(
        sorted(discovery_base_df["division_name"].dropna().unique().tolist()),
        label="Census division",
        full_width=True,
    )
    discovery_population_values = discovery_base_df["pop_total"].dropna()
    discovery_population_filter = mo.ui.range_slider(
        start=int(discovery_population_values.min()),
        stop=int(discovery_population_values.max()),
        step=50000,
        value=[int(discovery_population_values.min()), int(discovery_population_values.max())],
        label="Population range",
        show_value=True,
        full_width=True,
    )
    mo.vstack(
        [
            mo.md("## Find a lead"),
            discovery_lens_selector,
            discovery_division_filter,
            discovery_population_filter,
        ]
    )
    return discovery_division_filter, discovery_lens_selector, discovery_population_filter


@app.cell
def _(
    discovery_base_df,
    discovery_division_filter,
    discovery_lens_selector,
    discovery_population_filter,
):
    discovery_filtered_df = discovery_base_df.loc[
        discovery_base_df["eligible"]
        & discovery_base_df["pop_total"].between(*discovery_population_filter.value)
    ].copy()
    if discovery_division_filter.value:
        discovery_filtered_df = discovery_filtered_df.loc[
            discovery_filtered_df["division_name"].isin(discovery_division_filter.value)
        ]
    if discovery_lens_selector.value == "movement":
        discovery_filtered_df = discovery_filtered_df.sort_values(
            ["trajectory_salience_mean", "candidate_score", "cbsa_name"],
            ascending=[False, False, True],
        )
    elif discovery_lens_selector.value == "unusual":
        discovery_filtered_df = discovery_filtered_df.sort_values(
            ["divergence_percentile", "candidate_score", "cbsa_name"],
            ascending=[False, False, True],
        )
    elif discovery_lens_selector.value == "turns":
        discovery_filtered_df = discovery_filtered_df.loc[
            discovery_filtered_df["turn_status"].isin(
                ["confirmed_turn", "emerging_turn_watch"]
            )
        ].sort_values(
            ["turn_contribution", "candidate_score", "cbsa_name"],
            ascending=[False, False, True],
        )
    else:
        discovery_filtered_df = discovery_filtered_df.sort_values(
            ["candidate_rank", "cbsa_name"], ascending=[True, True]
        )

    discovery_filtered_df["why_explore"] = "Balanced unusual profile and recent movement"
    discovery_filtered_df.loc[
        discovery_filtered_df["trajectory_salience_mean"].ge(75)
        & discovery_filtered_df["divergence_percentile"].lt(60),
        "why_explore",
    ] = "Strong recent movement worth explaining"
    discovery_filtered_df.loc[
        discovery_filtered_df["divergence_percentile"].ge(75)
        & discovery_filtered_df["trajectory_salience_mean"].lt(60),
        "why_explore",
    ] = "Unusual cross-frame profile worth explaining"
    discovery_filtered_df.loc[
        discovery_filtered_df["turn_status"].eq("confirmed_turn"), "why_explore"
    ] = "Confirmed Opportunity turn plus current profile evidence"
    return (discovery_filtered_df,)


@app.cell
def _(discovery_filtered_df, mo, pd):
    discovery_table_df = discovery_filtered_df.head(25)[
        [
            "candidate_rank",
            "cbsa_name",
            "state_abbr_primary",
            "candidate_score",
            "why_explore",
            "overlap_profile",
            "trajectory_salience_mean",
            "turn_status",
        ]
    ].rename(
        columns={
            "candidate_rank": "v1 rank",
            "cbsa_name": "Metro",
            "state_abbr_primary": "State",
            "candidate_score": "Review score",
            "why_explore": "Why take a look",
            "overlap_profile": "Profile context",
            "trajectory_salience_mean": "Recent movement",
            "turn_status": "Opportunity turn",
        }
    )
    for discovery_numeric_column in ["v1 rank", "Review score", "Recent movement"]:
        discovery_table_df[discovery_numeric_column] = pd.to_numeric(
            discovery_table_df[discovery_numeric_column], errors="coerce"
        )
    mo.vstack(
        [
            mo.md(
                f"## First 25 markets under this lens ({len(discovery_filtered_df):,} eligible matches)"
            ),
            # This is deliberately a compact, fixed first-look list. A static
            # table is more reliable and easier to scan here than the large
            # exploratory dataframe widget used in the detailed notebook.
            mo.ui.table(discovery_table_df, selection=None),
            mo.md(
                "These are prompts for an analyst conversation. Do not interpret "
                "a review score as a final claim about a market."
            ),
        ]
    )
    return (discovery_table_df,)


@app.cell
def _(discovery_filtered_df, mo):
    discovery_market_options = sorted(
        f"{row.cbsa_name} ({row.cbsa_code})"
        for row in discovery_filtered_df.itertuples(index=False)
    )
    discovery_market_default = next(
        (label for label in discovery_market_options if label.endswith("(40060)")),
        next(iter(discovery_market_options), None),
    )
    discovery_market_selector = mo.ui.dropdown(
        discovery_market_options,
        value=discovery_market_default,
        label="Explore one market",
        searchable=True,
        full_width=True,
    )
    discovery_market_selector
    return discovery_market_selector, discovery_market_options


@app.cell
def _(discovery_filtered_df, discovery_market_selector):
    # Use the code printed in the visible selector label. This avoids a
    # dictionary-widget value mismatch that could leave the detail view on its
    # initial Richmond selection after an analyst chose another market.
    discovery_selected_cbsa_code = discovery_market_selector.value.rsplit("(", 1)[-1].rstrip(")")
    discovery_selected_df = discovery_filtered_df.loc[
        discovery_filtered_df["cbsa_code"].eq(discovery_selected_cbsa_code)
    ].copy()
    return (discovery_selected_df,)


@app.cell
def _(alt, discovery_selected_df, mo, pd):
    discovery_selected_row = discovery_selected_df.iloc[0]
    discovery_reason_df = pd.DataFrame(
        [
            {"question": "Why is it on this screen?", "answer": discovery_selected_row["why_explore"]},
            {"question": "v1 review rank", "answer": discovery_selected_row["candidate_rank"]},
            {"question": "Profile context", "answer": discovery_selected_row["overlap_profile"]},
            {"question": "Profile signature", "answer": discovery_selected_row["signature"]},
            {"question": "Opportunity turn", "answer": discovery_selected_row["turn_status"]},
            {
                "question": "Next step",
                "answer": "Use the detailed Candidate Scan to compare a shortlist and test sensitivity.",
            },
        ]
    )
    discovery_component_df = pd.DataFrame(
        [
            {"component": "Unusual profile", "points": 0.45 * discovery_selected_row["divergence_percentile"]},
            {"component": "Recent movement", "points": 0.45 * discovery_selected_row["trajectory_salience_mean"]},
            {"component": "Opportunity turn", "points": discovery_selected_row["turn_contribution"]},
        ]
    )
    discovery_component_chart = (
        alt.Chart(
            discovery_component_df,
            title="Why this market's review score is where it is",
        )
        .mark_bar()
        .encode(
            x=alt.X("points:Q", title="Points in the v1 review score"),
            y=alt.Y("component:N", title=None, sort="-x"),
            color=alt.Color("component:N", legend=None),
            tooltip=["component:N", alt.Tooltip("points:Q", format=".1f")],
        )
    )
    mo.vstack(
        [
            mo.md(f"## {discovery_selected_row['cbsa_name']}"),
            mo.ui.table(discovery_reason_df, selection=None),
            discovery_component_chart,
        ]
    )
    return discovery_component_chart, discovery_component_df, discovery_reason_df


@app.cell
def _(discovery_filtered_df, mo):
    discovery_shortlist_options = sorted(
        f"{row.cbsa_name} ({row.cbsa_code})"
        for row in discovery_filtered_df.itertuples(index=False)
    )
    discovery_shortlist_selector = mo.ui.multiselect(
        discovery_shortlist_options,
        label="Markets to discuss next",
        max_selections=8,
        full_width=True,
    )
    discovery_shortlist_selector
    return discovery_shortlist_selector, discovery_shortlist_options


@app.cell
def _(discovery_filtered_df, discovery_shortlist_selector, mo):
    discovery_shortlist_codes = [
        selected_label.rsplit("(", 1)[-1].rstrip(")")
        for selected_label in discovery_shortlist_selector.value
    ]
    discovery_shortlist_df = discovery_filtered_df.loc[
        discovery_filtered_df["cbsa_code"].isin(discovery_shortlist_codes)
    ].sort_values("candidate_rank")
    mo.vstack(
        [
            mo.md("## Discussion shortlist"),
            mo.ui.table(
                discovery_shortlist_df[
                    [
                        "candidate_rank",
                        "cbsa_name",
                        "why_explore",
                        "candidate_score",
                        "overlap_profile",
                        "turn_status",
                    ]
                ],
                selection=None,
            ),
        ]
    )
    return (discovery_shortlist_df,)


@app.cell
def _(discovery_base_df, mo, pd):
    # Keep the light notebook honest about coverage without turning it into the
    # detailed scan's full QA appendix.
    discovery_coverage_df = pd.DataFrame(
        [
            {"check": "Markets in current Profile universe", "value": len(discovery_base_df)},
            {"check": "Markets eligible for a review rank", "value": int(discovery_base_df["eligible"].sum())},
            {"check": "Coverage exceptions", "value": int((~discovery_base_df["eligible"]).sum())},
        ]
    )
    mo.vstack([mo.md("## Coverage note"), mo.ui.table(discovery_coverage_df, selection=None)])
    return discovery_coverage_df


if __name__ == "__main__":
    app.run()
