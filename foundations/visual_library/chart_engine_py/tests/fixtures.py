"""
Deterministic fixture builders for chart-engine regression tests.

These helpers keep the test inputs aligned to each generated chart spec so
golden snapshots fail only when the renderer contract changes, not because
each test hand-built slightly different input shapes.
"""

from __future__ import annotations

import pandas as pd


def bar_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa", "cbsa", "cbsa"],
            "geo_id": ["33100", "35620", "16980"],
            "geo_name": ["Miami-Fort Lauderdale-West Palm Beach, FL", "New York-Newark-Jersey City, NY-NJ-PA", "Chicago-Naperville-Elgin, IL-IN-WI"],
            "time_window": ["2023 level", "2023 level", "2023 level"],
            "metric_id": ["rent_burden", "rent_burden", "rent_burden"],
            "metric_label": ["Share of renter households spending 30%+ of income on rent"] * 3,
            "metric_value": [63.1, 57.4, 49.8],
            "rank": [1, 2, 3],
            "group": ["Top CBSAs by renter cost burden"] * 3,
            "highlight_flag": [True, False, False],
            "benchmark_value": [50.4, 50.4, 50.4],
            "note": ["Population filter: 250k+ | US benchmark shown for reference"] * 3,
            "source": ["ACS", "ACS", "ACS"],
            "vintage": ["2023", "2023", "2023"],
        }
    )


def line_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "period": ["2019", "2020", "2021", "2022", "2019", "2020", "2021", "2022"],
            "value": [100.0, 104.0, 108.0, 111.0, 100.0, 101.0, 103.0, 106.0],
            "series": ["Wilmington"] * 4 + ["Peer Average"] * 4,
            "metric_label": ["Per-capita income index"] * 8,
            "geo_name": ["Wilmington, NC"] * 4 + ["Peer Average"] * 4,
            "highlight_flag": [True] * 4 + [False] * 4,
            "benchmark_value": [102.0, 103.0, 104.0, 105.0, 102.0, 103.0, 104.0, 105.0],
            "time_window": ["indexed"] * 8,
            "index_base_period": [2019] * 8,
            "group": ["South Atlantic"] * 8,
            "source": ["BEA"] * 8,
            "vintage": ["2024"] * 8,
            "note": ["Indexed to 2019 to compare pace of change rather than absolute level."] * 8,
        }
    )


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
            "geo_level": ["cbsa"] * 6,
            "geo_id": ["1", "1", "2", "2", "3", "3"],
            "geo_name": ["A", "A", "B", "B", "National Benchmark", "National Benchmark"],
            "period": ["2019", "2023", "2019", "2023", "2019", "2023"],
            "metric_id": ["m1"] * 6,
            "metric_label": ["Jobs"] * 6,
            "metric_value": [10.0, 15.0, 12.0, 13.0, 11.0, 14.0],
            "highlight_flag": [True, True, False, False, False, False],
            "benchmark_label": [None, None, None, None, "US", "US"],
            "group": ["Peer CBSAs"] * 6,
            "source": ["ACS"] * 6,
            "vintage": ["2023"] * 6,
            "note": ["Benchmark line is shown for reference."] * 6,
        }
    )


def boxplot_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa"] * 6,
            "geo_id": ["1", "2", "3", "4", "5", "6"],
            "geo_name": ["A", "B", "C", "D", "E", "F"],
            "time_window": ["2023"] * 6,
            "metric_id": ["m1"] * 6,
            "metric_label": ["Jobs"] * 6,
            "metric_value": [10.0, 12.0, 16.0, 20.0, 14.0, 18.0],
            "group": ["East", "East", "West", "West", "South", "South"],
            "highlight_flag": [False, True, False, False, False, False],
            "label_flag": [False, True, False, False, False, False],
            "benchmark_value": [15.0] * 6,
            "source": ["ACS"] * 6,
            "vintage": ["2023"] * 6,
        }
    )


