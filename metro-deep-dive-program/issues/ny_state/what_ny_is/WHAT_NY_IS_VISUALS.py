import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")

with app.setup:
    import json
    import sys
    from pathlib import Path

    import geopandas as gpd
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd
    import shapely
    from matplotlib import font_manager, patheffects
    from matplotlib.patches import Patch

    HERE = Path(__file__).resolve().parent
    REPO_ROOT = HERE.parents[3]
    SQL_DIR = HERE / "sql"
    OUTPUT_DIR = HERE / "output"
    DRAFTS_DIR = OUTPUT_DIR / "drafts"
    SEED_PATH = REPO_ROOT / "foundations" / "etl" / "reference" / "ny_county_regions.csv"

    sys.path.insert(0, str(REPO_ROOT / "metro-deep-dive-program" / "issues" / "_shared" / "act_1"))
    sys.path.insert(0, str(REPO_ROOT / "foundations" / "visual_library" / "chart_engine_py"))
    from chart_engine.theme import Theme
    from duckdb_helpers import connect_duckdb, read_sql

    # Lambert conformal conic fitted to NY. Keeps the state's shape true at print size.
    NY_CRS = "+proj=lcc +lat_1=40.5 +lat_2=44.5 +lat_0=42 +lon_0=-75.8 +datum=NAD83 +units=m +no_defs"
    SOURCE_CRS = "EPSG:4269"
    DOWNSTATE_DEFINITIONS = ("downstate_core", "downstate_mta", "downstate_redc")

    # 2x Substack content width (728 px).
    EXPORT_WIDTH_PX = 1456
    EXPORT_DPI = 200

    THEME = Theme.default()
    # Style guide stack: Inter, then Arial. Skip any that aren't installed so matplotlib doesn't warn per glyph.
    _installed = {f.name for f in font_manager.fontManager.ttflist}
    plt.rcParams["font.family"] = [
        f for f in (THEME.fonts.get("family", "Inter"), "Arial", "Helvetica") if f in _installed
    ] + ["sans-serif"]


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # What New York Is: Visuals

    Builds the four visuals for the opening sections of the NY State of Mind series intro.
    Plan and decisions: `issues/ny_state/WHAT_NY_IS_VISUALS_BUILD_PLAN.md`.

    Layer queries live in `sql/`. Drafts save to `output/drafts/`, finals to `output/`.
    The shared map functions are in the **Map helpers** section at the end.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Shared setup

    Base layers from the display geometry, joined to the NY regions seed
    (`foundations/etl/reference/ny_county_regions.csv`), plus the seed checks from the plan.
    """)
    return


@app.cell
def _():
    con = connect_duckdb()
    layers = load_base_layers(con)
    return con, layers


@app.cell
def _(layers):
    seed_checks = check_seed(layers["seed"], layers["counties"])
    assert seed_checks["passed"].all(), seed_checks
    seed_checks
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Names and colors

    Everything the maps print. Edit here and the maps below re-run.

    - `region_labels`: REDC region → map label. Regions not listed use the official name.
    - `region_colors`: REDC region → fill. Ten muted, distinct tones so neighbors never match.
    - `cbsa_label_overrides`: CBSA code → map label. Overrides win over the style.
    - `cbsa_label_style`: `"full"` is the CBSA name without the state suffix, wrapped after each
      hyphen when longer than `cbsa_wrap_at` characters. `"short"` is the first city in the name.
    """)
    return


@app.cell
def _(layers):
    region_labels = {}

    region_colors = {
        "Western New York": "#C9D6E3",
        "Finger Lakes": "#D9CBB0",
        "Southern Tier": "#C8D8BC",
        "Central New York": "#E2CACA",
        "Mohawk Valley": "#D2CAE0",
        "North Country": "#BFD9D3",
        "Capital Region": "#E5D9AE",
        "Mid-Hudson": "#D7C2B4",
        "New York City": "#C2CCE6",
        "Long Island": "#DCE3C2",
    }

    cbsa_label_overrides = {}
    cbsa_label_style = "full"
    cbsa_wrap_at = 16

    # REDC region -> (longitude, latitude) for hand-placed labels, set to clear the metro labels.
    region_label_positions = {
        "Western New York": (-78.55, 42.2),
        "Finger Lakes": (-77.25, 42.7),
        "Central New York": (-76.1, 42.72),
        "Southern Tier": (-75.25, 42.25),
        "Capital Region": (-74.05, 42.3),
        "Mid-Hudson": (-74.75, 41.72),
        "Long Island": (-72.65, 40.86),
        "New York City": (-73.9, 40.6),
    }

    # CBSA code -> (longitude, latitude) for hand-placed labels. Others sit inside their CBSA.
    cbsa_label_positions = {
        "35620": (-73.39, 40.95),  # New York: center of the metro's NY part, in Long Island Sound
        "28880": (-73.7, 41.66),  # Kiryas Joel-Poughkeepsie-Newburgh: in Dutchess, off the Downstate line
    }

    cbsa_labels = {
        row.cbsa_code: cbsa_label_overrides.get(
            row.cbsa_code, default_cbsa_label(row.cbsa_name, cbsa_label_style, cbsa_wrap_at)
        )
        for row in layers["cbsas"].itertuples()
    }
    return (
        cbsa_label_overrides,
        cbsa_label_positions,
        cbsa_labels,
        region_colors,
        region_label_positions,
        region_labels,
    )


@app.cell
def _(cbsa_label_overrides, cbsa_labels, layers):
    # Every CBSA label the maps print.
    cbsa_label_table = layers["cbsas"][["cbsa_code", "cbsa_name", "cbsa_type"]].assign(
        map_label=lambda df: df["cbsa_code"].map(cbsa_labels),
        overridden=lambda df: df["cbsa_code"].isin(cbsa_label_overrides),
    )
    cbsa_label_table.sort_values(["cbsa_type", "cbsa_name"]).reset_index(drop=True)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Review maps

    One map per base layer, so each can be checked on its own: names, colors and boundaries.
    """)
    return


@app.cell
def _(layers, region_colors, region_labels):
    regions_fig, regions_ax = new_map(layers)
    draw_region_fills(regions_ax, layers, region_colors, region_labels)
    draw_counties(regions_ax, layers)
    draw_outline(regions_ax, layers)
    add_text(
        regions_fig,
        title="Review: REDC regions",
        subtitle="The 10 Regional Economic Development Council regions, with county lines",
        source="Source: Empire State Development (REDC regions); Census cartographic boundaries.",
    )
    # save(regions_fig, "review_regions")  # off until we export
    regions_fig
    return


@app.cell
def _(cbsa_label_positions, cbsa_labels, layers):
    cbsas_fig, cbsas_ax = new_map(layers)
    draw_counties(cbsas_ax, layers)
    draw_cbsas(cbsas_ax, layers, cbsa_labels, label_micros=True, positions=cbsa_label_positions)
    draw_outline(cbsas_ax, layers)
    add_text(
        cbsas_fig,
        title="Review: CBSAs",
        subtitle="13 metros (dark outline, bold) and 14 micros (light outline), 2023 delineations",
        source="Source: Census cartographic boundaries (2023 CBSA delineations).",
    )
    # save(cbsas_fig, "review_cbsas")  # off until we export
    cbsas_fig
    return


@app.cell
def _(layers):
    downstate_fig, downstate_ax = new_map(layers)
    draw_downstate_fills(downstate_ax, layers)
    draw_counties(downstate_ax, layers)
    draw_outline(downstate_ax, layers)
    add_text(
        downstate_fig,
        title="Review: Downstate definitions",
        subtitle="Three nested definitions; each adds counties to the one before it",
        source="Source: NY regions seed (see NY_REGIONS_SPEC.md); Census cartographic boundaries.",
    )
    # save(downstate_fig, "review_downstate")  # off until we export
    downstate_fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Population Rank Over Time (Center of the Story)

    X.3 for the intro's "largest state from 1810 to 1960, then passed by California, Texas and
    Florida". Two versions to compare: **rank** among the states at each census, and **share** of
    the US population.

    Seed: `reference/state_population_history.csv`, decennial counts 1810–2020 for NY, CA, TX, FL
    and the US, transcribed from Census counts via a pinned Wikipedia revision (`source_url`).
    Ranks were computed from all 50 states in that table: present-day boundaries, ranked among
    areas that were states at each census (territories and DC not ranked). US totals are the
    official totals of each census, which exclude Alaska and Hawaii before 1960.

    **Boundary caveat:** in 1810, Virginia as then constituted (with West Virginia, 983,152)
    outnumbered New York (959,049). New York is first in 1810 only on present-day boundaries.
    """)
    return


@app.cell
def _():
    history = pd.read_csv(HERE / "reference" / "state_population_history.csv")
    _ny = history.loc[history["geography"] == "New York"].set_index("year")
    history_checks = pd.DataFrame(
        {
            "check": [
                "22 censuses x 5 geographies",
                "NY 1st at every census 1810-1960",
                "NY 4th in 2020",
                "NY 2020 = 20,201,249",
                "one source revision",
            ],
            "passed": [
                len(history) == 110 and history["year"].nunique() == 22,
                (_ny.loc[1810:1960, "state_rank"] == 1).all(),
                _ny.loc[2020, "state_rank"] == 4,
                _ny.loc[2020, "population"] == 20_201_249,
                history["source_url"].nunique() == 1,
            ],
        }
    )
    assert history_checks["passed"].all(), history_checks
    history_checks
    return (history,)


@app.cell
def _():
    # Draw order: context states first, New York last so it sits on top.
    history_colors = {
        "California": "#6E859E",
        "Texas": "#9A7F6B",
        "Florida": "#8C9472",
        "New York": color("highlight.strength"),
    }
    # Annotations on New York's line: census year -> (text, offset in points).
    history_rank_events = {
        1970: ("Passed by California", (0, 13)),
        2000: ("by Texas", (0, 13)),
        2020: ("by Florida", (-4, -12)),
    }
    # End-label nudges in points, where 2020 values sit close together.
    history_rank_label_dy = {}
    history_share_label_dy = {"Florida": 4, "New York": -4}
    # Share notes: (geography, year) -> (text, offset in points).
    history_share_notes = {
        ("New York", 1830): ("14.9% in 1830:\nabout one in seven Americans", (0, 7)),
    }
    return (
        history_colors,
        history_rank_events,
        history_rank_label_dy,
        history_share_label_dy,
        history_share_notes,
    )


@app.cell
def _(history, history_colors, history_rank_events, history_rank_label_dy):
    history_rank_fig = draw_rank_history(history, history_colors, history_rank_events, history_rank_label_dy)
    add_text(
        history_rank_fig,
        title="New York was the largest state for 150 years",
        subtitle="Rank among the states by population at each census, 1810–2020 (log scale, so the top ranks spread out)",
        source=(
            "Source: US Census Bureau decennial counts, via Wikipedia (rev. 1369369888). Present-day boundaries; ranked among states at\n"
            "each census, territories not ranked. On 1810 boundaries Virginia, then including West Virginia, was larger than New York."
        ),
    )
    save(history_rank_fig, "population_rank_history")
    history_rank_fig
    return


