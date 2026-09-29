# Position Profile Spec

**Status:** Notebook implemented; interactive review and headless QA pending

**Default market:** Richmond, VA (`40060`)

**Primary surface:** `POSITION_PROFILE_NOTEBOOK.py`

**Headless QA:** `profile.py`

## Goal

Build the first reusable Position notebook for exploring what the Intelligence
Framework says about any single CBSA. The notebook should make identity,
position, topic structure, and the governed Act 1 KPI candidate pool easy to
inspect before any issue-layer selection or styling.

This is an exploratory analysis surface. It does not assemble Act 1, choose a
final fingerprint, or make publication claims.

## Architecture Boundary

The notebook is a thin consumer of two existing systems:

- `mart_intelligence` owns framework scores, labels, percentiles, and raw KPI
  fields.
- `mart_benchmarking` plus `foundations/benchmarking_py` owns reusable
  national, region, division, state, and peer-set comparisons.

Local SQL may reshape those outputs for analysis, but it must not recompute
framework scores, cluster labels, comparison-set membership, ranks, or
benchmark percentiles. DuckDB remains canonical; the notebook does not write a
profile mart or exported analysis dataset.

## Planned Folder Format

```text
profile/
├── README.md
├── POSITION_PROFILE_README.md
├── POSITION_PROFILE_SPEC.md
├── POSITION_PROFILE_OUTPUTS_README.md
├── POSITION_PROFILE_NOTEBOOK.py       # planned Marimo exploration surface
├── profile.py                         # existing headless QA runner
├── queries/
│   ├── profile_identity.sql
│   ├── profile_percentiles.sql
│   ├── profile_topic_scores.sql
│   └── profile_raw_kpis.sql
└── figures/
    └── <cbsa_code>/                   # headless QA output only
```

## Parameters

| Parameter | Default | Role |
|---|---|---|
| `cbsa_code` | `40060` | Searchable market selector backed by the promoted CBSA universe |
| `metric_type` | `topic_score` | Switch between topic and subject score exploration |
| `frame_id` | all frames | Optional filter for focused frame review |
| `comparison_set_type` | `national` | Benchmark context from the governed comparison-set registry |
| `fingerprint_metric_ids` | governed candidate pool | Optional multi-select for a smaller comparison view |

The notebook should derive available comparison sets and metrics from the live
contracts rather than hard-code a market-specific list.

## Inputs

### Intelligence Framework

- `mart_intelligence.intelligence_character`
- `mart_intelligence.intelligence_livability`
- `mart_intelligence.intelligence_opportunity`
- `mart_intelligence.intelligence_cross_frame`
- `engines/intelligence_framework/CONTRACT.md`

### Benchmarking

- `mart_benchmarking.benchmark_cbsa_metrics`
- `mart_benchmarking.benchmark_sets`
- `mart_benchmarking.benchmark_set_members`
- `foundations/benchmarking_py/pip_benchmarking`
- `engines/benchmarking/CONTRACT.md`

The first notebook should use the shared Python API for benchmark summaries
and member values. The engine-level
`queries/profile_fingerprint_benchmarks.sql` remains a useful contract check,
but its logic should not be copied into this folder.

The current Marimo environment has the notebook and plotting dependencies but
does not yet expose `pip_benchmarking`. Notebook implementation must add the
Foundations package through a documented repo-relative environment setup, not
a machine-specific import path.

## SQL Query Plan

| Query | Status | Grain | Purpose | Required notebook use |
|---|---|---|---|---|
| `queries/profile_identity.sql` | Exists | One selected CBSA | Join frame and cross-frame labels into one identity row | Identity summary and label QA |
| `queries/profile_percentiles.sql` | Exists | Selected CBSA × frame | Reshape the four framework percentile fields into a long surface | Frame-position chart |
| `queries/profile_topic_scores.sql` | Exists | Selected CBSA × frame × topic or subject | Expose scored dimensions with frame, theme group, label, value, and type | Topic/subject explorer and strongest/weakest table |
| `queries/profile_raw_kpis.sql` | Exists | Selected CBSA × raw KPI | Expose the fuller Act 1 candidate pool with source year | KPI inventory and vintage QA |

No new local SQL is required for the first notebook. Benchmark results should
come from `list_comparison_sets`, `get_target_metric_surface`, and
`benchmark_metric_bundle` in the shared Foundations package. Add a local query
only if a notebook view cannot be expressed by one of the four existing query
surfaces or the governed benchmark API.

## Notebook Flow

