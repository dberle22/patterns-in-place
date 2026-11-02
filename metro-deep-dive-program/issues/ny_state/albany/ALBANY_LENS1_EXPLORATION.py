import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium")

with app.setup:
    import json
    import sys
    from pathlib import Path

    import marimo as mo
    import pandas as pd

    HERE = Path(__file__).resolve().parent
    sys.path.insert(0, str(HERE))
    # Shared paths, layer loading and the scorecard helpers come from the piece's visuals notebook.
    from ALBANY_LENS1_VISUALS import (
        ACTIVITY_RULES,
        ANALYSES_DIR,
        ANCHOR_SOURCES,
        ANCHORS_CSV,
        CBSA_CODE,
        POI_RUN_DIR,
        SQL_DIR,
        ZONE_NAMES,
        color,
        connect_duckdb,
        load_metro_layers,
        metro_scorecard,
        run_sql,
        sql_list,
        to_geo,
        upstate_aggregate,
        upstate_sets,
    )
    # Exploration-only tables, maps and charts, shared with the other lenses' exploration notebooks.
    from albany_explore import (
        ACTIVITY_COLORS,
        ACTIVITY_ORDER,
        activity_profile,
        activity_surprises,
        adjusted_rand,
        all_jobs_centers,
        benchmark_bar_chart,
        benchmark_summary,
        benchmark_table,
        classify_migration,
        cluster_raw_profile,
        compare_centers,
        component_summary,
        county_matrix,
        explore_category_map,
        explore_map,
        explore_points,
        frame_peer_grid,
        glance_dot_plot,
        head_to_head,
        inbound_table,
        irs_flows_reversed,
        load_commute_flows,
        load_tract_profile,
        map_overlays,
        member_destinations,
        metric_strip_chart,
        migration_by_year,
        migration_counterparts,
        migration_summary,
        peer_shared_traits,
        peer_stats_table,
        poi_tract_clusters,
        tract_activity,
        trend_chart,
        zone_activity_crosstab,
        zone_place_summary,
        zone_stress_test,
    )



@app.cell
def _():
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Albany, Lens 1: Exploration

    Tables and quick maps that answer the outline's questions **before** we pick print
    visuals (rules: `issues/VISUALS_BUILD_RULES.md`, Phase 2: Explore). Nothing here is styled
    for print. Plan: `ALBANY_LENS1_VISUALS_BUILD_PLAN.md`.

    **Sections follow the article** (`ALBANY_LENS1_OUTLINE.md`, restructured 2026-10-26). The
    question IDs (Q1a, Q4g, …) are kept, because the plan and the reads refer to them. Each section
    ends with **Reads**: what the evidence says so far, to carry into the article.

    1. Albany Today: In a Nutshell (Q4a, Q4b, Q4e)
    2. A Bit of History (no data work)
    3. The Metro on the Map (Q1a, Q1b, Q1f, Q4f)
    4. What Kind of Place Is This? (Q4c, Q4g, Q4h, Q4i, Q4d)
    5. How It's Assembled (Q2, Q3)

    The commuting analysis banked for Lens 2 (Q1b–Q1e maps, Q1g, Q1h) lives in
    `ALBANY_LENS2_EXPLORATION.py`. The helpers live in `albany_explore.py`.
    """)
    return


@app.cell
def _():
    con = connect_duckdb()
    con.execute("LOAD spatial")
    layers = load_metro_layers(con)
    # City, CDP and village outlines: toggleable overlays on every interactive map.
    place_outlines = to_geo(run_sql(con, SQL_DIR / "metro_place_outlines.sql", cbsa_code=CBSA_CODE))
    tract_profile = load_tract_profile(con)
    return con, layers, place_outlines, tract_profile


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1. Albany Today: In a Nutshell (M.1)

    Grounding numbers for the opening and the peers: Albany's headline stats ranked among all
    **393 US metros** (2023 delineation; micros left out), the **13 NY metros**, and the **12
    Upstate metros**. Upstate is the series default: every county but the 10 Downstate ones (NYC,
    Long Island, Westchester, Putnam, Rockland; `downstate_core` in the What NY Is seed), so every
    NY metro but NYC's. The same scorecard feeds section 4.

    **Reading ranks:** rank 1 = the highest value, whatever the metric means. `position` says
    it in words: "lower than 72% of metros" for unemployment means 72% of metros have a
    higher rate. Each metric uses its source's latest complete year (column `year`): ACS
    2020–24 5-year (2024), BEA (2023), Zillow and FHFA (2025), LODES (2023), IRS (2022). Say so
    in the writing and the exhibits.

    **Reference columns:** NY State and US are published figures (blank where the source has
    no national total: BEA, LODES). **Upstate** is built from its 52 counties: exact for
    counts, growth and shares of jobs; marked **≈** where it is a population-weighted mean of
    county values (medians and person-level rates). The median metro is always shown. LODES
    skips about 23 metros (states not published for 2023), so their ranks are out of fewer.

    - **Q4e.** At a glance: the standard opening profile, two print forms
    - **Q4a.** Scorecard
    - **Q4b.** One metric at a time: where Albany sits among all metros (hover for names)

    **Status:** promoted → E0b percentile dots (visuals notebook, Albany Today: In a Nutshell).
    Dan picked the dots over the number cards (2026-10-27).
    """)
    return


@app.cell
def _():
    # Metric -> (label, format, group). Order here is the scorecard's order. Formats: see format_metric.
    q4_metrics = {
        "pop_total": ("Population", "count", "Size and growth"),
        "pop_growth_10yr": ("Population growth, 10 yr (ACS 2010–14 to 2020–24)", "change", "Size and growth"),
        "jobs_all_total": ("Jobs, all (LODES)", "count", "Size and growth"),
        "nominal_gdp_total": ("GDP (nominal)", "usd_big", "Size and growth"),
        "real_gdp_cagr_5yr": ("Real GDP growth, annual, 2019–24", "change", "Size and growth"),
        "irs_net_migration_rate": ("Net domestic migration rate (IRS)", "change", "Size and growth"),
        "median_hh_income": ("Median household income", "usd", "Income and output"),
        "calc_income_pc": ("Per capita income (BEA)", "usd", "Income and output"),
        "income_pc_growth_10yr": ("Per capita income growth, 2013–23", "change", "Income and output"),
        "rpp_real_pc_income": ("Per capita income, price-adjusted (RPP)", "usd", "Income and output"),
        "rpp_all_items": ("Regional price level (US = 100)", "index", "Income and output"),
        "nominal_gdp_pc": ("GDP per capita (workplace output / residents)", "usd", "Income and output"),
        "pov_rate": ("Poverty rate", "pct", "Income and output"),
        "median_home_value": ("Median home value (ACS)", "usd", "Housing"),
        "zhvi_annual_avg": ("Typical home value (Zillow, 2025)", "usd", "Housing"),
        "hpi_5yr_pct": ("Home price growth, 5 yr (FHFA, 2020–25)", "change", "Housing"),
        "value_to_income": ("Home value to income", "ratio", "Housing"),
        "median_gross_rent": ("Median gross rent", "usd", "Housing"),
        "owner_occ_rate": ("Owner-occupied homes", "pct", "Housing"),
        "pct_ba_plus": ("Adults with a bachelor's or higher", "pct", "People"),
        "median_age": ("Median age", "years", "People"),
        "pct_age_over_64": ("Age 65 and over", "pct", "People"),
        "pct_nonwhite": ("Non-white share (all but non-Hispanic white)", "pct", "People"),
        "pct_foreign_born": ("Foreign-born", "pct", "People"),
        "pct_moved_diff_st": ("Moved in from another state (past year)", "pct", "People"),
        "lfpr": ("Labor force participation", "pct", "Work"),
        "pct_unemployment_rate": ("Unemployment rate", "pct", "Work"),
        "public_job_share": ("Public-sector share of jobs (LODES)", "pct", "Work"),
        "private_health_share": ("Health care share of private jobs", "pct", "Work"),
        "private_education_share": ("Education share of private jobs", "pct", "Work"),
    }
    # How the Upstate column is built from its counties: (rule, exact). Rule is "sum", "growth"
    # (summed 2020-24 over summed 2010-14 population), or the metric to weight county values by.
    # Unlisted metrics are population-weighted means of county values, marked ≈.
    q4_upstate_rules = {
        "pop_total": ("sum", True),
        "jobs_all_total": ("sum", True),
        "nominal_gdp_total": ("sum", True),
        "pop_growth_10yr": ("growth", True),
        "public_job_share": ("jobs_all_total", True),
        "private_health_share": ("jobs_private_total", True),
        "private_education_share": ("jobs_private_total", True),
        "real_gdp_cagr_5yr": ("nominal_gdp_total", False),
        "pct_nonwhite": ("pop_total", True),
    }
    # At a glance: the standard opening profile (Dan, 2026-10-24). Not all economic on purpose.
    q4_glance_metrics = ["pop_total", "pop_growth_10yr", "median_hh_income", "calc_income_pc", "median_home_value",
                         "pct_ba_plus", "median_age", "pct_nonwhite"]
    return q4_glance_metrics, q4_metrics, q4_upstate_rules


