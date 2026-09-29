"""Focused behavior checks for the transparent Q4 point-density hub builder."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import pandas as pd


MODULE_PATH = Path(__file__).with_name("build_q4_amenity_hubs.py")
SPEC = importlib.util.spec_from_file_location("q4_amenity_hubs", MODULE_PATH)
assert SPEC and SPEC.loader
HUBS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = HUBS
SPEC.loader.exec_module(HUBS)


class AmenityHubBuilderTests(unittest.TestCase):
    """Protect the two rules that make candidate membership interpretable."""

    def test_components_do_not_merge_diagonal_cells(self) -> None:
        """Corner-only contact must not create the kind of hidden bridge Q2 avoids."""

        components = HUBS.connected_components({(0, 0), (1, 1), (1, 2)})
        self.assertEqual(components, [[(0, 0)], [(1, 1), (1, 2)]])

    def test_candidate_reconciles_hub_and_membership_counts(self) -> None:
        """A qualifying point cell creates one traceable hub with no duplicate POIs."""

        points = pd.DataFrame(
            {
                "source_record_key": ["poi-a", "poi-b", "poi-c"],
                "source_run_id": ["run"] * 3,
                "mapping_version": ["taxonomy"] * 3,
                "category": ["Retail", "Healthcare", "Food & Drink"],
                "sub_category": ["Grocery & Food Retail", "Primary & General Care", "Restaurants"],
                "longitude": [-77.4360, -77.4361, -77.4362],
                "latitude": [37.5400, 37.5401, 37.5402],
            }
        )
        version = HUBS.CandidateVersion("test_grid", 250, 2, recommended_for_review=True)
        hubs, memberships, _ = HUBS.build_candidate(points, "richmond_va", version)

        self.assertGreaterEqual(len(hubs), 1)
        HUBS.validate_outputs(hubs, memberships)
        self.assertEqual(set(memberships.candidate_status), {"selected_for_workbench"})
        self.assertFalse(memberships.duplicated(["candidate_version", "source_record_key"]).any())


if __name__ == "__main__":
    unittest.main()
