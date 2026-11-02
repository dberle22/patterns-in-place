import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")

with app.setup:
    import sys
    from pathlib import Path

    import marimo as mo
    import pandas as pd

    HERE = Path(__file__).resolve().parent
    # Queries only this lens uses; shared ones are in SQL_DIR (albany/sql/).
    LENS_SQL_DIR = HERE / "sql"
    sys.path.insert(0, str(HERE.parent))
    # Shared paths and layer loading.
    from albany_common import (
        CBSA_CODE,
        SQL_DIR,
        color,
        connect_duckdb,
        load_metro_layers,
        run_sql,
        sql_list,
        to_geo,
    )
    # Exploration-only tables, maps and charts, shared with the other lenses' exploration notebooks.
    from albany_explore import (
        all_jobs_centers,
        center_shed_shares,
        center_workforce_table,
        city_matrix,
        explore_category_map,
        explore_map,
        external_metro_pull,
        inbound_table,
        load_commute_flows,
        load_tract_profile,
        map_overlays,
        metro_reach,
        outbound_table,
    )


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Albany, Part 2: Exploration

    Commuting and regional role (M.13, M.14). **Banked from Lens 1** (Dan, 2026-10-24): Lens 1
    keeps only the high-level "does every county belong" test (its Q1a, Q1b table and Q1f). Moved
    here unchanged on 2026-10-26, so the question IDs (Q1b–Q1h) still match the Lens 1 build plan
    and its reads. This began as the Lens 2 notebook and is the starting point for Part 2
    (vault: metro_deep_dives/albany/part_2/), which has no build plan yet.

    Rules: `issues/VISUALS_BUILD_RULES.md`. Helpers: `albany_explore.py`.

    2023 LODES county OD, all jobs (JT00). Counts are **jobs**, not workers; a second job
    counts twice. Each flow links a home block to the employer's reported establishment,
    so long-distance flows include remote work and jobs reported at a headquarters
    address. Read anything past ~75 miles as "tied to an Albany employer", not as a daily
    commute.

    - **Q1b.** Which counties outside the metro send workers in, and from how far?
    - **Q1c.** Which counties outside the metro draw workers *from* Albany's counties?
    - **Q1d.** Statewide: which metro pulls each NY county?
    - **Q1e.** How far does each NY metro reach?
    - **Q1g.** The four cities: who works where they live?
    - **Q1h.** Tract-level sheds: where each job center's workers live
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


@app.cell
def _(con):
    commute_flows, commute_totals, commute_checks = load_commute_flows(con)
    assert commute_checks["passed"].all(), commute_checks
    commute_checks
    return commute_flows, commute_totals


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q1b. Commuting in: counties outside the metro

    `share_to_core` is OMB's measure (share of the county's resident jobs in the three
    central counties); `share_to_metro` counts all five. Sorted by jobs; the distance-band
    table shows how far the draw reaches.
    """)
    return


@app.cell
def _(commute_flows, commute_totals):
    inbound = inbound_table(commute_flows, commute_totals)
    _bands = pd.cut(inbound["miles"], [0, 25, 50, 75, 150, 300, 10_000],
                    labels=["<25 mi", "25–50", "50–75", "75–150", "150–300", "300+"])
    inbound_bands = inbound.groupby(_bands, observed=True).agg(
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
        mo.md(f"**{inbound['jobs_to_metro'].sum():,.0f}** jobs in the metro are held by people living outside it."),
        inbound_bands,
        mo.ui.table(inbound.head(60).round(3), page_size=20, selection=None),
    ])
    return (inbound,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q1c. Commuting out: counties that draw from Albany's counties

    `share_of_county_jobs` is how much of that county's workforce lives in the Albany
    metro: the reverse test (is Albany a labor shed for it?). `top_sender` is the metro
    county supplying the most.
    """)
    return


