"""Unit tests for the shared benchmarking package API."""

from __future__ import annotations

import unittest

import duckdb

from pip_benchmarking import (
    benchmark_metric,
    benchmark_metric_bundle,
    get_target_metric_surface,
    list_comparison_sets,
)


def build_test_connection() -> duckdb.DuckDBPyConnection:
    """Create an in-memory DuckDB connection with the benchmark contract tables."""

    con = duckdb.connect(":memory:")
    con.execute("CREATE SCHEMA mart_benchmarking")

    con.execute(
        """
        CREATE TABLE mart_benchmarking.benchmark_sets (
          comparison_set_id VARCHAR,
          comparison_set_type VARCHAR,
          target_geo_level VARCHAR,
          target_geo_id VARCHAR,
          target_geo_name VARCHAR,
          comparison_label VARCHAR,
          comparison_description VARCHAR,
          membership_source VARCHAR
        )
        """
    )
    con.execute(
        """
        INSERT INTO mart_benchmarking.benchmark_sets VALUES
          ('cbsa:11111|national', 'national', 'cbsa', '11111', 'Alpha Metro', 'National set', 'All metros', 'gold.dim_geo'),
          ('cbsa:11111|state_primary|01', 'state_primary', 'cbsa', '11111', 'Alpha Metro', 'Primary state set', 'Primary state peers', 'gold.dim_geo'),
          ('cbsa:11111|state_member|01', 'state_member', 'cbsa', '11111', 'Alpha Metro', 'Member state Alabama', 'Member state peers', 'gold.dim_geo'),
          ('cbsa:11111|state_member|02', 'state_member', 'cbsa', '11111', 'Alpha Metro', 'Member state Alaska', 'Member state peers', 'gold.dim_geo'),
          ('cbsa:11111|peer_set|cross_frame_top10', 'peer_set', 'cbsa', '11111', 'Alpha Metro', 'Peer set', 'Cross-frame peers', 'mart_intelligence.intelligence_cross_frame')
        """
    )

    con.execute(
        """
        CREATE TABLE mart_benchmarking.benchmark_set_members (
          comparison_set_id VARCHAR,
          comparison_set_type VARCHAR,
          target_geo_level VARCHAR,
          target_geo_id VARCHAR,
          member_geo_level VARCHAR,
          member_geo_id VARCHAR,
          member_geo_name VARCHAR,
          member_rank INTEGER,
          member_role VARCHAR,
          membership_source VARCHAR
        )
        """
    )
    con.execute(
        """
        INSERT INTO mart_benchmarking.benchmark_set_members VALUES
          ('cbsa:11111|national', 'national', 'cbsa', '11111', 'cbsa', '11111', 'Alpha Metro', 0, 'target', 'gold.dim_geo'),
          ('cbsa:11111|national', 'national', 'cbsa', '11111', 'cbsa', '22222', 'Beta Metro', NULL, 'comparison', 'gold.dim_geo'),
          ('cbsa:11111|national', 'national', 'cbsa', '11111', 'cbsa', '33333', 'Gamma Metro', NULL, 'comparison', 'gold.dim_geo'),
          ('cbsa:11111|state_primary|01', 'state_primary', 'cbsa', '11111', 'cbsa', '11111', 'Alpha Metro', 0, 'target', 'gold.dim_geo'),
          ('cbsa:11111|state_primary|01', 'state_primary', 'cbsa', '11111', 'cbsa', '22222', 'Beta Metro', NULL, 'comparison', 'gold.dim_geo'),
          ('cbsa:11111|state_member|01', 'state_member', 'cbsa', '11111', 'cbsa', '11111', 'Alpha Metro', 0, 'target', 'gold.dim_geo'),
          ('cbsa:11111|state_member|01', 'state_member', 'cbsa', '11111', 'cbsa', '22222', 'Beta Metro', NULL, 'comparison', 'gold.dim_geo'),
          ('cbsa:11111|state_member|02', 'state_member', 'cbsa', '11111', 'cbsa', '11111', 'Alpha Metro', 0, 'target', 'gold.dim_geo'),
          ('cbsa:11111|state_member|02', 'state_member', 'cbsa', '11111', 'cbsa', '33333', 'Gamma Metro', NULL, 'comparison', 'gold.dim_geo'),
          ('cbsa:11111|peer_set|cross_frame_top10', 'peer_set', 'cbsa', '11111', 'cbsa', '11111', 'Alpha Metro', 0, 'target', 'mart_intelligence.intelligence_cross_frame'),
          ('cbsa:11111|peer_set|cross_frame_top10', 'peer_set', 'cbsa', '11111', 'cbsa', '22222', 'Beta Metro', 1, 'comparison', 'mart_intelligence.intelligence_cross_frame'),
          ('cbsa:11111|peer_set|cross_frame_top10', 'peer_set', 'cbsa', '11111', 'cbsa', '33333', 'Gamma Metro', 2, 'comparison', 'mart_intelligence.intelligence_cross_frame')
        """
    )

    con.execute(
        """
        CREATE TABLE mart_benchmarking.benchmark_cbsa_metrics (
          geo_level VARCHAR,
          geo_id VARCHAR,
          geo_name VARCHAR,
          frame_id VARCHAR,
          theme_group VARCHAR,
          metric_id VARCHAR,
          metric_family VARCHAR,
          metric_type VARCHAR,
          unit VARCHAR,
          value_direction VARCHAR,
          preferred_summary_stat VARCHAR,
          metric_label VARCHAR,
          value DOUBLE,
          year INTEGER,
          source_name VARCHAR,
          vintage_note VARCHAR
        )
        """
    )
    con.execute(
        """
        INSERT INTO mart_benchmarking.benchmark_cbsa_metrics VALUES
          ('cbsa', '11111', 'Alpha Metro', 'character', 'demographics', 'pop_total', 'population', 'level', 'count', 'higher_is_better', 'median', 'Population', 100.0, 2024, 'test_source', 'Test vintage'),
          ('cbsa', '22222', 'Beta Metro', 'character', 'demographics', 'pop_total', 'population', 'level', 'count', 'higher_is_better', 'median', 'Population', 80.0, 2024, 'test_source', 'Test vintage'),
          ('cbsa', '33333', 'Gamma Metro', 'character', 'demographics', 'pop_total', 'population', 'level', 'count', 'higher_is_better', 'median', 'Population', 120.0, 2024, 'test_source', 'Test vintage'),
          ('cbsa', '11111', 'Alpha Metro', 'cross_frame', 'identity', 'cross_frame_percentile_rank', 'framework_scores', 'percentile', 'percentile', 'higher_is_better', 'median', 'Cross-frame percentile rank', 75.0, NULL, 'test_source', 'Current surface'),
          ('cbsa', '22222', 'Beta Metro', 'cross_frame', 'identity', 'cross_frame_percentile_rank', 'framework_scores', 'percentile', 'percentile', 'higher_is_better', 'median', 'Cross-frame percentile rank', 50.0, NULL, 'test_source', 'Current surface'),
          ('cbsa', '33333', 'Gamma Metro', 'cross_frame', 'identity', 'cross_frame_percentile_rank', 'framework_scores', 'percentile', 'percentile', 'higher_is_better', 'median', 'Cross-frame percentile rank', 90.0, NULL, 'test_source', 'Current surface')
        """
    )
    return con


