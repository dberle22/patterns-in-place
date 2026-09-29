#!/usr/bin/env python3
"""Build the Metro & Micro Panel public release from a private Foundations DuckDB.

This is deliberately one small, dependency-light script. It reads the frozen YAML contract,
extracts only its declared fields, validates the candidate before creating an output directory,
and writes the public artifacts. The private database path is an input only; it is never written
to a release artifact.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import yaml


# These sources and measures are intentionally outside v2026.1. Checking both the YAML contract
# and its lineage rows means a future edit cannot quietly broaden the public release.
BANNED_PUBLIC_DEPENDENCIES = re.compile(
    r"zillow|zhvi|zori|qcew|bfs|cbp|chas|permit|vacancy|occupancy", re.IGNORECASE
)


def quote_identifier(name: str) -> str:
    """Quote a DuckDB identifier; field names come from our reviewed local YAML contract."""

    return f'"{name.replace(chr(34), chr(34) * 2)}"'


def quote_table(name: str) -> str:
    """Quote a required schema-qualified table name without accepting arbitrary SQL fragments."""

    parts = name.split(".")
    if len(parts) != 2:
        raise ValueError(f"Expected a schema-qualified table name, got {name!r}.")
    return ".".join(quote_identifier(part) for part in parts)


def read_contract(config_path: Path) -> dict[str, Any]:
    """Load the single public allowlist that controls extraction and validation."""

    with config_path.open() as handle:
        contract = yaml.safe_load(handle)
    if not isinstance(contract, dict) or "release" not in contract or "tables" not in contract:
        raise ValueError("Release config must contain `release` and `tables`.")
    return contract


def table_fields(connection: duckdb.DuckDBPyConnection, table_name: str) -> set[str]:
    """Inspect source fields before querying, so a Foundations schema change fails clearly."""

    return {row[0] for row in connection.execute(f"DESCRIBE {quote_table(table_name)}").fetchall()}


def require_table_fields(
    connection: duckdb.DuckDBPyConnection, table_name: str, required_fields: list[str]
) -> None:
    missing = sorted(set(required_fields) - table_fields(connection, table_name))
    if missing:
        raise ValueError(f"{table_name} is missing required fields: {', '.join(missing)}")


def sql_cast(source: str, public_name: str, contract_type: str) -> str:
    """Make public Parquet and DuckDB types deterministic instead of inheriting private types."""

    valid_types = {"VARCHAR", "INTEGER", "DOUBLE", "BOOLEAN"}
    if contract_type not in valid_types:
        raise ValueError(f"Unsupported public contract type: {contract_type}")
    return f"CAST({quote_identifier(source)} AS {contract_type}) AS {quote_identifier(public_name)}"


def query_arrow_table(connection: duckdb.DuckDBPyConnection, query: str) -> pa.Table:
    """Return an Arrow table across the DuckDB versions used in this monorepo.

    Newer DuckDB documentation calls this ``to_arrow_table``, but the installed release still
    exposes only ``fetch_arrow_table`` while warning about that method's future deprecation.
    Prefer the new method when it exists and keep the older release usable until Foundations
    upgrades DuckDB; both return the same in-memory Arrow table used for public artifacts.
    """

    result = connection.execute(query)
    if hasattr(result, "to_arrow_table"):
        return result.to_arrow_table()
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=r"fetch_arrow_table\(\) is deprecated")
        return result.fetch_arrow_table()


def extract_crosswalk(
    connection: duckdb.DuckDBPyConnection, table_contract: dict[str, Any]
) -> pa.Table:
    """Build the public crosswalk from approved geography tables.

    County/state fields stay with their governed source tables. The primary-state fields reuse
    the deterministic title-order rule already materialized in gold.dim_geo, avoiding a second,
    slightly different implementation of multi-state CBSA logic in the release project.
    """

    require_table_fields(
        connection,
        "silver.xwalk_cbsa_county",
        [
            "county_geoid", "county_name", "state_fips", "state_name", "cbsa_code",
            "cbsa_name", "cbsa_type", "county_flag", "vintage",
        ],
    )
    require_table_fields(connection, "silver.xwalk_county_state", ["county_geoid", "state_abbr"])
    require_table_fields(connection, "gold.dim_geo", ["geo_level", "geo_id", "state_abbr", "state_fips"])

    # This SQL is intentionally explicit rather than generated from the YAML: two convenience
    # fields need governed joins and a documented type mapping, not a direct source-column alias.
    query = """
        SELECT
          CAST(x.county_geoid AS VARCHAR) AS county_geoid,
          x.county_name,
          LPAD(CAST(x.state_fips AS VARCHAR), 2, '0') AS state_fips,
          s.state_abbr,
          x.state_name,
          LPAD(CAST(x.cbsa_code AS VARCHAR), 5, '0') AS cbsa_code,
          x.cbsa_name,
          x.cbsa_type,
          CASE
            WHEN x.cbsa_type = 'Metropolitan Statistical Area' THEN 'metro'
            WHEN x.cbsa_type = 'Micropolitan Statistical Area' THEN 'micro'
            ELSE NULL
          END AS cbsa_type_short,
          x.county_flag AS county_role,
          d.state_abbr AS primary_state_abbr,
          LPAD(CAST(d.state_fips AS VARCHAR), 2, '0') AS primary_state_fips,
          CAST(x.vintage AS INTEGER) AS crosswalk_vintage
        FROM silver.xwalk_cbsa_county x
        LEFT JOIN silver.xwalk_county_state s ON x.county_geoid = s.county_geoid
        LEFT JOIN gold.dim_geo d
          ON LOWER(d.geo_level) = 'cbsa'
         AND LPAD(CAST(d.geo_id AS VARCHAR), 5, '0') = LPAD(CAST(x.cbsa_code AS VARCHAR), 5, '0')
    """
    source_table = query_arrow_table(connection, query)
    expected = [column["name"] for column in table_contract["columns"]]
    return source_table.select(expected)


def extract_fact_table(
    connection: duckdb.DuckDBPyConnection, table_contract: dict[str, Any]
) -> pa.Table:
    """Extract exactly the allowed fact-table columns and rename them at the public boundary."""

    source_columns = [column["source"] for column in table_contract["columns"]]
    require_table_fields(connection, table_contract["source_table"], source_columns)
    selected_columns = ", ".join(
        sql_cast(column["source"], column["name"], column["type"])
        for column in table_contract["columns"]
    )
    query = (
        f"SELECT {selected_columns} FROM {quote_table(table_contract['source_table'])} "
        f"WHERE {table_contract['row_filter']}"
    )
    return query_arrow_table(connection, query)


def extract_release_tables(
    connection: duckdb.DuckDBPyConnection, contract: dict[str, Any]
) -> dict[str, pa.Table]:
    """Materialize all three candidate tables in memory before any public artifact is created."""

    tables: dict[str, pa.Table] = {}
    for name, table_contract in contract["tables"].items():
        if name == "cbsa_county_crosswalk":
            tables[name] = extract_crosswalk(connection, table_contract)
        else:
            tables[name] = extract_fact_table(connection, table_contract)
    return tables


def expected_cbsa_count(contract: dict[str, Any]) -> int:
    """Read the declared universe from human-readable config instead of duplicating 935 in code."""

    match = re.search(r"\d+", contract["release"]["geographic_universe"])
    if not match:
        raise ValueError("Unable to determine expected CBSA count from release config.")
    return int(match.group())


def column_values(table: pa.Table, column_name: str) -> list[Any]:
    """Use Python values for small release-level checks; no mutable private DB tables are needed."""

    return table.column(column_name).to_pylist()


def read_lineage(lineage_path: Path) -> list[dict[str, str]]:
    with lineage_path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def validate_release_tables(
    tables: dict[str, pa.Table], contract: dict[str, Any], config_path: Path, lineage_path: Path
) -> None:
    """Fail closed on shape, geography, completeness, lineage, or scope-boundary violations."""

    errors: list[str] = []
    if BANNED_PUBLIC_DEPENDENCIES.search(config_path.read_text()):
        errors.append("Configured allowlist references a held-back source or metric.")
    lineage = read_lineage(lineage_path)

    for name, table_contract in contract["tables"].items():
        table = tables[name]
        expected_columns = [column["name"] for column in table_contract["columns"]]
        if table.num_rows == 0:
            errors.append(f"{name} has no rows.")
        if table.column_names != expected_columns:
            errors.append(f"{name} columns do not exactly match the configured order.")
            continue

        key_columns = table_contract["primary_key"]
        keys = list(zip(*(column_values(table, key) for key in key_columns)))
        duplicate_count = len(keys) - len(set(keys))
        if duplicate_count:
            errors.append(f"{name} has {duplicate_count} duplicate primary keys.")

        for column in table_contract["columns"]:
            if "max_null_rate" not in column:
                continue
            null_rate = table.column(column["name"]).null_count / max(table.num_rows, 1)
            if null_rate > column["max_null_rate"]:
                errors.append(
                    f"{table_contract['source_table']}.{column['name']} null rate "
                    f"{null_rate:.4f} exceeds {column['max_null_rate']:.4f}"
                )

        configured_sources = {column["source"] for column in table_contract["columns"]}
        relevant_lineage = [
            row for row in lineage
            if row["public_table"] == name
            and (row["public_column"] in expected_columns or row["public_column"] in configured_sources)
        ]
        for column in table_contract["columns"]:
            found = any(
                row["public_column"] in {column["name"], column["source"]}
                or row["private_source"] == column["source"]
                for row in relevant_lineage
            )
            if not found:
                errors.append(f"{name} has no lineage row for: {column['name']}")
        if any(BANNED_PUBLIC_DEPENDENCIES.search(row["private_source"] or "") for row in relevant_lineage):
            errors.append(f"{name} lineage references a held-back source.")

    crosswalk_cbsas = len(set(column_values(tables["cbsa_county_crosswalk"], "cbsa_code")))
    if crosswalk_cbsas != expected_cbsa_count(contract):
        errors.append(f"Crosswalk contains {crosswalk_cbsas} CBSAs; expected {expected_cbsa_count(contract)}.")

    for name in ("economics_industry_wide", "affordability_wide"):
        geo_levels = column_values(tables[name], "geo_level")
        years = column_values(tables[name], "year")
        if any(level != "cbsa" for level in geo_levels):
            errors.append(f"{name} contains non-CBSA geography rows.")
        if any(year is None or year < 2000 or year > 2100 for year in years):
            errors.append(f"{name} contains invalid years.")

    if errors:
        raise ValueError("\n".join(errors))


def sha256(path: Path) -> str:
    """Hash the bytes users download, allowing the public manifest to verify each artifact."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def lineage_for_column(
    lineage: list[dict[str, str]], table_name: str, public_name: str, source_name: str
) -> dict[str, str | None]:
    """Support public renames while preserving the private-source vintage in the manifest."""

    for row in lineage:
        if row["public_table"] == table_name and (
            row["public_column"] == public_name
            or row["public_column"] == source_name
            or row["private_source"] == source_name
        ):
            return {
                "source_vintage": row.get("source_vintage") or None,
                "observed_coverage_at_contract_review": row.get("observed_coverage") or None,
            }
    return {"source_vintage": None, "observed_coverage_at_contract_review": None}


