#!/usr/bin/env python3
"""Build the versioned Time-Series / Trajectory mart in DuckDB.

Usage:
    python3 metro-deep-dive-program/engines/time_series/build_time_series_engine.py

The script is intentionally sequential: it reads the declared Gold sources,
calculates all four mart grains, then replaces the four canonical tables in one
DuckDB transaction. Review exports are copied from those materialized tables.
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

import duckdb
import pandas as pd
import yaml

from trajectory_engine import (
    build_frame_mart,
    build_metric_mart,
    build_sensitivity_summary,
    build_turn_signals,
    empirical_percentile,
    transform_values,
)


ENGINE_DIR = Path(__file__).resolve().parent
REPO_ROOT = ENGINE_DIR.parents[2]
DEFAULT_CONFIG = ENGINE_DIR / "config" / "trajectory_metrics.yml"
REVIEW_DIR = ENGINE_DIR / "outputs" / "review"
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def db_path_from_environment() -> Path:
    """Resolve the shared DuckDB path from the environment or repo .Renviron."""

    configured = os.environ.get("DB_PATH")
    if configured:
        return Path(configured).expanduser()

    renviron = REPO_ROOT / ".Renviron"
    if renviron.exists():
        for line in renviron.read_text().splitlines():
            if line.startswith("DB_PATH="):
                return Path(line.split("=", 1)[1].strip().strip('"')).expanduser()
    raise RuntimeError("Set DB_PATH or add DB_PATH to the repository .Renviron file.")


def identifier(value: str) -> str:
    """Allow only simple schema/table/column names supplied by the checked-in registry."""

    if not IDENTIFIER.fullmatch(value):
        raise ValueError(f"Unsafe SQL identifier in trajectory registry: {value!r}")
    return f'"{value}"'


def sql_literal(value: str) -> str:
    """Quote a local output path for DuckDB COPY statements."""

    return "'" + value.replace("'", "''") + "'"


def load_config(path: Path) -> dict:
    """Load the declarative pilot registry once for the entire build."""

    with path.open() as handle:
        return yaml.safe_load(handle)


def validate_registry(con: duckdb.DuckDBPyConnection, config: dict) -> None:
    """Fail before scoring if a declared Gold source or field is unavailable."""

    seen_metrics: set[str] = set()
    for metric in config["metrics"]:
        metric_id = metric["metric_id"]
        if metric_id in seen_metrics:
            raise ValueError(f"Duplicate metric_id in registry: {metric_id}")
        seen_metrics.add(metric_id)

        table = metric["source_table"]
        column = metric["source_column"]
        exists = con.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = 'gold' AND table_name = ? AND column_name = ?
            """,
            [table, column],
        ).fetchone()[0]
        if not exists:
            raise ValueError(f"Registry source gold.{table}.{column} is not available in DuckDB.")

        for window_name in metric["windows"]:
            if window_name not in config["engine"]["windows"]:
                raise ValueError(f"Metric {metric_id} references unknown window {window_name}.")


def load_universe(con: duckdb.DuckDBPyConnection, config: dict) -> pd.DataFrame:
    """Load the stable population-based CBSA universe used for national ranks."""

    universe = config["engine"]["universe"]
    result = con.execute(
        """
        SELECT DISTINCT
            CAST(geo_id AS VARCHAR) AS cbsa_code,
            geo_name AS cbsa_name
        FROM gold.population_demographics
        WHERE geo_level = 'cbsa'
          AND year = ?
          AND pop_total >= ?
          AND geo_name NOT LIKE '%' || ?
        ORDER BY cbsa_code
        """,
        [universe["base_year"], universe["min_population"], universe["excluded_name_suffix"]],
    ).fetchdf()
    if result.empty:
        raise RuntimeError("The trajectory universe query returned no CBSAs.")
    if result["cbsa_code"].duplicated().any():
        raise RuntimeError("The trajectory universe has duplicate CBSA codes.")
    return result


