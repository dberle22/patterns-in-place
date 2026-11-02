"""Append one source run to a DuckDB table without deleting or replacing rows."""

from __future__ import annotations

import re

import duckdb


IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")


def append_run(con: duckdb.DuckDBPyConnection, schema: str, table: str, select: str, source_run_id: str) -> int:
    """Create or append in one transaction, refusing a run the table already holds.

    `select` must supply a `source_run_id` column. A failure leaves the table
    as it was, so a publish can be retried; a repeat of a published run cannot
    double its rows.
    """

    if not IDENTIFIER.fullmatch(schema) or not IDENTIFIER.fullmatch(table):
        raise ValueError(f"Unsafe table name: {schema}.{table}.")
    target = f"{schema}.{table}"
    incoming = {row[0] for row in con.execute(f"DESCRIBE {select}").fetchall()}
    if "source_run_id" not in incoming:
        raise ValueError(f"{target}: the published rows must carry source_run_id.")
    expected = con.execute(f"SELECT count(*) FROM ({select}) WHERE source_run_id = ?", [source_run_id]).fetchone()[0]
    total = con.execute(f"SELECT count(*) FROM ({select})").fetchone()[0]
    if not total or expected != total:
        raise RuntimeError(f"{target}: {expected:,} of {total:,} rows belong to run {source_run_id}.")

    exists = con.execute(
        "SELECT count(*) FROM information_schema.tables WHERE table_schema = ? AND table_name = ?", [schema, table]
    ).fetchone()[0]
    if exists:
        existing = con.execute(f"SELECT count(*) FROM {target} WHERE source_run_id = ?", [source_run_id]).fetchone()[0]
        if existing:
            raise RuntimeError(f"Refusing to append: {target} already has {existing:,} rows for run {source_run_id}.")
        # BY NAME fills an absent column with null, so require an exact match.
        columns = {row[0] for row in con.execute(f"DESCRIBE {target}").fetchall()}
        if columns != incoming:
            raise RuntimeError(f"{target} columns differ from the run: {sorted(columns ^ incoming)}.")

    con.execute("BEGIN TRANSACTION")
    try:
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        if exists:
            con.execute(f"INSERT INTO {target} BY NAME {select}")
        else:
            con.execute(f"CREATE TABLE {target} AS {select}")
        actual = con.execute(f"SELECT count(*) FROM {target} WHERE source_run_id = ?", [source_run_id]).fetchone()[0]
        if actual != total:
            raise RuntimeError(f"{target} has {actual:,} rows for run {source_run_id}; expected {total:,}.")
        con.execute("COMMIT")
    except Exception:
        con.execute("ROLLBACK")
        raise
    return actual
