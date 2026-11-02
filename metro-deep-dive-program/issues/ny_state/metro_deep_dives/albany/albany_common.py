"""Paths, constants and helpers shared by every Albany lens.

Imported by each lens's notebooks and by albany_explore.py. Anything a second lens uses, or that any lens's print
exhibits would reuse (map frames, map layers, chart frames, loaders), lives here; a helper for one exhibit stays in
its lens's visuals notebook. Plain Python rather than a notebook, so no lens depends on another lens's notebook.
"""

import json
import sys

import numpy as np
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import shapely
from matplotlib import font_manager, patheffects
from matplotlib.patches import Patch

# The albany/ folder: shared queries, data and reference files sit here; each part has its own folder below it.
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[4]
SQL_DIR = HERE / "sql"
ANALYSES_DIR = REPO_ROOT / "metro-deep-dive-program" / "analyses"
# The What NY Is notebook's folder, which holds the series intro's statewide layers.
SERIES_INTRO_DIR = HERE.parents[1] / "primer" / "series_intro"
# The NY Infrastructure handoff that the series intro's Map 2 uses. Read-only here, for the rivers.
INFRA_HANDOFF = SERIES_INTRO_DIR / "data" / "map2_infrastructure_handoff.json"

sys.path.insert(0, str(REPO_ROOT / "metro-deep-dive-program" / "issues" / "_shared" / "act_1"))
sys.path.insert(0, str(REPO_ROOT / "foundations" / "visual_library" / "chart_engine_py"))
# Q2's own center method, so the all-jobs centers (E8) use it unchanged.
sys.path.insert(0, str(ANALYSES_DIR / "explanation" / "q2_job_proximity"))
from build_q2_job_center_mart import apply_method
from chart_engine.theme import Theme
from duckdb_helpers import connect_duckdb, read_sql  # noqa: F401 (connect_duckdb is re-exported for the notebooks)

# Albany-Schenectady-Troy, 2023 delineation (D4).
CBSA_CODE = "10580"
# NAD83 / New York East state plane (meters); all five counties sit in the East zone.
MAP_CRS = "EPSG:32115"
SOURCE_CRS = "EPSG:4269"
RIVER_COLOR = "#6FA3CF"
# The series' default Downstate: `downstate_core` in the What NY Is seed (NYC, Long Island,
# Westchester, Putnam, Rockland). Upstate is the other 52 counties, so every NY metro but NYC's.
REGIONS_SEED = REPO_ROOT / "foundations" / "etl" / "reference" / "ny_county_regions.csv"
NYC_CBSA_CODE = "35620"
# Key places: curated landmarks with one source each (data review passed, Dan, 2026-10-24).
ANCHORS_CSV = HERE / "reference" / "anchors.csv"
ANCHOR_SOURCES = HERE / "reference" / "anchor_sources.json"
# The What NY Is highway, rail and canal selection, read from its own folder (R8).
INFRA_SQL = SERIES_INTRO_DIR / "sql" / "map2_infrastructure.sql"
# NYS Canal Corporation centerline, pulled for What NY Is (its manifest has the URL and checksum).
CANAL_GEOJSON = SERIES_INTRO_DIR / "data" / "canal_centerline.geojson"
CANAL_COLOR = "#2A9D8F"
# Towns (county subdivisions; NY towns and cities aren't Census places) and their ACS 2020-24 population,
# parks (OpenStreetMap, curated in reference/parks.csv), and the Adirondack Park boundary from What NY Is.
# Local downloads; provenance in data/anchors_reference_manifest.json.
TOWNS_ZIP = HERE / "data" / "cb_2023_36_cousub_500k.zip"
TOWNS_POP = HERE / "data" / "acs2024_cousub_population.json"
# IRS county migration totals, 2018-22, uncapped (data/build_irs_county_totals.py): E3 and E4's migration column.
IRS_TOTALS_CSV = HERE / "data" / "irs_county_totals_2018_2022.csv"
PARKS_GEOJSON = HERE / "data" / "osm_parks_selected.geojson"
PARKS_CSV = HERE / "reference" / "parks.csv"
ADIRONDACK_GEOJSON = SERIES_INTRO_DIR / "data" / "adirondack_park.geojson"
PARK_FILL = "#B9D9A8"
PARK_EDGE = "#6E9E5A"
# E1c's area layers from OpenStreetMap (data/build_osm_core_detail.py): layer -> (fill, edge, legend label).
CORE_DETAIL_GEOJSON = HERE / "data" / "osm_core_detail.geojson"
CORE_AREA_STYLES = {
    "park": (PARK_FILL, PARK_EDGE, "Park or preserve"),
    "campus": ("#CFE0F0", "#1F78B4", "College or university campus"),
    "hospital": ("#F7CDD2", "#D7263D", "Hospital campus"),
    "airport": ("#D3E3E5", "#00838F", "Albany International Airport"),
}
# Latest local Albany POI engine run (E10's activity bars). Switch to the POI mart once the run is published.
POI_RUN_DIR = sorted((REPO_ROOT / "metro-deep-dive-program" / "engines" / "poi" / "outputs" / "albany_ny").glob("overture-places-*"))[-1]

FOUR_CITIES = ["Albany", "Schenectady", "Troy", "Saratoga Springs"]
# "The triangle" (Dan, 2026-10-27, redrawn north the same day): the three old cities, the small cities and towns
# between them, and southern Saratoga County up to the Northway. Bethlehem and Guilderland stay out (the text puts
# Bethlehem with the southern towns). Menands is a village inside Colonie, so Colonie covers it.
TRIANGLE_TOWNS = ["Albany", "Troy", "Schenectady", "Rensselaer", "Watervliet", "Cohoes", "Green Island", "Colonie",
                  "Niskayuna", "Waterford", "Halfmoon", "Clifton Park"]
# The Northway arm: the towns along I-87 from the triangle up to Saratoga Springs. Triangle + arm = the arrow (E6, E7).
NORTHWAY_ARM = ["Malta", "Saratoga Springs"]