def load_prepared_series(con: duckdb.DuckDBPyConnection, universe: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Normalize all registry sources into one CBSA × metric × year annual panel."""

    windows = config["engine"]["windows"].values()
    history_start = min(window["start_year"] for window in windows)
    history_end = max(window["end_year"] for window in windows)
    years = pd.DataFrame({"year": list(range(history_start, history_end + 1))})
    universe_keyed = universe.assign(_cross_key=1)
    years_keyed = years.assign(_cross_key=1)
    base_panel = universe_keyed.merge(years_keyed, on="_cross_key").drop(columns="_cross_key")
    records: list[pd.DataFrame] = []

    for metric in config["metrics"]:
        table = identifier(metric["source_table"])
        column = identifier(metric["source_column"])
        source = con.execute(
            f"""
            SELECT
                CAST(geo_id AS VARCHAR) AS cbsa_code,
                year,
                CAST({column} AS DOUBLE) AS raw_value
            FROM gold.{table}
            WHERE geo_level = 'cbsa'
              AND year BETWEEN ? AND ?
            """,
            [history_start, history_end],
        ).fetchdf()
        if source.duplicated(["cbsa_code", "year"]).any():
            raise RuntimeError(f"gold.{metric['source_table']} has duplicate CBSA/year rows for {metric['metric_id']}.")

        prepared = base_panel.merge(source, how="left", on=["cbsa_code", "year"])
        prepared["transformed_value"] = transform_values(prepared["raw_value"], metric["transform"])
        prepared["national_percentile"] = prepared.groupby("year")["transformed_value"].transform(empirical_percentile)
        prepared["eligibility_status"] = prepared["transformed_value"].notna().map(
            {True: "available", False: "missing_value"}
        )
        prepared["method_version"] = config["engine"]["method_version"]
        prepared["frame_id"] = metric["frame_id"]
        prepared["topic_id"] = metric["topic_id"]
        prepared["metric_id"] = metric["metric_id"]
        prepared["metric_label"] = metric["metric_label"]
        prepared["source_schema"] = "gold"
        prepared["source_table"] = metric["source_table"]
        prepared["source_column"] = metric["source_column"]
        prepared["transform"] = metric["transform"]
        prepared["polarity"] = metric["polarity"]
        records.append(prepared)

    result = pd.concat(records, ignore_index=True)
    key = ["method_version", "cbsa_code", "metric_id", "year"]
    if result.duplicated(key).any():
        raise RuntimeError("Prepared trajectory series violates its declared primary grain.")
    return result[
        [
            "method_version",
            "cbsa_code",
            "cbsa_name",
            "frame_id",
            "topic_id",
            "metric_id",
            "metric_label",
            "source_schema",
            "source_table",
            "source_column",
            "transform",
            "polarity",
            "year",
            "raw_value",
            "transformed_value",
            "national_percentile",
            "eligibility_status",
        ]
    ]


def add_method_version(frame: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Attach the version key consistently to derived mart grains."""

    result = frame.copy()
    result.insert(0, "method_version", config["engine"]["method_version"])
    return result


def assert_mart_grains(series: pd.DataFrame, metric: pd.DataFrame, frame: pd.DataFrame, turns: pd.DataFrame) -> None:
    """Check each output's key before replacing any canonical DuckDB table."""

    checks = {
        "series": (series, ["method_version", "cbsa_code", "metric_id", "year"]),
        "metric": (metric, ["method_version", "cbsa_code", "metric_id", "window_name", "end_year"]),
        "frame": (frame, ["method_version", "cbsa_code", "frame_id", "window_name", "end_year"]),
        "turn": (turns, ["method_version", "cbsa_code", "frame_id", "method_window_pair", "end_year"]),
    }
    for name, (data, key) in checks.items():
        if data.duplicated(key).any():
            raise RuntimeError(f"Trajectory {name} mart violates its declared grain: {key}")


def materialize_table(con: duckdb.DuckDBPyConnection, table_name: str, data: pd.DataFrame) -> None:
    """Replace one canonical table from its already validated in-memory result."""

    temporary_name = f"_trajectory_{table_name}"
    con.register(temporary_name, data)
    con.execute(f"CREATE OR REPLACE TABLE mart_intelligence.{identifier(table_name)} AS SELECT * FROM {identifier(temporary_name)}")
    con.unregister(temporary_name)


def export_review_artifacts(con: duckdb.DuckDBPyConnection, sensitivity: pd.DataFrame) -> None:
    """Write non-canonical review snapshots only after the canonical mart is built."""

    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    tables = [
        "intelligence_trajectory_series",
        "intelligence_trajectory_metric",
        "intelligence_trajectory_frame",
        "intelligence_trajectory_turn_signals",
    ]
    for table_name in tables:
        destination = REVIEW_DIR / f"{table_name}.parquet"
        con.execute(
            f"COPY mart_intelligence.{identifier(table_name)} TO {sql_literal(str(destination))} (FORMAT PARQUET)"
        )

    con.register("_trajectory_sensitivity", sensitivity)
    destination = REVIEW_DIR / "trajectory_threshold_sensitivity.csv"
    con.execute(f"COPY _trajectory_sensitivity TO {sql_literal(str(destination))} (HEADER, DELIMITER ',')")
    con.unregister("_trajectory_sensitivity")


def print_summary(universe: pd.DataFrame, series: pd.DataFrame, metric: pd.DataFrame, frame: pd.DataFrame, turns: pd.DataFrame) -> None:
    """Give a compact audit summary suitable for build logs and review."""

    print(f"Universe: {len(universe):,} CBSAs")
    print(f"Series rows: {len(series):,}")
    print(f"Metric rows: {len(metric):,}; eligible: {(metric['coverage_status'] == 'eligible').sum():,}")
    print(f"Frame rows: {len(frame):,}; eligible: {(frame['coverage_status'] == 'eligible').sum():,}")
    print("Turn signals:")
    print(turns["turn_status"].value_counts(dropna=False).to_string())


def main() -> None:
    """Run the build from one checked-in metric registry and one shared DuckDB path."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Path to the trajectory metric registry.")
    parser.add_argument("--db-path", type=Path, help="Override DB_PATH for this invocation.")
    parser.add_argument("--dry-run", action="store_true", help="Calculate and validate outputs without replacing mart tables.")
    args = parser.parse_args()

    config = load_config(args.config)
    database = args.db_path or db_path_from_environment()
    if not database.exists():
        raise FileNotFoundError(f"DuckDB database does not exist: {database}")

    with duckdb.connect(str(database)) as con:
        validate_registry(con, config)
        universe = load_universe(con, config)
        series = load_prepared_series(con, universe, config)
        metric = add_method_version(build_metric_mart(series, config), config)
        frame = add_method_version(build_frame_mart(metric, universe, config), config)
        turns = add_method_version(build_turn_signals(metric, frame, config), config)
        sensitivity = build_sensitivity_summary(frame, config)
        assert_mart_grains(series, metric, frame, turns)
        print_summary(universe, series, metric, frame, turns)

        if args.dry_run:
            print("Dry run complete; no DuckDB tables or review exports were written.")
            return

        # One transaction prevents consumers from seeing a partially refreshed mart.
        con.execute("BEGIN TRANSACTION")
        try:
            con.execute("CREATE SCHEMA IF NOT EXISTS mart_intelligence")
            materialize_table(con, "intelligence_trajectory_series", series)
            materialize_table(con, "intelligence_trajectory_metric", metric)
            materialize_table(con, "intelligence_trajectory_frame", frame)
            materialize_table(con, "intelligence_trajectory_turn_signals", turns)
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
        export_review_artifacts(con, sensitivity)
        print(f"Materialized mart_intelligence trajectory tables and review exports in {REVIEW_DIR.relative_to(REPO_ROOT)}.")


if __name__ == "__main__":
    main()
