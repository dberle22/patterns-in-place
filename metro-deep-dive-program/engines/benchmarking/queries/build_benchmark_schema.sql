-- Build-order reference for the first-pass benchmarking schema.
-- The executable runner is ../build_benchmark_schema.py, which executes these
-- files in the same order against the configured DuckDB path.

CREATE SCHEMA IF NOT EXISTS mart_benchmarking;
