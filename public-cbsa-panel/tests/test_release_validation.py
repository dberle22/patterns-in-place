"""Focused release-build fixtures that do not open the in-progress Foundations DuckDB."""

import csv
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import duckdb
import pyarrow as pa
import yaml


PROJECT_DIR = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_release", PROJECT_DIR / "scripts" / "build_release.py")
BUILD_RELEASE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(BUILD_RELEASE)


class ReleaseValidationTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.config_path = self.root / "config.yml"
        self.lineage_path = self.root / "lineage.csv"
        self.config_path.write_text("tables: {}\n")
        rows = [
            ("cbsa_county_crosswalk", "county_geoid", "county_geoid"),
            ("cbsa_county_crosswalk", "cbsa_code", "cbsa_code"),
            ("economics_industry_wide", "geo_level", "geo_level"),
            ("economics_industry_wide", "geo_id", "geo_id"),
            ("economics_industry_wide", "year", "year"),
            ("affordability_wide", "geo_level", "geo_level"),
            ("affordability_wide", "geo_id", "geo_id"),
            ("affordability_wide", "year", "year"),
        ]
        with self.lineage_path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["public_table", "public_column", "private_source"])
            writer.writerows(rows)

        self.contract = {
            "release": {"title": "Test panel", "version": "v-test", "status": "test", "geographic_universe": "2 current CBSAs"},
            "tables": {
                "cbsa_county_crosswalk": {
                    "source_table": "silver.xwalk_cbsa_county", "primary_key": ["county_geoid", "cbsa_code"],
                    "columns": [
                        {"name": "county_geoid", "source": "county_geoid", "type": "VARCHAR", "max_null_rate": 0},
                        {"name": "cbsa_code", "source": "cbsa_code", "type": "VARCHAR", "max_null_rate": 0},
                    ],
                },
                "economics_industry_wide": self.fact_contract("gold.economics_industry_wide"),
                "affordability_wide": self.fact_contract("gold.affordability_wide"),
            },
        }
        self.tables = {
            "cbsa_county_crosswalk": pa.table({"county_geoid": ["01001", "02001"], "cbsa_code": ["10000", "20000"]}),
            "economics_industry_wide": pa.table({"geo_level": ["cbsa"], "geo_id": ["10000"], "year": [2024]}),
            "affordability_wide": pa.table({"geo_level": ["cbsa"], "geo_id": ["10000"], "year": [2024]}),
        }

    @staticmethod
    def fact_contract(source_table):
        return {
            "source_table": source_table,
            "primary_key": ["geo_level", "geo_id", "year"],
            "columns": [
                {"name": "geo_level", "source": "geo_level", "type": "VARCHAR", "max_null_rate": 0},
                {"name": "geo_id", "source": "geo_id", "type": "VARCHAR", "max_null_rate": 0},
                {"name": "year", "source": "year", "type": "INTEGER", "max_null_rate": 0},
            ],
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_valid_tables_pass(self):
        BUILD_RELEASE.validate_release_tables(self.tables, self.contract, self.config_path, self.lineage_path)

    def test_duplicate_fact_key_fails(self):
        tables = dict(self.tables)
        tables["economics_industry_wide"] = pa.concat_tables([
            self.tables["economics_industry_wide"], self.tables["economics_industry_wide"]
        ])
        with self.assertRaisesRegex(ValueError, "duplicate primary keys"):
            BUILD_RELEASE.validate_release_tables(tables, self.contract, self.config_path, self.lineage_path)

    def test_non_cbsa_fact_fails(self):
        tables = dict(self.tables)
        tables["affordability_wide"] = pa.table({"geo_level": ["county"], "geo_id": ["10000"], "year": [2024]})
        with self.assertRaisesRegex(ValueError, "non-CBSA geography"):
            BUILD_RELEASE.validate_release_tables(tables, self.contract, self.config_path, self.lineage_path)

    def test_artifacts_and_prior_manifest_guard(self):
        artifact_dir = self.root / "artifacts"
        manifest = BUILD_RELEASE.write_artifacts(self.tables, self.contract, self.lineage_path, artifact_dir)
        self.assertTrue((artifact_dir / "manifest.json").is_file())
        self.assertTrue((artifact_dir / "coverage_report.md").is_file())
        with duckdb.connect(str(artifact_dir / "pip-metro-micro-panel.duckdb"), read_only=True) as connection:
            table_names = {row[0] for row in connection.execute("SHOW TABLES").fetchall()}
        self.assertTrue({"cbsa_county_crosswalk", "economics_industry_wide", "affordability_wide", "_manifest"}.issubset(table_names))

        manifest["tables"]["economics_industry_wide"]["row_count"] = 999
        prior_path = self.root / "prior-manifest.json"
        prior_path.write_text(json.dumps(manifest))
        blocked_dir = self.root / "blocked-artifacts"
        with self.assertRaisesRegex(ValueError, "allow-coverage-change"):
            BUILD_RELEASE.write_artifacts(self.tables, self.contract, self.lineage_path, blocked_dir, prior_path)
        self.assertFalse(blocked_dir.exists())


if __name__ == "__main__":
    unittest.main()
