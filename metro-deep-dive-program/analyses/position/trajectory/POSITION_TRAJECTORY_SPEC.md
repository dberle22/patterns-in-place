# Position Trajectory Spec

**Status:** Query surfaces and notebook implemented; interactive review and headless QA pending

**Default market:** Richmond, VA (`40060`)

**Primary surface:** `POSITION_TRAJECTORY_NOTEBOOK.py`

**Headless QA:** `trajectory.py`

**Initial method:** `trajectory_pilot_v1`

## Goal

Build a thin Position notebook that lets an analyst inspect where a metro
started and ended, how it moved in absolute and relative terms, whether that
movement is nationally salient, which metrics support the frame result, and
whether compatible short- and medium-run evidence indicates a turn.

The first notebook is the human review surface for the materialized 50-metric
direct recurring panel. It is not yet the full Act 3 trend candidate pool and
must not present frame labels as publication-ready conclusions before contract
review is complete.

## Architecture Boundary

The Time-Series engine is the sole owner of:

- metric eligibility and transformations
- annual national percentiles
- robust trend estimates
- polarity alignment
- relative momentum
- topic-balanced frame aggregation
- salience tiers and trajectory labels
- short/medium turn-signal logic

The notebook may filter, join, label for display, and visualize the four
`mart_intelligence.intelligence_trajectory_*` tables. It must not recompute
any method field or silently substitute missing evidence. DuckDB is canonical;
review Parquet and CSV exports under the engine are not notebook inputs.

## Current Pilot Boundary

The current registry currently provides:

- 50 direct recurring KPIs: 13 Character, 23 Livability, and 14 Opportunity
- a stable 396-CBSA universe
- a common 2023 end vintage
- five-year evidence for all three frames using 2018–2023
- one-year Opportunity evidence using 2022–2023
- one compatible Opportunity turn comparison

The engine build plan explicitly treats this as method validation. The
remaining core KPI expansion, topic-balance review, and final contract freeze
must happen before the frame labels are considered publishable.

## Planned Folder Format

```text
trajectory/
├── README.md
├── POSITION_TRAJECTORY_README.md
├── POSITION_TRAJECTORY_SPEC.md
├── POSITION_TRAJECTORY_OUTPUTS_README.md
├── POSITION_TRAJECTORY_NOTEBOOK.py      # planned Marimo exploration surface
├── trajectory.py                       # planned headless QA runner
├── queries/
│   ├── trajectory_run_inventory.sql
│   ├── trajectory_frame_summary.sql
│   ├── trajectory_frame_context.sql
│   ├── trajectory_metric_evidence.sql
│   ├── trajectory_series.sql
│   └── trajectory_turn_signals.sql
└── figures/
    └── <cbsa_code>/                     # planned headless QA output only
```

## Parameters

| Parameter | Default | Role |
|---|---|---|
| `cbsa_code` | `40060` | Searchable target-market selector |
| `method_version` | `trajectory_pilot_v1` | Explicit engine-method selector; never silently mix versions |
| `window_name` | `five_year` | Chooses a compatible frame/metric window |
| `frame_id` | `opportunity` | Focuses national context and metric drill-through |
| `metric_id` | first eligible metric in selected frame/window | Drives the annual evidence view |
| `signal_threshold` | production p80 view | Display-only sensitivity control over persisted p80/p90/p95 flags |

Controls should be populated from the live run inventory. Invalid combinations
such as a one-year Character view should not be offered.

## Inputs

- `mart_intelligence.intelligence_trajectory_series`
- `mart_intelligence.intelligence_trajectory_metric`
- `mart_intelligence.intelligence_trajectory_frame`
- `mart_intelligence.intelligence_trajectory_turn_signals`
- `engines/time_series/CONTRACT.md`
- `engines/time_series/config/trajectory_metrics.yml`
- `engines/time_series/TIME_SERIES_ENGINE_BUILD_PLAN.md`

Profile identity and Peers may be linked later for interpretation, but they are
not required to build or validate the first Trajectory notebook.

## SQL Query Plan

| Query | Status | Grain | Purpose | Required notebook use |
|---|---|---|---|---|
| `queries/trajectory_run_inventory.sql` | Planned | Method version × frame × window × end year | Return row counts, eligible counts, metric/topic counts, and available year bounds from the four canonical tables | Populate valid controls and show pilot coverage |
| `queries/trajectory_frame_summary.sql` | Planned | Selected CBSA × frame × window | Return start/end position, momentum, salience, tier flags, label, direction, and coverage | Selected-market headline and position path |
| `queries/trajectory_frame_context.sql` | Planned | Method version × CBSA × frame × window | Return the compact all-market frame surface without recalculation | National distribution and target-highlight context |
| `queries/trajectory_metric_evidence.sql` | Planned | Selected CBSA × metric × window | Return endpoints, percentile change, transformed trend, absolute direction, relative momentum, salience, tier, and coverage | Metric evidence table and start/end comparison |
| `queries/trajectory_series.sql` | Planned | Selected CBSA × metric × year | Return raw value, transformed value, national percentile, source fields, polarity, and eligibility | Annual drill-through and source lineage |
| `queries/trajectory_turn_signals.sql` | Planned | Method version × CBSA × frame × window pair | Return the all-market turn surface with the selected CBSA marked for display | Turn-status summary and national short/medium context |