@app.cell
def _(history, history_colors, history_share_label_dy, history_share_notes):
    history_share_fig = draw_share_history(history, history_colors, history_share_notes, history_share_label_dy)
    add_text(
        history_share_fig,
        title="At its peak, one in seven Americans lived in New York",
        subtitle="Share of the US population at each census, 1810–2020",
        source=(
            "Source: US Census Bureau decennial counts, via Wikipedia (rev. 1369369888). Present-day state boundaries; official US totals,\n"
            "which exclude Alaska and Hawaii before 1960. Florida is shown from 1830, when it was still a territory."
        ),
    )
    save(history_share_fig, "population_share_history")
    history_share_fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Population Map (Two New Yorks)

    Tract population density (people per sq mi of land, ACS 2020–24) on a log scale, with REDC
    regions and CBSAs drawn on top. Classes step by ×5 then ×2 (10, 50, 100, 500, …), so each
    class is about half a decade on a log scale. NYC fills the top classes; that's expected.

    Grey tracts are "no data": 14 Suffolk tracts missing from the warehouse for 2023–24
    (ticket in `foundations/ROADMAP.md`). White tracts have land but no residents
    (parks, airports, cemeteries).

    Drafts compare palettes on the same classes. Nothing is saved yet.
    """)
    return


@app.cell
def _():
    density_breaks = [0, 10, 50, 100, 500, 1_000, 5_000, 10_000, 50_000]
    density_palettes = {
        "Green → red": "RdYlGn_r",
        "Yellow → red": "YlOrRd",
        "Viridis": "viridis",
    }
    return density_breaks, density_palettes


@app.cell
def _(con):
    tracts = read_geo(con, "ny_tract_density.sql")
    # Water-only tracts have no land, so no density; drop them from the drawing.
    tracts = tracts.loc[tracts["land_area_sqmi"] > 0]

    tract_checks = pd.DataFrame(
        {
            "check": [
                "tracts drawn",
                "tracts with no population row (no data)",
                "tracts with land but no residents",
                "population on the map",
            ],
            "value": [
                len(tracts),
                int(tracts["pop_total"].isna().sum()),
                int((tracts["pop_total"] == 0).sum()),
                f"{tracts['pop_total'].sum():,.0f}",
            ],
        }
    )
    tract_checks
    return (tracts,)


@app.cell
def _(
    cbsa_label_positions,
    cbsa_labels,
    density_breaks,
    density_palettes,
    layers,
    tracts,
):
    density_figs = {}
    for _name, _cmap in density_palettes.items():
        _fig, _ax = new_map(layers)
        draw_density(_ax, tracts, density_breaks, _cmap)
        draw_regions(_ax, layers, linewidth=0.7, line_color="white")
        draw_cbsas(_ax, layers, cbsa_labels, micros=True, positions=cbsa_label_positions)
        draw_outline(_ax, layers)
        add_text(
            _fig,
            title="Where New Yorkers live",
            subtitle=f"People per square mile by census tract, log scale · draft palette: {_name}",
            source=(
                "Source: ACS 2020–24 5-year; Census cartographic boundaries (2023 CBSA delineations); "
                "ESD REDC regions. Grey: 14 Suffolk tracts with no data."
            ),
        )
        # save(_fig, f"population_density_{_cmap}")  # off until we export
        density_figs[_name] = _fig
    mo.vstack(list(density_figs.values()))
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Population Map v2

    The 2026-10-19 review fixes (build plan, "Review, 2026-10-19"): yellow → red in six named
    bands, the Downstate line with each side's share of people and land, city labels in place of
    the CBSA outlines (Map 1's job), and a "no data" fill that no longer matches the neighboring
    states. The v1 drafts above stay for comparison.

    Shares come from county population (complete) and county land area, not from the tracts,
    which are missing 14 Suffolk tracts.
    """)
    return


@app.cell
def _():
    density_v2_breaks = [0, 50, 250, 1_000, 5_000, 25_000]
    density_v2_cmap = "YlOrRd"
    density_v2_no_data = color("neutral.comparison_fill")
    # Principal city -> label offset in points from its dot. Cities not listed are not drawn.
    density_v2_cities = {
        "Buffalo": (-14, -8), "Rochester": (0, 9), "Syracuse": (0, 9), "Utica": (0, 9),
        "Albany": (18, 0), "Binghamton": (0, -9), "Ithaca": (0, -9), "Elmira": (-4, -9),
        "Watertown": (0, 9), "Glens Falls": (0, 9), "Kingston": (-18, 0), "Poughkeepsie": (27, 0),
    }
    # Downstate / Rest of State -> (longitude, latitude) of its share note.
    density_v2_share_positions = {"Downstate": (-72.65, 41.58), "Rest of State": (-77.0, 41.72)}
    density_v2_share_colors = {"Downstate": color("highlight.strength"), "Rest of State": color("quadrant.low_high")}
    # Printed names; the data keeps "Rest of State". Map 1 and the article say Upstate.
    density_v2_share_names = {"Rest of State": "Upstate"}
    return (
        density_v2_breaks,
        density_v2_cities,
        density_v2_cmap,
        density_v2_no_data,
        density_v2_share_colors,
        density_v2_share_names,
        density_v2_share_positions,
    )


@app.cell
def _(con):
    # The principal-city query derives points with spatial functions.
    con.execute("LOAD spatial")
    density_v2_city_points = read_geo(con, "ny_principal_cities.sql")
    density_v2_shares = run_benchmark_sql(con, "downstate_shares.sql", "downstate_core").set_index("geography")
    density_v2_shares
    return density_v2_city_points, density_v2_shares


@app.cell
def _(
    density_v2_breaks,
    density_v2_cities,
    density_v2_city_points,
    density_v2_cmap,
    density_v2_no_data,
    density_v2_share_colors,
    density_v2_share_names,
    density_v2_share_positions,
    density_v2_shares,
    layers,
    tracts,
):
    density_v2_fig, _ax = new_map(layers)
    draw_density(_ax, tracts, density_v2_breaks, density_v2_cmap, missing_color=density_v2_no_data)
    draw_downstate(_ax, layers, "downstate_core", linewidth=1.4, line_color=color("neutral.text"))
    draw_outline(_ax, layers)
    draw_city_labels(_ax, density_v2_city_points, density_v2_cities)
    draw_share_notes(
        _ax, density_v2_shares, density_v2_share_positions, density_v2_share_colors, density_v2_share_names
    )
    add_text(
        density_v2_fig,
        title="Two-thirds of New Yorkers live on one-twentieth of the land",
        subtitle="People per square mile by census tract · dashed line: Downstate, the NY counties of the NYC metro",
        source=(
            "Source: ACS 2020–24 5-year (tracts; county totals for the shares); Census cartographic boundaries. "
            "Grey: 14 Suffolk tracts with no data."
        ),
    )
    save(density_v2_fig, "population_density")
    density_v2_fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## How New York Stacks Up (benchmark)

    Six metrics in three lenses for Downstate, Rest of State, NY Total and the US, with NY's rank
    among the 50 states (1 = highest; DC excluded).

    - Downstate and Rest of State are built from counties: sums, ratios of sums, and pooled medians
      for median age and household income (`sql/benchmark_median_bins.sql`).
    - NY Total and US are the published figures. US GDP per capita is the sum of the states and DC,
      since the warehouse US row has no GDP.
    - Years: ACS 2020–24 for everything except GDP per capita, which is BEA 2023 (the latest county year).

    Change `benchmark_downstate` to rerun everything with another Downstate definition.
    """)
    return


@app.cell
def _():
    benchmark_downstate = "downstate_core"  # downstate_core | downstate_mta | downstate_redc
    return (benchmark_downstate,)


@app.cell
def _(benchmark_downstate, con):
    benchmark_counties = run_benchmark_sql(con, "benchmark_stack_up.sql", benchmark_downstate)
    benchmark_bins = run_benchmark_sql(con, "benchmark_median_bins.sql", benchmark_downstate)

    # Pooled medians for Downstate and Rest of State, plus all 62 counties for the check.
    _pooled = (
        benchmark_bins.groupby(["geography", "metric_id"])
        .apply(pooled_median, include_groups=False)
        .rename("value")
        .reset_index()
    )
    _labels = benchmark_counties[["lens", "metric_id", "metric_label", "metric_order"]].drop_duplicates()
    _pooled_rows = _pooled.loc[_pooled["geography"] != "NY counties"].merge(_labels, on="metric_id").assign(
        year=2024, method="pooled_median", downstate_definition=benchmark_downstate
    )
    _geo_order = {"Downstate": 1, "Rest of State": 2, "NY Total": 3, "US": 4}
    benchmark = (
        pd.concat([benchmark_counties, _pooled_rows], ignore_index=True)
        .assign(_geo=lambda df: df["geography"].map(_geo_order))
        .sort_values(["metric_order", "_geo"])
        .drop(columns="_geo")
        .reset_index(drop=True)
    )
    benchmark_pooled_ny = _pooled.loc[_pooled["geography"] == "NY counties"].set_index("metric_id")["value"]
    return benchmark, benchmark_pooled_ny


@app.cell
def _(benchmark, benchmark_pooled_ny):
    def _value(geography, metric_id):
        _match = (benchmark["geography"] == geography) & (benchmark["metric_id"] == metric_id)
        return benchmark.loc[_match, "value"].iloc[0]

    _pop_parts = _value("Downstate", "population") + _value("Rest of State", "population")
    _checks = [
        ("Downstate + Rest of State = NY population", _pop_parts, _value("NY Total", "population"),
         abs(_pop_parts - _value("NY Total", "population")) < 1),
    ]
    for _metric in ["median_age", "median_hh_income"]:
        _published = _value("NY Total", _metric)
        _pooled = benchmark_pooled_ny[_metric]
        _checks.append(
            (f"62-county pooled {_metric} within 1% of published", _pooled, _published,
             abs(_pooled / _published - 1) < 0.01)
        )
    benchmark_checks = pd.DataFrame(_checks, columns=["check", "computed", "published", "passed"])
    assert benchmark_checks["passed"].all(), benchmark_checks
    benchmark_checks
    return


@app.cell
def _(benchmark):
    # Review table: the numbers as they would print.
    benchmark_review = benchmark_wide(benchmark)
    benchmark_review
    return


@app.cell
def _(benchmark, benchmark_downstate):
    benchmark_table_fig = draw_benchmark_table(benchmark)
    add_text(
        benchmark_table_fig,
        title="How New York stacks up",
        subtitle=f"Draft form: table · Downstate = {benchmark_downstate}",
        source=(
            "Source: ACS 2020–24 5-year; BEA 2023 GDP. Downstate and Rest of State built from counties; "
            "medians pooled from ACS bins. Rank among 50 states, DC excluded."
        ),
    )
    # save(benchmark_table_fig, "benchmark_table")  # off until we export
    benchmark_table_fig
    return


@app.cell
def _(benchmark, benchmark_downstate):
    benchmark_strip_fig = draw_benchmark_strip(benchmark)
    add_text(
        benchmark_strip_fig,
        title="How New York stacks up",
        subtitle=f"Draft form: dot strip · Downstate = {benchmark_downstate}",
        source=(
            "Source: ACS 2020–24 5-year; BEA 2023 GDP. Downstate and Rest of State built from counties; "
            "medians pooled from ACS bins. Rank among 50 states, DC excluded."
        ),
    )
    # save(benchmark_strip_fig, "benchmark_strip")  # off until we export
    benchmark_strip_fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Benchmark v2: table with "as if a state" ranks

    The table form won the 2026-10-19 review. v2 ranks Downstate and Rest of State (printed as Upstate) **as if each
    were a state**: each value is ranked against the 49 states other than New York, out of 50
    (1 = highest). NY Total is ranked the same way, which reproduces the SQL's state rank; the
    check below asserts that. A share-of-New-Yorkers row sits under population.

    State values: `sql/benchmark_state_values.sql`, same definitions and years as the benchmark.
    """)
    return


