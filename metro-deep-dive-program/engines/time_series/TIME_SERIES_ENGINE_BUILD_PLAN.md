# Time-Series / Trajectory Engine Build Plan

Status: 50-metric direct recurring panel materialized 2026-09-07. Method direction agreed 2026-09-05.

This engine replaces the first-pass Phase 6 trajectory classification with
a reusable time-series method and a DuckDB-backed trajectory mart. The old
Phase 6 inputs, exclusions, and outputs are useful evidence, but its score and
four-way classification are not the new contract.

## Goal

Build a reusable time-series engine that can answer:

- where did a metro start and end relative to the national CBSA universe?
- what was its absolute direction over the period?
- did it gain or lose ground relative to other metros?
- was that relative movement common, notable, strong, or exceptional?
- do compatible short- and medium-run signals suggest a genuine turn?
- which KPIs support or contradict the frame-level interpretation?

## Architecture boundary

The engine owns metric eligibility and transformations, annual-series
normalization, trend estimation, national standardization, topic/frame
aggregation, sensitivity tiers, turn-signal logic, tests, and DuckDB
materialization.

`analyses/position/trajectory/` is a later thin consumer. It selects a CBSA,
queries the engine tables, and produces market-specific QA and interpretation
surfaces without recomputing the method.

This component belongs in `engines/time_series/` from the outset because the
program already names multiple consumers: Position / Trajectory, Act 3,
Data Takes, forward-analog slopes, and Candidate Scan support. The reuse case
is known rather than hypothetical.

## Storage contract

DuckDB is the canonical data layer. The initial build should materialize these
tables in `mart_intelligence`:

| Table | Grain | Purpose | Why it stays separate |
|---|---|---|---|
| `intelligence_trajectory_series` | CBSA × metric × year | Prepared annual history with transformation, percentile, vintage, eligibility, and coverage metadata | Preserves the reusable time path without repeating derived window results on every annual row |
| `intelligence_trajectory_metric` | CBSA × metric × window × end vintage | Metric-level start/end path, robust trend, absolute direction, relative momentum, and salience | Is the auditable method truth between raw history and frame aggregation |
| `intelligence_trajectory_frame` | CBSA × frame × window × end vintage | Topic-balanced frame path, momentum, signal tiers, labels, coverage, and agreement | Is the compact default surface most Position and Act 3 consumers will query |
| `intelligence_trajectory_turn_signals` | CBSA × frame × compatible window comparison | Confirmed turns, emerging watches, comparison status, and supporting KPI evidence | Has a window-pair grain and evidence fields that do not fit cleanly in a single-window frame row |

Downstream analyses should query these tables. Parquet files under `outputs/`
are review exports from the materialized tables, not the system of record and
not an input dependency for later analyses. CSV and HTML files are smaller QA
surfaces for national sensitivity checks and individual metros.

The table names should be added to the Intelligence Framework contract and
semantic table catalog when the build is validated. Until then they are the
proposed first-build names.

Keep all four tables. They are a small normalized mart rather than four
versions of the same output. `intelligence_trajectory_frame` is the default
consumer surface; the series and metric tables provide drill-through and
lineage, while the turn-signal table serves the specialized window-comparison
workflow.

## Method contract

`Trajectory` is the full path, not one composite number. Keep these concepts
separate:

| Concept | Meaning | Role in interpretation |
|---|---|---|
| Starting position | National percentile at the beginning of the window | Establishes where the path began |
| Ending position | National percentile at the end of the window | Establishes where the metro sits now |
| Percentile-point change | `ending_percentile - starting_percentile` | Gives a reader-facing description of relative movement |
| Estimated trend | Metric-aware slope using all valid observations in the window | Reduces dependence on two noisy endpoints |
| Absolute trend direction | Direction of the polarity-aligned trend in the metric's meaningful unit | Distinguishes outright improvement/decline from relative outperformance/underperformance |
| Momentum score | Signed, cross-market-standardized movement relative to the national pattern; position is excluded | Measures relative direction and movement |
| Trajectory salience | Percentile of absolute frame momentum within the national CBSA universe | Measures how unusual the movement is regardless of direction |
| Signal tier | Common, notable, strong, or exceptional | Controls whether movement receives an editorial label |
| Trajectory label | Plain-language description derived from position band, relative movement, and signal tier | Frames the story without replacing the measures |