def release_shape(tables: dict[str, pa.Table], contract: dict[str, Any]) -> dict[str, Any]:
    """Create the portion of a manifest needed for pre-write prior-release comparisons."""

    return {
        "tables": {
            name: {
                "row_count": table.num_rows,
                "columns": [{"name": column["name"]} for column in contract["tables"][name]["columns"]],
            }
            for name, table in tables.items()
        }
    }


def validate_prior_manifest(
    shape: dict[str, Any], prior_manifest_path: Path | None, allow_coverage_change: bool
) -> None:
    """Require deliberate approval for a refresh that changes schema or row counts."""

    if prior_manifest_path is None:
        return
    with prior_manifest_path.open() as handle:
        prior = json.load(handle)
    changes: list[str] = []
    for name, table_shape in shape["tables"].items():
        old = prior.get("tables", {}).get(name)
        if old is None:
            changes.append(f"New table: {name}")
            continue
        old_columns = [column["name"] for column in old["columns"]]
        new_columns = [column["name"] for column in table_shape["columns"]]
        if old_columns != new_columns:
            changes.append(f"Schema change: {name}")
        if old["row_count"] != table_shape["row_count"]:
            changes.append(f"Row-count change: {name}")
    if changes and not allow_coverage_change:
        raise ValueError(
            "Prior-release differences require --allow-coverage-change:\n" + "\n".join(changes)
        )