def heatmap_table_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa"] * 6,
            "geo_id": ["1", "1", "1", "2", "2", "2"],
            "geo_name": ["Target", "Target", "Target", "Peer", "Peer", "Peer"],
            "metric_id": ["m1", "m2", "m3", "m1", "m2", "m3"],
            "metric_label": ["Jobs", "Income", "Rent", "Jobs", "Income", "Rent"],
            "metric_value": [10.0, 20.0, 30.0, 30.0, 40.0, 25.0],
            "normalized_value": [0.1, 0.3, 0.8, 0.7, 0.9, 0.4],
            "metric_order": [1, 2, 3, 1, 2, 3],
            "row_order": [2, 2, 2, 1, 1, 1],
            "direction": ["higher_is_better", "higher_is_better", "lower_is_better", "higher_is_better", "higher_is_better", "lower_is_better"],
            "highlight_flag": [True, True, True, False, False, False],
            "time_window": ["2023"] * 6,
            "source": ["ACS"] * 6,
            "vintage": ["2023"] * 6,
        }
    )


def bump_chart_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa"] * 9,
            "geo_id": ["1", "1", "1", "2", "2", "2", "3", "3", "3"],
            "geo_name": ["A", "A", "A", "B", "B", "B", "C", "C", "C"],
            "period": ["2019", "2021", "2023"] * 3,
            "metric_id": ["m1"] * 9,
            "metric_label": ["Jobs"] * 9,
            "metric_value": [10.0, 13.0, 15.0, 20.0, 19.0, 18.0, 30.0, 28.0, 25.0],
            "highlight_flag": [True, True, True, False, False, False, False, False, False],
            "peer_flag": [True, True, True, False, False, False, True, True, True],
            "group": ["Peer universe"] * 9,
            "source": ["ACS"] * 9,
            "vintage": ["2023"] * 9,
        }
    )


def waterfall_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa"] * 6,
            "geo_id": ["1"] * 6,
            "geo_name": ["A"] * 6,
            "time_window": ["2023"] * 6,
            "total_label": ["Total"] * 6,
            "component_id": ["c1", "c2", "c3", "c1", "c2", "c3"],
            "component_label": ["Base", "Growth", "Adjustment", "Base", "Growth", "Adjustment"],
            "component_value": [100.0, 20.0, -10.0, 90.0, 15.0, -5.0],
            "sort_order": [1, 2, 3, 1, 2, 3],
            "benchmark_label": ["Target", "Target", "Target", "Benchmark", "Benchmark", "Benchmark"],
            "source": ["ACS"] * 6,
            "vintage": ["2023"] * 6,
        }
    )


def strength_strip_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa"] * 8,
            "geo_id": ["1", "2", "1", "2", "1", "2", "1", "2"],
            "geo_name": ["Target", "Peer", "Target", "Peer", "Target", "Peer", "Target", "Peer"],
            "time_window": ["level", "level", "level", "level", "growth", "growth", "growth", "growth"],
            "metric_id": ["m1", "m1", "m2", "m2", "m1", "m1", "m2", "m2"],
            "metric_label": ["Jobs", "Jobs", "Income", "Income", "Jobs", "Jobs", "Income", "Income"],
            "metric_value": [10.0, 20.0, 30.0, 40.0, 2.0, 5.0, -1.0, 3.0],
            "benchmark_value": [15.0, 15.0, 35.0, 35.0, 4.0, 4.0, 0.0, 0.0],
            "metric_group": ["Economy", "Economy", "Prosperity", "Prosperity", "Economy", "Economy", "Prosperity", "Prosperity"],
            "direction": ["higher_is_better", "higher_is_better", "higher_is_better", "higher_is_better", "higher_is_better", "higher_is_better", "higher_is_better", "higher_is_better"],
            "highlight_flag": [True, False, True, False, True, False, True, False],
            "benchmark_label": ["Benchmark"] * 8,
            "source": ["ACS"] * 8,
            "vintage": ["2023"] * 8,
        }
    )


