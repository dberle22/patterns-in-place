"""Shared D2 helpers for tract-staged Place Intelligence builds."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import sys
from typing import Any

import pandas as pd


SECTION_ROOT = Path(__file__).resolve().parents[2]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from site_prep import METRIC_DEFINITIONS, MetricDefinition, Site, get_connection


D2_METRIC_COLUMNS = [metric.metric_id for metric in METRIC_DEFINITIONS]


def normalize_weight_table(weight_table: pd.DataFrame) -> pd.DataFrame:
    """Keep tract ids string-typed so CSV round-trips do not break D2 joins."""

    if weight_table.empty:
        return weight_table.copy()
    normalized = weight_table.copy()
    if "tract_geoid" in normalized.columns:
        normalized["tract_geoid"] = normalized["tract_geoid"].astype(str).str.zfill(11)
    return normalized


def build_tract_inputs_frame(site: Site) -> pd.DataFrame:
    """Join the required tract-level D2 Gold tables into one wide site-scoped input table."""

    frames: list[pd.DataFrame] = []
    for table_name in source_table_names():
        table_frame = query_gold_table_tract_inputs(table_name, site.market_id)
        if table_frame.empty:
            continue
        frames.append(table_frame)

    if not frames:
        return empty_tract_inputs_frame()

    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on=["tract_geoid", "year"], how="outer", sort=True)

    ordered_columns = ["tract_geoid", "year"] + [
        column for column in D2_METRIC_COLUMNS if column in merged.columns
    ]
    return merged[ordered_columns].sort_values(["year", "tract_geoid"], kind="mergesort").reset_index(drop=True)


def build_metric_long_frame(site: Site, weight_table: pd.DataFrame, tract_inputs: pd.DataFrame) -> pd.DataFrame:
    """Build the canonical D2 fact table from staged tract inputs plus saved ring weights."""

    metric_long_rows = build_metric_long_rows(site, weight_table, tract_inputs)
    benchmark_rows = build_benchmark_rows(site)
    rows = metric_long_rows + benchmark_rows
    if not rows:
        return empty_metric_long_frame()

    return pd.DataFrame(rows).sort_values(
        ["metric", "record_type", "ring_mi", "benchmark_level"],
        kind="mergesort",
        na_position="last",
    ).reset_index(drop=True)


def build_metric_long_rows(site: Site, weight_table: pd.DataFrame, tract_inputs: pd.DataFrame) -> list[dict[str, Any]]:
    """Aggregate staged tract inputs into ring-level catchment rows for every D2 metric."""

    normalized_weights = normalize_weight_table(weight_table)
    metric_long = tract_inputs_to_long(tract_inputs)
    if metric_long.empty or normalized_weights.empty:
        return []

    rows: list[dict[str, Any]] = []
    for metric in METRIC_DEFINITIONS:
        metric_rows = metric_long.loc[metric_long["metric"] == metric.metric_id].copy()
        if metric_rows.empty:
            continue

        latest_year = int(metric_rows["year"].max())
        latest_values = metric_rows.loc[metric_rows["year"] == latest_year, ["tract_geoid", "metric_value"]].dropna()
        if latest_values.empty:
            continue

        latest_result = apportion_metric_series(
            metric.metric_id,
            metric.kind,
            latest_values.set_index("tract_geoid")["metric_value"],
            normalized_weights,
        )
        if latest_result.empty:
            continue

        prior_year = latest_year - 5
        prior_values = metric_rows.loc[metric_rows["year"] == prior_year, ["tract_geoid", "metric_value"]].dropna()
        prior_result = (
            apportion_metric_series(
                metric.metric_id,
                metric.kind,
                prior_values.set_index("tract_geoid")["metric_value"],
                normalized_weights,
            )
            if not prior_values.empty
            else pd.Series(dtype=float)
        )

        latest_distribution = latest_values["metric_value"]
        denominator = int(len(latest_distribution))
        for ring_mi, value in latest_result.items():
            change_value = None
            change_years = None
            if not prior_result.empty and ring_mi in prior_result.index:
                change_value = float(value) - float(prior_result.loc[ring_mi])
                change_years = f"{prior_year}-{latest_year}"

            percentile = None
            percentile_denominator = None
            if int(ring_mi) == int(site.primary_ring_mi) and denominator > 0:
                percentile = float((latest_distribution <= float(value)).sum() / denominator * 100.0)
                percentile_denominator = denominator

            rows.append(
                {
                    "site_id": site.site_id,
                    "market_id": site.market_id,
                    "record_type": "catchment",
                    "metric": metric.metric_id,
                    "metric_label": metric.label,
                    "topic": metric.topic,
                    "ring_mi": int(ring_mi),
                    "benchmark_level": None,
                    "benchmark_geo_id": None,
                    "benchmark_geo_name": None,
                    "value": float(value),
                    "year": latest_year,
                    "source_table": metric.table_name,
                    "change_5yr": change_value,
                    "change_5yr_period": change_years,
                    "cbsa_percentile": percentile,
                    "cbsa_percentile_denominator": percentile_denominator,
                }
            )
    return rows


def build_metric_summary_frame(metric_long: pd.DataFrame, site: Site) -> pd.DataFrame:
    """Aggregate the canonical long table into one app-friendly row per metric."""

    if metric_long.empty:
        return empty_metric_summary_frame(site)

    catchment = metric_long.loc[metric_long["record_type"] == "catchment"].copy()
    if catchment.empty:
        return empty_metric_summary_frame(site)
    benchmarks = metric_long.loc[metric_long["record_type"] == "benchmark"].copy()

    rows: list[dict[str, Any]] = []
    ring_values = sorted(int(ring) for ring in site.rings_mi)
    for metric, metric_rows in catchment.groupby("metric", sort=False):
        metric_rows = metric_rows.sort_values("ring_mi", kind="mergesort").copy()
        first_row = metric_rows.iloc[0]
        primary_row = metric_rows.loc[metric_rows["ring_mi"] == int(site.primary_ring_mi)].head(1)
        benchmark_rows = benchmarks.loc[benchmarks["metric"] == metric].copy()

        row: dict[str, Any] = {
            "site_id": site.site_id,
            "market_id": site.market_id,
            "metric": metric,
            "metric_label": first_row["metric_label"],
            "topic": first_row["topic"],
            "source_table": first_row["source_table"],
            "primary_ring_mi": int(site.primary_ring_mi),
        }

        for ring_mi in ring_values:
            ring_row = metric_rows.loc[metric_rows["ring_mi"] == int(ring_mi)].head(1)
            row[f"ring_{ring_mi}_value"] = None if ring_row.empty else float(ring_row["value"].iloc[0])
            row[f"ring_{ring_mi}_year"] = None if ring_row.empty else int(ring_row["year"].iloc[0])
            row[f"ring_{ring_mi}_change_5yr"] = None if ring_row.empty or pd.isna(ring_row["change_5yr"].iloc[0]) else float(ring_row["change_5yr"].iloc[0])
            row[f"ring_{ring_mi}_change_5yr_period"] = None if ring_row.empty else ring_row["change_5yr_period"].iloc[0]

        if primary_row.empty:
            row["primary_value"] = None
            row["primary_year"] = None
            row["primary_change_5yr"] = None
            row["primary_change_5yr_period"] = None
            row["primary_cbsa_percentile"] = None
            row["primary_cbsa_percentile_denominator"] = None
        else:
            row["primary_value"] = float(primary_row["value"].iloc[0])
            row["primary_year"] = int(primary_row["year"].iloc[0])
            row["primary_change_5yr"] = None if pd.isna(primary_row["change_5yr"].iloc[0]) else float(primary_row["change_5yr"].iloc[0])
            row["primary_change_5yr_period"] = primary_row["change_5yr_period"].iloc[0]
            row["primary_cbsa_percentile"] = None if pd.isna(primary_row["cbsa_percentile"].iloc[0]) else float(primary_row["cbsa_percentile"].iloc[0])
            row["primary_cbsa_percentile_denominator"] = None if pd.isna(primary_row["cbsa_percentile_denominator"].iloc[0]) else int(primary_row["cbsa_percentile_denominator"].iloc[0])

        for benchmark_level in ["cbsa", "county", "state", "national"]:
            benchmark_row = benchmark_rows.loc[benchmark_rows["benchmark_level"] == benchmark_level].head(1)
            row[f"benchmark_{benchmark_level}_value"] = None if benchmark_row.empty else float(benchmark_row["value"].iloc[0])
            row[f"benchmark_{benchmark_level}_year"] = None if benchmark_row.empty else int(benchmark_row["year"].iloc[0])
            row[f"benchmark_{benchmark_level}_geo_name"] = None if benchmark_row.empty else benchmark_row["benchmark_geo_name"].iloc[0]

        rows.append(row)

    return pd.DataFrame(rows).sort_values(["topic", "metric_label"], kind="mergesort").reset_index(drop=True)


def build_catchment_profile_frame(metric_long: pd.DataFrame) -> pd.DataFrame:
    """Filter the canonical long table down to ring-level catchment rows."""

    if metric_long.empty:
        return pd.DataFrame()
    return (
        metric_long.loc[metric_long["record_type"] == "catchment"]
        .drop(columns=["record_type", "market_id"])
        .reset_index(drop=True)
    )


def build_benchmark_table_frame(metric_long: pd.DataFrame) -> pd.DataFrame:
    """Filter the canonical long table down to current benchmark rows."""

    if metric_long.empty:
        return empty_benchmark_table_frame()
    return (
        metric_long.loc[metric_long["record_type"] == "benchmark"]
        .drop(
            columns=[
                "record_type",
                "market_id",
                "change_5yr",
                "change_5yr_period",
                "cbsa_percentile",
                "cbsa_percentile_denominator",
            ]
        )
        .reset_index(drop=True)
    )


def build_skip_reasons_frame(site: Site, weight_table: pd.DataFrame, tract_inputs: pd.DataFrame) -> pd.DataFrame:
    """List the metrics that still cannot produce tract-weighted catchment rows."""

    normalized_weights = normalize_weight_table(weight_table)
    metric_long = tract_inputs_to_long(tract_inputs)
    reasons: list[dict[str, Any]] = []
    for metric in METRIC_DEFINITIONS:
        metric_rows = metric_long.loc[metric_long["metric"] == metric.metric_id].copy()
        if metric_rows.empty:
            reasons.append(
                {
                    "metric": metric.metric_id,
                    "reason": "No tract-grain values available for the configured market.",
                    "table_name": metric.table_name,
                }
            )
            continue

        latest_year = int(metric_rows["year"].max())
        latest_values = metric_rows.loc[metric_rows["year"] == latest_year, ["tract_geoid", "metric_value"]].dropna()
        if latest_values.empty:
            reasons.append(
                {
                    "metric": metric.metric_id,
                    "reason": "Latest tract-year values are empty after filtering nulls.",
                    "table_name": metric.table_name,
                }
            )
            continue

        result = apportion_metric_series(
            metric.metric_id,
            metric.kind,
            latest_values.set_index("tract_geoid")["metric_value"],
            normalized_weights,
        )
        if result.empty:
            reasons.append(
                {
                    "metric": metric.metric_id,
                    "reason": "No weighted overlap remained after joining tract values to base ring weights.",
                    "table_name": metric.table_name,
                }
            )
    return pd.DataFrame(reasons)


def build_d2_payload(site: Site, weight_table: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Compatibility assembler for callers that still expect the old D2 payload shape."""

    tract_inputs = build_tract_inputs_frame(site)
    metric_long = build_metric_long_frame(site, weight_table, tract_inputs)
    return {
        "metric_long": metric_long,
        "metric_summary": build_metric_summary_frame(metric_long, site),
        "catchment_profile": build_catchment_profile_frame(metric_long),
        "benchmark_table": build_benchmark_table_frame(metric_long),
        "skip_reasons": build_skip_reasons_frame(site, weight_table, tract_inputs),
    }


