#!/usr/bin/env python3
"""Build one validated, incremental tract OD commute-shed artifact in DuckDB."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import tempfile

import duckdb


REPO_ROOT = Path(__file__).resolve().parents[3]
LODES_ROOT = "https://lehd.ces.census.gov/data/lodes/LODES8"
YEAR = 2023
RELEASE = "8.4"
TRANSFORMATION_VERSION = "lodes_od_tract_metro_v1"
UNAVAILABLE_STATES = {"ak", "mi"}
STATE_ABBRS = ("al,ak,az,ar,ca,co,ct,de,fl,ga,hi,id,il,in,ia,ks,ky,la,me,md,ma,mi,mn,ms,mo,mt,ne,nv,nh,nj,nm,ny,nc,nd,oh,ok,or,pa,ri,sc,sd,tn,tx,ut,vt,va,wa,wv,wi,wy,dc").split(",")


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def download_asset(url: str, destination: Path) -> None:
    """Use the system curl trust store, matching Foundations' R LODES loaders."""

    subprocess.run(["/usr/bin/curl", "-fsSL", url, "-o", str(destination)], check=True)
    if not destination.exists() or destination.stat().st_size == 0:
        raise RuntimeError(f"LODES download produced no file: {url}")


def database_path(argument: str | None) -> str:
    if argument:
        return argument
    env_path = os.getenv("DB_PATH")
    if env_path:
        return env_path
    renviron = REPO_ROOT / ".Renviron"
    if renviron.exists():
        for line in renviron.read_text().splitlines():
            if line.startswith("DB_PATH="):
                return line.split("=", 1)[1]
    raise RuntimeError("Set DB_PATH or pass --db-path.")


def create_tables(con: duckdb.DuckDBPyConnection) -> None:
    """Create durable scoped outputs once; each requested scope is state-replaced."""

    con.execute("CREATE SCHEMA IF NOT EXISTS silver")
    con.execute("""
        CREATE TABLE IF NOT EXISTS silver.lehd_lodes_od_tract_metro (
          cbsa_code VARCHAR, relationship_scope VARCHAR, home_tract_geoid VARCHAR,
          home_tract_status VARCHAR, work_tract_geoid VARCHAR, work_tract_status VARCHAR,
          year INTEGER, source_state VARCHAR, source_part VARCHAR, job_type VARCHAR,
          segment VARCHAR, jobs DOUBLE, source_block_row_count BIGINT, source_file VARCHAR,
          source_createdate VARCHAR, release_format_version VARCHAR, transformation_version VARCHAR
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS silver.lehd_lodes_od_tract_metro_coverage (
          cbsa_code VARCHAR, relationship_scope VARCHAR, source_state VARCHAR, year INTEGER,
          source_part VARCHAR, job_type VARCHAR, segment VARCHAR, source_file VARCHAR,
          source_row_count BIGINT, source_jobs_total DOUBLE, selected_row_count BIGINT,
          selected_jobs_total DOUBLE, tract_pair_row_count BIGINT, reconciliation_passed BOOLEAN,
          coverage_status VARCHAR, release_format_version VARCHAR, transformation_version VARCHAR
        )
    """)


def metro_workplace_states(con: duckdb.DuckDBPyConnection, cbsa_code: str) -> list[str]:
    """Resolve every workplace state represented by the CBSA's governed tracts."""

    fips = con.execute("SELECT DISTINCT state_fips FROM silver.xwalk_cbsa_county WHERE cbsa_code = ?", [cbsa_code]).fetchall()
    fips_map = {"01":"al","02":"ak","04":"az","05":"ar","06":"ca","08":"co","09":"ct","10":"de","11":"dc","12":"fl","13":"ga","15":"hi","16":"id","17":"il","18":"in","19":"ia","20":"ks","21":"ky","22":"la","23":"me","24":"md","25":"ma","26":"mi","27":"mn","28":"ms","29":"mo","30":"mt","31":"ne","32":"nv","33":"nh","34":"nj","35":"nm","36":"ny","37":"nc","38":"nd","39":"oh","40":"ok","41":"or","42":"pa","44":"ri","45":"sc","46":"sd","47":"tn","48":"tx","49":"ut","50":"vt","51":"va","53":"wa","54":"wv","55":"wi","56":"wy"}
    states = [fips_map.get(row[0]) for row in fips]
    if not states or any(state is None for state in states):
        raise RuntimeError(f"Could not resolve workplace states for CBSA {cbsa_code}.")
    return sorted(set(states))


def source_assets(workplace_states: list[str], scope: str, job_types: list[str]) -> list[tuple[str, str, str]]:
    """Select files precisely; full resident/outbound coverage needs national aux."""

    assets: list[tuple[str, str, str]] = []
    if scope == "workplace_side":
        for state in workplace_states:
            for job_type in job_types:
                assets.extend((state, part, job_type) for part in ("main", "aux"))
    else:
        for state in workplace_states:
            for job_type in job_types:
                assets.append((state, "main", job_type))
        for state in STATE_ABBRS:
            for job_type in job_types:
                assets.append((state, "aux", job_type))
    return list(dict.fromkeys(assets))