| Order | Section | Data and interaction | Expected result |
|---:|---|---|---|
| 1 | Purpose and caveats | Markdown describing the exploratory role, 396-CBSA framework universe, and public-use caveat | The analyst knows what the notebook can and cannot establish |
| 2 | Setup | Portable paths, read-only DuckDB connection helpers, SQL registry, benchmark package import | Dependencies fail early and visibly |
| 3 | Market selection | Searchable CBSA dropdown, defaulting to Richmond | All downstream cells react to one `cbsa_code` |
| 4 | Run summary | Identity-row presence, query row counts, available comparison sets, source-year range | Missing or partial inputs are visible before charts |
| 5 | Identity | Compact label table for frame clusters, combined cluster, top/bottom frame, overlap, and signature | Headline framework identity can be checked in one place |
| 6 | Frame position | Long percentile table and four-bar chart | Relative Character, Livability, Opportunity, and cross-frame position is legible |
| 7 | Topic and subject structure | Metric-type and frame controls, ranked table, strongest/weakest bar view | The analyst can inspect what drives the broad identity without exposing every KPI at once |
| 8 | Raw KPI candidate pool | Interactive dataframe with frame, theme, metric, value, and source year | Candidate fields and mixed vintages remain inspectable |
| 9 | Benchmark explorer | Comparison-set selector and optional metric multi-select using the shared benchmark API | Selected raw KPIs can be compared consistently against national, geographic, or peer sets |
| 10 | Interpretation candidates | Small table of strongest/weakest scored dimensions and largest benchmark departures | The notebook surfaces leads without selecting final issue claims |
| 11 | QA appendix | Missingness, duplicate-grain checks, row counts, and vintage spans | The notebook closes with an auditable health check |

## Visual Plan

| Visual | Source | Form | Question it helps answer |
|---|---|---|---|
| Frame position | `profile_percentiles.sql` | Four-bar chart on a fixed `0–100` scale | Which frames are relatively high or low? |
| Topic/subject strengths | `profile_topic_scores.sql` | Ranked horizontal bars, filterable by type and frame | Which modeled dimensions most shape the profile? |
| Fingerprint benchmark | Shared benchmark summary | Dot or lollipop chart showing target and comparison median, with percentile in tooltip/table | Which governed KPI candidates are most distinctive in the chosen comparison context? |
| Vintage coverage | `profile_raw_kpis.sql` | Compact table; chart only if mixed years are difficult to scan | Are apparent differences mixing materially different source years? |

Do not make a radar chart the default exploratory view. A radar can be tested
later after the fingerprint KPI set and axis order are locked at the issue
layer. The notebook should favor comparable bars, dots, and tables first.

## Notebook Outputs

The Marimo notebook renders interactive tables and charts in place. It has no
required file exports.

The existing `profile.py` headless runner continues to write:

- `figures/<cbsa_code>/profile_frame_percentiles.html`
- `figures/<cbsa_code>/profile_topic_strengths.html`

The QA runner may later gain small machine-readable check summaries, but it
must not become a second data mart or silently diverge from notebook queries.

## Validation Rules

- one and only one identity row exists for the selected CBSA
- percentile output contains Character, Livability, Opportunity, and
  cross-frame rows on a `0–100` scale
- topic/subject keys are unique within selected CBSA, frame, and metric type
- raw KPI keys are unique within selected CBSA, frame, and metric ID
- missing values and mixed source years remain visible
- available comparison sets come from `mart_benchmarking.benchmark_sets`
- benchmark denominators and membership sources remain visible
- changing the CBSA updates every table and visual without writing to DuckDB

## Interpretation Guardrails

- framework percentiles are modeled upstream; do not recalculate or relabel
  them locally
- high and low Character scores are descriptive, not better/worse judgments
- topic scores help explain the framework but are not raw observed measures
- final fingerprint slots, radar axes, stat boxes, and prose are issue-layer
  decisions
- public sharing remains subject to the Intelligence Framework similarity and
  universe review documented by the program

## Out Of Scope

- final issue visuals or Act 1 assembly
- a locked fingerprint KPI subset
- trajectory or peer derivation
- a new profile mart
- notebook-authored benchmark math
- automated narrative generation

## Build Tasks

### Contract and query foundation

- [x] Confirm the four promoted Intelligence Framework profile tables.
- [x] Confirm the shared benchmarking schema and Foundations Python API.
- [x] Create separate identity, percentile, topic/subject, and raw KPI queries.
- [x] Make `pip_benchmarking` importable in the Marimo environment through a
  documented repo-relative package install.
- [ ] Add query-level uniqueness, required-frame, and null checks to headless QA.

### Marimo notebook

- [x] Create `POSITION_PROFILE_NOTEBOOK.py` with portable path resolution.
- [x] Add a Richmond-default searchable CBSA selector.
- [x] Load the four local SQL surfaces through a read-only DuckDB connection.
- [x] Add run-summary and identity sections.
- [x] Add frame-position and topic/subject visuals.
- [x] Add interactive raw KPI and vintage tables.
- [x] Integrate comparison-set discovery and metric benchmarks through
  `foundations/benchmarking_py`.
- [x] Add interpretation-candidate and QA appendix sections.

### Headless QA and verification

- [x] Retain `profile.py` as a separate QA runner.
- [x] Preserve CBSA-specific HTML output folders.
- [ ] Reconcile notebook row counts with the headless runner for Richmond.
- [ ] Run at least one additional CBSA to verify parameterization.
- [ ] Verify that the notebook performs no DuckDB writes.
- [ ] Review the rendered notebook in both the VS Code Marimo view and
  `marimo edit`.

## Success Check

The analysis is ready for exploratory use when an analyst can select any
covered metro, understand its identity and frame position, inspect the topic
and raw KPI evidence behind that identity, change benchmark context through
the governed comparison engine, and trace every displayed value to a reusable
query or engine-owned API.