def tract_inputs_to_long(tract_inputs: pd.DataFrame) -> pd.DataFrame:
    """Unpivot one wide tract/year staging table into metric-long records."""

    if tract_inputs.empty:
        return pd.DataFrame(columns=["tract_geoid", "year", "metric", "metric_value"])

    value_columns = [column for column in D2_METRIC_COLUMNS if column in tract_inputs.columns]
    if not value_columns:
        return pd.DataFrame(columns=["tract_geoid", "year", "metric", "metric_value"])

    long_frame = tract_inputs.melt(
        id_vars=["tract_geoid", "year"],
        value_vars=value_columns,
        var_name="metric",
        value_name="metric_value",
    ).dropna(subset=["metric_value"])
    long_frame["tract_geoid"] = long_frame["tract_geoid"].astype(str).str.zfill(11)
    return long_frame.reset_index(drop=True)


def build_benchmark_rows(site: Site) -> list[dict[str, Any]]:
    """Project benchmark rows once per source table rather than once per metric."""

    county_geoid, state_fips = get_site_county_and_state(site)
    rows: list[dict[str, Any]] = []
    for table_name in source_table_names():
        benchmark_surface = query_gold_table_benchmark_inputs(table_name, site.market_id)
        if benchmark_surface.empty:
            continue

        latest_year = int(benchmark_surface["year"].max())
        latest_frame = benchmark_surface.loc[benchmark_surface["year"] == latest_year].copy()
        selector = (
            ((latest_frame["geo_level_normalized"] == "cbsa") & (latest_frame["geo_id"] == str(site.market_id)))
            | ((latest_frame["geo_level_normalized"] == "county") & (latest_frame["geo_id"] == county_geoid))
            | ((latest_frame["geo_level_normalized"] == "state") & (latest_frame["geo_id"] == state_fips))
            | (latest_frame["geo_level_normalized"] == "us")
        )
        selected = latest_frame.loc[selector].copy()
        if selected.empty:
            continue

        table_metrics = [metric for metric in METRIC_DEFINITIONS if metric.table_name == table_name]
        for metric in table_metrics:
            metric_rows = selected.loc[selected[metric.value_column].notna()].copy()
            for row in metric_rows.itertuples(index=False):
                rows.append(
                    {
                        "site_id": site.site_id,
                        "market_id": site.market_id,
                        "record_type": "benchmark",
                        "metric": metric.metric_id,
                        "metric_label": metric.label,
                        "topic": metric.topic,
                        "ring_mi": site.primary_ring_mi,
                        "benchmark_level": normalize_benchmark_level(str(row.geo_level_normalized)),
                        "benchmark_geo_id": str(row.geo_id),
                        "benchmark_geo_name": str(row.geo_name),
                        "value": float(getattr(row, metric.value_column)),
                        "year": int(row.year),
                        "source_table": table_name,
                        "change_5yr": None,
                        "change_5yr_period": None,
                        "cbsa_percentile": None,
                        "cbsa_percentile_denominator": None,
                    }
                )
    return rows


