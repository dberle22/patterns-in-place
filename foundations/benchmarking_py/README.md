# Benchmarking Python Package

Shared Python package for the Metro Deep Dive benchmarking engine.

Purpose:

- centralize benchmark lookup and calculation logic
- keep benchmark behavior consistent across notebooks and apps
- read from `mart_benchmarking` rather than encouraging bespoke query logic

Current scope:

- DuckDB connection helpers
- comparison-set lookup
- target metric lookup
- on-demand benchmark summaries
- on-demand member-level comparison tables
