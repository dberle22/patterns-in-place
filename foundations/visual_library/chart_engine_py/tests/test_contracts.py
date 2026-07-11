"""
Contract-level tests for the Python chart engine.

These checks keep the failure mode readable when prep or generated specs drift
out of sync with what a renderer expects.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chart_engine.contracts import ContractError, validate_contract
from chart_engine.specs import ChartSpec


class ValidateContractTests(unittest.TestCase):
    def test_missing_required_field_raises_readable_error(self) -> None:
        df = pd.DataFrame({"entity": ["A"]})
        spec = ChartSpec(
            chart_type="bar_chart",
            backend="altair",
            required_fields=["entity", "value"],
        )

        with self.assertRaises(ContractError) as exc:
            validate_contract(df, spec)

        self.assertIn("bar_chart", str(exc.exception))
        self.assertIn("value", str(exc.exception))

    def test_empty_dataframe_raises_contract_error(self) -> None:
        df = pd.DataFrame(columns=["entity", "value"])
        spec = ChartSpec(
            chart_type="bar_chart",
            backend="altair",
            required_fields=["entity", "value"],
        )

        with self.assertRaises(ContractError) as exc:
            validate_contract(df, spec)

        self.assertIn("empty dataframe", str(exc.exception))

    def test_valid_dataframe_passes_silently(self) -> None:
        df = pd.DataFrame({"entity": ["A"], "value": [1.2]})
        spec = ChartSpec(
            chart_type="bar_chart",
            backend="altair",
            required_fields=["entity", "value"],
        )

        validate_contract(df, spec)


if __name__ == "__main__":
    unittest.main()