# National zone type -> (Albany working name, what we expect its tracts to look like). Working names are
# Albany's; the national types stay as they are (Dan, 2026-10-22). Not yet cleared for print.
ZONE_NAMES = {
    "Mixed-Income Middle Neighborhoods": ("Comfortable suburbs", "low poverty, owners, educated, moderate density"),
    "Established Residential": ("Rural and exurban", "very low density, owners, older"),
    "Entry-Market Neighborhoods": ("Lower-income urban", "high poverty, renters, dense"),
    "Working Neighborhoods": ("Working-class urban", "moderate poverty, low BA+, dense"),
    "Emerging Knowledge Districts": ("Students and young professionals", "renters, high BA+, high turnover, dense"),
    "Knowledge Corridor": ("Professional mixed-use", "educated, jobs and apartments mixed, moderate density"),
    "Commercial Core / Jobs Center": ("Jobs center", "far more jobs than residents"),
}
# Working name -> fill (E9, E10). Legend order follows this dict.
ZONE_COLORS = {
    "Professional mixed-use": "#1B6CA8",
    "Students and young professionals": "#7FB2D9",
    "Comfortable suburbs": "#D9CBB0",
    "Rural and exurban": "#A9BF8E",
    "Working-class urban": "#C9A44C",
    "Lower-income urban": "#E0A375",
    "Jobs center": "#5F6C7B",
}

# Q3e activity classes: what's there, next to who lives there (the zones). Category bundles over the governed POI
# categories; the rest (recreation, parks, civic, religious, agriculture) count toward the total only.
ACTIVITY_BUNDLES = {
    "local": ["Food & Drink", "Retail", "Personal Care", "Services", "Financial Institutions"],
    "destination": ["Healthcare", "Education", "Government & Public Safety", "Arts, Culture & Landmarks", "Lodging",
                    "Entertainment & Nightlife"],
    "industrial": ["Industrial & Logistics", "Automotive", "Utilities", "Transportation"],
}
ACTIVITY_ORDER = ["Residential", "Local-serving", "Destination", "Employment and industrial"]
ACTIVITY_COLORS = dict(zip(ACTIVITY_ORDER, ["#C9D3DD", "#66A61E", "#7570B3", "#D95F02"]))
# The Q3e rule settings (Dan, 2026-10-27), shared with the exploration notebook. The Residential cut is the
# metro median of POIs per 1,000 residents, computed in tract_activity.
ACTIVITY_RULES = {"shrink": 20, "jobs_cut": 1.0, "destination_lift": 1.5, "industrial_lift": 2.0}

# 2x Substack content width (728 px).
EXPORT_WIDTH_PX = 1456
EXPORT_DPI = 200

THEME = Theme.default()
# Style guide stack: Inter, then Arial. Skip any that aren't installed so matplotlib doesn't warn per glyph.
_installed = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams["font.family"] = [
    f for f in (THEME.fonts.get("family", "Inter"), "Arial", "Helvetica") if f in _installed
] + ["sans-serif"]


def color(key: str) -> str:
    return THEME.color(key, "#7B8794")


def run_sql(con, path: Path, **params: str) -> pd.DataFrame:
    """Run a query file after filling each `__NAME__` placeholder (keyword names upper-cased)."""
    sql = read_sql(path)
    for name, value in params.items():
        sql = sql.replace(f"__{name.upper()}__", value)
    return con.sql(sql).df()


def sql_list(codes) -> str:
    """['10580', '15380'] -> "'10580', '15380'" for an IN list."""
    return ", ".join(f"'{code}'" for code in codes)


def to_geo(df: pd.DataFrame, *, wkb_column: str = "geom_wkb", crs: str = SOURCE_CRS) -> gpd.GeoDataFrame:
    """A query result with a WKB column, as a GeoDataFrame in MAP_CRS."""
    df = df.copy()
    geometry = shapely.from_wkb(df.pop(wkb_column).map(bytes))
    return gpd.GeoDataFrame(df, geometry=geometry, crs=crs).to_crs(MAP_CRS)


def load_metro_layers(con) -> dict:
    """Every layer the maps share, in MAP_CRS."""
    counties = to_geo(run_sql(con, SQL_DIR / "metro_counties.sql", cbsa_code=CBSA_CODE))
    context = to_geo(run_sql(con, SQL_DIR / "context_counties.sql"))
    artifact = REPO_ROOT / json.loads(INFRA_HANDOFF.read_text())["artifact_uri"]
    rivers = run_sql(con, SQL_DIR / "rivers.sql", infrastructure_path=artifact.as_posix().replace("'", "''"))
    return {
        "counties": counties,
        "outline": gpd.GeoDataFrame(geometry=[counties.union_all()], crs=MAP_CRS),
        "context": context,
        "states": context.dissolve(by="state_fips", as_index=False),
        "rivers": to_geo(rivers, crs="EPSG:4326"),
        "places": to_geo(run_sql(con, SQL_DIR / "metro_place_points.sql", cbsa_code=CBSA_CODE)),
    }


def county_short_name(name: str) -> str:
    return name.removesuffix(" County")


def metro_county_table(counties: gpd.GeoDataFrame) -> pd.DataFrame:
    """One row per county: flag, population, share of the metro, growth 2012–2024."""
    table = pd.DataFrame(
        {
            "county": counties["county_name"].map(county_short_name),
            "flag": counties["county_flag"],
            "pop_2024": counties["pop_2024"],
            "metro_share": counties["pop_2024"] / counties["pop_2024"].sum(),
            "pop_2012": counties["pop_2012"],
            "growth": counties["pop_growth"],
        }
    )
    return table.sort_values("growth", ascending=False).reset_index(drop=True)


