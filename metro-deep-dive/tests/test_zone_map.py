"""Tests for zone_map helper functions (pure unit tests, no database required)."""

import pandas as pd
import pytest
import pydeck as pdk

from retail_opportunity_finder.app.zone_map import (
    apply_color_ramp,
    build_label_layer,
    build_metric_options,
    build_tooltip,
    build_tract_layer,
    build_zone_layer,
)

_SQUARE_WKT = "POLYGON ((-81.7 30.3, -81.6 30.3, -81.6 30.4, -81.7 30.4, -81.7 30.3))"


def _make_tract_df(n=5):
    return pd.DataFrame(
        {
            "tract_geoid": [f"1203100{i:04d}" for i in range(n)],
            "geom_wkt": [_SQUARE_WKT] * (n - 1) + [None],
            "pop_total": [1000.0 * (i + 1) for i in range(n - 1)] + [None],
            "pop_growth_3yr": [0.05, -0.02, 0.10, 0.01, None],
            "tract_score": [0.6, 0.4, 0.8, None, 0.5],
            "gate_pop": [1, 0, 1, 1, None],
            "pov_rate": [0.10, 0.25, 0.05, 0.30, None],
        }
    )


def _make_zone_df(n=3):
    return pd.DataFrame(
        {
            "zone_id": [f"cluster_0{i}" for i in range(1, n + 1)],
            "zone_label": [f"Zone {chr(64+i)}" for i in range(1, n + 1)],
            "zone_order": list(range(1, n + 1)),
            "label_lon": [-81.65, -81.55, None],
            "label_lat": [30.35, 30.45, None],
            "geom_wkt": [_SQUARE_WKT, _SQUARE_WKT, None],
            "tracts": [7, 5, 3],
            "total_population": [70000.0, 50000.0, 30000.0],
            "pop_growth_3yr_wtd": [0.3, 0.2, 0.1],
            "mean_tract_score": [0.8, 0.6, 0.4],
        }
    )


class TestBuildMetricOptions:
    def test_returns_ordered_dict(self):
        from collections import OrderedDict
        opts = build_metric_options()
        assert isinstance(opts, OrderedDict)

    def test_has_expected_count(self):
        opts = build_metric_options()
        assert len(opts) == 16

    def test_keys_are_strings(self):
        for k in build_metric_options():
            assert isinstance(k, str)

    def test_values_are_column_names(self):
        expected_cols = {
            "pop_total", "pop_growth_3yr", "median_hh_income", "per_capita_income",
            "pov_rate", "median_gross_rent", "median_home_value", "pop_density",
            "units_per_1k_3yr", "tract_score", "gate_pop", "gate_price",
            "gate_density", "retail_parcel_count", "retail_area_density",
            "local_retail_context_score",
        }
        assert set(build_metric_options().values()) == expected_cols

    def test_no_duplicate_values(self):
        vals = list(build_metric_options().values())
        assert len(vals) == len(set(vals))


class TestApplyColorRamp:
    def test_adds_fill_color_column(self):
        df = _make_tract_df()
        result = apply_color_ramp(df, "pop_total")
        assert "fill_color" in result.columns

    def test_null_row_gets_null_color(self):
        df = _make_tract_df()
        result = apply_color_ramp(df, "pop_total")
        null_idx = df[df["pop_total"].isna()].index[0]
        # After reset_index the position may shift; find the null in result
        null_colors = [
            c for c, v in zip(result["fill_color"], result["pop_total"])
            if pd.isna(v)
        ]
        assert null_colors[0] == [160, 160, 160, 80]

    def test_gate_pass_gets_green(self):
        df = _make_tract_df()
        result = apply_color_ramp(df, "gate_pop")
        pass_colors = [
            c for c, v in zip(result["fill_color"], result["gate_pop"])
            if pd.notna(v) and int(v) == 1
        ]
        assert all(c == [40, 167, 69, 200] for c in pass_colors)

    def test_gate_fail_gets_red(self):
        df = _make_tract_df()
        result = apply_color_ramp(df, "gate_pop")
        fail_colors = [
            c for c, v in zip(result["fill_color"], result["gate_pop"])
            if pd.notna(v) and int(v) == 0
        ]
        assert all(c == [220, 53, 69, 200] for c in fail_colors)

    def test_inverted_metric_high_value_gets_low_rank_color(self):
        # pov_rate is inverted: highest poverty → lowest rank → lightest color
        df = pd.DataFrame({"pov_rate": [0.05, 0.30]})  # 0.30 is worst (highest)
        result = apply_color_ramp(df, "pov_rate")
        # Index 0 (0.05 = low pov, inverted = high rank) should be darker blue
        # Index 1 (0.30 = high pov, inverted = low rank) should be lighter
        color_low_pov = result["fill_color"].iloc[0]
        color_high_pov = result["fill_color"].iloc[1]
        # Red channel: high rank → closer to HI_COLOR red=8, low rank → LO_COLOR red=239
        assert color_low_pov[0] < color_high_pov[0]

    def test_does_not_mutate_input(self):
        df = _make_tract_df()
        cols_before = list(df.columns)
        apply_color_ramp(df, "pop_total")
        assert list(df.columns) == cols_before

    def test_all_null_column_gives_null_color_for_all(self):
        df = pd.DataFrame({"x": [None, None, None]})
        result = apply_color_ramp(df, "x")
        assert all(c == [160, 160, 160, 80] for c in result["fill_color"])


class TestBuildLayers:
    def test_build_tract_layer_type(self):
        df = _make_tract_df()
        colored = apply_color_ramp(df, "pop_total")
        layer = build_tract_layer(colored)
        assert isinstance(layer, pdk.Layer)
        assert layer.type == "PolygonLayer"

    def test_build_zone_layer_type(self):
        df = _make_zone_df()
        layer = build_zone_layer(df)
        assert isinstance(layer, pdk.Layer)
        assert layer.type == "PolygonLayer"

    def test_build_label_layer_type(self):
        df = _make_zone_df()
        layer = build_label_layer(df)
        assert isinstance(layer, pdk.Layer)
        assert layer.type == "TextLayer"

    def test_label_layer_drops_null_centroids(self):
        df = _make_zone_df()  # third row has None lat/lon
        layer = build_label_layer(df)
        # Layer data should have 2 rows (null centroid row dropped)
        assert len(layer.data) == 2


class TestBuildTooltip:
    def test_tract_tooltip_has_html_and_style(self):
        t = build_tooltip("tract")
        assert "html" in t and "style" in t

    def test_zone_tooltip_has_html_and_style(self):
        t = build_tooltip("zone")
        assert "html" in t and "style" in t

    def test_tract_tooltip_references_tract_fields(self):
        html = build_tooltip("tract")["html"]
        assert "tract_geoid" in html
        assert "pop_total" in html

    def test_zone_tooltip_references_zone_fields(self):
        html = build_tooltip("zone")["html"]
        assert "zone_label" in html
        assert "total_population" in html

    def test_unknown_type_returns_empty(self):
        assert build_tooltip("unknown") == {}
