"""Regression checks for synthetic markets and the append-only publish.

Run from the repo root with .venv-marimo/bin/python -m unittest discover
-s metro-deep-dive-program/engines/poi/qa -p 'test_*.py'.
"""

from pathlib import Path
import sys
import tempfile
import unittest

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from acquire_overture_places import market_county_geoids, resolve_market
from assign_poi_geography import market_geography_sql
from publish_poi_append import append_market


CONFIG = {"markets": {
    "cbsa": {"market_id": "10580"},
    "synthetic": {"market_id": "SYNTH-NY", "county_geoids": ["36031"]},
    "bad_id": {"market_id": "SYNTH-new-york"},
    "no_counties": {"market_id": "SYNTH-NY"},
    "bad_county": {"market_id": "SYNTH-NY", "county_geoids": ["36031'; --"]},
}}


class MarketTests(unittest.TestCase):
    def test_market_ids(self):
        self.assertEqual(resolve_market(CONFIG, "cbsa"), ("cbsa", "10580"))
        self.assertEqual(resolve_market(CONFIG, "synthetic"), ("synthetic", "SYNTH-NY"))
        with self.assertRaises(ValueError):
            resolve_market(CONFIG, "bad_id")

    def test_county_declarations(self):
        self.assertIsNone(market_county_geoids(CONFIG, "cbsa"))
        self.assertEqual(market_county_geoids(CONFIG, "synthetic"), ["36031"])
        for market in ("no_counties", "bad_county"):
            with self.assertRaises(ValueError):
                market_county_geoids(CONFIG, market)

    def test_assignment_scope(self):
        counties, tracts = market_geography_sql("SYNTH-NY", ["36031"])
        self.assertNotIn("rollup", counties + tracts)
        counties, tracts = market_geography_sql("10580", None)
        self.assertIn("rollup_county_to_cbsa", counties)
        self.assertIn("rollup_tract_to_cbsa", tracts)


class AppendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.con = duckdb.connect()
        self.con.execute("CREATE SCHEMA mart_poi")
        self.con.execute("CREATE TABLE mart_poi.a (cbsa_code VARCHAR, market_id VARCHAR, x INTEGER, y INTEGER)")
        self.con.execute("CREATE TABLE mart_poi.b (cbsa_code VARCHAR, x INTEGER)")
        self.con.execute("INSERT INTO mart_poi.a VALUES ('10580', '10580', 1, 2)")

    def tearDown(self):
        self.con.close()
        self.tmp.cleanup()

    def artifact(self, name, query):
        path = self.dir / name
        self.con.execute(f"COPY ({query}) TO '{path}' (FORMAT PARQUET)")
        return path

    def rows(self, table):
        return self.con.execute(f"SELECT * FROM mart_poi.{table} ORDER BY ALL").fetchall()

    def test_appends_by_name_and_keeps_existing_rows(self):
        # Reversed columns must land by name, and market_id must become cbsa_code.
        a = self.artifact("a.parquet", "SELECT 20 AS y, 10 AS x, 'SYNTH-NY' AS market_id")
        b = self.artifact("b.parquet", "SELECT 30 AS x")
        self.assertEqual(append_market(self.con, "SYNTH-NY", {"a": a, "b": b}), {"a": 1, "b": 1})
        self.assertEqual(self.rows("a"), [("10580", "10580", 1, 2), ("SYNTH-NY", "SYNTH-NY", 10, 20)])
        self.assertEqual(self.rows("b"), [("SYNTH-NY", 30)])

    def test_refuses_published_market_and_writes_nothing(self):
        a = self.artifact("a.parquet", "SELECT '10580' AS cbsa_code, '10580' AS market_id, 9 AS x, 9 AS y")
        b = self.artifact("b.parquet", "SELECT 9 AS x")
        with self.assertRaisesRegex(RuntimeError, "Refusing to append"):
            append_market(self.con, "10580", {"b": b, "a": a})
        self.assertEqual(self.rows("a"), [("10580", "10580", 1, 2)])
        self.assertEqual(self.rows("b"), [])

    def test_refuses_column_mismatch(self):
        a = self.artifact("a.parquet", "SELECT 'SYNTH-NY' AS cbsa_code, 1 AS x")
        with self.assertRaisesRegex(RuntimeError, "columns differ"):
            append_market(self.con, "SYNTH-NY", {"a": a})
        self.assertEqual(self.rows("a"), [("10580", "10580", 1, 2)])

    def test_failed_insert_rolls_back_every_table(self):
        a = self.artifact("a.parquet", "SELECT 'SYNTH-NY' AS market_id, 1 AS x, 2 AS y")
        b = self.artifact("b.parquet", "SELECT 'not a number' AS x")
        with self.assertRaises(duckdb.Error):
            append_market(self.con, "SYNTH-NY", {"a": a, "b": b})
        self.assertEqual(self.rows("a"), [("10580", "10580", 1, 2)])
        self.assertEqual(self.rows("b"), [])


if __name__ == "__main__":
    unittest.main()
