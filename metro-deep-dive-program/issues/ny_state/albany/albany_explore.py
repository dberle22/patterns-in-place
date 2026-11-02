"""Exploration helpers for the Albany pieces: quick tables, zoomable Plotly maps and picker charts.

Imported by the exploration notebooks (ALBANY_LENS1_EXPLORATION.py, ALBANY_LENS2_EXPLORATION.py, and later
lenses). Nothing here is styled for print. Print helpers live in ALBANY_LENS1_VISUALS.py; when a print exhibit
uses one of these, it moves there (move, don't copy). Promote to a shared module when another market reuses
them unchanged (NATIONAL_FOLLOWUPS N10).
"""

import json
import math
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.colors as plotly_colors
import plotly.graph_objects as go

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ALBANY_LENS1_VISUALS import (  # noqa: E402
    CBSA_CODE,
    NYC_CBSA_CODE,
    SQL_DIR,
    color,
    county_short_name,
    format_metric,
    metro_wide,
    position_words,
    run_sql,
    short_cbsa,
)
# Moved to the visuals notebook when their exhibits were promoted (move, don't copy); re-exported here so the
# exploration notebooks keep importing them from this module.
from ALBANY_LENS1_VISUALS import (  # noqa: E402, F401
    ACTIVITY_BUNDLES,
    ACTIVITY_COLORS,
    ACTIVITY_ORDER,
    all_jobs_centers,
    classify_migration,
    irs_flows_reversed,
    load_tract_profile,
    migration_summary,
    tract_activity,
)

# Albany city center, for distances from county centroids.
ALBANY_LONLAT = (-73.7562, 42.6526)
# The four cities, for map overlays and place tables.
FOUR_CITIES = ("Albany", "Schenectady", "Troy", "Saratoga Springs")
# Web maps are simplified to keep each cell's output under marimo's 8 MB default
# (runtime.output_max_bytes; MARIMO_OUTPUT_MAX_BYTES). explore_map warns above this.
MAP_OUTPUT_WARN_BYTES = 6_000_000
# Category colors for the interactive maps (Plotly's qualitative sets, enough for ~20 categories).
QUALITATIVE_COLORS = plotly_colors.qualitative.Set2 + plotly_colors.qualitative.Dark2 + plotly_colors.qualitative.Pastel1


# ---- Shared data loaders ----


def load_commute_flows(con) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """2023 LODES county OD touching the metro, and every county's resident and workplace jobs with miles from
    Albany. Returns (flows, totals, checks); the caller asserts the checks."""
    flows = run_sql(con, SQL_DIR / "county_commute_flows.sql", cbsa_code=CBSA_CODE)
    totals = run_sql(con, SQL_DIR / "county_commute_totals.sql").assign(
        miles=lambda df: [miles_from_albany(lon, lat) for lon, lat in zip(df["lon"], df["lat"])]
    )
    member_total = totals.loc[totals["cbsa_code"] == CBSA_CODE, "resident_jobs"].sum()
    from_flows = flows.loc[flows["home_flag"].notna(), "jobs"].sum()
    checks = pd.DataFrame(
        {
            "check": ["metro resident jobs: flows = county totals", "counties with totals"],
            "value": [f"{from_flows:,.0f} vs {member_total:,.0f}", len(totals)],
            "passed": [abs(from_flows - member_total) < 1, len(totals) > 3000],
        }
    )
    return flows, totals, checks


# ---- Interactive maps ----


def web_geometry(gdf: gpd.GeoDataFrame, tolerance: float = 0.0003) -> gpd.GeoDataFrame:
    """Lon/lat geometry, simplified for web maps (keeps each cell's output well under marimo's 8 MB)."""
    out = gdf.to_crs("EPSG:4326").copy()
    out["geometry"] = out.geometry.simplify(tolerance, preserve_topology=True)
    return out


def outline_trace(gdf: gpd.GeoDataFrame, name: str, line_color: str, width: float = 1.5, *, shown: bool = True,
                  tolerance: float = 0.0003):
    """Polygon edges (or lines) as one map line trace. Click its legend entry to toggle it."""
    lon, lat = [], []
    for geom in web_geometry(gdf[["geometry"]], tolerance).geometry:
        if geom is None or geom.is_empty:
            continue
        edges = geom.boundary if geom.geom_type in ("Polygon", "MultiPolygon") else geom
        for part in getattr(edges, "geoms", [edges]):
            xs, ys = part.xy
            lon += [round(v, 5) for v in xs] + [None]
            lat += [round(v, 5) for v in ys] + [None]
    return go.Scattermap(lon=lon, lat=lat, mode="lines", name=name, line={"color": line_color, "width": width},
                         hoverinfo="skip", visible=True if shown else "legendonly")


def map_overlays(layers: dict, places: gpd.GeoDataFrame | None = None, *, extra: dict | None = None) -> list:
    """Standard toggleable overlays: county lines, the metro outline, the four cities, other places (off),
    plus `extra` as name -> (GeoDataFrame, color, shown). Built fresh per figure."""
    traces = [
        outline_trace(layers["counties"], "County lines", "#52606D", 1.0),
        outline_trace(layers["outline"], "Metro outline", "#1F2933", 2.2),
    ]
    if places is not None:
        four = places["place_name"].isin(FOUR_CITIES) & (places["place_kind"] == "city")
        traces.append(outline_trace(places.loc[four], "Four cities", "#7B2CBF", 1.8))
        traces.append(outline_trace(places.loc[~four], "Other places (cities, CDPs, villages)", "#7B8794", 0.8, shown=False))
    for name, (gdf, line_color, shown) in (extra or {}).items():
        traces.append(outline_trace(gdf, name, line_color, 1.6, shown=shown))
    return traces


def warn_if_large(fig, title: str) -> None:
    size = len(fig.to_json())
    if size > MAP_OUTPUT_WARN_BYTES:
        warnings.warn(f"{title}: {size / 1e6:.1f} MB of output; marimo's default cell limit is 8 MB. Simplify more or filter.")


