"""Unit tests for trajectory scoring rules that do not require the shared DuckDB."""

from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd


ENGINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ENGINE_DIR))

from trajectory_engine import (  # noqa: E402 - import follows the local path setup above.
    empirical_percentile,
    frame_label,
    signal_tier,
    theil_sen_slope,
    transform_values,
    turn_status,
)


class TrajectoryMethodTests(unittest.TestCase):
    """Protect the key distinctions agreed for the first trajectory method."""

    def test_theil_sen_resists_a_single_endpoint_outlier(self) -> None:
        years = pd.Series([2018, 2019, 2020, 2021, 2022])
        values = pd.Series([10.0, 11.0, 12.0, 13.0, 40.0])
        self.assertAlmostEqual(theil_sen_slope(years, values), 1.0)

    def test_log_transform_marks_nonpositive_values_unavailable(self) -> None:
        transformed = transform_values(pd.Series([1.0, 10.0, 0.0, -1.0]), "log")
        self.assertAlmostEqual(transformed.iloc[0], 0.0)
        self.assertAlmostEqual(transformed.iloc[1], np.log(10.0))
        self.assertTrue(pd.isna(transformed.iloc[2]))
        self.assertTrue(pd.isna(transformed.iloc[3]))

    def test_empirical_percentile_keeps_ties_equal(self) -> None:
        percentiles = empirical_percentile(pd.Series([2.0, 2.0, 4.0]))
        self.assertEqual(percentiles.iloc[0], percentiles.iloc[1])
        self.assertGreater(percentiles.iloc[2], percentiles.iloc[0])

    def test_signal_tiers_are_nested_at_agreed_thresholds(self) -> None:
        self.assertEqual(signal_tier(79.9), "common")
        self.assertEqual(signal_tier(80.0), "notable")
        self.assertEqual(signal_tier(90.0), "strong")
        self.assertEqual(signal_tier(95.0), "exceptional")

    def test_normative_labels_depend_on_position_and_notable_movement(self) -> None:
        self.assertEqual(frame_label("livability", "high", "gaining_ground", "notable", "eligible"), "pulling_ahead")
        self.assertEqual(frame_label("opportunity", "low", "losing_ground", "strong", "eligible"), "falling_further_behind")
        self.assertEqual(frame_label("livability", "middle", "gaining_ground", "common", "eligible"), "no_standout_trend")
        self.assertEqual(frame_label("character", "high", "non_normative", "common", "eligible"), "typical_character_change")
        self.assertEqual(frame_label("character", "high", "non_normative", "strong", "eligible"), "strong_character_change")

    def test_turns_need_opposite_directions_and_sufficient_magnitude(self) -> None:
        self.assertEqual(turn_status(0.5, -0.5, 85, 90, 4, 2, 80), "confirmed_turn")
        self.assertEqual(turn_status(0.5, -0.5, 85, 70, 4, 2, 80), "emerging_turn_watch")
        self.assertEqual(turn_status(0.5, 0.3, 90, 90, 4, 2, 80), "no_turn_signal")
        self.assertEqual(turn_status(0.5, -0.5, 90, 90, 1, 2, 80), "insufficient_evidence")


if __name__ == "__main__":
    unittest.main()
