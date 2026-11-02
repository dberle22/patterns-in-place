import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")

with app.setup:
    import json
    import sys
    import numpy as np
    from pathlib import Path
    import geopandas as gpd
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd
    import shapely
    from matplotlib.patches import Patch

    HERE = Path(__file__).resolve().parent
    # Queries only this lens uses; shared ones are in SQL_DIR (albany/sql/).
    LENS_SQL_DIR = HERE / "sql"
    OUTPUT_DIR = HERE / "output"
    DRAFTS_DIR = OUTPUT_DIR / "drafts"

    # Paths, constants and helpers shared by every Albany lens.
    sys.path.insert(0, str(HERE.parent))
    from albany_common import (
        ACTIVITY_COLORS,
        ACTIVITY_ORDER,
        ACTIVITY_RULES,
        ADIRONDACK_GEOJSON,
        ANALYSES_DIR,
        ANCHORS_CSV,
        CANAL_GEOJSON,
        CBSA_CODE,
        CORE_AREA_STYLES,
        CORE_DETAIL_GEOJSON,
        EXPORT_DPI,
        EXPORT_WIDTH_PX,
        INFRA_HANDOFF,
        INFRA_SQL,
        IRS_TOTALS_CSV,
        MAP_CRS,
        NORTHWAY_ARM,
        PARKS_CSV,
        PARKS_GEOJSON,
        POI_RUN_DIR,
        REPO_ROOT,
        RIVER_COLOR,
        SQL_DIR,
        TRIANGLE_TOWNS,
        ZONE_COLORS,
        ZONE_NAMES,
        add_text,
        all_jobs_centers,
        chart_figure,
        classify,
        classify_migration,
        color,
        connect_duckdb,
        core_box,
        county_short_name,
        draw_anchor_key,
        draw_anchors,
        draw_core_areas,
        draw_county_flags,
        draw_county_labels,
        draw_county_lines,
        draw_metro_counties,
        draw_metro_outline,
        draw_numbered_anchors,
        draw_parks,
        draw_place_outlines,
        draw_region_lines,
        draw_route_labels,
        draw_text_table,
        draw_towns,
        draw_tract_classes,
        format_count,
        format_metric,
        halo,
        irs_flows_reversed,
        key_row_count,
        load_metro_layers,
        load_towns,
        load_tract_profile,
        metro_county_table,
        metro_wide,
        new_box_map,
        new_detail_map,
        new_map,
        offset_align,
        position_words,
        region_legend,
        run_sql,
        short_metro,
        sql_list,
        style_axes,
        tex_safe,
        to_geo,
        tract_activity,
        upstate_aggregate,
        upstate_sets,
    )


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Albany, Lens 1: Visuals

    The print exhibits for the article (text in the vault), in the article's order (rebuilt 2026-10-27 to follow Dan's
    draft). Geography: the 5-county Albany-Schenectady-Troy CBSA (10580), 2023 delineation (D4).
    Exploration and reads live in `ALBANY_LENS1_EXPLORATION.py`; an exhibit is built here once its view is
    chosen there. Each section's data cell ends with a check table that tests the numbers the text uses.
    Drafts save to `output/drafts/`. The shared drawing functions are in the **Helpers** section at the end.

    | # | Exhibit | Section |
    |---|---|---|
    | E0b | At a glance: percentile dot plot (Dan picked the dots over the number cards, 2026-10-27) | Albany Today |
    | E1, E1c | The metro on the map, and the core detail | The Metro on the Map |
    | E2 | Albany vs Buffalo, real GDP 2012–24 | What Kind of Place |
    | E3 | Migration in and out, by where people came from or went (rebuilt on the IRS county totals) | What Kind of Place |
    | E4 | The 10 peers with core metrics | What Kind of Place |
    | E5 | Top places: cities and towns | How It's Assembled: where people live |
    | E6, E7 | Population density and the arrow (the triangle and its Northway arm); residents and land by area | How It's Assembled: where people live |
    | E8 | Job centers on all jobs, by public share | How It's Assembled: where people work |
    | E9, E10 | Zone map; zone table with what's there (activity classes) | How It's Assembled: summary zones |

    Exhibit numbers have gaps (no E0a, E11 or E12: cut 2026-10-27; E3 came back the same day, rebuilt) so they still match the draft's review
    notes; renumber before print.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Shared setup

    Base layers: the five metro counties with their OMB flag, neighboring counties as
    grey context, Hudson and Mohawk river lines, and a display point for each Census
    Place in the metro.
    """)
    return


@app.cell
def _():
    con = connect_duckdb()
    con.execute("LOAD spatial")
    layers = load_metro_layers(con)
    return con, layers


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1. Albany Today: In a Nutshell (E0b)

    The standard opening profile (Dan, 2026-10-24): eight metrics, not all economic, as a
    **percentile dot plot** (Dan chose it over number cards, 2026-10-27). Ranks are
    among the 393 US metro areas (2023 delineation) and the 12 Upstate metros (series default:
    NY outside NYC, Long Island, Westchester, Putnam and Rockland). Source years differ by
    metric and are named in each source line.
    """)
    return


@app.cell
def _():
    # Metric -> (printed label, format kind from format_metric). Order = dot-plot rows.
    nutshell_metrics = {
        "pop_total": ("Population", "count"),
        "pop_growth_10yr": ("Population growth, 10 years", "change"),
        "median_hh_income": ("Median household income", "usd"),
        "calc_income_pc": ("Income per person", "usd"),
        "median_home_value": ("Median home value", "usd"),
        "pct_ba_plus": ("Bachelor's degree or higher", "pct"),
        "median_age": ("Median age", "years"),
        "pct_nonwhite": ("Non-white residents", "pct"),
    }
    # How Upstate is built from its counties: (rule, exact); unlisted = population-weighted, approximate.
    nutshell_upstate_rules = {"pop_total": ("sum", True), "pop_growth_10yr": ("growth", True), "pct_nonwhite": ("pop_total", True)}
    nutshell_source = (
        "Source: ACS 2020–24 5-year (growth vs 2010–14); BEA 2023 (income per person). US metro areas: OMB 2023 delineation.\n"
        "Upstate: NY outside NYC, Long Island, Westchester, Putnam and Rockland; ≈ = population-weighted county approximation."
    )
    return nutshell_metrics, nutshell_source, nutshell_upstate_rules


@app.cell
def _(con, nutshell_metrics, nutshell_upstate_rules):
    nutshell_raw = run_sql(con, LENS_SQL_DIR / "q4_metro_scorecard.sql")
    _counties, nutshell_upstate_metros, _set_checks = upstate_sets(con, nutshell_raw)
    _upstate = upstate_aggregate(nutshell_raw, _counties, nutshell_metrics, nutshell_upstate_rules)
    nutshell = nutshell_table(nutshell_raw, nutshell_metrics, nutshell_upstate_metros, _upstate)
    _n = nutshell.set_index("metric_id")
    # The confirmed reads (Review 7): a data refresh that changes a printed claim fails here.
    nutshell_checks = pd.DataFrame([
        ("Population 906k, #64 of 393, 3rd of 12 Upstate", f"{_n.loc['pop_total', 'value']:,.0f}",
         round(_n.loc["pop_total", "value"]) == 906_052 and _n.loc["pop_total", "us_rank"] == 64 and _n.loc["pop_total", "upstate_rank"] == 3),
        ("Growth +3.5%, 2nd of 12 Upstate; Upstate flat", f"{_n.loc['pop_growth_10yr', 'value']:+.1%} / {_n.loc['pop_growth_10yr', 'upstate']:+.1%}",
         round(_n.loc["pop_growth_10yr", "value"], 3) == 0.035 and _n.loc["pop_growth_10yr", "upstate_rank"] == 2
         and abs(_n.loc["pop_growth_10yr", "upstate"]) < 0.005),
        ("Income per person 1st of 12 Upstate", _n.loc["calc_income_pc", "upstate_rank"], _n.loc["calc_income_pc", "upstate_rank"] == 1),
        ("Bachelor's 42.1%, #49 of 393", f"{_n.loc['pct_ba_plus', 'value']:.1%}",
         round(_n.loc["pct_ba_plus", "value"], 3) == 0.421 and _n.loc["pct_ba_plus", "us_rank"] == 49),
    ], columns=["check", "value", "passed"])
    assert nutshell_checks["passed"].all(), nutshell_checks
    mo.vstack([_set_checks, nutshell_checks, nutshell])
    return nutshell, nutshell_raw, nutshell_upstate_metros


@app.cell
def _(nutshell, nutshell_metrics, nutshell_raw, nutshell_source, nutshell_upstate_metros):
    nutshell_dots_fig = draw_nutshell_dots(nutshell, nutshell_raw, nutshell_metrics, nutshell_upstate_metros)
    add_text(
        nutshell_dots_fig,
        title="High on income and education, middle of the pack on growth and age",
        subtitle="Where each metro ranks among the 393 US metro areas (percentile; 100 = highest value)",
        source=nutshell_source,
    )
    save(nutshell_dots_fig, "e0b_nutshell_dots")
    nutshell_dots_fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 2. A Bit of History

    No exhibit. The history's places (Fort Orange, the Stockade, the Waterford Flight, Saratoga, the GE works,
    the Capitol and Empire State Plaza, the colleges) are on the E1 map as key places, so the map can carry
    them in the next section.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3. The Metro on the Map (E1, E1c)

    What the region is, on one page: the five counties (central or outlying), the four cities'
    outlines, the other places you choose to show, highways, main-line rail, the canal, the
    rivers, and the key places by theme. Two static figures: the **whole metro**, and a
    **core detail** (Albany, Troy, Schenectady) where the landmarks are numbered with a key.
    Population density moved to How It's Assembled (E6), so it's shown once.

    Places are Census places: cities, villages and CDPs. **Towns aren't Census places in New
    York**, so Colonie, Clifton Park, Bethlehem and Guilderland have no outline here; only
    their CDPs do (Latham, Loudonville, Delmar and so on).
    """)
    return


@app.cell
def _(con, layers):
    map_places = to_geo(run_sql(con, SQL_DIR / "metro_place_outlines.sql", cbsa_code=CBSA_CODE))
    map_places = map_places.assign(
        county=lambda df: gpd.sjoin(
            gpd.GeoDataFrame(geometry=df.geometry.representative_point(), crs=MAP_CRS),
            layers["counties"][["county_name", "geometry"]], how="left", predicate="within",
        )["county_name"].map(county_short_name).to_numpy()
    )
    _artifact = REPO_ROOT / json.loads(INFRA_HANDOFF.read_text())["artifact_uri"]
    _infra = to_geo(run_sql(con, INFRA_SQL, infrastructure_path=_artifact.as_posix().replace("'", "''")), crs="EPSG:4326")
    map_lines = {
        "thruway": _infra.loc[_infra["map_layer"] == "thruway"],
        "interstate": _infra.loc[_infra["map_layer"] == "interstate"],
        "rail": _infra.loc[_infra["map_layer"] == "mainline_rail"],
        "canal": gpd.read_file(CANAL_GEOJSON).to_crs(MAP_CRS),
    }
    # Lines within 25 km of the metro, so they run off the frame's edges rather than stopping at them.
    _clip = layers["outline"].buffer(25_000).iloc[0]
    map_lines = {k: v.loc[v.intersects(_clip)].clip(_clip) for k, v in map_lines.items()}
    _anchors = pd.read_csv(ANCHORS_CSV, dtype={"overture_id": str}).query("keep == True")
    map_anchors = gpd.GeoDataFrame(
        _anchors, geometry=gpd.points_from_xy(_anchors["lon"], _anchors["lat"]), crs="EPSG:4326"
    ).to_crs(MAP_CRS)
    map_towns = load_towns(layers)
    _parks_keep = pd.read_csv(PARKS_CSV).query("keep == True")
    map_parks = gpd.read_file(PARKS_GEOJSON).to_crs(MAP_CRS).merge(_parks_keep[["osm_id"]], on="osm_id")
    map_adirondack = gpd.read_file(ADIRONDACK_GEOJSON).to_crs(MAP_CRS).clip(_clip)
    map_core_areas = gpd.read_file(CORE_DETAIL_GEOJSON).to_crs(MAP_CRS)
    map_checks = pd.DataFrame({
        "check": ["65 metro places", "anchors kept", "every anchor inside the metro", "line features in frame",
                  "72 towns and cities", "town populations sum to the metro (ACS 2020-24)", "parks kept", "Adirondack Park reaches the metro",
                  "E1c areas: 1 airport, 10 hospitals, 16 campus polygons, parks of 10+ acres"],
        "value": [len(map_places), len(map_anchors), bool(map_anchors.within(layers["outline"].iloc[0].geometry).all()),
                  {k: len(v) for k, v in map_lines.items()}, len(map_towns), f"{map_towns['population'].sum():,.0f}",
                  len(map_parks), bool(map_adirondack.intersects(layers["outline"].iloc[0].geometry).any()),
                  map_core_areas["layer"].value_counts().to_dict()],
        "passed": [len(map_places) == 65, len(map_anchors) > 0, bool(map_anchors.within(layers["outline"].iloc[0].geometry).all()),
                   all(len(v) for v in map_lines.values()), len(map_towns) == 72, map_towns["population"].sum() == 906_052,
                   len(map_parks) == len(_parks_keep), bool(map_adirondack.intersects(layers["outline"].iloc[0].geometry).any()),
                   map_core_areas["layer"].value_counts().reindex(["airport", "hospital", "campus"]).tolist() == [1, 10, 16]],
    })
    assert map_checks["passed"].all(), map_checks
    map_checks
    return map_adirondack, map_anchors, map_core_areas, map_lines, map_parks, map_places, map_towns


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Every place in the metro**, largest first, to decide which to show. `map1v2_places` below
    holds the current pick; the four cities are always drawn and labeled.
    """)
    return


