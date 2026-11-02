"""Regression checks for the shared append-only table publish.

Run from the repo root with .venv-marimo/bin/python -m unittest discover
-s metro-deep-dive-program/engines/poi/qa -p 'test_*.py'.
"""

from pathlib import Path
import sys
import unittest

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_shared"))
from append_run import append_run


class AppendRunTests(unittest.TestCase):
    def setUp(self):
        self.con = duckdb.connect()

    def tearDown(self):
        self.con.close()

    def rows(self):
        return self.con.execute("SELECT * FROM s.t ORDER BY ALL").fetchall()

    def test_creates_then_appends_by_name(self):
        self.assertEqual(append_run(self.con, "s", "t", "SELECT 'r1' AS source_run_id, 1 AS x", "r1"), 1)
        self.assertEqual(append_run(self.con, "s", "t", "SELECT 2 AS x, 'r2' AS source_run_id", "r2"), 1)
        self.assertEqual(self.rows(), [("r1", 1), ("r2", 2)])

    def test_refuses_published_run(self):
        append_run(self.con, "s", "t", "SELECT 'r1' AS source_run_id, 1 AS x", "r1")
        with self.assertRaisesRegex(RuntimeError, "Refusing to append"):
            append_run(self.con, "s", "t", "SELECT 'r1' AS source_run_id, 9 AS x", "r1")
        self.assertEqual(self.rows(), [("r1", 1)])

    def test_refuses_column_mismatch(self):
        append_run(self.con, "s", "t", "SELECT 'r1' AS source_run_id, 1 AS x", "r1")
        with self.assertRaisesRegex(RuntimeError, "columns differ"):
            append_run(self.con, "s", "t", "SELECT 'r2' AS source_run_id", "r2")
        self.assertEqual(self.rows(), [("r1", 1)])

    def test_refuses_rows_from_another_run(self):
        with self.assertRaisesRegex(RuntimeError, "belong to run"):
            append_run(self.con, "s", "t", "SELECT 'other' AS source_run_id", "r1")

    def test_failed_insert_changes_nothing(self):
        append_run(self.con, "s", "t", "SELECT 'r1' AS source_run_id, 1 AS x", "r1")
        with self.assertRaises(duckdb.Error):
            append_run(self.con, "s", "t", "SELECT 'r2' AS source_run_id, 'not a number' AS x", "r2")
        self.assertEqual(self.rows(), [("r1", 1)])


if __name__ == "__main__":
    unittest.main()
