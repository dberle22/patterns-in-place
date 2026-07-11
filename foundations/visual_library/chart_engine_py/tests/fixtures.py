"""
Deterministic fixture builders for chart-engine regression tests.

These helpers keep the test inputs aligned to each generated chart spec so
golden snapshots fail only when the renderer contract changes, not because
each test hand-built slightly different input shapes.
"""

from __future__ import annotations

import pandas as pd


def scatter_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa", "cbsa", "cbsa"],
            "geo_id": ["1", "2", "3"],
            "geo_name": ["A", "B", "C"],
            "time_window": ["2023", "2023", "2023"],
            "x_value": [10.0, 12.0, 15.0],
            "y_value": [20.0, 22.0, 28.0],
            "x_label": ["X metric", "X metric", "X metric"],
            "y_label": ["Y metric", "Y metric", "Y metric"],
            "group": ["South", "South", "West"],
            "size_value": [100, 200, 150],
            "label_flag": [False, True, False],
            "source": ["ACS", "ACS", "ACS"],
            "vintage": ["2023", "2023", "2023"],
        }
    )


def slopegraph_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa", "cbsa", "cbsa", "cbsa"],
            "geo_id": ["1", "1", "2", "2"],
            "geo_name": ["A", "A", "B", "B"],
            "period": ["2019", "2023", "2019", "2023"],
            "metric_id": ["m1", "m1", "m1", "m1"],
            "metric_label": ["Jobs", "Jobs", "Jobs", "Jobs"],
            "metric_value": [10.0, 15.0, 12.0, 13.0],
            "highlight_flag": [True, True, False, False],
            "source": ["ACS", "ACS", "ACS", "ACS"],
            "vintage": ["2023", "2023", "2023", "2023"],
        }
    )


def boxplot_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa", "cbsa", "cbsa", "cbsa"],
            "geo_id": ["1", "2", "3", "4"],
            "geo_name": ["A", "B", "C", "D"],
            "time_window": ["2023", "2023", "2023", "2023"],
            "metric_id": ["m1", "m1", "m1", "m1"],
            "metric_label": ["Jobs", "Jobs", "Jobs", "Jobs"],
            "metric_value": [10.0, 12.0, 16.0, 20.0],
            "group": ["East", "East", "West", "West"],
            "highlight_flag": [False, True, False, False],
            "source": ["ACS", "ACS", "ACS", "ACS"],
            "vintage": ["2023", "2023", "2023", "2023"],
        }
    )


def heatmap_table_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa", "cbsa", "cbsa", "cbsa"],
            "geo_id": ["1", "1", "2", "2"],
            "geo_name": ["A", "A", "B", "B"],
            "metric_id": ["m1", "m2", "m1", "m2"],
            "metric_label": ["Jobs", "Income", "Jobs", "Income"],
            "metric_value": [10.0, 20.0, 30.0, 40.0],
            "normalized_value": [0.1, 0.3, 0.7, 0.9],
            "source": ["ACS", "ACS", "ACS", "ACS"],
            "vintage": ["2023", "2023", "2023", "2023"],
        }
    )


def bump_chart_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa", "cbsa", "cbsa", "cbsa", "cbsa", "cbsa"],
            "geo_id": ["1", "1", "2", "2", "3", "3"],
            "geo_name": ["A", "A", "B", "B", "C", "C"],
            "period": ["2019", "2023", "2019", "2023", "2019", "2023"],
            "metric_id": ["m1", "m1", "m1", "m1", "m1", "m1"],
            "metric_label": ["Jobs", "Jobs", "Jobs", "Jobs", "Jobs", "Jobs"],
            "metric_value": [10.0, 15.0, 20.0, 18.0, 30.0, 25.0],
            "source": ["ACS", "ACS", "ACS", "ACS", "ACS", "ACS"],
            "vintage": ["2023", "2023", "2023", "2023", "2023", "2023"],
        }
    )


def waterfall_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa", "cbsa", "cbsa"],
            "geo_id": ["1", "1", "1"],
            "geo_name": ["A", "A", "A"],
            "time_window": ["2023", "2023", "2023"],
            "total_label": ["Total", "Total", "Total"],
            "component_id": ["c1", "c2", "c3"],
            "component_label": ["Base", "Growth", "Adjustment"],
            "component_value": [100.0, 20.0, -10.0],
            "sort_order": [1, 2, 3],
            "source": ["ACS", "ACS", "ACS"],
            "vintage": ["2023", "2023", "2023"],
        }
    )


def strength_strip_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa", "cbsa", "cbsa", "cbsa"],
            "geo_id": ["1", "2", "1", "2"],
            "geo_name": ["A", "B", "A", "B"],
            "time_window": ["2023", "2023", "2023", "2023"],
            "metric_id": ["m1", "m1", "m2", "m2"],
            "metric_label": ["Jobs", "Jobs", "Income", "Income"],
            "metric_value": [10.0, 20.0, 30.0, 40.0],
            "normalized_value": [25.0, 75.0, 40.0, 90.0],
            "source": ["ACS", "ACS", "ACS", "ACS"],
            "vintage": ["2023", "2023", "2023", "2023"],
        }
    )