@app.cell
def _(map_towns):
    mo.vstack([
        mo.md("**Every town and city** (county subdivisions), largest first. In NY these, not Census places, are the "
              "municipalities: Colonie, Clifton Park and Bethlehem are towns. `map1v2_towns` holds the labels shown."),
        mo.ui.table(map_towns.drop(columns="geometry").sort_values("population", ascending=False)
                    .assign(metro_share=lambda d: (d["population"] / d["population"].sum()).round(3)),
                    page_size=25, selection=None),
    ])
    return


@app.cell
def _(map_places):
    mo.ui.table(
        map_places.drop(columns="geometry").assign(population_in_metro=lambda d: d["population_in_metro"].round())[
            ["place_name", "place_kind", "county", "population_in_metro", "is_principal_city"]],
        page_size=25, selection=None,
    )
    return


@app.cell
def _():
    map1v2_colors = {"Central": "#DCE6EF", "Outlying": "#EFE8D2"}
    # Other places to outline and label (beyond the four cities): the other cities, the CDPs over
    # about 6k, and the two Schoharie County villages. Edit freely; names as in the table above.
    # Delmar (Bethlehem) and Clifton Park have no Census place in the 2020 boundaries, so they can't be drawn.
    map1v2_places = [
        "Cohoes", "Watervliet", "Rensselaer", "Mechanicville",
        "Rotterdam", "Niskayuna", "Latham", "East Glenville", "Roessleville", "Loudonville", "Westmere", "East Greenbush",
        "Ballston Spa", "Scotia", "Cobleskill", "Schoharie",
    ]
    # Theme -> (color, marker). Legend and key order follow this dict.
    map1v2_themes = {
        "State government": ("#6A3D9A", "*"),
        "History and the canal": ("#A0522D", "^"),
        "Education and research": ("#1F78B4", "s"),
        "Health": ("#D7263D", "P"),
        "Industry": ("#4D4D4D", "D"),
        "Transport": ("#00838F", "o"),
        "Parks and nature": ("#2E8B3E", "v"),
        "Culture and sports": ("#E07B00", "p"),
    }
    # The core detail's extent (lon, lat): the Albany–Troy–Schenectady triangle with Latham and the airport.
    map1v2_core = (-74.0, 42.6, -73.64, 42.86)
    # Label offsets in points, for the whole-metro map. Places: from the place's label point; anchors: from the marker.
    # Inside the core box the metro map labels only the four cities; the core detail labels the rest.
    map1v2_place_offsets = {"Albany": (-16, -12), "Schenectady": (-24, 10), "Troy": (14, 4), "Saratoga Springs": (-34, 2)}
    map1v2_anchor_offsets = {
        "Skidmore College": (6, 7), "Saratoga Race Course": (7, 3),
        "Saratoga Performing Arts Center": (7, -3), "Saratoga Spa State Park": (-7, -6),
    }
    # The core's main places, also shown on the whole-metro map (Dan, 2026-10-27): name -> (short label, offset).
    map1v2_metro_core_anchors = {
        "New York State Capitol": ("State Capitol", (7, -6)), "University at Albany": ("UAlbany", (-6, 6)),
        "Albany International Airport": ("Airport", (0, 8)), "Rensselaer Polytechnic Institute": ("RPI", (7, -7)),
        "Union College": ("Union College", (6, 6)), "GE Vernova Schenectady works": ("GE Vernova", (-6, -7)),
    }
    # The same for the core detail.
    map1v2_core_place_offsets = {"Albany": (-34, -2), "Schenectady": (-8, 24), "Watervliet": (-22, 12), "Rensselaer": (26, -4), "Troy": (14, 30)}
    map1v2_core_anchor_offsets = {
        "New York State Capitol": (4, 16), "Empire State Plaza": (-2, -18), "MVP Arena": (16, 8),
        "Washington Park": (2, 14), "Albany Medical Center": (-12, -6), "Stockade Historic District": (12, 14),
        "Fort Orange (site)": (18, -6), "Schuyler Mansion": (-14, -10), "Albany–Rensselaer station": (14, -14),
        "GE Vernova Schenectady works": (-4, -22),
    }
    # Towns to label: name -> (lon, lat), or None to use the town's own label point. The suburban towns
    # Census places miss. Whole-metro map, then the core detail (where the CDPs already name Niskayuna and Rotterdam).
    map1v2_towns = {"Clifton Park": (-73.80, 42.885), "Halfmoon": (-73.70, 42.875), "Malta": None, "Wilton": None,
                    "Glenville": None, "Bethlehem": (-73.90, 42.545), "Brunswick": (-73.55, 42.77)}
    map1v2_core_towns = {"Colonie": (-73.765, 42.772), "Guilderland": None, "Bethlehem": (-73.84, 42.615),
                         "Clifton Park": None, "Halfmoon": None, "East Greenbush": None, "North Greenbush": None}
    # Hand-placed highway labels: text -> (lon, lat).
    map1v2_routes = {"I-87": (-73.79, 43.18), "I-90": (-74.22, 42.79), "I-88": (-74.27, 42.74), "Thruway": (-73.93, 42.52)}
    map1v2_county_positions = {"Saratoga": (-73.93, 43.27), "Schenectady": (-74.08, 42.75), "Albany": (-74.08, 42.55)}
    return (map1v2_anchor_offsets, map1v2_colors, map1v2_core, map1v2_core_anchor_offsets, map1v2_core_place_offsets,
            map1v2_core_towns, map1v2_county_positions, map1v2_metro_core_anchors, map1v2_place_offsets, map1v2_places,
            map1v2_routes, map1v2_themes, map1v2_towns)


@app.cell
def _(layers, map1v2_anchor_offsets, map1v2_colors, map1v2_core, map1v2_county_positions, map1v2_metro_core_anchors,
      map1v2_place_offsets, map1v2_places, map1v2_routes, map1v2_themes, map1v2_towns, map_adirondack, map_anchors, map_lines,
      map_parks, map_places, map_towns):
    map1v2_fig, _ax = new_map(layers, footer_in=0.45)
    _core = core_box(map1v2_core)
    draw_county_flags(_ax, layers, map1v2_colors)
    draw_parks(_ax, map_parks, map_adirondack)
    draw_towns(_ax, map_towns, labels=map1v2_towns)
    draw_region_lines(_ax, layers, map_lines)
    # Places in or just outside the core box are labeled on the core detail instead.
    _unlabeled = set(map_places.loc[map_places.geometry.representative_point().within(_core.buffer(3_000)), "place_name"])
    draw_place_outlines(_ax, map_places, map1v2_places, map1v2_place_offsets, label_size=6.2, unlabeled=_unlabeled)
    draw_metro_outline(_ax, layers)
    draw_county_labels(_ax, layers, positions=map1v2_county_positions)
    draw_route_labels(_ax, map1v2_routes)
    # Landmarks inside the core box are left to the core detail, except its main places.
    _outside = map_anchors.loc[~map_anchors.within(_core)]
    assert set(map1v2_metro_core_anchors) <= set(map_anchors["name"]), set(map1v2_metro_core_anchors) - set(map_anchors["name"])
    _shown = pd.concat([_outside, map_anchors.loc[map_anchors["name"].isin(map1v2_metro_core_anchors)]])
    draw_anchors(_ax, _shown, map1v2_themes, labels=set(_shown["name"]),
                 offsets={**map1v2_anchor_offsets, **{k: v[1] for k, v in map1v2_metro_core_anchors.items()}}, size=26,
                 display={k: v[0] for k, v in map1v2_metro_core_anchors.items()})
    gpd.GeoSeries([_core], crs=MAP_CRS).boundary.plot(ax=_ax, color=color("neutral.text"), linewidth=0.8, linestyle=(0, (3, 2)), zorder=11)
    _ax.annotate(f"Core detail: {len(map_anchors) - len(_outside)} key places", (_core.bounds[0], _core.bounds[1]),
                 xytext=(3, -3), textcoords="offset points", ha="left", va="top",
                 fontsize=6.2, fontweight="bold", color=color("neutral.text"), path_effects=halo(), zorder=12)
    region_legend(_ax, map1v2_colors, map1v2_themes)
    add_text(
        map1v2_fig,
        title="Five counties, four old cities, and the Capital in the middle",
        subtitle="Albany-Schenectady-Troy metro area: OMB central and outlying counties, cities and key places, 2023 delineation",
        source="Source: OMB 2023 delineation; Census places (2020) and county subdivisions (2023); OpenStreetMap (highways, rail, rivers, parks);\n"
               "NYS Canal Corporation; Adirondack Park Agency (park boundary); key places from Wikipedia and Overture (reference/anchor_sources.json).",
    )
    save(map1v2_fig, "e1_metro_map")
    map1v2_fig
    return


