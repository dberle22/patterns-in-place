"""Reusable geospatial helpers."""

from __future__ import annotations

from collections.abc import Iterable

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

DEFAULT_WGS84_CRS = "EPSG:4326"
DEFAULT_PROJECTED_CRS = "EPSG:2263"


def points_from_lon_lat(
    dataframe: pd.DataFrame,
    lon_col: str = "lon",
    lat_col: str = "lat",
    crs: str = DEFAULT_WGS84_CRS,
) -> gpd.GeoDataFrame:
    """Convert longitude/latitude columns into a GeoDataFrame."""

    required_columns = {lon_col, lat_col}
    missing_columns = required_columns.difference(dataframe.columns)
    if missing_columns:
        raise ValueError(f"Missing coordinate columns: {sorted(missing_columns)}")

    geometry = [Point(lon, lat) for lon, lat in zip(dataframe[lon_col], dataframe[lat_col], strict=False)]
    return gpd.GeoDataFrame(dataframe.copy(), geometry=geometry, crs=crs)


def ensure_crs(geo_df: gpd.GeoDataFrame, crs: str = DEFAULT_WGS84_CRS) -> gpd.GeoDataFrame:
    """Return a GeoDataFrame with a CRS set or transformed to the requested CRS."""

    if geo_df.crs is None:
        return geo_df.set_crs(crs)
    if geo_df.crs.to_string() != crs:
        return geo_df.to_crs(crs)
    return geo_df


def spatial_join_points_to_polygons(
    points: gpd.GeoDataFrame,
    polygons: gpd.GeoDataFrame,
    point_columns: Iterable[str] | None = None,
    polygon_columns: Iterable[str] | None = None,
    predicate: str = "within",
) -> gpd.GeoDataFrame:
    """Join point geometries to polygon attributes."""

    points_wgs84 = ensure_crs(points)
    polygons_wgs84 = ensure_crs(polygons)

    if point_columns is not None:
        points_wgs84 = points_wgs84[[*point_columns, "geometry"]]
    if polygon_columns is not None:
        polygons_wgs84 = polygons_wgs84[[*polygon_columns, "geometry"]]

    joined = gpd.sjoin(points_wgs84, polygons_wgs84, how="left", predicate=predicate)
    return joined.drop(columns=["index_right"], errors="ignore")


def spatial_join_centroids_to_polygons(
    source_polygons: gpd.GeoDataFrame,
    target_polygons: gpd.GeoDataFrame,
    source_id_col: str,
    target_columns: Iterable[str],
) -> gpd.GeoDataFrame:
    """Assign each source polygon to a target polygon using its centroid."""

    source_wgs84 = ensure_crs(source_polygons)
    centroids = source_wgs84.copy()
    centroids["geometry"] = source_wgs84.to_crs(DEFAULT_PROJECTED_CRS).centroid.to_crs(DEFAULT_WGS84_CRS)
    keep_cols = [source_id_col, "geometry"]
    return spatial_join_points_to_polygons(
        points=centroids[keep_cols],
        polygons=target_polygons,
        point_columns=[source_id_col],
        polygon_columns=list(target_columns),
    )


def distance_miles_between_points(
    left: gpd.GeoDataFrame,
    right: gpd.GeoDataFrame,
    left_id_col: str,
    right_id_col: str,
) -> pd.DataFrame:
    """Return all pairwise distances in miles between two point GeoDataFrames."""

    left_projected = ensure_crs(left).to_crs(DEFAULT_PROJECTED_CRS)
    right_projected = ensure_crs(right).to_crs(DEFAULT_PROJECTED_CRS)
    rows: list[dict[str, object]] = []

    for _, left_row in left_projected.iterrows():
        distances_feet = right_projected.geometry.distance(left_row.geometry)
        for right_index, distance_feet in distances_feet.items():
            rows.append(
                {
                    left_id_col: left_row[left_id_col],
                    right_id_col: right_projected.loc[right_index, right_id_col],
                    "distance_miles": float(distance_feet) / 5280,
                }
            )

    return pd.DataFrame(rows)


def nearest_neighbor(
    origins: gpd.GeoDataFrame,
    destinations: gpd.GeoDataFrame,
    origin_id_col: str,
    destination_id_col: str,
    destination_name_col: str | None = None,
) -> pd.DataFrame:
    """Find the nearest destination for every origin point."""

    distances = distance_miles_between_points(
        left=origins,
        right=destinations,
        left_id_col=origin_id_col,
        right_id_col=destination_id_col,
    )
    if distances.empty:
        return pd.DataFrame(columns=[origin_id_col, destination_id_col, "distance_miles"])

    nearest = distances.sort_values("distance_miles").drop_duplicates(origin_id_col, keep="first")
    if destination_name_col:
        names = destinations[[destination_id_col, destination_name_col]].drop_duplicates()
        nearest = nearest.merge(names, on=destination_id_col, how="left")
    return nearest.reset_index(drop=True)


def count_points_within_radius(
    origins: gpd.GeoDataFrame,
    points: gpd.GeoDataFrame,
    origin_id_col: str,
    point_category_col: str | None = None,
    radius_miles: float = 0.5,
) -> pd.DataFrame:
    """Count nearby points around each origin, optionally by category."""

    origins_projected = ensure_crs(origins).to_crs(DEFAULT_PROJECTED_CRS)
    points_projected = ensure_crs(points).to_crs(DEFAULT_PROJECTED_CRS)
    radius_feet = radius_miles * 5280
    rows: list[dict[str, object]] = []

    for _, origin in origins_projected.iterrows():
        nearby = points_projected[points_projected.geometry.distance(origin.geometry) <= radius_feet]
        row: dict[str, object] = {origin_id_col: origin[origin_id_col], "poi_count": int(len(nearby))}
        if point_category_col and not nearby.empty:
            counts = nearby[point_category_col].value_counts().to_dict()
            row["poi_category_counts"] = counts
        elif point_category_col:
            row["poi_category_counts"] = {}
        rows.append(row)

    return pd.DataFrame(rows)