def correlation_heatmap_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa"] * 18,
            "geo_id": ["1", "1", "1", "2", "2", "2", "3", "3", "3", "4", "4", "4", "5", "5", "5", "6", "6", "6"],
            "geo_name": ["A", "A", "A", "B", "B", "B", "C", "C", "C", "D", "D", "D", "E", "E", "E", "F", "F", "F"],
            "time_window": ["2023"] * 18,
            "metric_id": ["m1", "m2", "m3"] * 6,
            "metric_label": ["Jobs", "Income", "Rent"] * 6,
            "metric_value": [10.0, 20.0, 30.0, 30.0, 10.0, 28.0, 50.0, 40.0, 18.0, 20.0, 12.0, 22.0, 45.0, 32.0, 26.0, 15.0, 18.0, 29.0],
            "group": ["Target", "Target", "Target", "Target", "Target", "Target", "Target", "Target", "Target", "Benchmark", "Benchmark", "Benchmark", "Benchmark", "Benchmark", "Benchmark", "Benchmark", "Benchmark", "Benchmark"],
            "include_flag": [True] * 18,
            "source": ["ACS"] * 18,
            "vintage": ["2023"] * 18,
        }
    )


def age_pyramid_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa"] * 24,
            "geo_id": ["1"] * 12 + ["0"] * 12,
            "geo_name": ["Wilmington, NC"] * 12 + ["United States"] * 12,
            "period": ["2023"] * 6 + ["2024"] * 6 + ["2023"] * 6 + ["2024"] * 6,
            "age_bin": ["0-17", "18-34", "35-64", "0-17", "18-34", "35-64"] * 4,
            "sex": ["Male", "Male", "Male", "Female", "Female", "Female"] * 4,
            "pop_value": [
                100, 120, 80, 95, 130, 90,
                102, 124, 83, 97, 133, 92,
                98, 118, 96, 96, 121, 99,
                99, 119, 97, 97, 122, 100,
            ],
            "benchmark_label": [None] * 12 + ["United States"] * 12,
            "highlight_flag": [True] * 12 + [False] * 12,
            "source": ["ACS"] * 24,
            "vintage": ["2024"] * 24,
            "note": ["Bars show Wilmington shares; dashed outline shows US benchmark."] * 24,
        }
    )


def choropleth_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["county"] * 4,
            "geo_id": ["1", "2", "1", "2"],
            "geo_name": ["Alpha", "Beta", "Alpha", "Beta"],
            "time_window": ["2023", "2023", "2024", "2024"],
            "metric_value": [12.0, 24.0, 10.0, 30.0],
            "metric_label": ["Rent burden"] * 4,
            "benchmark_value": [18.0] * 4,
            "group": ["2023", "2023", "2024", "2024"],
            "geometry": [
                [(0, 0), (1, 0), (1, 1), (0, 1)],
                [(1.2, 0), (2.2, 0), (2.2, 1), (1.2, 1)],
                [(0, 0), (1, 0), (1, 1), (0, 1)],
                [(1.2, 0), (2.2, 0), (2.2, 1), (1.2, 1)],
            ],
            "highlight_flag": [True, False, True, False],
            "source": ["ACS"] * 4,
            "vintage": ["2024"] * 4,
        }
    )


def hexbin_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["tract"] * 8,
            "geo_id": ["1", "2", "3", "4", "5", "6", "7", "8"],
            "geo_name": ["A", "B", "C", "D", "E", "F", "G", "H"],
            "question_id": ["hexbin_regional_density_compare"] * 8,
            "time_window": ["2023"] * 8,
            "group": ["Target", "Target", "Target", "Target", "Peer", "Peer", "Peer", "Peer"],
            "x_value": [1.0, 1.3, 1.5, 2.0, 2.2, 2.5, 2.7, 3.0],
            "y_value": [4.0, 4.2, 4.5, 5.0, 5.1, 5.4, 5.6, 5.9],
            "weight_value": [120.0, 140.0, 160.0, 110.0, 180.0, 210.0, 190.0, 170.0],
            "x_label": ["Income"] * 8,
            "y_label": ["Burden"] * 8,
            "highlight_flag": [False, False, True, False, False, False, True, False],
            "label_flag": [False, False, True, False, False, False, True, False],
            "source": ["ACS"] * 8,
            "vintage": ["2023"] * 8,
        }
    )