@app.cell
def _(layers, map1v2_colors, map1v2_core, map1v2_core_anchor_offsets, map1v2_core_place_offsets, map1v2_core_towns,
      map1v2_places, map1v2_themes, map_adirondack, map_anchors, map_core_areas, map_lines, map_places, map_towns):
    _core = core_box(map1v2_core)
    _inside = map_anchors.loc[map_anchors.within(_core)].copy()
    map1v2_core_fig, _ax, _key_ax = new_detail_map(_core, key_rows=key_row_count(_inside, map1v2_themes))
    layers["context"].plot(ax=_ax, color=color("neutral.grid_minor"), edgecolor="white", linewidth=0.6)
    draw_county_flags(_ax, layers, map1v2_colors)
    # The detail draws every park of 10+ acres, campuses, hospitals and the airport from OSM (CORE_AREA_STYLES).
    draw_core_areas(_ax, map_core_areas)
    draw_towns(_ax, map_towns, labels=map1v2_core_towns, size=6.6)
    draw_region_lines(_ax, layers, map_lines, scale=1.4)
    draw_place_outlines(_ax, map_places, map1v2_places, map1v2_core_place_offsets, label_size=7)
    draw_metro_outline(_ax, layers)
    _numbered = draw_numbered_anchors(_ax, _inside, map1v2_themes, offsets=map1v2_core_anchor_offsets)
    _ax.legend(handles=[Patch(facecolor=f, edgecolor=e, label=lab) for f, e, lab in CORE_AREA_STYLES.values()], loc="lower left",
               frameon=True, facecolor="white", edgecolor="none", framealpha=0.85, fontsize=6.4)
    draw_anchor_key(_key_ax, _numbered, map1v2_themes)
    add_text(
        map1v2_core_fig,
        title="The core: three old cities a few miles apart",
        subtitle="Key places in the Albany–Troy–Schenectady triangle, numbered by theme (see key)",
        source="Source: Census places (2020) and county subdivisions (2023); OpenStreetMap (highways, rail, rivers; parks of 10+ acres, campuses,\n"
               "hospitals and the airport, 2026-10-27); NYS Canal Corporation; key places from Wikipedia and Overture (reference/anchor_sources.json).",
    )
    save(map1v2_core_fig, "e1c_core_map")
    map1v2_core_fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    **Numbers for the text: what each county is.** No exhibit. Albany, Rensselaer and Schenectady are
    **central**; Saratoga and Schoharie are **outlying** (OMB 2023). Growth compares the ACS 2008–12 and
    2020–24 5-year estimates, which don't overlap. The belonging numbers rerun OMB's outlying-county rule
    on 2023 LODES jobs (OMB used ACS 2016–20 workers), so say "on our rerun", not that a county is
    misdelineated: **at least 25% of a county's resident jobs in the central counties, or at least 25% of
    the jobs in the county held by central-county residents.**
    """)
    return


@app.cell
def _(con, layers):
    county_table = metro_county_table(layers["counties"])
    _by_county = county_table.set_index("county")
    county_flows = run_sql(con, SQL_DIR / "county_commute_flows.sql", cbsa_code=CBSA_CODE)
    county_belonging = integration_test(county_flows, layers["counties"], 0.25)
    _b = county_belonging.set_index("county")
    county_checks = pd.DataFrame([
        ("5 counties, 3 central and 2 outlying", county_table["flag"].value_counts().to_dict(),
         county_table["flag"].value_counts().to_dict() == {"Central": 3, "Outlying": 2}),
        ("Saratoga is outlying and grew fastest", f"{_by_county.loc['Saratoga', 'growth']:+.1%}",
         _by_county.loc["Saratoga", "flag"] == "Outlying" and _by_county["growth"].idxmax() == "Saratoga"),
        ("Saratoga: 39% of resident jobs at home, 35% in the core",
         f"{_b.loc['Saratoga', 'work_in_own_county']:.0%} / {_b.loc['Saratoga', 'out_to_central']:.0%}",
         round(_b.loc["Saratoga", "work_in_own_county"], 2) == 0.39 and round(_b.loc["Saratoga", "out_to_central"], 2) == 0.35),
        ("Schoharie: 16% to the core, under the 25% rule", f"{_b.loc['Schoharie', 'out_to_central']:.0%}",
         round(_b.loc["Schoharie", "out_to_central"], 2) == 0.16 and not _b.loc["Schoharie", "meets_threshold"]),
    ], columns=["check", "value", "passed"])
    assert county_checks["passed"].all(), county_checks
    mo.vstack([county_checks, county_table, county_belonging.drop(columns="county_geoid")])
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 4. What Kind of Place Is This? (E2, E3, E4)

    The second-city case against Buffalo (E2), migration in and out by where people came from or went (E3:
    Dan asked for it back on 2026-10-27, as gross flows rather than nets), and the ten metros most like it
    (E4). Explored in Q4h, Q4i and Q4g. **Migration now uses the IRS county totals** (see the migration cell).
    """)
    return


@app.cell
def _():
    # The big Upstate metros, in print order.
    rivals = {"15380": "Buffalo", "40380": "Rochester", "45060": "Syracuse"}
    return (rivals,)


@app.cell
def _(con, rivals):
    _trends = run_sql(con, LENS_SQL_DIR / "q4_trends.sql", cbsa_codes=sql_list([CBSA_CODE, *rivals]))
    gdp = _trends.loc[_trends["metric_id"] == "real_gdp_total"].pivot(index="year", columns="geo_id", values="value")
    _gap = gdp["15380"] - gdp[CBSA_CODE]
    _growth = gdp.iloc[-1] / gdp.loc[2012] - 1
    gdp_checks = pd.DataFrame([
        ("Years 2012–2024", f"{gdp.index.min()}–{gdp.index.max()}", gdp.index.min() == 2012 and gdp.index.max() == 2024),
        ("Buffalo's lead, 2012: $8.2B", f"{_gap[2012] / 1e9:.1f}B", round(_gap[2012] / 1e9, 1) == 8.2),
        ("Buffalo's lead, 2024: $1.6B", f"{_gap[2024] / 1e9:.1f}B", round(_gap[2024] / 1e9, 1) == 1.6),
        ("Real GDP growth since 2012: Albany +34%, Buffalo +19%", f"{_growth[CBSA_CODE]:+.0%} / {_growth['15380']:+.0%}",
         round(_growth[CBSA_CODE], 2) == 0.34 and round(_growth["15380"], 2) == 0.19),
    ], columns=["check", "value", "passed"])
    assert gdp_checks["passed"].all(), gdp_checks
    mo.vstack([gdp_checks, (gdp / 1e9).round(2)])
    return (gdp,)


@app.cell
def _(gdp):
    gdp_fig = draw_gdp_gap(gdp, {CBSA_CODE: "Albany", "15380": "Buffalo"})
    add_text(
        gdp_fig,
        title="Albany is closing in on Buffalo",
        subtitle=r"Real GDP, billions of chained 2017 dollars. Buffalo's lead shrank from \$8.2 billion in 2012 to \$1.6 billion in 2024",
        source="Source: BEA, GDP by county and metropolitan area (real GDP, chained 2017 dollars); OMB 2023 delineation.",
    )
    save(gdp_fig, "e2_albany_buffalo_gdp")
    gdp_fig
    return


@app.cell
def _(con, nutshell_raw, rivals):
    # Migration (Q4i), rebuilt 2026-10-27 on the IRS county totals. The county *pairs* in silver.irs_migration_flows leave
    # out every pair under 20 returns, which is most moves to and from other states: on pairs, Albany showed a net gain
    # of about 1,500 people a year; on the totals it loses about 1,500. Pairs are still used to split New York into
    # Downstate and Upstate (the big Downstate flows are all published); suppressed in-state flows fall into Upstate.
    assert not irs_flows_reversed(con), "IRS migration flows look reversed again: see foundations/etl/gold/check_irs_migration_direction.sql"
    _totals = pd.read_csv(IRS_TOTALS_CSV, dtype={"county_geoid": str})
    _members = con.sql("SELECT cbsa_code, county_geoid FROM silver.xwalk_cbsa_county").df()
    _pop = nutshell_raw.loc[(nutshell_raw["metric_id"] == "pop_total") & (nutshell_raw["geo_level"] == "cbsa")].set_index("geo_id")["value"]
    migration_rates = metro_net_uncapped(_totals, _members, _pop, years=5)
    _flows = run_sql(con, LENS_SQL_DIR / "q4_metro_migration.sql", cbsa_codes=sql_list([CBSA_CODE]), year_from="2018", year_to="2022")
    _xwalk = con.sql(
        "SELECT d.geo_id AS county_geoid, d.geo_name AS other_county_name, x.cbsa_code AS other_cbsa, "
        "coalesce(x.cbsa_name, 'Not in a metro') AS other_cbsa_name "
        "FROM gold.dim_geo AS d LEFT JOIN silver.xwalk_cbsa_county AS x ON x.county_geoid = d.geo_id WHERE d.geo_level = 'county'"
    ).df()
    _upstate_counties, _upstate_metros, _ = upstate_sets(con, nutshell_raw)
    _within = con.sql(
        "SELECT sum(f.n_exemptions) FROM silver.irs_migration_flows AS f "
        "JOIN silver.xwalk_cbsa_county AS a ON a.county_geoid = f.origin_geo_id "
        "JOIN silver.xwalk_cbsa_county AS b ON b.county_geoid = f.dest_geo_id AND b.cbsa_code = a.cbsa_code "
        f"WHERE f.geo_level = 'county' AND f.year BETWEEN 2018 AND 2022 AND f.origin_geo_id <> f.dest_geo_id AND a.cbsa_code = '{CBSA_CODE}'"
    ).fetchone()[0]
    migration = flows_by_region(_totals, classify_migration(_flows, _xwalk, _upstate_counties),
                                _members.loc[_members["cbsa_code"] == CBSA_CODE, "county_geoid"], _within, years=5)
    _m = migration.set_index("region")
    _r = migration_rates["net_rate"]
    _upstate_rank = _r.reindex(list(_upstate_metros)).rank(ascending=False)[CBSA_CODE]
    migration_checks = pd.DataFrame([
        ("Albany: 23,000 in, 24,500 out, net −1,500 a year", f"{_m.loc['All moves', 'in']:,.0f} / {_m.loc['All moves', 'out']:,.0f} / {_m.loc['All moves', 'net']:+,.0f}",
         round(_m.loc["All moves", "net"], -2) == -1500 and round(_m.loc["All moves", "in"], -2) == 23_000),
        ("Net: Downstate +2,500, rest of Upstate +1,100, other states −5,100",
         " / ".join(f"{_m.loc[k, 'net']:+,.0f}" for k in ["Downstate NY", "Rest of Upstate NY", "Other states"]),
         [round(_m.loc[k, "net"], -2) for k in ["Downstate NY", "Rest of Upstate NY", "Other states"]] == [2500, 1100, -5100]),
        ("Regions add up to the IRS totals", f"{migration.loc[migration['region'] != 'All moves', 'net'].sum():+,.0f}",
         abs(migration.loc[migration["region"] != "All moves", "net"].sum() - _m.loc["All moves", "net"]) < 1),
        ("Albany −1.6 per 1,000 a year; Buffalo, Rochester, Syracuse lose more", f"{1000 * _r[CBSA_CODE]:+.1f} vs "
         + ", ".join(f"{1000 * _r[c]:+.1f}" for c in rivals), round(1000 * _r[CBSA_CODE], 1) == -1.6 and all(_r[c] < _r[CBSA_CODE] for c in rivals)),
        ("Albany 4th of 12 Upstate metros", int(_upstate_rank), _upstate_rank == 4),
    ], columns=["check", "value", "passed"])
    assert migration_checks["passed"].all(), migration_checks
    mo.vstack([migration_checks, migration, migration_rates.loc[[CBSA_CODE, *rivals]]])
    return migration, migration_rates


@app.cell
def _(migration):
    migration_fig = draw_migration_flows(migration)
    add_text(
        migration_fig,
        title="Albany gains from the rest of New York and loses to other states",
        subtitle="People moving into and out of the Albany metro each year, by where they came from or went (2018–2022 average)",
        source="Source: IRS SOI county migration, 2018–2022 (exemptions, about people; moves abroad not included). In and out use the IRS county\n"
               "totals, which include the small county pairs IRS suppresses; Downstate (NYC, Long Island, Westchester, Putnam, Rockland) uses\n"
               "the published pairs, and the rest of New York is the remainder. Moves between the metro's own five counties are left out.",
    )
    save(migration_fig, "e3_migration_flows")
    migration_fig
    return


@app.cell
def _():
    # Metric -> (column header, format kind). The traits the peers share and the two where Albany breaks from them (Q4g).
    peer_table_metrics = {
        "pop_total": ("Population", "count"),
        "pop_weighted_density_sqmi": ("Density¹", "int"),
        "pct_struct_multifam": ("Multifamily\nhomes", "pct0"),
        "median_age": ("Median\nage", "years"),
        "calc_income_pc": ("Income per\nperson", "usd"),
        "pct_foreign_born": ("Foreign-\nborn", "pct0"),
        "public_job_share": ("Public-\nsector jobs", "pct0"),
        "irs_net_rate_uncapped": ("Net\nmigration²", "per1k"),
    }
    return (peer_table_metrics,)