def new_map(layers: dict, *, pad: float = 0.04, header_in: float = 0.75, footer_in: float = 0.3):
    """A figure framed on the metro with neighboring counties in faint grey. Height follows the metro's shape."""
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

    layers["context"].plot(ax=ax, color=color("neutral.grid_minor"), edgecolor="white", linewidth=0.6)
    layers["states"].boundary.plot(ax=ax, color=color("neutral.border"), linewidth=0.8)
    ax.set_xlim(minx - dx, maxx + dx)
    ax.set_ylim(miny - dy, maxy + dy)
    ax.set_aspect("equal")
    return fig, ax


def draw_metro_counties(ax, layers: dict) -> None:
    """The metro counties in white over the grey context, with county lines."""
    layers["counties"].plot(ax=ax, color=color("neutral.background_white"), edgecolor=color("neutral.border"),
                            linewidth=0.6)


def draw_county_flags(ax, layers: dict, colors: dict) -> None:
    counties = layers["counties"]
    counties.plot(ax=ax, color=counties["county_flag"].map(colors), edgecolor="white", linewidth=1.4)


def draw_county_lines(ax, layers: dict) -> None:
    layers["counties"].boundary.plot(ax=ax, color="white", linewidth=1.2)


def draw_metro_outline(ax, layers: dict, linewidth: float = 1.0) -> None:
    layers["outline"].boundary.plot(ax=ax, color=color("neutral.text"), linewidth=linewidth)


def to_map_points(positions: dict | None) -> dict:
    """{key: (lon, lat)} -> {key: shapely Point in MAP_CRS}."""
    return {
        key: gpd.GeoSeries([shapely.Point(lonlat)], crs="EPSG:4326").to_crs(MAP_CRS).iloc[0]
        for key, lonlat in (positions or {}).items()
    }


def halo(width: float = 2.0) -> list:
    return [patheffects.withStroke(linewidth=width, foreground="white")]


def offset_align(offset: tuple) -> str:
    """Left-align labels pushed right of their point, right-align those pushed left."""
    return "left" if offset[0] > 3 else "right" if offset[0] < -3 else "center"


def draw_county_labels(ax, layers: dict, *, positions: dict | None = None) -> None:
    """County name in bold with its OMB flag underneath, in small muted capitals."""
    placed = to_map_points(positions)
    for row in layers["counties"].itertuples():
        name = county_short_name(row.county_name)
        point = placed.get(name, row.geometry.representative_point())
        ax.annotate(name, (point.x, point.y), ha="center", va="bottom", fontsize=8, fontweight="bold",
                    color=color("neutral.text"), path_effects=halo(), zorder=8)
        ax.annotate(row.county_flag.upper(), (point.x, point.y), xytext=(0, -2), textcoords="offset points",
                    ha="center", va="top", fontsize=5.8, color=color("neutral.text_muted"),
                    path_effects=halo(), zorder=8)


def format_count(value: float) -> str:
    return f"{value / 1e3:,.0f}k" if value >= 10_000 else f"{value / 1e3:,.1f}k"


def short_cbsa(name: str) -> str:
    """'Albany-Schenectady-Troy, NY' -> 'Albany'."""
    return name.split(",")[0].split("-")[0]


def format_metric(kind: str, value: float) -> str:
    """Display format by metric kind (the second item in q4_metrics)."""
    if pd.isna(value):
        return "—"
    if kind == "count":
        return f"{value / 1e6:,.2f}M" if value >= 1e6 else f"{value / 1e3:,.0f}k"
    if kind == "usd_big":
        return f"${value / 1e12:,.2f}T" if value >= 1e12 else f"${value / 1e9:,.1f}B"
    if kind == "usd":
        return f"${value:,.0f}"
    if kind == "change":
        return f"{value:+.1%}"
    if kind == "pct":
        return f"{value:.1%}"
    if kind == "pct0":
        return f"{value:.0%}"
    if kind == "int":
        return f"{value:,.0f}"
    if kind == "per1k":
        return f"{1000 * value:+.1f}"
    if kind == "ratio":
        return f"{value:.2f}"
    return f"{value:,.1f}"


def metro_wide(raw: pd.DataFrame) -> pd.DataFrame:
    """Metros only: geo_id x metric_id values."""
    return raw.loc[raw["geo_level"] == "cbsa"].pivot(index="geo_id", columns="metric_id", values="value")


def upstate_aggregate(raw: pd.DataFrame, counties: set, metrics: dict, rules: dict) -> dict:
    """Upstate value per metric from its counties: metric_id -> (value, exact). See q4_upstate_rules."""
    wide = raw.loc[(raw["geo_level"] == "county") & raw["geo_id"].isin(counties)].pivot(
        index="geo_id", columns="metric_id", values="value")
    out = {}
    for metric_id in metrics:
        rule, exact = rules.get(metric_id, ("pop_total", False))
        if metric_id not in wide or wide[metric_id].isna().all():
            # No county rows for this metric (e.g. BEA real GDP growth): leave Upstate blank.
            out[metric_id] = (np.nan, True)
            continue
        if rule == "sum":
            value = wide[metric_id].sum()
        elif rule == "growth":
            value = wide["pop_total"].sum() / wide["pop_total_2014"].sum() - 1
        else:
            pair = wide[[metric_id, rule]].dropna()
            value = (pair[metric_id] * pair[rule]).sum() / pair[rule].sum()
        out[metric_id] = (value, exact)
    return out


def position_words(values: pd.Series, value: float) -> str:
    """'higher than 84% of metros' or 'lower than 72% of metros', whichever side Albany is on."""
    above, below = (values < value).mean(), (values > value).mean()
    return f"higher than {above:.0%} of metros" if above >= below else f"lower than {below:.0%} of metros"