@app.cell
def _(commute_flows, commute_totals):
    outbound = outbound_table(commute_flows, commute_totals)
    mo.vstack([
        mo.md(f"**{outbound['metro_resident_jobs'].sum():,.0f}** jobs held by metro residents are outside the metro."),
        mo.ui.table(outbound.head(40).round(3), page_size=20, selection=None),
    ])
    return (outbound,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Map, both directions.** Pick a view; zoom and pan; click legend entries to toggle the
    overlays. Hover a county for its numbers. Metro counties are left unshaded.
    """)
    return


@app.cell
def _():
    commute_map_view = mo.ui.dropdown(
        options={
            "In: share of each county's resident jobs located in the metro": "in",
            "Out: share of each county's jobs held by metro residents": "out",
        },
        value="In: share of each county's resident jobs located in the metro",
        label="View",
    )
    return (commute_map_view,)


@app.cell
def _(commute_map_view, inbound, layers, outbound, place_outlines):
    if commute_map_view.value == "in":
        _table, _value, _scale = inbound, "share_to_metro", "Blues"
        _hover = {"share_to_metro": "{:.1%}", "jobs_to_metro": "{:,.0f}", "share_to_core": "{:.1%}", "miles": "{:,.0f}"}
    else:
        _table, _value, _scale = outbound, "share_of_county_jobs", "Oranges"
        _hover = {"share_of_county_jobs": "{:.1%}", "metro_resident_jobs": "{:,.0f}", "top_sender": "{}", "miles": "{:,.0f}"}
    _counties = layers["context"][["county_geoid", "geometry"]].merge(_table, on="county_geoid")
    mo.vstack([
        commute_map_view,
        explore_map(
            _counties, _value, id_col="county_geoid", name_col="county", hover=_hover, colorscale=_scale,
            tickformat=".0%", title=commute_map_view.selected_key, clip=(0, 0.97), zoom=6.4, tolerance=0.001,
            overlays=map_overlays(layers, place_outlines),
        ),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q1d. Statewide: which metro pulls each county?

    For every NY county: the CBSA other than its own that holds the most of its residents'
    jobs, and that share (color = which metro, depth = how strong). The second map leaves out
    the NYC metro, whose statewide pull is largely the remote-work and single-address effect
    (R33). Counties in no CBSA have no "own" metro, so every metro counts as external.
    """)
    return


@app.cell
def _(con):
    county_by_cbsa = run_sql(con, LENS_SQL_DIR / "county_jobs_by_cbsa.sql")
    pull_all = external_metro_pull(county_by_cbsa)
    pull_no_nyc = external_metro_pull(county_by_cbsa, exclude={"35620"})
    _review = pull_all.merge(
        pull_no_nyc[["home_county_geoid", "top_external", "top_external_share"]],
        on="home_county_geoid", suffixes=("", "_without_nyc"),
    )
    mo.ui.table(_review.round(3), page_size=20, selection=None)
    return county_by_cbsa, pull_all, pull_no_nyc


@app.cell
def _():
    pull_map_view = mo.ui.dropdown(
        options={
            "Largest outside metro for each county's resident jobs": "all",
            "Largest outside metro, leaving out NYC": "no_nyc",
            "Share of each county's resident jobs in the Albany metro": "albany",
        },
        value="Largest outside metro, leaving out NYC", label="View",
    )
    return (pull_map_view,)


