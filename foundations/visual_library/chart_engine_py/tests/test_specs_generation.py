"""
Tests for the generated spec workflow.

This protects the migration rule that machine-readable specs are artifacts:
they should load cleanly and regenerate deterministically.
"""

from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from chart_engine.specs import load_spec
from scripts.generate_chart_specs import main as generate_chart_specs


class GeneratedSpecsTests(unittest.TestCase):
    def test_all_generated_specs_load(self) -> None:
        spec_dir = PROJECT_ROOT / "chart_engine" / "chart_specs"

        for spec_path in sorted(spec_dir.glob("*.md")):
            with self.subTest(spec_path=spec_path.name):
                spec = load_spec(spec_path)
                self.assertEqual(spec.chart_type, spec_path.stem)
                self.assertTrue(spec.backend in {"altair", "matplotlib"})

    def test_regeneration_is_deterministic(self) -> None:
        spec_dir = PROJECT_ROOT / "chart_engine" / "chart_specs"

        def digest() -> str:
            hash_obj = hashlib.sha256()
            for spec_path in sorted(spec_dir.glob("*.md")):
                hash_obj.update(spec_path.name.encode())
                hash_obj.update(spec_path.read_bytes())
            return hash_obj.hexdigest()

        before = digest()
        generate_chart_specs()
        after = digest()

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