def metro_scorecard(raw: pd.DataFrame, metrics: dict, upstate_metros: set, upstate: dict) -> pd.DataFrame:
    """Per metric: Albany's value, its position and ranks (US, NY, Upstate; 1 = highest), and the references."""
    names = raw.drop_duplicates("geo_id").set_index("geo_id")["geo_name"]
    ny = set(raw.loc[raw["is_ny_metro"].fillna(False).astype(bool), "geo_id"])
    refs = raw.loc[raw["geo_level"].isin(["state", "us"])].pivot(index="metric_id", columns="geo_level", values="value")
    wide = metro_wide(raw)
    years = raw.drop_duplicates("metric_id").set_index("metric_id")["year"]
    rows = []
    for metric_id, (label, kind, group) in metrics.items():
        values = wide[metric_id].dropna()
        ny_values = values.loc[values.index.isin(ny)]
        up_values = values.loc[values.index.isin(upstate_metros)]
        albany = values.get(CBSA_CODE, np.nan)
        top_other = up_values.drop(CBSA_CODE).idxmax()
        up_value, up_exact = upstate[metric_id]
        rows.append({
            "group": group,
            "metric": label,
            "year": int(years[metric_id]),
            "Albany": format_metric(kind, albany),
            "position": position_words(values, albany),
            "US rank": f"{int((values > albany).sum() + 1)} of {len(values)}",
            "NY rank": f"{int((ny_values > albany).sum() + 1)} of {len(ny_values)}",
            "Upstate rank": f"{int((up_values > albany).sum() + 1)} of {len(up_values)}",
            "Upstate": ("" if up_exact else "≈ ") + format_metric(kind, up_value),
            "NY State": format_metric(kind, refs.loc[metric_id].get("state", np.nan)) if metric_id in refs.index else "—",
            "US": format_metric(kind, refs.loc[metric_id].get("us", np.nan)) if metric_id in refs.index else "—",
            "median metro": format_metric(kind, values.median()),
            "top other Upstate metro": f"{short_cbsa(names[top_other])} {format_metric(kind, up_values[top_other])}",
        })
    return pd.DataFrame(rows)


def upstate_sets(con, raw: pd.DataFrame) -> tuple:
    """Upstate counties (the series default: all but `downstate_core`) and Upstate metros (every NY metro but
    NYC's), with a check table. Upstate metros = NY metros minus NYC holds only if NYC's NY counties are Downstate."""
    regions = pd.read_csv(REGIONS_SEED, dtype={"county_geoid": str})
    counties = set(regions.loc[regions["downstate_core"].astype(str).str.lower() == "false", "county_geoid"])
    metros = raw.loc[raw["geo_level"] == "cbsa"]
    ny_metros = set(metros.loc[metros["is_ny_metro"].fillna(False).astype(bool), "geo_id"])
    upstate_metros = ny_metros - {NYC_CBSA_CODE}
    nyc_ny_counties = set(con.sql(
        f"SELECT county_geoid FROM silver.xwalk_cbsa_county WHERE cbsa_code = '{NYC_CBSA_CODE}' AND county_geoid LIKE '36%'"
    ).df()["county_geoid"])
    downstate = set(regions["county_geoid"]) - counties
    albany_pop = metros.loc[(metros["geo_id"] == CBSA_CODE) & (metros["metric_id"] == "pop_total"), "value"].iloc[0]
    checks = pd.DataFrame({
        "check": ["US metros (2023 delineation)", "NY metros", "Upstate metros", "Upstate counties",
                  "NYC metro's NY counties = Downstate", "Albany population, ACS 2020–24"],
        "value": [metros["geo_id"].nunique(), len(ny_metros), len(upstate_metros), len(counties),
                  nyc_ny_counties == downstate, f"{albany_pop:,.0f}"],
        "passed": [metros["geo_id"].nunique() == 393, len(ny_metros) == 13, len(upstate_metros) == 12,
                   len(counties) == 52, nyc_ny_counties == downstate, round(albany_pop) == 906_052],
    })
    assert checks["passed"].all(), checks
    return counties, upstate_metros, checks


def load_towns(layers: dict) -> gpd.GeoDataFrame:
    """The metro's county subdivisions (towns and cities) with ACS 2020-24 population and land area, in MAP_CRS."""
    counties = set(layers["counties"]["county_geoid"].str[2:])
    towns = gpd.read_file(f"zip://{TOWNS_ZIP}")
    towns = towns.loc[(towns["STATEFP"] == "36") & towns["COUNTYFP"].isin(counties)].to_crs(MAP_CRS)
    rows = json.loads(TOWNS_POP.read_text())
    pop = pd.DataFrame(rows[1:], columns=rows[0]).assign(
        GEOID=lambda d: d["state"] + d["county"] + d["county subdivision"], population=lambda d: d["B01003_001E"].astype(int))
    towns = towns.merge(pop[["GEOID", "population"]], on="GEOID", how="left")
    county_names = dict(zip(layers["counties"]["county_geoid"].str[2:], layers["counties"]["county_name"].map(county_short_name)))
    return gpd.GeoDataFrame({
        # "Colonie town", "Troy city": the type is the last word of NAMELSAD.
        "town": towns["NAME"], "kind": towns["NAMELSAD"].str.rsplit(" ", n=1).str[-1],
        "county": towns["COUNTYFP"].map(county_names), "population": towns["population"].fillna(0).astype(int),
        "land_sqmi": towns["ALAND"].astype(float) / 2_589_988.11,
    }, geometry=towns.geometry, crs=MAP_CRS)


def draw_towns(ax, towns: gpd.GeoDataFrame, *, labels: dict, size: float = 5.8) -> None:
    """Town lines in white over a soft grey edge, and italic names for the towns in `labels`: name -> (lon, lat),
    or None for the town's own label point. Cities are labeled as places, not here."""
    towns.boundary.plot(ax=ax, color="#AAB4BF", linewidth=1.0, zorder=2)
    towns.boundary.plot(ax=ax, color="white", linewidth=0.45, zorder=2)
    placed = to_map_points({k: v for k, v in labels.items() if v is not None})
    for row in towns.loc[towns["town"].isin(labels) & (towns["kind"] == "town")].itertuples():
        point = placed.get(row.town, row.geometry.representative_point())
        ax.annotate(row.town, (point.x, point.y), ha="center", va="center", fontsize=size, fontstyle="italic",
                    color="#52606D", path_effects=halo(1.6), zorder=7)


