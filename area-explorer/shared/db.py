"""Shared DuckDB access for Area Explorer."""

from __future__ import annotations

import os
from pathlib import Path
import re
from typing import Any

import duckdb
import pandas as pd
import streamlit as st

from shared.catalog import get_metric_meta, get_table_meta


INTELLIGENCE_PARQUETS = {
    "intelligence_character": "exploration/intelligence_framework/phase_2_character_calibration/outputs/character_scores.parquet",
    "intelligence_livability": "exploration/intelligence_framework/phase_3_livability_calibration/outputs/livability_scores.parquet",
    "intelligence_opportunity": "exploration/intelligence_framework/phase_4_opportunity_calibration/outputs/opportunity_scores.parquet",
    "intelligence_cross_frame": "exploration/intelligence_framework/phase_5_cross_frame_integration/outputs/cross_frame_scores.parquet",
}
VALID_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PRIMARY_STATE_ABBR_PATTERN = re.compile(r",\s*([A-Z]{2})(?:-[A-Z]{2})*$")
STATE_ABBR_TO_NAME = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    "DC": "District of Columbia",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_db_path() -> Path:
    return _repo_root() / "foundations" / "etl" / "data" / "duckdb" / "patterns_in_place.duckdb"


def _normalize_geo_level_expression(column_name: str) -> str:
    return (
        f"CASE "
        f"WHEN {column_name} = 'US' THEN 'us' "
        f"WHEN {column_name} = 'Region' THEN 'region' "
        f"ELSE lower({column_name}) END"
    )


def _quote_identifier(identifier: str) -> str:
    if not VALID_IDENTIFIER.match(identifier):
        raise ValueError(f"Unsafe identifier: {identifier}")
    return f'"{identifier}"'


def _derive_primary_state_abbr(geo_name: str | None) -> str | None:
    """Extract the first state abbreviation from a CBSA display name."""
    if not geo_name:
        return None
    match = PRIMARY_STATE_ABBR_PATTERN.search(str(geo_name))
    if match is None:
        return None
    return match.group(1)


def _fill_primary_state_context(
    df: pd.DataFrame,
    *,
    geo_name_col: str,
    state_name_col: str,
    state_abbr_col: str | None = None,
) -> pd.DataFrame:
    """Backfill a primary state for multi-state CBSAs when dim_geo leaves it null.

    The current geography dimension intentionally leaves some multi-state CBSA
    state fields null. For the explorer we want a stable, human-readable
    default, so we use the first state abbreviation in the CBSA name as the
    primary state.
    """
    if df.empty:
        return df

    filled = df.copy()
    if state_abbr_col is not None and state_abbr_col in filled.columns:
        parsed_abbr = filled[geo_name_col].map(_derive_primary_state_abbr)
        filled[state_abbr_col] = filled[state_abbr_col].fillna(parsed_abbr)
    else:
        parsed_abbr = filled[geo_name_col].map(_derive_primary_state_abbr)

    if state_name_col in filled.columns:
        filled[state_name_col] = filled[state_name_col].fillna(parsed_abbr.map(STATE_ABBR_TO_NAME))
    return filled


def resolve_db_path() -> Path:
    """Resolve the DuckDB path from env vars or the repo default."""
    db_connection = os.getenv("DB_CONNECTION") or os.getenv("DB_PATH")
    if db_connection:
        return Path(db_connection)
    return _default_db_path()


def get_connection() -> duckdb.DuckDBPyConnection:
    """Open a read-only DuckDB connection from the configured path."""
    db_path = resolve_db_path()
    if not db_path.exists():
        raise FileNotFoundError(f"DuckDB file does not exist: {db_path}")
    return duckdb.connect(str(db_path), read_only=True)


