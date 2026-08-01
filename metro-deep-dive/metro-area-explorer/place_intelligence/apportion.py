"""Catchment ring construction and tract apportionment for Place Intelligence."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import duckdb
import geopandas as gpd
import pandas as pd
from shapely import Point, wkb


REPO_ROOT = Path(__file__).resolve().parents[3]
DB_PATH = REPO_ROOT / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"
METERS_PER_MILE = 1609.344
WGS84_CRS = "EPSG:4326"


def build_rings(lat: float, lon: float, rings_mi: list[int]) -> gpd.GeoDataFrame:
    """Build non-overlapping distance bands around a site point in a local projected CRS."""

    sorted_rings = _validate_rings(rings_mi)
    site = gpd.GeoDataFrame(
        [{"lat": float(lat), "lon": float(lon)}],
        geometry=[Point(float(lon), float(lat))],
        crs=WGS84_CRS,
    )
    projected_crs = site.estimate_utm_crs()
    if projected_crs is None:
        raise ValueError("Could not estimate a projected CRS for the site point.")

    site_projected = site.to_crs(projected_crs)
    point = site_projected.geometry.iloc[0]

    rows: list[dict] = []
    previous_buffer = None
    for ring_mi in sorted_rings:
        outer_buffer = point.buffer(ring_mi * METERS_PER_MILE)
        ring_geometry = outer_buffer if previous_buffer is None else outer_buffer.difference(previous_buffer)
        rows.append(
            {
                "ring_mi": ring_mi,
                "geometry": ring_geometry,
                "ring_area_sq_mi": ring_geometry.area / (METERS_PER_MILE**2),
            }
        )
        previous_buffer = outer_buffer

    return gpd.GeoDataFrame(rows, geometry="geometry", crs=projected_crs)


def apportion_weights(rings: gpd.GeoDataFrame, market_id: str) -> pd.DataFrame:
    """Intersect tract geometry with ring bands and return tract-share weights per band."""

    if rings.empty:
        return pd.DataFrame(
            columns=[
                "site_id",
                "ring_mi",
                "tract_geoid",
                "weight",
                "weight_method",
                "intersect_area",
                "tract_area",
                "containment",
                "centroid_in",
            ]
        )

    _validate_ring_frame(rings)
    market_tracts = _load_market_tracts(str(market_id))
    tracts_projected = market_tracts.to_crs(rings.crs)
    site_id = _extract_site_id(rings)

    rows: list[dict] = []
    for ring in rings.sort_values("ring_mi").itertuples(index=False):
        ring_geom = ring.geometry
        intersecting = tracts_projected.loc[tracts_projected.geometry.intersects(ring_geom)].copy()
        if intersecting.empty:
            continue

        intersecting["intersect_geometry"] = intersecting.geometry.intersection(ring_geom)
        intersecting["intersect_area"] = intersecting["intersect_geometry"].area
        intersecting = intersecting.loc[intersecting["intersect_area"] > 0].copy()
        if intersecting.empty:
            continue

        intersecting["tract_area"] = intersecting.geometry.area
        intersecting["weight"] = intersecting["intersect_area"] / intersecting["tract_area"]
        intersecting["containment"] = intersecting["weight"].apply(
            lambda value: "full" if abs(float(value) - 1.0) <= 1e-9 else "fragment"
        )
        intersecting["centroid_in"] = intersecting.geometry.centroid.within(ring_geom)

        rows.extend(
            {
                "site_id": site_id,
                "ring_mi": int(ring.ring_mi),
                "tract_geoid": str(record.tract_geoid),
                "weight": float(record.weight),
                "weight_method": "areal",
                "intersect_area": float(record.intersect_area),
                "tract_area": float(record.tract_area),
                "containment": str(record.containment),
                "centroid_in": bool(record.centroid_in),
            }
            for record in intersecting.itertuples(index=False)
        )

    return pd.DataFrame(rows)


def apportion(
    metric_series: pd.Series,
    weight_table: pd.DataFrame,
    kind: Literal["extensive", "intensive"],
    method: str | None = None,
) -> pd.Series:
    """Aggregate tract-grain metrics into ring-grain values using the weight table."""

    if kind not in {"extensive", "intensive"}:
        raise ValueError("kind must be 'extensive' or 'intensive'.")

    metric_name = str(metric_series.name or "")
    if kind == "intensive" and _is_median_metric(metric_name) and method != "approximate":
        raise ValueError(
            f"Metric '{metric_name or '<unnamed>'}' looks median-like and requires method='approximate'."
        )

    if weight_table.empty:
        return pd.Series(dtype=float)

    values = metric_series.rename("metric_value").rename_axis("tract_geoid").reset_index()
    merged = weight_table.merge(values, on="tract_geoid", how="inner")
    if merged.empty:
        return pd.Series(dtype=float)

    group_columns = ["ring_mi"]
    if "site_id" in merged.columns and merged["site_id"].nunique() > 1:
        group_columns = ["site_id", "ring_mi"]

    if kind == "extensive":
        result = merged.assign(weighted_value=merged["metric_value"] * merged["weight"]).groupby(
            group_columns,
            sort=True,
        )["weighted_value"].sum()
        return result.astype(float)

    numerator = merged.assign(weighted_value=merged["metric_value"] * merged["weight"]).groupby(
        group_columns,
        sort=True,
    )["weighted_value"].sum()
    denominator = merged.groupby(group_columns, sort=True)["weight"].sum()
    return (numerator / denominator).astype(float)


def coverage_diagnostic(weight_table: pd.DataFrame) -> pd.DataFrame:
    """Summarize how much of each ring comes from whole tracts versus fragments."""

    if weight_table.empty:
        return pd.DataFrame(
            columns=[
                "ring_mi",
                "intersecting_tract_count",
                "total_weight_captured",
                "whole_tract_count",
                "fragment_share",
                "reliability_flag",
            ]
        )

    rows: list[dict] = []
    for ring_mi, ring_rows in weight_table.groupby("ring_mi", sort=True):
        intersecting_tract_count = int(len(ring_rows))
        total_weight_captured = float(ring_rows["weight"].sum())
        whole_tract_count = int((ring_rows["containment"] == "full").sum())
        fragment_weight = float(ring_rows.loc[ring_rows["containment"] == "fragment", "weight"].sum())
        fragment_share = fragment_weight / total_weight_captured if total_weight_captured else 0.0
        rows.append(
            {
                "ring_mi": int(ring_mi),
                "intersecting_tract_count": intersecting_tract_count,
                "total_weight_captured": total_weight_captured,
                "whole_tract_count": whole_tract_count,
                "fragment_share": fragment_share,
                "reliability_flag": _classify_reliability(whole_tract_count, fragment_share),
            }
        )

    return pd.DataFrame(rows).sort_values("ring_mi").reset_index(drop=True)


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open the shared repo DuckDB in read-only mode."""

    return duckdb.connect(str(DB_PATH), read_only=True)