@app.cell
def _(con, q4_metrics, q4_upstate_rules):
    # The IRS net migration rate reads directly since the 2026-10-26 direction fix; fail if the reversal returns.
    assert not irs_flows_reversed(con), "IRS migration flows look reversed again: see foundations/etl/gold/check_irs_migration_direction.sql"
    q4_scorecard_raw = run_sql(con, SQL_DIR / "q4_metro_scorecard.sql")
    # Upstate counties and metros, with their checks, from the visuals notebook (shared with Albany Today).
    q4_upstate_counties, q4_upstate_metros, q4_checks = upstate_sets(con, q4_scorecard_raw)
    q4_upstate = upstate_aggregate(q4_scorecard_raw, q4_upstate_counties, q4_metrics, q4_upstate_rules)
    q4_checks
    return q4_scorecard_raw, q4_upstate, q4_upstate_counties, q4_upstate_metros


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q4e. At a glance (prototype)

    The standard opening for every metro piece (N6): eight metrics, chosen to describe the
    place rather than only its economy. Two print forms to compare: number cards with ranks,
    and a percentile dot plot (Albany against the Upstate metros; hover for names). A radar was
    ruled out (Review 6). Edit `q4_glance_metrics` to change the set.
    """)
    return


@app.cell
def _(
    q4_glance_metrics,
    q4_metrics,
    q4_scorecard_raw,
    q4_upstate,
    q4_upstate_metros,
):
    _card = metro_scorecard(q4_scorecard_raw, {m: q4_metrics[m] for m in q4_glance_metrics}, q4_upstate_metros, q4_upstate)
    mo.vstack([
        mo.hstack([
            mo.stat(value=row["Albany"], label=row["metric"], bordered=True,
                    caption=f"#{row['US rank'].split(' of ')[0]} of {row['US rank'].split(' of ')[1]} US · "
                            f"#{row['Upstate rank'].split(' of ')[0]} of 12 Upstate")
            for _, row in _card.iterrows()
        ], wrap=True, justify="start"),
        glance_dot_plot(q4_scorecard_raw, {m: q4_metrics[m] for m in q4_glance_metrics}, q4_upstate_metros, q4_upstate),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q4a. Scorecard: Albany's ranks nationally, in New York, and Upstate
    """)
    return


@app.cell
def _(q4_metrics, q4_scorecard_raw, q4_upstate, q4_upstate_metros):
    q4_scorecard = metro_scorecard(q4_scorecard_raw, q4_metrics, q4_upstate_metros, q4_upstate)
    mo.ui.table(q4_scorecard, page_size=40, selection=None)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q4b. One metric: where Albany sits among all metros

    Every US metro is a dot (size metrics on a log scale). Upstate metros are labeled; hover
    any dot for its name, value and rank. The dashed line is the median metro.
    """)
    return


@app.cell
def _(q4_metrics):
    q4_strip_metric = mo.ui.dropdown(
        options={label: metric for metric, (label, _kind, _group) in q4_metrics.items()},
        value=q4_metrics["pct_ba_plus"][0], label="Metric",
    )
    return (q4_strip_metric,)


@app.cell
def _(q4_metrics, q4_scorecard_raw, q4_strip_metric, q4_upstate_metros):
    mo.vstack([
        q4_strip_metric,
        metric_strip_chart(q4_scorecard_raw, q4_strip_metric.value, q4_metrics[q4_strip_metric.value], q4_upstate_metros),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 2. A Bit of History

    No data work: Dan is writing it (review notes in `lens1_albany.md`).

    ## 3. The Metro on the Map (M.10)

    The print maps are built in the visuals notebook: E1v2 (the whole metro and the core
    detail), and E1b top places (towns, cities and the hamlets inside the towns). This section
    keeps the evidence behind them:

    - **Does every county belong** (Q1a, Q1f, Q1b): the high-level commuting test. The full
      commuting analysis is banked for **Lens 2** (Dan, 2026-10-24; M.13, M.14) and lives in
      `ALBANY_LENS2_EXPLORATION.py`.
    - **Key places** (Q4f): the landmark list behind the E1v2 maps.

    2023 LODES county OD, all jobs (JT00). Counts are **jobs**, not workers; a second job
    counts twice. Each flow links a home block to the employer's reported establishment,
    so long-distance flows include remote work and jobs reported at a headquarters
    address. Read anything past ~75 miles as "tied to an Albany employer", not as a daily
    commute.
    """)
    return


@app.cell
def _(con):
    commute_flows, commute_totals, commute_checks = load_commute_flows(con)
    assert commute_checks["passed"].all(), commute_checks
    commute_checks
    return commute_flows, commute_totals


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q1a. Where each metro county's residents work
    """)
    return


@app.cell
def _(commute_flows):
    member_destinations(commute_flows)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q1f. Inside the metro: county to county

    Share of each metro county's resident jobs by work county.
    """)
    return