@st.cache_data(ttl=3600)
def has_intelligence_datamart() -> bool:
    """Return whether the connected DuckDB has the promoted intelligence schema."""
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'mart_intelligence'
              AND table_name IN (
                'intelligence_character',
                'intelligence_livability',
                'intelligence_opportunity',
                'intelligence_cross_frame'
              )
            """
        ).fetchone()
        return bool(rows and rows[0] >= 3)
    finally:
        connection.close()


def _intelligence_relation(table_name: str) -> str:
    """Resolve an intelligence source to either the datamart table or its phase parquet."""
    if has_intelligence_datamart():
        return f"mart_intelligence.{table_name}"

    parquet_rel_path = INTELLIGENCE_PARQUETS.get(table_name)
    if parquet_rel_path is None:
        raise ValueError(f"Unknown intelligence table: {table_name}")

    parquet_path = _repo_root() / parquet_rel_path
    if not parquet_path.exists():
        raise FileNotFoundError(f"Intelligence parquet does not exist: {parquet_path}")
    return f"read_parquet('{parquet_path.as_posix()}')"


def _character_select_fields() -> str:
    if has_intelligence_datamart():
        return """
            cbsa_code,
            cbsa_name,
            character_percentile_rank,
            character_cluster,
            demographics_score,
            social_fabric_score
        """
    return """
        cbsa_code,
        cbsa_name,
        CAST(round(character_percentile) AS INTEGER) AS character_percentile_rank,
        character_cluster_name AS character_cluster,
        subject_score_demographics AS demographics_score,
        subject_score_social_fabric AS social_fabric_score
    """


def _livability_select_fields() -> str:
    if has_intelligence_datamart():
        return """
            cbsa_code,
            livability_percentile_rank,
            livability_cluster,
            affordability_score,
            health_and_safety_score,
            access_and_infrastructure_score,
            physical_environment_score
        """
    return """
        cbsa_code,
        CAST(round(livability_percentile) AS INTEGER) AS livability_percentile_rank,
        livability_cluster_name AS livability_cluster,
        subject_score_affordability AS affordability_score,
        subject_score_health_and_safety AS health_and_safety_score,
        subject_score_access_and_infrastructure AS access_and_infrastructure_score,
        subject_score_physical_environment AS physical_environment_score
    """


def _opportunity_select_fields() -> str:
    if has_intelligence_datamart():
        return """
            cbsa_code,
            opportunity_percentile_rank,
            opportunity_cluster,
            resident_opportunity_score,
            market_opportunity_score,
            business_and_industry_score
        """
    return """
        cbsa_code,
        CAST(round(opportunity_percentile) AS INTEGER) AS opportunity_percentile_rank,
        opportunity_cluster_name AS opportunity_cluster,
        subject_score_resident_opportunity AS resident_opportunity_score,
        subject_score_market_opportunity AS market_opportunity_score,
        subject_score_business_and_industry_opportunity AS business_and_industry_score
    """


def _cross_frame_select_fields() -> str:
    if has_intelligence_datamart():
        return """
            cbsa_code,
            combined_cluster,
            cross_frame_percentile_rank,
            top_gmm_cluster,
            top_gmm_probability,
            second_gmm_cluster,
            second_gmm_probability,
            NULL::BOOLEAN AS cross_frame_divergence_flag
        """
    return """
        cbsa_code,
        cross_frame_cluster_name AS combined_cluster,
        CAST(round(cross_frame_percentile) AS INTEGER) AS cross_frame_percentile_rank,
        top_gmm_cluster,
        top_gmm_probability,
        second_gmm_cluster,
        second_gmm_probability,
        NULL::BOOLEAN AS cross_frame_divergence_flag
    """


def _metric_table_ref(metric_id: str) -> tuple[str, str, str]:
    metric_meta = get_metric_meta(metric_id)
    if metric_meta is None:
        raise ValueError(f"Unknown metric: {metric_id}")

    table_id = metric_meta["source_table"]
    if str(table_id).startswith("intelligence_"):
        raise ValueError(f"Metric picker does not currently support intelligence metric leafs: {metric_id}")

    table_meta = get_table_meta(table_id)
    if table_meta is None:
        raise ValueError(f"Unknown source table for metric {metric_id}: {table_id}")

    return table_meta["schema"], table_meta["table_name"], metric_meta["source_column"]


@st.cache_data(ttl=3600)
def get_state_options() -> list[tuple[str, str]]:
    """Return selectable state options for CBSA filtering."""
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT DISTINCT state_name, state_fips
            FROM gold.dim_geo
            WHERE geo_level = 'cbsa'
              AND state_fips IS NOT NULL
            ORDER BY state_name, state_fips
            """
        ).fetchall()
    finally:
        connection.close()

    return [(state_name, state_fips) for state_name, state_fips in rows]