@app.cell
def _(benchmark, con):
    benchmark_v2_states = con.sql(read_sql(SQL_DIR / "benchmark_state_values.sql")).df()
    benchmark_v2 = add_as_if_ranks(benchmark, benchmark_v2_states)

    _ny = benchmark_v2.loc[benchmark_v2["geography"] == "NY Total"]
    assert (_ny["as_if_rank"] == _ny["state_rank"]).all(), _ny
    assert benchmark_v2_states.groupby("metric_id").size().eq(50).all()

    # Review table: value and as-if rank per geography.
    benchmark_v2.assign(
        shown=lambda df: [format_benchmark_value(m, v) for m, v in zip(df["metric_id"], df["value"])]
    ).pivot(index=["metric_order", "metric_label"], columns="geography", values=["shown", "as_if_rank"])
    return (benchmark_v2,)


@app.cell
def _(benchmark_downstate, benchmark_v2):
    _definitions = {
        "downstate_core": "the 10 NY counties of the NYC metro",
        "downstate_mta": "the 12 counties of the MTA region",
        "downstate_redc": "the 14 counties of the REDC Downstate regions",
    }
    benchmark_v2_fig = draw_benchmark_table_v2(benchmark_v2)
    add_text(
        benchmark_v2_fig,
        title="Split in two, New York ranks 1st and 35th in GDP per person",
        subtitle=f"Downstate = {_definitions[benchmark_downstate]}. Small numbers: rank among the 50 states",
        source=(
            "Rank 1 = highest (oldest, most foreign-born, richest, fastest growing). Downstate and Upstate (the rest of the state) are ranked as if each\n"
            "were a state, against the 49 states other than NY; DC excluded. Source: ACS 2020–24 5-year; BEA 2023 GDP. "
            "Medians pooled from ACS bins."
        ),
    )
    save(benchmark_v2_fig, "benchmark_table")
    benchmark_v2_fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Map 1: Regions and CBSAs

    The reader's bearings: REDC regions as muted fills with direct labels, metros outlined and
    labeled, micros in a lighter outline without labels, and the Downstate line dashed.
    Names, colors and label positions come from the Names and colors cell.

    The Downstate line uses the risk red so it reads over the black metro outline it runs along
    (the core definition is exactly the NY part of the NYC metro). Change `map1_downstate` to
    draw another definition.
    """)
    return


@app.cell
def _():
    map1_downstate = "downstate_core"  # downstate_core | downstate_mta | downstate_redc
    map1_downstate_color = color("highlight.risk")
    return map1_downstate, map1_downstate_color


@app.cell
def _(
    cbsa_label_positions,
    cbsa_labels,
    layers,
    map1_downstate,
    map1_downstate_color,
    region_colors,
    region_label_positions,
    region_labels,
):
    map1_fig, map1_ax = new_map(layers)
    draw_region_fills(map1_ax, layers, region_colors, region_labels, show_labels=False)
    draw_counties(map1_ax, layers)
    draw_cbsas(map1_ax, layers, cbsa_labels, micros=True, positions=cbsa_label_positions)
    draw_downstate(map1_ax, layers, map1_downstate, linewidth=1.6, line_color=map1_downstate_color)
    draw_outline(map1_ax, layers)
    draw_region_labels(map1_ax, layers, region_labels, positions=region_label_positions, caps=True)
    map1_ax.legend(
        handles=[
            plt.Line2D([], [], color=color("neutral.text"), linewidth=1.1, label="Metro area"),
            plt.Line2D([], [], color=color("neutral.outline"), linewidth=0.6, label="Micro area"),
            plt.Line2D([], [], color=map1_downstate_color, linewidth=1.6, linestyle=(0, (4, 2)),
                       label="Downstate line"),
        ],
        loc="upper left", frameon=False, fontsize=7.5, handlelength=2.2,
    )
    add_text(
        map1_fig,
        title="New York's regions and metro areas",
        subtitle="10 REDC regions · 13 metro and 14 micro areas (2023) · Downstate = NYC metro counties",
        source="Source: Empire State Development (REDC regions); Census cartographic boundaries (2023 CBSA delineations).",
    )
    # save(map1_fig, "map1_regions_cbsas")  # off until we export
    map1_fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Map 1 v2

    The 2026-10-19 review fixes: the Downstate line is labeled on the map instead of in the
    legend; micro areas get a visible dashed outline and a small first-city label (D2: show
    micros, lead with metros); and the NYC, Central New York and Albany labels are moved.
    Positions start from the Names and colors cell and override only what changes.
    """)
    return


@app.cell
def _(cbsa_label_positions, region_label_positions):
    map1v2_region_label_positions = {
        **region_label_positions,
        "New York City": (-73.95, 40.47),
        "Central New York": (-76.25, 42.87),
        "Capital Region": (-74.2, 42.33),
        "Finger Lakes": (-77.5, 42.6),
        "Western New York": (-78.55, 42.12),
    }
    map1v2_cbsa_label_positions = {**cbsa_label_positions, "10580": (-73.82, 42.68)}
    # Micro CBSA code -> (lon, lat) where the default spot collides with another label.
    map1v2_micro_label_positions = {"26460": (-73.62, 42.16)}  # Hudson, clear of CAPITAL REGION
    # Direct labels for the Downstate line: text -> (lon, lat).
    map1v2_downstate_labels = {"↑ Upstate": (-72.95, 41.64), "↓ Downstate": (-72.95, 41.4)}
    return (
        map1v2_cbsa_label_positions,
        map1v2_downstate_labels,
        map1v2_micro_label_positions,
        map1v2_region_label_positions,
    )