@app.cell
def _(con, migration_rates, nutshell_raw, peer_table_metrics):
    _peer_list = run_sql(con, ANALYSES_DIR / "position" / "peers" / "queries" / "peer_list.sql", cbsa_code=CBSA_CODE)
    peers = _peer_list.loc[_peer_list["peer_type"] == "cross_frame", ["peer_rank", "peer_cbsa_code", "peer_cbsa_name", "similarity"]]
    # Net migration from the IRS county totals (the migration cell above), not the pair-based irs_net_migration_rate.
    _mig_long = pd.DataFrame({"geo_level": "cbsa", "geo_id": migration_rates.index, "metric_id": "irs_net_rate_uncapped",
                              "value": migration_rates["net_rate"].to_numpy()})
    _raw = pd.concat([nutshell_raw, run_sql(con, LENS_SQL_DIR / "q4_peer_extra_metrics.sql"), _mig_long], ignore_index=True)
    peer_table = peer_rows(_raw, peers, peer_table_metrics)
    _t = peer_table.set_index("metro")
    _mig = _t.loc[[n for n in _t.index if _t.loc[n, "kind"] == "peer"], "irs_net_rate_uncapped"]
    peer_checks = pd.DataFrame([
        ("10 peers, Buffalo first", f"{len(peers)}, {short_metro(peers.iloc[0]['peer_cbsa_name'])}",
         len(peers) == 10 and peers.iloc[0]["peer_cbsa_code"] == "15380"),
        ("Albany loses −1.6 per 1,000; 8 of 10 peers lose people too", f"{(_mig < 0).sum()} of 10 negative",
         round(1000 * _t.loc["Albany, NY", "irs_net_rate_uncapped"], 1) == -1.6 and (_mig < 0).sum() == 8),
        ("Public-sector share 23.7%", f"{_t.loc['Albany, NY', 'public_job_share']:.1%}", round(_t.loc["Albany, NY", "public_job_share"], 3) == 0.237),
    ], columns=["check", "value", "passed"])
    assert peer_checks["passed"].all(), peer_checks
    mo.vstack([peer_checks, peer_table])
    return (peer_table,)


@app.cell
def _(peer_table, peer_table_metrics):
    peer_fig = draw_peer_stats(peer_table, peer_table_metrics)
    add_text(
        peer_fig,
        title="Albany's closest matches are older Northeast metros",
        subtitle="The 10 US metros most like Albany across 35 measures of character, livability and opportunity",
        source="Similarity: cosine similarity of the standardized profiles (1 = the same shape). ¹ Population-weighted residents per square mile.\n"
               "² Net domestic migration, people per 1,000 residents a year (IRS county totals, 2018–22, including suppressed flows). Source: Patterns\n"
               "in Place Intelligence Framework (cross-frame peers); ACS 2020–24; BEA 2023 (income per person); LODES 2023 (public-sector jobs).",
    )
    save(peer_fig, "e4_peer_table")
    peer_fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 5. How It's Assembled (E5–E10)

    Where people live (E5–E7), where people work (E8), and the summary zones with what's there (E9, E10).
    Explored in Q2 and Q3.

    ### Where people live

    #### E5. Top places: the largest cities and towns

    NY's municipalities are cities, towns and villages. **Towns are incorporated** and cover all the
    land outside cities; the suburbs people name (Latham, Loudonville, Delmar) are **unincorporated
    hamlets** inside them (Census CDPs), and villages (Scotia, Ballston Spa) are incorporated places
    inside towns. Each town's bar lists its largest hamlets and villages.
    """)
    return


@app.cell
def _():
    # Rows shown, and how many hamlets or villages to name beside each town.
    top_places_n = 15
    top_places_hamlets = 3
    return top_places_hamlets, top_places_n


@app.cell
def _(map_places, map_towns, top_places_hamlets):
    top_places = municipality_table(map_towns, map_places, top_places_hamlets)
    _t = top_places.set_index("town")
    _cities = top_places.loc[top_places["kind"] == "city", "population"].sum() / top_places["population"].sum()
    _four = _t.loc[["Albany", "Schenectady", "Troy", "Saratoga Springs"], "population"].sum() / top_places["population"].sum()
    top_places_checks = pd.DataFrame([
        ("Colonie is the 2nd-largest municipality", top_places.index[top_places["town"] == "Colonie"][0] + 1,
         top_places.iloc[1]["town"] == "Colonie"),
        ("Colonie larger than Schenectady and Troy", f"{_t.loc['Colonie', 'population']:,}",
         _t.loc["Colonie", "population"] > max(_t.loc["Schenectady", "population"], _t.loc["Troy", "population"])),
        ("Clifton Park, Guilderland, Bethlehem each larger than Saratoga Springs", f"{_t.loc['Saratoga Springs', 'population']:,}",
         all(_t.loc[t, "population"] > _t.loc["Saratoga Springs", "population"] for t in ["Clifton Park", "Guilderland", "Bethlehem"])),
        ("share of residents in the 8 cities", f"{_cities:.0%}", True),
        ("share in the four cities", f"{_four:.0%}", True),
    ], columns=["check", "value", "passed"])
    assert top_places_checks["passed"].all(), top_places_checks
    mo.vstack([top_places_checks, top_places.drop(columns="geometry", errors="ignore")])
    return (top_places,)


@app.cell
def _(top_places, top_places_n):
    _four = top_places.loc[top_places["town"].isin(["Albany", "Schenectady", "Troy", "Saratoga Springs"]), "population"].sum()
    top_places_fig = draw_top_places(top_places.head(top_places_n))
    add_text(
        top_places_fig,
        title="The second-largest municipality is a suburban town",
        subtitle=f"Largest cities and towns in the Albany metro by population. The four cities hold "
                 f"{_four / top_places['population'].sum():.0%} of residents; "
                 f"{top_places.loc[top_places['kind'] == 'town', 'population'].sum() / top_places['population'].sum():.0%} live in towns.",
        source="Source: ACS 2020–24 5-year (county subdivisions); Census places (2020) for hamlets (CDPs) and villages, assigned to the town\n"
               "that contains them. Towns are incorporated municipalities in New York; hamlets are not.",
    )
    save(top_places_fig, "e5_top_places")
    top_places_fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    #### E6, E7. Population density and the arrow

    Residents per square mile of land, by census tract (ACS 2020–24). **The triangle** (`TRIANGLE_TOWNS`) is
    the three old cities, the small cities and towns between them, and southern Saratoga County up to the
    Northway (Clifton Park, Halfmoon, Waterford); Dan moved it north on 2026-10-27, dropping Bethlehem and
    Guilderland and adding Rensselaer. The **Northway arm** (`NORTHWAY_ARM`: Malta and Saratoga Springs)
    carries it up I-87, so the two draw as one arrow; the dashed line joins the three downtowns for
    reference. Shares use the towns' ACS population and land area, so they match E5.
    """)
    return


@app.cell
def _(con, map_towns):
    tracts = load_tract_profile(con).merge(run_sql(con, LENS_SQL_DIR / "tract_activity_base.sql", cbsa_code=CBSA_CODE), on="tract_geoid")
    tracts["density"] = tracts["residents"] / tracts["land_area_sqmi"]
    assert set(TRIANGLE_TOWNS + NORTHWAY_ARM) <= set(map_towns["town"]), set(TRIANGLE_TOWNS + NORTHWAY_ARM) - set(map_towns["town"])
    town_groups = map_towns.assign(group=lambda d: np.select(
        [d["town"].isin(TRIANGLE_TOWNS), d["town"].isin(NORTHWAY_ARM)], ["The triangle", "Northway arm"], "Rest of the metro"))
    area_shares = (town_groups.groupby("group")[["population", "land_sqmi"]].sum()
                   .reindex(["The triangle", "Northway arm", "Rest of the metro"]))
    area_shares = area_shares.assign(resident_share=lambda d: d["population"] / d["population"].sum(),
                                     land_share=lambda d: d["land_sqmi"] / d["land_sqmi"].sum())
    _tri = area_shares.loc["The triangle"]
    _arrow = area_shares.loc[["The triangle", "Northway arm"]].sum()
    density_checks = pd.DataFrame([
        ("251 tracts with residents and land area", len(tracts), len(tracts) == 251 and tracts["land_area_sqmi"].gt(0).all()),
        ("Tract residents sum to the metro", f"{tracts['residents'].sum():,.0f}", round(tracts["residents"].sum()) == 906_052),
        ("Town residents sum to the metro", f"{area_shares['population'].sum():,.0f}", area_shares["population"].sum() == 906_052),
        ("The triangle: 49% of residents on 7% of land", f"{_tri['resident_share']:.0%} / {_tri['land_share']:.0%}",
         round(_tri["resident_share"], 2) == 0.49 and round(_tri["land_share"], 2) == 0.07),
        ("The arrow (triangle + Northway arm): 54% of residents on 9% of land", f"{_arrow['resident_share']:.0%} / {_arrow['land_share']:.0%}",
         round(_arrow["resident_share"], 2) == 0.54 and round(_arrow["land_share"], 2) == 0.09),
    ], columns=["check", "value", "passed"])
    assert density_checks["passed"].all(), density_checks
    mo.vstack([density_checks, area_shares.round(3)])
    return area_shares, town_groups, tracts


@app.cell
def _():
    # Density classes (residents per square mile of land) -> fill, light to dark.
    density_classes = {
        "Under 250": (0, 250, "#F1F4F7"),
        "250–1,000": (250, 1_000, "#D3E0EA"),
        "1,000–2,500": (1_000, 2_500, "#A9C4DA"),
        "2,500–5,000": (2_500, 5_000, "#779FC2"),
        "5,000–10,000": (5_000, 10_000, "#4677A3"),
        "10,000 and up": (10_000, np.inf, "#1F4E79"),
    }
    # Town labels on the density map: name -> (lon, lat), or None for the town's own label point.
    density_towns = {"Colonie": (-73.80, 42.745), "Guilderland": None, "Bethlehem": (-73.86, 42.58), "Clifton Park": (-73.80, 42.865),
                     "Halfmoon": (-73.735, 42.85), "Malta": None, "Milton": None, "Wilton": None, "Niskayuna": (-73.87, 42.80)}
    density_city_offsets = {"Albany": (-18, -10), "Schenectady": (-30, 6), "Troy": (16, 4), "Saratoga Springs": (-40, 2)}
    return density_city_offsets, density_classes, density_towns


@app.cell
def _(area_shares, density_city_offsets, density_classes, density_towns, layers, map_lines, map_places, town_groups, tracts):
    _arrow = area_shares.loc[["The triangle", "Northway arm"]].sum()
    density_fig, _ax = new_map(layers, footer_in=0.4)
    draw_tract_classes(_ax, tracts.assign(cls=classify(tracts["density"], density_classes)), "cls",
                       {k: v[2] for k, v in density_classes.items()})
    draw_towns(_ax, town_groups, labels=density_towns)
    layers["rivers"].plot(ax=_ax, color=RIVER_COLOR, linewidth=0.9, zorder=3)
    map_lines["interstate"].plot(ax=_ax, color="#52606D", linewidth=0.9, zorder=4)
    map_lines["thruway"].plot(ax=_ax, color="#52606D", linewidth=1.3, zorder=4)
    draw_triangle(_ax, town_groups, map_places)
    draw_place_outlines(_ax, map_places, [], density_city_offsets, label_size=6.4, fill=False)
    draw_metro_outline(_ax, layers)
    _legend = [Patch(facecolor=v[2], edgecolor="#C9D2DC", label=k) for k, v in density_classes.items()]
    _legend += [plt.Line2D([], [], color=color("highlight.risk"), linewidth=1.8,
                           label=f"The triangle and its Northway arm: {_arrow['resident_share']:.0%} of residents"),
                plt.Line2D([], [], color=color("highlight.risk"), linewidth=0.9, linestyle=(0, (3, 2)), label="Line joining the three downtowns"),
                plt.Line2D([], [], color="#52606D", linewidth=1.1, label="Interstates (I-87 north is the Northway)"),
                Patch(facecolor="none", edgecolor=color("neutral.text"), label="The four cities")]
    _ax.legend(handles=_legend, loc="upper left", frameon=True, facecolor="white", edgecolor="none", framealpha=0.85,
               fontsize=6.4, title="Residents per sq mi", title_fontsize=6.8, alignment="left")
    add_text(
        density_fig,
        title=f"{_arrow['resident_share']:.0%} of the metro lives in the triangle and up the Northway",
        subtitle="Residents per square mile by census tract. The triangle between the three old cities points up I-87 to Saratoga Springs",
        source="Source: ACS 2020–24 5-year (tract and town population); Census tracts and county subdivisions; OpenStreetMap (highways, rivers).\n"
               "The triangle: Albany, Troy, Schenectady, Rensselaer, Watervliet, Cohoes, Green Island, Colonie, Niskayuna, Waterford, Halfmoon,\n"
               "Clifton Park. The Northway arm: Malta, Saratoga Springs.",
    )
    save(density_fig, "e6_population_density")
    density_fig
    return