@st.cache_data(ttl=3600)
def query_available_years(metric_id: str, geo_level: str = "cbsa") -> list[int]:
    """Return available years for a metric and geography level."""
    schema_name, table_name, _ = _metric_table_ref(metric_id)
    connection = get_connection()
    try:
        rows = connection.execute(
            f"""
            SELECT DISTINCT year
            FROM {schema_name}.{table_name}
            WHERE {_normalize_geo_level_expression('geo_level')} = ?
            ORDER BY year DESC
            """,
            [geo_level],
        ).fetchall()
    finally:
        connection.close()
    return [int(year) for (year,) in rows]


@st.cache_data(ttl=3600)
def query_metric(metric_id: str, year: int, state_filter: tuple[str, ...] = ()) -> pd.DataFrame:
    """Query a single metric across the CBSA universe with benchmark context."""
    schema_name, table_name, source_column = _metric_table_ref(metric_id)
    quoted_column = _quote_identifier(source_column)

    state_filter_clause = ""
    state_filter_values: list[Any] = [year]
    if state_filter:
        placeholders = ", ".join("?" for _ in state_filter)
        state_filter_clause = f"WHERE ranked.state_fips IN ({placeholders})"
        state_filter_values.extend(state_filter)

    connection = get_connection()
    try:
        metric_df = connection.execute(
            f"""
            WITH metric_base AS (
              SELECT
                {_normalize_geo_level_expression('geo_level')} AS geo_level_norm,
                geo_id,
                geo_name,
                year,
                {quoted_column} AS metric_value
              FROM {schema_name}.{table_name}
              WHERE year = ?
                AND {_normalize_geo_level_expression('geo_level')} = 'cbsa'
                AND {quoted_column} IS NOT NULL
            ),
            ranked AS (
              SELECT
                mb.geo_id,
                mb.geo_name,
                mb.year,
                mb.metric_value,
                dg.state_fips,
                dg.state_name,
                dg.division_name,
                dg.region_name,
                dg.primary_city_name,
                PERCENT_RANK() OVER (
                  PARTITION BY mb.year
                  ORDER BY mb.metric_value
                ) * 100 AS national_pct_rank,
                PERCENT_RANK() OVER (
                  PARTITION BY mb.year, dg.division_name
                  ORDER BY mb.metric_value
                ) * 100 AS division_pct_rank
              FROM metric_base mb
              LEFT JOIN gold.dim_geo dg
                ON dg.geo_level = 'cbsa'
               AND dg.geo_id = mb.geo_id
            )
            SELECT *
            FROM ranked
            {state_filter_clause}
            ORDER BY metric_value DESC, geo_name
            """,
            state_filter_values,
        ).fetchdf()
    finally:
        connection.close()
    return _fill_primary_state_context(
        metric_df,
        geo_name_col="geo_name",
        state_name_col="state_name",
    )


@st.cache_data(ttl=3600)
def query_metric_timeseries(metric_id: str, geo_id: str) -> pd.DataFrame:
    """Return the full metric time series for one CBSA."""
    schema_name, table_name, source_column = _metric_table_ref(metric_id)
    quoted_column = _quote_identifier(source_column)
    connection = get_connection()
    try:
        return connection.execute(
            f"""
            SELECT
              year,
              geo_id,
              geo_name,
              {quoted_column} AS metric_value
            FROM {schema_name}.{table_name}
            WHERE {_normalize_geo_level_expression('geo_level')} = 'cbsa'
              AND geo_id = ?
              AND {quoted_column} IS NOT NULL
            ORDER BY year
            """,
            [geo_id],
        ).fetchdf()
    finally:
        connection.close()