@app.cell
def _(
    cbsa_labels,
    layers,
    map1_downstate,
    map1_downstate_color,
    map1v2_cbsa_label_positions,
    map1v2_downstate_labels,
    map1v2_micro_label_positions,
    map1v2_region_label_positions,
    region_colors,
    region_labels,
):
    map1v2_fig, _ax = new_map(layers)
    draw_region_fills(_ax, layers, region_colors, region_labels, show_labels=False)
    draw_counties(_ax, layers)
    draw_micros(_ax, layers, positions=map1v2_micro_label_positions)
    draw_cbsas(_ax, layers, cbsa_labels, micros=False, positions=map1v2_cbsa_label_positions)
    draw_downstate(_ax, layers, map1_downstate, linewidth=1.6, line_color=map1_downstate_color)
    draw_outline(_ax, layers)
    draw_region_labels(_ax, layers, region_labels, positions=map1v2_region_label_positions, caps=True)
    for _text, _point in to_map_points(map1v2_downstate_labels).items():
        label(_ax, _point.x, _point.y, _text, size=6.8, weight="bold", text_color=map1_downstate_color)
    _ax.legend(
        handles=[
            plt.Line2D([], [], color=color("neutral.text"), linewidth=1.1, label="Metro area"),
            plt.Line2D([], [], color=color("neutral.text_muted"), linewidth=0.7, linestyle=(0, (3, 1.5)),
                       label="Micro area"),
        ],
        loc="upper left", frameon=False, fontsize=7.5, handlelength=2.2,
    )
    add_text(
        map1v2_fig,
        title="New York's regions and metro areas",
        subtitle="10 REDC regions · 13 metro areas (bold) and 14 micro areas, 2023 delineations",
        source="Source: Empire State Development (REDC regions); Census cartographic boundaries (2023 CBSA delineations).",
    )
    save(map1v2_fig, "map1_regions_cbsas")
    map1v2_fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Map 2: Core Infrastructure

    A first working draft with every landmark and port retained for review. The Erie Canal
    is the accent; the Thruway is heavier than other interstates; main-line rail is dashed.
    NYC's seven crowded landmarks appear in a detail inset, with one cluster marker statewide.

    The Infrastructure consumer handoff supplies the OSM features. The Thruway highlight uses
    source names and route references, checked against the Authority's section descriptions;
    operator tags are not required. It is a cartographic selection, not a legal road inventory.
    Rail with missing `usage` is not silently classified as main-line rail.
    """)
    return


@app.cell
def _():
    # Edit the drawing here; the source layers and earlier visuals stay read-only.
    map2_visible = dict(canal=True, thruway=True, interstate=True, mainline_rail=True,
                        parks=True, ports=True, landmarks=True, cities=True)
    map2_colors = dict(
        canal=color("diverging.worse"), thruway=color("neutral.text"),
        interstate=color("context.road"), mainline_rail=color("neutral.outline"),
        parks=color("highlight.opportunity"), ports=color("highlight.strength"),
        landmarks=color("neutral.text"),
    )
    # Offsets are typographic points from each actual source coordinate. Leader
    # lines retain the location when nearby numbered symbols need separation.
    map2_landmark_offsets = {
        "1": (6, 8), "2": (3, 8), "3": (8, 7), "4": (-8, 4), "5": (-7, -5),
        "6": (9, -3), "7": (0, 8), "8": (-3, -10), "9": (-8, 5),
        "13": (11, 0), "14": (-9, 5), "15": (9, -6), "16": (6, 9),
        "21": (8, 0), "22": (-10, 6), "25": (5, -5), "27": (-9, -2),
        "P4": (-10, -5),
    }
    map2_city_label_offsets = {
        "Buffalo": (7, -9), "Rochester": (0, -9), "Syracuse": (0, -9),
        "Albany": (17, -2), "Binghamton": (0, -9), "Elmira": (-5, -9),
        "Ithaca": (-4, -9), "Glens Falls": (0, -9), "Kingston": (-15, 0),
        "Poughkeepsie": (17, -8), "Utica": (0, -9), "Watertown": (0, -9),
    }
    map2_nyc_bounds = (-74.22, 40.60, -73.94, 40.79)  # W, S, E, N; includes Howland Hook.
    return map2_city_label_offsets, map2_colors, map2_landmark_offsets, map2_nyc_bounds, map2_visible


@app.cell
def _(con, layers):
    map2_data = load_map2_layers(con, layers)
    # Counts refer to selected source features before drawing-only shoreline
    # clipping. The review table also exposes the independent reference inputs.
    map2_inventory = pd.concat([
        map2_data["network"].groupby("map_layer").size().rename("features"),
        pd.Series({"canal routes": len(map2_data["canal"]), "park boundaries": len(map2_data["parks"]),
                   "landmark points": int(map2_data["landmarks"]["kind"].eq("point").sum()),
                   "port candidates": int(map2_data["landmarks"]["kind"].eq("port").sum()),
                   "principal cities": len(map2_data["cities"])},
                  name="features"),
    ]).rename_axis("layer").reset_index()
    mo.ui.table(map2_inventory, selection=None)
    return (map2_data,)


@app.cell
def _(layers, map2_city_label_offsets, map2_colors, map2_data, map2_landmark_offsets,
      map2_nyc_bounds, map2_visible):
    map2_fig = draw_infrastructure_map(
        layers, map2_data, map2_visible, map2_colors, map2_landmark_offsets,
        map2_city_label_offsets, map2_nyc_bounds,
    )
    # save(map2_fig, "map2_core_infrastructure")  # off until we export
    map2_fig
    return (map2_fig,)


@app.cell(hide_code=True)
def _(map2_data):
    mo.md(f"""
    **Sources and limits.** OSM snapshot 2026-10-17, © OpenStreetMap contributors (ODbL),
    extracted by Geofabrik; source run `{map2_data['source_run_id']}`. The highlight follows
    [Thruway Authority section descriptions](https://www.thruway.ny.gov/business/real-property)
    and source-supported names/refs; unnamed segments can remain in the lighter interstate
    layer. There is no routing or access inference. Only `railway=rail, usage=main` is drawn;
    6,334 rail features lack a usage tag.

    Canal centerline: [NYS Canal Corporation](https://services6.arcgis.com/DmQy2NS38tchd4fs/arcgis/rest/services/Canal_Centerline/FeatureServer/10).
    Park blue lines: [Adirondack Park Agency](https://services2.arcgis.com/8krRUWgifzA4cgL3/ArcGIS/rest/services/BluelinePolygon/FeatureServer/0)
    and [NYS DEC](https://gisservices.dec.ny.gov/arcgis/rest/services/dil_reference/MapServer/8);
    these boundaries include public and private land. All three were pulled 2026-10-18;
    checksums are in `data/map2_reference_manifest.json`. The 20 canal routes total about
    534 miles including lake stretches and spurs; this is not the official 524-mile system total.
    The canal service declares no license text. Landmark coordinates and interpretation are in
    `reference/landmark_sources.json`. Rochester's port marker represents its terminal/marina
    complex. City dots use Census display-geometry representative points.

    **Review next:** cut landmarks and ports, adjust labels and layer emphasis at phone width,
    then approve exports. PNG/SVG and Carto exports remain off.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Map 2 v2: infrastructure first

    The 2026-10-19 review cut: six landmarks the article mentions, labeled directly; four ports;
    one NYC callout in place of the inset and numbered key; the Hudson River in water blue; no
    REDC borders (Map 1 has them); darker main-line rail. Same source layers as v1, plus the
    Hudson River lines from the same Infrastructure handoff (`sql/map2_v2_water.sql`).
    `landmarks.csv` is unchanged; the cut lives in the settings below.
    """)
    return


@app.cell
def _(map2_city_label_offsets, map2_colors):
    # Landmark name in landmarks.csv -> (map label, offset in points). Horizontal offsets
    # left- or right-align the label away from the marker.
    map2v2_landmarks = {
        "Lockport Flight of Five": ("Lockport\nFlight of Five", (0, 11)),
        "Waterford Flight": ("Waterford\nFlight", (7, 4)),
        "Empire State Plaza": ("Empire State\nPlaza", (-7, -6)),
        "Niagara Power Project": ("Niagara Power\nProject", (-7, 3)),
        "Bear Mountain": ("Bear Mountain", (-7, 0)),
        "Attica": ("Attica", (0, -8)),
    }
    # Port name -> (map label, offset) or None for a marker without a label.
    map2v2_ports = {
        "Port of New York and New Jersey (NY side)": None,
        "Port of Albany–Rensselaer": None,
        "Buffalo Harbor": None,
        "Port of Oswego": ("Port of Oswego", (-7, 3)),
    }
    map2v2_city_offsets = {**map2_city_label_offsets}
    # Area label name -> (lon, lat) override; Finger Lakes moves off the Cayuga-Seneca canal.
    map2v2_area_positions = {"Finger Lakes": (-77.35, 42.45)}
    map2v2_nyc_callout = {
        "at": (-74.0, 40.72),
        "text_at": (-74.55, 40.62),
        "title": "New York City",
        "body": "Ellis Island · Wall Street\nUN · 9/11 Memorial",
    }
    # Water blue for the Hudson: the theme's context.water is a fill tint, too pale for a line.
    map2v2_colors = {**map2_colors, "mainline_rail": color("neutral.text_muted"), "river": "#6FA3CF"}
    return (
        map2v2_area_positions,
        map2v2_city_offsets,
        map2v2_colors,
        map2v2_landmarks,
        map2v2_nyc_callout,
        map2v2_ports,
    )


@app.cell
def _(con):
    map2v2_water = load_map2v2_water(con)
    mo.md(f"Hudson River features drawn: **{len(map2v2_water)}**")
    return (map2v2_water,)


@app.cell
def _(
    layers,
    map2_data,
    map2v2_area_positions,
    map2v2_city_offsets,
    map2v2_colors,
    map2v2_landmarks,
    map2v2_nyc_callout,
    map2v2_ports,
    map2v2_water,
):
    map2v2_fig = draw_infrastructure_map_v2(
        layers, map2_data, map2v2_water, map2v2_colors, map2v2_landmarks, map2v2_ports,
        map2v2_city_offsets, map2v2_area_positions, map2v2_nyc_callout,
    )
    save(map2v2_fig, "map2_core_infrastructure")
    map2v2_fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Map helpers

    The visual library can't draw these maps yet (no categorical fills, no line or point layers),
    so they are one-off matplotlib maps. Everything the maps share is below so they match:
    layer loading, the base frame, overlays, labels, titles and export. Promote to library
    types if a later piece reuses them.
    """)
    return


@app.function
def color(key: str) -> str:
    return THEME.color(key, "#7B8794")


@app.function
def read_geo(con, sql_name: str) -> gpd.GeoDataFrame:
    """Run a query from sql/ that returns `geom_wkb`, as a GeoDataFrame in NY_CRS."""
    df = con.sql(read_sql(SQL_DIR / sql_name)).df()
    geometry = shapely.from_wkb(df.pop("geom_wkb").map(bytes))
    return gpd.GeoDataFrame(df, geometry=geometry, crs=SOURCE_CRS).to_crs(NY_CRS)


@app.function
def check_seed(seed: pd.DataFrame, counties: gpd.GeoDataFrame) -> pd.DataFrame:
    """The seed checks from the build plan, as a pass/fail table."""
    core, mta, redc = (set(seed.loc[seed[c], "county_geoid"]) for c in DOWNSTATE_DEFINITIONS)
    checks = {
        "62 rows": len(seed) == 62,
        "each county once": seed["county_geoid"].is_unique,
        "matches geo.counties": set(seed["county_geoid"]) == set(counties["county_geoid"]),
        "10 REDC regions": seed["redc_region"].nunique() == 10,
        "downstate_core is 10 counties": len(core) == 10,
        "downstate_mta is 12 counties": len(mta) == 12,
        "downstate_redc is 14 counties": len(redc) == 14,
        "core ⊂ mta ⊂ redc": core < mta < redc,
    }
    return pd.DataFrame({"check": list(checks), "passed": list(checks.values())})


@app.function
def load_base_layers(con) -> dict:
    """Every layer the maps share, in NY_CRS, drawn from the display geometry."""
    seed = pd.read_csv(SEED_PATH, dtype={"county_geoid": str})
    counties = read_geo(con, "ny_counties.sql").merge(
        seed.drop(columns=["county_name"]), on="county_geoid", how="left", validate="1:1"
    )
    outline = gpd.GeoDataFrame(geometry=[counties.union_all()], crs=NY_CRS)
    regions = counties.dissolve(by="redc_region", as_index=False)[["redc_region", "geometry"]]
    # Downstate lines are the inland edge only: the area boundary minus the state outline and coast.
    state_edge = outline.boundary.buffer(200).union_all()
    downstate = gpd.GeoDataFrame(
        {
            "definition": list(DOWNSTATE_DEFINITIONS),
            "geometry": [
                counties.loc[counties[d]].union_all().boundary.difference(state_edge)
                for d in DOWNSTATE_DEFINITIONS
            ],
        },
        crs=NY_CRS,
    )
    cbsas = read_geo(con, "ny_cbsas.sql")
    return {
        "seed": seed,
        "counties": counties,
        "outline": outline,
        "regions": regions,
        "downstate": downstate,
        "cbsas": cbsas,
        "cbsas_drawn": cbsas.clip(outline),
        "neighbors": read_geo(con, "neighbor_states.sql"),
    }


@app.function
def default_cbsa_label(cbsa_name: str, style: str = "full", wrap_at: int = 16) -> str:
    """'Albany-Schenectady-Troy, NY' -> 'Albany-\\nSchenectady-\\nTroy' (full) or 'Albany' (short)."""
    name = cbsa_name.split(",")[0]
    if style == "short":
        return name.split("-")[0]
    return name.replace("-", "-\n") if len(name) > wrap_at else name


@app.function
def new_map(layers: dict, *, pad: float = 0.03, header_in: float = 0.75, footer_in: float = 0.3):
    """A figure framed on NY with neighboring states in faint grey. Height follows the state's shape."""
    minx, miny, maxx, maxy = layers["outline"].total_bounds
    dx, dy = (maxx - minx) * pad, (maxy - miny) * pad
    width_in = EXPORT_WIDTH_PX / EXPORT_DPI
    map_height_in = width_in * (maxy - miny + 2 * dy) / (maxx - minx + 2 * dx)
    height_in = map_height_in + header_in + footer_in

    fig = plt.figure(figsize=(width_in, height_in), dpi=EXPORT_DPI)
    ax = fig.add_axes((0, footer_in / height_in, 1, map_height_in / height_in))
    background = color("neutral.background_white")
    fig.patch.set_facecolor(background)
    ax.set_facecolor(background)
    ax.set_axis_off()

    layers["neighbors"].plot(ax=ax, color=color("neutral.grid_minor"), edgecolor="white", linewidth=0.6)
    ax.set_xlim(minx - dx, maxx + dx)
    ax.set_ylim(miny - dy, maxy + dy)
    ax.set_aspect("equal")
    return fig, ax


@app.function
def draw_outline(ax, layers: dict, linewidth: float = 0.8) -> None:
    layers["outline"].boundary.plot(ax=ax, color=color("context.boundary"), linewidth=linewidth)


@app.function
def draw_counties(ax, layers: dict, linewidth: float = 0.25) -> None:
    layers["counties"].boundary.plot(ax=ax, color=color("context.internal_boundary"), linewidth=linewidth)


@app.function
def draw_regions(ax, layers: dict, linewidth: float = 0.9, line_color: str | None = None) -> None:
    layers["regions"].boundary.plot(ax=ax, color=line_color or color("neutral.text_muted"), linewidth=linewidth)


@app.function
def draw_downstate(
    ax, layers: dict, definition: str = "downstate_core", linewidth: float = 1.4, line_color: str | None = None
) -> None:
    line = layers["downstate"].loc[layers["downstate"]["definition"] == definition]
    # White underlay so the dashes read over the metro outline the core line runs along.
    line.plot(ax=ax, color="white", linewidth=linewidth + 1.6)
    line.plot(ax=ax, color=line_color or color("neutral.text"), linewidth=linewidth, linestyle=(0, (4, 2)))


@app.function
def label(
    ax, x: float, y: float, text: str, *, size: float = 6.5, weight: str = "normal", text_color: str | None = None
) -> None:
    """Map label with a thin white halo so it reads over lines and fills."""
    ax.annotate(
        text, (x, y), ha="center", va="center", fontsize=size, fontweight=weight,
        color=text_color or color("neutral.text"),
        path_effects=[patheffects.withStroke(linewidth=2, foreground="white")],
    )


@app.function
def draw_region_fills(ax, layers: dict, colors: dict, labels: dict | None = None, *, show_labels: bool = True) -> None:
    regions = layers["regions"]
    regions.plot(ax=ax, color=regions["redc_region"].map(colors), edgecolor="white", linewidth=1.2)
    if show_labels:
        draw_region_labels(ax, layers, labels)


@app.function
def draw_region_labels(
    ax, layers: dict, labels: dict | None = None, *, positions: dict | None = None, caps: bool = False
) -> None:
    """Region names, drawn separately so maps can put them on top of other layers.

    `positions` maps region -> (lon, lat) for hand-placed labels. `caps` draws them as smaller grey
    capitals, so they read as a different layer from metro names.
    """
    placed = to_map_points(positions)
    for row in layers["regions"].itertuples():
        point = placed.get(row.redc_region, row.geometry.representative_point())
        text = (labels or {}).get(row.redc_region, row.redc_region)
        if caps:
            label(ax, point.x, point.y, text.upper(), size=6.3, weight="bold", text_color=color("neutral.text_muted"))
        else:
            label(ax, point.x, point.y, text, size=7.5, weight="bold")


@app.function
def to_map_points(positions: dict | None) -> dict:
    """{key: (lon, lat)} -> {key: shapely Point in NY_CRS}."""
    return {
        key: gpd.GeoSeries([shapely.Point(lonlat)], crs="EPSG:4326").to_crs(NY_CRS).iloc[0]
        for key, lonlat in (positions or {}).items()
    }


@app.function
def draw_cbsas(
    ax,
    layers: dict,
    labels: dict,
    *,
    micros: bool = True,
    label_metros: bool = True,
    label_micros: bool = False,
    positions: dict | None = None,
) -> None:
    """Metro and micro outlines with labels. `positions` maps CBSA code -> (lon, lat) for hand-placed labels."""
    placed = to_map_points(positions)
    drawn = layers["cbsas_drawn"]
    metros = drawn.loc[drawn["cbsa_type"] == "metro"]
    micro_rows = drawn.loc[drawn["cbsa_type"] == "micro"]
    if micros:
        micro_rows.boundary.plot(ax=ax, color=color("neutral.outline"), linewidth=0.6)
    metros.boundary.plot(ax=ax, color=color("neutral.text"), linewidth=1.1)
    for rows, show, size, weight in (
        (metros, label_metros, 6.5, "bold"),
        (micro_rows, micros and label_micros, 5.5, "normal"),
    ):
        if show:
            for row in rows.itertuples():
                point = placed.get(row.cbsa_code, row.geometry.representative_point())
                label(ax, point.x, point.y, labels[row.cbsa_code], size=size, weight=weight)


@app.function
def draw_downstate_fills(ax, layers: dict) -> None:
    """The three Downstate definitions as nested fills, darkest for the core, with a legend."""
    counties = layers["counties"]
    shades = {
        "downstate_redc": ("#C6DBEF", "REDC: + Ulster, Sullivan (14 counties)"),
        "downstate_mta": ("#6BAED6", "MTA: + Orange, Dutchess (12 counties)"),
        "downstate_core": ("#2C7FB8", "Core: NY part of the NYC metro (10 counties)"),
    }
    for definition, (fill, _) in shades.items():
        counties.loc[counties[definition]].plot(ax=ax, color=fill, edgecolor="white", linewidth=0.4)
    handles = [Patch(facecolor=fill, label=text) for fill, text in reversed(shades.values())]
    ax.legend(
        handles=handles, loc="upper left", frameon=False, fontsize=7.5, title="Downstate definition",
        title_fontsize=8, alignment="left",
    )


@app.function
def density_class_labels(breaks: list) -> list[str]:
    """[0, 10, 50, ...] -> ['Under 10', '10–50', ..., '50,000+']."""
    labels = [f"Under {breaks[1]:,}"]
    labels += [f"{lo:,}–{hi:,}" for lo, hi in zip(breaks[1:-1], breaks[2:])]
    labels.append(f"{breaks[-1]:,}+")
    return labels


@app.function
def draw_density(
    ax, tracts: gpd.GeoDataFrame, breaks: list, cmap_name: str, *, missing_color: str | None = None
) -> None:
    """Tract density in log classes, plus grey for no data and white for no residents, with a legend."""
    missing_color = missing_color or color("neutral.missing_fill")
    n_classes = len(breaks)
    cmap = plt.get_cmap(cmap_name, n_classes)
    fills = [cmap(i) for i in range(n_classes)]
    labels = density_class_labels(breaks)

    has_data = tracts["pop_total"].notna()
    has_people = has_data & (tracts["pop_total"] > 0)
    populated = tracts.loc[has_people]
    # Class index: the last break at or below the density.
    class_index = pd.cut(
        populated["pop_per_sqmi"], bins=list(breaks) + [float("inf")], right=False, labels=False
    ).astype(int)
    populated.plot(ax=ax, color=[fills[i] for i in class_index], linewidth=0)
    tracts.loc[has_data & ~has_people].plot(ax=ax, color="white", linewidth=0)
    tracts.loc[~has_data].plot(ax=ax, color=missing_color, linewidth=0)

    handles = [Patch(facecolor=fill, label=text) for fill, text in zip(reversed(fills), reversed(labels))]
    handles += [
        Patch(facecolor="white", edgecolor=color("neutral.border"), label="No residents"),
        Patch(facecolor=missing_color, label="No data"),
    ]
    ax.legend(
        handles=handles, loc="upper left", frameon=False, fontsize=6.5, title="People per sq mi",
        title_fontsize=7.5, alignment="left", handlelength=1.4, handleheight=0.9,
    )


@app.function
def run_benchmark_sql(con, sql_name: str, downstate: str) -> pd.DataFrame:
    """Run a benchmark query with the Downstate definition and seed path filled in."""
    if downstate not in DOWNSTATE_DEFINITIONS:
        raise ValueError(f"Unknown Downstate definition: {downstate}")
    sql = read_sql(SQL_DIR / sql_name).replace("__DOWNSTATE__", downstate).replace("__SEED_PATH__", SEED_PATH.as_posix())
    return con.sql(sql).df()


@app.function
def pooled_median(bins: pd.DataFrame) -> float:
    """Median from binned counts, interpolating linearly inside the bin that holds the middle value.

    The same method ACS uses for medians from its distribution tables. If the median falls in the
    open top bin, returns that bin's lower edge.
    """
    bins = bins.sort_values("bin_lower")
    half = bins["n"].sum() / 2
    below = 0.0
    for row in bins.itertuples():
        if below + row.n >= half:
            if pd.isna(row.bin_upper):
                return row.bin_lower
            return row.bin_lower + (half - below) / row.n * (row.bin_upper - row.bin_lower)
        below += row.n
    return float("nan")


@app.function
def ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


@app.function
def format_benchmark_value(metric_id: str, value: float) -> str:
    if metric_id == "population":
        return f"{value / 1e6:,.1f}M"
    if metric_id == "median_age":
        return f"{value:.1f}"
    if metric_id in ("median_hh_income", "gdp_per_capita"):
        return f"${value / 1e3:,.1f}k"
    if metric_id == "foreign_born_share":
        return f"{value:.1%}"
    if metric_id == "pop_growth":
        return f"{value:+.1%}"
    return f"{value:,.2f}"


@app.function
def benchmark_wide(benchmark: pd.DataFrame) -> pd.DataFrame:
    """One row per metric, formatted: Downstate | Rest of State | NY Total | NY rank | US."""
    df = benchmark.assign(
        shown=[format_benchmark_value(m, v) for m, v in zip(benchmark["metric_id"], benchmark["value"])]
    )
    wide = df.pivot(index=["metric_order", "lens", "metric_label"], columns="geography", values="shown")
    ranks = df.loc[df["state_rank"].notna()].set_index("metric_order")["state_rank"].astype(int)
    wide["NY rank"] = [ordinal(ranks[i]) if i in ranks.index else "" for i in wide.index.get_level_values(0)]
    wide = wide[["Downstate", "Rest of State", "NY Total", "NY rank", "US"]]
    return wide.reset_index(level=0, drop=True).reset_index()


@app.function
def draw_benchmark_table(benchmark: pd.DataFrame):
    """The benchmark as a print table: lens headings, one row per metric, NY rank beside NY Total."""
    wide = benchmark_wide(benchmark)
    columns = ["Downstate", "Rest of State", "NY Total", "NY rank", "US"]
    n_rows = len(wide) + wide["lens"].nunique()
    width_in = EXPORT_WIDTH_PX / EXPORT_DPI
    row_in, header_in, top_in, footer_in = 0.36, 0.45, 0.75, 0.35
    height_in = top_in + header_in + n_rows * row_in + footer_in
    fig = plt.figure(figsize=(width_in, height_in), dpi=EXPORT_DPI)
    fig.patch.set_facecolor(color("neutral.background_white"))

    def y_of(inches_from_top):
        return 1 - inches_from_top / height_in

    label_x, col_x = 0.03, [0.42, 0.57, 0.72, 0.83, 0.95]
    y = top_in + header_in * 0.6
    for x, name in zip(col_x, columns):
        fig.text(x, y_of(y), name, ha="right", va="center", fontsize=8.5, fontweight="bold", color=color("neutral.text"))
    fig.add_artist(plt.Line2D([label_x, 0.97], [y_of(top_in + header_in)] * 2, color=color("neutral.text"), linewidth=0.8))

    y = top_in + header_in
    for lens, rows in wide.groupby("lens", sort=False):
        y += row_in
        fig.text(label_x, y_of(y - row_in / 2), lens, ha="left", va="center", fontsize=8, fontweight="bold",
                 color=color("neutral.text_muted"))
        for _, row in rows.iterrows():
            y += row_in
            mid = y_of(y - row_in / 2)
            fig.text(label_x + 0.02, mid, row["metric_label"], ha="left", va="center", fontsize=8.5, color=color("neutral.text"))
            for x, name in zip(col_x, columns):
                fig.text(x, mid, row[name], ha="right", va="center", fontsize=8.5,
                         fontweight="bold" if name == "NY Total" else "normal",
                         color=color("neutral.text_muted") if name == "NY rank" else color("neutral.text"))
            fig.add_artist(plt.Line2D([label_x, 0.97], [y_of(y)] * 2, color=color("neutral.grid_major"), linewidth=0.5))
    return fig


@app.function
def draw_benchmark_strip(benchmark: pd.DataFrame):
    """One row per metric, each on its own scale, with a dot per geography and NY's rank at the right.

    Population leaves the US off the strip (it would flatten the other three) and notes it in text.
    """
    geo_style = {
        "Downstate": dict(color=color("highlight.strength"), marker="o"),
        "Rest of State": dict(color=color("quadrant.low_high"), marker="o"),
        "NY Total": dict(color=color("neutral.text"), marker="D"),
        "US": dict(color=color("neutral.text_muted"), marker="o", facecolor="white"),
    }
    metrics = benchmark.drop_duplicates("metric_id").sort_values("metric_order")
    width_in = EXPORT_WIDTH_PX / EXPORT_DPI
    row_in, top_in, legend_in, footer_in = 0.62, 0.75, 0.35, 0.35
    height_in = top_in + legend_in + len(metrics) * row_in + footer_in
    fig = plt.figure(figsize=(width_in, height_in), dpi=EXPORT_DPI)
    fig.patch.set_facecolor(color("neutral.background_white"))

    handles = [
        plt.Line2D([], [], linestyle="", markersize=6, label=name, marker=s["marker"],
                   markerfacecolor=s.get("facecolor", s["color"]), markeredgecolor=s["color"])
        for name, s in geo_style.items()
    ]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.02, 1 - top_in / height_in), ncol=4,
               frameon=False, fontsize=8, handletextpad=0.3, columnspacing=1.4)

    for i, metric in enumerate(metrics.itertuples()):
        bottom = 1 - (top_in + legend_in + (i + 1) * row_in) / height_in
        ax = fig.add_axes((0.30, bottom + 0.15 * row_in / height_in, 0.52, 0.7 * row_in / height_in))
        ax.set_axis_off()
        rows = benchmark.loc[benchmark["metric_id"] == metric.metric_id]
        shown = rows.loc[~((metric.metric_id == "population") & (rows["geography"] == "US"))]
        lo, hi = shown["value"].min(), shown["value"].max()
        pad = (hi - lo) * 0.12 or abs(hi) * 0.05
        ax.set_xlim(lo - pad, hi + pad)
        ax.set_ylim(-1, 1)
        ax.plot([lo, hi], [0, 0], color=color("neutral.grid_major"), linewidth=2.5, solid_capstyle="round", zorder=1)
        for j, row in enumerate(shown.itertuples()):
            s = geo_style[row.geography]
            ax.scatter(row.value, 0, s=42, marker=s["marker"], facecolor=s.get("facecolor", s["color"]),
                       edgecolor=s["color"], linewidth=1.2, zorder=3)
            # Alternate labels above and below so near-equal values don't collide.
            ax.annotate(format_benchmark_value(metric.metric_id, row.value), (row.value, 0),
                        xytext=(0, 8 if j % 2 == 0 else -8), textcoords="offset points", ha="center",
                        va="bottom" if j % 2 == 0 else "top", fontsize=6.5, color=s["color"])
        mid = bottom + 0.5 * row_in / height_in
        fig.text(0.03, mid, metric.metric_label, ha="left", va="center", fontsize=8.5, color=color("neutral.text"))
        rank = rows["state_rank"].dropna()
        note = f"NY {ordinal(int(rank.iloc[0]))} of 50" if len(rank) else ""
        if metric.metric_id == "population":
            us = rows.loc[rows["geography"] == "US", "value"].iloc[0]
            note += f"\nUS: {format_benchmark_value('population', us)}"
        fig.text(0.97, mid, note, ha="right", va="center", fontsize=7.5, color=color("neutral.text_muted"))
    return fig


@app.function
def add_text(fig, *, title: str, subtitle: str | None = None, source: str | None = None) -> None:
    """Left-aligned title, subtitle and source line, per the visual style guide."""
    height_in = fig.get_figheight()
    fig.text(0.02, 1 - 0.1 / height_in, title, ha="left", va="top", fontsize=13, fontweight="bold",
             color=color("neutral.text"))
    if subtitle:
        fig.text(0.02, 1 - 0.42 / height_in, subtitle, ha="left", va="top", fontsize=9,
                 color=color("neutral.text_muted"))
    if source:
        fig.text(0.02, 0.08 / height_in, source, ha="left", va="bottom", fontsize=6.5,
                 color=color("neutral.text_muted"))


@app.function
def save(fig, name: str, *, draft: bool = True) -> Path:
    """PNG at 2x Substack width. Drafts go to output/drafts/, finals to output/ with an SVG."""
    folder = DRAFTS_DIR if draft else OUTPUT_DIR
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.png"
    fig.savefig(path, dpi=EXPORT_DPI, facecolor=fig.get_facecolor())
    if not draft:
        fig.savefig(folder / f"{name}.svg", facecolor=fig.get_facecolor())
    return path


@app.function
def load_map2_layers(con, layers: dict) -> dict:
    """Load the published interface and one-off references without warehouse writes."""
    # Principal-city SQL derives display representative points. The earlier
    # visuals only read stored WKB, so their connection need not load spatial.
    con.execute("LOAD spatial")
    handoff = json.loads((HERE / "data/map2_infrastructure_handoff.json").read_text())
    artifact = REPO_ROOT / handoff["artifact_uri"]
    sql = read_sql(SQL_DIR / "map2_infrastructure.sql").replace(
        "__INFRASTRUCTURE_PATH__", artifact.as_posix().replace("'", "''")
    )
    network = con.sql(sql).df()
    assert network["source_record_key"].is_unique
    network = gpd.GeoDataFrame(
        network.drop(columns="geom_wkb"), geometry=shapely.from_wkb(network["geom_wkb"].map(bytes)),
        crs="EPSG:4326",
    ).to_crs(NY_CRS)
    # Clip display geometry only. The governed analytical artifact stays intact.
    network_drawn = network.clip(layers["outline"], keep_geom_type=True)
    canal = gpd.read_file(HERE / "data/canal_centerline.geojson").to_crs(NY_CRS)
    parks = pd.concat([
        gpd.read_file(HERE / "data/adirondack_park.geojson").to_crs(NY_CRS).assign(park="Adirondack Park"),
        gpd.read_file(HERE / "data/catskill_park.geojson").to_crs(NY_CRS).assign(park="Catskill Park"),
    ], ignore_index=True)
    landmarks = pd.read_csv(HERE / "reference/landmarks.csv", keep_default_na=False)
    # Number the original input order before applying keep, so an editorial cut
    # does not renumber every subsequent item in the review key.
    landmarks["marker_id"] = ""
    for kind, prefix in (("point", ""), ("port", "P")):
        mask = landmarks["kind"].eq(kind)
        landmarks.loc[mask, "marker_id"] = [f"{prefix}{i + 1}" for i in range(mask.sum())]
    landmarks["nyc_detail"] = (
        landmarks["kind"].eq("point") & landmarks["lon"].between(-74.06, -73.95)
        & landmarks["lat"].between(40.68, 40.78)
    )
    landmarks = landmarks.loc[landmarks["keep"]].copy()
    landmarks = gpd.GeoDataFrame(
        landmarks, geometry=gpd.points_from_xy(landmarks["lon"], landmarks["lat"]), crs="EPSG:4326"
    ).to_crs(NY_CRS)
    return dict(
        source_run_id=handoff["source_run_id"], network=network, network_drawn=network_drawn,
        canal=canal, canal_drawn=canal.clip(layers["outline"], keep_geom_type=True),
        parks=parks.clip(layers["outline"]), landmarks=landmarks,
        cities=read_geo(con, "ny_principal_cities.sql"),
    )


@app.function
def draw_lines(ax, frame, line_color: str, linewidth: float, *, linestyle="solid", zorder: int = 3) -> None:
    """Draw a selected line layer; layer toggles may leave an empty selection."""
    if not frame.empty:
        frame.plot(ax=ax, color=line_color, linewidth=linewidth, linestyle=linestyle, zorder=zorder)


@app.function
def draw_point_markers(ax, frame, *, marker="o", size=9, fill=None, edge="white", zorder=7) -> None:
    """Use source point locations for city dots and port symbols at both scales."""
    if not frame.empty:
        ax.scatter(frame.geometry.x, frame.geometry.y, s=size, marker=marker,
                   facecolor=fill or color("neutral.text"), edgecolor=edge, linewidth=0.5, zorder=zorder)


@app.function
def draw_landmark_numbers(ax, frame, offsets: dict, colors: dict, *, ports: bool = True, landmarks: bool = True) -> None:
    """Number landmarks at offset locations with leaders back to the actual coordinate."""
    for row in frame.itertuples():
        if row.kind == "area" or (row.kind == "port" and not ports) or (row.kind == "point" and not landmarks):
            continue
        is_port = row.kind == "port"
        point_color = colors["ports"] if is_port else colors["landmarks"]
        if is_port:
            draw_point_markers(ax, frame.loc[[row.Index]], marker="D", size=17, fill=point_color)
        else:
            ax.plot(row.geometry.x, row.geometry.y, ".", color=point_color, markersize=2, zorder=8)
        offset = offsets.get(row.marker_id, (0, 7) if is_port else (0, 0))
        ax.annotate(
            row.marker_id, (row.geometry.x, row.geometry.y), xytext=offset,
            textcoords="offset points", ha="center", va="center", fontsize=5.5,
            color=point_color, zorder=10,
            bbox=dict(boxstyle="round,pad=0.18" if is_port else "circle,pad=0.18",
                      facecolor="white", edgecolor=point_color, linewidth=0.55),
            arrowprops=dict(arrowstyle="-", color=point_color, linewidth=0.4) if offset != (0, 0) else None,
        )


@app.function
def draw_infrastructure_map(layers: dict, data: dict, visible: dict, colors: dict,
                            offsets: dict, city_offsets: dict, nyc_bounds: tuple):
    """All-input review draft: statewide network, NYC detail and a numbered key."""
    # Reserve a separate key area instead of squeezing every full landmark name
    # onto a state-scale map. The final editorial cut can shorten this review key.
    entries = data["landmarks"].loc[data["landmarks"]["kind"].isin(["point", "port"])]
    entries = entries.loc[entries["kind"].map({"point": visible["landmarks"], "port": visible["ports"]})]
    key_rows = (len(entries) + 1) // 2
    footer = 0.85 + key_rows * 0.18
    fig, ax = new_map(layers, footer_in=footer, header_in=0.85)
    if visible["parks"]:
        data["parks"].plot(ax=ax, color=colors["parks"], alpha=0.10, edgecolor=colors["parks"], linewidth=0.5)
    draw_regions(ax, layers, linewidth=0.45, line_color=color("neutral.border"))
    for kind, width, style in (("interstate", 0.45, "solid"), ("mainline_rail", 0.4, (0, (3, 2))),
                               ("thruway", 1.3, "solid")):
        if visible[kind]:
            draw_lines(ax, data["network_drawn"].loc[data["network_drawn"]["map_layer"].eq(kind)],
                       colors[kind], width, linestyle=style)
    if visible["canal"]:
        draw_lines(ax, data["canal_drawn"], colors["canal"], 0.95, zorder=5)
        draw_lines(ax, data["canal_drawn"].loc[data["canal_drawn"]["ROUTE"].eq("ER")],
                   colors["canal"], 1.8, zorder=5)
    draw_outline(ax, layers, linewidth=0.65)
    if visible["cities"]:
        draw_point_markers(ax, data["cities"], size=8)
        for row in data["cities"].itertuples():
            if row.primary_city in city_offsets:
                ax.annotate(row.primary_city, (row.geometry.x, row.geometry.y),
                            xytext=city_offsets[row.primary_city], textcoords="offset points",
                            ha="center", va="center", fontsize=6, fontweight="bold", zorder=9,
                            path_effects=[patheffects.withStroke(linewidth=2, foreground="white")])
    # Area rows are label anchors; the two park shapes come from official blue
    # lines. Finger Lakes remains a regional label with no invented boundary.
    for row in data["landmarks"].loc[data["landmarks"]["kind"].eq("area")].itertuples():
        if visible["parks"] or row.name == "Finger Lakes":
            label(ax, row.geometry.x, row.geometry.y, row.name.replace(" Park", "\nPark"),
                  size=6.5, text_color=colors["parks"])
    draw_landmark_numbers(ax, data["landmarks"].loc[~data["landmarks"]["nyc_detail"]], offsets, colors,
                          ports=visible["ports"], landmarks=visible["landmarks"])
    if visible["landmarks"]:
        point = to_map_points({"nyc": (-74.005, 40.73)})["nyc"]
        ax.plot(point.x, point.y, "o", color=colors["landmarks"], markersize=3, zorder=9)
        ax.annotate("NYC → detail", (point.x, point.y), xytext=(-36, -13),
                    textcoords="offset points", fontsize=6, fontweight="bold",
                    arrowprops=dict(arrowstyle="-", linewidth=0.6), zorder=10)
        # Place the detail in the map's empty Canadian context. Its extent is
        # declared in lon/lat and projected into the same CRS as the main map.
        detail = ax.inset_axes((0.025, 0.61, 0.28, 0.35))
        layers["neighbors"].plot(ax=detail, color=color("neutral.grid_minor"), edgecolor="white", linewidth=0.5)
        draw_outline(detail, layers, linewidth=0.5)
        for kind, width in (("interstate", 0.45), ("thruway", 0.9)):
            if visible[kind]:
                draw_lines(detail, data["network_drawn"].loc[data["network_drawn"]["map_layer"].eq(kind)],
                           colors[kind], width)
        window = gpd.GeoSeries([shapely.box(*nyc_bounds)], crs="EPSG:4326").to_crs(NY_CRS).iloc[0]
        draw_landmark_numbers(detail, data["landmarks"].loc[data["landmarks"].intersects(window)], offsets, colors,
                              ports=visible["ports"], landmarks=visible["landmarks"])
        detail.set_xlim(window.bounds[0], window.bounds[2])
        detail.set_ylim(window.bounds[1], window.bounds[3])
        detail.set_aspect("equal")
        detail.set_xticks([])
        detail.set_yticks([])
        detail.set_title("New York City · detail", fontsize=7, loc="left", pad=4)
        for spine in detail.spines.values():
            spine.set_edgecolor(color("neutral.border"))
    handles = [plt.Line2D([], [], color=colors[k], linewidth=w, linestyle=style, label=text)
               for k, w, style, text in (
                   ("canal", 1.8, "solid", "Canal system"), ("thruway", 1.3, "solid", "Thruway · named sections"),
                   ("interstate", 0.6, "solid", "Other interstate segments"),
                   ("mainline_rail", 0.6, (0, (3, 2)), "Main-line rail · tagged")) if visible[k]]
    if visible["ports"]:
        handles.append(plt.Line2D([], [], marker="D", color=colors["ports"], linestyle="", markersize=4, label="Port candidate"))
    if visible["cities"]:
        handles.append(plt.Line2D([], [], marker="o", color=color("neutral.text"), linestyle="", markersize=3, label="Principal city"))
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=6.5, handlelength=2.3)
    height = fig.get_figheight()
    fig.text(0.025, (footer - 0.16) / height, "LANDMARKS AND PORTS · ALL CANDIDATES FOR REVIEW",
             fontsize=7, fontweight="bold", color=color("neutral.text_muted"), va="top")
    for i, row in enumerate(entries.itertuples()):
        col, line = divmod(i, key_rows)
        fig.text(0.025 + col * 0.5, (footer - 0.43 - line * 0.18) / height,
                 f"{row.marker_id}  {row.name}", fontsize=6.7, va="top",
                 color=colors["ports"] if row.kind == "port" else color("neutral.text"))
    add_text(fig, title="The corridors that made New York",
             subtitle="Erie Canal and canal system · Thruway · interstates · main-line rail · landmarks",
             source="Sources: © OpenStreetMap contributors / Geofabrik (17 Oct 2026); NYS Canal Corporation; APA; NYS DEC.\n"
                    "Landmark coordinates: Wikipedia, OSM and official records. Working draft; source tagging is incomplete.")
    return fig


