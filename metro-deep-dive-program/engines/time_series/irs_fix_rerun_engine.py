#!/usr/bin/env python3
"""IRS direction fix rerun (2026-10): build the trajectory mart side by side.

Usage, from the repository root:
    python3 metro-deep-dive-program/engines/time_series/irs_fix_rerun_engine.py control
    python3 metro-deep-dive-program/engines/time_series/irs_fix_rerun_engine.py fixed
    python3 metro-deep-dive-program/engines/time_series/irs_fix_rerun_engine.py fixed gdp_frozen
    python3 metro-deep-dive-program/engines/time_series/irs_fix_rerun_engine.py promote

Runs the same steps as build_time_series_engine.py on a read-only connection
and writes the four mart grains (series, metric, frame, turn signals) to
outputs_irs_fix_2026-10/<mode>/ as Parquet. It never writes to DuckDB.

- control: IRS registry sources (gold.migration_wide irs_* columns) are read
  from the before snapshot of gold.migration_wide, i.e. the reversed values the
  current mart was built from. Every other source still reads gold. This should
  reproduce the current intelligence_trajectory_* tables.
- fixed: current (fixed) gold.
- gdp_frozen (optional): the promotion run (Dan, 2026-10-26: ship the IRS fix
  alone). The two BEA GDP series (industry_concentration_hhi,
  pct_real_gdp_information) are read from the current mart's series table
  instead of gold, so the only input change is IRS. Outputs go to
  <mode>_gdp_frozen/.
- promote (Dan approved, 2026-10-26): replace the four canonical
  intelligence_trajectory_* tables with the fixed_gdp_frozen outputs, in one
  transaction, and refresh outputs/review/. build_time_series_engine.py is not
  used for this because it reads gold and would also publish the GDP refresh.

Spec: foundations/etl/IRS_MIGRATION_DIRECTION_FIX_SPEC.md, Part B.
"""

from __future__ import annotations

import re
import sys

import duckdb
import pandas as pd

from build_time_series_engine import (
    DEFAULT_CONFIG,
    ENGINE_DIR,
    REPO_ROOT,
    add_method_version,
    assert_mart_grains,
    build_frame_mart,
    build_metric_mart,
    build_sensitivity_summary,
    export_review_artifacts,
    materialize_table,
    build_turn_signals,
    db_path_from_environment,
    load_config,
    load_prepared_series,
    load_universe,
    validate_registry,
)

SNAPSHOT = (
    REPO_ROOT / "foundations" / "etl" / "data" / "snapshots" / "irs_direction_fix_2026-10" / "before" / "gold__migration_wide_irs.parquet"
)
# load_prepared_series reads one registry column per query in this shape:
#   CAST("<column>" AS DOUBLE) AS raw_value FROM gold."migration_wide"
IRS_SOURCE_QUERY = re.compile(r'CAST\("irs_[A-Za-z0-9_]+" AS DOUBLE\).*FROM gold\."migration_wide"', re.DOTALL)
SERIES_SNAPSHOT = SNAPSHOT.parent / "mart_intelligence__intelligence_trajectory_series.parquet"
GDP_SOURCE_QUERY = re.compile(r'CAST\("(industry_concentration_hhi|pct_real_gdp_information)" AS DOUBLE\)')


