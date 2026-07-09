"""
Loads settings.yaml and (optionally) data_sources.yaml.

data_sources.yaml holds machine-specific paths and is gitignored.
On cloud deployments it won't exist, so the app falls back to the
committed export DB defined in settings.yaml.
"""

from pathlib import Path
import yaml

# Repo root is three levels up from this file (src/rof/utils/config.py).
_REPO_ROOT = Path(__file__).parent.parent.parent.parent


def _load_yaml(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f) or {}


def load_settings() -> dict:
    return _load_yaml(_REPO_ROOT / "config" / "settings.yaml")


def load_data_sources() -> dict | None:
    """Returns data source paths, or None if running on cloud (file absent)."""
    path = _REPO_ROOT / "config" / "data_sources.yaml"
    if not path.exists():
        return None
    return _load_yaml(path)


def get_db_path() -> Path:
    """
    Returns the DuckDB path to use for the app.
    Local dev:  data/processed/rof_app.duckdb  (full dataset)
    Cloud:      data/exports/jacksonville_rof.duckdb  (committed subset)
    """
    settings = load_settings()
    sources = load_data_sources()

    if sources is not None:
        # Local dev — use the full app DB.
        return _REPO_ROOT / settings["database_path"]
    else:
        # Cloud — use the committed export artifact.
        return _REPO_ROOT / settings["export_database_path"]