@app.cell
def _(area_shares, density_city_offsets, density_classes, density_towns, layers, map_lines, map_places, town_groups, tracts):
    # E6b: the same density map with a hand-drawn arrow instead of the town outline (Dan, 2026-10-30). A reference shape,
    # not tract-exact; the shares quoted are still the E6 town shares.
    _arrow = area_shares.loc[["The triangle", "Northway arm"]].sum()
    arrow_fig, _ax = new_map(layers, footer_in=0.4)
    draw_tract_classes(_ax, tracts.assign(cls=classify(tracts["density"], density_classes)), "cls",
                       {k: v[2] for k, v in density_classes.items()})
    draw_towns(_ax, town_groups, labels=density_towns)
    layers["rivers"].plot(ax=_ax, color=RIVER_COLOR, linewidth=0.9, zorder=3)
    map_lines["interstate"].plot(ax=_ax, color="#52606D", linewidth=0.9, zorder=4)
    map_lines["thruway"].plot(ax=_ax, color="#52606D", linewidth=1.3, zorder=4)
    draw_arrow_schematic(_ax, map_places)
    draw_place_outlines(_ax, map_places, [], density_city_offsets, label_size=6.4, fill=False)
    draw_metro_outline(_ax, layers)
    _legend = [Patch(facecolor=v[2], edgecolor="#C9D2DC", label=k) for k, v in density_classes.items()]
    _legend += [Patch(facecolor=color("highlight.risk"), alpha=0.25, edgecolor=color("highlight.risk"),
                      label=f"The arrow (schematic): {_arrow['resident_share']:.0%} of residents"),
                plt.Line2D([], [], color="#52606D", linewidth=1.1, label="Interstates (I-87 north is the Northway)"),
                Patch(facecolor="none", edgecolor=color("neutral.text"), label="The four cities")]
    _ax.legend(handles=_legend, loc="upper left", frameon=True, facecolor="white", edgecolor="none", framealpha=0.85,
               fontsize=6.4, title="Residents per sq mi", title_fontsize=6.8, alignment="left")
    add_text(
        arrow_fig,
        title=f"{_arrow['resident_share']:.0%} of the metro lives in the arrow",
        subtitle="Residents per square mile by census tract. The three old cities form the head; the shaft runs up I-87 to Saratoga",
        source="Source: ACS 2020–24 5-year (tract and town population); Census tracts and county subdivisions; OpenStreetMap (highways, rivers).\n"
               "The arrow is drawn by hand for reference. Its share uses the towns in E6: the triangle's twelve towns and cities plus Malta\n"
               "and Saratoga Springs.",
    )
    save(arrow_fig, "e6b_population_arrow")
    arrow_fig
    return


@app.cell
def _(area_shares):
    triangle_fig = draw_share_bars(area_shares, {"The triangle": color("highlight.risk"), "Northway arm": "#E8A87C",
                                                 "Rest of the metro": "#C9D2DC"})
    _arrow = area_shares.loc[["The triangle", "Northway arm"]].sum()
    add_text(
        triangle_fig,
        title=f"{_arrow['resident_share']:.0%} of residents on {_arrow['land_share']:.0%} of the land",
        subtitle="Share of the metro's residents and land area: the triangle, its Northway arm to Saratoga Springs, and everywhere else",
        source="Source: ACS 2020–24 5-year (county subdivision population); Census county subdivisions, 2023 (land area). Areas as in E6.",
    )
    save(triangle_fig, "e7_triangle_share")
    triangle_fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Where people work

    #### E8. Job centers on all jobs

    Q2's center method, unchanged, run on **all jobs** (LODES JT00, 2023), so public jobs count. Every tract is
    a circle sized by its jobs; center tracts are colored by their public share. Hollow rings are tracts that
    are centers only on **private** jobs, the published Q2 run; on all jobs they fall under the 1% share floor
    as the metro total rises (Malta's GlobalFoundries among them). This replaces the old "center in both"
    comparison, which said nothing about public share. Framed on the triangle and the Northway; the
    outer towns hold few jobs.
    """)
    return


@app.cell
def _(con, tracts):
    _candidates, _components, _private, _checks = all_jobs_centers(con)
    assert _checks["passed"].all(), _checks
    job_tracts = tracts[["tract_geoid", "place", "geometry"]].merge(
        _candidates[["tract_geoid", "jobs_total", "private_jobs", "is_recommended_center", "recommended_cluster_id"]], on="tract_geoid", how="left"
    ).merge(_private, on="tract_geoid", how="left")
    job_tracts["public_share"] = 1 - job_tracts["private_jobs"] / job_tracts["jobs_total"]
    job_tracts["is_recommended_center"] = job_tracts["is_recommended_center"].fillna(False).astype(bool)
    job_tracts["private_only"] = job_tracts["private_center"].fillna(False).astype(bool) & ~job_tracts["is_recommended_center"]
    _centers = job_tracts.loc[job_tracts["is_recommended_center"]]
    job_components = (_centers.sort_values("jobs_total", ascending=False).groupby("recommended_cluster_id")
                      .agg(tracts=("tract_geoid", "size"), jobs=("jobs_total", "sum"), private_jobs=("private_jobs", "sum"),
                           top_tract=("tract_geoid", "first"))
                      .assign(public_share=lambda d: 1 - d["private_jobs"] / d["jobs"]).sort_values("jobs", ascending=False))
    _c = job_components.set_index("top_tract")
    job_checks = pd.DataFrame([
        ("11 centers on all jobs", len(job_components), len(job_components) == 11),
        ("Largest: the 13-tract uptown band, 96k jobs", f"{_c.loc['36001013703', 'tracts']} tracts, {_c.loc['36001013703', 'jobs']:,.0f}",
         _c.loc["36001013703", "tracts"] == 13 and round(_c.loc["36001013703", "jobs"], -3) == 96_000),
        ("Downtown Albany: 50k jobs, 71% public", f"{_c.loc['36001001100', 'jobs']:,.0f}, {_c.loc['36001001100', 'public_share']:.0%}",
         round(_c.loc["36001001100", "jobs"], -3) == 50_000 and round(_c.loc["36001001100", "public_share"], 2) == 0.71),
        ("Malta (GlobalFoundries) is a center on private jobs only", "36091061907", bool(job_tracts.set_index("tract_geoid").loc["36091061907", "private_only"])),
        ("Centers' share of metro jobs", f"{_centers['jobs_total'].sum() / job_tracts['jobs_total'].sum():.0%}", True),
    ], columns=["check", "value", "passed"])
    assert job_checks["passed"].all(), job_checks
    mo.vstack([job_checks, job_components])
    return job_components, job_tracts


@app.cell
def _():
    # Each center's printed name, keyed by its largest tract (names from the POIs and key places in each tract).
    job_center_names = {
        "36001013703": "Uptown Albany to Wolf Road",
        "36001001100": "Downtown Albany",
        "36001002100": "Albany Med",
        "36091061202": "Saratoga Springs",
        "36093021001": "Downtown Schenectady",
        "36083052406": "East Greenbush",
        "36091060704": "Wilton",
        "36091062508": "Clifton Park",
        "36083040701": "Downtown Troy",
        "36093032101": "Niskayuna",
        "36001002600": "Port of Albany",
    }
    # Printed name -> label offset in points from the center's jobs-weighted point.
    job_center_offsets = {
        "Uptown Albany to Wolf Road": (-46, 22), "Downtown Albany": (34, -16), "Albany Med": (-40, -18),
        "Port of Albany": (22, -30), "Downtown Troy": (30, 10), "East Greenbush": (34, -6), "Downtown Schenectady": (-30, 16),
        "Niskayuna": (-12, 30), "Clifton Park": (-34, 6), "Wilton": (30, 6), "Saratoga Springs": (-36, -10),
    }
    # The frame (lon, lat): the triangle and the Northway up to Wilton.
    job_center_box = (-74.04, 42.57, -73.58, 43.2)
    return job_center_box, job_center_names, job_center_offsets


@app.cell
def _(job_center_box, job_center_names, job_center_offsets, job_components, job_tracts, layers, map_lines, map_places, map_towns):
    assert set(job_components["top_tract"]) == set(job_center_names), set(job_components["top_tract"]) ^ set(job_center_names)
    jobs_fig, _ax = new_box_map(core_box(job_center_box), footer_in=0.45)
    layers["context"].plot(ax=_ax, color=color("neutral.grid_minor"), edgecolor="white", linewidth=0.6)
    draw_metro_counties(_ax, layers)
    map_towns.boundary.plot(ax=_ax, color="#E1E6EB", linewidth=0.5, zorder=2)
    layers["rivers"].plot(ax=_ax, color=RIVER_COLOR, linewidth=0.9, zorder=3)
    map_lines["interstate"].plot(ax=_ax, color="#B7C0C9", linewidth=0.8, zorder=3)
    map_lines["thruway"].plot(ax=_ax, color="#B7C0C9", linewidth=1.1, zorder=3)
    draw_place_outlines(_ax, map_places, [], {}, label_size=6.4, fill=False, labels=False)
    _labels = {row.recommended_cluster_id: job_center_names[row.top_tract] for row in job_components.reset_index().itertuples()}
    draw_job_center_map(_ax, job_tracts, _labels, job_center_offsets)
    draw_metro_outline(_ax, layers)
    add_text(
        jobs_fig,
        title="The largest job center is the band from uptown Albany to Wolf Road",
        subtitle=f"Jobs by census tract, 2023; colored: the {len(job_components)} job centers on all jobs, by public share of their jobs",
        source="Source: 2023 LEHD LODES WAC, all jobs (JT00) and private jobs (JT02); Q2 job-center method (recommended core, one hop),\n"
               "run on all jobs. Center names from the key places and points of interest in each center's tracts.",
    )
    save(jobs_fig, "e8_job_centers")
    jobs_fig
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ### Summary zones

    #### E9, E10. The zones, and what's there

    The national tract zones (Phase 7, promoted 2026-10-23: k-means on 22 tract metrics across every US metro
    and micro area), with Albany's **working names** (`ZONE_NAMES`). **Print gate:** the national type names
    are still draft, and the working names are Albany's; both need Dan's sign-off before print.

    **What's there** is a small add-on to the zone table (Dan, 2026-10-27, replacing the E11 table and E12
    map): each tract also gets one of four **activity classes** from its points of interest (Overture
    2026-10-21.0) and its jobs, by plain rules (`ACTIVITY_RULES`, spelled out in the exploration notebook,
    Q3e): more jobs than residents makes Destination or Employment and industrial; few POIs per resident
    makes Residential; a destination or industrial mix makes that class; the rest is Local-serving. E10's
    last column splits each zone's residents by class.
    """)
    return


