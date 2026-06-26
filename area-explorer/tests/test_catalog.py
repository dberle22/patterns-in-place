"""Smoke tests for the Area Explorer catalog helpers."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


TESTS_DIR = Path(__file__).resolve().parent
AREA_EXPLORER_ROOT = TESTS_DIR.parent
if str(AREA_EXPLORER_ROOT) not in sys.path:
    sys.path.insert(0, str(AREA_EXPLORER_ROOT))

from shared.catalog import RAW_THEME_ID, get_hierarchy, get_metric_meta, get_metrics_for_geo_level


class CatalogSmokeTests(unittest.TestCase):
    """Validate that the semantic-layer catalogs produce the expected app tree."""

    def test_cbsa_metrics_are_available(self) -> None:
        metrics = get_metrics_for_geo_level("cbsa")
        self.assertGreater(len(metrics), 0)

    def test_common_metric_is_resolvable(self) -> None:
        metric_meta = get_metric_meta("median_hh_income")
        self.assertIsNotNone(metric_meta)
        self.assertEqual(metric_meta["metric_id"], "median_hh_income")

    def test_hierarchy_includes_raw_theme(self) -> None:
        hierarchy = get_hierarchy("cbsa")
        theme_ids = {theme["theme_id"] for theme in hierarchy["themes"]}
        self.assertIn(RAW_THEME_ID, theme_ids)


if __name__ == "__main__":
    unittest.main()