@app.cell
def _(layers, place_outlines, pull_all, pull_map_view, pull_no_nyc):
    _pull = pull_no_nyc if pull_map_view.value == "no_nyc" else pull_all
    _counties = layers["context"].loc[layers["context"]["state_fips"] == "36", ["county_geoid", "county_name", "geometry"]].merge(
        _pull, left_on="county_geoid", right_on="home_county_geoid")
    _hover = {"top_external": "{}", "top_external_share": "{:.1%}", "albany_share": "{:.1%}", "own_cbsa_share": "{:.1%}"}
    if pull_map_view.value == "albany":
        _map = explore_map(_counties, "albany_share", id_col="county_geoid", name_col="county_name", hover=_hover,
                           colorscale="Blues", tickformat=".0%", clip=(0, 0.97), zoom=6.0, tolerance=0.001,
                           title=pull_map_view.selected_key, overlays=map_overlays(layers, place_outlines))
    else:
        _map = explore_category_map(_counties.fillna({"top_external": "None"}), "top_external", id_col="county_geoid",
                                    name_col="county_name", hover=_hover, zoom=6.0, tolerance=0.001,
                                    title=f"{pull_map_view.selected_key} (hover for the share)",
                                    overlays=map_overlays(layers, place_outlines))
    mo.vstack([pull_map_view, _map])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q1e. How far does each NY metro reach?

    For each metro with NY counties: `jobs_held_by_other_ny_residents` is the jobs located in
    the metro that are held by residents of NY counties outside it, and `share_of_metro_jobs`
    is that over all the metro's jobs (LODES WAC, all jobs). The `counties_*` columns count the
    NY counties outside it that send at least 5%, 10% or 25% of their resident jobs there.
    NY homes only (the county OD here starts from NY residents), so out-of-state commuters
    (Berkshire, Bennington) are not counted; the long-distance tail (R33) is.
    """)
    return


@app.cell
def _(con, county_by_cbsa):
    _metro_jobs = con.sql(
        "SELECT geo_id, jobs_all_total FROM gold.economics_lodes_wide WHERE geo_level = 'cbsa' AND year = 2023"
    ).df().set_index("geo_id")["jobs_all_total"]
    metro_reach(county_by_cbsa, _metro_jobs)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q1g. The four cities: who works where they live?

    2023 LODES OD at Census Place grain. "Outside any place" means a home or job in a town
    area that isn't a Census Place (common in NY), so its location is unknown at this grain.
    """)
    return


@app.cell
def _():
    # City -> Census Place GEOID.
    four_cities = {"Albany": "3601000", "Schenectady": "3665508", "Troy": "3675484", "Saratoga Springs": "3665255"}
    return (four_cities,)


