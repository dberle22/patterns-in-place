"""Shared spatial helpers used by pipelines and app modules."""

from shapely import wkt
from shapely.geometry import mapping
import pandas as pd


def wkt_to_polygon_coords(geom_wkt: str) -> list[list[list[float]]] | None:
    """
    Converts a WKT polygon/multipolygon string into the nested coordinate
    list format that PyDeck's PolygonLayer expects:
      [ [ [lon, lat], [lon, lat], ... ] ]   <- one ring per polygon part

    Returns None for null or invalid geometries so callers can filter them out.
    """
    if not geom_wkt:
        return None
    try:
        geom = wkt.loads(geom_wkt)
    except Exception:
        return None

    geom_type = geom.geom_type

    if geom_type == "Polygon":
        # exterior ring only — holes are uncommon in parcel/tract data
        return [list(geom.exterior.coords)]

    if geom_type == "MultiPolygon":
        # flatten each sub-polygon's exterior ring into the list
        return [list(part.exterior.coords) for part in geom.geoms]

    return None


def wkt_to_centroid(geom_wkt: str) -> tuple[float, float] | None:
    """Returns (lat, lon) centroid of a WKT geometry, or None if invalid."""
    if not geom_wkt:
        return None
    try:
        centroid = wkt.loads(geom_wkt).centroid
        return centroid.y, centroid.x  # lat, lon
    except Exception:
        return None


def wkt_to_area_sqmi(geom_wkt: str) -> float | None:
    """
    Approximates area in square miles from a WKT geometry in EPSG:4326.
    Uses a quick degree-to-meters conversion — good enough for parcel sizing,
    not for precise engineering measurements.
    """
    if not geom_wkt:
        return None
    try:
        geom = wkt.loads(geom_wkt)
        # Project to a local equal-area CRS via GeoDataFrame for accuracy.
        import geopandas as gpd

        gdf = gpd.GeoDataFrame(geometry=[geom], crs="EPSG:4326")
        gdf = gdf.to_crs("EPSG:5070")  # Conus Albers — accurate for SE US
        area_m2 = gdf.geometry.area.iloc[0]
        return area_m2 / 2_589_988.11  # m² → sq mi
    except Exception:
        return None


def add_polygon_coords(df: pd.DataFrame, wkt_col: str = "geom_wkt") -> pd.DataFrame:
    """
    Adds a 'polygon_coords' column to df, parsed from a WKT column.
    Rows with null/invalid geometry will have polygon_coords = None.
    PyDeck PolygonLayer filters out None rows automatically.
    """
    df = df.copy()
    df["polygon_coords"] = df[wkt_col].apply(wkt_to_polygon_coords)
    return df
