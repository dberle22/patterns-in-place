"""Reusable public API for DuckDB-backed benchmark queries."""

from __future__ import annotations

import duckdb
import pandas as pd


def list_comparison_sets(
    con: duckdb.DuckDBPyConnection,
    target_geo_id: str,
) -> pd.DataFrame:
    """List the materialized comparison sets available for one target CBSA."""

    return con.execute(
        """
        SELECT
          comparison_set_id,
          comparison_set_type,
          comparison_label,
          comparison_description,
          membership_source
        FROM mart_benchmarking.benchmark_sets
        WHERE target_geo_level = 'cbsa'
          AND target_geo_id = ?
        ORDER BY
          CASE comparison_set_type
            WHEN 'national' THEN 1
            WHEN 'region' THEN 2
            WHEN 'division' THEN 3
            WHEN 'state_primary' THEN 4
            WHEN 'state_member' THEN 5
            WHEN 'peer_set' THEN 6
            ELSE 99
          END,
          comparison_set_id
        """,
        [str(target_geo_id)],
    ).fetchdf()


def get_target_metric_surface(
    con: duckdb.DuckDBPyConnection,
    target_geo_id: str,
) -> pd.DataFrame:
    """Return the long benchmarkable metric surface for one target CBSA."""

    return con.execute(
        """
        SELECT
          geo_level,
          geo_id,
          geo_name,
          frame_id,
          theme_group,
          metric_id,
          metric_family,
          metric_type,
          unit,
          value_direction,
          preferred_summary_stat,
          metric_label,
          value,
          year,
          source_name,
          vintage_note
        FROM mart_benchmarking.benchmark_cbsa_metrics
        WHERE geo_level = 'cbsa'
          AND geo_id = ?
        ORDER BY frame_id, theme_group, metric_id, year
        """,
        [str(target_geo_id)],
    ).fetchdf()