@app.cell
def _(con, four_cities):
    place_flows = run_sql(con, LENS_SQL_DIR / "place_flows.sql", place_geoids=sql_list(four_cities.values()))
    mo.vstack([
        mo.md("**Where each city's residents work** (share of the city's resident jobs)"),
        city_matrix(place_flows, four_cities, side="home"),
        mo.md("**Who holds each city's jobs** (share of the jobs located in the city)"),
        city_matrix(place_flows, four_cities, side="work"),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Q1h. Tract-level sheds: where each job center's workers live

    2023 LODES tract-to-tract OD, all jobs (JT00), built for Albany by the commute-sheds engine
    (`either_endpoint`: every flow with a home or a job in the metro; 49 states' aux files,
    AK and MI unpublished for 2023). Centers are the **all-jobs** components from Lens 1's Q2a
    (the same `all_jobs_centers` run).

    - Table: each center's jobs, where its workers live (metro county or outside), and how far
      (jobs-weighted median miles from home tract to the center)
    - Maps: for every metro tract, the share of its residents' jobs located in that center
    """)
    return


@app.cell
def _(con):
    q2_all_candidates, _components, _private, q2_checks = all_jobs_centers(con)
    assert q2_checks["passed"].all(), q2_checks
    tract_flows = run_sql(con, LENS_SQL_DIR / "tract_flows.sql", cbsa_code=CBSA_CODE, job_type="JT00")
    tract_flow_checks = pd.DataFrame({
        "check": ["flows touching the metro (jobs)", "tract pairs", "home tracts without geometry (jobs)"],
        "value": [f"{tract_flows['jobs'].sum():,.0f}", f"{len(tract_flows):,}", f"{tract_flows.loc[tract_flows['home_lon'].isna(), 'jobs'].sum():,.0f}"],
    })
    tract_flow_checks
    return q2_all_candidates, tract_flows


@app.cell
def _():
    # All-jobs component (Lens 1, Q2a) -> label. Check labels against the component table there.
    shed_centers = {
        "10580_c002": "Downtown Albany",
        "10580_c001": "Uptown Albany to Wolf Road",
        "10580_c010": "Schenectady",
        "10580_c008": "Saratoga Springs",
    }
    return (shed_centers,)


@app.cell
def _(layers, q2_all_candidates, shed_centers, tract_flows):
    center_tracts = {
        label: set(q2_all_candidates.loc[q2_all_candidates["recommended_cluster_id"] == cid, "tract_geoid"])
        for cid, label in shed_centers.items()
    }
    center_workforce_table(tract_flows, center_tracts, layers["counties"])
    return (center_tracts,)


@app.cell
def _(shed_centers):
    shed_center_pick = mo.ui.dropdown(options=list(shed_centers.values()), value="Uptown Albany to Wolf Road", label="Job center")
    return (shed_center_pick,)


@app.cell
def _(center_tracts, layers, place_outlines, shed_center_pick, tract_flows, tract_profile):
    _center = center_tracts[shed_center_pick.value]
    _tracts = tract_profile[["tract_geoid", "place", "county_name", "geometry"]].assign(
        share_to_center=center_shed_shares(tract_flows, _center, tract_profile)
    )
    mo.vstack([
        shed_center_pick,
        explore_map(
            _tracts, "share_to_center", id_col="tract_geoid", hover={"place": "{}", "county_name": "{}", "share_to_center": "{:.1%}"},
            colorscale="Blues", tickformat=".0%", clip=(0, 0.98),
            title=f"{shed_center_pick.value}: share of each tract's resident jobs located in the center",
            overlays=map_overlays(layers, place_outlines, extra={
                "Center tracts": (tract_profile.loc[tract_profile["tract_geoid"].isin(_center)], color("highlight.risk"), True),
            }),
        ),
    ])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Reads (draft, 2026-10-22; written during Lens 1, confirm in review).** The county-belonging
    reads (central counties, Saratoga, Schoharie, the ring of six) stay in Lens 1.

    - **The long tail is real but isn't commuting.** About 63k inbound jobs come from counties
      75–150 miles away (mostly the NYC metro), and 14k metro residents hold jobs "in"
      Manhattan. 74–90% of these are private-sector, so this isn't state jobs reported at
      Albany addresses. It is most likely remote work and companies that report every job at
      one address. Worth a sentence ("Albany's labor market reaches the city on paper"), not a
      map claim about commuting.

    Added after Q1d–Q1g (draft, 2026-10-22):

    - **Albany has the widest commute shed upstate.** Leaving out NYC, it is the largest
      outside metro for 10 NY counties, more than any other (Kiryas Joel-Poughkeepsie and
      Rochester 9, Buffalo and Syracuse 7). Eleven NY counties outside it send at least 5% of
      their resident jobs there, and four send over 25% (Montgomery, Washington, Warren,
      Fulton). Only the NYC metro reaches further (24 counties at 5%+), and much of that reach
      is the remote-work effect.
    - **Albany city is a commuter city.** It holds about 132k jobs (all sectors), and only 14%
      of them are held by its own residents. Of the other three cities' jobs, 20–22% (Troy,
      Schenectady) and 15% (Saratoga Springs) go to their own residents. **Troy residents are
      as likely to work in Albany (19%) as in Troy (18%).**
    - **Saratoga Springs draws from the towns around it.** Half its jobs (51%) are held by
      people living outside any Census Place, i.e. in the surrounding towns.

    Added after Q1h, tract-level sheds on all jobs (draft, 2026-10-22):

    - **The uptown-Albany-to-Wolf-Road band is the metro's shared job center.** 96k jobs; the
      median worker lives 11 miles away, drawn evenly from Albany (30%), Schenectady (13%),
      Saratoga (12%) and Rensselaer (11%) counties. It holds 10–20% of the resident jobs of
      nearly every tract in the four inner counties.
    - **Schenectady and Saratoga Springs run their own sheds.** Schenectady draws 47% of its
      workers from Schenectady County (median 8 miles). Saratoga Springs draws 59% from
      Saratoga County and 28% from outside the metro, the Glens Falls side.
    - **Downtown Albany's 50k jobs need a caveat.** 39% are held by people living outside the
      metro, and 30% by people living 75+ miles away. Those aren't commutes: statewide
      employers, public and private, report jobs at downtown addresses. The local downtown
      workforce is nearer 35k. Any "biggest job center" line must say so, or cap the shed at
      75 miles.
    """)
    return


if __name__ == "__main__":
    app.run()