@app.cell
def _(commute_flows):
    county_matrix(commute_flows)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q1b. Commuting in: counties outside the metro

    `share_to_core` is OMB's measure (share of the county's resident jobs in the three
    central counties); `share_to_metro` counts all five. Sorted by jobs; the distance-band
    table shows how far the draw reaches. The map of both directions is in the Lens 2 notebook.
    """)
    return


@app.cell
def _(commute_flows, commute_totals):
    _inbound = inbound_table(commute_flows, commute_totals)
    _bands = pd.cut(_inbound["miles"], [0, 25, 50, 75, 150, 300, 10_000],
                    labels=["<25 mi", "25–50", "50–75", "75–150", "150–300", "300+"])
    _inbound_bands = _inbound.groupby(_bands, observed=True).agg(
        counties=("county", "size"),
        jobs_to_metro=("jobs_to_metro", "sum"),
        counties_over_5pct=("share_to_metro", lambda s: int((s >= 0.05).sum())),
        private_jobs=("private_to_metro", "sum"),
    ).assign(
        share_of_inbound=lambda df: df["jobs_to_metro"] / df["jobs_to_metro"].sum(),
        # R33: if long-distance flows were state jobs reported at Albany addresses, this would spike with distance.
        public_share=lambda df: 1 - df["private_jobs"] / df["jobs_to_metro"],
    )
    mo.vstack([
        mo.md(f"**{_inbound['jobs_to_metro'].sum():,.0f}** jobs in the metro are held by people living outside it."),
        _inbound_bands,
        mo.ui.table(_inbound.head(60).round(3), page_size=20, selection=None),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Reads (draft, 2026-10-22; confirm in review):**

    - **The three central counties are one labor market.** Rensselaer and Schenectady
      residents hold more jobs in the other central counties (42%, 38%) than at home (28%, 33%).
      **Albany County is the hub:** Rensselaer residents hold more jobs in Albany County (39%)
      than at home (28%); Schenectady residents split evenly (34% Albany County, 33% home).
    - **Saratoga is a bridge, not an edge.** 39% of its residents' jobs are at home, 35% in
      the core, and it supplies most of the metro residents working in Glens Falls's counties
      (80% of them for Warren, 72% for Washington). Glens Falls draws on Saratoga, not on Albany.
    - **Schoharie is the loosest member.** Nearly half (49%) of its residents' jobs are outside
      the metro, and only 16% are in the core.
    - **A ring of six counties outside the metro sends 20–30% of its resident jobs in**
      (Montgomery, Washington, Warren, Fulton, Greene, Columbia). OMB gives five of them their
      own micro or metro areas inside the CSA; **Greene** has neither, and the tie runs both
      ways (20% of Greene's jobs are held by metro residents, mostly from Albany County).
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q4f. Key places (draft, for review)

    `reference/anchors.csv`: 35 key places in eight themes (review passed 2026-10-24), each with a source in
    `reference/anchor_sources.json` (Wikipedia primary coordinates; the Overture run where
    Wikipedia has none or points elsewhere; Waterford Flight reused from What NY Is). All are
    `keep=true` and inside the five counties. **Data review gate (R14):** Dan sets `keep` and
    flags any wrong point before any of them goes on a print map. Toggle themes in the legend.
    """)
    return