@st.cache_data(ttl=3600)
def query_metric_timeseries_batch(metric_id: str, geo_ids: tuple[str, ...]) -> pd.DataFrame:
    """Return a metric time series for multiple CBSAs for comparison charts."""
    if not geo_ids:
        return pd.DataFrame(columns=["year", "geo_id", "geo_name", "metric_value"])

    schema_name, table_name, source_column = _metric_table_ref(metric_id)
    quoted_column = _quote_identifier(source_column)
    placeholders = ", ".join("?" for _ in geo_ids)

    connection = get_connection()
    try:
        return connection.execute(
            f"""
            SELECT
              year,
              geo_id,
              geo_name,
              {quoted_column} AS metric_value
            FROM {schema_name}.{table_name}
            WHERE {_normalize_geo_level_expression('geo_level')} = 'cbsa'
              AND geo_id IN ({placeholders})
              AND {quoted_column} IS NOT NULL
            ORDER BY geo_name, year
            """,
            list(geo_ids),
        ).fetchdf()
    finally:
        connection.close()


@st.cache_data(ttl=3600)
def query_metric_timeseries_bounds(metric_id: str) -> tuple[float | None, float | None]:
    """Return global CBSA min/max bounds for a metric across all available years.

    The trend chart uses these bounds so a metro's time series sits in the
    context of the broader CBSA distribution rather than re-scaling to only the
    selected places on every interaction.
    """
    schema_name, table_name, source_column = _metric_table_ref(metric_id)
    quoted_column = _quote_identifier(source_column)

    connection = get_connection()
    try:
        row = connection.execute(
            f"""
            SELECT
              MIN({quoted_column}) AS metric_min,
              MAX({quoted_column}) AS metric_max
            FROM {schema_name}.{table_name}
            WHERE {_normalize_geo_level_expression('geo_level')} = 'cbsa'
              AND {quoted_column} IS NOT NULL
              AND isfinite({quoted_column})
            """
        ).fetchone()
    finally:
        connection.close()

    if row is None:
        return (None, None)
    metric_min, metric_max = row
    return (
        float(metric_min) if metric_min is not None else None,
        float(metric_max) if metric_max is not None else None,
    )


@st.cache_data(ttl=3600)
def query_intelligence_profile(cbsa_code: str) -> dict[str, Any]:
    """Return Intelligence summary fields for one CBSA."""
    connection = get_connection()
    profile: dict[str, Any] = {}
    try:
        rows = connection.execute(
            f"""
            WITH character AS (
              SELECT {_character_select_fields()}
              FROM {_intelligence_relation('intelligence_character')}
            ),
            livability AS (
              SELECT {_livability_select_fields()}
              FROM {_intelligence_relation('intelligence_livability')}
            ),
            opportunity AS (
              SELECT {_opportunity_select_fields()}
              FROM {_intelligence_relation('intelligence_opportunity')}
            ),
            cross_frame AS (
              SELECT {_cross_frame_select_fields()}
              FROM {_intelligence_relation('intelligence_cross_frame')}
            )
            SELECT
              c.*,
              l.livability_percentile_rank,
              l.livability_cluster,
              l.affordability_score,
              l.health_and_safety_score,
              l.access_and_infrastructure_score,
              l.physical_environment_score,
              o.opportunity_percentile_rank,
              o.opportunity_cluster,
              o.resident_opportunity_score,
              o.market_opportunity_score,
              o.business_and_industry_score,
              x.combined_cluster,
              x.cross_frame_percentile_rank,
              x.top_gmm_cluster,
              x.top_gmm_probability,
              x.second_gmm_cluster,
              x.second_gmm_probability,
              x.cross_frame_divergence_flag
            FROM character c
            LEFT JOIN livability l USING (cbsa_code)
            LEFT JOIN opportunity o USING (cbsa_code)
            LEFT JOIN cross_frame x USING (cbsa_code)
            WHERE c.cbsa_code = ?
            """,
            [cbsa_code],
        ).fetchone()
    finally:
        connection.close()

    if rows is None:
        return {}

    columns = [
        "cbsa_code",
        "cbsa_name",
        "character_percentile_rank",
        "character_cluster",
        "demographics_score",
        "social_fabric_score",
        "livability_percentile_rank",
        "livability_cluster",
        "affordability_score",
        "health_and_safety_score",
        "access_and_infrastructure_score",
        "physical_environment_score",
        "opportunity_percentile_rank",
        "opportunity_cluster",
        "resident_opportunity_score",
        "market_opportunity_score",
        "business_and_industry_score",
        "combined_cluster",
        "cross_frame_percentile_rank",
        "top_gmm_cluster",
        "top_gmm_probability",
        "second_gmm_cluster",
        "second_gmm_probability",
        "cross_frame_divergence_flag",
    ]
    return dict(zip(columns, rows))