Starting and ending frame percentiles must come from a consistent metric panel
and scoring method. Do not compare unlike historical model vintages.

### Trend estimation

For windows with at least four annual observations, use a robust Theil-Sen
slope on the declared transformed values as the canonical trend estimate. A
`1yr` window is necessarily a two-point short-run change and should be named as
such rather than presented as a fitted trend.

Keep the endpoint change alongside the fitted trend because it is easier to
explain and useful for reconciliation. Store observation count, start/end
year, estimator, transformation, and source vintage on every result. Do not
attach inferential significance to overlapping annual estimates such as ACS
five-year products.

Metric transformations must be explicit in `config/trajectory_metrics.yml`:

- shares and rates use percentage-point change where that is the meaningful
  unit
- dollar values use real or log change as appropriate
- counts and levels declare whether absolute or proportional change is the
  relevant measure
- rolling growth/change metrics declare whether the result represents level
  growth, a change in growth, or acceleration
- Livability and Opportunity may align polarity to better/worse movement
- Character remains non-normative: aggregate movement magnitude and keep
  direction in metric-specific evidence

### Relative momentum

Within each metric and compatible window/end vintage, convert the estimated
trend to an empirical national percentile and center that percentile into the
signed momentum score used for aggregation. Retain raw and polarity-aligned
absolute direction beside it.

This distinction is required because a metro can improve in absolute terms
while losing relative ground. Labels and evidence should be able to state both
rather than calling below-average growth an outright decline.

### Topic and frame aggregation

Aggregate metrics topic-first, then frame-level, so a topic does not gain
weight merely because it has more eligible KPIs. Store metric count, topic
count, coverage, and directional agreement alongside every aggregate.

Livability and Opportunity receive signed, polarity-aligned momentum.
Character receives a magnitude-of-change composite; its frame-level output
does not call demographic or structural movement better or worse.

## Signal sensitivity and labels

Calculate one continuous `trajectory_salience_percentile`, then expose nested
threshold flags rather than building three competing models:

| Absolute-momentum percentile | Signal tier | Approximate count in a 396-CBSA universe |
|---|---|---:|
| Below 80th | `common` | 317 |
| 80th to below 90th | `notable` | 39–40 |
| 90th to below 95th | `strong` | 20 |
| 95th and above | `exceptional` | 20 |

Counts are expectations rather than validation constants because ties and
missing coverage can change them. Persist `signal_p80`, `signal_p90`, and
`signal_p95` so the analysis can show which findings survive stricter cuts.

For Livability and Opportunity, assign a display label only when relative
movement is at least notable:

| Ending position band | Relative movement | Display label |
|---|---|---|
| High | Gaining ground | `pulling_ahead` |
| Low | Gaining ground | `catching_up` |
| High | Losing ground | `losing_ground` |
| Low | Losing ground | `falling_further_behind` |
| Middle | Gaining ground | `moving_up_quickly` |
| Middle | Losing ground | `moving_down_quickly` |
| Any | Below notable threshold | `no_standout_trend` |

Review the initial position-band boundary in the national sensitivity pass;
do not use a zero/mean split by default. Store `position_band`,
`movement_direction`, and `signal_tier` separately from the display label so
wording can change without recomputing scores.

Character uses `typical_character_change`, `notable_character_change`,
`strong_character_change`, and `exceptional_character_change`. Metric evidence
explains what changed.

## Turn-signal rule

Short- and medium-run comparisons must use the same KPI panel and compatible
end years. A sign change alone is not a turn signal.

- `confirmed_turn`: short- and medium-run momentum point in opposite
  directions and both clear the selected magnitude gate
- `emerging_turn_watch`: directions conflict and only the short-run signal
  clears the gate
