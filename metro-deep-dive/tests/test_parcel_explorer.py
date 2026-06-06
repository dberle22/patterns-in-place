"""Tests for parcel_explorer helper functions (pure unit tests, no database required)."""

import pandas as pd
import pytest
import pydeck as pdk

from retail_opportunity_finder.app.parcel_explorer import (
    SHORTLIST_STATUSES,
    SORT_OPTIONS,
    apply_filters,
    apply_sort,
    build_out_of_zone_layer,
    build_parcel_layer,
    build_parcel_scatter_layer,
    build_selected_layer,
    score_status,
)

_SQUARE_WKT = "POLYGON ((-81.7 30.3, -81.6 30.3, -81.6 30.4, -81.7 30.4, -81.7 30.3))"


def _make_parcel_df():
    return pd.DataFrame(
        {
            "parcel_uid": ["p1", "p2", "p3", "p4"],
            "county_name": ["Duval County", "Clay County", "Duval County", "Nassau County"],
            "zone_id": ["cluster_01", "cluster_02", "cluster_01", "cluster_03"],
            "zone_label": ["Zone A", "Zone B", "Zone A", "Zone C"],
            "retail_subtype": ["commercial_vacant", "restaurant", "parking_lot", "restaurant"],
            "just_value": [500_000.0, 1_000_000.0, 200_000.0, 3_000_000.0],
            "parcel_area_sqmi": [0.005, 0.010, 0.002, 0.020],
            "shortlist_score": [0.75, 0.60, 0.50, 0.80],
            "zone_quality_score": [0.90, 0.70, 0.80, 0.65],
            "parcel_characteristics_score": [0.55, 0.60, 0.45, 0.70],
            "last_sale_date": pd.to_datetime(["2024-01-01", "2023-06-15", "2022-03-20", "2025-02-28"]),
            "centroid_lat": [30.33, 30.34, 30.35, 30.36],
            "centroid_lon": [-81.66, -81.67, -81.68, -81.69],
            "geom_wkt": [_SQUARE_WKT, _SQUARE_WKT, None, _SQUARE_WKT],
            "user_status": [None, "active", None, "rejected"],
        }
    )


class TestScoreStatus:
    def test_positive_value_is_scored(self):
        assert score_status(0.75) == "scored"

    def test_zero_is_partial(self):
        assert score_status(0.0) == "partial"

    def test_negative_is_partial(self):
        assert score_status(-0.1) == "partial"

    def test_none_is_unavailable(self):
        assert score_status(None) == "unavailable"

    def test_nan_is_unavailable(self):
        import math
        assert score_status(float("nan")) == "unavailable"


class TestApplyFilters:
    def test_empty_filters_keeps_all_rows(self):
        df = _make_parcel_df()
        result = apply_filters(df, {})
        assert len(result) == len(df)

    def test_county_filter(self):
        df = _make_parcel_df()
        result = apply_filters(df, {"counties": ["Duval County"]})
        assert list(result["county_name"].unique()) == ["Duval County"]
        assert len(result) == 2

    def test_zone_filter(self):
        df = _make_parcel_df()
        result = apply_filters(df, {"zone_ids": ["cluster_01"]})
        assert len(result) == 2
        assert all(result["zone_id"] == "cluster_01")

    def test_subtype_filter(self):
        df = _make_parcel_df()
        result = apply_filters(df, {"subtypes": ["restaurant"]})
        assert all(result["retail_subtype"] == "restaurant")
        assert len(result) == 2

    def test_val_range_filter(self):
        df = _make_parcel_df()
        result = apply_filters(df, {"val_range": (400_000, 1_100_000)})
        assert all(result["just_value"].between(400_000, 1_100_000))
        assert len(result) == 2

    def test_area_range_filter(self):
        df = _make_parcel_df()
        result = apply_filters(df, {"area_range": (0.006, 0.025)})
        assert len(result) == 2

    def test_min_shortlist_score_filter(self):
        df = _make_parcel_df()
        result = apply_filters(df, {"min_shortlist_score": 0.70})
        assert all(result["shortlist_score"] >= 0.70)
        assert len(result) == 2

    def test_status_filter_active(self):
        df = _make_parcel_df()
        result = apply_filters(df, {"status_filter": "Active"})
        assert all(result["user_status"] == "active")
        assert len(result) == 1

    def test_status_filter_unreviewed(self):
        df = _make_parcel_df()
        result = apply_filters(df, {"status_filter": "Unreviewed"})
        assert all(result["user_status"].isna())
        assert len(result) == 2

    def test_status_filter_all_keeps_all(self):
        df = _make_parcel_df()
        result = apply_filters(df, {"status_filter": "All"})
        assert len(result) == len(df)

    def test_combined_filters(self):
        df = _make_parcel_df()
        result = apply_filters(
            df,
            {"counties": ["Duval County"], "subtypes": ["commercial_vacant"]},
        )
        assert len(result) == 1
        assert result.iloc[0]["parcel_uid"] == "p1"

    def test_result_index_reset(self):
        df = _make_parcel_df()
        result = apply_filters(df, {"counties": ["Clay County"]})
        assert list(result.index) == list(range(len(result)))