@app.function
def offset_align(offset: tuple) -> str:
    """Horizontal alignment that keeps an offset label clear of its marker."""
    dx, dy = offset
    if abs(dx) >= abs(dy) and dx != 0:
        return "left" if dx > 0 else "right"
    return "center"


@app.function
def draw_city_labels(ax, cities: gpd.GeoDataFrame, offsets: dict, *, size: float = 6, dot_size: float = 8) -> None:
    """Dots and bold names for the principal cities listed in `offsets` (city -> offset in points)."""
    shown = cities.loc[cities["primary_city"].isin(offsets)]
    draw_point_markers(ax, shown, size=dot_size)
    for row in shown.itertuples():
        ax.annotate(row.primary_city, (row.geometry.x, row.geometry.y), xytext=offsets[row.primary_city],
                    textcoords="offset points", ha="center", va="center", fontsize=size, fontweight="bold",
                    color=color("neutral.text"), zorder=9,
                    path_effects=[patheffects.withStroke(linewidth=2, foreground="white")])


@app.function
def draw_share_notes(ax, shares: pd.DataFrame, positions: dict, colors: dict, names: dict | None = None) -> None:
    """A heading and 'x% of people / y% of land' under it, for each geography in `positions`.

    `names` maps a geography to its printed heading, e.g. Rest of State -> Upstate.
    """
    halo = [patheffects.withStroke(linewidth=2.5, foreground="white")]
    for geography, point in to_map_points(positions).items():
        row = shares.loc[geography]
        ax.annotate((names or {}).get(geography, geography).upper(), (point.x, point.y), ha="center", va="bottom", fontsize=7.5,
                    fontweight="bold", color=colors[geography], path_effects=halo, zorder=10)
        ax.annotate(f"{row['pop_share']:.0%} of people\n{row['land_share']:.0%} of land", (point.x, point.y),
                    xytext=(0, -2), textcoords="offset points", ha="center", va="top", fontsize=7,
                    color=colors[geography], path_effects=halo, zorder=10)