The selected-market queries should use the existing
`'__CBSA_CODE__'` placeholder convention. Method, frame, and window controls
must be restricted to values returned by `trajectory_run_inventory.sql`.
Queries should expose stored engine fields directly and avoid CASE expressions
that recreate labels or signal rules.

### Required fields by view

`trajectory_frame_summary.sql` must retain:

- `method_version`, `cbsa_code`, `cbsa_name`, `frame_id`,
  `window_name`, `start_year`, and `end_year`
- `topic_count`, `metric_count`, and `coverage_status`
- `start_position_percentile`, `end_position_percentile`, and
  `percentile_point_change`
- `frame_momentum_score` and `trajectory_salience_percentile`
- `position_band`, `movement_direction`, `absolute_direction`,
  `signal_tier`, the three persisted signal flags, and `trajectory_label`

`trajectory_metric_evidence.sql` must preserve both raw endpoint movement and
relative evidence. A notebook label must never replace
`endpoint_change_raw`, `trend_slope_transformed`,
`polarity_aligned_slope`, or `relative_momentum_score`.

## Notebook Flow

| Order | Section | Data and interaction | Expected result |
|---:|---|---|---|
| 1 | Purpose and panel warning | Markdown naming the 50-metric direct recurring boundary and internal-only status | The analyst cannot mistake this for a complete Act 3 surface |
| 2 | Setup | Portable paths, read-only DuckDB helpers, and query registry | Canonical mart dependencies fail early |
| 3 | Run inventory | Method/window/frame availability, year ranges, row counts, and eligible coverage | Controls are grounded in real materialized combinations |
| 4 | Market and view controls | Searchable CBSA plus method, window, frame, metric, and threshold controls | Every later view uses one coherent slice |
| 5 | Selected-market frame summary | Compact table of position, momentum, salience, tier, label, and coverage | Stored engine interpretation is visible without hiding component fields |
| 6 | Position path | Start-to-end percentile view for all available selected-market frame/window rows | The analyst can see where each frame began and ended |
| 7 | National trajectory context | All-market scatter for one frame/window with target highlighted | Position and movement are interpreted against the national distribution |
| 8 | Metric evidence | Table plus start/end percentile comparison for the selected frame/window | Supporting and contradictory KPI paths remain visible |
| 9 | Annual metric drill-through | Selected metric metadata, raw annual series, and national-percentile series | A frame result can be traced to observed annual evidence |
| 10 | Turn signals | Stored turn status, supporting metric IDs, short/medium momentum, and all-market context | `no_turn_signal` is shown as a valid result rather than missing data |
| 11 | Signal sensitivity | Counts and selected-market membership at persisted p80/p90/p95 flags | Analysts can see whether a lead survives stricter gates without rerunning the engine |
| 12 | QA appendix | Grain checks, eligibility/coverage, missing endpoints, and selected-row reconciliation | The notebook ends with explicit evidence health |

## Visual Plan

| Visual | Source | Form | Question it helps answer |
|---|---|---|---|
| Frame position path | `trajectory_frame_summary.sql` | Dumbbell or slope chart from start to end national percentile | Where did the metro begin and end relative to other metros? |
| Position and momentum context | `trajectory_frame_context.sql` | All-market scatter: ending-position percentile × frame momentum, target highlighted; salience in tooltip | Is the selected path unusual, and does position differ from movement? |
| Metric evidence | `trajectory_metric_evidence.sql` | Start/end percentile dumbbells plus a table of absolute direction, momentum, salience, and coverage | Which KPIs support or contradict the frame-level read? |
| Annual raw path | `trajectory_series.sql` | Single-metric line chart in the metric's raw unit | What actually happened to the observed measure? |
| Annual relative path | `trajectory_series.sql` | Separate line chart on a fixed `0–100` national-percentile scale | Did the metro gain or lose relative standing? |
| Turn context | `trajectory_turn_signals.sql` | Short-momentum × medium-momentum scatter with status and target highlight | Is the apparent reversal strong and unusual enough to count? |
| Threshold sensitivity | Stored frame flags | Compact p80/p90/p95 counts and selected-market status table | Does the signal persist under stricter salience thresholds? |