class SnapshotConnection:
    """Pass every query through, except the series reads being held at their old values.

    The engine code is used unchanged. In control mode the table reference in
    the IRS series query is swapped for the snapshot Parquet (same geo_level,
    geo_id, year and irs_* columns). With gdp_frozen, the GDP series query is
    replaced by the same CBSA-year raw values from the current mart's series
    table (the universe and years match; the year parameters are kept).
    """

    def __init__(self, con: duckdb.DuckDBPyConnection, control: bool, gdp_frozen: bool) -> None:
        self._con = con
        self._control = control
        self._gdp_frozen = gdp_frozen

    def execute(self, query: str, parameters=None):
        gdp_match = GDP_SOURCE_QUERY.search(query) if self._gdp_frozen else None
        if gdp_match:
            query = f"""
                SELECT DISTINCT cbsa_code, year, raw_value
                FROM read_parquet('{SERIES_SNAPSHOT}')
                WHERE source_column = '{gdp_match.group(1)}'
                  AND year BETWEEN ? AND ?
            """
            print(f"  [gdp_frozen] {gdp_match.group(1)} series read from the current mart")
        if self._control and IRS_SOURCE_QUERY.search(query):
            query = query.replace('gold."migration_wide"', f"read_parquet('{SNAPSHOT}')")
            print("  [control] IRS series read from the before snapshot")
        if parameters is None:
            return self._con.execute(query)
        return self._con.execute(query, parameters)


TABLES = [
    "intelligence_trajectory_series",
    "intelligence_trajectory_metric",
    "intelligence_trajectory_frame",
    "intelligence_trajectory_turn_signals",
]


def promote() -> None:
    """Load the reviewed fixed_gdp_frozen tables into mart_intelligence."""

    source = ENGINE_DIR / "outputs_irs_fix_2026-10" / "fixed_gdp_frozen"
    data = {name: pd.read_parquet(source / f"{name}.parquet") for name in TABLES}
    config = load_config(DEFAULT_CONFIG)
    assert_mart_grains(*(data[name] for name in TABLES))
    sensitivity = build_sensitivity_summary(data["intelligence_trajectory_frame"], config)

    with duckdb.connect(str(db_path_from_environment())) as con:
        # Same single transaction as the engine build, so consumers never see a
        # partially refreshed mart.
        con.execute("BEGIN TRANSACTION")
        try:
            for name in TABLES:
                materialize_table(con, name, data[name])
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
        export_review_artifacts(con, sensitivity)
        for name in TABLES:
            print(f"mart_intelligence.{name}: {con.execute(f'SELECT COUNT(*) FROM mart_intelligence.{name}').fetchone()[0]} rows")


def main() -> None:
    args = sys.argv[1:]
    if args == ["promote"]:
        promote()
        return
    if not args or args[0] not in {"control", "fixed"} or args[1:] not in ([], ["gdp_frozen"]):
        raise SystemExit("Usage: irs_fix_rerun_engine.py control|fixed [gdp_frozen]")
    mode, gdp_frozen = args[0], args[1:] == ["gdp_frozen"]
    if mode == "control" and not SNAPSHOT.exists():
        raise FileNotFoundError(SNAPSHOT)
    if gdp_frozen and not SERIES_SNAPSHOT.exists():
        raise FileNotFoundError(SERIES_SNAPSHOT)

    out_dir = ENGINE_DIR / "outputs_irs_fix_2026-10" / (f"{mode}_gdp_frozen" if gdp_frozen else mode)
    out_dir.mkdir(parents=True, exist_ok=True)
    config = load_config(DEFAULT_CONFIG)

    with duckdb.connect(str(db_path_from_environment()), read_only=True) as raw_con:
        con = SnapshotConnection(raw_con, control=mode == "control", gdp_frozen=gdp_frozen)
        validate_registry(con, config)
        universe = load_universe(con, config)
        series = load_prepared_series(con, universe, config)

    # Same assembly as build_time_series_engine.main(), minus the DuckDB write.
    metric = add_method_version(build_metric_mart(series, config), config)
    frame = add_method_version(build_frame_mart(metric, universe, config), config)
    turns = add_method_version(build_turn_signals(metric, frame, config), config)
    assert_mart_grains(series, metric, frame, turns)

    for name, data in {
        "intelligence_trajectory_series": series,
        "intelligence_trajectory_metric": metric,
        "intelligence_trajectory_frame": frame,
        "intelligence_trajectory_turn_signals": turns,
    }.items():
        data.to_parquet(out_dir / f"{name}.parquet", index=False)
        print(f"{name}: {len(data)} rows")
    print(f"IRS fix rerun (engine, {mode}) written to {out_dir.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