@app.function
def draw_micros(ax, layers: dict, *, positions: dict | None = None, size: float = 5.3) -> None:
    """Micro outlines, dashed and darker than v1 so they read over region fills, with first-city labels."""
    placed = to_map_points(positions)
    drawn = layers["cbsas_drawn"]
    micros = drawn.loc[drawn["cbsa_type"] == "micro"]
    micros.boundary.plot(ax=ax, color=color("neutral.text_muted"), linewidth=0.7, linestyle=(0, (3, 1.5)))
    for row in micros.itertuples():
        point = placed.get(row.cbsa_code, row.geometry.representative_point())
        label(ax, point.x, point.y, default_cbsa_label(row.cbsa_name, "short"), size=size,
              text_color=color("neutral.text_muted"))


@app.function
def add_as_if_ranks(benchmark: pd.DataFrame, states: pd.DataFrame) -> pd.DataFrame:
    """Rank each non-US value against the 49 states other than NY, out of 50 (1 = highest)."""
    others = states.loc[states["geo_id"] != "36"]

    def rank(row):
        if row.geography == "US":
            return pd.NA
        values = others.loc[others["metric_id"] == row.metric_id, "value"]
        return 1 + int((values > row.value).sum())

    return benchmark.assign(as_if_rank=[rank(row) for row in benchmark.itertuples()])