def build_manifest(
    tables: dict[str, pa.Table], contract: dict[str, Any], lineage_path: Path, artifact_paths: dict[str, Path]
) -> dict[str, Any]:
    """Record what was released without leaking a local database path or internal credentials."""

    lineage = read_lineage(lineage_path)
    manifest_tables: dict[str, Any] = {}
    for name, table in tables.items():
        table_contract = contract["tables"][name]
        columns = []
        for column in table_contract["columns"]:
            columns.append(
                {
                    "name": column["name"],
                    "type": column["type"],
                    "private_source_column": column["source"],
                    **lineage_for_column(lineage, name, column["name"], column["source"]),
                }
            )
        parquet_path = artifact_paths[f"{name}_parquet"]
        manifest_tables[name] = {
            "name": name,
            "source_table": table_contract["source_table"],
            "row_count": table.num_rows,
            "primary_key": table_contract["primary_key"],
            "columns": columns,
            "parquet": {"file": parquet_path.name, "sha256": sha256(parquet_path)},
        }
    return {
        "title": contract["release"]["title"],
        "version": contract["release"]["version"],
        "contract_status": contract["release"]["status"],
        "geographic_universe": contract["release"]["geographic_universe"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_database": "private Foundations DuckDB (path intentionally omitted)",
        "tables": manifest_tables,
        "bundled_duckdb": {"file": artifact_paths["duckdb"].name, "sha256": sha256(artifact_paths["duckdb"])},
    }


def write_coverage_report(tables: dict[str, pa.Table], contract: dict[str, Any], path: Path) -> None:
    """Write the human review artifact; it complements hard validation rather than replacing it."""

    lines = ["# Release coverage report", "", f"Release: `{contract['release']['version']}`", ""]
    for name, table in tables.items():
        lines.extend([f"## {name}", "", f"Rows: {table.num_rows}", "", "| Column | Null rate |", "| --- | ---: |"])
        lines.extend(
            f"| `{column}` | {table.column(column).null_count / max(table.num_rows, 1):.2%} |"
            for column in table.column_names
        )
        lines.append("")
        if "year" in table.column_names:
            years = column_values(table, "year")
            geo_ids = column_values(table, "geo_id")
            annual = {}
            for year, geo_id in zip(years, geo_ids):
                annual.setdefault(year, set()).add(geo_id)
            lines.extend(["| Year | CBSAs |", "| ---: | ---: |"])
            lines.extend(f"| {year} | {len(annual[year])} |" for year in sorted(annual))
            lines.append("")
            # Table-row coverage alone can hide sparse optional fields such as BEA GDP or HUD
            # FMR. Show every numeric field's annual non-null count so reviewers can distinguish
            # a complete ACS panel from a source-specific coverage gap.
            annual_numeric_columns = [
                field.name for field in table.schema
                if pa.types.is_integer(field.type) or pa.types.is_floating(field.type)
            ]
            if annual_numeric_columns:
                lines.extend(["| Year | " + " | ".join(f"`{column}`" for column in annual_numeric_columns) + " |"])
                lines.extend(["| ---: | " + " | ".join("---:" for _ in annual_numeric_columns) + " |"])
                # Convert each Arrow column once. The earlier implementation converted an entire
                # column again for every year and measure, which made a small coverage report
                # disproportionately slow during release builds.
                numeric_values = {
                    column: column_values(table, column) for column in annual_numeric_columns
                }
                annual_counts = {
                    year: {column: 0 for column in annual_numeric_columns} for year in annual
                }
                for index, year in enumerate(years):
                    for column, values in numeric_values.items():
                        if values[index] is not None:
                            annual_counts[year][column] += 1
                for year in sorted(annual):
                    counts = [annual_counts[year][column] for column in annual_numeric_columns]
                    lines.append(f"| {year} | " + " | ".join(str(count) for count in counts) + " |")
                lines.append("")
        numeric_columns = [
            field.name for field in table.schema
            if pa.types.is_integer(field.type) or pa.types.is_floating(field.type)
        ]
        if numeric_columns:
            lines.extend(["| Numeric column | Non-null | Min | Max |", "| --- | ---: | ---: | ---: |"])
            for column in numeric_columns:
                values = [value for value in column_values(table, column) if value is not None]
                if values:
                    lines.append(f"| `{column}` | {len(values)} | {min(values):.6g} | {max(values):.6g} |")
            lines.append("")
    path.write_text("\n".join(lines))


def write_artifacts(
    tables: dict[str, pa.Table], contract: dict[str, Any], lineage_path: Path, output_dir: Path,
    prior_manifest_path: Path | None = None, allow_coverage_change: bool = False,
) -> dict[str, Any]:
    """Write immutable-style release artifacts only after all non-I/O checks have passed."""

    if output_dir.exists():
        raise ValueError(f"Output directory already exists: {output_dir}")
    validate_prior_manifest(release_shape(tables, contract), prior_manifest_path, allow_coverage_change)
    output_dir.mkdir(parents=True)
    artifact_paths: dict[str, Path] = {}

    for name, table in tables.items():
        parquet_path = output_dir / f"{name}.parquet"
        # ZSTD keeps remote-download costs reasonable while DuckDB and Arrow read it directly.
        pq.write_table(table, parquet_path, compression="zstd")
        artifact_paths[f"{name}_parquet"] = parquet_path

    duckdb_path = output_dir / "pip-metro-micro-panel.duckdb"
    with duckdb.connect(str(duckdb_path)) as bundled_connection:
        for name, table in tables.items():
            bundled_connection.register("release_frame", table)
            bundled_connection.execute(f"CREATE TABLE {quote_identifier(name)} AS SELECT * FROM release_frame")
            bundled_connection.unregister("release_frame")
        # `_manifest` supports people opening only the bundled database; the adjacent JSON has
        # complete hashes and column provenance, which cannot be embedded without a hash cycle.
        bundled_connection.execute(
            "CREATE TABLE _manifest AS SELECT * FROM (VALUES "
            + ", ".join(
                f"('{contract['release']['version']}', '{name}', {table.num_rows})"
                for name, table in tables.items()
            )
            + ") AS manifest(release_version, table_name, row_count)"
        )
    artifact_paths["duckdb"] = duckdb_path

    manifest = build_manifest(tables, contract, lineage_path, artifact_paths)
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    write_coverage_report(tables, contract, output_dir / "coverage_report.md")
    return manifest


def build_release(
    db_path: Path, config_path: Path, lineage_path: Path, output_dir: Path, version: str,
    prior_manifest_path: Path | None, allow_coverage_change: bool,
) -> dict[str, Any]:
    """Orchestrate the release in the only order that can safely expose public artifacts."""

    contract = read_contract(config_path)
    if version != contract["release"]["version"]:
        raise ValueError(f"Requested version {version} does not match config version {contract['release']['version']}.")
    # An unset shell variable expands to an empty string, and Path("") becomes `.`. Calling
    # that out directly is much more useful than the generic "does not exist" message.
    if db_path == Path("."):
        raise ValueError(
            "--db was empty. Supply the Foundations DuckDB path directly or set "
            "PIP_FOUNDATIONS_DUCKDB before running this command."
        )
    if not db_path.is_file():
        raise ValueError(f"Input DuckDB does not exist: {db_path}")

    # Read-only access ensures this downstream release task cannot alter Foundation source data.
    with duckdb.connect(str(db_path), read_only=True) as connection:
        tables = extract_release_tables(connection, contract)
    validate_release_tables(tables, contract, config_path, lineage_path)
    return write_artifacts(
        tables, contract, lineage_path, output_dir, prior_manifest_path, allow_coverage_change
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, type=Path, help="Private Foundations DuckDB path.")
    parser.add_argument("--output", required=True, type=Path, help="New output directory for this release.")
    parser.add_argument("--version", required=True, help="Must match config/tables.yml exactly.")
    parser.add_argument("--prior-manifest", type=Path, help="Optional preceding release manifest for diff checks.")
    parser.add_argument("--allow-coverage-change", action="store_true", help="Approve a prior-release schema or row-count change.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_dir = Path(__file__).resolve().parents[1]
    build_release(
        db_path=args.db,
        config_path=project_dir / "config" / "tables.yml",
        lineage_path=project_dir / "audit" / "public_column_lineage.csv",
        output_dir=args.output,
        version=args.version,
        prior_manifest_path=args.prior_manifest,
        allow_coverage_change=args.allow_coverage_change,
    )
    print(f"Release artifacts written to {args.output}")


if __name__ == "__main__":
    main()
