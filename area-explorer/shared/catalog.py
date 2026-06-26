"""Catalog loading helpers for Area Explorer."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st
import yaml


RAW_THEME_ID = "raw"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _semantic_layer_root() -> Path:
    return _repo_root() / "foundations" / "semantic_layer"


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


@st.cache_data(ttl=3600)
def load_metric_catalog() -> list[dict[str, Any]]:
    """Load the metric catalog from the foundations semantic layer."""
    metrics = _load_yaml(_semantic_layer_root() / "metric_catalog.yml").get("metrics", [])
    if not isinstance(metrics, list):
        raise ValueError("metric_catalog.yml does not contain a valid metrics list")
    return metrics


@st.cache_data(ttl=3600)
def load_theme_catalog() -> list[dict[str, Any]]:
    """Load the theme catalog from the foundations semantic layer."""
    themes = _load_yaml(_semantic_layer_root() / "theme_catalog.yml").get("themes", [])
    if not isinstance(themes, list):
        raise ValueError("theme_catalog.yml does not contain a valid themes list")
    return themes


@st.cache_data(ttl=3600)
def load_intelligence_catalog() -> list[dict[str, Any]]:
    """Load the intelligence frame catalog."""
    frames = _load_yaml(_semantic_layer_root() / "intelligence_catalog.yml").get("frames", [])
    if not isinstance(frames, list):
        raise ValueError("intelligence_catalog.yml does not contain a valid frames list")
    return frames


@st.cache_data(ttl=3600)
def load_table_catalog() -> list[dict[str, Any]]:
    """Load the table catalog for table-to-schema resolution."""
    tables = _load_yaml(_semantic_layer_root() / "table_catalog.yml").get("tables", [])
    if not isinstance(tables, list):
        raise ValueError("table_catalog.yml does not contain a valid tables list")
    return tables


def load_catalog_summary() -> dict[str, int]:
    """Return a small catalog summary used by the app."""
    return {
        "metric_count": len(get_metrics_for_geo_level("cbsa")),
        "theme_count": len(load_theme_catalog()),
    }


def get_metric_meta(metric_id: str) -> dict[str, Any] | None:
    """Return metric metadata for a metric id or source column."""
    for metric in load_metric_catalog():
        if metric.get("metric_id") == metric_id or metric.get("source_column") == metric_id:
            return metric
    return None


def get_table_meta(table_id: str) -> dict[str, Any] | None:
    """Return table metadata for a table id."""
    for table in load_table_catalog():
        if table.get("table_id") == table_id:
            return table
    return None


def _is_metric_active(metric: dict[str, Any]) -> bool:
    return metric.get("status", "active") == "active"


def _is_intelligence_metric(metric: dict[str, Any]) -> bool:
    return str(metric.get("source_table", "")).startswith("intelligence_")


def get_metrics_for_geo_level(geo_level: str, *, include_intelligence: bool = False) -> list[dict[str, Any]]:
    """Return active metrics valid for the requested geography level."""
    metrics: list[dict[str, Any]] = []
    for metric in load_metric_catalog():
        if geo_level not in metric.get("valid_geo_levels", []):
            continue
        if not _is_metric_active(metric):
            continue
        if not include_intelligence and _is_intelligence_metric(metric):
            continue
        metrics.append(metric)
    return metrics


def get_theme_options(geo_level: str) -> list[tuple[str, str]]:
    """Return selectable themes for the current geography level."""
    hierarchy = get_hierarchy(geo_level)
    return [(theme["theme_id"], theme["display_name"]) for theme in hierarchy["themes"]]


def get_hierarchy(geo_level: str) -> dict[str, Any]:
    """Build the theme -> subject -> topic -> metric hierarchy for the app."""
    theme_topics = {
        theme["theme_id"]: {topic["topic_id"]: topic for topic in theme.get("topics", [])}
        for theme in load_theme_catalog()
    }
    frames = {
        frame["frame_id"]: frame
        for frame in load_intelligence_catalog()
        if frame.get("frame_id") in {"character", "livability", "opportunity"}
    }

    themes: list[dict[str, Any]] = []
    for theme in load_theme_catalog():
        theme_id = theme["theme_id"]
        frame = frames.get(theme_id)
        if frame is None:
            continue

        subject_nodes: list[dict[str, Any]] = []
        for subject in frame.get("subjects", []):
            topic_nodes: list[dict[str, Any]] = []
            for topic in subject.get("topics", []):
                theme_topic = theme_topics.get(theme_id, {}).get(topic["topic_id"], {})
                metrics = []
                for metric_id in theme_topic.get("metrics", []):
                    metric_meta = get_metric_meta(metric_id)
                    if metric_meta is None or not _is_metric_active(metric_meta):
                        continue
                    if geo_level not in metric_meta.get("valid_geo_levels", []):
                        continue
                    if _is_intelligence_metric(metric_meta):
                        continue
                    metrics.append(metric_meta)

                if metrics:
                    topic_nodes.append(
                        {
                            "topic_id": topic["topic_id"],
                            "display_name": topic.get("display_name", topic["topic_id"]),
                            "metrics": sorted(metrics, key=lambda metric: metric["display_name"]),
                        }
                    )

            if topic_nodes:
                subject_nodes.append(
                    {
                        "subject_id": subject["subject_id"],
                        "display_name": subject.get("display_name", subject["subject_id"]),
                        "topics": topic_nodes,
                    }
                )

        if subject_nodes:
            themes.append(
                {
                    "theme_id": theme_id,
                    "display_name": theme["display_name"],
                    "subjects": subject_nodes,
                }
            )

    raw_metrics = sorted(
        get_metrics_for_geo_level(geo_level),
        key=lambda metric: metric["display_name"],
    )
    themes.append(
        {
            "theme_id": RAW_THEME_ID,
            "display_name": "Raw / All Metrics",
            "subjects": [
                {
                    "subject_id": "all_metrics",
                    "display_name": "All Metrics",
                    "topics": [
                        {
                            "topic_id": "all_topics",
                            "display_name": "All Topics",
                            "metrics": raw_metrics,
                        }
                    ],
                }
            ],
        }
    )
    return {"themes": themes}
