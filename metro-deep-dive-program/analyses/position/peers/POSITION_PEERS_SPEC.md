# Position Peers Spec

**Status:** Notebook implemented; interactive review and headless QA pending

**Default market:** Richmond, VA (`40060`)

**Primary surface:** `POSITION_PEERS_NOTEBOOK.py`

**Headless QA:** `peers.py`

## Goal

Build a reusable Position notebook for exploring which metros resemble a
selected CBSA, whether that resemblance holds across frames, and where the
target and its peers differ on governed profile metrics.

The notebook should make both cross-frame and frame-specific peer sources
explicit. It may surface candidates for a featured comparison, but the issue
layer chooses the featured peer and writes the claim.

## Architecture Boundary

The Intelligence Framework owns cosine similarity, peer ranking, and the
promoted top-10 peer fields. The Benchmarking engine owns comparison-set
membership and metric-level benchmark calculations.

This analysis may reshape peer fields, compare ranks, and join existing
profile outputs. It must not recompute similarity, extend the peer universe
beyond the promoted top 10, create slope-based peers, or implement a
forward-analog method.

## Planned Folder Format

```text
peers/
├── README.md
├── POSITION_PEERS_README.md
├── POSITION_PEERS_SPEC.md
├── POSITION_PEERS_OUTPUTS_README.md
├── POSITION_PEERS_NOTEBOOK.py         # planned Marimo exploration surface
├── peers.py                           # existing headless QA runner
├── queries/
│   ├── peer_list.sql
│   ├── peer_benchmark_top5.sql
│   └── peer_overlap_summary.sql       # planned
└── figures/
    └── <cbsa_code>/                   # headless QA output only
```

## Parameters

| Parameter | Default | Role |
|---|---|---|
| `cbsa_code` | `40060` | Searchable target-market selector |
| `peer_type` | `cross_frame` | Switch among cross-frame, Character, Livability, and Opportunity peers |
| `peer_count` | `5` | Display control capped by the promoted top-10 contract |
| `featured_peer_code` | highest-ranked visible peer | Analyst-controlled head-to-head candidate |
| `comparison_metric_ids` | profile candidate subset | Metrics shown in the featured-peer comparison |

The selected peer must always come from the currently loaded peer surface.
Changing `peer_type` should update the available featured-peer choices.

## Inputs

### Intelligence Framework and Profile

- `mart_intelligence.intelligence_character`
- `mart_intelligence.intelligence_livability`
- `mart_intelligence.intelligence_opportunity`
- `mart_intelligence.intelligence_cross_frame`
- `analyses/position/profile/queries/profile_identity.sql`
- `analyses/position/profile/queries/profile_percentiles.sql`
- `analyses/position/profile/queries/profile_raw_kpis.sql`
- `engines/intelligence_framework/CONTRACT.md`

### Benchmarking

- `mart_benchmarking.benchmark_cbsa_metrics`
- `mart_benchmarking.benchmark_sets`
- `mart_benchmarking.benchmark_set_members`
- `foundations/benchmarking_py/pip_benchmarking`
- `engines/benchmarking/CONTRACT.md`

The peer list comes from the Intelligence Framework. Metric comparisons should
use the benchmarkable metric surface and shared Foundations API rather than
reimplementing comparison calculations in notebook cells.

The current Marimo environment has the notebook and plotting dependencies but
does not yet expose `pip_benchmarking`. Notebook implementation must add the
Foundations package through a documented repo-relative environment setup, not
a machine-specific import path.

## SQL Query Plan

| Query | Status | Grain | Purpose | Required notebook use |
|---|---|---|---|---|
| `queries/peer_list.sql` | Exists | Selected CBSA × peer type × peer rank | Unpivot the four promoted wide top-10 lists into one long peer surface | Peer inventory, rank controls, and similarity charts |
| `queries/peer_benchmark_top5.sql` | Exists | Target plus top five cross-frame peers | Join cluster labels and four framework percentiles for a compact comparison | First-pass target/peer position heatmap |
| `queries/peer_overlap_summary.sql` | Planned | Selected CBSA × unique peer CBSA | Summarize which peer types contain each metro, each rank, and each similarity without inventing a new score | Cross-frame/frame overlap table and rank-pattern visual |

`peer_overlap_summary.sql` should derive only transparent fields:

- `peer_cbsa_code`
- `peer_cbsa_name`
- `peer_type_count`
- one rank and similarity column per peer type
- `best_rank`
- `mean_available_rank`

It should not collapse those fields into a new peer score. Metric-level
head-to-head comparisons should be loaded from
`mart_benchmarking.benchmark_cbsa_metrics` through the shared API. If the API
needs a two-geography convenience function later, add it to Foundations only
after a second consumer confirms the same need.

## Notebook Flow