def _load_market_tracts(market_id: str) -> gpd.GeoDataFrame:
    """Read tract geometry for one market from the governed DuckDB warehouse."""

    con = get_connection()
    try:
        con.execute("LOAD spatial;")
        rows = con.execute(
            """
            WITH market_counties AS (
                SELECT DISTINCT county_geoid
                FROM patterns_in_place.silver.xwalk_cbsa_county
                WHERE cbsa_code = ?
            )
            SELECT
                g.tract_geoid,
                ST_AsWKB(g.geom) AS geom_wkb
            FROM patterns_in_place.geo.tracts_all_us g
            INNER JOIN market_counties c
                ON g.county_geoid = c.county_geoid
            ORDER BY g.tract_geoid
            """,
            [str(market_id)],
        ).fetchall()
    finally:
        con.close()

    if not rows:
        raise ValueError(f"No tract geometry found for market_id={market_id}.")

    return gpd.GeoDataFrame(
        [{"tract_geoid": str(tract_geoid)} for tract_geoid, _geom in rows],
        geometry=[wkb.loads(bytes(geom)) for _tract_geoid, geom in rows],
        crs=WGS84_CRS,
    )


def _validate_rings(rings_mi: list[int]) -> list[int]:
    """Require positive integer ring distances and normalize them into ascending order."""

    if not isinstance(rings_mi, list) or not rings_mi:
        raise ValueError("rings_mi must be a non-empty list of positive integers.")

    normalized: list[int] = []
    for ring in rings_mi:
        if isinstance(ring, bool) or not isinstance(ring, int) or ring <= 0:
            raise ValueError("rings_mi must be a non-empty list of positive integers.")
        normalized.append(int(ring))
    return sorted(set(normalized))


def _validate_ring_frame(rings: gpd.GeoDataFrame) -> None:
    """Ensure downstream weighting is working from a valid projected ring frame."""

    if "ring_mi" not in rings.columns:
        raise ValueError("rings must include a 'ring_mi' column.")
    if rings.crs is None:
        raise ValueError("rings must carry a CRS.")
    if str(rings.crs).upper() == WGS84_CRS:
        raise ValueError("rings must be projected before weighting; WGS84 degrees are not allowed.")


def _extract_site_id(rings: gpd.GeoDataFrame) -> str:
    """Keep the weight schema stable even before site orchestration is wired in."""

    if "site_id" not in rings.columns:
        return "site"
    unique_values = [value for value in rings["site_id"].dropna().unique()]
    if not unique_values:
        return "site"
    return str(unique_values[0])


def _is_median_metric(metric_name: str) -> bool:
    """Catch common median naming patterns so they are not averaged silently."""

    lowered = metric_name.lower()
    return "median" in lowered or lowered.startswith("med_") or "_med_" in lowered or lowered.endswith("_med")


def _classify_reliability(whole_tract_count: int, fragment_share: float) -> str:
    """Translate fragment dominance into a simple appendix-friendly reliability flag."""

    if whole_tract_count == 0:
        return "fragment_only"
    if fragment_share >= 0.75:
        return "fragment_heavy"
    if fragment_share >= 0.5:
        return "mixed"
    return "stable"
