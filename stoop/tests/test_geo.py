import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon

from nyc_property_finder.utils.geo import points_from_lon_lat, spatial_join_points_to_polygons


def test_spatial_join_points_to_polygons_assigns_polygon_attributes() -> None:
    points = points_from_lon_lat(
        pd.DataFrame(
            [
                {"property_id": "p1", "lat": 0.5, "lon": 0.5},
                {"property_id": "p2", "lat": 2.5, "lon": 2.5},
            ]
        )
    )
    polygons = gpd.GeoDataFrame(
        [{"tract_id": "t1", "geometry": Polygon([(0, 0), (1, 0), (1, 1), (0, 1)])}],
        crs="EPSG:4326",
    )

    joined = spatial_join_points_to_polygons(
        points=points,
        polygons=polygons,
        point_columns=["property_id"],
        polygon_columns=["tract_id"],
    )

    assert joined.loc[joined["property_id"] == "p1", "tract_id"].iloc[0] == "t1"
    assert pd.isna(joined.loc[joined["property_id"] == "p2", "tract_id"].iloc[0])