def apportion_metric_series(
    metric_name: str,
    kind: str,
    metric_series: pd.Series,
    weight_table: pd.DataFrame,
) -> pd.Series:
    """Push the tract-to-ring rollup into `apportion.py` with consistent D2 defaults."""

    from apportion import apportion

    named_series = metric_series.copy()
    named_series.name = metric_name
    method = "approximate" if is_median_metric(metric_name) else None
    result = apportion(named_series, normalize_weight_table(weight_table), kind=kind, method=method)
    if isinstance(result.index, pd.MultiIndex):
        result = result.droplevel(0)
    return result.sort_index()


def get_site_county_and_state(site: Site) -> tuple[str, str]:
    """Resolve county/state context once so every benchmark builder shares the same lookup."""

    tract_geoid: str
    if site.lat is not None and site.lon is not None:
        from geocode import resolve_tract_from_coordinates

        tract_geoid = resolve_tract_from_coordinates(site.lon, site.lat)
    else:
        from geocode import resolve_site_geocode

        tract_geoid = resolve_site_geocode(site).tract_geoid

    con = get_connection()
    try:
        row = con.execute(
            """
            SELECT county_geoid, state_fips
            FROM patterns_in_place.geo.tracts_all_us
            WHERE tract_geoid = ?
            LIMIT 1
            """,
            [tract_geoid],
        ).fetchone()
    finally:
        con.close()

    if row is None:
        raise ValueError(f"Could not resolve county/state for tract {tract_geoid}.")
    return str(row[0]), str(row[1]).zfill(2)


