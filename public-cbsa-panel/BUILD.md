# Release build

`scripts/build_release.py` is the complete private-monorepo release builder. It has no package
or helper-module layer: the command-line entry point and the documented build functions live in
the same file. Its only runtime dependencies are Python, DuckDB, PyArrow, and PyYAML.

## Inputs

- A private Foundations DuckDB supplied with `--db`.
- `config/tables.yml`, the frozen public allowlist and validation contract.
- `audit/public_column_lineage.csv`, the field-level provenance record.
- A new output directory supplied with `--output`.

The input database remains read-only throughout the build. Its local path is deliberately
omitted from `manifest.json`.

## What the script does

1. Reads the YAML contract and checks that the requested version matches it.
2. Reads the county-to-CBSA crosswalk from its governed Silver and Gold geography tables.
   It retains the established primary-state rule from `gold.dim_geo` rather than rebuilding that
   multi-state logic in the public project.
3. Reads each fact table with an explicit `SELECT` generated from the allowlist. It cannot export
   an undeclared Gold column.
4. Validates the in-memory candidate: ordered schema, keys, null thresholds, CBSA geography,
   935-CBSA crosswalk universe, lineage rows, and excluded-source boundary.
5. If a previous manifest is supplied, compares schemas and row counts before creating the output
   directory. A difference requires `--allow-coverage-change`.
6. Writes three ZSTD Parquet files, a bundled DuckDB containing the three tables and `_manifest`,
   `manifest.json` with hashes/provenance, and `coverage_report.md` for human review.

The inline comments in the script explain the business rule or safety reason for each
non-obvious block. The implementation uses DuckDB for source queries and the portable bundled
database, PyArrow for standard ZSTD Parquet, YAML for the human-reviewed contract, and Python's
standard library for argument parsing, hashing, manifests, and validation bookkeeping.

## Run

```sh
python3 public-cbsa-panel/scripts/build_release.py \
  --db foundations/etl/data/duckdb/patterns_in_place.duckdb \
  --output public-cbsa-panel/output/v2026.1 \
  --version v2026.1
```

Run this from the monorepo root. If you prefer an environment variable, export
`PIP_FOUNDATIONS_DUCKDB` in your shell first; the Python builder does not read R's `.Renviron`.

For a refresh, add `--prior-manifest <path>`. If the reviewed schema or row-count change is
intentional, add `--allow-coverage-change` as an explicit acknowledgement.

## Test

```sh
python3 -m unittest public-cbsa-panel/tests/test_release_validation.py
```