@st.cache_data(ttl=3600)
def query_similarity_peers(cbsa_code: str, limit: int = 10) -> pd.DataFrame:
    """Return the ranked peer list for one CBSA from the wide cross-frame table."""
    peer_limit = max(1, min(limit, 10))

    if has_intelligence_datamart():
        peer_rows = [
            (
                index,
                f"top10_peer_{index}_cbsa_code",
                f"top10_peer_{index}_cbsa_name",
                f"top10_peer_{index}_similarity",
            )
            for index in range(1, peer_limit + 1)
        ]

        select_clauses = []
        for peer_rank, code_col, name_col, similarity_col in peer_rows:
            select_clauses.append(
                f"""
                SELECT
                    {peer_rank} AS peer_rank,
                    {code_col} AS peer_cbsa_code,
                    {name_col} AS peer_cbsa_name,
                    {similarity_col} AS similarity
                FROM mart_intelligence.intelligence_cross_frame
                WHERE cbsa_code = ?
                """
            )

        query_sql = "\nUNION ALL\n".join(select_clauses) + "\nORDER BY peer_rank"
        parameters = [cbsa_code] * peer_limit
    else:
        query_sql = f"""
            SELECT
                1 AS peer_rank,
                peer_1_code AS peer_cbsa_code,
                peer_1_name AS peer_cbsa_name,
                peer_1_similarity AS similarity
            FROM {_intelligence_relation('intelligence_cross_frame')}
            WHERE cbsa_code = ?
            ORDER BY peer_rank
        """
        parameters = [cbsa_code]

    connection = get_connection()
    try:
        peers = connection.execute(query_sql, parameters).fetchdf()
    finally:
        connection.close()

    if peers.empty:
        return peers

    return peers.loc[peers["peer_cbsa_code"].notna()].reset_index(drop=True)


@st.cache_data(ttl=3600)
def query_peer_comparison_snapshot(
    cbsa_code: str,
    year: int,
    peer_limit: int = 5,
) -> pd.DataFrame:
    """Return a compact selected-CBSA-plus-peers comparison table for the UI.

    This uses the app-serving mart when available because it already contains
    the key comparison fields we want to show together in one row model.
    """
    peers_df = query_similarity_peers(cbsa_code, limit=peer_limit)
    comparison_ids = tuple([cbsa_code, *peers_df["peer_cbsa_code"].tolist()])
    placeholders = ", ".join("?" for _ in comparison_ids)

    connection = get_connection()
    try:
        comparison_df = connection.execute(
            f"""
            SELECT
              cbsa_code,
              cbsa_name,
              state_name_primary,
              pop_total,
              median_hh_income,
              rent_to_income,
              character_percentile_rank,
              livability_percentile_rank,
              opportunity_percentile_rank
            FROM mart_area_explorer.cbsa_profile_year
            WHERE year = ?
              AND cbsa_code IN ({placeholders})
            """,
            [year, *comparison_ids],
        ).fetchdf()
    finally:
        connection.close()

    if comparison_df.empty:
        return comparison_df

    comparison_df["peer_rank"] = comparison_df["cbsa_code"].map(
        {cbsa_code: 0, **dict(zip(peers_df["peer_cbsa_code"], peers_df["peer_rank"]))}
    )
    comparison_df["similarity"] = comparison_df["cbsa_code"].map(
        {cbsa_code: 1.0, **dict(zip(peers_df["peer_cbsa_code"], peers_df["similarity"]))}
    )
    comparison_df["comparison_role"] = comparison_df["cbsa_code"].map(
        {cbsa_code: "Selected", **{peer_code: "Peer" for peer_code in peers_df["peer_cbsa_code"]}}
    )
    comparison_df = _fill_primary_state_context(
        comparison_df,
        geo_name_col="cbsa_name",
        state_name_col="state_name_primary",
    )
    return comparison_df.sort_values(["peer_rank", "cbsa_name"]).reset_index(drop=True)