@lru_cache(maxsize=None)
def query_gold_table_tract_inputs(table_name: str, market_id: str) -> pd.DataFrame:
    """Read one tract-only D2 source table once and return only the required metric columns."""

    metric_columns = metric_value_columns_for_table(table_name)
    select_metric_columns = ",\n                ".join(f"t.{column}" for column in metric_columns)
    con = get_connection()
    try:
        rows = con.execute(
            f"""
            WITH market_counties AS (
                SELECT DISTINCT county_geoid
                FROM patterns_in_place.silver.xwalk_cbsa_county
                WHERE cbsa_code = ?
            )
            SELECT
                t.geo_id AS tract_geoid,
                t.year,
                {select_metric_columns}
            FROM patterns_in_place.gold.{table_name} t
            INNER JOIN patterns_in_place.geo.tracts_all_us g
                ON t.geo_id = g.tract_geoid
            WHERE LOWER(t.geo_level) = 'tract'
              AND g.county_geoid IN (SELECT county_geoid FROM market_counties)
            ORDER BY t.year, t.geo_id
            """,
            [str(market_id)],
        ).fetchdf()
    finally:
        con.close()

    if rows.empty:
        return pd.DataFrame(columns=["tract_geoid", "year", *metric_columns])
    rows["tract_geoid"] = rows["tract_geoid"].astype(str).str.zfill(11)
    return rows