@app.function
def draw_benchmark_table_v2(benchmark: pd.DataFrame):
    """v2 print table: each value with its as-if-a-state rank, plus a share-of-New-Yorkers row."""
    geos = ["Downstate", "Rest of State", "NY Total", "US"]
    headers = {"Downstate": "Downstate", "Rest of State": "Upstate", "NY Total": "New York", "US": "US"}
    header_colors = {
        "Downstate": color("highlight.strength"), "Rest of State": color("quadrant.low_high"),
        "NY Total": color("neutral.text"), "US": color("neutral.text_muted"),
    }
    value_x = {"Downstate": 0.42, "Rest of State": 0.61, "NY Total": 0.80, "US": 0.965}
    values = benchmark.set_index(["metric_id", "geography"])
    metrics = benchmark.drop_duplicates("metric_id").sort_values("metric_order")
    pop = values.loc["population", "value"]

    n_rows = len(metrics) + 1 + metrics["lens"].nunique()
    width_in = EXPORT_WIDTH_PX / EXPORT_DPI
    row_in, header_in, top_in, footer_in = 0.36, 0.45, 0.75, 0.5
    height_in = top_in + header_in + n_rows * row_in + footer_in
    fig = plt.figure(figsize=(width_in, height_in), dpi=EXPORT_DPI)
    fig.patch.set_facecolor(color("neutral.background_white"))

    def y_of(inches_from_top):
        return 1 - inches_from_top / height_in

    def rule(y):
        fig.add_artist(plt.Line2D([label_x, 0.97], [y_of(y)] * 2, color=color("neutral.grid_major"), linewidth=0.5))

    label_x = 0.03
    y = top_in + header_in * 0.6
    for g in geos:
        fig.text(value_x[g] + (0.045 if g != "US" else 0), y_of(y), headers[g], ha="right", va="center",
                 fontsize=8.5, fontweight="bold", color=header_colors[g])
    fig.add_artist(plt.Line2D([label_x, 0.97], [y_of(top_in + header_in)] * 2, color=color("neutral.text"), linewidth=0.8))

    y = top_in + header_in
    for lens, rows in metrics.groupby("lens", sort=False):
        y += row_in
        fig.text(label_x, y_of(y - row_in / 2), lens, ha="left", va="center", fontsize=8, fontweight="bold",
                 color=color("neutral.text_muted"))
        for metric in rows.itertuples():
            y += row_in
            mid = y_of(y - row_in / 2)
            fig.text(label_x + 0.02, mid, metric.metric_label, ha="left", va="center", fontsize=8.5, color=color("neutral.text"))
            for g in geos:
                cell = values.loc[(metric.metric_id, g)]
                fig.text(value_x[g], mid, format_benchmark_value(metric.metric_id, cell["value"]), ha="right",
                         va="center", fontsize=8.5, fontweight="bold" if g == "NY Total" else "normal",
                         color=color("neutral.text"))
                if g != "US" and pd.notna(cell["as_if_rank"]):
                    fig.text(value_x[g] + 0.012, mid, ordinal(int(cell["as_if_rank"])), ha="left", va="center",
                             fontsize=7.2, color=color("neutral.text_muted"))
            if metric.metric_id == "population":
                y += row_in
                mid = y_of(y - row_in / 2)
                fig.text(label_x + 0.04, mid, "Share of New Yorkers", ha="left", va="center", fontsize=7.8,
                         color=color("neutral.text_muted"))
                for g in ("Downstate", "Rest of State", "NY Total"):
                    fig.text(value_x[g], mid, f"{pop[g] / pop['NY Total']:.0%}", ha="right", va="center",
                             fontsize=7.8, color=color("neutral.text_muted"))
            rule(y)
    return fig