def draw_parks(ax, parks: gpd.GeoDataFrame, adirondack: gpd.GeoDataFrame) -> None:
    """Parks and preserves as soft green fills; the Adirondack Park as a dashed green boundary."""
    parks.plot(ax=ax, facecolor=PARK_FILL, edgecolor=PARK_EDGE, linewidth=0.3, alpha=0.85, zorder=2)
    adirondack.boundary.plot(ax=ax, color=PARK_EDGE, linewidth=1.1, linestyle=(0, (5, 2)), zorder=3)


def draw_core_areas(ax, areas: gpd.GeoDataFrame) -> None:
    """E1c's OSM areas over the place fills (zorder 7), parks first so campuses, hospitals and the airport sit on top."""
    for layer, (fill, edge, _label) in CORE_AREA_STYLES.items():
        part = areas.loc[areas["layer"] == layer]
        if not part.empty:
            part.plot(ax=ax, facecolor=fill, edgecolor=edge, linewidth=0.5 if layer == "park" else 0.8, alpha=0.95, zorder=7)


def ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def compact_value(kind: str, value: float) -> str:
    """Short reference values for card footers: $76.8k, 7.0M, otherwise format_metric."""
    if pd.isna(value):
        return "—"
    if kind == "usd":
        return f"${value / 1e3:,.1f}k"
    if kind == "count":
        return f"{value / 1e6:,.1f}M" if value >= 1e6 else f"{value / 1e3:,.0f}k"
    return format_metric(kind, value)


def tex_safe(text: str) -> str:
    """Escape $ so matplotlib never reads two of them as mathtext (R22)."""
    return text.replace("$", r"\$")


def core_box(bounds: tuple):
    """(lon_min, lat_min, lon_max, lat_max) -> a polygon in MAP_CRS."""
    return gpd.GeoSeries([shapely.box(*bounds)], crs="EPSG:4326").to_crs(MAP_CRS).iloc[0]


def draw_region_lines(ax, layers: dict, lines: dict, *, scale: float = 1.0) -> None:
    """Rail, canal, rivers and highways, lightest first."""
    lines["rail"].plot(ax=ax, color="#5F6C7B", linewidth=0.6 * scale, linestyle=(0, (4, 2)), zorder=3)
    layers["rivers"].plot(ax=ax, color=RIVER_COLOR, linewidth=1.1 * scale, zorder=3)
    lines["canal"].plot(ax=ax, color=CANAL_COLOR, linewidth=1.0 * scale, zorder=3)
    lines["interstate"].plot(ax=ax, color="#7B8794", linewidth=0.9 * scale, zorder=4)
    lines["thruway"].plot(ax=ax, color="#52606D", linewidth=1.5 * scale, zorder=4)


def draw_place_outlines(ax, places: gpd.GeoDataFrame, others: list, offsets: dict, *, label_size: float = 6.5,
                        unlabeled: set = frozenset(), fill: bool = True, labels: bool = True) -> None:
    """The four cities filled and labeled in bold; the chosen other places outlined and labeled lightly
    (except those in `unlabeled`, which keep their outline). `fill=False` draws the four cities as outlines only,
    for maps whose fill is data; `labels=False` skips every label."""
    four = places.loc[places["place_name"].isin(["Albany", "Schenectady", "Troy", "Saratoga Springs"]) & (places["place_kind"] == "city")]
    rest = places.loc[places["place_name"].isin(others) & ~places.index.isin(four.index)]
    if len(rest):
        rest.plot(ax=ax, facecolor="#C9D2DC", edgecolor="#7B8794", linewidth=0.4, alpha=0.7, zorder=5)
    four.plot(ax=ax, facecolor="#9FB0C2" if fill else "none", edgecolor=color("neutral.text"), linewidth=0.7 if fill else 1.0, zorder=6)
    if not labels:
        return
    for group, size, weight in ((rest.loc[~rest["place_name"].isin(unlabeled)], label_size, "normal"),
                                (four, label_size + 1.6, "bold")):
        for row in group.itertuples():
            point = row.geometry.representative_point()
            offset = offsets.get(row.place_name, (0, 0))
            ax.annotate(row.place_name, (point.x, point.y), xytext=offset, textcoords="offset points",
                        ha=offset_align(offset), va="center", fontsize=size, fontweight=weight,
                        color=color("neutral.text"), path_effects=halo(1.8), zorder=12)


def draw_route_labels(ax, routes: dict) -> None:
    for text, point in to_map_points(routes).items():
        ax.annotate(text, (point.x, point.y), ha="center", va="center", fontsize=5.8, fontweight="bold", color="#52606D",
                    bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "#52606D", "linewidth": 0.5}, zorder=11)


def draw_anchors(ax, anchors: gpd.GeoDataFrame, themes: dict, *, labels: set, offsets: dict, size: float = 26,
                 display: dict | None = None) -> None:
    """Key places as themed markers; names only for those in `labels`, shortened by `display` (name -> label)."""
    for theme, (fill, marker) in themes.items():
        part = anchors.loc[anchors["theme"] == theme]
        ax.scatter(part.geometry.x, part.geometry.y, s=size * (1.8 if marker == "*" else 1), marker=marker, color=fill,
                   edgecolor="white", linewidth=0.5, zorder=13)
    for row in anchors.loc[anchors["name"].isin(labels)].itertuples():
        offset = offsets.get(row.name, (5, 0))
        ax.annotate((display or {}).get(row.name, row.name), (row.geometry.x, row.geometry.y), xytext=offset, textcoords="offset points",
                    ha=offset_align(offset), va="center", fontsize=5.6, color=themes[row.theme][0],
                    path_effects=halo(1.6), zorder=14)


