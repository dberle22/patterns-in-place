"""Tests for geo utility functions (pure unit tests, no database required)."""

import pandas as pd
import pytest

from retail_opportunity_finder.utils.geo import (
    add_polygon_coords,
    wkt_to_area_sqmi,
    wkt_to_centroid,
    wkt_to_polygon_coords,
)

_SQUARE_WKT = "POLYGON ((-81.7 30.3, -81.6 30.3, -81.6 30.4, -81.7 30.4, -81.7 30.3))"
_MULTI_WKT = (
    "MULTIPOLYGON (((-81.7 30.3, -81.6 30.3, -81.6 30.4, -81.7 30.3)), "
    "((-81.5 30.3, -81.4 30.3, -81.4 30.4, -81.5 30.3)))"
)


class TestWktToPolygonCoords:
    def test_simple_polygon_returns_ring(self):
        coords = wkt_to_polygon_coords(_SQUARE_WKT)
        assert coords is not None
        assert len(coords) == 1
        assert all(len(pt) == 2 for pt in coords[0])

    def test_multipolygon_returns_multiple_rings(self):
        coords = wkt_to_polygon_coords(_MULTI_WKT)
        assert coords is not None
        assert len(coords) == 2

    def test_none_returns_none(self):
        assert wkt_to_polygon_coords(None) is None

    def test_empty_string_returns_none(self):
        assert wkt_to_polygon_coords("") is None

    def test_invalid_wkt_returns_none(self):
        assert wkt_to_polygon_coords("NOT WKT") is None

    def test_point_wkt_returns_none(self):
        assert wkt_to_polygon_coords("POINT (-81.6 30.3)") is None


class TestWktToCentroid:
    def test_centroid_near_center(self):
        lat, lon = wkt_to_centroid(_SQUARE_WKT)
        assert abs(lat - 30.35) < 0.01
        assert abs(lon - (-81.65)) < 0.01

    def test_returns_lat_lon_order(self):
        lat, lon = wkt_to_centroid(_SQUARE_WKT)
        assert 25 < lat < 35   # Florida latitude range
        assert -90 < lon < -75  # Florida longitude range

    def test_none_returns_none(self):
        assert wkt_to_centroid(None) is None

    def test_invalid_returns_none(self):
        assert wkt_to_centroid("GARBAGE") is None


class TestWktToAreaSqmi:
    def test_returns_positive_float(self):
        area = wkt_to_area_sqmi(_SQUARE_WKT)
        assert area is not None
        assert area > 0

    def test_larger_polygon_has_larger_area(self):
        big = "POLYGON ((-82.0 30.0, -81.0 30.0, -81.0 31.0, -82.0 31.0, -82.0 30.0))"
        small = _SQUARE_WKT
        assert wkt_to_area_sqmi(big) > wkt_to_area_sqmi(small)

    def test_none_returns_none(self):
        assert wkt_to_area_sqmi(None) is None

    def test_invalid_returns_none(self):
        assert wkt_to_area_sqmi("GARBAGE") is None


class TestAddPolygonCoords:
    def test_adds_column(self):
        df = pd.DataFrame({"geom_wkt": [_SQUARE_WKT, None, "GARBAGE"]})
        result = add_polygon_coords(df)
        assert "polygon_coords" in result.columns

    def test_valid_wkt_gets_coords(self):
        df = pd.DataFrame({"geom_wkt": [_SQUARE_WKT]})
        result = add_polygon_coords(df)
        assert result["polygon_coords"].iloc[0] is not None

    def test_null_wkt_gets_none(self):
        df = pd.DataFrame({"geom_wkt": [None]})
        result = add_polygon_coords(df)
        assert result["polygon_coords"].iloc[0] is None

    def test_invalid_wkt_gets_none(self):
        df = pd.DataFrame({"geom_wkt": ["NOT WKT"]})
        result = add_polygon_coords(df)
        assert result["polygon_coords"].iloc[0] is None

    def test_does_not_mutate_original(self):
        df = pd.DataFrame({"geom_wkt": [_SQUARE_WKT]})
        original_cols = list(df.columns)
        add_polygon_coords(df)
        assert list(df.columns) == original_cols
