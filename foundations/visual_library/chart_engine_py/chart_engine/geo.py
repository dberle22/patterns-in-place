"""
Pure-Python geo helpers shared by the matplotlib-backed map renderers.

These utilities intentionally avoid heavy GIS dependencies so the first Python
package port can accept simple polygon-like payloads from tests or upstream
data shaping before we take on geopandas packaging work.
"""

from __future__ import annotations

import math
from typing import Any

import pandas as pd


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_point(value: Any) -> bool:
    return isinstance(value, (list, tuple)) and len(value) >= 2 and _is_number(value[0]) and _is_number(value[1])


def _normalize_ring(ring: Any) -> list[tuple[float, float]]:
    if not isinstance(ring, (list, tuple)):
        return []
    points = [(float(point[0]), float(point[1])) for point in ring if _is_point(point)]
    if len(points) >= 3 and points[0] != points[-1]:
        points.append(points[0])
    return points


def geometry_to_polygons(geometry: Any) -> list[list[tuple[float, float]]]:
    """
    Convert a lightweight geometry payload into a list of polygon rings.

    Supported shapes:
    - GeoJSON-like dicts with `Polygon` or `MultiPolygon`
    - a flat list of `(x, y)` coordinate pairs
    - a list of polygon coordinate lists
    """
    if geometry is None:
        return []
    if isinstance(geometry, float) and pd.isna(geometry):
        return []

    if isinstance(geometry, dict):
        geom_type = geometry.get("type")
        coordinates = geometry.get("coordinates", [])
        if geom_type == "Polygon":
            return [_normalize_ring(coordinates[0])] if coordinates else []
        if geom_type == "MultiPolygon":
            polygons: list[list[tuple[float, float]]] = []
            for polygon in coordinates:
                if polygon:
                    polygons.append(_normalize_ring(polygon[0]))
            return [polygon for polygon in polygons if polygon]
        return []

    if isinstance(geometry, (list, tuple)):
        if geometry and _is_point(geometry[0]):
            polygon = _normalize_ring(geometry)
            return [polygon] if polygon else []
        polygons = [_normalize_ring(polygon) for polygon in geometry if isinstance(polygon, (list, tuple))]
        return [polygon for polygon in polygons if polygon]

    return []


def centroid_from_polygons(polygons: list[list[tuple[float, float]]]) -> tuple[float | None, float | None]:
    all_points = [point for polygon in polygons for point in polygon]
    if not all_points:
        return None, None
    x_coords = [point[0] for point in all_points]
    y_coords = [point[1] for point in all_points]
    return sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords)


def bounds_from_polygons(polygons: list[list[tuple[float, float]]]) -> tuple[float, float, float, float] | None:
    all_points = [point for polygon in polygons for point in polygon]
    if not all_points:
        return None
    x_coords = [point[0] for point in all_points]
    y_coords = [point[1] for point in all_points]
    return min(x_coords), max(x_coords), min(y_coords), max(y_coords)


def quantile_class(series: pd.Series, classes: int = 3) -> pd.Series:
    """
    Assign stable 1..N quantile-style classes without depending on qcut.

    Ranking keeps the behavior deterministic even when the sample size is
    small or repeated values make exact quantile breaks awkward.
    """
    numeric = pd.to_numeric(series, errors="coerce")
    ranked = numeric.rank(method="average", pct=True)
    out = ranked.apply(
        lambda value: None
        if pd.isna(value)
        else max(1, min(classes, int(math.ceil(float(value) * classes))))
    )
    return out.astype("Int64")