def region_legend(ax, county_colors: dict, themes: dict) -> None:
    handles = [Patch(facecolor=county_colors["Central"], label="Central county"),
               Patch(facecolor=county_colors["Outlying"], label="Outlying county"),
               Patch(facecolor="#9FB0C2", edgecolor=color("neutral.text"), label="The four cities"),
               Patch(facecolor="#C9D2DC", edgecolor="#7B8794", label="Other places"),
               plt.Line2D([], [], color="white", linewidth=1.0, path_effects=[patheffects.withStroke(linewidth=1.8, foreground="#AAB4BF")],
                          label="Town line (town names in italics)"),
               Patch(facecolor=PARK_FILL, edgecolor=PARK_EDGE, label="Park or preserve"),
               plt.Line2D([], [], color=PARK_EDGE, linewidth=1.1, linestyle=(0, (5, 2)), label="Adirondack Park boundary"),
               plt.Line2D([], [], color="#52606D", linewidth=1.5, label="Thruway"),
               plt.Line2D([], [], color="#7B8794", linewidth=0.9, label="Other interstate"),
               plt.Line2D([], [], color="#5F6C7B", linewidth=0.6, linestyle=(0, (4, 2)), label="Main-line rail"),
               plt.Line2D([], [], color=CANAL_COLOR, linewidth=1.0, label="Canal"),
               plt.Line2D([], [], color=RIVER_COLOR, linewidth=1.1, label="River")]
    handles += [plt.Line2D([], [], linestyle="", marker=m, markersize=6 if m != "*" else 8, color=f, label=t)
                for t, (f, m) in themes.items()]
    ax.legend(handles=handles, loc="upper left", frameon=True, facecolor="white", edgecolor="none", framealpha=0.85,
              fontsize=6, handlelength=1.4, labelspacing=0.35, borderpad=0.5)