@st.cache_data(ttl=3600)
def query_intelligence_scatter(state_filter: tuple[str, ...] = ()) -> pd.DataFrame:
    """Return the cross-frame scatter surface used by the Intelligence tab."""
    state_filter_clause = ""
    state_filter_values: list[Any] = []
    if state_filter:
        placeholders = ", ".join("?" for _ in state_filter)
        state_filter_clause = f"WHERE dg.state_fips IN ({placeholders})"
        state_filter_values.extend(state_filter)

    connection = get_connection()
    try:
        intelligence_df = connection.execute(
            f"""
            WITH character AS (
              SELECT cbsa_code, cbsa_name, character_cluster
              FROM (
                SELECT {_character_select_fields()}
                FROM {_intelligence_relation('intelligence_character')}
              )
            ),
            livability AS (
              SELECT cbsa_code, livability_percentile_rank
              FROM (
                SELECT {_livability_select_fields()}
                FROM {_intelligence_relation('intelligence_livability')}
              )
            ),
            opportunity AS (
              SELECT cbsa_code, opportunity_percentile_rank
              FROM (
                SELECT {_opportunity_select_fields()}
                FROM {_intelligence_relation('intelligence_opportunity')}
              )
            ),
            cross_frame AS (
              SELECT
                cbsa_code,
                combined_cluster,
                cross_frame_divergence_flag,
                top_gmm_cluster,
                top_gmm_probability,
                second_gmm_cluster,
                second_gmm_probability
              FROM (
                SELECT {_cross_frame_select_fields()}
                FROM {_intelligence_relation('intelligence_cross_frame')}
              )
            )
            SELECT
              c.cbsa_code,
              c.cbsa_name,
              c.character_cluster,
              l.livability_percentile_rank,
              o.opportunity_percentile_rank,
              x.combined_cluster,
              x.cross_frame_divergence_flag,
              x.top_gmm_cluster,
              x.top_gmm_probability,
              x.second_gmm_cluster,
              x.second_gmm_probability,
              dg.state_fips,
              dg.state_name,
              dg.division_name
            FROM character c
            LEFT JOIN livability l USING (cbsa_code)
            LEFT JOIN opportunity o USING (cbsa_code)
            LEFT JOIN cross_frame x USING (cbsa_code)
            LEFT JOIN gold.dim_geo dg
              ON dg.geo_level = 'cbsa'
             AND dg.geo_id = c.cbsa_code
            {state_filter_clause}
            ORDER BY c.cbsa_name
            """,
            state_filter_values,
        ).fetchdf()
    finally:
        connection.close()
    return _fill_primary_state_context(
        intelligence_df,
        geo_name_col="cbsa_name",
        state_name_col="state_name",
    )


@st.cache_data(ttl=3600)
def query_intelligence_membership_table(state_filter: tuple[str, ...] = ()) -> pd.DataFrame:
    """Return the cluster membership table used by the internal Intelligence tab."""
    intelligence_df = query_intelligence_scatter(state_filter)
    if intelligence_df.empty:
        return intelligence_df

    ordered_columns = [
        "cbsa_code",
        "cbsa_name",
        "state_name",
        "division_name",
        "character_cluster",
        "combined_cluster",
        "livability_percentile_rank",
        "opportunity_percentile_rank",
        "top_gmm_probability",
        "second_gmm_probability",
        "cross_frame_divergence_flag",
    ]
    available_columns = [column for column in ordered_columns if column in intelligence_df.columns]
    return intelligence_df[available_columns].sort_values("cbsa_name").reset_index(drop=True)