def correlation_heatmap_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa", "cbsa", "cbsa", "cbsa", "cbsa", "cbsa"],
            "geo_id": ["1", "1", "2", "2", "3", "3"],
            "geo_name": ["A", "A", "B", "B", "C", "C"],
            "time_window": ["2023", "2023", "2023", "2023", "2023", "2023"],
            "metric_id": ["m1", "m2", "m1", "m2", "m1", "m2"],
            "metric_label": ["Jobs", "Income", "Jobs", "Income", "Jobs", "Income"],
            "metric_value": [10.0, 20.0, 30.0, 10.0, 50.0, 40.0],
            "source": ["ACS", "ACS", "ACS", "ACS", "ACS", "ACS"],
            "vintage": ["2023", "2023", "2023", "2023", "2023", "2023"],
        }
    )


def age_pyramid_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa", "cbsa", "cbsa", "cbsa", "cbsa", "cbsa"],
            "geo_id": ["1", "1", "1", "1", "1", "1"],
            "geo_name": ["A", "A", "A", "A", "A", "A"],
            "period": ["2023", "2023", "2023", "2023", "2023", "2023"],
            "age_bin": ["0-17", "18-34", "35-64", "0-17", "18-34", "35-64"],
            "sex": ["Male", "Male", "Male", "Female", "Female", "Female"],
            "pop_value": [100, 120, 80, 95, 130, 90],
            "source": ["ACS", "ACS", "ACS", "ACS", "ACS", "ACS"],
            "vintage": ["2023", "2023", "2023", "2023", "2023", "2023"],
        }
    )


def choropleth_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["county", "county"],
            "geo_id": ["1", "2"],
            "geo_name": ["Alpha", "Beta"],
            "time_window": ["2023", "2023"],
            "metric_value": [12.0, 24.0],
            "metric_label": ["Rent burden", "Rent burden"],
            "geometry": [
                [(0, 0), (1, 0), (1, 1), (0, 1)],
                [(1.2, 0), (2.2, 0), (2.2, 1), (1.2, 1)],
            ],
            "highlight_flag": [True, False],
            "source": ["ACS", "ACS"],
            "vintage": ["2023", "2023"],
        }
    )


def hexbin_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["tract"] * 6,
            "geo_id": ["1", "2", "3", "4", "5", "6"],
            "geo_name": ["A", "B", "C", "D", "E", "F"],
            "time_window": ["2023"] * 6,
            "x_value": [1.0, 1.3, 1.5, 2.0, 2.2, 2.5],
            "y_value": [4.0, 4.2, 4.5, 5.0, 5.1, 5.4],
            "x_label": ["Income", "Income", "Income", "Income", "Income", "Income"],
            "y_label": ["Burden", "Burden", "Burden", "Burden", "Burden", "Burden"],
            "highlight_flag": [False, False, True, False, False, False],
            "source": ["ACS"] * 6,
            "vintage": ["2023"] * 6,
        }
    )


def highlight_context_map_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["county", "county", "county"],
            "geo_id": ["1", "2", "3"],
            "geo_name": ["Target", "Neighbor", "Context"],
            "time_window": ["2023", "2023", "2023"],
            "highlight_flag": [True, False, False],
            "neighbor_flag": [False, True, False],
            "metric_value": [20.0, 14.0, 10.0],
            "metric_label": ["Jobs", "Jobs", "Jobs"],
            "geometry": [
                [(0, 0), (1, 0), (1, 1), (0, 1)],
                [(1.1, 0), (2.1, 0), (2.1, 1), (1.1, 1)],
                [(0.5, 1.2), (1.5, 1.2), (1.5, 2.2), (0.5, 2.2)],
            ],
            "source": ["ACS", "ACS", "ACS"],
            "vintage": ["2023", "2023", "2023"],
        }
    )


def proportional_symbol_map_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa", "cbsa", "cbsa"],
            "geo_id": ["1", "2", "3"],
            "geo_name": ["A", "B", "C"],
            "time_window": ["2023", "2023", "2023"],
            "size_value": [100.0, 250.0, 175.0],
            "size_label": ["Population", "Population", "Population"],
            "lon": [-77.4, -77.0, -76.6],
            "lat": [37.5, 37.8, 37.4],
            "highlight_flag": [False, True, False],
            "label_flag": [False, True, False],
            "source": ["ACS", "ACS", "ACS"],
            "vintage": ["2023", "2023", "2023"],
        }
    )


def bivariate_choropleth_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["county", "county", "county"],
            "geo_id": ["1", "2", "3"],
            "geo_name": ["A", "B", "C"],
            "time_window": ["2023", "2023", "2023"],
            "x_value": [10.0, 20.0, 30.0],
            "y_value": [30.0, 20.0, 10.0],
            "x_label": ["Growth", "Growth", "Growth"],
            "y_label": ["Affordability", "Affordability", "Affordability"],
            "geometry": [
                [(0, 0), (1, 0), (1, 1), (0, 1)],
                [(1.1, 0), (2.1, 0), (2.1, 1), (1.1, 1)],
                [(2.2, 0), (3.2, 0), (3.2, 1), (2.2, 1)],
            ],
            "highlight_flag": [False, True, False],
            "source": ["ACS", "ACS", "ACS"],
            "vintage": ["2023", "2023", "2023"],
        }
    )