def key_row_count(anchors: pd.DataFrame, themes: dict, ncols: int = 3) -> int:
    """Rows the numbered key needs: each theme's header plus its entries, packed into `ncols` columns."""
    lines = sum(1 + (anchors["theme"] == t).sum() for t in themes if (anchors["theme"] == t).any())
    return -(-lines // ncols) + 1


def new_detail_map(box, *, key_rows: int, header_in: float = 0.75, footer_in: float = 0.45, key_row_in: float = 0.16):
    """A figure framed on `box` (MAP_CRS polygon) with a key panel under the map."""
    minx, miny, maxx, maxy = box.bounds
    width_in = EXPORT_WIDTH_PX / EXPORT_DPI
    map_h = width_in * (maxy - miny) / (maxx - minx)
    key_h = key_rows * key_row_in
    height_in = header_in + map_h + key_h + footer_in
    fig = plt.figure(figsize=(width_in, height_in), dpi=EXPORT_DPI)
    fig.patch.set_facecolor(color("neutral.background_white"))
    ax = fig.add_axes((0, (footer_in + key_h) / height_in, 1, map_h / height_in))
    ax.set_axis_off()
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_aspect("equal")
    key_ax = fig.add_axes((0.02, footer_in / height_in, 0.96, key_h / height_in))
    key_ax.set_axis_off()
    return fig, ax, key_ax


def draw_numbered_anchors(ax, anchors: gpd.GeoDataFrame, themes: dict, *, offsets: dict) -> pd.DataFrame:
    """Numbered circles in theme colors, numbered in theme order then west to east. Returns the numbering."""
    order = {t: i for i, t in enumerate(themes)}
    numbered = anchors.assign(_t=anchors["theme"].map(order), _x=anchors.geometry.x).sort_values(["_t", "_x"]).reset_index(drop=True)
    numbered["number"] = range(1, len(numbered) + 1)
    for row in numbered.itertuples():
        offset = offsets.get(row.name, (0, 0))
        x, y = row.geometry.x, row.geometry.y
        if offset != (0, 0):
            ax.annotate("", (x, y), xytext=offset, textcoords="offset points",
                        arrowprops={"arrowstyle": "-", "color": themes[row.theme][0], "linewidth": 0.6}, zorder=13)
        ax.annotate(str(row.number), (x, y), xytext=offset, textcoords="offset points", ha="center", va="center",
                    fontsize=5.6, fontweight="bold", color="white", zorder=15,
                    bbox={"boxstyle": "circle,pad=0.25", "facecolor": themes[row.theme][0], "edgecolor": "white", "linewidth": 0.6})
    return numbered


def draw_anchor_key(ax, numbered: pd.DataFrame, themes: dict, *, ncols: int = 3) -> None:
    """The numbered key, grouped by theme, filled column by column."""
    lines = []
    for theme, (fill, _marker) in themes.items():
        part = numbered.loc[numbered["theme"] == theme]
        if part.empty:
            continue
        lines.append((theme, fill, True))
        lines += [(f"{r.number}  {r.name}", fill, False) for r in part.itertuples()]
    per_col = -(-len(lines) // ncols)
    for i, (text, fill, is_header) in enumerate(lines):
        col, row = divmod(i, per_col)
        ax.text(col / ncols, 1 - (row + 0.5) / (per_col + 1), text, transform=ax.transAxes, ha="left", va="center",
                fontsize=6.4 if is_header else 6.2, fontweight="bold" if is_header else "normal",
                color=fill if is_header else color("neutral.text"))


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


def load_tract_profile(con) -> gpd.GeoDataFrame:
    """Metro tracts with raw ACS metrics, zone type, county and main place, with geometry."""
    return to_geo(run_sql(con, SQL_DIR / "metro_tract_profile.sql", cbsa_code=CBSA_CODE)).assign(
        # A tract belongs to a place only when the place holds most of its population.
        place=lambda df: df["main_place"].where(df["main_place_weight"] >= 0.5, "Town area (no place)")
    )


def all_jobs_centers(con) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Q2's center method, unchanged, on all jobs (JT00) for this metro, and the published private-jobs centers.
    Returns (candidates, components, private, checks); the caller asserts the checks."""
    tracts = run_sql(con, SQL_DIR / "q2_tracts_all_jobs.sql", cbsa_code=CBSA_CODE)
    geometry = pd.DataFrame({"tract_geoid": tracts["tract_geoid"], "geometry": shapely.from_wkb(tracts.pop("geom_wkb").map(bytes))})
    tracts["market_jobs_total"] = tracts.groupby("cbsa_code")["jobs_total"].transform("sum")
    candidates, components = apply_method(tracts, geometry)
    private = con.sql(
        f"SELECT tract_geoid, is_recommended_center AS private_center, recommended_cluster_id AS private_component "
        f"FROM mart_explanation_q2.job_center_candidates_v0 WHERE cbsa_code = '{CBSA_CODE}'"
    ).df()
    checks = pd.DataFrame({
        "check": ["251 tracts", "all jobs = 460,466", "private centers (mart) = 14 components"],
        "value": [len(candidates), f"{candidates['jobs_total'].sum():,.0f}", private["private_component"].nunique()],
        "passed": [len(candidates) == 251, candidates["jobs_total"].sum() == 460_466, private["private_component"].nunique() == 14],
    })
    return candidates, components, private, checks


def irs_flows_reversed(con) -> bool:
    """True if silver.irs_migration_flows stores origin and destination reversed: New York State would then gain
    people from other states in 2022 (it lost them). Fixed 2026-10-26; the notebooks assert this stays False.
    Foundations has the same guard: foundations/etl/gold/check_irs_migration_direction.sql."""
    into, out = con.sql(
        "SELECT sum(n_exemptions) FILTER (WHERE dest_state_fips = '36' AND origin_state_fips <> '36'), "
        "sum(n_exemptions) FILTER (WHERE origin_state_fips = '36' AND dest_state_fips <> '36') "
        "FROM silver.irs_migration_flows WHERE year = 2022"
    ).fetchone()
    return into > out


def classify_migration(flows: pd.DataFrame, xwalk: pd.DataFrame, upstate_counties: set) -> pd.DataFrame:
    """Tag the other end of each flow: Downstate NY, Upstate NY (outside the metro, by construction) or another state."""
    out = flows.merge(xwalk, left_on="other_county_geoid", right_on="county_geoid", how="left").drop(columns="county_geoid")
    is_ny = out["other_county_geoid"].str.startswith("36")
    out["region"] = np.where(~is_ny, "Other states", np.where(out["other_county_geoid"].isin(upstate_counties), "Upstate NY", "Downstate NY"))
    return out


def migration_summary(mig: pd.DataFrame, pop: pd.Series, names: dict, *, years: int) -> pd.DataFrame:
    """Per metro: annual-average people in, out and net, by region of the other end, per 1,000 residents, and mover AGI."""
    rows = []
    for code, name in names.items():
        part = mig.loc[mig["cbsa_code"] == code]
        row = {"metro": name}
        for region in ["Downstate NY", "Upstate NY", "Other states"]:
            r = part.loc[part["region"] == region]
            inn = r.loc[r["direction"] == "in", "people"].sum() / years
            out = r.loc[r["direction"] == "out", "people"].sum() / years
            row[f"net {region}"] = round(inn - out)
            row[f"in {region}"] = round(inn)
        inn = part.loc[part["direction"] == "in", "people"].sum() / years
        out = part.loc[part["direction"] == "out", "people"].sum() / years
        row.update({"in total": round(inn), "out total": round(out), "net total": round(inn - out),
                    "net per 1,000": round(1000 * (inn - out) / pop[code], 2),
                    "in from NY share": round(part.loc[(part["direction"] == "in") & (part["region"] != "Other states"), "people"].sum()
                                              / part.loc[part["direction"] == "in", "people"].sum(), 3)})
        for direction in ["in", "out"]:
            d = part.loc[part["direction"] == direction]
            row[f"avg_agi_{direction}"] = round(d["agi"].sum() / d["households"].sum())
        rows.append(row)
    return pd.DataFrame(rows)


def tract_activity(counts: pd.DataFrame, base: pd.DataFrame, *, shrink: float, jobs_cut: float, destination_lift: float,
                   industrial_lift: float, activity_cut: float | None = None) -> pd.DataFrame:
    """One activity class per tract, by plain rules, first match wins:
    1. Jobs per resident >= jobs_cut: Destination if the destination lift clears destination_lift, else Employment
       and industrial.
    2. POIs per 1,000 residents below activity_cut (default: the metro median): Residential.
    3. Destination or industrial lift clears its bar: that class (the larger lift relative to its bar wins).
    4. Otherwise: Local-serving.
    Lift = the tract's bundle share over the metro's. Shares are pulled toward the metro mix by `shrink` pseudo-POIs,
    so a tract with few POIs can't swing on one listing. Unclassified and Residential POIs are dropped."""
    wide = counts.pivot_table(index="tract_geoid", columns="category", values="pois", aggfunc="sum", fill_value=0)
    wide = wide.drop(columns=[c for c in ("Unclassified", "Residential") if c in wide])
    total = wide.sum(axis=1)
    bundles = pd.DataFrame({b: wide.reindex(columns=cats, fill_value=0).sum(axis=1) for b, cats in ACTIVITY_BUNDLES.items()})
    metro_share = bundles.sum() / total.sum()
    share = (bundles + shrink * metro_share).div(total + shrink, axis=0)
    lift = share / metro_share

    out = base.set_index("tract_geoid").join(total.rename("pois")).join(share.add_prefix("share_")).join(lift.add_prefix("lift_"))
    out["pois"] = out["pois"].fillna(0)
    out[share.add_prefix("share_").columns] = out[share.add_prefix("share_").columns].fillna(metro_share.add_prefix("share_"))
    out[lift.add_prefix("lift_").columns] = out[lift.add_prefix("lift_").columns].fillna(1.0)
    residents = out["residents"].clip(lower=100)  # a floor so near-empty tracts don't divide by almost nothing
    out["pois_per_1k"] = 1000 * out["pois"] / residents
    out["pois_per_sqmi"] = out["pois"] / out["land_area_sqmi"]
    out["jobs_per_resident"] = out["jobs"].fillna(0) / residents
    cut = out["pois_per_1k"].median() if activity_cut is None else activity_cut

    def classify(r):
        if r.jobs_per_resident >= jobs_cut:
            return "Destination" if r.lift_destination >= destination_lift else "Employment and industrial"
        if r.pois_per_1k < cut:
            return "Residential"
        d, i = r.lift_destination / destination_lift, r.lift_industrial / industrial_lift
        if max(d, i) >= 1:
            return "Destination" if d >= i else "Employment and industrial"
        return "Local-serving"

    out["activity"] = out.apply(classify, axis=1)
    return out.reset_index()


def short_metro(name: str) -> str:
    """'Albany-Schenectady-Troy, NY' -> 'Albany, NY'; 'Providence-Warwick, RI-MA' -> 'Providence, RI'."""
    city, states = name.split(", ")
    if city.startswith("Kiryas Joel"):
        return "Poughkeepsie, NY"
    return f"{city.split('-')[0]}, {states.split('-')[0]}"


def classify(values: pd.Series, classes: dict) -> pd.Series:
    """Values -> class names, from {name: (low, high, fill)} with low <= value < high."""
    out = pd.Series(pd.NA, index=values.index, dtype="object")
    for name, (low, high, _fill) in classes.items():
        out[(values >= low) & (values < high)] = name
    return out


def new_box_map(box, *, header_in: float = 0.75, footer_in: float = 0.45):
    """A figure framed on `box` (MAP_CRS polygon), no key panel."""
    minx, miny, maxx, maxy = box.bounds
    width_in = EXPORT_WIDTH_PX / EXPORT_DPI
    map_h = width_in * (maxy - miny) / (maxx - minx)
    height_in = header_in + map_h + footer_in
    fig = plt.figure(figsize=(width_in, height_in), dpi=EXPORT_DPI)
    fig.patch.set_facecolor(color("neutral.background_white"))
    ax = fig.add_axes((0, footer_in / height_in, 1, map_h / height_in))
    ax.set_facecolor(color("neutral.background_white"))
    ax.set_axis_off()
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    ax.set_aspect("equal")
    return fig, ax


def draw_tract_classes(ax, tracts: gpd.GeoDataFrame, column: str, colors: dict, *, counts: bool = False,
                       title: str | None = None) -> None:
    """Tracts filled by a categorical column. With `counts`, a legend of the classes present with tract counts."""
    tracts.plot(ax=ax, color=tracts[column].map(colors).fillna("#FFFFFF"), edgecolor="white", linewidth=0.15, zorder=2)
    if counts:
        n = tracts[column].value_counts()
        handles = [Patch(facecolor=fill, label=f"{name} ({n[name]})") for name, fill in colors.items() if name in n]
        ax.legend(handles=handles, loc="upper left", frameon=True, facecolor="white", edgecolor="none", framealpha=0.85,
                  fontsize=6.8, title=title, title_fontsize=7.2, alignment="left")


def chart_figure(height_in: float):
    fig = plt.figure(figsize=(EXPORT_WIDTH_PX / EXPORT_DPI, height_in), dpi=EXPORT_DPI)
    fig.patch.set_facecolor(color("neutral.background_white"))
    return fig


def style_axes(ax) -> None:
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(color("neutral.border"))
    ax.tick_params(colors=color("neutral.text_muted"), labelsize=7, length=0)
    ax.grid(axis="y", color=color("neutral.grid_major"), linewidth=0.5)
    ax.set_axisbelow(True)


def draw_text_table(columns: list, rows: list, *, row_styles: list, top_in: float = 0.8, header_in: float = 0.5,
                    row_in: float = 0.3, footer_in: float = 0.7, shading: list | None = None):
    """A printed table. `columns`: (header, x, align); `rows`: lists of cell text; `row_styles`: per row, a dict with
    optional 'bold', 'fill' (row background) and 'color'. `shading`: per row, per cell, an optional cell fill."""
    n = len(rows)
    height_in = top_in + header_in + n * row_in + footer_in
    fig = chart_figure(height_in)

    def y_of(inches):
        return 1 - inches / height_in

    for header, x, ha in columns:
        fig.text(x, y_of(top_in + header_in - 0.06), header, ha=ha, va="bottom", fontsize=7.4, fontweight="bold",
                 color=color("neutral.text"), linespacing=1.1)
    fig.add_artist(plt.Line2D([0.02, 0.98], [y_of(top_in + header_in)] * 2, color=color("neutral.text"), linewidth=0.8))
    edges = [c[1] for c in columns]
    for r, (cells, style) in enumerate(zip(rows, row_styles)):
        y0 = top_in + header_in + r * row_in
        if style.get("fill"):
            fig.add_artist(plt.Rectangle((0.02, y_of(y0 + row_in)), 0.96, row_in / height_in, transform=fig.transFigure,
                                         facecolor=style["fill"], edgecolor="none", zorder=0))
        for c, (text, (_header, x, ha)) in enumerate(zip(cells, columns)):
            cell_fill = shading[r][c] if shading else None
            if cell_fill:
                left = x - 0.005 if ha == "left" else max(edges[c - 1] + 0.01 if c else 0.02, x - 0.12)
                fig.add_artist(plt.Rectangle((left, y_of(y0 + row_in) + 0.002), x + 0.008 - left if ha != "left" else 0.1,
                                             row_in / height_in - 0.004, transform=fig.transFigure, facecolor=cell_fill,
                                             edgecolor="none", zorder=0))
            fig.text(x, y_of(y0 + row_in / 2), tex_safe(text), ha=ha, va="center", fontsize=7.6,
                     fontweight="bold" if style.get("bold") else "normal", color=style.get("color", color("neutral.text")))
        fig.add_artist(plt.Line2D([0.02, 0.98], [y_of(y0 + row_in)] * 2, color=color("neutral.grid_major"), linewidth=0.5))
    return fig