def explore_map(polys: gpd.GeoDataFrame, value: str, *, id_col: str, hover: dict, title: str, name_col: str | None = None,
                labels: dict | None = None, colorscale: str = "Blues", tickformat: str | None = None, overlays=(),
                clip: tuple = (0.02, 0.98), zoom: float = 8.4, height: int = 680, tolerance: float = 0.0003,
                symmetric: bool = False):
    """Zoomable choropleth on a Carto basemap, with toggleable overlays (legend). `hover`: column -> format string
    ("{:.1%}"); `labels`: column -> display name. Colors clip at the `clip` quantiles so outliers don't flatten it."""
    labels = labels or {}
    name_col = name_col or id_col
    columns = list(dict.fromkeys([id_col, name_col, value, *hover]))
    shapes = web_geometry(gpd.GeoDataFrame(polys[columns], geometry=polys.geometry).reset_index(drop=True), tolerance)
    geojson = json.loads(shapes[[id_col, "geometry"]].set_index(id_col).to_json())
    z = shapes[value].astype(float)
    text = [
        "<br>".join([f"<b>{row[name_col]}</b>"] + [
            f"{labels.get(col, col)}: {fmt.format(row[col]) if pd.notna(row[col]) else '—'}" for col, fmt in hover.items()
        ])
        for _, row in shapes.iterrows()
    ]
    choropleth = go.Choroplethmap(
        geojson=geojson, locations=shapes[id_col], featureidkey="id", z=z,
        zmin=-z.abs().quantile(clip[1]) if symmetric else z.quantile(clip[0]),
        zmax=z.abs().quantile(clip[1]) if symmetric else z.quantile(clip[1]), colorscale=colorscale,
        marker={"opacity": 0.72, "line": {"width": 0.3, "color": "white"}},
        text=text, hovertemplate="%{text}<extra></extra>", showlegend=False,
        colorbar={"title": {"text": labels.get(value, value)}, "tickformat": tickformat, "thickness": 12, "len": 0.6},
    )
    minx, miny, maxx, maxy = shapes.total_bounds
    fig = go.Figure([choropleth, *overlays])
    fig.update_layout(
        title={"text": title, "x": 0.01, "font": {"size": 14}}, height=height, margin={"l": 0, "r": 0, "t": 40, "b": 0},
        map={"style": "carto-positron", "center": {"lon": (minx + maxx) / 2, "lat": (miny + maxy) / 2}, "zoom": zoom},
        legend={"x": 0.01, "y": 0.99, "bgcolor": "rgba(255,255,255,0.85)", "font": {"size": 11}},
    )
    warn_if_large(fig, title)
    return fig


def explore_category_map(polys: gpd.GeoDataFrame, category: str, *, id_col: str, hover: dict, title: str,
                         name_col: str | None = None, labels: dict | None = None, colors: dict | None = None,
                         order: list | None = None, overlays=(), zoom: float = 8.4, height: int = 680,
                         tolerance: float = 0.0003, opacity: float = 0.7):
    """Categorical choropleth on a Carto basemap: one trace per category, so each toggles in the legend."""
    labels = labels or {}
    name_col = name_col or id_col
    columns = list(dict.fromkeys([id_col, name_col, category, *hover]))
    shapes = web_geometry(gpd.GeoDataFrame(polys[columns], geometry=polys.geometry).reset_index(drop=True), tolerance)
    order = order or shapes[category].value_counts().index.tolist()
    palette = QUALITATIVE_COLORS
    traces = []
    for i, group in enumerate(order):
        part = shapes.loc[shapes[category] == group]
        if part.empty:
            continue
        fill = (colors or {}).get(group, palette[i % len(palette)])
        text = ["<br>".join([f"<b>{row[name_col]}</b>"] + [
            f"{labels.get(col, col)}: {fmt.format(row[col]) if pd.notna(row[col]) else '—'}" for col, fmt in hover.items()
        ]) for _, row in part.iterrows()]
        traces.append(go.Choroplethmap(
            geojson=json.loads(part[[id_col, "geometry"]].set_index(id_col).to_json()), locations=part[id_col],
            featureidkey="id", z=[1] * len(part), colorscale=[[0, fill], [1, fill]], showscale=False,
            marker={"opacity": opacity, "line": {"width": 0.3, "color": "white"}}, name=f"{group} ({len(part)})",
            showlegend=True, text=text, hovertemplate="%{text}<extra></extra>",
        ))
    minx, miny, maxx, maxy = shapes.total_bounds
    fig = go.Figure([*traces, *overlays])
    fig.update_layout(
        title={"text": title, "x": 0.01, "font": {"size": 14}}, height=height, margin={"l": 0, "r": 0, "t": 40, "b": 0},
        map={"style": "carto-positron", "center": {"lon": (minx + maxx) / 2, "lat": (miny + maxy) / 2}, "zoom": zoom},
        legend={"x": 0.01, "y": 0.99, "bgcolor": "rgba(255,255,255,0.85)", "font": {"size": 11}},
    )
    warn_if_large(fig, title)
    return fig


def explore_points(points: pd.DataFrame, *, color_col: str, hover: list, title: str, overlays=(), zoom: float = 8.4,
                   height: int = 680, size: int = 5):
    """Point map on a Carto basemap: one trace per `color_col` value (toggle in the legend), overlays below."""
    palette = plt.get_cmap("tab10").colors
    fig = go.Figure(list(overlays))
    for i, (group, part) in enumerate(points.groupby(color_col)):
        rgb = palette[i % len(palette)]
        fig.add_trace(go.Scattermap(
            lon=part["longitude"].round(5), lat=part["latitude"].round(5), mode="markers", name=f"{group} ({len(part):,})",
            marker={"size": size, "color": f"rgb({rgb[0] * 255:.0f},{rgb[1] * 255:.0f},{rgb[2] * 255:.0f})", "opacity": 0.7},
            text=["<br>".join(str(v) for v in row) for row in part[hover].itertuples(index=False)],
            hovertemplate="%{text}<extra></extra>",
        ))
    fig.update_layout(
        title={"text": title, "x": 0.01, "font": {"size": 14}}, height=height, margin={"l": 0, "r": 0, "t": 40, "b": 0},
        map={"style": "carto-positron", "center": {"lon": points["longitude"].median(), "lat": points["latitude"].median()},
             "zoom": zoom},
        legend={"x": 0.01, "y": 0.99, "bgcolor": "rgba(255,255,255,0.85)", "font": {"size": 11}},
    )
    warn_if_large(fig, title)
    return fig


# ---- Distances ----


def miles_from_albany(lon: float, lat: float) -> float:
    """Great-circle miles from Albany city center."""
    lon0, lat0 = map(math.radians, ALBANY_LONLAT)
    lon1, lat1 = math.radians(lon), math.radians(lat)
    a = math.sin((lat1 - lat0) / 2) ** 2 + math.cos(lat0) * math.cos(lat1) * math.sin((lon1 - lon0) / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(a))