class TestApplySort:
    def test_best_opportunity_descending(self):
        df = _make_parcel_df()
        result = apply_sort(df, "Best opportunity")
        assert result["shortlist_score"].iloc[0] == result["shortlist_score"].max()

    def test_strongest_zone_descending(self):
        df = _make_parcel_df()
        result = apply_sort(df, "Strongest zone")
        assert result["zone_quality_score"].iloc[0] == result["zone_quality_score"].max()

    def test_lowest_assessed_value_ascending(self):
        df = _make_parcel_df()
        result = apply_sort(df, "Lowest assessed value")
        assert result["just_value"].iloc[0] == result["just_value"].min()

    def test_newest_sale_descending(self):
        df = _make_parcel_df()
        result = apply_sort(df, "Newest sale")
        assert result["last_sale_date"].iloc[0] == result["last_sale_date"].max()

    def test_unknown_sort_key_falls_back(self):
        df = _make_parcel_df()
        result = apply_sort(df, "nonexistent")  # should not raise
        assert len(result) == len(df)

    def test_result_index_reset(self):
        df = _make_parcel_df()
        result = apply_sort(df, "Best opportunity")
        assert list(result.index) == list(range(len(result)))

    def test_all_sort_options_run_without_error(self):
        df = _make_parcel_df()
        for opt in SORT_OPTIONS:
            apply_sort(df, opt)  # must not raise


class TestBuildLayers:
    def test_parcel_layer_is_polygon(self):
        df = _make_parcel_df()
        layer = build_parcel_layer(df, color_by="subtype")
        assert isinstance(layer, pdk.Layer)
        assert layer.type == "PolygonLayer"

    def test_parcel_layer_score_coloring(self):
        df = _make_parcel_df()
        layer = build_parcel_layer(df, color_by="score")
        assert isinstance(layer, pdk.Layer)

    def test_parcel_layer_filters_null_geometry(self):
        df = _make_parcel_df()  # row 2 has None geom_wkt
        layer = build_parcel_layer(df, color_by="subtype")
        assert len(layer.data) == 3  # one null geometry dropped

    def test_scatter_layer_is_scatterplot(self):
        df = _make_parcel_df()
        layer = build_parcel_scatter_layer(df)
        assert isinstance(layer, pdk.Layer)
        assert layer.type == "ScatterplotLayer"

    def test_scatter_layer_filters_null_centroids(self):
        df = _make_parcel_df()
        df.loc[0, "centroid_lat"] = None
        layer = build_parcel_scatter_layer(df)
        assert len(layer.data) == 3

    def test_out_of_zone_layer_is_scatterplot(self):
        df = pd.DataFrame({
            "centroid_lat": [30.33, None, 30.35],
            "centroid_lon": [-81.66, -81.67, -81.68],
            "retail_subtype": ["commercial_vacant", "restaurant", "parking_lot"],
        })
        layer = build_out_of_zone_layer(df)
        assert isinstance(layer, pdk.Layer)
        assert layer.type == "ScatterplotLayer"
        assert len(layer.data) == 2  # null centroid dropped

    def test_selected_layer_returns_none_for_null_centroid(self):
        row = pd.Series({"centroid_lat": None, "centroid_lon": -81.66})
        assert build_selected_layer(row) is None

    def test_selected_layer_returns_scatterplot_for_valid_centroid(self):
        row = pd.Series({"centroid_lat": 30.33, "centroid_lon": -81.66})
        layer = build_selected_layer(row)
        assert isinstance(layer, pdk.Layer)
        assert layer.type == "ScatterplotLayer"


class TestConstants:
    def test_shortlist_statuses(self):
        assert set(SHORTLIST_STATUSES) == {"active", "needs_review", "watchlist", "rejected"}

    def test_sort_options_count(self):
        assert len(SORT_OPTIONS) == 7