@app.cell
def _(tracts):
    zone_tracts = tracts.assign(working_name=lambda d: d["zone_type"].map(lambda z: ZONE_NAMES[z][0]))
    zone_table = zone_summary(zone_tracts)
    _z = zone_table.set_index("working_name")
    zone_checks = pd.DataFrame([
        ("Six zone types in Albany", len(zone_table), len(zone_table) == 6),
        ("Comfortable suburbs: 143 tracts, 557k residents", f"{_z.loc['Comfortable suburbs', 'tracts']}, {_z.loc['Comfortable suburbs', 'residents']:,.0f}",
         _z.loc["Comfortable suburbs", "tracts"] == 143 and round(_z.loc["Comfortable suburbs", "residents"], -3) == 557_000),
        ("Rural and exurban: 39 tracts", _z.loc["Rural and exurban", "tracts"], _z.loc["Rural and exurban", "tracts"] == 39),
    ], columns=["check", "value", "passed"])
    assert zone_checks["passed"].all(), zone_checks
    mo.vstack([zone_checks, zone_table])
    return zone_table, zone_tracts


@app.cell
def _(density_city_offsets, layers, map_places, map_towns, zone_tracts):
    zone_map_fig, _ax = new_map(layers, footer_in=0.4)
    draw_tract_classes(_ax, zone_tracts, "working_name", ZONE_COLORS, counts=True, title="Zone (tracts)")
    map_towns.boundary.plot(ax=_ax, color="white", linewidth=0.35, zorder=3)
    draw_county_lines(_ax, layers)
    layers["rivers"].plot(ax=_ax, color=RIVER_COLOR, linewidth=0.8, zorder=4)
    draw_place_outlines(_ax, map_places, [], density_city_offsets, label_size=6.4, fill=False)
    draw_metro_outline(_ax, layers)
    add_text(
        zone_map_fig,
        title="Comfortable suburbs fill the middle; the cities hold the rest",
        subtitle="Neighborhood type by census tract (national zone types, Albany working names; not cleared for print)",
        source="Source: Patterns in Place Intelligence Framework, Phase 7 tract zones (k-means on 22 tract metrics, all US metro and micro\n"
               "tracts); ACS 2020–24; LODES 2023; Census tracts and places.",
    )
    save(zone_map_fig, "e9_zone_map")
    zone_map_fig
    return


@app.cell
def _(zone_activity, zone_table):
    zone_table_fig = draw_zone_table(zone_table, zone_activity)
    add_text(
        zone_table_fig,
        title="Six kinds of neighborhood",
        subtitle="Albany's zones: national type, size, median tract values (ACS 2020–24), and what's there",
        source="Source: Patterns in Place Intelligence Framework, Phase 7 tract zones; ACS 2020–24 5-year; Overture Maps places (2026-10-21.0);\n"
               "LODES 2023. Medians across each zone's tracts. ¹ Population-weighted residents per square mile. ² Each tract's activity class,\n"
               "from its points of interest and jobs: more jobs than residents, POIs per resident, and its POI mix against the metro.",
    )
    save(zone_table_fig, "e10_zone_table")
    zone_table_fig
    return