def benchmark_metric(
    con: duckdb.DuckDBPyConnection,
    target_geo_id: str,
    metric_id: str,
    comparison_set_type: str,
    year: int | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Benchmark one metric for one target CBSA against one comparison-set type."""

    summary_df = con.execute(
        """
        WITH requested_set AS (
          SELECT
            comparison_set_id,
            comparison_set_type,
            target_geo_level,
            target_geo_id,
            target_geo_name,
            membership_source
          FROM mart_benchmarking.benchmark_sets
          WHERE target_geo_level = 'cbsa'
            AND target_geo_id = ?
            AND comparison_set_type = ?
        ),
        selected_target_metric AS (
          SELECT
            *
          FROM mart_benchmarking.benchmark_cbsa_metrics
          WHERE geo_level = 'cbsa'
            AND geo_id = ?
            AND metric_id = ?
            AND (? IS NULL OR year = ?)
          QUALIFY ROW_NUMBER() OVER (ORDER BY year DESC NULLS LAST) = 1
        ),
        member_values AS (
          SELECT
            rs.comparison_set_id,
            rs.comparison_set_type,
            rs.target_geo_level,
            rs.target_geo_id,
            rs.target_geo_name,
            m.member_geo_level,
            m.member_geo_id,
            m.member_geo_name,
            m.member_rank,
            m.member_role,
            bm.frame_id,
            bm.theme_group,
            bm.metric_id,
            bm.metric_family,
            bm.metric_type,
            bm.unit,
            bm.value_direction,
            bm.preferred_summary_stat,
            bm.metric_label,
            bm.year,
            stm.value AS target_value,
            bm.value AS member_value,
            bm.source_name,
            bm.vintage_note,
            rs.membership_source
          FROM requested_set AS rs
          INNER JOIN selected_target_metric AS stm
            ON rs.target_geo_id = stm.geo_id
          INNER JOIN mart_benchmarking.benchmark_set_members AS m
            ON rs.comparison_set_id = m.comparison_set_id
          INNER JOIN mart_benchmarking.benchmark_cbsa_metrics AS bm
            ON m.member_geo_level = bm.geo_level
           AND m.member_geo_id = bm.geo_id
           AND stm.metric_id = bm.metric_id
           AND stm.year IS NOT DISTINCT FROM bm.year
        ),
        summary AS (
          SELECT
            comparison_set_id,
            comparison_set_type,
            target_geo_level,
            target_geo_id,
            target_geo_name,
            ANY_VALUE(frame_id) AS frame_id,
            ANY_VALUE(theme_group) AS theme_group,
            metric_id,
            ANY_VALUE(metric_family) AS metric_family,
            ANY_VALUE(metric_type) AS metric_type,
            ANY_VALUE(unit) AS unit,
            ANY_VALUE(value_direction) AS value_direction,
            ANY_VALUE(preferred_summary_stat) AS preferred_summary_stat,
            ANY_VALUE(metric_label) AS metric_label,
            year,
            ANY_VALUE(target_value) AS target_value,
            COUNT(member_value) AS comparison_n,
            AVG(member_value) AS comparison_mean,
            MEDIAN(member_value) AS comparison_median,
            MIN(member_value) AS comparison_min,
            MAX(member_value) AS comparison_max,
            STDDEV_SAMP(member_value) AS comparison_stddev,
            SUM(CASE WHEN member_value < target_value THEN 1 ELSE 0 END) + 1 AS rank_asc,
            SUM(CASE WHEN member_value > target_value THEN 1 ELSE 0 END) + 1 AS rank_desc,
            100.0 * SUM(CASE WHEN member_value <= target_value THEN 1 ELSE 0 END) / NULLIF(COUNT(member_value), 0) AS percentile_rank,
            ANY_VALUE(source_name) AS source_name,
            ANY_VALUE(vintage_note) AS vintage_note,
            ANY_VALUE(membership_source) AS membership_source
          FROM member_values
          GROUP BY
            comparison_set_id,
            comparison_set_type,
            target_geo_level,
            target_geo_id,
            target_geo_name,
            metric_id,
            year
        )
        SELECT
          comparison_set_id,
          comparison_set_type,
          target_geo_level,
          target_geo_id,
          target_geo_name,
          frame_id,
          theme_group,
          metric_id,
          metric_family,
          metric_type,
          unit,
          value_direction,
          preferred_summary_stat,
          metric_label,
          year,
          target_value,
          comparison_n,
          comparison_mean,
          comparison_median,
          comparison_min,
          comparison_max,
          comparison_stddev,
          rank_asc,
          rank_desc,
          percentile_rank,
          target_value - comparison_mean AS delta_from_mean,
          target_value - comparison_median AS delta_from_median,
          CASE
            WHEN comparison_mean IS NULL OR comparison_mean = 0 THEN NULL
            ELSE (target_value - comparison_mean) / comparison_mean
          END AS pct_diff_from_mean,
          CASE
            WHEN comparison_median IS NULL OR comparison_median = 0 THEN NULL
            ELSE (target_value - comparison_median) / comparison_median
          END AS pct_diff_from_median,
          CASE
            WHEN comparison_stddev IS NULL OR comparison_stddev = 0 THEN NULL
            ELSE (target_value - comparison_mean) / comparison_stddev
          END AS z_score,
          source_name,
          vintage_note,
          membership_source
        FROM summary
        """,
        [
            str(target_geo_id),
            str(comparison_set_type),
            str(target_geo_id),
            str(metric_id),
            year,
            year,
        ],
    ).fetchdf()

    member_df = con.execute(
        """
        WITH requested_set AS (
          SELECT comparison_set_id
          FROM mart_benchmarking.benchmark_sets
          WHERE target_geo_level = 'cbsa'
            AND target_geo_id = ?
            AND comparison_set_type = ?
        ),
        selected_target_metric AS (
          SELECT *
          FROM mart_benchmarking.benchmark_cbsa_metrics
          WHERE geo_level = 'cbsa'
            AND geo_id = ?
            AND metric_id = ?
            AND (? IS NULL OR year = ?)
          QUALIFY ROW_NUMBER() OVER (ORDER BY year DESC NULLS LAST) = 1
        )
        SELECT
          m.comparison_set_id,
          ? AS comparison_set_type,
          m.member_role,
          m.member_rank,
          m.member_geo_level,
          m.member_geo_id,
          m.member_geo_name,
          bm.frame_id,
          bm.theme_group,
          bm.metric_id,
          bm.metric_label,
          bm.metric_family,
          bm.metric_type,
          bm.unit,
          bm.value_direction,
          bm.year,
          stm.value AS target_value,
          bm.value AS member_value,
          bm.value - stm.value AS delta_from_target,
          bm.source_name,
          bm.vintage_note
        FROM requested_set AS rs
        INNER JOIN mart_benchmarking.benchmark_set_members AS m
          ON rs.comparison_set_id = m.comparison_set_id
        INNER JOIN selected_target_metric AS stm
          ON TRUE
        INNER JOIN mart_benchmarking.benchmark_cbsa_metrics AS bm
          ON m.member_geo_level = bm.geo_level
         AND m.member_geo_id = bm.geo_id
         AND stm.metric_id = bm.metric_id
         AND stm.year IS NOT DISTINCT FROM bm.year
        ORDER BY m.member_rank NULLS LAST, m.member_geo_name
        """,
        [
            str(target_geo_id),
            str(comparison_set_type),
            str(target_geo_id),
            str(metric_id),
            year,
            year,
            str(comparison_set_type),
        ],
    ).fetchdf()

    return summary_df, member_df


def benchmark_metric_bundle(
    con: duckdb.DuckDBPyConnection,
    target_geo_id: str,
    metric_ids: list[str],
    comparison_set_types: list[str],
) -> pd.DataFrame:
    """Benchmark a list of metrics across a list of comparison-set types."""

    summary_frames: list[pd.DataFrame] = []
    for comparison_set_type in comparison_set_types:
        for metric_id in metric_ids:
            summary_df, _ = benchmark_metric(
                con=con,
                target_geo_id=target_geo_id,
                metric_id=metric_id,
                comparison_set_type=comparison_set_type,
            )
            if not summary_df.empty:
                summary_frames.append(summary_df)

    if not summary_frames:
        return pd.DataFrame()

    return pd.concat(summary_frames, ignore_index=True)