@app.cell
def _(layers, place_outlines):
    anchors = pd.read_csv(ANCHORS_CSV, dtype={"overture_id": str})
    _sources = pd.DataFrame(json.loads(ANCHOR_SOURCES.read_text())["sources"])
    anchors_review = anchors.merge(_sources, on="name", how="left")
    assert len(anchors_review) == len(anchors) and anchors_review["source_url"].notna().all(), "every anchor needs a source"
    mo.vstack([
        explore_points(
            anchors.rename(columns={"lat": "latitude", "lon": "longitude"}), color_col="theme", size=11,
            hover=["name", "place", "theme"], title="Draft key places by theme (keep = true for all, pending review)",
            overlays=map_overlays(layers, place_outlines), zoom=8.6,
        ),
        mo.ui.table(anchors_review[["name", "theme", "place", "kind", "keep", "coordinate_method", "source_url", "notes"]],
                    page_size=40, selection=None),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 4. What Kind of Place Is This? (M.1, M.3)

    Albany's national peers (without naming the cluster, N1), the second-city thread, and where its
    growth comes from. Uses the scorecard from section 1. The follow-ups, in Dan's priority order
    (2026-10-26): **Q4g** what the ten peers share, **Q4h** Albany, Buffalo and Rochester head to
    head, **Q4i** in-migration from the rest of New York. Q4j, the peer-method explainer, is
    writing; the regional shadow is an idea only (N3).

    - **Q4c.** Peers: the cross-frame list with raw stats, the frame-specific lists, the cluster on raw values (R32)
    - **Q4g.** What the peers share
    - **Q4h.** Head to head, with trends since 2012
    - **Q4i.** Migration by where the other end is
    - **Q4d.** Benchmark bars: one metric at a time, against metros you pick and the references
    """)
    return


@app.cell
def _():
    # Extra raw metrics for the peer profile (from the Intelligence marts; raw values, R32): (label, format, group).
    q4_peer_extra = {
        "pop_weighted_density_sqmi": ("Population-weighted density (per sq mi)", "count_plain", "Built form"),
        "pct_struct_multifam": ("Homes in multifamily buildings", "pct", "Built form"),
        "vacancy_rate": ("Housing vacancy rate", "pct", "Built form"),
        "permits_per_1000_housing_units": ("Building permits per 1,000 homes", "index", "Built form"),
        "pct_rent_burden_30plus": ("Renters paying 30%+ of income", "pct", "Built form"),
        "pct_hh_0_vehicles": ("Households without a car", "pct", "Getting around"),
        "pct_commute_wfh": ("Work from home", "pct", "Getting around"),
        "walkability_index": ("Walkability index (EPA)", "index", "Getting around"),
        "diversity_index": ("Diversity index", "ratio", "Community"),
        "social_associations_per_10k": ("Social associations per 10k", "index", "Community"),
        "civic_organizations_per_1000": ("Civic organizations per 1,000", "ratio", "Community"),
        "premature_death_rate": ("Premature death rate", "index", "Community"),
    }
    # Head-to-head metros (Q4h), in print order.
    q4_rivals = {"15380": "Buffalo", "40380": "Rochester", "45060": "Syracuse"}
    # IRS migration years (Q4i), pooled into an annual average. 2020–22 carry the pandemic moves.
    q4_mig_years = (2018, 2022)
    return q4_mig_years, q4_peer_extra, q4_rivals


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q4c. Peers

    Peer lists are cleared for print. **Cluster names stay out of Lens 1** (Dan, 2026-10-24):
    describe what the peers share instead; the national cluster naming review is future work.
    The first table is the cross-frame top 10 with the raw stats from Q4a. The second puts the
    frame-specific top 10s side by side, to see which peers hold across frames. The third
    profiles Albany's cluster on raw values (R32), against all metros.
    """)
    return


@app.cell
def _(con, q4_metrics, q4_scorecard_raw):
    q4_peer_list = run_sql(con, ANALYSES_DIR / "position" / "peers" / "queries" / "peer_list.sql", cbsa_code=CBSA_CODE)
    q4_clusters = run_sql(
        con, SQL_DIR / "peer_clusters.sql",
        cbsa_codes=sql_list(q4_scorecard_raw.loc[q4_scorecard_raw["geo_level"] == "cbsa", "geo_id"].unique()),
    ).set_index("cbsa_code")
    q4_peers = q4_peer_list.loc[q4_peer_list["peer_type"] == "cross_frame"]
    q4_albany_cluster = q4_clusters.loc[CBSA_CODE, "cross_frame_cluster_name"]
    _stats = ["pop_total", "pop_growth_10yr", "median_hh_income", "median_home_value", "pct_ba_plus", "public_job_share"]
    mo.vstack([
        mo.md(f"**Albany's cluster:** {q4_albany_cluster} ({q4_clusters.loc[CBSA_CODE, 'cross_frame_cluster_label']}), "
              f"{(q4_clusters['cross_frame_cluster_name'] == q4_albany_cluster).sum()} of {len(q4_clusters)} metros"),
        mo.md("**Cross-frame peers, with raw stats** (Albany first, for reference)"),
        peer_stats_table(q4_peers, q4_clusters, q4_scorecard_raw, {m: q4_metrics[m] for m in _stats}),
        mo.md("**Frame-specific peers** (top 10 per frame; * = also a cross-frame peer)"),
        frame_peer_grid(q4_peer_list),
    ])
    return q4_albany_cluster, q4_clusters, q4_peers


@app.cell
def _(q4_albany_cluster, q4_clusters, q4_metrics, q4_scorecard_raw):
    _profile_metrics = ["pop_total", "pop_growth_10yr", "median_hh_income", "median_home_value", "value_to_income",
                        "pct_ba_plus", "pov_rate", "median_age", "pct_foreign_born", "public_job_share", "real_gdp_cagr_5yr"]
    mo.vstack([
        mo.md(f"**{q4_albany_cluster}, on raw values** (medians; R32 check before printing the name)"),
        cluster_raw_profile(q4_scorecard_raw, q4_clusters, q4_albany_cluster, {m: q4_metrics[m] for m in _profile_metrics}),
        mo.md("**The 13 NY metros and their clusters**"),
        q4_clusters.loc[q4_clusters["cbsa_name"].str.contains(", NY")].reset_index()[
            ["cbsa_code", "cbsa_name", "cross_frame_cluster_name", "cross_frame_cluster_label"]],
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q4g. What Albany's ten peers share

    For every metric: how many of the ten cross-frame peers sit above the median US metro. **8 or
    more on one side** is a shared trait; the rest are mixed. Raw values (R32). The strip chart
    marks the peers among all metros. Peers are found on the *shape* of the profile across the
    three frames (cosine similarity), so shared traits are what the peers have in common, not
    what defines them one by one.
    """)
    return


@app.cell
def _(con, q4_metrics, q4_peer_extra, q4_peers, q4_scorecard_raw):
    q4_profile_raw = pd.concat([q4_scorecard_raw, run_sql(con, SQL_DIR / "q4_peer_extra_metrics.sql")], ignore_index=True)
    q4_profile_metrics = {**q4_metrics, **q4_peer_extra}
    q4_peer_codes = set(q4_peers["peer_cbsa_code"])
    q4_shared = peer_shared_traits(q4_profile_raw, q4_profile_metrics, q4_peer_codes)
    mo.vstack([
        mo.md(f"**{(q4_shared['verdict'] != 'Mixed').sum()} shared traits** out of {len(q4_shared)} metrics. "
              "`peers_above` counts peers above the median metro; percentiles are among US metros (100 = highest)."),
        mo.ui.table(q4_shared, page_size=45, selection=None),
    ])
    return q4_peer_codes, q4_profile_metrics, q4_profile_raw


@app.cell
def _(q4_profile_metrics):
    q4_peer_metric = mo.ui.dropdown(
        options={label: m for m, (label, _kind, _group) in q4_profile_metrics.items()},
        value=q4_profile_metrics["pct_age_over_64"][0], label="Metric",
    )
    return (q4_peer_metric,)


@app.cell
def _(q4_peer_codes, q4_peer_metric, q4_profile_metrics, q4_profile_raw):
    mo.vstack([
        q4_peer_metric,
        metric_strip_chart(q4_profile_raw, q4_peer_metric.value, q4_profile_metrics[q4_peer_metric.value], q4_peer_codes,
                           highlight_label="Albany's peers"),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q4h. Albany, Buffalo and Rochester head to head

    The second-city thread. Every scorecard metric for the big Upstate metros (Syracuse for
    context), with the leader and Albany's place among the four. "Leads" means the highest value,
    good or bad. Then the trends since 2012, indexed, to see whether the gaps are closing.
    """)
    return


@app.cell
def _(q4_metrics, q4_rivals, q4_scorecard_raw):
    q4_h2h = head_to_head(q4_scorecard_raw, q4_metrics, q4_rivals)
    _summary = (q4_h2h.assign(albany_first=lambda d: d["Albany place (of 4)"] == 1)
                .groupby("group", sort=False)
                .agg(metrics=("metric", "size"), albany_leads=("albany_first", "sum"),
                     buffalo_leads=("leader", lambda x: (x == "Buffalo").sum()), rochester_leads=("leader", lambda x: (x == "Rochester").sum()))
                .reset_index())
    mo.vstack([mo.md("**Who leads, by group**"), _summary, mo.ui.table(q4_h2h, page_size=40, selection=None)])
    return


@app.cell
def _(con, q4_rivals):
    q4_trends = run_sql(con, SQL_DIR / "q4_trends.sql", cbsa_codes=sql_list([CBSA_CODE, *q4_rivals]))
    q4_trend_metric = mo.ui.dropdown(
        options={"Population (ACS 5-year)": "pop_total", "Real GDP (BEA, chained 2017 $)": "real_gdp_total",
                 "Jobs, BEA employment": "employed", "Income per person (BEA)": "calc_income_pc"},
        value="Real GDP (BEA, chained 2017 $)", label="Metric",
    )
    q4_trend_index = mo.ui.switch(value=True, label="Index (2012 = 100)")
    return q4_trend_index, q4_trend_metric, q4_trends


@app.cell
def _(q4_rivals, q4_trend_index, q4_trend_metric, q4_trends):
    mo.vstack([
        mo.hstack([q4_trend_metric, q4_trend_index], justify="start"),
        trend_chart(q4_trends, q4_trend_metric.value, q4_trend_metric.selected_key, {CBSA_CODE: "Albany", **q4_rivals},
                    index=q4_trend_index.value),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q4i. Does Albany draw people from the rest of New York?

    IRS SOI county-to-county migration, pooled 2018–2022 into an annual average. **People =
    exemptions** (an approximation of persons; returns ≈ households). Flows into a metro's counties
    from counties outside it, and out of them, by where the other end is: **Downstate NY**
    (the series default), **Upstate NY** outside the metro, or **another state**.

    **Data bug found here, fixed 2026-10-26:** the warehouse stored IRS origin and destination reversed
    (`foundations/etl/IRS_MIGRATION_DIRECTION_FIX_SPEC.md`). It now reads them directly; a guard fails
    if the reversal comes back.

    **Second data issue, found 2026-10-27:** these views sum county *pairs*, and IRS suppresses pairs under
    20 returns, which are mostly moves to and from other states. On the IRS county totals (which include
    them), Albany loses about 1,500 people a year instead of gaining 1,500. The print numbers (E3, E4) use
    the totals (`data/irs_county_totals_2018_2022.csv`, visuals notebook); the views below still show pairs.
    National fix: `NATIONAL_FOLLOWUPS.md` N11.

    Caveats for print: IRS suppresses county pairs under 20 returns, so these totals undercount
    small, scattered flows (and international moves aren't here). Tax filers only. 2020–22 carry
    the pandemic moves, so the by-year table matters. And the scorecard's "net domestic migration
    rate" (Q4a) is net *households* per resident from the warehouse, not people.
    """)
    return


@app.cell
def _(con, q4_mig_years, q4_rivals, q4_scorecard_raw, q4_upstate_counties):
    assert not irs_flows_reversed(con), "IRS migration flows look reversed again: see foundations/etl/gold/check_irs_migration_direction.sql"
    _flows = run_sql(con, SQL_DIR / "q4_metro_migration.sql", cbsa_codes=sql_list([CBSA_CODE, *q4_rivals]),
                     year_from=str(q4_mig_years[0]), year_to=str(q4_mig_years[1]))
    _xwalk = con.sql(
        "SELECT d.geo_id AS county_geoid, d.geo_name AS other_county_name, x.cbsa_code AS other_cbsa, "
        "coalesce(x.cbsa_name, 'Not in a metro') AS other_cbsa_name "
        "FROM gold.dim_geo AS d LEFT JOIN silver.xwalk_cbsa_county AS x ON x.county_geoid = d.geo_id WHERE d.geo_level = 'county'"
    ).df()
    q4_mig = classify_migration(_flows, _xwalk, q4_upstate_counties)
    _pop = q4_scorecard_raw.loc[(q4_scorecard_raw["metric_id"] == "pop_total") & (q4_scorecard_raw["geo_level"] == "cbsa")].set_index("geo_id")["value"]
    q4_mig_summary = migration_summary(q4_mig, _pop, {CBSA_CODE: "Albany", **q4_rivals}, years=q4_mig_years[1] - q4_mig_years[0] + 1)
    mo.vstack([
        mo.md("**Annual average, people.** Per 1,000 residents uses ACS 2020–24 population. "
              "`avg_agi_*` is average adjusted gross income per household moving in or out."),
        q4_mig_summary,
        mo.md("**Albany by year: net people by where the other end is**"),
        migration_by_year(q4_mig, CBSA_CODE),
    ])
    return (q4_mig,)


@app.cell
def _(q4_mig):
    mo.vstack([
        mo.md("**Albany: the counties people come from and go to** (annual average 2018–22; net = in − out)"),
        mo.ui.table(migration_counterparts(q4_mig, CBSA_CODE), page_size=20, selection=None),
    ])
    return


@app.cell
def _(layers, place_outlines, q4_mig):
    _net = migration_counterparts(q4_mig, CBSA_CODE).set_index("county_geoid")
    _counties = layers["context"][["county_geoid", "county_name", "geometry"]].merge(_net.drop(columns=["county", "metro"]), left_on="county_geoid", right_index=True)
    explore_map(
        _counties, "net_per_year", id_col="county_geoid", name_col="county_name",
        hover={"in_per_year": "{:,.0f}", "out_per_year": "{:,.0f}", "net_per_year": "{:+,.0f}", "region": "{}"},
        colorscale="RdBu", tickformat="+,.0f", clip=(0, 0.97), zoom=6.2, tolerance=0.001, symmetric=True,
        title="Net people per year between each county and the Albany metro, 2018–22 (blue: Albany gains)",
        overlays=map_overlays(layers, place_outlines),
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q4d. Benchmark bars

    Albany against the metros you pick, the median of its 10 cross-frame peers, Upstate, NY
    State, the US and the median metro. The table under the chart holds every metric for the
    same rows. `q4_benchmark_metrics` keeps the default print candidates for the static version.
    """)
    return


@app.cell
def _(q4_metrics, q4_scorecard_raw):
    # Default print candidates (Dan, 2026-10-24: fine as defaults). The static exhibit uses these.
    q4_benchmark_metrics = ["median_hh_income", "pct_ba_plus", "median_home_value", "pop_growth_10yr",
                            "nominal_gdp_pc", "public_job_share"]
    _names = (q4_scorecard_raw.loc[q4_scorecard_raw["geo_level"] == "cbsa"].drop_duplicates("geo_id")
              .set_index("geo_name")["geo_id"].sort_index())
    q4_bench_metric = mo.ui.dropdown(
        options={label: metric for metric, (label, _kind, _group) in q4_metrics.items()},
        value=q4_metrics[q4_benchmark_metrics[0]][0], label="Metric",
    )
    q4_bench_metros = mo.ui.multiselect(
        options=_names.to_dict(), value=["Buffalo-Cheektowaga, NY", "Rochester, NY", "Syracuse, NY"], label="Compare with",
    )
    return q4_bench_metric, q4_bench_metros


@app.cell
def _(
    q4_bench_metric,
    q4_bench_metros,
    q4_metrics,
    q4_peers,
    q4_scorecard_raw,
    q4_upstate,
):
    _names = q4_scorecard_raw.drop_duplicates("geo_id").set_index("geo_id")["geo_name"]
    q4_benchmark = benchmark_table(
        q4_scorecard_raw, {code: _names[code] for code in q4_bench_metros.value}, list(q4_peers["peer_cbsa_code"]), q4_upstate,
    )
    mo.vstack([
        mo.hstack([q4_bench_metric, q4_bench_metros], justify="start"),
        benchmark_bar_chart(q4_benchmark, q4_bench_metric.value, q4_metrics[q4_bench_metric.value]),
        mo.md("**Every metric, same rows**"),
        mo.ui.table(benchmark_summary(q4_benchmark, q4_metrics), page_size=40, selection=None),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Reads (draft, 2026-10-26; confirm in review):**

    *Q4g, what the peers share.* 23 of 42 metrics are shared traits (8+ of the 10 peers on one side of the median metro).
    - **Albany's peers are older, educated, built-up legacy metros.** All ten are denser than the median metro and have
      more homes in multifamily buildings (Albany 36%, median metro 21%). Nine of ten have more households without a car,
      an older population, more foreign-born residents and higher income per person; all but one build little (permits per
      1,000 homes below the median) and have fewer owners.
    - **Where Albany breaks from its peers:** it gains people from the rest of the country while nine of its ten peers
      lose them, and its public-sector share (23.7%, 92nd percentile) is far above the peer median (14.6%).

    *Q4h, Albany vs Buffalo.*
    - **Buffalo is bigger; Albany is better off.** Buffalo leads on population (1.16M vs 906k), jobs and GDP. Among the
      four big Upstate metros Albany leads on income per person ($72k vs Buffalo's $61k), household income, bachelor's
      share, labor force participation and 10-year growth.
    - **The gap is closing.** Since 2012 Albany's real GDP grew 34%, Buffalo's 19%; Buffalo's lead shrank from $8.2B to
      $1.6B (2017 dollars). Population: +4.0% vs +2.3%.

    *Q4i, migration (IRS, 2018–22, after the direction fix).* **Superseded 2026-10-27:** on the IRS county
    totals Albany's net is about −1,500 a year (−1.6 per 1,000; Buffalo −2.4, Rochester −3.5, Syracuse −4.2):
    +2,500 Downstate, +1,100 rest of Upstate, −5,100 other states. The bullets below are pair-based.
    - **Albany draws people from the rest of New York.** It gained about 1,500 people a year from other US counties, the
      only big Upstate metro with a net gain (Buffalo −1,800, Rochester −2,200, Syracuse −1,500). It gains about 2,500 a
      year from Downstate (Queens +730, Brooklyn +440) and 1,300 from the rest of Upstate (mostly the Hudson Valley), and
      loses about 2,400 a year to other states (the Carolinas, Florida, Arizona). 86% of its in-movers come from New York.
    - **The pandemic tripled it.** The net gain was about 400 a year in 2018–19 and about 2,200 a year in 2020–22, almost
      all of the increase from Downstate. IRS years after 2022 will show whether it held.

    *Q4c and Q4d:* reads to write after Dan's look at the peers and benchmarks.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 5. How It's Assembled (M.2, M.9)

    Four cities, no center: where the jobs are (Q2) and what kinds of neighborhoods make up the
    metro (Q3). **Still to do** (plan, Q2 and Q3):

    - Q2: tract population density with the four city outlines; jobs per resident worker (all
      jobs); a table of the four cities and the larger CDPs (residents, resident workers, jobs);
      the corrected Q6 anchor table; the job center map with roads, rail, city outlines and key places
    - Q3: a POI corridor view (Q3a–c re-run on the promoted zones and Q3e built, 2026-10-27)

    ## Q2. Is there a center, or four cities?

    ### Q2a. Job centers on all jobs

    Q2's published centers (`mart_explanation_q2.job_center_candidates_v0`) use the
    warehouse's default LODES count, **private jobs only** (JT02). Albany is a state capital,
    so this reruns Q2's method **unchanged** (`apply_method`, same floors) on all jobs (JT00)
    for this metro only (`sql/q2_tracts_all_jobs.sql`). Q2's national mart is untouched.

    One interaction to state: the 1% market-share floor rises with the metro total
    (351k private → 460k all jobs, so about 3.5k → 4.6k jobs), which can drop small private
    centers even though their own jobs didn't change.
    """)
    return


@app.cell
def _(con):
    q2_all_candidates, q2_all_components, q2_private, q2_checks = all_jobs_centers(con)
    assert q2_checks["passed"].all(), q2_checks
    q2_checks
    return q2_all_candidates, q2_all_components, q2_private


@app.cell
def _(q2_all_candidates, q2_all_components, q2_private, tract_profile):
    q2_compare = compare_centers(q2_all_candidates, q2_private, tract_profile)
    mo.vstack([
        mo.md(f"**All jobs: {len(q2_all_components)} components, {int(q2_all_candidates['is_recommended_center'].sum())} tracts.** Private (published): 14 components, 35 tracts."),
        mo.md("**Components on all jobs**, with the places their tracts sit in and the public share of their jobs:"),
        component_summary(q2_all_candidates, tract_profile),
        mo.md("**Tracts whose center status changes:**"),
        q2_compare.loc[q2_compare["status"] != "Center in both"],
    ])
    return (q2_compare,)


@app.cell
def _(layers, place_outlines, q2_compare):
    explore_category_map(
        q2_compare, "status", id_col="tract_geoid", name_col="place",
        hover={"status": "{}", "jobs_total": "{:,.0f}", "private_jobs": "{:,.0f}", "public_share": "{:.0%}",
               "recommended_cluster_id": "{}", "private_component": "{}"},
        order=["Center in both", "Center on all jobs only", "Center on private jobs only", "Not a center"],
        colors={"Center in both": color("highlight.strength"), "Center on all jobs only": color("highlight.risk"),
                "Center on private jobs only": color("quadrant.low_high"), "Not a center": "#E4E7EB"},
        title="Job centers: all jobs vs private jobs (2023 LODES)", overlays=map_overlays(layers, place_outlines),
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q2b. Where the public jobs are

    Public share of each tract's jobs (all jobs minus private, 2023 LODES). Sets up Lens 4's
    "state as employer" story; here it explains why the private-only centers missed Albany's core.
    The picker also shows all and private jobs; the public share is blank under 500 jobs. Toggle
    the job-center outlines (all jobs, Q2a) in the legend.
    """)
    return


@app.cell
def _():
    q2_map_metric = mo.ui.dropdown(
        options={"Public share of jobs": "public_share", "All jobs": "jobs_total", "Private jobs": "private_jobs"},
        value="Public share of jobs", label="Measure",
    )
    return (q2_map_metric,)


@app.cell
def _(layers, place_outlines, q2_compare, q2_map_metric):
    _tracts = q2_compare.assign(public_share=q2_compare["public_share"].where(q2_compare["jobs_total"] >= 500))
    _centers = q2_compare.loc[q2_compare["status"].isin(["Center in both", "Center on all jobs only"])]
    _share = q2_map_metric.value == "public_share"
    mo.vstack([
        q2_map_metric,
        explore_map(
            _tracts, q2_map_metric.value, id_col="tract_geoid",
            hover={"place": "{}", "status": "{}", "jobs_total": "{:,.0f}", "private_jobs": "{:,.0f}", "public_share": "{:.0%}"},
            colorscale="Purples", tickformat=".0%" if _share else ",.0f", clip=(0, 0.98 if _share else 0.95),
            title=f"{q2_map_metric.selected_key} by tract (2023 LODES)",
            overlays=map_overlays(layers, place_outlines, extra={"Job centers, all jobs": (_centers, color("highlight.risk"), True)}),
        ),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Reads (draft, 2026-10-22; confirm in review):**

    - **The metro's biggest job tract is downtown Albany**: tract 36001001100, with 50k jobs,
      71% of them public (the Empire State Plaza area; confirm with anchors). Counting private
      jobs only, it looked like 14.5k.
    - **The largest center becomes one 13-tract, 96k-job band** from uptown Albany through
      Colonie and Wolf Road. It joins two uptown tracts that are mostly public (87% and 66%),
      likely the state office campus and the university (confirm with anchors).
    - **On all jobs there are 11 centers, not 14.** Six small private centers drop below the
      1% share floor as the metro total rises, Malta (GlobalFoundries) among them. Say this
      when comparing the two maps, or hold the floor at the private-jobs level as a check.
    - Public jobs aren't only downtown. Rural tracts show 40–60% public shares on small
      totals (schools, county seats).
    - From the Lens 2 sheds (Q1h): the uptown-to-Wolf-Road band is the **shared** center (median
      worker 11 miles away, drawn evenly from the four inner counties); Schenectady and Saratoga
      Springs run their own sheds; downtown's 50k jobs need the 75+ mile caveat (R33).
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Q3. How is the metro assembled?

    ### Q3a. What the Phase 7 labels actually describe

    Median raw tract values by zone type, nationally and in Albany. Raw means before
    imputation and before the model flips "bad" KPIs (poverty, rent burden, risk) so
    higher is better. The published centroid tables are on the flipped scale, which is
    easy to misread.
    """)
    return


@app.cell
def _(con):
    zone_profile = run_sql(con, SQL_DIR / "zone_profile.sql", cbsa_code=CBSA_CODE)
    zone_profile.round(3)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q3b. Without labels: the raw metrics by tract

    One map, a picker for the metric. These need no zone names, so they are print candidates
    if the labels aren't settled. Hover a tract to see all six values and its zone type.
    """)
    return


@app.cell
def _():
    # Metric -> (title, colorscale, hover format, colorbar tick format).
    tract_metrics = {
        "pct_ba_plus": ("Adults with a bachelor's or higher", "Blues", "{:.0%}", ".0%"),
        "median_hh_income": ("Median household income", "Greens", "${:,.0f}", "$,.0f"),
        "pov_rate": ("Poverty rate", "Reds", "{:.0%}", ".0%"),
        "owner_occ_rate": ("Owner-occupied homes", "Purples", "{:.0%}", ".0%"),
        "pct_age_over_64": ("Age 65 and over", "Oranges", "{:.0%}", ".0%"),
        "pop_weighted_density_sqmi": ("Population-weighted density (per sq mi)", "YlOrRd", "{:,.0f}", ",.0f"),
    }
    return (tract_metrics,)


@app.cell
def _(tract_metrics):
    tract_metric_pick = mo.ui.dropdown(
        options={title: metric for metric, (title, *_rest) in tract_metrics.items()},
        value=tract_metrics["pct_ba_plus"][0], label="Metric",
    )
    return (tract_metric_pick,)


@app.cell
def _(layers, place_outlines, tract_metric_pick, tract_metrics, tract_profile):
    _title, _scale, _fmt, _ticks = tract_metrics[tract_metric_pick.value]
    mo.vstack([
        tract_metric_pick,
        explore_map(
            tract_profile, tract_metric_pick.value, id_col="tract_geoid",
            hover={"place": "{}", "county_name": "{}", "zone_type": "{}", **{m: spec[2] for m, spec in tract_metrics.items()}},
            labels={m: spec[0] for m, spec in tract_metrics.items()},
            colorscale=_scale, tickformat=_ticks, title=f"{_title} by tract (ACS 2020–24)",
            overlays=map_overlays(layers, place_outlines),
        ),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q3c. Albany working names for the national zones

    The national clusters stay as they are; Albany gets plain-language **working names** that
    we test against the tracts as we go (Dan, 2026-10-22). The stress test lists the tracts
    each name fits worst. Edit `albany_zone_names` and the notes as the names firm up.
    """)
    return


@app.cell
def _():
    # National zone type -> (Albany working name, expectation). Edit ZONE_NAMES in the visuals notebook, which prints them.
    albany_zone_names = ZONE_NAMES
    return (albany_zone_names,)


@app.cell
def _(albany_zone_names, tract_profile):
    zone_names_used = tract_profile.assign(
        working_name=lambda df: df["zone_type"].map(lambda z: albany_zone_names[z][0])
    )
    zone_stress = zone_stress_test(zone_names_used)
    mo.vstack([
        mo.md("**Each working name: its tracts and where they are**"),
        zone_place_summary(zone_names_used),
        mo.md("**Worst fits: tracts furthest from their type's Albany median** (review these on the map)"),
        mo.ui.table(zone_stress.round(3), page_size=15, selection=None),
    ])
    return (zone_names_used,)


@app.cell
def _(layers, place_outlines, tract_metrics, zone_names_used):
    explore_category_map(
        zone_names_used, "working_name", id_col="tract_geoid", name_col="place",
        hover={"zone_type": "{}", "county_name": "{}", **{m: spec[2] for m, spec in tract_metrics.items()}},
        labels={m: spec[0] for m, spec in tract_metrics.items()},
        title="Zones by Albany working name (Phase 7, promoted 2026-10-23; names not cleared for print)",
        overlays=map_overlays(layers, place_outlines),
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q3d. What kinds of places are where? (POIs)

    Albany POI engine run (Overture 2026-10-21.0, 47,047 places, governed categories), read
    from the run's local files until it is published. POI counts reflect what Overture lists,
    which over-represents businesses with an online presence; read shares, not totals.

    - Category mix by working zone name (table)
    - **POI clusters:** tracts grouped by their category mix and POI density (k-means on
      shares of the top categories plus log density; tracts with fewer than
      `poi_min_per_tract` POIs are left out). A label-free alternative to the zones.
    - Dot maps for a few categories
    """)
    return


@app.cell
def _():
    poi_k = 5
    poi_min_per_tract = 15
    poi_cluster_categories = [
        "Services", "Retail", "Healthcare", "Food & Drink", "Personal Care", "Automotive",
        "Recreation & Fitness", "Education", "Community & Civic", "Industrial & Logistics",
        "Government & Public Safety", "Arts, Culture & Landmarks", "Lodging",
    ]
    poi_dot_categories = ["Education", "Healthcare", "Government & Public Safety", "Food & Drink"]
    return poi_cluster_categories, poi_dot_categories, poi_k, poi_min_per_tract


@app.cell
def _(con, zone_names_used):
    poi_counts = run_sql(con, SQL_DIR / "poi_tract_categories.sql", poi_run_dir=POI_RUN_DIR.as_posix())
    poi_by_zone = (
        poi_counts.merge(zone_names_used[["tract_geoid", "working_name"]], on="tract_geoid")
        .pivot_table(index="category", columns="working_name", values="pois", aggfunc="sum", fill_value=0)
    )
    poi_by_zone = (poi_by_zone / poi_by_zone.sum()).round(3)
    mo.vstack([mo.md(f"**{poi_counts['pois'].sum():,.0f}** POIs in **{poi_counts['tract_geoid'].nunique()}** tracts. Share of each zone's POIs by category:"), poi_by_zone])
    return (poi_counts,)


@app.cell
def _(
    layers,
    place_outlines,
    poi_cluster_categories,
    poi_counts,
    poi_k,
    poi_min_per_tract,
    zone_names_used,
):
    poi_clusters, poi_profile = poi_tract_clusters(
        poi_counts, zone_names_used, poi_cluster_categories, k=poi_k, min_pois=poi_min_per_tract
    )
    mo.vstack([
        explore_category_map(
            poi_clusters, "poi_cluster", id_col="tract_geoid", name_col="place",
            hover={"poi_cluster": "{}", "working_name": "{}", "pois": "{:,.0f}", "pois_per_sqmi": "{:,.0f}"},
            title="POI clusters: tracts grouped by what kinds of places they hold",
            overlays=map_overlays(layers, place_outlines),
        ),
        mo.md("**Cluster profiles** (mean category shares, median POI density, tracts, top places, zone overlap)"),
        poi_profile,
    ])
    return (poi_clusters,)


@app.cell
def _(con, poi_dot_categories):
    poi_points = run_sql(con, SQL_DIR / "poi_points.sql", poi_run_dir=POI_RUN_DIR.as_posix())
    poi_pick = mo.ui.multiselect(options=sorted(poi_points["category"].unique()), value=poi_dot_categories, label="Categories")
    return poi_pick, poi_points


@app.cell
def _(layers, place_outlines, poi_pick, poi_points):
    mo.vstack([
        poi_pick,
        explore_points(
            poi_points.loc[poi_points["category"].isin(poi_pick.value)], color_col="category",
            hover=["source_name", "category", "sub_category"],
            title="POIs by category (Overture 2026-10-21.0; click legend entries to toggle)",
            overlays=map_overlays(layers, place_outlines),
        ),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q3e. Who lives here, and what's there?

    The zones say **who lives in a tract** (the national clusters, on the 22 hard metrics; Albany working
    names). The POIs say **what's there**. Rather than cluster the two together, which would break the
    national comparison and pull Overture's coverage into the hard metrics, each tract keeps its zone and
    gets one of four **activity classes**, by plain rules (Dan, 2026-10-27):

    1. **More jobs than residents** (LODES all jobs, 2023): **Destination** if its destination POIs run at
       least `q3e_destination_lift` × the metro share, otherwise **Employment and industrial**.
    2. **Few POIs for its residents** (below the metro median per 1,000 residents): **Residential**.
    3. **A destination or industrial mix**: destination POIs (healthcare, education, government, arts and
       landmarks, lodging, nightlife) at `q3e_destination_lift` × the metro share, or industrial POIs
       (industrial and logistics, automotive, utilities, transportation) at `q3e_industrial_lift` ×:
       **Destination** or **Employment and industrial**.
    4. **Otherwise: Local-serving** (food, retail, personal care, services, banks).

    Shares are pulled toward the metro mix by `q3e_shrink` pseudo-POIs so small tracts don't swing on one
    listing. Agriculture is left out of the industrial bundle (it pulled farm tracts in). Residents are ACS
    2020–24; POIs are the same Overture run as Q3d, so read classes, not counts.
    """)
    return


@app.cell
def _():
    # Q3e rule settings, from ACTIVITY_RULES in the visuals notebook (E10's "What's there" column).
    # The activity cut is set from the data (metro median POIs per 1,000 residents) below.
    q3e_jobs_cut = ACTIVITY_RULES["jobs_cut"]
    q3e_destination_lift = ACTIVITY_RULES["destination_lift"]
    q3e_industrial_lift = ACTIVITY_RULES["industrial_lift"]
    q3e_shrink = ACTIVITY_RULES["shrink"]
    return q3e_destination_lift, q3e_industrial_lift, q3e_jobs_cut, q3e_shrink


@app.cell
def _(
    con,
    poi_counts,
    q3e_destination_lift,
    q3e_industrial_lift,
    q3e_jobs_cut,
    q3e_shrink,
    zone_names_used,
):
    _base = run_sql(con, SQL_DIR / "tract_activity_base.sql", cbsa_code=CBSA_CODE)
    _pois = poi_counts.loc[~poi_counts["category"].isin(["Unclassified", "Residential"])].groupby("tract_geoid")["pois"].sum()
    _per_1k = 1000 * _pois.reindex(_base["tract_geoid"]).fillna(0).to_numpy() / _base["residents"].clip(lower=100).to_numpy()
    q3e_activity_cut = float(pd.Series(_per_1k).median())
    # The zone inputs carry their own jobs_per_resident (private jobs); Q3e uses all jobs, so that one is dropped.
    q3e_tracts = zone_names_used.drop(columns="jobs_per_resident").merge(
        tract_activity(poi_counts, _base, shrink=q3e_shrink, activity_cut=q3e_activity_cut, jobs_cut=q3e_jobs_cut,
                       destination_lift=q3e_destination_lift, industrial_lift=q3e_industrial_lift),
        on="tract_geoid", how="left",
    )
    assert len(q3e_tracts) == 251 and q3e_tracts["activity"].notna().all(), "every metro tract should get an activity class"
    mo.vstack([
        mo.md(f"**Zone × activity: tracts (residents).** Residential cut: {q3e_activity_cut:.1f} POIs per 1,000 residents "
              f"(metro median). {q3e_tracts['residents'].sum():,.0f} residents, {q3e_tracts['jobs'].sum():,.0f} jobs."),
        zone_activity_crosstab(q3e_tracts),
        mo.md("**What each class looks like** (medians; residents and jobs are totals)"),
        activity_profile(q3e_tracts),
    ])
    return (q3e_tracts,)


@app.cell
def _(q3e_tracts):
    q3e_color_by = mo.ui.radio(options={"Activity class": "activity", "Zone (working name)": "working_name"},
                               value="Activity class", label="Color by", inline=True)
    q3e_zones = mo.ui.multiselect(options=sorted(q3e_tracts["working_name"].unique()),
                                  value=sorted(q3e_tracts["working_name"].unique()), label="Zones shown")
    return q3e_color_by, q3e_zones


@app.cell
def _(layers, place_outlines, q3e_color_by, q3e_tracts, q3e_zones):
    _by_activity = q3e_color_by.value == "activity"
    mo.vstack([
        mo.hstack([q3e_color_by, q3e_zones], justify="start"),
        explore_category_map(
            q3e_tracts.loc[q3e_tracts["working_name"].isin(q3e_zones.value)], q3e_color_by.value,
            id_col="tract_geoid", name_col="place",
            hover={"working_name": "{}", "activity": "{}", "residents": "{:,.0f}", "jobs": "{:,.0f}", "pois": "{:,.0f}",
                   "pois_per_1k": "{:,.1f}", "jobs_per_resident": "{:.2f}", "share_local": "{:.0%}",
                   "share_destination": "{:.0%}", "share_industrial": "{:.0%}"},
            labels={"working_name": "Zone", "activity": "Activity", "pois_per_1k": "POIs per 1,000 residents",
                    "jobs_per_resident": "Jobs per resident", "share_local": "Local-serving POIs",
                    "share_destination": "Destination POIs", "share_industrial": "Industrial POIs"},
            colors=ACTIVITY_COLORS if _by_activity else None, order=ACTIVITY_ORDER if _by_activity else None,
            title="Who lives here and what's there: zones by activity class (pick zones to show only those tracts)",
            overlays=map_overlays(layers, place_outlines),
        ),
    ])
    return


@app.cell
def _(poi_clusters, q3e_tracts):
    _both = q3e_tracts.merge(poi_clusters[["tract_geoid", "poi_cluster"]], on="tract_geoid")
    _k = _both.loc[~_both["poi_cluster"].str.startswith("Under")]
    mo.vstack([
        mo.md("**Tracts whose activity is rare for their zone** (under 15% of the zone's tracts): where who lives "
              "there and what's there part ways."),
        mo.ui.table(activity_surprises(q3e_tracts), page_size=15, selection=None),
        mo.md(f"**Check against the Q3d k-means clusters.** Agreement (adjusted Rand; 1 = same grouping, 0 = chance): "
              f"activity classes vs k-means **{adjusted_rand(_k['activity'], _k['poi_cluster']):.2f}**; "
              f"zones vs k-means **{adjusted_rand(_k['working_name'], _k['poi_cluster']):.2f}**; "
              f"zones vs activity **{adjusted_rand(q3e_tracts['working_name'], q3e_tracts['activity']):.2f}**."),
        pd.crosstab(_k["poi_cluster"], _k["activity"]).reindex(columns=[a for a in ACTIVITY_ORDER if a in set(_k["activity"])]),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Reads (re-run on the promoted zones, 2026-10-27; confirm in review):**

    *Q3a–c, the zones.*
    - **"Comfortable suburbs" is most of the metro:** 143 of 251 tracts and 557k of 906k residents
      (median income $102k, poverty 6%). The stress test still splits it: affluent suburbs (Loudonville
      $200k, poverty under 1%; town tracts near Niskayuna and in Saratoga County, $166–181k) sit with
      modest small-city neighborhoods (Watervliet, Mechanicville, inner Schenectady: $49–71k, poverty
      16–19%).
      Either a broader working name ("Middle neighborhoods") or an Albany-only split. Q3e splits it a
      different way, by what's there.
    - **"Rural and exurban" fits:** 36 of its 39 tracts are town areas outside any Census Place.
      "Lower-income urban" (32) and "Students and young professionals" (13) sit in the four cities'
      cores, as expected. "Working-class urban" is only 2 tracts here (Schenectady, Troy).
    - Albany's zones run close to the national medians for their type, with two departures: its
      "Lower-income urban" tracts are poorer and twice as dense (poverty 33% vs 27%, 8,400 vs 4,000
      per sq mi), and its "Professional mixed-use" tracts (was "Affluent urban") are less dense and less affluent ($88k vs $110k).

    *Q3d, POIs.* The k-means clusters mostly sort by density, with one functional cluster, **P4,
    healthcare-heavy** (25 tracts). Q3e recovers it as Destination (15 of P4's 25), and the rest of the
    k-means grouping matches neither the zones nor the activity classes (agreement 0.08 and 0.06).
    Suggest retiring the k-means for print and keeping Q3e.

    *Q3e, who lives here and what's there.*
    - **The two layers are close to independent** (agreement 0.06), so activity adds what the zones
      can't see. Half the metro's residents (51%) live in Residential tracts, which hold 19% of the jobs.
    - **Jobs gather in a few active tracts.** Employment and industrial plus Destination tracts are 48
      of 251 and 17% of residents but 58% of jobs (267k of 460k).
    - **Comfortable suburbs come in four kinds:** 76 Residential, 45 Local-serving, 14 Employment
      and industrial and 8 Destination. The employment tracts are the suburban job districts: the
      airport and Wolf Road (15k jobs in one tract), Colonie Center, Crossgates, Washington Avenue
      Extension, the Harriman state office campus, and the Northway retail in Clifton Park and Wilton.
      The destinations are St. Peter's Hospital, Corporate Woods, Skidmore and the race course, and
      Saratoga Hospital's offices. The four kinds barely differ on income or poverty ($93–107k,
      5–7%), so the split is about function, not class.
    - **The other Destinations are the hospitals and campuses:** Albany Med, Albany Medical College
      and the VA (17k jobs, 65% destination POIs), the University at Albany, RPI and Samaritan
      Hospital in Troy, and Union College with Ellis Hospital in Schenectady. (Names from the POIs in
      each tract; confirm with the Q4f anchors.)
    - **Downtown Albany (the Capitol and Empire State Plaza) sits in "Students and young
      professionals"** by its 2,065 residents, but holds 50k jobs (24 per resident). Zone types describe who lives in a tract, so the job centers (Q2)
      need the activity layer, or their own map, to show up.
    - Healthcare and food POIs line up along a few arterial corridors; worth a corridor view once the
      roads layer is in.
    """)
    return


if __name__ == "__main__":
    app.run()
