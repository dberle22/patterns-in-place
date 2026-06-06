"""YAML configuration loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG_DIR = PROJECT_ROOT / "config"


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load one YAML file into a dictionary."""

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file does not exist: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a mapping at the top level: {path}")
    return data


def load_config(config_dir: str | Path = DEFAULT_CONFIG_DIR) -> dict[str, Any]:
    """Load all starter config files into one dictionary."""

    config_dir = Path(config_dir)
    data_sources_path = config_dir / "data_sources.yaml"
    if not data_sources_path.exists():
        data_sources_path = config_dir / "data_sources.example.yaml"
    return {
        "settings": load_yaml(config_dir / "settings.yaml"),
        "data_sources": load_yaml(data_sources_path),
        "poi_categories": load_yaml(config_dir / "poi_categories.yaml"),
        "curated_scrape_articles": load_yaml(config_dir / "curated_scrape_articles.yaml"),
        "scoring_weights": load_yaml(config_dir / "scoring_weights.yaml"),
    }
