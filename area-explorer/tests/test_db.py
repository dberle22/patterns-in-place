"""Smoke tests for the Area Explorer DuckDB query helpers."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


TESTS_DIR = Path(__file__).resolve().parent
AREA_EXPLORER_ROOT = TESTS_DIR.parent
if str(AREA_EXPLORER_ROOT) not in sys.path:
    sys.path.insert(0, str(AREA_EXPLORER_ROOT))

from shared.db import (
    has_intelligence_datamart,
    query_available_years,
    query_intelligence_membership_table,
    query_intelligence_profile,
    query_metric,
    query_similarity_peers,
    resolve_db_path,
)


@unittest.skipUnless(resolve_db_path().exists(), "DuckDB file is required for DB smoke tests.")
class DatabaseSmokeTests(unittest.TestCase):
    """Confirm the active DuckDB supports the minimum query surface for the app."""

    def test_metric_query_returns_rows(self) -> None:
        available_years = query_available_years("median_hh_income")
        self.assertGreater(len(available_years), 0)
        metric_df = query_metric("median_hh_income", available_years[0])
        self.assertGreater(len(metric_df), 0)

    def test_intelligence_profile_and_peers_are_available(self) -> None:
        if not has_intelligence_datamart():
            self.skipTest("Promoted intelligence tables are not available in the active DuckDB.")

        profile = query_intelligence_profile("35620")
        peers = query_similarity_peers("35620")
        self.assertEqual(profile.get("cbsa_code"), "35620")
        self.assertGreater(len(peers), 0)

    def test_membership_table_has_expected_columns(self) -> None:
        if not has_intelligence_datamart():
            self.skipTest("Promoted intelligence tables are not available in the active DuckDB.")

        membership_df = query_intelligence_membership_table(())
        self.assertGreater(len(membership_df), 0)
        self.assertIn("top_gmm_probability", membership_df.columns)
        self.assertIn("second_gmm_probability", membership_df.columns)


if __name__ == "__main__":
    unittest.main()