- `no_turn_signal`: directions align or the apparent conflict is ordinary
  movement
- `insufficient_evidence`: coverage or window comparability fails

The sensitivity output should show how confirmed/watch membership changes at
the 80th, 90th, and 95th percentile gates before one production gate is
locked.

## Initial KPI inventory

The first-pass Phase 6 configuration supplies an initial inventory of `58`
recurring-series candidates: `13` Character, `23` Livability, and `22`
Opportunity. These are candidates for the metric audit, not automatically the
locked first run.

The proposed build separates a small method pilot, the broader direct
level/rate inventory, and already-derived change measures:

| Build lane | Character | Livability | Opportunity | Total | Treatment |
|---|---:|---:|---:|---:|---|
| Method-development pilot | 4 | 4 | 4 | 12 | Build the pipeline, tests, DuckDB grains, and review outputs; do not publish its partial frame labels |
| Additional core candidates | 9 | 19 | 10 | 38 | Add after transformation, coverage, vintage, and topic-balance checks |
| Derived-change review | 0 | 0 | 8 | 8 | Replace with underlying levels where possible; otherwise label explicitly as acceleration/deceleration |
| Context only | 4 | 3 | 1 | 8 | Do not score without verified recurring comparable histories |

The initial `12`-KPI pilot uses a common `2023` end vintage: the five-year
window is `2018–2023` and the Opportunity short-run comparison is `2022–2023`.
The universe remains the `396` CBSAs with a 2024 population of at least
100,000; that population reference defines membership and is not a claim that
every input is available through 2024. No missing metric values are imputed.

The pilot is:

- Character: `diversity_index`, `pct_age_over_64`,
  `pop_weighted_density_sqmi`, and `pct_ba_plus`
- Livability: `value_to_income`, `pct_rent_burden_30plus`,
  `pct_uninsured_adults`, and `aqi_median`
- Opportunity: `pct_unemployment_rate`, `lfpr`,
  `qcew_private_avg_wkly_wage`, and
  `bfs_business_application_rate_per_1000_establishments`

This panel covers indices, shares, rates, ratios, density, real-dollar
handling, positive/negative/neutral polarity, non-normative Character change,
ACS coverage rules, and multiple sources. All four Opportunity metrics support
compatible `1yr` and `5yr` comparisons, so the pilot can exercise turn-signal
logic without changing the KPI panel between windows.

The pilot validates mechanics, not final analytical balance. Expand to the
remaining `38` core candidates and rerun topic-balance and coverage QA before
the frame table or labels become publishable. A failed comparability check can
still move any candidate to context-only.

### Derived-change review queue (not scored)

The following eight Opportunity fields remain outside the trajectory registry.
They are already changes or growth rates, so trending them would generally
measure a change in an existing change measure. Review the underlying annual
level series first; retain a derived field only when acceleration or
deceleration is the explicit analytic question:

- `income_pc_growth_5yr`
- `pov_rate_change_5yr`
- `hpi_5yr_pct`
- `hpi_yoy_pct`
- `zori_annual_avg_yoy_pct`
- `pop_growth_5yr`
- `productivity_growth_5yr`
- `pct_ba_plus_change_5yr`

These are a future engine-review queue, not a second trajectory method or a
notebook input. The eight context-only fields likewise remain unscored until
their recurring, comparable annual histories are verified.

### Character — 13 trajectory candidates

- `diversity_index`
- `pct_black_nh`
- `pct_asian_nh`
- `pct_hispanic`
- `pct_age_over_64`
- `pct_ba_plus`
- `pct_foreign_born`
- `pop_weighted_density_sqmi`
- `irs_net_migration_rate`
- `pct_moved_diff_st`
- `pct_moved_abroad`
- `social_associations_per_10k`
- `pct_struct_multifam`

These remain descriptive. Composition shares also need a redundancy and
interpretation check because multiple shares can move together or trade off
without defining a single positive direction.

### Livability — 23 trajectory candidates

