# Time-Series / Trajectory Engine Contract

Status: 50-metric direct recurring panel implemented; interactive review and
contract freeze remain. Method version: `trajectory_pilot_v1`.

## Canonical outputs

The engine is the sole writer for these DuckDB tables in `mart_intelligence`:

| Table | Key | Contract |
|---|---|---|
| `intelligence_trajectory_series` | `method_version`, `cbsa_code`, `metric_id`, `year` | Prepared annual values, declared transformations, national percentiles, and availability status |
| `intelligence_trajectory_metric` | `method_version`, `cbsa_code`, `metric_id`, `window_name`, `end_year` | Endpoints, robust trend evidence, aligned relative momentum, metric salience, and coverage |
| `intelligence_trajectory_frame` | `method_version`, `cbsa_code`, `frame_id`, `window_name`, `end_year` | Topic-balanced frame evidence, position, movement, salience tiers, labels, and coverage |
| `intelligence_trajectory_turn_signals` | `method_version`, `cbsa_code`, `frame_id`, `method_window_pair`, `end_year` | Compatible-window comparison, supporting KPI panel, and turn status |

The tables are replaced together in a transaction. `outputs/review/` contains
Parquet snapshots and the threshold CSV copied from the completed mart; those
files are human-review artifacts, not downstream inputs.

## Scope and eligibility

- Universe: 396 CBSAs with 2024 population of at least 100,000, excluding
  Puerto Rico. The population year establishes stable membership only.
- End vintage: 2023. The five-year window is 2018–2023; the short-run
  Opportunity window is 2022–2023.
- A metric/window requires exact start and end observations and at least four
  annual observations for the five-year Theil-Sen trend. The one-year window
  is stored as a two-point change.
- Missing values remain missing. The engine does not impute observations or
  substitute one metric for another.
- A frame is eligible with at least two observed topics. Its topic and metric
  counts are exposed so consumers can judge partial coverage.
- The registry scores direct recurring series only. The eight derived-change
  candidates are documented in the build plan and remain out of this contract
  until their underlying annual-level alternatives are reviewed.

## Method fields

Metric output retains raw endpoint change, national start/end percentiles,
percentile-point change, transformed slope, polarity-aligned slope, momentum
percentile, and signed relative momentum separately. A label must never be
used as a substitute for these fields.

For Livability and Opportunity, polarity aligns metric movement to a
better/worse direction before relative momentum is aggregated. Character is
non-normative: its frame score is the topic-balanced magnitude of relative
movement, and it receives only a change-salience label.

Frame salience is the percentile rank of absolute frame momentum among eligible
metros within the same frame, window, and end year. `signal_p80`, `signal_p90`,
and `signal_p95` are nested flags. The production label gate is p80.

## Consumer rules

`analyses/position/trajectory/` and other consumers may filter or explain this
mart, but may not recompute transformations, trends, rankings, or labels.
Candidate Scan remains a later editorial consumer, not an engine output.