@app.function
def load_map2v2_water(con) -> gpd.GeoDataFrame:
    """Hudson River lines from the same Infrastructure handoff as Map 2, read-only, in NY_CRS."""
    con.execute("LOAD spatial")
    handoff = json.loads((HERE / "data/map2_infrastructure_handoff.json").read_text())
    artifact = REPO_ROOT / handoff["artifact_uri"]
    sql = read_sql(SQL_DIR / "map2_v2_water.sql").replace(
        "__INFRASTRUCTURE_PATH__", artifact.as_posix().replace("'", "''")
    )
    water = con.sql(sql).df()
    return gpd.GeoDataFrame(
        water.drop(columns="geom_wkb"), geometry=shapely.from_wkb(water["geom_wkb"].map(bytes)), crs="EPSG:4326"
    ).to_crs(NY_CRS)


@app.function
def draw_infrastructure_map_v2(layers: dict, data: dict, water: gpd.GeoDataFrame, colors: dict, landmarks: dict,
                               ports: dict, city_offsets: dict, area_positions: dict, nyc_callout: dict):
    """Infrastructure-first Map 2: canal, Hudson, Thruway, interstates, rail; a short landmark cut, labeled directly."""
    halo = [patheffects.withStroke(linewidth=2, foreground="white")]
    fig, ax = new_map(layers, header_in=0.85, footer_in=0.45)
    data["parks"].plot(ax=ax, color=colors["parks"], alpha=0.10, edgecolor=colors["parks"], linewidth=0.5)
    network = data["network_drawn"]
    for kind, width, style, z in (("interstate", 0.5, "solid", 3), ("mainline_rail", 0.45, (0, (3, 2)), 3),
                                  ("thruway", 1.3, "solid", 4)):
        draw_lines(ax, network.loc[network["map_layer"].eq(kind)], colors[kind], width, linestyle=style, zorder=z)
    draw_lines(ax, water, colors["river"], 1.2, zorder=4)
    canal = data["canal_drawn"]
    draw_lines(ax, canal.loc[~canal["ROUTE"].eq("ER")], colors["canal"], 0.9, zorder=5)
    draw_lines(ax, canal.loc[canal["ROUTE"].eq("ER")], colors["canal"], 1.9, zorder=5)
    draw_outline(ax, layers, linewidth=0.65)
    draw_city_labels(ax, data["cities"], city_offsets)

    places = data["landmarks"]
    moved = to_map_points(area_positions)
    for row in places.loc[places["kind"].eq("area")].itertuples():
        point = moved.get(row.name, row.geometry)
        label(ax, point.x, point.y, row.name.replace(" Park", "\nPark"), size=6.5, text_color=colors["parks"])

    for row in places.loc[places["name"].isin(landmarks)].itertuples():
        text, offset = landmarks[row.name]
        ax.plot(row.geometry.x, row.geometry.y, "o", markersize=3.4, markerfacecolor="white",
                markeredgecolor=colors["landmarks"], markeredgewidth=0.9, zorder=8)
        ax.annotate(text, (row.geometry.x, row.geometry.y), xytext=offset, textcoords="offset points",
                    ha=offset_align(offset), va="center", fontsize=5.8, color=colors["landmarks"],
                    path_effects=halo, zorder=9, linespacing=1.0)

    shown_ports = places.loc[places["name"].isin(ports)]
    draw_point_markers(ax, shown_ports, marker="D", size=16, fill=colors["ports"], zorder=8)
    for row in shown_ports.itertuples():
        if ports[row.name]:
            text, offset = ports[row.name]
            ax.annotate(text, (row.geometry.x, row.geometry.y), xytext=offset, textcoords="offset points",
                        ha=offset_align(offset), va="center", fontsize=5.8, color=colors["ports"],
                        path_effects=halo, zorder=9)

    points = to_map_points({"at": nyc_callout["at"], "text_at": nyc_callout["text_at"]})
    ax.plot(points["at"].x, points["at"].y, "o", color=colors["landmarks"], markersize=3, zorder=9)
    ax.annotate(nyc_callout["title"], (points["at"].x, points["at"].y), xytext=(points["text_at"].x, points["text_at"].y),
                ha="right", va="bottom", fontsize=6.5, fontweight="bold", color=colors["landmarks"], zorder=10,
                path_effects=halo, arrowprops=dict(arrowstyle="-", linewidth=0.6, color=colors["landmarks"]))
    ax.text(points["text_at"].x, points["text_at"].y, nyc_callout["body"], ha="right", va="top", fontsize=5.8,
            color=colors["landmarks"], path_effects=halo, zorder=10, linespacing=1.1)

    handles = [
        plt.Line2D([], [], color=colors["canal"], linewidth=1.9, label="Erie Canal"),
        plt.Line2D([], [], color=colors["canal"], linewidth=0.9, label="Other canal routes"),
        plt.Line2D([], [], color=colors["river"], linewidth=1.2, label="Hudson River"),
        plt.Line2D([], [], color=colors["thruway"], linewidth=1.3, label="Thruway"),
        plt.Line2D([], [], color=colors["interstate"], linewidth=0.7, label="Other interstates"),
        plt.Line2D([], [], color=colors["mainline_rail"], linewidth=0.6, linestyle=(0, (3, 2)), label="Main-line rail"),
        plt.Line2D([], [], marker="D", color=colors["ports"], linestyle="", markersize=4, label="Port"),
        plt.Line2D([], [], marker="o", markerfacecolor="white", markeredgecolor=colors["landmarks"], linestyle="",
                   markersize=4, label="Landmark"),
    ]
    ax.legend(handles=handles, loc="lower left", frameon=False, fontsize=6.5, handlelength=2.3)
    add_text(fig, title="The corridors that made New York",
             subtitle="The Erie Canal set the line from Buffalo to Albany. The Thruway and the railroads still follow it",
             source="Sources: © OpenStreetMap contributors / Geofabrik (17 Oct 2026), roads, rail and the Hudson; "
                    "NYS Canal Corporation; APA; NYS DEC.\nThruway = named sections in OSM; main-line rail = tagged "
                    "usage=main. Landmark coordinates: Wikipedia, OSM and official records.")
    return fig


@app.function
def history_figure(*, height_in: float = 4.7, header_in: float = 0.85, footer_in: float = 0.75,
                   left_in: float = 0.5, right_in: float = 1.2):
    """A line-chart frame that matches the maps: same width, title space on top, source space below."""
    width_in = EXPORT_WIDTH_PX / EXPORT_DPI
    fig = plt.figure(figsize=(width_in, height_in), dpi=EXPORT_DPI)
    fig.patch.set_facecolor(color("neutral.background_white"))
    ax = fig.add_axes((left_in / width_in, footer_in / height_in, 1 - (left_in + right_in) / width_in,
                       1 - (header_in + footer_in) / height_in))
    ax.set_facecolor(color("neutral.background_white"))
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(color("neutral.border"))
    ax.tick_params(colors=color("neutral.axis"), labelsize=7.5, length=0)
    ax.set_xlim(1805, 2025)
    ax.set_xticks([1810, 1850, 1900, 1950, 2000, 2020])
    ax.grid(axis="y", color=color("neutral.grid_major"), linewidth=0.5)
    ax.set_axisbelow(True)
    return fig, ax


@app.function
def draw_history_end_labels(ax, ends: dict, colors: dict, label_dy: dict) -> None:
    """Direct labels right of the last census: {geography: (y, text)}."""
    for geography, (y, text) in ends.items():
        ax.annotate(text, (2020, y), xytext=(7, label_dy.get(geography, 0)), textcoords="offset points",
                    ha="left", va="center", fontsize=7.5, color=colors[geography], annotation_clip=False,
                    fontweight="bold" if geography == "New York" else "normal")


@app.function
def draw_rank_history(history: pd.DataFrame, colors: dict, events: dict, label_dy: dict):
    """Rank among the states at each census, on an inverted log axis so ranks 1-4 spread out."""
    fig, ax = history_figure()
    ranked = history.loc[history["state_rank"].notna()]
    ax.set_yscale("log")
    ax.set_ylim(40, 0.68)
    ticks = [1, 2, 3, 4, 5, 10, 20, 30]
    ax.set_yticks(ticks, [ordinal(t) for t in ticks])
    ax.minorticks_off()
    ax.axvspan(1805, 1965, color=color("neutral.grid_minor"), zorder=0, linewidth=0)
    ax.text(1885, 0.8, "New York 1st at every census, 1810–1960", ha="center", va="center", fontsize=7,
            color=color("neutral.text_muted"))
    ends = {}
    for geography, line_color in colors.items():
        rows = ranked.loc[ranked["geography"] == geography]
        is_ny = geography == "New York"
        ax.plot(rows["year"], rows["state_rank"], color=line_color, linewidth=2.3 if is_ny else 1.4,
                marker="o", markersize=3.2 if is_ny else 2.4, zorder=4 if is_ny else 3)
        last = rows.iloc[-1]
        ends[geography] = (last["state_rank"], f"{geography} · {ordinal(int(last['state_rank']))}")
    ny = ranked.loc[ranked["geography"] == "New York"].set_index("year")["state_rank"]
    for year, (text, offset) in events.items():
        ax.annotate(text, (year, ny[year]), xytext=offset, textcoords="offset points", ha="center", va="center",
                    fontsize=6.5, color=colors["New York"], zorder=6,
                    path_effects=[patheffects.withStroke(linewidth=2.5, foreground="white")])
    draw_history_end_labels(ax, ends, colors, label_dy)
    return fig


@app.function
def draw_share_history(history: pd.DataFrame, colors: dict, notes: dict, label_dy: dict):
    """Each state's share of the US population at each census."""
    fig, ax = history_figure()
    us = history.loc[history["geography"] == "United States"].set_index("year")["population"]
    states = history.loc[(history["geography"] != "United States") & history["population"].notna()].copy()
    states["share"] = states["population"] / states["year"].map(us)
    ax.set_ylim(0, 0.17)
    ax.set_yticks([0, 0.05, 0.10, 0.15], ["0%", "5%", "10%", "15%"])
    ends = {}
    for geography, line_color in colors.items():
        rows = states.loc[states["geography"] == geography]
        is_ny = geography == "New York"
        ax.plot(rows["year"], rows["share"], color=line_color, linewidth=2.3 if is_ny else 1.4,
                marker="o", markersize=3.2 if is_ny else 2.4, zorder=4 if is_ny else 3)
        last = rows.iloc[-1]
        ends[geography] = (last["share"], f"{geography} · {last['share']:.1%}")
    shares = states.set_index(["geography", "year"])["share"]
    for (geography, year), (text, offset) in notes.items():
        ax.annotate(text, (year, shares[(geography, year)]), xytext=offset, textcoords="offset points",
                    ha="center", va="bottom", fontsize=6.5, color=colors[geography], zorder=6,
                    path_effects=[patheffects.withStroke(linewidth=2.5, foreground="white")])
    draw_history_end_labels(ax, ends, colors, label_dy)
    return fig


if __name__ == "__main__":
    app.run()