Raw values and national percentiles must use separate charts rather than a
dual axis. Character momentum is magnitude-oriented and non-normative; do not
compare its sign or display wording as if it used the same better/worse
semantics as Livability and Opportunity.

## Notebook Outputs

The Marimo notebook renders its tables and charts in place and has no required
exports.

The planned `trajectory.py` headless runner should write a small stable bundle:

- `figures/<cbsa_code>/trajectory_frame_paths.html`
- `figures/<cbsa_code>/trajectory_frame_context.html`
- `figures/<cbsa_code>/trajectory_metric_evidence.html`
- `figures/<cbsa_code>/trajectory_turn_context.html`

These are QA artifacts only. The engine review snapshots remain engine QA
artifacts, and neither output location is a downstream data source.

## Validation Rules

- all rows use one explicit `method_version`
- frame and metric keys are unique at their contracted grains
- selected controls correspond to a materialized frame/window combination
- start and end years match the selected window
- coverage and eligibility fields remain visible and missing values are not
  imputed
- frame metric/topic counts reconcile to the metric evidence rows
- annual endpoints reconcile to the metric table for eligible rows
- p95 implies p90, and p90 implies p80
- signal tier and label are read from the engine rather than recreated
- turn evidence uses compatible windows and the stored shared metric panel
- `no_standout_trend` and `no_turn_signal` render as valid results
- changing the selected CBSA updates all target highlights and evidence tables
- the notebook performs no DuckDB writes

## Interpretation Guardrails

- starting/ending position, absolute direction, relative momentum, and salience
  are distinct concepts and must remain separately labeled
- below-average relative momentum does not necessarily mean an observed raw
  metric declined
- Character is descriptive and non-normative at frame level
- pilot labels are useful for method review but not ready for publication
- a turn requires the stored magnitude and compatibility rules; a sign change
  alone is insufficient
- ordinary movement is evidence too; the notebook should not manufacture a
  story when the engine returns no standout or turn signal
- regional and peer trajectory comparisons belong to later Position/Thematic
  extensions after this base consumer is verified

## Out Of Scope

- metric transformation, trend, momentum, salience, or label computation
- expanding the pilot KPI panel
- final Act 3 lead-panel selection
- peer slopes, forward analogs, or diverging-peer scoring
- candidate-market ranking
- publication styling or narrative generation
- reading engine Parquet/CSV snapshots as canonical inputs

## Build Tasks

### Contract and query foundation

- [x] Confirm that all four trajectory tables are materialized in
  `mart_intelligence`.
- [x] Confirm the initial 12-KPI pilot boundary and the expanded 50-metric,
  396-CBSA, 2023-vintage direct recurring panel.
- [x] Confirm the frame, metric, series, and turn-signal grains and fields.
- [x] Create `trajectory_run_inventory.sql`.
- [x] Create the selected-market frame, metric, and annual-series queries.
- [x] Create the all-market frame and turn-context queries.
- [ ] Add query-level uniqueness, coverage, endpoint, and nested-threshold
  checks.

### Marimo notebook

- [x] Create `POSITION_TRAJECTORY_NOTEBOOK.py` with portable path resolution.
- [x] Add the pilot warning and live run inventory before the market charts.
- [x] Add Richmond-default market and valid method/window/frame controls.
- [x] Add the stored frame summary and position-path view.
- [x] Add the national position/momentum context scatter.
- [x] Add metric evidence and annual drill-through sections.
- [x] Add the turn-signal and p80/p90/p95 sensitivity sections.
- [x] Add the QA appendix and explicit coverage messaging.

### Headless QA and verification

- [ ] Create `trajectory.py` separately from the notebook.
- [ ] Write CBSA-specific HTML QA outputs without writing derived data.
- [ ] Reconcile Richmond notebook values to the four mart tables.
- [ ] Test one standout-signal metro and one ordinary-signal metro.
- [ ] Test one confirmed or emerging turn and one `no_turn_signal` case.
- [ ] Verify that invalid frame/window combinations cannot be selected.
- [ ] Review the rendered notebook in both the VS Code Marimo view and
  `marimo edit`.

### Engine gates carried forward

- [ ] Expand the audited core KPI panel in the Time-Series engine before
  treating frame labels as publication-ready.
- [ ] Re-run topic-balance, coverage, and threshold review after expansion.
- [ ] Freeze and catalog the full engine contract before downstream issue use.

## Success Check

The first Trajectory analysis is ready for exploratory review when an analyst
can select any covered metro, see its stored frame path in national context,
drill from frame evidence to metric and annual rows, understand why a signal or
turn status was assigned, and distinguish a valid ordinary result from missing
or insufficient evidence without any notebook-authored method calculation.