class BenchmarkApiTests(unittest.TestCase):
    """Validate the shared benchmark API against a minimal in-memory schema."""

    def setUp(self) -> None:
        self.con = build_test_connection()

    def tearDown(self) -> None:
        self.con.close()

    def test_list_comparison_sets_orders_expected_types(self) -> None:
        sets_df = list_comparison_sets(self.con, "11111")
        self.assertEqual(
            ["national", "state_primary", "state_member", "state_member", "peer_set"],
            sets_df["comparison_set_type"].tolist(),
        )

    def test_get_target_metric_surface_returns_target_rows(self) -> None:
        metric_df = get_target_metric_surface(self.con, "11111")
        self.assertEqual(2, len(metric_df))
        self.assertEqual({"pop_total", "cross_frame_percentile_rank"}, set(metric_df["metric_id"].tolist()))

    def test_benchmark_metric_returns_summary_and_member_rows(self) -> None:
        summary_df, member_df = benchmark_metric(
            self.con,
            target_geo_id="11111",
            metric_id="pop_total",
            comparison_set_type="national",
            year=2024,
        )

        self.assertEqual(1, len(summary_df))
        self.assertEqual(3, int(summary_df.loc[0, "comparison_n"]))
        self.assertAlmostEqual(100.0, float(summary_df.loc[0, "target_value"]))
        self.assertAlmostEqual(100.0, float(summary_df.loc[0, "comparison_mean"]))
        self.assertAlmostEqual(100.0, float(summary_df.loc[0, "comparison_median"]))
        self.assertAlmostEqual(66.6666666667, float(summary_df.loc[0, "percentile_rank"]), places=4)
        self.assertEqual(3, len(member_df))
        self.assertEqual("target", member_df.iloc[0]["member_role"])

    def test_benchmark_metric_supports_null_year_metrics(self) -> None:
        summary_df, member_df = benchmark_metric(
            self.con,
            target_geo_id="11111",
            metric_id="cross_frame_percentile_rank",
            comparison_set_type="peer_set",
            year=None,
        )

        self.assertEqual(1, len(summary_df))
        self.assertEqual(3, len(member_df))
        self.assertEqual("peer_set", summary_df.iloc[0]["comparison_set_type"])

    def test_benchmark_metric_bundle_stacks_multiple_requests(self) -> None:
        bundle_df = benchmark_metric_bundle(
            self.con,
            target_geo_id="11111",
            metric_ids=["pop_total", "cross_frame_percentile_rank"],
            comparison_set_types=["national", "state_member"],
        )

        self.assertEqual(6, len(bundle_df))
        self.assertEqual(
            {"national", "state_member"},
            set(bundle_df["comparison_set_type"].tolist()),
        )

    def test_state_member_returns_one_summary_per_member_state_set(self) -> None:
        summary_df, member_df = benchmark_metric(
            self.con,
            target_geo_id="11111",
            metric_id="pop_total",
            comparison_set_type="state_member",
            year=2024,
        )

        self.assertEqual(2, len(summary_df))
        self.assertEqual(
            {"cbsa:11111|state_member|01", "cbsa:11111|state_member|02"},
            set(summary_df["comparison_set_id"].tolist()),
        )
        self.assertEqual(4, len(member_df))