- `value_to_income`
- `pct_rent_burden_30plus`
- `pov_rate`
- `permits_per_1000_housing_units`
- `permits_share_units_5_plus`
- `pct_struct_mobile`
- `pct_struct_small_mf`
- `pct_struct_mid_mf`
- `premature_death_rate`
- `mental_health_provider_ratio`
- `drug_overdose_death_rate`
- `pct_uninsured_adults`
- `preventable_hospital_stay_rate`
- `firearm_fatality_rate`
- `motor_vehicle_crash_rate`
- `pct_commute_walk`
- `pct_commute_wfh`
- `vacancy_rate`
- `pct_hh_0_vehicles`
- `pct_no_internet_access`
- `pop_weighted_density_sqmi`
- `aqi_median`
- `fema_risk_score`

FEMA risk, health outcomes, and other periodically revised sources must pass a
comparability audit before their observed movement is treated as a real local
trend rather than a source-method change.

### Opportunity — 22 trajectory candidates

- `income_pc_growth_5yr`
- `pct_unemployment_rate`
- `lfpr`
- `pov_rate_change_5yr`
- `qcew_private_avg_wkly_wage`
- `hpi_5yr_pct`
- `hpi_yoy_pct`
- `zori_annual_avg_yoy_pct`
- `pop_growth_5yr`
- `irs_net_migration_rate`
- `irs_net_agi`
- `permits_per_1000_housing_units`
- `permits_share_units_5_plus`
- `productivity_growth_5yr`
- `industry_concentration_hhi`
- `bfs_business_application_rate_per_1000_establishments`
- `cbp_estabs_per_1000_residents`
- `pct_ba_plus_change_5yr`
- `lq_professional`
- `lq_information`
- `lq_manufacturing`
- `pct_real_gdp_information`

The rolling-change fields require the most work. Trending
`income_pc_growth_5yr`, `pov_rate_change_5yr`, `hpi_5yr_pct`, `hpi_yoy_pct`,
`zori_annual_avg_yoy_pct`, `pop_growth_5yr`, `productivity_growth_5yr`, or
`pct_ba_plus_change_5yr` measures a change in an existing change measure. The
metric audit should prefer the underlying level series where available; keep
the derived series only when acceleration or deceleration is the intended
signal.

### Context-only — 8 current fields

- Character: `friending_bias`, `civic_engagement_volunteering_rate`,
  `civic_organizations_per_1000`, `nonprofits_per_100k`
- Livability: `walkability_index`, `jobs_access_45min_transit`,
  `pct_population_low_income_low_access_1_10`
- Opportunity: `economic_connectedness`

These can appear in selected-market evidence but do not contribute to trend
or salience until recurring and comparable annual series are verified.

## Build stages

Build and validate each data layer sequentially. Do not run parallel DuckDB
writes.

| Status | Stage | Work | Verification gate |
|---|---|---|---|
| [ ] | 1. Audit the legacy build | Inventory Phase 6 metrics, windows, source tables, exclusions, and outputs. Mark each field reuse, revise, or retire. | Every legacy input/output has a disposition; the old score cannot be mistaken for the new contract. |
| [x] | 2. Lock the metric specification | Declare frame, topic, source, cadence, transformation, normativity, windows, minimum observations, and coverage for the initial 12-KPI pilot, then the 50-metric direct recurring panel; classify derived-change and context candidates for later review. | No scored metric relies on an implicit transformation; recurring-series and vintage checks pass. |
| [x] | 3. Build and materialize pilot annual history | Extract the consistent all-market metric-year table for the pilot and write a version-tagged `intelligence_trajectory_series`. | Grain is unique; year coverage, missingness, and endpoints are profiled before trend scoring proceeds. |
| [x] | 4. Estimate and materialize metric trends | Calculate transformed endpoints, percentiles, endpoint change, robust slope, absolute direction, relative momentum, and salience; write `intelligence_trajectory_metric`. | Synthetic rising, falling, flat, gapped, and outlier cases pass; real examples reconcile to sources. |
| [x] | 5. Aggregate and materialize frames | Aggregate metrics topic-first; calculate signed Livability/Opportunity momentum and magnitude-only Character change; write `intelligence_trajectory_frame`. | Metric-rich topics do not receive extra weight; coverage and disagreement remain visible. |
| [x] | 6. Run sensitivity and labels | Calculate continuous salience, nested 80th/90th/95th flags, position bands, tiers, and labels. | Flags are nested, counts are plausible, and ordinary movement never receives a strong story. |
| [x] | 7. Build and materialize turn signals | Compare compatible short- and medium-run estimates from the same KPI panel; write `intelligence_trajectory_turn_signals`. | Synthetic reversals distinguish confirmed, watch, no-signal, and insufficient-evidence cases. |
| [x] | 8. Expand and produce review outputs | Add the remaining audited core candidates, export table snapshots, run Richmond, and inspect national distributions plus automatically selected strong cases. | Topic coverage is sufficient, Richmond is interpretable, thresholds behave monotonically, and highlighted metros trace back to metric evidence. |
| [ ] | 9. Freeze the contract | Document tables/columns, grains, null rules, version/as-of fields, loader/build order, and QA-only exports. Update the Intelligence Framework contract and semantic catalogs. | A clean sequential full-panel rebuild is deterministic and another consumer can query DuckDB without notebook-specific knowledge. |