def build(args: argparse.Namespace) -> None:
    con = duckdb.connect(database_path(args.db_path))
    try:
        create_tables(con)
        workplace_states = metro_workplace_states(con, args.cbsa_code)
        assets = source_assets(workplace_states, args.scope, args.job_types)
        # The scope table makes the selected CBSA a reusable relationship set.
        con.execute("CREATE OR REPLACE TEMP TABLE selected_tracts AS SELECT DISTINCT b.tract_geoid FROM silver.block_registry b JOIN silver.xwalk_cbsa_county c ON b.county_geoid = c.county_geoid WHERE c.cbsa_code = ?", [args.cbsa_code])
        con.execute("DELETE FROM silver.lehd_lodes_od_tract_metro WHERE cbsa_code = ? AND relationship_scope = ? AND year = ?", [args.cbsa_code, args.scope, YEAR])
        con.execute("DELETE FROM silver.lehd_lodes_od_tract_metro_coverage WHERE cbsa_code = ? AND relationship_scope = ? AND year = ?", [args.cbsa_code, args.scope, YEAR])
        for state, part, job_type in assets:
            filename = f"{state}_od_{part}_{job_type}_{YEAR}.csv.gz"
            if state in UNAVAILABLE_STATES:
                con.execute("INSERT INTO silver.lehd_lodes_od_tract_metro_coverage VALUES (?, ?, ?, ?, ?, ?, 'S000', ?, NULL, NULL, NULL, NULL, NULL, NULL, 'provider_unavailable_2023', ?, ?)", [args.cbsa_code, args.scope, state.upper(), YEAR, part, job_type, filename, RELEASE, TRANSFORMATION_VERSION])
                continue
            with tempfile.TemporaryDirectory(prefix="lodes_od_") as directory:
                local_path = Path(directory) / filename
                download_asset(f"{LODES_ROOT}/{state}/od/{filename}", local_path)
                source = sql_literal(str(local_path))
                mapped = f"""WITH source AS (SELECT * FROM read_csv_auto({source}, types={{'w_geocode':'VARCHAR','h_geocode':'VARCHAR','createdate':'VARCHAR'}})), mapped AS (SELECT source.*, h.tract_geoid AS home_tract, w.tract_geoid AS work_tract FROM source LEFT JOIN silver.block_registry h ON source.h_geocode=h.block_geoid LEFT JOIN silver.block_registry w ON source.w_geocode=w.block_geoid), selected AS (SELECT * FROM mapped WHERE {'work_tract IN (SELECT tract_geoid FROM selected_tracts)' if args.scope == 'workplace_side' else 'work_tract IN (SELECT tract_geoid FROM selected_tracts) OR home_tract IN (SELECT tract_geoid FROM selected_tracts)'})"""
                counts = con.execute(mapped + " SELECT (SELECT count(*) FROM mapped), (SELECT sum(S000) FROM mapped), (SELECT count(*) FROM selected), (SELECT sum(S000) FROM selected)").fetchone()
                aggregate = mapped + f""" SELECT {sql_literal(args.cbsa_code)} AS cbsa_code, {sql_literal(args.scope)} AS relationship_scope, coalesce(home_tract, 'unmapped_block') AS home_tract_geoid, CASE WHEN home_tract IS NULL THEN 'unmapped_block' ELSE 'matched' END AS home_tract_status, coalesce(work_tract, 'unmapped_block') AS work_tract_geoid, CASE WHEN work_tract IS NULL THEN 'unmapped_block' ELSE 'matched' END AS work_tract_status, {YEAR} AS year, {sql_literal(state.upper())} AS source_state, {sql_literal(part)} AS source_part, {sql_literal(job_type)} AS job_type, 'S000' AS segment, sum(S000) AS jobs, count(*) AS source_block_row_count, {sql_literal(filename)} AS source_file, min(createdate) AS source_createdate, {sql_literal(RELEASE)} AS release_format_version, {sql_literal(TRANSFORMATION_VERSION)} AS transformation_version FROM selected GROUP BY ALL"""
                pairs, jobs = con.execute("SELECT count(*), coalesce(sum(jobs), 0) FROM (" + aggregate + ")").fetchone()
                con.execute("INSERT INTO silver.lehd_lodes_od_tract_metro " + aggregate)
                if jobs != counts[3]:
                    raise RuntimeError(f"Selected tract aggregation did not reconcile for {filename}.")
                con.execute("INSERT INTO silver.lehd_lodes_od_tract_metro_coverage VALUES (?, ?, ?, ?, ?, ?, 'S000', ?, ?, ?, ?, ?, ?, ?, 'available_validated', ?, ?)", [args.cbsa_code, args.scope, state.upper(), YEAR, part, job_type, filename, counts[0], counts[1], counts[2], jobs, pairs, True, RELEASE, TRANSFORMATION_VERSION])
        con.execute("CHECKPOINT")
    finally:
        con.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cbsa-code", required=True, help="Five-digit OMB CBSA code.")
    parser.add_argument("--scope", choices=("workplace_side", "either_endpoint"), default="workplace_side")
    parser.add_argument("--job-types", default="JT00,JT02", help="Comma-separated LODES job types.")
    parser.add_argument("--db-path", help="DuckDB path; defaults to DB_PATH.")
    args = parser.parse_args()
    args.job_types = [item.strip().upper() for item in args.job_types.split(",") if item.strip()]
    if not args.job_types or any(item not in {"JT00", "JT02"} for item in args.job_types):
        parser.error("--job-types currently supports JT00 and JT02.")
    return args


if __name__ == "__main__":
    build(parse_args())