def haversine_miles(lon1, lat1, lon2, lat2):
    """Vectorized great-circle miles."""
    lon1, lat1, lon2, lat2 = (np.radians(np.asarray(v, dtype=float)) for v in (lon1, lat1, lon2, lat2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 3958.8 * 2 * np.arcsin(np.sqrt(a))


def weighted_median(values: pd.Series, weights: pd.Series) -> float:
    order = np.argsort(values.to_numpy())
    v, w = values.to_numpy()[order], weights.to_numpy()[order]
    return float(v[np.searchsorted(np.cumsum(w), w.sum() / 2)])


# ---- Commuting: county and place OD (Lens 1 belonging test; Lens 2) ----


def member_destinations(flows: pd.DataFrame) -> pd.DataFrame:
    """For each metro county: shares of its residents' jobs by destination type, and its top outside destination."""
    home = flows.loc[flows["home_flag"].notna()].copy()
    rows = []
    for (geoid, name, flag), group in home.groupby(["home_county_geoid", "home_county_name", "home_flag"]):
        total = group["jobs"].sum()
        own = group["work_county_geoid"] == geoid
        outside = group.loc[group["work_flag"].isna()]
        top = outside.groupby("work_county_name")["jobs"].sum().sort_values(ascending=False)
        rows.append({
            "county": county_short_name(name),
            "flag": flag,
            "resident_jobs": total,
            "own_county": group.loc[own, "jobs"].sum() / total,
            "other_central": group.loc[~own & (group["work_flag"] == "Central"), "jobs"].sum() / total,
            "other_outlying": group.loc[~own & (group["work_flag"] == "Outlying"), "jobs"].sum() / total,
            "outside_metro": outside["jobs"].sum() / total,
            "top_outside": f"{top.index[0]} ({top.iloc[0] / total:.1%})",
        })
    return pd.DataFrame(rows).sort_values(["flag", "county"]).reset_index(drop=True).round(3)


def inbound_table(flows: pd.DataFrame, totals: pd.DataFrame) -> pd.DataFrame:
    """Counties outside the metro: jobs their residents hold in the metro and in its core, as shares."""
    into = flows.loc[flows["home_flag"].isna()]
    by_home = pd.DataFrame({
        "jobs_to_metro": into.groupby("home_county_geoid")["jobs"].sum(),
        "private_to_metro": into.groupby("home_county_geoid")["private_jobs"].sum(),
        "jobs_to_core": into.loc[into["work_flag"] == "Central"].groupby("home_county_geoid")["jobs"].sum(),
    }).fillna(0)
    table = totals.set_index("county_geoid").join(by_home, how="inner").reset_index()
    return (
        table.assign(
            county=lambda df: df["county_name"] + ", " + df["state_abbr"],
            share_to_metro=lambda df: df["jobs_to_metro"] / df["resident_jobs"],
            share_to_core=lambda df: df["jobs_to_core"] / df["resident_jobs"],
            meets_25pct_core=lambda df: df["share_to_core"] >= 0.25,
        )[["county_geoid", "county", "cbsa_name", "county_flag", "csa_name", "miles", "resident_jobs",
           "jobs_to_metro", "share_to_metro", "jobs_to_core", "share_to_core", "meets_25pct_core",
           "private_to_metro"]]
        .sort_values("jobs_to_metro", ascending=False)
        .reset_index(drop=True)
    )


def outbound_table(flows: pd.DataFrame, totals: pd.DataFrame) -> pd.DataFrame:
    """Counties outside the metro where metro residents work: jobs, shares both ways, and the top sending county."""
    out = flows.loc[flows["home_flag"].notna() & flows["work_flag"].isna()]
    metro_residents = flows.loc[flows["home_flag"].notna(), "jobs"].sum()
    senders = out.groupby(["work_county_geoid", "home_county_name"])["jobs"].sum().reset_index()
    top = senders.sort_values("jobs", ascending=False).drop_duplicates("work_county_geoid").set_index("work_county_geoid")
    by_work = out.groupby("work_county_geoid")["jobs"].sum().rename("metro_resident_jobs")
    table = totals.set_index("county_geoid").join(by_work, how="inner")
    table["top_sender"] = [
        f"{county_short_name(top.loc[g, 'home_county_name'])} ({top.loc[g, 'jobs'] / j:.0%})"
        for g, j in zip(table.index, table["metro_resident_jobs"])
    ]
    return (
        table.reset_index()
        .assign(
            county=lambda df: df["county_name"] + ", " + df["state_abbr"],
            share_of_metro_residents=lambda df: df["metro_resident_jobs"] / metro_residents,
            share_of_county_jobs=lambda df: df["metro_resident_jobs"] / df["workplace_jobs"],
        )[["county_geoid", "county", "cbsa_name", "miles", "workplace_jobs", "metro_resident_jobs",
           "share_of_metro_residents", "share_of_county_jobs", "top_sender"]]
        .sort_values("metro_resident_jobs", ascending=False)
        .reset_index(drop=True)
    )


def external_metro_pull(by_cbsa: pd.DataFrame, exclude: set = frozenset()) -> pd.DataFrame:
    """Per NY home county: own-CBSA share, Albany share, and the top CBSA outside its own (minus `exclude`)."""
    df = by_cbsa
    totals = df.groupby("home_county_geoid")["jobs"].sum().rename("resident_jobs")
    own = df.loc[df["work_cbsa_code"] == df["home_cbsa_code"]].groupby("home_county_geoid")["jobs"].sum().rename("own_cbsa_jobs")
    albany = df.loc[df["work_cbsa_code"] == CBSA_CODE].groupby("home_county_geoid")["jobs"].sum().rename("albany_jobs")
    external = df.loc[
        (df["work_cbsa_code"] != df["home_cbsa_code"].fillna("")) & (df["work_cbsa_code"] != "none")
        & ~df["work_cbsa_code"].isin(exclude)
    ]
    top = (
        external.groupby(["home_county_geoid", "work_cbsa_code", "work_cbsa_name"])["jobs"].sum().reset_index()
        .sort_values("jobs", ascending=False).drop_duplicates("home_county_geoid").set_index("home_county_geoid")
    )
    out = pd.concat([totals, own, albany], axis=1).fillna(0).join(top)
    return (
        out.assign(
            own_cbsa_share=lambda d: d["own_cbsa_jobs"] / d["resident_jobs"],
            albany_share=lambda d: d["albany_jobs"] / d["resident_jobs"],
            top_external=lambda d: d["work_cbsa_name"].map(short_cbsa, na_action="ignore"),
            top_external_code=lambda d: d["work_cbsa_code"],
            top_external_share=lambda d: d["jobs"] / d["resident_jobs"],
        )[["resident_jobs", "own_cbsa_share", "albany_share", "top_external", "top_external_code", "top_external_share"]]
        .rename_axis("home_county_geoid").reset_index()
    )


def metro_reach(by_cbsa: pd.DataFrame, metro_jobs: pd.Series) -> pd.DataFrame:
    """For each metro with NY counties: jobs held by residents of other NY counties, as a share of the
    metro's jobs (`metro_jobs`: all jobs by CBSA code), and how many of those counties send 5/10/25%+."""
    totals = by_cbsa.groupby("home_county_geoid")["jobs"].sum()
    outside = by_cbsa.loc[
        (by_cbsa["work_cbsa_code"] != by_cbsa["home_cbsa_code"].fillna(""))
        & (by_cbsa["work_cbsa_type"] == "Metropolitan Statistical Area")
        & by_cbsa["work_cbsa_name"].str.contains("NY")
    ]
    per_county = outside.groupby(["work_cbsa_code", "work_cbsa_name", "home_county_geoid"])["jobs"].sum().reset_index()
    per_county["share"] = per_county["jobs"] / per_county["home_county_geoid"].map(totals)
    return (
        per_county.groupby(["work_cbsa_code", "work_cbsa_name"])
        .agg(
            jobs_held_by_other_ny_residents=("jobs", "sum"),
            counties_5pct=("share", lambda x: int((x >= 0.05).sum())),
            counties_10pct=("share", lambda x: int((x >= 0.10).sum())),
            counties_25pct=("share", lambda x: int((x >= 0.25).sum())),
        )
        .reset_index()
        .assign(
            metro_jobs=lambda d: d["work_cbsa_code"].map(metro_jobs),
            share_of_metro_jobs=lambda d: (d["jobs_held_by_other_ny_residents"] / d["metro_jobs"]).round(3),
        )
        .sort_values("counties_5pct", ascending=False)
        .reset_index(drop=True)
    )


def county_matrix(flows: pd.DataFrame) -> pd.DataFrame:
    """Rows: metro home counties. Columns: metro work counties plus 'Outside metro'. Shares of resident jobs."""
    home = flows.loc[flows["home_flag"].notna()].assign(
        home=lambda d: d["home_county_name"].map(county_short_name),
        work=lambda d: d["work_county_name"].map(county_short_name).where(d["work_flag"].notna(), "Outside metro"),
    )
    matrix = home.pivot_table(index="home", columns="work", values="jobs", aggfunc="sum", fill_value=0)
    matrix = matrix.div(matrix.sum(axis=1), axis=0)
    order = ["Albany", "Rensselaer", "Schenectady", "Saratoga", "Schoharie"]
    return matrix.loc[order, order + ["Outside metro"]].round(3)


def city_matrix(flows: pd.DataFrame, cities: dict, *, side: str) -> pd.DataFrame:
    """side='home': where each city's residents work. side='work': where each city's job holders live. Shares."""
    key, other = ("home", "work") if side == "home" else ("work", "home")
    names = {geoid: name for name, geoid in cities.items()}
    rows = {}
    for name, geoid in cities.items():
        part = flows.loc[flows[f"{key}_place_geoid"] == geoid]
        label = np.where(
            part[f"{other}_place_geoid"].isin(names),
            part[f"{other}_place_geoid"].map(names),
            np.where(part[f"{other}_place_status"] == "matched", "Other places", "Outside any place"),
        )
        rows[name] = part.groupby(label)["jobs"].sum() / part["jobs"].sum()
    columns = list(cities) + ["Other places", "Outside any place"]
    return pd.DataFrame(rows).T.reindex(columns=columns).fillna(0).round(3)


# ---- Job centers and sheds (Q2, Lens 2 Q1h) ----


def compare_centers(all_jobs: pd.DataFrame, private: pd.DataFrame, tracts: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Every tract with all-jobs and private center status, public share, place, and geometry."""
    merged = all_jobs[["tract_geoid", "jobs_total", "private_jobs", "workers_total", "is_recommended_center", "recommended_cluster_id"]].merge(
        private, on="tract_geoid", how="left"
    )
    merged["status"] = np.select(
        [merged["is_recommended_center"] & merged["private_center"], merged["is_recommended_center"], merged["private_center"]],
        ["Center in both", "Center on all jobs only", "Center on private jobs only"],
        default="Not a center",
    )
    merged["public_share"] = 1 - merged["private_jobs"] / merged["jobs_total"]
    out = tracts[["tract_geoid", "place", "county_name", "geometry"]].merge(merged, on="tract_geoid")
    return out[["tract_geoid", "place", "county_name", "status", "jobs_total", "private_jobs", "public_share",
                "workers_total", "recommended_cluster_id", "private_component", "geometry"]].sort_values("jobs_total", ascending=False)


def component_summary(candidates: pd.DataFrame, tracts: gpd.GeoDataFrame) -> pd.DataFrame:
    """Per all-jobs component: tracts, jobs, public share, places (by tract count)."""
    centers = candidates.loc[candidates["is_recommended_center"]].merge(tracts[["tract_geoid", "place"]], on="tract_geoid")
    return (
        centers.groupby("recommended_cluster_id")
        .agg(
            tracts=("tract_geoid", "size"),
            jobs=("jobs_total", "sum"),
            private_jobs=("private_jobs", "sum"),
            places=("place", lambda s: ", ".join(f"{p} ({n})" for p, n in s.value_counts().items())),
            top_tract=("tract_geoid", "first"),
        )
        .assign(public_share=lambda d: (1 - d["private_jobs"] / d["jobs"]).round(2))
        .sort_values("jobs", ascending=False)
        .reset_index()
    )


def center_workforce_table(flows: pd.DataFrame, centers: dict, counties: gpd.GeoDataFrame) -> pd.DataFrame:
    """Per center: jobs, share of its workers by home county (metro) or outside, and distance from home."""
    names = dict(zip(counties["county_geoid"], counties["county_name"].map(county_short_name)))
    rows = []
    for label, tracts in centers.items():
        into = flows.loc[flows["work_tract_geoid"].isin(tracts)].copy()
        total = into["jobs"].sum()
        # Jobs-weighted center point, from the work tracts' centroids.
        center_lon = (into["work_lon"] * into["jobs"]).sum() / total
        center_lat = (into["work_lat"] * into["jobs"]).sum() / total
        into["miles"] = haversine_miles(into["home_lon"], into["home_lat"], center_lon, center_lat)
        located = into.dropna(subset=["miles"])
        row = {"center": label, "tracts": len(tracts), "jobs": total}
        by_home = into.groupby(into["home_county_geoid"].map(names).fillna("Outside metro"))["jobs"].sum() / total
        row.update({f"from_{k}": v for k, v in by_home.items()})
        row["median_miles"] = weighted_median(located["miles"], located["jobs"])
        row["share_over_25mi"] = located.loc[located["miles"] > 25, "jobs"].sum() / located["jobs"].sum()
        row["share_over_75mi"] = located.loc[located["miles"] > 75, "jobs"].sum() / located["jobs"].sum()
        rows.append(row)
    order = ["center", "tracts", "jobs", "median_miles", "share_over_25mi", "share_over_75mi"]
    table = pd.DataFrame(rows).fillna(0)
    rest = [c for c in table.columns if c not in order]
    return table[order + sorted(rest)].round(3)


def center_shed_shares(flows: pd.DataFrame, center: set, tracts: gpd.GeoDataFrame) -> np.ndarray:
    """For each metro tract (in `tracts` order): share of its residents' jobs located in the center's tracts."""
    metro_homes = flows.loc[flows["home_tract_geoid"].isin(tracts["tract_geoid"])]
    resident_jobs = metro_homes.groupby("home_tract_geoid")["jobs"].sum()
    to_center = metro_homes.loc[metro_homes["work_tract_geoid"].isin(center)].groupby("home_tract_geoid")["jobs"].sum()
    return (to_center / resident_jobs).reindex(tracts["tract_geoid"]).fillna(0).to_numpy()


# ---- Zones and POIs (Q3) ----


def zone_place_summary(tracts: pd.DataFrame) -> pd.DataFrame:
    """Per working name: tracts, top places (by tract count), and median raw values."""
    def top_places(series):
        counts = series.value_counts()
        return ", ".join(f"{p} ({n})" for p, n in counts.head(4).items())

    return (
        tracts.groupby(["working_name", "zone_type"])
        .agg(
            tracts=("tract_geoid", "size"),
            top_places=("place", top_places),
            poverty=("pov_rate", "median"),
            ba_plus=("pct_ba_plus", "median"),
            income=("median_hh_income", "median"),
            owners=("owner_occ_rate", "median"),
            density=("pop_weighted_density_sqmi", "median"),
        )
        .sort_values("tracts", ascending=False)
        .round(3)
        .reset_index()
    )


def zone_stress_test(tracts: pd.DataFrame, n: int = 25) -> pd.DataFrame:
    """Tracts furthest from their type's Albany median, in metro standard deviations across five metrics."""
    metrics = ["pov_rate", "pct_ba_plus", "median_hh_income", "owner_occ_rate", "pop_weighted_density_sqmi"]
    values = tracts[metrics].assign(pop_weighted_density_sqmi=np.log10(tracts["pop_weighted_density_sqmi"].clip(lower=1)))
    z = (values - values.mean()) / values.std()
    medians = z.groupby(tracts["zone_type"]).transform("median")
    distance = np.sqrt(((z - medians) ** 2).sum(axis=1, min_count=1))
    return (
        tracts.assign(distance=distance)[["tract_geoid", "working_name", "place", "county_name", "distance"] + metrics]
        .sort_values("distance", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def kmeans(x: np.ndarray, k: int, *, seed: int = 7, iterations: int = 100) -> np.ndarray:
    """Plain k-means (k-means++ start). Exploration only; no scikit-learn in this environment."""
    rng = np.random.default_rng(seed)
    centers = [x[rng.integers(len(x))]]
    for _ in range(1, k):
        d = np.min([((x - c) ** 2).sum(axis=1) for c in centers], axis=0)
        centers.append(x[rng.choice(len(x), p=d / d.sum())])
    centers = np.array(centers)
    for _ in range(iterations):
        labels = np.argmin(((x[:, None, :] - centers[None]) ** 2).sum(axis=2), axis=1)
        new = np.array([x[labels == j].mean(axis=0) if (labels == j).any() else centers[j] for j in range(k)])
        if np.allclose(new, centers):
            break
        centers = new
    return labels


def poi_tract_clusters(counts: pd.DataFrame, tracts: gpd.GeoDataFrame, categories: list, *, k: int, min_pois: int):
    """Cluster tracts by POI category shares plus log POI density. Returns (tracts with cluster, profile table)."""
    wide = counts.pivot_table(index="tract_geoid", columns="category", values="pois", aggfunc="sum", fill_value=0)
    total = wide.sum(axis=1)
    shares = wide.reindex(columns=categories, fill_value=0).div(total, axis=0)
    area = tracts.set_index("tract_geoid").geometry.area / 2_589_988  # sq m -> sq mi in MAP_CRS
    density = np.log10((total / area.reindex(total.index)).clip(lower=0.1))
    eligible = total.index[total >= min_pois]
    features = pd.concat([shares, density.rename("log_density")], axis=1).loc[eligible]
    z = (features - features.mean()) / features.std()
    labels = kmeans(z.to_numpy(), k)
    cluster = pd.Series([f"P{j + 1}" for j in labels], index=eligible, name="poi_cluster")
    out = tracts.merge(cluster, left_on="tract_geoid", right_index=True, how="left")
    out["poi_cluster"] = out["poi_cluster"].fillna(f"Under {min_pois} POIs")
    out["pois"] = out["tract_geoid"].map(total).fillna(0)
    out["pois_per_sqmi"] = out["tract_geoid"].map(total / area.reindex(total.index))

    clustered = out.loc[out["tract_geoid"].isin(eligible)]
    profile = shares.loc[eligible].groupby(cluster).mean()
    top3 = profile.apply(lambda r: ", ".join(f"{c} {v:.0%}" for c, v in r.sort_values(ascending=False).head(3).items()), axis=1)
    summary = clustered.groupby("poi_cluster").agg(
        tracts=("tract_geoid", "size"),
        median_pois_per_sqmi=("pois_per_sqmi", "median"),
        top_places=("place", lambda s: ", ".join(f"{p} ({n})" for p, n in s.value_counts().head(3).items())),
        top_zone=("working_name", lambda s: f"{s.value_counts().index[0]} ({s.value_counts().iloc[0] / len(s):.0%})"),
    )
    return out, summary.join(top3.rename("top_categories")).round(1).reset_index()


def zone_activity_crosstab(tracts: pd.DataFrame) -> pd.DataFrame:
    """Working name by activity class: tracts, with residents (thousands) in brackets, and totals."""
    order = [a for a in ACTIVITY_ORDER if a in set(tracts["activity"])]
    n = pd.crosstab(tracts["working_name"], tracts["activity"], margins=True, margins_name="All").reindex(columns=order + ["All"])
    pop = pd.crosstab(tracts["working_name"], tracts["activity"], values=tracts["residents"], aggfunc="sum",
                      margins=True, margins_name="All").reindex(index=n.index, columns=n.columns).fillna(0)
    cells = n.fillna(0).astype(int).astype(str) + " (" + (pop / 1000).round(0).astype(int).astype(str) + "k)"
    rows = n.drop(index="All").sort_values("All", ascending=False).index.tolist() + ["All"]
    return cells.where(n.fillna(0) > 0, "–").reindex(rows)


def activity_profile(tracts: pd.DataFrame) -> pd.DataFrame:
    """Median inputs by activity class: what each class looks like on the numbers the rules use."""
    return (tracts.groupby("activity")
            .agg(tracts=("tract_geoid", "size"), residents=("residents", "sum"), jobs=("jobs", "sum"),
                 pois_per_1k=("pois_per_1k", "median"), jobs_per_resident=("jobs_per_resident", "median"),
                 share_local=("share_local", "median"), share_destination=("share_destination", "median"),
                 share_industrial=("share_industrial", "median"))
            .reindex([a for a in ACTIVITY_ORDER if a in set(tracts["activity"])]).round(2).reset_index())


def activity_surprises(tracts: pd.DataFrame, *, rare: float = 0.15) -> pd.DataFrame:
    """Tracts whose activity class is rare for their zone (under `rare` of the zone's tracts): the places where
    who lives there and what's there part ways. Zones under 5 tracts are skipped."""
    zone_n = tracts.groupby("working_name")["tract_geoid"].transform("size")
    cell_share = tracts.groupby(["working_name", "activity"])["tract_geoid"].transform("size") / zone_n
    picked = tracts.loc[(cell_share < rare) & (zone_n >= 5)]
    return (picked.assign(share_of_zone=cell_share)
            [["tract_geoid", "working_name", "activity", "place", "county_name", "share_of_zone", "residents", "jobs",
              "pois", "pois_per_1k", "jobs_per_resident", "share_local", "share_destination", "share_industrial"]]
            .sort_values(["working_name", "activity", "jobs_per_resident"], ascending=[True, True, False])
            .round(2).reset_index(drop=True))


def adjusted_rand(a, b) -> float:
    """Adjusted Rand index between two labelings (1 = identical, about 0 = no better than chance). No scikit-learn here."""
    table = pd.crosstab(pd.Series(list(a)), pd.Series(list(b))).to_numpy()
    pairs = lambda x: (x * (x - 1) / 2).sum()  # noqa: E731
    index, rows, cols, total = pairs(table), pairs(table.sum(axis=1)), pairs(table.sum(axis=0)), pairs(np.array([table.sum()]))
    expected = rows * cols / total
    return float((index - expected) / ((rows + cols) / 2 - expected))


# ---- Metro profile: scorecard charts, peers, benchmarks (Q4) ----


def glance_dot_plot(raw: pd.DataFrame, metrics: dict, upstate_metros: set, upstate: dict):
    """One row per metric: each metro's percentile among US metros. Upstate metros faint, Albany red,
    the Upstate aggregate and the US value (where published) as references. Hover for names and values."""
    wide = metro_wide(raw)
    us = raw.loc[raw["geo_level"] == "us"].set_index("metric_id")["value"]
    names = raw.drop_duplicates("geo_id").set_index("geo_id")["geo_name"]
    rows = list(metrics.items())
    fig = go.Figure()

    def pct(values, v):
        return 100 * (values < v).mean()

    series = {"Upstate metros": [], "Albany": [], "Upstate (aggregate)": [], "US": []}
    for i, (metric_id, (label, kind, _group)) in enumerate(rows):
        values = wide[metric_id].dropna()
        for code in sorted(upstate_metros - {CBSA_CODE}):
            if code in values:
                series["Upstate metros"].append((pct(values, values[code]), i, f"{short_cbsa(names[code])}: {format_metric(kind, values[code])}"))
        series["Albany"].append((pct(values, values[CBSA_CODE]), i, f"Albany: {format_metric(kind, values[CBSA_CODE])}"))
        up_value, up_exact = upstate[metric_id]
        if pd.notna(up_value):
            series["Upstate (aggregate)"].append((pct(values, up_value), i, f"Upstate: {'' if up_exact else '≈ '}{format_metric(kind, up_value)}"))
        if pd.notna(us.get(metric_id)):
            series["US"].append((pct(values, us[metric_id]), i, f"US: {format_metric(kind, us[metric_id])}"))
    styles = {"Upstate metros": (color("highlight.strength"), 9, 0.45, "circle"), "US": ("#3E4C59", 11, 1, "line-ns-open"),
              "Upstate (aggregate)": ("#3E4C59", 10, 1, "diamond-open"), "Albany": (color("highlight.risk"), 15, 1, "circle")}
    for name, points in series.items():
        fill, size, opacity, symbol = styles[name]
        fig.add_trace(go.Scatter(
            x=[p[0] for p in points], y=[p[1] for p in points], mode="markers", name=name,
            marker={"color": fill, "size": size, "opacity": opacity, "symbol": symbol, "line": {"width": 2 if "open" in symbol else 0}},
            hovertext=[p[2] for p in points], hovertemplate="%{hovertext} (percentile %{x:.0f})<extra></extra>",
        ))
    fig.update_layout(
        title={"text": "Albany's percentile among the 393 US metros on each At a glance metric", "x": 0.01, "font": {"size": 14}},
        height=110 + 48 * len(rows), margin={"l": 10, "r": 10, "t": 50, "b": 40}, plot_bgcolor="white",
        xaxis={"range": [-2, 102], "title": "Percentile among US metros (100 = highest value)", "gridcolor": "#EEF1F4"},
        yaxis={"tickvals": list(range(len(rows))), "ticktext": [spec[0] for _, spec in rows], "autorange": "reversed"},
        legend={"orientation": "h", "y": -0.18},
    )
    return fig


def metric_strip_chart(raw: pd.DataFrame, metric_id: str, spec: tuple, upstate_metros: set, *, height: int = 430,
                       highlight_label: str = "Upstate NY metros"):
    """Every US metro as a dot on one metric; the highlighted set (Upstate metros by default) labeled, NYC and Albany
    marked; hover for names."""
    label, kind, _group = spec
    metros = raw.loc[(raw["geo_level"] == "cbsa") & (raw["metric_id"] == metric_id)].dropna(subset=["value"]).copy()
    n = len(metros)
    metros["rank"] = metros["value"].rank(ascending=False, method="min").astype(int)
    metros["group"] = np.select(
        [metros["geo_id"] == CBSA_CODE, metros["geo_id"].isin(upstate_metros), metros["geo_id"] == NYC_CBSA_CODE],
        ["Albany", highlight_label, "NYC metro"], "Other US metros",
    )
    metros["y"] = np.random.default_rng(7).uniform(-1, 1, n)
    metros.loc[metros["geo_id"] == CBSA_CODE, "y"] = 0
    metros["hover"] = [f"<b>{name}</b><br>{format_metric(kind, v)}<br>#{r} of {n}"
                       for name, v, r in zip(metros["geo_name"], metros["value"], metros["rank"])]
    styles = {
        "Other US metros": (color("neutral.comparison_fill"), 6, 0.55, False),
        "NYC metro": ("#3E4C59", 10, 1.0, True),
        highlight_label: (color("highlight.strength"), 10, 1.0, True),
        "Albany": (color("highlight.risk"), 16, 1.0, True),
    }
    fig = go.Figure()
    for group, (fill, size, opacity, labeled) in styles.items():
        part = metros.loc[metros["group"] == group]
        fig.add_trace(go.Scatter(
            x=part["value"], y=part["y"], mode="markers+text" if labeled else "markers", name=group,
            marker={"color": fill, "size": size, "opacity": opacity, "line": {"color": "white", "width": 0.5}},
            text=part["geo_name"].map(short_cbsa) if labeled else None, textposition="top center", textfont={"size": 10},
            hovertext=part["hover"], hovertemplate="%{hovertext}<extra></extra>",
        ))
    values = metros.set_index("geo_id")["value"]
    albany = values[CBSA_CODE]
    fig.add_vline(x=values.median(), line_dash="dash", line_width=1, line_color="#3E4C59",
                  annotation_text=f"Median metro {format_metric(kind, values.median())}", annotation_position="top")
    fig.update_layout(
        title={"text": f"{label}: Albany {format_metric(kind, albany)}, #{int((values > albany).sum() + 1)} of {n} "
                       f"({position_words(values, albany)})", "x": 0.01, "font": {"size": 14}},
        height=height, margin={"l": 10, "r": 10, "t": 60, "b": 40}, plot_bgcolor="white",
        yaxis={"visible": False, "range": [-1.4, 1.4]},
        xaxis={"type": "log" if kind in ("count", "usd_big") else "linear", "showgrid": True, "gridcolor": "#EEF1F4"},
        legend={"orientation": "h", "y": -0.12},
    )
    return fig


def benchmark_table(raw: pd.DataFrame, comparisons: dict, peer_codes: list, upstate: dict) -> pd.DataFrame:
    """Long rows for the benchmark: Albany, the picked metros (code -> name), then the references."""
    wide = metro_wide(raw)
    refs = raw.loc[raw["geo_level"].isin(["state", "us"])].pivot(index="geo_level", columns="metric_id", values="value")
    rows = [("Albany", "Albany", wide.loc[CBSA_CODE])]
    rows += [(short_cbsa(name), "Picked metro", wide.loc[code]) for code, name in comparisons.items()]
    rows += [
        (f"Peer median ({len(peer_codes)})", "Reference", wide.loc[wide.index.isin(peer_codes)].median()),
        ("Upstate", "Reference", pd.Series({m: v for m, (v, _exact) in upstate.items()})),
        ("NY State", "Reference", refs.loc["state"]),
        ("US", "Reference", refs.loc["us"]),
        ("Median US metro", "Reference", wide.median()),
    ]
    frames = [values.rename("value").rename_axis("metric_id").reset_index().assign(row=name, kind=kind)
              for name, kind, values in rows]
    return pd.concat(frames, ignore_index=True)[["row", "kind", "metric_id", "value"]]


def benchmark_bar_chart(bench: pd.DataFrame, metric_id: str, spec: tuple):
    """One metric: a bar per row, Albany highlighted, references in a lighter tone. Missing references are skipped."""
    label, kind, _group = spec
    part = bench.loc[(bench["metric_id"] == metric_id)].dropna(subset=["value"])
    fills = {"Albany": color("highlight.risk"), "Picked metro": color("neutral.comparison_fill"), "Reference": "#D3DCE6"}
    fig = go.Figure(go.Bar(
        x=part["value"], y=part["row"], orientation="h", marker={"color": part["kind"].map(fills)},
        text=[format_metric(kind, v) for v in part["value"]], textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{text}<extra></extra>",
    ))
    fig.update_layout(
        title={"text": f"{label} (Upstate ≈ where noted in Q4a)", "x": 0.01, "font": {"size": 14}},
        height=90 + 34 * len(part), margin={"l": 10, "r": 60, "t": 50, "b": 20}, plot_bgcolor="white",
        yaxis={"autorange": "reversed"}, xaxis={"visible": False, "type": "log" if kind in ("count", "usd_big") else "linear"},
    )
    return fig


def benchmark_summary(bench: pd.DataFrame, metrics: dict) -> pd.DataFrame:
    """Every metric (rows) for every benchmark row (columns), formatted."""
    table = bench.pivot(index="metric_id", columns="row", values="value")
    table = table.loc[[m for m in metrics if m in table.index], bench["row"].unique()]
    out = table.apply(lambda col: [format_metric(metrics[m][1], v) for m, v in col.items()])
    out.index = [metrics[m][0] for m in out.index]
    return out.rename_axis("metric").reset_index()


def peer_stats_table(peers: pd.DataFrame, clusters: pd.DataFrame, raw: pd.DataFrame, stats: dict) -> pd.DataFrame:
    """Albany plus its cross-frame peers: similarity, cluster, and raw stats (`stats` is a slice of q4_metrics)."""
    wide = metro_wide(raw)
    albany_cluster = clusters.loc[CBSA_CODE, "cross_frame_cluster_name"]
    rows = [{"rank": 0, "metro": "Albany-Schenectady-Troy, NY", "code": CBSA_CODE, "similarity": np.nan}]
    rows += [{"rank": r.peer_rank, "metro": r.peer_cbsa_name, "code": r.peer_cbsa_code, "similarity": round(r.similarity, 3)}
             for r in peers.itertuples()]
    table = pd.DataFrame(rows)
    table["cluster"] = [
        "(Albany's)" if code != CBSA_CODE and clusters.loc[code, "cross_frame_cluster_name"] == albany_cluster
        else clusters.loc[code, "cross_frame_cluster_name"] for code in table["code"]
    ]
    for metric_id, (label, kind, _group) in stats.items():
        table[label] = [format_metric(kind, wide.loc[code, metric_id]) for code in table["code"]]
    return table.drop(columns="code")


def frame_peer_grid(peer_list: pd.DataFrame) -> pd.DataFrame:
    """Rank x frame grid of peer names; names that are also cross-frame peers get a *."""
    cross = set(peer_list.loc[peer_list["peer_type"] == "cross_frame", "peer_cbsa_code"])
    grid = peer_list.assign(
        name=lambda d: [f"{short_cbsa(n)}, {n.split(', ')[-1]}" + (" *" if c in cross else "")
                        for n, c in zip(d["peer_cbsa_name"], d["peer_cbsa_code"])]
    ).pivot(index="peer_rank", columns="peer_type", values="name")
    return grid[["cross_frame", "character", "livability", "opportunity"]].reset_index()


def cluster_raw_profile(raw: pd.DataFrame, clusters: pd.DataFrame, cluster: str, metrics: dict) -> pd.DataFrame:
    """Albany, its cluster's median and all metros' median on raw values, plus where the cluster median ranks."""
    wide = metro_wide(raw)
    members = clusters.index[clusters["cross_frame_cluster_name"] == cluster]
    rows = []
    for metric_id, (label, kind, _group) in metrics.items():
        values = wide[metric_id].dropna()
        cluster_median = values.loc[values.index.isin(members)].median()
        rows.append({
            "metric": label,
            "Albany": format_metric(kind, values.get(CBSA_CODE, np.nan)),
            "cluster median": format_metric(kind, cluster_median),
            "all metros median": format_metric(kind, values.median()),
            "cluster median above % of metros": round(100 * (values < cluster_median).mean()),
        })
    return pd.DataFrame(rows)


def peer_shared_traits(raw: pd.DataFrame, metrics: dict, peers: set) -> pd.DataFrame:
    """Per metric: Albany, the peer median, the median US metro, how many peers sit above it, and a verdict
    (8+ of the peers on one side = shared). Shared traits first, strongest first."""
    wide = metro_wide(raw)
    rows = []
    for metric_id, (label, kind, group) in metrics.items():
        if metric_id not in wide:
            continue
        values = wide[metric_id].dropna()
        peer_values = values.loc[values.index.isin(peers)]
        median = values.median()
        above = int((peer_values > median).sum())
        n = len(peer_values)
        verdict = "Shared: higher" if above >= n - 2 else "Shared: lower" if above <= 2 else "Mixed"
        albany = values.get(CBSA_CODE, np.nan)
        rows.append({
            "group": group, "metric": label, "verdict": verdict, "peers_above": f"{above} of {n}",
            "Albany": format_metric(kind, albany), "peer median": format_metric(kind, peer_values.median()),
            "median metro": format_metric(kind, median),
            "peer median pctl": round(100 * (values < peer_values.median()).mean()),
            "Albany pctl": round(100 * (values < albany).mean()) if pd.notna(albany) else None,
            "Albany fits": "" if verdict == "Mixed" else ("yes" if (albany > median) == (verdict == "Shared: higher") else "no"),
            "_strength": abs(above - n / 2),
        })
    return pd.DataFrame(rows).sort_values(["_strength", "group"], ascending=[False, True]).drop(columns="_strength").reset_index(drop=True)


def head_to_head(raw: pd.DataFrame, metrics: dict, rivals: dict) -> pd.DataFrame:
    """Albany against `rivals` (code -> name) on every metric: values, the leader (highest value) and Albany's place."""
    wide = metro_wide(raw)
    names = {CBSA_CODE: "Albany", **rivals}
    rows = []
    for metric_id, (label, kind, group) in metrics.items():
        values = wide.loc[list(names), metric_id].rename(index=names)
        row = {"group": group, "metric": label}
        row.update({name: format_metric(kind, v) for name, v in values.items()})
        row["leader"] = values.idxmax() if values.notna().any() else ""
        row["Albany place (of 4)"] = int((values > values["Albany"]).sum() + 1) if pd.notna(values["Albany"]) else None
        rows.append(row)
    return pd.DataFrame(rows)


def trend_chart(trends: pd.DataFrame, metric_id: str, label: str, names: dict, *, index: bool = True):
    """One line per metro since the first year; indexed to the first year (= 100) or as levels."""
    part = trends.loc[trends["metric_id"] == metric_id].dropna(subset=["value"]).sort_values("year")
    fig = go.Figure()
    for code, name in names.items():
        series = part.loc[part["geo_id"] == code].set_index("year")["value"]
        if series.empty:
            continue
        y = 100 * series / series.iloc[0] if index else series
        fig.add_trace(go.Scatter(
            x=series.index, y=y, mode="lines+markers", name=name,
            line={"width": 3.5 if code == CBSA_CODE else 1.8, "color": color("highlight.risk") if code == CBSA_CODE else None},
            hovertemplate=f"{name} %{{x}}: %{{y:,.1f}}<extra></extra>",
        ))
    fig.update_layout(
        title={"text": f"{label}{', indexed to ' + str(int(part['year'].min())) + ' = 100' if index else ''}", "x": 0.01, "font": {"size": 14}},
        height=420, margin={"l": 10, "r": 10, "t": 50, "b": 30}, plot_bgcolor="white",
        yaxis={"gridcolor": "#EEF1F4"}, legend={"orientation": "h", "y": -0.15},
    )
    return fig


# ---- Migration (Q4i) ----


def migration_by_year(mig: pd.DataFrame, code: str) -> pd.DataFrame:
    """Net people per year for one metro, by region of the other end."""
    part = mig.loc[mig["cbsa_code"] == code].assign(signed=lambda d: np.where(d["direction"] == "in", d["people"], -d["people"]))
    table = part.pivot_table(index="year", columns="region", values="signed", aggfunc="sum").fillna(0)
    table["Total"] = table.sum(axis=1)
    return table.round(0).astype(int)


def migration_counterparts(mig: pd.DataFrame, code: str) -> pd.DataFrame:
    """For one metro: every other county, annual-average people in, out and net, largest exchanges first."""
    part = mig.loc[mig["cbsa_code"] == code]
    years = part["year"].nunique()
    table = part.pivot_table(index=["other_county_geoid", "other_county_name", "region", "other_cbsa_name"], columns="direction", values="people",
                             aggfunc="sum", fill_value=0, dropna=False).reset_index()
    for c in ("in", "out"):
        if c not in table:
            table[c] = 0
    table = table.assign(in_per_year=lambda d: d["in"] / years, out_per_year=lambda d: d["out"] / years,
                         net_per_year=lambda d: (d["in"] - d["out"]) / years)
    table = table.loc[(table["in"] + table["out"]) > 0]
    return (table.rename(columns={"other_county_geoid": "county_geoid", "other_county_name": "county", "other_cbsa_name": "metro"})
            [["county_geoid", "county", "metro", "region", "in_per_year", "out_per_year", "net_per_year"]]
            .assign(exchange=lambda d: d["in_per_year"] + d["out_per_year"])
            .sort_values("exchange", ascending=False).drop(columns="exchange").round(1).reset_index(drop=True))