### Pilot build summary — 2026-09-05

The `trajectory_pilot_v1` build materialized all four proposed
`mart_intelligence` tables: 28,512 annual series rows, 6,336 metric-window
rows, 1,584 frame-window rows, and 396 Opportunity turn-signal rows. Structural
validation found no duplicate keys. The pilot has 390 eligible metros in every
five-year frame and 396 in the one-year Opportunity frame; the remaining
coverage statuses remain visible rather than being imputed.

The p80/p90/p95 review output is written to
`outputs/review/trajectory_threshold_sensitivity.csv`. The engine and metric
specification are complete for this pilot. Legacy-inventory disposition,
expanded KPI coverage, and catalog registration remain the next planned work.

## Planned engine folder

```text
engines/time_series/
├── README.md
├── TIME_SERIES_ENGINE_BUILD_PLAN.md
├── time_series_architecture.drawio
├── CONTRACT.md
├── NOTES.md
├── build_time_series_engine.py
├── trajectory_engine.py
├── config/
│   └── trajectory_metrics.yml
├── queries/
│   └── validate_trajectory_mart.sql
├── tests/
│   └── test_trajectory_method.py
└── outputs/
    ├── review/
    │   ├── intelligence_trajectory_series.parquet
    │   ├── intelligence_trajectory_metric.parquet
    │   ├── intelligence_trajectory_frame.parquet
    │   ├── intelligence_trajectory_turn_signals.parquet
    │   └── trajectory_threshold_sensitivity.csv
```

The Parquet files mirror the four DuckDB tables for review and portable QA.
They are not canonical inputs. The sensitivity CSV is a national inspection
artifact rather than a substitute mart.

## Planned Position consumer

```text
analyses/position/trajectory/
├── README.md
├── POSITION_TRAJECTORY_README.md
├── POSITION_TRAJECTORY_SPEC.md
├── POSITION_TRAJECTORY_OUTPUTS_README.md
├── trajectory.py
├── queries/
│   ├── trajectory_summary.sql
│   ├── trajectory_metric_evidence.sql
│   └── trajectory_turn_signals.sql
├── outputs/
│   └── <cbsa_code>/
│       ├── trajectory_summary.csv
│       ├── trajectory_metric_evidence.csv
│       └── trajectory_turn_signals.csv
└── figures/
    └── <cbsa_code>/
        ├── trajectory_percentile_paths.html
        ├── trajectory_signal_distribution.html
        └── trajectory_window_comparison.html
```

The Position folder does not own model code or all-market Parquet outputs. Its
CSV and HTML files are selected-market QA artifacts, not final issue visuals.

Candidate ranking is not a canonical trajectory output. A later Candidate
Scan may combine these signals with peer divergence or other Position
evidence, but it should consume the DuckDB trajectory contract rather than
place editorial weights inside the measurement method.
