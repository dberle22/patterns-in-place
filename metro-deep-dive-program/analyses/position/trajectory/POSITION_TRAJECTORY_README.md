# Position Trajectory Analysis

This analysis is the thin exploratory consumer of the Time-Series / Trajectory
engine.

Its first job is to review the materialized 50-metric direct recurring panel for any selected metro
without rebuilding trend, momentum, salience, label, or turn-signal logic.

## What It Reads

- `mart_intelligence.intelligence_trajectory_series`
- `mart_intelligence.intelligence_trajectory_metric`
- `mart_intelligence.intelligence_trajectory_frame`
- `mart_intelligence.intelligence_trajectory_turn_signals`

DuckDB is canonical. Engine review exports are QA artifacts, not analysis
inputs.

## Planned Surfaces

- `POSITION_TRAJECTORY_NOTEBOOK.py`
  Marimo notebook for interactive market, frame, window, metric, and threshold
  exploration.
- `trajectory.py`
  Separate headless runner for stable query checks and CBSA-specific HTML QA
  outputs.
- `queries/`
  Thin SQL views for run inventory, selected-market frame and metric evidence,
  annual paths, national frame context, and turn signals.

See [POSITION_TRAJECTORY_SPEC.md](POSITION_TRAJECTORY_SPEC.md) for the SQL
plan, visuals, notebook flow, guardrails, and build checklist.

## Current Boundary

The current panel covers 50 direct recurring KPIs, 396 CBSAs, and a common
2023 end vintage. It is ready for method and interpretation review, but its
frame labels are not yet publication-ready until the contract review is
complete. Derived-change candidates remain future engine-review work.
