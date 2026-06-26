"""Smoke tests for benchmark helpers used by Area Explorer."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

import pandas as pd


TESTS_DIR = Path(__file__).resolve().parent
AREA_EXPLORER_ROOT = TESTS_DIR.parent
if str(AREA_EXPLORER_ROOT) not in sys.path:
    sys.path.insert(0, str(AREA_EXPLORER_ROOT))

from shared.benchmark import add_benchmark_ranks, format_metric_value, format_percentile


class BenchmarkSmokeTests(unittest.TestCase):
    """Check the display formatting and benchmark rank math we expose in the app."""

    def test_format_metric_value_handles_common_units(self) -> None:
        self.assertEqual(format_metric_value(1250, "currency"), "$1,250")
        self.assertEqual(format_metric_value(0.123, "percent"), "12.3%")
        self.assertEqual(format_metric_value(4.567, "ratio"), "4.57")

    def test_format_percentile_handles_nulls(self) -> None:
        self.assertEqual(format_percentile(None), "NA")
        self.assertEqual(format_percentile(62.4), "62nd percentile")

    def test_add_benchmark_ranks_adds_expected_columns(self) -> None:
        source_df = pd.DataFrame(
            {
                "geo_id": ["a", "b", "c", "d"],
                "division_name": ["East", "East", "West", "West"],
                "metric_value": [10.0, 20.0, 5.0, 15.0],
            }
        )
        ranked_df = add_benchmark_ranks(source_df, "metric_value", "division_name")
        self.assertIn("national_pct_rank", ranked_df.columns)
        self.assertIn("division_pct_rank", ranked_df.columns)
        self.assertEqual(float(ranked_df.loc[ranked_df["geo_id"] == "a", "division_pct_rank"].iloc[0]), 0.0)
        self.assertEqual(float(ranked_df.loc[ranked_df["geo_id"] == "b", "division_pct_rank"].iloc[0]), 100.0)


if __name__ == "__main__":
    unittest.main()
