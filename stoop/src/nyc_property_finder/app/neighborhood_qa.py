"""QA helpers for neighborhood geography, demographics, and POI coverage."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from nyc_property_finder.app.base_map import (
    DEFAULT_PUBLIC_POI_CATEGORIES,
    DEMOGRAPHIC_METRICS,
    NTA_FEATURE_TABLE,
    POI_V3_TABLE,
    POI_V2_TABLE,
    PUBLIC_POI_TABLE,
    TRACT_FEATURE_TABLE,
    TRACT_TO_NTA_TABLE,
    canonical_public_poi_category,
    load_feature_table,
)
from nyc_property_finder.app.explorer import table_exists
from nyc_property_finder.curated_poi.google_takeout.config import (
    DEFAULT_DETAILS_CACHE_PATH,
    DEFAULT_RESOLUTION_CACHE_PATH,
)
from nyc_property_finder.public_poi.config import CATEGORY_SLUGS
from nyc_property_finder.services.config import PROJECT_ROOT, load_config
from nyc_property_finder.services.duckdb_service import DuckDBService


QA_TABLES = {
    "Tract to NTA mapping": TRACT_TO_NTA_TABLE,
    "Tract features": TRACT_FEATURE_TABLE,
    "NTA features": NTA_FEATURE_TABLE,
    "Curated POI canonical": POI_V3_TABLE,
    "Curated POI canonical v2": POI_V2_TABLE,
    "Curated POI stage (Google Takeout)": "property_explorer_gold.stg_user_poi_google_takeout",
    "Curated POI stage (Web scrape)": "property_explorer_gold.stg_user_poi_web_scrape",
    "Curated POI stage (Manual upload)": "property_explorer_gold.stg_user_poi_manual_upload",
    "Public POI baseline": PUBLIC_POI_TABLE,
}


def format_coverage(value: float) -> str:
    """Format a coverage ratio for Streamlit display."""

    return f"{value:.1%}"


def resolve_config_path(path: str | None, project_root: Path = PROJECT_ROOT) -> Path | None:
    """Resolve a possibly relative config path against the project root."""

    if not path:
        return None

    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return project_root / candidate


def table_row_count(database_path: str | Path, full_table_name: str) -> int | None:
    """Return row count for a DuckDB table, or None when unavailable."""

    if not table_exists(database_path, full_table_name):
        return None

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        result = duckdb_service.query_df(f"SELECT COUNT(*) AS row_count FROM {full_table_name}")
    return int(result["row_count"].iloc[0])


def table_columns(database_path: str | Path, full_table_name: str) -> set[str]:
    """Return the available columns for a DuckDB table."""

    if not table_exists(database_path, full_table_name):
        return set()

    with DuckDBService(database_path, read_only=True) as duckdb_service:
        return set(duckdb_service.query_df(f"SELECT * FROM {full_table_name} LIMIT 0").columns)


def build_table_status(database_path: str | Path) -> pd.DataFrame:
    """Summarize expected gold tables used by the neighborhood apps."""

    rows = []
    for label, full_table_name in QA_TABLES.items():
        exists = table_exists(database_path, full_table_name)
        rows.append(
            {
                "Area": label,
                "Table": full_table_name,
                "Status": "ready" if exists else "missing",
                "Rows": table_row_count(database_path, full_table_name) if exists else 0,
            }
        )
    return pd.DataFrame(rows)


def build_metric_coverage(database_path: str | Path, grain: str) -> pd.DataFrame:
    """Summarize non-null demographic coverage for tract or NTA feature tables."""

    if grain == "tract":
        table_name = TRACT_FEATURE_TABLE
        id_columns = ["tract_id"]
    elif grain == "nta":
        table_name = NTA_FEATURE_TABLE
        id_columns = ["nta_id", "nta_name"]
    else:
        raise ValueError(f"Unsupported metric coverage grain: {grain}")

    features = load_feature_table(database_path, table_name, id_columns)
    row_count = len(features)
    rows = []
    for metric, metadata in DEMOGRAPHIC_METRICS.items():
        values = pd.to_numeric(features[metric], errors="coerce")
        populated = int(values.notna().sum())
        coverage = float(populated / row_count) if row_count else 0.0
        rows.append(
            {
                "Metric": metadata["label"],
                "Column": metric,
                "Rows": row_count,
                "Populated": populated,
                "Missing": int(row_count - populated),
                "Coverage": coverage,
                "Coverage label": format_coverage(coverage),
            }
        )
    return pd.DataFrame(rows)


def build_source_status(
    data_sources: dict[str, Any],
    project_root: Path = PROJECT_ROOT,
) -> pd.DataFrame:
    """Summarize configured source files and metadata."""

    rows = []
    sources = data_sources.get("sources", {})
    for source_key, source in sources.items():
        if not isinstance(source, dict):
            continue

        resolved_path = resolve_config_path(source.get("path"), project_root)
        alternate_paths = [
            resolve_config_path(path, project_root)
            for path in source.get("alternate_paths", [])
            if resolve_config_path(path, project_root) is not None
        ]
        existing_alternates = [path for path in alternate_paths if path and path.exists()]
        path_exists = bool(resolved_path and resolved_path.exists())
        any_source_exists = path_exists or bool(existing_alternates)
        rows.append(
            {
                "Source": source_key,
                "Status": "ready" if any_source_exists else source.get("status", "missing"),
                "Path": str(resolved_path) if resolved_path else "",
                "Path exists": path_exists,
                "Existing alternate paths": ", ".join(str(path) for path in existing_alternates),
                "Format": source.get("expected_format", ""),
                "Owner": source.get("owner", ""),
                "URL": source.get("source_url", source.get("search_url", "")),
                "Notes": source.get("notes", ""),
            }
        )
    return pd.DataFrame(rows)


def _expected_curated_inventory() -> list[dict[str, str]]:
    config = load_config()["poi_categories"]
    file_rules = config.get("curated_taxonomy", {}).get("files", {})
    inventory = []
    for source_file, rule in sorted(file_rules.items()):
        if not isinstance(rule, dict):
            continue

        category = str(rule.get("category", "")).strip()
        if not category:
            continue

        raw_subcategory = str(rule.get("subcategory", "")).strip()
        expected_subcategory = raw_subcategory or category
        taxonomy_rule_parts = []
        if rule.get("subcategory_from_tags_or_comment"):
            taxonomy_rule_parts.append("subcategory from tags/comment")
        if rule.get("detail_level_3_from_tags_or_comment"):
            taxonomy_rule_parts.append("detail level 3 from tags/comment")
        if not taxonomy_rule_parts:
            taxonomy_rule_parts.append("file-level taxonomy")

        inventory.append(
            {
                "category": category,
                "subcategory": expected_subcategory,
                "source_file": str(source_file),
                "taxonomy_rule": "; ".join(taxonomy_rule_parts),
            }
        )
    return inventory


def build_curated_poi_coverage(database_path: str | Path) -> pd.DataFrame:
    """Summarize curated POI taxonomy coverage against configured expectations."""

    expected_inventory = _expected_curated_inventory()
    observed = pd.DataFrame(columns=["category", "subcategory", "rows"])
    unresolved_rows = 0
    duplicate_place_ids = 0
    total_rows = 0
    rows_without_place_details = 0

    canonical_table = POI_V3_TABLE if table_exists(database_path, POI_V3_TABLE) else POI_V2_TABLE

    if table_exists(database_path, canonical_table):
        available_columns = table_columns(database_path, canonical_table)
        category_expr = "NULLIF(TRIM(category), '')"
        if "primary_category" in available_columns:
            category_expr = f"COALESCE(NULLIF(TRIM(primary_category), ''), {category_expr})"

        subcategory_fallback_expr = category_expr
        if "subcategory" in available_columns:
            subcategory_fallback_expr = (
                f"COALESCE(NULLIF(TRIM(subcategory), ''), {subcategory_fallback_expr})"
            )
        if "primary_subcategory" in available_columns:
            subcategory_fallback_expr = (
                "COALESCE("
                "NULLIF(TRIM(primary_subcategory), ''), "
                f"{subcategory_fallback_expr}"
                ")"
            )

        with DuckDBService(database_path, read_only=True) as duckdb_service:
            observed = duckdb_service.query_df(
                f"""
                SELECT
                    COALESCE({category_expr}, 'other') AS category,
                    COALESCE({subcategory_fallback_expr}, 'other') AS subcategory,
                    COUNT(*) AS rows
                FROM {canonical_table}
                GROUP BY 1, 2
                """
            )
            total_rows = int(
                duckdb_service.query_df(
                    f"SELECT COUNT(*) AS rows FROM {canonical_table}"
                )["rows"].iloc[0]
            )
            unresolved_rows = int(
                duckdb_service.query_df(
                    f"""
                    SELECT COUNT(*) AS rows
                    FROM {canonical_table}
                    WHERE COALESCE(TRIM(category), '') IN ('', 'other')
                    """
                )["rows"].iloc[0]
            )
            duplicate_place_ids = int(
                duckdb_service.query_df(
                    f"""
                    SELECT COUNT(*) AS duplicate_place_ids
                    FROM (
                        SELECT google_place_id
                        FROM {canonical_table}
                        WHERE COALESCE(TRIM(google_place_id), '') <> ''
                        GROUP BY google_place_id
                        HAVING COUNT(*) > 1
                    )
                    """
                )["duplicate_place_ids"].iloc[0]
            )
            if "has_place_details" in available_columns:
                rows_without_place_details = int(
                    duckdb_service.query_df(
                        f"""
                        SELECT COUNT(*) AS rows
                        FROM {canonical_table}
                        WHERE COALESCE(has_place_details, FALSE) = FALSE
                        """
                    )["rows"].iloc[0]
                )

    observed_counts = {
        (str(row["category"]).strip(), str(row["subcategory"]).strip()): int(row["rows"])
        for _, row in observed.iterrows()
        if str(row["category"]).strip()
    }
    rows = []
    expected_keys = set()
    for item in expected_inventory:
        key = (item["category"], item["subcategory"])
        expected_keys.add(key)
        row_count = observed_counts.get(key, 0)
        rows.append(
            {
                "Category": item["category"],
                "Subcategory": item["subcategory"],
                "Expected files": item["source_file"],
                "Taxonomy rule": item["taxonomy_rule"],
                "Rows": row_count,
                "Expected": True,
                "Present": row_count > 0,
                "Status": "present" if row_count > 0 else "missing",
            }
        )

    for (category, subcategory), row_count in sorted(observed_counts.items()):
        if (category, subcategory) in expected_keys:
            continue
        rows.append(
            {
                "Category": category,
                "Subcategory": subcategory,
                "Expected files": "",
                "Taxonomy rule": "observed only",
                "Rows": row_count,
                "Expected": False,
                "Present": row_count > 0,
                "Status": "review",
            }
        )

    coverage = pd.DataFrame(rows).drop_duplicates(
        subset=["Category", "Subcategory", "Expected files"]
    ).sort_values(
        ["Expected", "Category", "Subcategory"],
        ascending=[False, True, True],
    )
    coverage.attrs["summary"] = {
        "expected_inventory_rows": len(expected_inventory),
        "total_rows": total_rows,
        "present_expected_categories": int(
            coverage.loc[coverage["Expected"], "Present"].fillna(False).astype(bool).sum()
        ),
        "missing_expected_categories": int(
            (~coverage.loc[coverage["Expected"], "Present"].fillna(False).astype(bool)).sum()
        ),
        "unresolved_rows": unresolved_rows,
        "duplicate_place_ids": duplicate_place_ids,
        "rows_without_place_details": rows_without_place_details,
    }
    return coverage.reset_index(drop=True)


def build_public_poi_coverage(
    database_path: str | Path,
    expected_categories: Iterable[str] = CATEGORY_SLUGS,
    ws3_categories: Iterable[str] = DEFAULT_PUBLIC_POI_CATEGORIES,
) -> pd.DataFrame:
    """Summarize public POI category coverage against the expected baseline set."""

    expected = sorted({canonical_public_poi_category(category) for category in expected_categories})
    ws3_selected = {
        canonical_public_poi_category(category)
        for category in ws3_categories
        if canonical_public_poi_category(category)
    }
    observed = pd.DataFrame(columns=["category", "rows", "source_systems", "latest_snapshot"])
    latest_snapshot = None
    total_rows = 0

    if table_exists(database_path, PUBLIC_POI_TABLE):
        with DuckDBService(database_path, read_only=True) as duckdb_service:
            observed = duckdb_service.query_df(
                f"""
                SELECT
                    category,
                    COUNT(*) AS rows,
                    string_agg(DISTINCT source_system, ', ' ORDER BY source_system) AS source_systems,
                    MAX(snapshotted_at) AS latest_snapshot
                FROM {PUBLIC_POI_TABLE}
                GROUP BY category
                """
            )
            total_rows = int(
                duckdb_service.query_df(
                    f"SELECT COUNT(*) AS rows FROM {PUBLIC_POI_TABLE}"
                )["rows"].iloc[0]
            )
            latest_snapshot = duckdb_service.query_df(
                f"SELECT MAX(snapshotted_at) AS latest_snapshot FROM {PUBLIC_POI_TABLE}"
            )["latest_snapshot"].iloc[0]

    observed_lookup = {
        canonical_public_poi_category(row["category"]): {
            "rows": int(row["rows"]),
            "source_systems": str(row["source_systems"] or "").strip(),
            "latest_snapshot": row["latest_snapshot"],
        }
        for _, row in observed.iterrows()
        if str(row["category"]).strip()
    }
    categories = sorted(set(expected).union(observed_lookup))
    rows = []
    for category in categories:
        observed_row = observed_lookup.get(category, {})
        row_count = int(observed_row.get("rows", 0))
        rows.append(
            {
                "Category": category,
                "Source systems": observed_row.get("source_systems", ""),
                "Rows": row_count,
                "Expected": category in expected,
                "Present": row_count > 0,
                "Included in WS3 UI": category in ws3_selected,
                "Status": "present" if row_count > 0 else "missing",
                "Latest snapshot": observed_row.get("latest_snapshot"),
            }
        )

    coverage = pd.DataFrame(rows).sort_values(
        ["Included in WS3 UI", "Category"],
        ascending=[False, True],
    )
    coverage.attrs["summary"] = {
        "expected_categories": len(expected),
        "total_rows": total_rows,
        "present_expected_categories": int(
            coverage.loc[coverage["Expected"], "Present"].fillna(False).astype(bool).sum()
        ),
        "missing_expected_categories": int(
            (~coverage.loc[coverage["Expected"], "Present"].fillna(False).astype(bool)).sum()
        ),
        "ws3_categories": len(ws3_selected),
        "ws3_missing_categories": int(
            (~coverage.loc[coverage["Included in WS3 UI"], "Present"].fillna(False).astype(bool)).sum()
        ),
        "latest_snapshot": latest_snapshot,
    }
    return coverage.reset_index(drop=True)


def build_pipeline_timestamps(database_path: str | Path) -> pd.DataFrame:
    """Summarize the freshest available timestamps for key data assets."""

    rows = [
        {
            "Asset": "DuckDB file",
            "Timestamp": datetime.fromtimestamp(Path(database_path).stat().st_mtime)
            if Path(database_path).exists()
            else pd.NaT,
            "Source": "filesystem modified time",
        }
    ]

    timestamp_queries = [
        ("Curated POI details", POI_V2_TABLE, "details_fetched_at"),
        ("Public POI snapshot", PUBLIC_POI_TABLE, "snapshotted_at"),
    ]
    for label, table_name, column in timestamp_queries:
        timestamp = pd.NaT
        if table_exists(database_path, table_name):
            with DuckDBService(database_path, read_only=True) as duckdb_service:
                timestamp = duckdb_service.query_df(
                    f"SELECT MAX({column}) AS ts FROM {table_name}"
                )["ts"].iloc[0]
        rows.append(
            {
                "Asset": label,
                "Timestamp": timestamp,
                "Source": f"{table_name}.{column}",
            }
        )

    file_timestamp_paths = [
        ("Curated POI resolution cache", DEFAULT_RESOLUTION_CACHE_PATH),
        ("Curated POI details cache", DEFAULT_DETAILS_CACHE_PATH),
    ]
    for label, path in file_timestamp_paths:
        rows.append(
            {
                "Asset": label,
                "Timestamp": datetime.fromtimestamp(path.stat().st_mtime) if path.exists() else pd.NaT,
                "Source": str(path.relative_to(PROJECT_ROOT)) if path.exists() else str(path),
            }
        )

    output = pd.DataFrame(rows)
    output["Timestamp"] = pd.to_datetime(output["Timestamp"], errors="coerce", utc=True)
    output["Timestamp label"] = output["Timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S").fillna("Unavailable")
    return output