| Order | Section | Data and interaction | Expected result |
|---:|---|---|---|
| 1 | Purpose and caveats | Markdown defining primary cross-frame peers, supporting frame peers, the top-10 limit, and internal-use caveat | The analyst understands what “peer” means here |
| 2 | Setup | Portable paths, read-only connection, SQL registry, shared benchmark import | Engine and query dependencies fail early |
| 3 | Market and peer controls | Searchable CBSA selector, peer-type selector, and peer-count control | All peer views share one target and explicit peer lens |
| 4 | Run summary | Counts by peer type, missing fields, duplicate peers, and comparison-set availability | Contract gaps are visible before interpretation |
| 5 | Ranked peer inventory | Interactive long table and similarity bars for the selected peer type | The basic ranking is easy to inspect |
| 6 | Peer overlap | Overlap summary table plus a rank-by-frame heatmap | The analyst can distinguish broad resemblance from one-frame resemblance |
| 7 | Cross-frame position comparison | Existing target-plus-top-five percentile surface | The target and primary peers can be compared across the three frames and combined position |
| 8 | Featured-peer selection | Dropdown populated from the active peer list | The analyst can choose a concrete comparison without changing peer generation |
| 9 | Head-to-head profile | Identity labels, selected raw KPI values, benchmark metadata, and a compact difference view | Similarity and meaningful differences can be examined together |
| 10 | Candidate notes | Transparent table of rank, similarity, frame overlap, and largest metric gaps | Potential featured peers are surfaced without an automated editorial choice |
| 11 | QA appendix | Rank continuity, self-peer, duplicate, missing-name, and similarity-order checks | The peer contract is auditable for the selected CBSA |

## Visual Plan

| Visual | Source | Form | Question it helps answer |
|---|---|---|---|
| Peer similarity ranking | `peer_list.sql` | Horizontal bars, one selected peer type at a time | Which metros are the closest peers under this lens? |
| Rank across frames | `peer_overlap_summary.sql` | Heatmap with peers as rows and peer types as columns | Does a peer recur across frames or only in one? |
| Target and top-five position | `peer_benchmark_top5.sql` | Percentile heatmap on a fixed `0–100` scale | How do the primary peers differ in broad framework position? |
| Featured-peer KPI comparison | Shared benchmark metric surface | Dumbbell or paired-dot chart for a small metric selection | Where are two otherwise similar metros materially different? |

Keep similarity and percentile values visually separate. They answer different
questions and should not share one color scale or be presented as interchangeable
scores.

## Notebook Outputs

The Marimo notebook renders interactive tables and simple charts in place and
has no required exports.

The existing `peers.py` headless runner continues to write:

- `figures/<cbsa_code>/peer_similarity_bars.html`
- `figures/<cbsa_code>/peer_compare_heatmap.html`

The headless runner should eventually validate the overlap query too, but
durable issue assets remain out of scope.

## Validation Rules

- peer rank is unique within selected CBSA and peer type
- non-null ranks are contiguous from 1 through the available peer count
- the target CBSA never appears as its own peer
- peer names and codes are non-null together
- similarity values are ordered consistently with the promoted rank
- no control exposes more than the contracted top 10
- overlap summaries preserve the source rank and similarity for every frame
- target-plus-peer comparison rows are unique by CBSA
- benchmark comparison denominators and source years remain visible
- changing the selected CBSA or peer type updates every downstream view

## Interpretation Guardrails

- cross-frame cosine peers are the primary identity peer set; frame-specific
  peers are supporting lenses
- similarity indicates resemblance in modeled feature space, not causal or
  geographic equivalence
- a high-similarity peer may still differ sharply on individual observed KPIs
- a peer appearing in several frame lists is a transparent robustness clue,
  not a newly validated composite score
- featured-peer selection remains an analyst and issue-layer decision
- slope-based peers, diverging peers, and forward analogs require Trajectory
  and are not implied by the current level-based peer surface
- public use must retain the framework-method caveat until similarity and
  universe questions are resolved

## Out Of Scope

- recomputing similarity or cluster membership
- peers beyond the promoted top 10
- slope-based peer generation
- diverging-peer or forward-analog scoring
- final issue comparison styling or copy
- automated featured-peer selection
- peer-network and threshold-neighborhood analysis

## Build Tasks

### Contract and query foundation

- [x] Confirm the promoted top-10 peer fields for all four peer types.
- [x] Create a long peer-list query.
- [x] Create the target-plus-top-five framework-position query.
- [x] Confirm that peer-set membership is also materialized in
  `mart_benchmarking`.
- [x] Make `pip_benchmarking` importable in the Marimo environment through a
  documented repo-relative package install.
- [ ] Add `queries/peer_overlap_summary.sql` without a synthetic composite
  score.
- [ ] Add rank, self-peer, duplicate, and null checks to headless QA.

### Marimo notebook

- [x] Create `POSITION_PEERS_NOTEBOOK.py` with portable path resolution.
- [x] Add Richmond-default market, peer-type, and peer-count controls.
- [x] Add the ranked inventory and similarity chart.
- [x] Add the cross-frame/frame overlap table and rank heatmap.
- [x] Add the target-plus-top-five position comparison.
- [x] Add a featured-peer selector driven by the active peer list.
- [x] Add a small head-to-head KPI comparison using the governed benchmark
  surface.
- [x] Add candidate-notes and QA appendix sections.

### Headless QA and verification

- [x] Retain `peers.py` as a separate QA runner.
- [x] Preserve CBSA-specific HTML output folders.
- [ ] Reconcile notebook peer counts and ordering with the headless runner for
  Richmond.
- [ ] Run at least one additional CBSA and one frame-specific peer lens.
- [ ] Confirm that every displayed peer traces to a promoted engine field.
- [ ] Verify that the notebook performs no DuckDB writes.
- [ ] Review the rendered notebook in both the VS Code Marimo view and
  `marimo edit`.

## Success Check

The analysis is ready for exploratory use when an analyst can select any
covered metro, move between its cross-frame and frame-specific peer sets,
understand where peer membership overlaps, compare the target with a chosen
peer on governed profile metrics, and distinguish engine-owned similarity from
analysis-layer interpretation.