@lru_cache(maxsize=None)
def query_gold_table_benchmark_inputs(table_name: str, market_id: str) -> pd.DataFrame:
    """Read one benchmark-only D2 source table once for the market comparison geographies."""

    metric_columns = metric_value_columns_for_table(table_name)
    select_metric_columns = ",\n                ".join(f"t.{column}" for column in metric_columns)
    con = get_connection()
    try:
        rows = con.execute(
            f"""
            SELECT
                LOWER(t.geo_level) AS geo_level_normalized,
                t.geo_level,
                t.geo_id,
                t.geo_name,
                t.year,
                {select_metric_columns}
            FROM patterns_in_place.gold.{table_name} t
            WHERE LOWER(t.geo_level) IN ('cbsa', 'county', 'state', 'us')
              AND (
                    LOWER(t.geo_level) != 'cbsa'
                 OR t.geo_id = ?
              )
            ORDER BY t.year, t.geo_level, t.geo_id
            """,
            [str(market_id)],
        ).fetchdf()
    finally:
        con.close()
    return rows


def source_table_names() -> list[str]:
    """Return the distinct D2 source Gold tables in a stable order."""

    return sorted({metric.table_name for metric in METRIC_DEFINITIONS})


def metric_value_columns_for_table(table_name: str) -> list[str]:
    """Return the D2 metric columns required from one Gold table."""

    columns = sorted(
        {
            metric.value_column
            for metric in METRIC_DEFINITIONS
            if metric.table_name == table_name
        }
    )
    if not columns:
        raise ValueError(f"No D2 metric columns registered for table '{table_name}'.")
    return columns


def is_median_metric(metric_name: str) -> bool:
    """Flag metrics that need approximate areal weighting rather than weighted means."""

    metric_name = metric_name.lower()
    return metric_name.startswith("median_") or metric_name.endswith("_median")


def normalize_benchmark_level(level: str) -> str:
    """Keep benchmark labels stable for downstream app contracts."""

    mapping = {"us": "national"}
    return mapping.get(level, level)


def empty_tract_inputs_frame() -> pd.DataFrame:
    """Return the empty tract staging shape used by the staged D2 build."""

    return pd.DataFrame(columns=["tract_geoid", "year", *D2_METRIC_COLUMNS])


def empty_metric_long_frame() -> pd.DataFrame:
    """Return the canonical empty D2 long-record frame."""

    return pd.DataFrame(
        columns=[
            "site_id",
            "market_id",
            "record_type",
            "metric",
            "metric_label",
            "topic",
            "ring_mi",
            "benchmark_level",
            "benchmark_geo_id",
            "benchmark_geo_name",
            "value",
            "year",
            "source_table",
            "change_5yr",
            "change_5yr_period",
            "cbsa_percentile",
            "cbsa_percentile_denominator",
        ]
    )


def empty_benchmark_table_frame() -> pd.DataFrame:
    """Return the legacy empty benchmark table shape."""

    return pd.DataFrame(
        columns=[
            "site_id",
            "ring_mi",
            "benchmark_level",
            "benchmark_geo_id",
            "benchmark_geo_name",
            "metric",
            "metric_label",
            "topic",
            "value",
            "year",
            "source_table",
        ]
    )


def empty_metric_summary_frame(site: Site) -> pd.DataFrame:
    """Return the app-facing empty D2 summary shape."""

    columns = [
        "site_id",
        "market_id",
        "metric",
        "metric_label",
        "topic",
        "source_table",
        "primary_ring_mi",
        "primary_value",
        "primary_year",
        "primary_change_5yr",
        "primary_change_5yr_period",
        "primary_cbsa_percentile",
        "primary_cbsa_percentile_denominator",
        "benchmark_cbsa_value",
        "benchmark_cbsa_year",
        "benchmark_cbsa_geo_name",
        "benchmark_county_value",
        "benchmark_county_year",
        "benchmark_county_geo_name",
        "benchmark_state_value",
        "benchmark_state_year",
        "benchmark_state_geo_name",
        "benchmark_national_value",
        "benchmark_national_year",
        "benchmark_national_geo_name",
    ]
    for ring_mi in sorted(int(ring) for ring in site.rings_mi):
        columns.extend(
            [
                f"ring_{ring_mi}_value",
                f"ring_{ring_mi}_year",
                f"ring_{ring_mi}_change_5yr",
                f"ring_{ring_mi}_change_5yr_period",
            ]
        )
    return pd.DataFrame(columns=columns)