@app.cell
def _(con, zone_tracts):
    _counts = run_sql(con, LENS_SQL_DIR / "poi_tract_categories.sql", poi_run_dir=POI_RUN_DIR.as_posix())
    _base = zone_tracts[["tract_geoid", "land_area_sqmi", "residents", "jobs"]]
    activity_tracts = zone_tracts.drop(columns=["jobs_per_resident"]).merge(
        tract_activity(_counts, _base, **ACTIVITY_RULES).drop(columns=["land_area_sqmi", "residents", "jobs"]), on="tract_geoid")
    _n = activity_tracts["activity"].value_counts()
    _active = activity_tracts["activity"].isin(["Destination", "Employment and industrial"])
    activity_checks = pd.DataFrame([
        ("Residential 120, Local-serving 83, Employment 29, Destination 19", _n.to_dict(),
         _n.to_dict() == {"Residential": 120, "Local-serving": 83, "Employment and industrial": 29, "Destination": 19}),
        ("Active tracts: 17% of residents, 58% of jobs",
         f"{activity_tracts.loc[_active, 'residents'].sum() / activity_tracts['residents'].sum():.0%} / "
         f"{activity_tracts.loc[_active, 'jobs'].sum() / activity_tracts['jobs'].sum():.0%}",
         round(activity_tracts.loc[_active, "residents"].sum() / activity_tracts["residents"].sum(), 2) == 0.17
         and round(activity_tracts.loc[_active, "jobs"].sum() / activity_tracts["jobs"].sum(), 2) == 0.58),
    ], columns=["check", "value", "passed"])
    assert activity_checks["passed"].all(), activity_checks
    zone_activity = (activity_tracts.pivot_table(index="working_name", columns="activity", values="residents", aggfunc="sum", fill_value=0)
                     .reindex(columns=ACTIVITY_ORDER, fill_value=0))
    mo.vstack([activity_checks, zone_activity])
    return (zone_activity,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Helpers

    Drawing and prep functions for this notebook. The map frame, labels, titles and
    export follow `primer/series_intro/WHAT_NY_IS_VISUALS.py` so the series reads as one set,
    framed on the metro instead of the state.
    """)
    return


@app.function
def integration_test(flows: pd.DataFrame, counties: gpd.GeoDataFrame, threshold: float) -> pd.DataFrame:
    """OMB's outlying-county commuting rule, rerun on LODES jobs. One row per metro county.

    Out: share of the county's resident jobs located in the central counties.
    In: share of the jobs located in the county held by central-county residents.
    The test applies to outlying counties only; central rows are context.
    """
    rows = []
    for county in counties.itertuples():
        home = flows.loc[flows["home_county_geoid"] == county.county_geoid]
        work = flows.loc[flows["work_county_geoid"] == county.county_geoid]
        out_share = home.loc[home["work_flag"] == "Central", "jobs"].sum() / home["jobs"].sum()
        in_share = work.loc[work["home_flag"] == "Central", "jobs"].sum() / work["jobs"].sum()
        outlying = county.county_flag == "Outlying"
        rows.append({
            "county_geoid": county.county_geoid,
            "county": county_short_name(county.county_name),
            "flag": county.county_flag,
            "resident_jobs": home["jobs"].sum(),
            "work_in_own_county": home.loc[home["work_county_geoid"] == county.county_geoid, "jobs"].sum() / home["jobs"].sum(),
            "work_anywhere_in_metro": home.loc[home["work_flag"].notna(), "jobs"].sum() / home["jobs"].sum(),
            "out_to_central": out_share,
            "in_from_central": in_share,
            "meets_threshold": (max(out_share, in_share) >= threshold) if outlying else None,
        })
    return pd.DataFrame(rows).sort_values(["flag", "county"]).reset_index(drop=True)


@app.function
def municipality_table(towns: gpd.GeoDataFrame, places: gpd.GeoDataFrame, n_hamlets: int) -> pd.DataFrame:
    """Every city and town, largest first, with the largest hamlets (CDPs) and villages inside each town."""
    inside = gpd.sjoin(
        gpd.GeoDataFrame(places[["place_name", "place_kind", "population_in_metro"]], geometry=places.geometry.representative_point(), crs=MAP_CRS),
        towns[["town", "kind", "geometry"]], how="inner", predicate="within",
    )
    inside = inside.loc[(inside["kind"] == "town") & inside["place_kind"].isin(["CDP", "village"])]
    names = (inside.sort_values("population_in_metro", ascending=False).groupby("town")
             .apply(lambda g: ", ".join(f"{r.place_name}{'*' if r.place_kind == 'village' else ''}" for r in g.head(n_hamlets).itertuples()),
                    include_groups=False))
    out = towns.drop(columns="geometry").assign(inside=lambda d: d["town"].map(names).fillna(""))
    return out.sort_values("population", ascending=False).reset_index(drop=True)


@app.function
def draw_top_places(table: pd.DataFrame, *, row_in: float = 0.3):
    """Ranked bars: the four cities, other cities and towns in three fills; each town's hamlets named beside its bar."""
    four = {"Albany", "Schenectady", "Troy", "Saratoga Springs"}
    fills = {"The four cities": "#3E5C76", "Other city": "#9FB0C2", "Town": "#C9B48A"}
    n = len(table)
    width_in = EXPORT_WIDTH_PX / EXPORT_DPI
    top_in, legend_in, footer_in = 0.75, 0.32, 0.6
    height_in = top_in + legend_in + n * row_in + footer_in
    fig = plt.figure(figsize=(width_in, height_in), dpi=EXPORT_DPI)
    fig.patch.set_facecolor(color("neutral.background_white"))
    ax = fig.add_axes((0.2, footer_in / height_in, 0.36, n * row_in / height_in))
    group = ["The four cities" if t in four else "Other city" if k == "city" else "Town" for t, k in zip(table["town"], table["kind"])]
    ax.barh(range(n), table["population"], height=0.66, color=[fills[g] for g in group])
    vmax = table["population"].max()
    for r, row in enumerate(table.itertuples()):
        ax.annotate(format_count(row.population), (row.population, r), xytext=(3, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=7, color=color("neutral.text"))
        if row.inside:
            fig.text(0.6, (footer_in + (n - r - 0.5) * row_in) / height_in, row.inside, ha="left", va="center",
                     fontsize=6.6, fontstyle="italic", color=color("neutral.text_muted"))
    ax.set_xlim(0, vmax * 1.18)
    ax.set_ylim(n - 0.5, -0.5)
    ax.set_yticks(range(n))
    ax.set_yticklabels([f"{t} ({k})" if k == "town" else t for t, k in zip(table["town"], table["kind"])], fontsize=7.6)
    for tick, g in zip(ax.get_yticklabels(), group):
        tick.set_fontweight("bold" if g == "The four cities" else "normal")
    ax.set_xticks([])
    ax.tick_params(axis="y", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.text(0.6, (footer_in + n * row_in + 0.06) / height_in, "Largest hamlets and villages* inside the town",
             ha="left", va="bottom", fontsize=6.8, fontweight="bold", color=color("neutral.text_muted"))
    fig.legend(handles=[Patch(facecolor=f, label=k) for k, f in fills.items()], loc="upper left",
               bbox_to_anchor=(0.02, 1 - top_in / height_in), ncol=3, frameon=False, fontsize=7.5)
    return fig


@app.function
def nutshell_table(raw: pd.DataFrame, metrics: dict, upstate_metros: set, upstate: dict) -> pd.DataFrame:
    """Numbers behind the At a glance exhibits: Albany's value, percentile and ranks, and the references."""
    wide = metro_wide(raw)
    us = raw.loc[raw["geo_level"] == "us"].set_index("metric_id")["value"]
    rows = []
    for metric_id, (label, kind) in metrics.items():
        values = wide[metric_id].dropna()
        up = values.loc[values.index.isin(upstate_metros)]
        albany = values[CBSA_CODE]
        rows.append({
            "metric_id": metric_id, "label": label, "kind": kind, "value": albany,
            "percentile": 100 * (values < albany).mean(),
            "position": position_words(values, albany),
            "us_rank": int((values > albany).sum() + 1), "us_n": len(values),
            "upstate_rank": int((up > albany).sum() + 1), "upstate_n": len(up),
            "upstate": upstate[metric_id][0], "upstate_exact": upstate[metric_id][1], "us": us.get(metric_id, np.nan),
        })
    return pd.DataFrame(rows)


@app.function
def draw_nutshell_dots(table: pd.DataFrame, raw: pd.DataFrame, metrics: dict, upstate_metros: set):
    """Percentile dot plot: a row per metric, the other Upstate metros as grey dots, Albany in red with its value,
    the Upstate aggregate as a hollow diamond and the US as a tick (where published)."""
    wide = metro_wide(raw)
    n = len(table)
    width_in = EXPORT_WIDTH_PX / EXPORT_DPI
    top_in, legend_in, row_in, footer_in = 0.8, 0.42, 0.42, 0.75
    height_in = top_in + legend_in + n * row_in + footer_in
    fig = plt.figure(figsize=(width_in, height_in), dpi=EXPORT_DPI)
    fig.patch.set_facecolor(color("neutral.background_white"))
    left, right = 0.4, 0.96
    ax = fig.add_axes((left, footer_in / height_in, right - left, n * row_in / height_in))
    red, grey = color("highlight.risk"), "#9AA5B1"
    for i, row in enumerate(table.itertuples()):
        values = wide[row.metric_id].dropna()
        ax.plot([0, 100], [i, i], color=color("neutral.grid_major"), linewidth=0.8, zorder=1)
        others = [100 * (values < values[c]).mean() for c in upstate_metros - {CBSA_CODE} if c in values]
        ax.scatter(others, [i] * len(others), s=22, color=grey, alpha=0.7, linewidth=0, zorder=2)
        # Upstate and US totals aren't metros, so they have no place among metros on a count.
        is_count = row.kind in ("count", "usd_big")
        if pd.notna(row.us) and not is_count:
            ax.scatter([100 * (values < row.us).mean()], [i], marker="|", s=140, color=color("neutral.text"), linewidth=1.3, zorder=3)
        if pd.notna(row.upstate) and not is_count:
            ax.scatter([100 * (values < row.upstate).mean()], [i], marker="D", s=30, facecolor="white",
                       edgecolor=color("neutral.text"), linewidth=1.0, zorder=4)
        ax.scatter([row.percentile], [i], s=70, color=red, edgecolor="white", linewidth=0.8, zorder=5)
        y = (footer_in + (n - i - 0.5) * row_in) / height_in
        fig.text(0.02, y, row.label, ha="left", va="center", fontsize=8, color=color("neutral.text"))
        fig.text(left - 0.025, y, tex_safe(format_metric(row.kind, row.value)), ha="right", va="center", fontsize=8,
                 fontweight="bold", color=red)
    ax.set_xlim(-3, 103)
    ax.set_ylim(n - 0.5, -0.5)
    ax.set_yticks([])
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["Lowest", "25th", "Median", "75th", "Highest"], fontsize=7, color=color("neutral.text_muted"))
    ax.tick_params(axis="x", length=0)
    for x in (25, 50, 75):
        ax.axvline(x, color=color("neutral.grid_major"), linewidth=0.5, linestyle=":", zorder=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.text(left - 0.025, (footer_in + n * row_in + 0.08) / height_in, "Albany", ha="right", va="bottom", fontsize=7.5,
             fontweight="bold", color=red)
    handles = [
        plt.Line2D([], [], linestyle="", marker="o", markersize=7, color=red, label="Albany"),
        plt.Line2D([], [], linestyle="", marker="o", markersize=5, color=grey, label="Other Upstate metros"),
        plt.Line2D([], [], linestyle="", marker="D", markersize=5, markerfacecolor="white", markeredgecolor=color("neutral.text"),
                   label="Upstate as a whole"),
        plt.Line2D([], [], linestyle="", marker="|", markersize=9, color=color("neutral.text"), label="United States"),
    ]
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(left - 0.01, 1 - top_in / height_in), ncol=4,
               frameon=False, fontsize=7, handletextpad=0.3, columnspacing=1.2)
    return fig


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
def draw_triangle(ax, town_groups: gpd.GeoDataFrame, places: gpd.GeoDataFrame) -> None:
    """The arrow (the triangle's towns and the Northway arm) as one solid outline, and a dashed line joining the three
    downtowns (city label points)."""
    area = town_groups.loc[town_groups["group"].isin(["The triangle", "Northway arm"])].union_all()
    gpd.GeoSeries([area], crs=MAP_CRS).boundary.plot(ax=ax, color=color("highlight.risk"), linewidth=1.8, zorder=9)
    cities = places.loc[places["place_name"].isin(["Albany", "Troy", "Schenectady"]) & (places["place_kind"] == "city")]
    points = [cities.loc[cities["place_name"] == c].geometry.iloc[0].representative_point() for c in ["Albany", "Troy", "Schenectady"]]
    ring = shapely.LineString([*points, points[0]])
    gpd.GeoSeries([ring], crs=MAP_CRS).plot(ax=ax, color=color("highlight.risk"), linewidth=0.9, linestyle=(0, (3, 2)), zorder=9)


@app.function
def draw_arrow_schematic(ax, places: gpd.GeoDataFrame, *, head_pad: float = 1.35, shaft_frac: float = 0.22) -> None:
    """A hand-drawn arrow for E6b: the head is the Albany-Schenectady-Troy triangle (grown about its centroid so it
    covers the inner suburbs), pointing south at Albany; the shaft runs from the middle of the Schenectady-Troy side up
    to Saratoga Springs. Schematic only."""
    cities = places.loc[places["place_kind"] == "city"].set_index("place_name").geometry.representative_point()
    albany, schenectady, troy, saratoga = (np.array(cities[c].coords[0]) for c in ["Albany", "Schenectady", "Troy", "Saratoga Springs"])
    centroid = (albany + schenectady + troy) / 3
    tip, west, east = (centroid + head_pad * (p - centroid) for p in (albany, schenectady, troy))
    base_mid = (west + east) / 2
    top = saratoga + 0.06 * (saratoga - base_mid)
    along = (top - base_mid) / np.linalg.norm(top - base_mid)
    half = shaft_frac * np.linalg.norm(east - west) / 2 * np.array([along[1], -along[0]])
    start = base_mid - 0.15 * (base_mid - tip)  # overlap the head so the two pieces join cleanly
    shaft = shapely.Polygon([start - half, top - half, top + half, start + half])
    arrow = shapely.Polygon([tip, west, east]).union(shaft)
    series = gpd.GeoSeries([arrow], crs=MAP_CRS)
    series.plot(ax=ax, facecolor=color("highlight.risk"), alpha=0.18, edgecolor="none", zorder=8)
    series.boundary.plot(ax=ax, color=color("highlight.risk"), linewidth=1.6, zorder=9)


@app.function
def draw_job_center_map(ax, tracts: gpd.GeoDataFrame, labels: dict, offsets: dict, *, max_size: float = 900) -> None:
    """Tract jobs as circles (area to scale): grey for non-centers, center tracts by public share, hollow rings for
    tracts that are centers on private jobs only. One label per center: name, jobs and public share."""
    points = tracts.geometry.representative_point()
    scale = max_size / tracts["jobs_total"].max()
    bins = {"Mostly private (under 25% public)": (0, 0.25, "#4F7FA8"), "Mixed (25–50% public)": (0.25, 0.5, "#B27BC0"),
            "Mostly public (over 50%)": (0.5, 1.01, "#6A3D9A")}
    others = ~tracts["is_recommended_center"]
    ax.scatter(points[others].x, points[others].y, s=tracts.loc[others, "jobs_total"] * scale, facecolor=color("neutral.comparison_fill"),
               alpha=0.5, edgecolor="white", linewidth=0.4, zorder=5)
    for _name, (low, high, fill) in bins.items():
        mask = tracts["is_recommended_center"] & (tracts["public_share"] >= low) & (tracts["public_share"] < high)
        ax.scatter(points[mask].x, points[mask].y, s=tracts.loc[mask, "jobs_total"] * scale, facecolor=fill, alpha=0.85,
                   edgecolor="white", linewidth=0.5, zorder=6)
    private_only = tracts["private_only"]
    ax.scatter(points[private_only].x, points[private_only].y, s=tracts.loc[private_only, "jobs_total"] * scale, facecolor="none",
               edgecolor=color("neutral.text"), linewidth=0.9, zorder=7)

    centers = tracts.loc[tracts["is_recommended_center"]].assign(x=points.x, y=points.y)
    for component, group in centers.groupby("recommended_cluster_id"):
        weights = group["jobs_total"]
        x, y = (group["x"] * weights).sum() / weights.sum(), (group["y"] * weights).sum() / weights.sum()
        name = labels[component]
        public = 1 - group["private_jobs"].sum() / weights.sum()
        offset = offsets.get(name, (14, 0))
        ax.annotate(f"{name}\n{format_count(weights.sum())} jobs · {public:.0%} public", (x, y), xytext=offset, textcoords="offset points",
                    ha=offset_align(offset), va="center", fontsize=6.2, fontweight="bold", color=color("neutral.text"), path_effects=halo(),
                    arrowprops={"arrowstyle": "-", "color": "#7B8794", "linewidth": 0.5, "shrinkA": 0, "shrinkB": 3}, zorder=10)
    malta = tracts.loc[tracts["tract_geoid"] == "36091061907"]
    if len(malta):
        p = malta.geometry.representative_point().iloc[0]
        ax.annotate("Malta (GlobalFoundries)\ncenter on private jobs only", (p.x, p.y), xytext=(16, -4), textcoords="offset points",
                    ha="left", va="center", fontsize=5.8, fontstyle="italic", color=color("neutral.text"), path_effects=halo(), zorder=10)

    handles = [plt.scatter([], [], s=jobs * scale, facecolor=color("neutral.comparison_fill"), edgecolor="white", label=f"{jobs:,} jobs")
               for jobs in (2_000, 10_000, 25_000)]
    handles += [plt.scatter([], [], s=60, facecolor=fill, label=name) for name, (_lo, _hi, fill) in bins.items()]
    handles += [plt.scatter([], [], s=60, facecolor="none", edgecolor=color("neutral.text"), label="Center on private jobs only")]
    ax.legend(handles=handles, loc="upper left", frameon=True, facecolor="white", edgecolor="none", framealpha=0.85, fontsize=6.4,
              labelspacing=1.7, borderpad=1.0, title="Job center tracts", title_fontsize=6.8, alignment="left")


@app.function
def draw_gdp_gap(gdp: pd.DataFrame, names: dict):
    """Two lines (the first metro in red), the gap between them shaded, and the gap labeled at both ends."""
    fig = chart_figure(4.6)
    ax = fig.add_axes((0.08, 0.13, 0.78, 0.68))
    (a, a_name), (b, b_name) = names.items()
    years = gdp.index
    va, vb = gdp[a] / 1e9, gdp[b] / 1e9
    ax.fill_between(years, va, vb, color="#E6EAEE", zorder=1)
    for values, name, fill, width in ((vb, b_name, "#52606D", 1.6), (va, a_name, color("highlight.risk"), 2.2)):
        ax.plot(years, values, color=fill, linewidth=width, zorder=3)
        ax.annotate(f"{name}  ${values.iloc[-1]:.1f}B", (years[-1], values.iloc[-1]), xytext=(6, 4 if name == b_name else -4),
                    textcoords="offset points", ha="left", va="center", fontsize=8, fontweight="bold", color=fill)
    for year in (years[0], years[-1]):
        gap = vb[year] - va[year]
        ax.annotate("", (year, va[year]), xytext=(year, vb[year]), arrowprops={"arrowstyle": "<->", "color": "#7B8794", "linewidth": 0.8})
        first = year == years[0]
        ax.annotate(tex_safe(f"${gap:.1f}B gap"), (year, (va[year] + vb[year]) / 2), xytext=(6, 0) if first else (-10, 16),
                    textcoords="offset points", ha="left" if first else "right", va="center", fontsize=7.2,
                    color=color("neutral.text"))
    ax.set_xlim(years[0] - 0.3, years[-1] + 0.3)
    ax.yaxis.set_major_locator(plt.MultipleLocator(5))
    ax.yaxis.set_major_formatter(lambda y, _: tex_safe(f"${y:.0f}B"))
    ax.set_xticks(list(years[::2]))
    style_axes(ax)
    return fig


@app.function
def metro_net_uncapped(totals: pd.DataFrame, members: pd.DataFrame, pop: pd.Series, *, years: int) -> pd.DataFrame:
    """Per CBSA, annual net domestic migration from the IRS county totals ('us' bucket, uncapped). Moves between a
    metro's own counties count in both its in and out totals, so they cancel in the net."""
    us = totals.loc[totals["bucket"] == "us"].merge(members, on="county_geoid")
    sums = us.pivot_table(index="cbsa_code", columns="direction", values="people", aggfunc="sum") / years
    out = pd.DataFrame({"net_people": sums["in"] - sums["out"]})
    out["net_rate"] = out["net_people"] / pop.reindex(out.index)
    return out.dropna()


@app.function
def flows_by_region(totals: pd.DataFrame, pairs: pd.DataFrame, counties: pd.Series, within: float, *, years: int) -> pd.DataFrame:
    """One New York metro's annual people in, out and net, by the other end: other states and New York from the IRS
    county totals (New York less `within`, the moves between the metro's own counties); Downstate from the published
    pairs (`pairs`, classified); the rest of Upstate is the remainder, so it holds New York's suppressed pairs."""
    t = totals.loc[totals["county_geoid"].isin(counties)].pivot_table(index="bucket", columns="direction", values="people", aggfunc="sum")
    down = pairs.loc[pairs["region"] == "Downstate NY"].groupby("direction")["people"].sum()
    rows = {
        "Other states": (t.loc["different_state", "in"], t.loc["different_state", "out"]),
        "Downstate NY": (down.get("in", 0), down.get("out", 0)),
        "Rest of Upstate NY": (t.loc["same_state", "in"] - within - down.get("in", 0), t.loc["same_state", "out"] - within - down.get("out", 0)),
    }
    rows["All moves"] = (t.loc["us", "in"] - within, t.loc["us", "out"] - within)
    out = pd.DataFrame([(k, i / years, o / years) for k, (i, o) in rows.items()], columns=["region", "in", "out"])
    return out.assign(net=lambda d: d["in"] - d["out"])


@app.function
def draw_migration_flows(migration: pd.DataFrame):
    """E3: mirrored bars per region, people moving in to the right and out to the left, with the net at the right edge."""
    fills = {"Other states": "#C9B48A", "Downstate NY": "#3E5C76", "Rest of Upstate NY": "#9FB0C2", "All moves": "#52606D"}
    rows = migration.reset_index(drop=True)
    n = len(rows)
    fig = chart_figure(0.8 + 0.45 + n * 0.5 + 0.85)
    height = fig.get_figheight()
    ax = fig.add_axes((0.2, 0.85 / height, 0.62, n * 0.5 / height))
    limit = rows[["in", "out"]].to_numpy().max() * 1.3
    for r, row in rows.iterrows():
        total = row["region"] == "All moves"
        fill = fills[row["region"]]
        ax.barh(r, row["in"], color=fill, height=0.6, zorder=2)
        ax.barh(r, -row["out"], color=fill, alpha=0.55, height=0.6, zorder=2)
        for value, sign in [(row["in"], 1), (row["out"], -1)]:
            ax.annotate(f"{value:,.0f}", (sign * value, r), xytext=(sign * 4, 0), textcoords="offset points",
                        ha="left" if sign > 0 else "right", va="center", fontsize=7, color=color("neutral.text"),
                        fontweight="bold" if total else "normal")
    ax.axvline(0, color=color("neutral.text"), linewidth=0.8, zorder=3)
    ax.axhline(n - 1.5, color=color("neutral.grid_major"), linewidth=0.6)
    ax.set_xlim(-limit, limit)
    ax.set_ylim(n - 0.5, -0.5)
    for r, row in rows.iterrows():
        ax.annotate(f"{row['net']:+,.0f}", (1.0, r), xycoords=("axes fraction", "data"), xytext=(60, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=8.2, fontweight="bold",
                    color=color("highlight.risk") if row["net"] < 0 else "#2E7D32")
    ax.set_yticks(range(n))
    ax.set_yticklabels(rows["region"], fontsize=8.2)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.xaxis.set_major_formatter(lambda x, _: f"{abs(x):,.0f}")
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(axis="x", labelsize=7, colors=color("neutral.text_muted"), length=0)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=color("neutral.grid_major"), linewidth=0.5)
    ax.set_axisbelow(True)
    top = 1 - 0.85 / height
    fig.text(0.2 + 0.31 - 0.01, top, "← Moved out", ha="right", va="bottom", fontsize=7.6, fontweight="bold", color=color("neutral.text_muted"))
    fig.text(0.2 + 0.31 + 0.01, top, "Moved in →", ha="left", va="bottom", fontsize=7.6, fontweight="bold", color=color("neutral.text_muted"))
    fig.text(0.82 + 60 / 72 / fig.get_figwidth(), top, "Net", ha="right", va="bottom", fontsize=7.6, fontweight="bold", color=color("neutral.text_muted"))
    return fig


@app.function
def peer_rows(raw: pd.DataFrame, peers: pd.DataFrame, metrics: dict) -> pd.DataFrame:
    """Albany, its peers in rank order, the peer median and the median US metro, with the raw metric values."""
    wide = metro_wide(raw)
    codes = [CBSA_CODE, *peers["peer_cbsa_code"]]
    names = raw.drop_duplicates("geo_id").set_index("geo_id")["geo_name"]
    rows = pd.DataFrame({"metro": [short_metro(names[c]) for c in codes], "rank": ["", *peers["peer_rank"].astype(str)],
                         "similarity": [np.nan, *peers["similarity"]], "kind": ["albany", *["peer"] * len(peers)]})
    rows = pd.concat([rows, wide.loc[codes, list(metrics)].reset_index(drop=True)], axis=1)
    peer_median = wide.loc[peers["peer_cbsa_code"], list(metrics)].median()
    us_median = wide[list(metrics)].median()
    extra = pd.DataFrame([{"metro": "Peer median", "rank": "", "similarity": np.nan, "kind": "summary", **peer_median},
                          {"metro": "Median US metro", "rank": "", "similarity": np.nan, "kind": "summary", **us_median}])
    return pd.concat([rows, extra], ignore_index=True)


@app.function
def draw_peer_stats(table: pd.DataFrame, metrics: dict):
    """E4: rank, metro, similarity and the metric columns. Albany shaded at the top; the peer and US medians in grey."""
    columns = [("#", 0.035, "right"), ("Metro area", 0.05, "left"), ("Similarity", 0.255, "right")]
    x = 0.255
    for metric_id, (header, _kind) in metrics.items():
        x += 0.0905
        columns.append((header, x, "right"))
    kinds = [kind for _header, kind in metrics.values()]
    rows, styles = [], []
    for row in table.itertuples():
        cells = [row.rank, row.metro, "" if pd.isna(row.similarity) else f"{row.similarity:.2f}"]
        cells += [format_metric(kind, getattr(row, metric_id)) for metric_id, kind in zip(metrics, kinds)]
        rows.append(cells)
        styles.append({"albany": {"bold": True, "fill": "#FBE9E7", "color": color("neutral.text")},
                       "summary": {"color": color("neutral.text_muted")}}.get(row.kind, {}))
    return draw_text_table(columns, rows, row_styles=styles, header_in=0.5, footer_in=0.75)


@app.function
def draw_share_bars(shares: pd.DataFrame, colors: dict):
    """Two 100% stacked bars, residents and land area, by area group, each segment labeled with its share."""
    fig = chart_figure(0.75 + 0.35 + 2 * 0.55 + 0.45)
    ax = fig.add_axes((0.14, 0.45 / fig.get_figheight(), 0.82, 1.1 / fig.get_figheight()))
    for r, (column, label) in enumerate((("resident_share", "Residents"), ("land_share", "Land area"))):
        left = 0.0
        for group, fill in colors.items():
            value = shares.loc[group, column]
            ax.barh(r, value, left=left, height=0.62, color=fill, edgecolor="white", linewidth=1)
            if value >= 0.04:
                ax.annotate(f"{value:.0%}", (left + value / 2, r), ha="center", va="center", fontsize=8, fontweight="bold",
                            color="white" if fill == color("highlight.risk") else color("neutral.text"))
            left += value
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Residents", "Land area"], fontsize=8.5)
    ax.set_ylim(1.5, -0.5)
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.tick_params(axis="y", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.legend(handles=[Patch(facecolor=f, label=g) for g, f in colors.items()], loc="upper left",
               bbox_to_anchor=(0.02, 1 - 0.78 / fig.get_figheight()), ncol=3, frameon=False, fontsize=7.5)
    return fig


@app.function
def zone_summary(tracts: pd.DataFrame) -> pd.DataFrame:
    """Per working name: national type, tracts, residents, median raw values and the places with the most tracts."""
    def mostly_in(series):
        counts = series.replace("Town area (no place)", "town areas").value_counts()
        return ", ".join(counts.head(3).index)

    return (tracts.groupby("working_name")
            .agg(national_type=("zone_type", "first"), tracts=("tract_geoid", "size"), residents=("residents", "sum"),
                 income=("median_hh_income", "median"), poverty=("pov_rate", "median"), ba_plus=("pct_ba_plus", "median"),
                 owners=("owner_occ_rate", "median"), density=("pop_weighted_density_sqmi", "median"), mostly_in=("place", mostly_in))
            .sort_values("tracts", ascending=False).reset_index())


@app.function
def draw_zone_table(table: pd.DataFrame, activity: pd.DataFrame):
    """E10: one row per zone: a color swatch, the working name over the national type, size, median values, and a bar
    splitting the zone's residents by activity class. `activity`: residents, working name x activity class."""
    row_in = 0.42
    columns = [("Zone (Albany working name)\nNational type", 0.05, "left"), ("Tracts", 0.355, "right"), ("Residents", 0.43, "right"),
               ("Median\nincome", 0.5, "right"), ("Poverty", 0.565, "right"), ("BA or\nhigher", 0.63, "right"),
               ("Owners", 0.695, "right"), ("Density¹", 0.765, "right"), ("What's there²\n(share of residents)", 0.79, "left")]
    rows = [["", f"{r.tracts}", format_count(r.residents), f"${r.income / 1e3:,.0f}k", f"{r.poverty:.0%}", f"{r.ba_plus:.0%}",
             f"{r.owners:.0%}", f"{r.density:,.0f}", ""] for r in table.itertuples()]
    fig = draw_text_table(columns, rows, row_styles=[{} for _ in rows], row_in=row_in, footer_in=0.95)
    height_in = fig.get_figheight()
    bar_x, bar_w, bar_h = 0.79, 0.19, 0.2
    for i, r in enumerate(table.itertuples()):
        mid = 0.8 + 0.5 + (i + 0.5) * row_in
        fig.text(0.035, 1 - mid / height_in, "■", ha="right", va="center", fontsize=11, color=ZONE_COLORS.get(r.working_name, "#999999"))
        fig.text(0.05, 1 - (mid - 0.075) / height_in, r.working_name, ha="left", va="center", fontsize=7.6, color=color("neutral.text"))
        fig.text(0.05, 1 - (mid + 0.095) / height_in, r.national_type, ha="left", va="center", fontsize=6.3,
                 color=color("neutral.text_muted"))
        shares = activity.loc[r.working_name] / activity.loc[r.working_name].sum()
        left = bar_x
        for name in ACTIVITY_ORDER:
            width = shares.get(name, 0) * bar_w
            fig.add_artist(plt.Rectangle((left, 1 - (mid + bar_h / 2) / height_in), width, bar_h / height_in, transform=fig.transFigure,
                                         facecolor=ACTIVITY_COLORS[name], edgecolor="white", linewidth=0.4))
            left += width
    handles = [Patch(facecolor=ACTIVITY_COLORS[name], label=name) for name in ACTIVITY_ORDER]
    fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.985, 1 - (0.8 + 0.5 + len(rows) * row_in + 0.04) / height_in),
               ncol=4, frameon=False, fontsize=6.6, handlelength=1.1, columnspacing=1.0, title="² What's there", title_fontsize=6.6,
               alignment="right")
    return fig


if __name__ == "__main__":
    app.run()