def highlight_context_map_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["county"] * 6,
            "geo_id": ["1", "2", "3", "1", "2", "3"],
            "geo_name": ["Target", "Neighbor", "Context", "Target", "Neighbor", "Context"],
            "time_window": ["2023", "2023", "2023", "2024", "2024", "2024"],
            "highlight_flag": [True, False, False, True, False, False],
            "neighbor_flag": [False, True, False, False, True, False],
            "metric_value": [20.0, 14.0, 10.0, 18.0, 15.0, 9.0],
            "benchmark_value": [15.0] * 6,
            "metric_label": ["Jobs"] * 6,
            "geometry": [
                [(0, 0), (1, 0), (1, 1), (0, 1)],
                [(1.1, 0), (2.1, 0), (2.1, 1), (1.1, 1)],
                [(0.5, 1.2), (1.5, 1.2), (1.5, 2.2), (0.5, 2.2)],
                [(0, 0), (1, 0), (1, 1), (0, 1)],
                [(1.1, 0), (2.1, 0), (2.1, 1), (1.1, 1)],
                [(0.5, 1.2), (1.5, 1.2), (1.5, 2.2), (0.5, 2.2)],
            ],
            "label_flag": [True, False, False, True, False, False],
            "group": ["2023", "2023", "2023", "2024", "2024", "2024"],
            "source": ["ACS"] * 6,
            "vintage": ["2024"] * 6,
        }
    )


def proportional_symbol_map_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["cbsa"] * 4,
            "geo_id": ["1", "2", "3", "4"],
            "geo_name": ["A", "B", "C", "D"],
            "time_window": ["2023"] * 4,
            "size_value": [100.0, 250.0, 175.0, 90.0],
            "size_label": ["Population"] * 4,
            "lon": [-77.4, -77.0, -76.6, -76.9],
            "lat": [37.5, 37.8, 37.4, 37.1],
            "color_group": ["Target", "Target", "Peer", "Peer"],
            "highlight_flag": [False, True, False, False],
            "label_flag": [False, True, False, False],
            "source": ["ACS"] * 4,
            "vintage": ["2023"] * 4,
        }
    )


def bivariate_choropleth_fixture() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "geo_level": ["county"] * 6,
            "geo_id": ["1", "2", "3", "1", "2", "3"],
            "geo_name": ["A", "B", "C", "A", "B", "C"],
            "time_window": ["2023"] * 6,
            "x_value": [10.0, 20.0, 30.0, 12.0, 25.0, 35.0],
            "y_value": [30.0, 20.0, 10.0, 28.0, 18.0, 12.0],
            "x_label": ["Growth"] * 6,
            "y_label": ["Affordability"] * 6,
            "group": ["Target", "Target", "Target", "Benchmark", "Benchmark", "Benchmark"],
            "geometry": [
                [(0, 0), (1, 0), (1, 1), (0, 1)],
                [(1.1, 0), (2.1, 0), (2.1, 1), (1.1, 1)],
                [(2.2, 0), (3.2, 0), (3.2, 1), (2.2, 1)],
                [(0, 0), (1, 0), (1, 1), (0, 1)],
                [(1.1, 0), (2.1, 0), (2.1, 1), (1.1, 1)],
                [(2.2, 0), (3.2, 0), (3.2, 1), (2.2, 1)],
            ],
            "highlight_flag": [False, True, False, False, True, False],
            "source": ["ACS"] * 6,
            "vintage": ["2023"] * 6,
        }
    )
