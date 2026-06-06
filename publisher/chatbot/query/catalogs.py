"""Helpers for loading semantic-layer catalogs and data dictionary metadata."""

from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
FOUNDATIONS_DIR = Path(os.environ["FOUNDATIONS_PATH"])
SEMANTIC_DIR = FOUNDATIONS_DIR / "semantic_layer"
DATA_DICTIONARY_GOLD_DIR = FOUNDATIONS_DIR / "data_dictionary" / "layers" / "gold"


def _read_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_semantic_catalogs() -> dict[str, Any]:
    """Load the semantic-layer YAML files once per process."""

    table_catalog = _read_yaml(SEMANTIC_DIR / "table_catalog.yml")
    metric_catalog = _read_yaml(SEMANTIC_DIR / "metric_catalog.yml")
    join_catalog = _read_yaml(SEMANTIC_DIR / "join_catalog.yml")
    geography_catalog = _read_yaml(SEMANTIC_DIR / "geography_catalog.yml")
    query_templates = _read_yaml(SEMANTIC_DIR / "query_templates.yml")

    tables = {table["table_id"]: _normalize_table(table) for table in table_catalog["tables"]}
    metrics = {metric["metric_id"]: _normalize_metric(metric) for metric in metric_catalog["metrics"]}
    joins = {
        join_rule["join_id"]: join_rule
        for join_rule in join_catalog.get("join_rules", join_catalog.get("non_standard_joins", []))
    }
    geo_levels = {
        geo_level["geo_level"]: geo_level
        for geo_level in geography_catalog["geo_levels"]
    }
    templates = {
        template["template_id"]: template
        for template in query_templates["templates"]
    }

    return {
        "table_catalog": table_catalog,
        "metric_catalog": metric_catalog,
        "join_catalog": join_catalog,
        "geography_catalog": geography_catalog,
        "query_templates": query_templates,
        "tables": tables,
        "metrics": metrics,
        "joins": joins,
        "geo_levels": geo_levels,
        "templates": templates,
    }


def _normalize_metric(metric: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(metric)
    if "subject_area" not in normalized and normalized.get("subject_areas"):
        normalized["subject_area"] = normalized["subject_areas"][0]
    return normalized


def _normalize_table(table: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(table)
    if "subject_area" not in normalized and normalized.get("subject_areas"):
        normalized["subject_area"] = normalized["subject_areas"][0]
    return normalized


@lru_cache(maxsize=1)
def load_table_columns() -> dict[str, set[str]]:
    """Map semantic table ids to the column names listed in the data dictionary."""

    catalogs = load_semantic_catalogs()
    columns_by_table: dict[str, set[str]] = {}

    for table_id, table in catalogs["tables"].items():
        path = DATA_DICTIONARY_GOLD_DIR / f"gold__{table['table_name']}.yml"
        if not path.exists():
            columns_by_table[table_id] = set()
            continue

        payload = _read_yaml(path)
        columns_by_table[table_id] = {
            column["name"] for column in payload.get("columns", [])
        }

    return columns_by_table
