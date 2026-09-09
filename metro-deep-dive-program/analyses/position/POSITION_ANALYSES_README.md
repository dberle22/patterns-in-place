# Position Analyses

`position/` holds the first consumer layer on top of the Intelligence
Framework engine.

These analyses should stay thin. They consume the engine contracts under
`metro-deep-dive-program/engines/` and turn them into usable Position surfaces
without rebuilding engine logic locally. Most are selected-market notebooks;
Candidate Scan is the deliberate all-market exception used to choose which
metro to inspect next.

## Build Rule

The default analysis folder in `position/` should produce these things:

- a named README that explains what the analysis is for
- a named SPEC that defines its inputs, outputs, and scope
- a Marimo `.py` notebook as the primary human exploration surface
- a separate runnable `.py` entrypoint for repeatable headless QA
- reusable SQL query surfaces
- lightweight validation artifacts so we can inspect whether the analysis is
  behaving correctly before any issue-layer cleanup

Use the same folder shape for Profile, Peers, and Trajectory:

```text
<analysis>/
├── README.md
├── POSITION_<ANALYSIS>_README.md
├── POSITION_<ANALYSIS>_SPEC.md
├── POSITION_<ANALYSIS>_NOTEBOOK.py
├── <analysis>.py
├── queries/
└── figures/
    └── <cbsa_code>/
```

The notebook and QA entrypoint have different jobs:

- `POSITION_<ANALYSIS>_NOTEBOOK.py` is interactive, parameterized, and meant
  for browsing tables and simple visuals in Marimo.
- `<analysis>.py` reruns stable checks and writes a small QA bundle without
  requiring an interactive session.
- neither file owns engine calculations or final issue assembly.

Architecture rule:

- DuckDB is the data layer
- SQL files define the reusable analysis surfaces
- Marimo notebooks load and explore those query surfaces
- headless Python scripts validate stable query and visual expectations
- saved files in this layer should usually be QA visuals, not substitute marts

An analysis spec may declare a lighter build when the workflow does not need a
second execution path. Candidate Scan is notebook-only by design: its Marimo
surface owns the interactive ranking, explanation, sensitivity, and QA views.
Internal Structure starts notebook-first and adds durable QA only after its
two-part spatial surface stabilizes.

Shared comparison logic is the exception to a SQL-only consumer pattern.
Position notebooks should use `foundations/benchmarking_py` for on-demand
benchmark summaries and member rows because that package is the governed
consumer interface to `mart_benchmarking`. They should not reproduce its
ranking and percentile calculations in local notebook cells.

## Marimo Rule

- keep notebooks as Marimo-native `.py` files
- use `.venv-marimo/bin/python` and `.venv-marimo/bin/marimo`
- make shared Foundations packages available through a documented,
  repo-relative environment install; do not add machine-specific `sys.path`
  entries
- resolve paths from `Path(__file__)`, not the current working directory
- use a searchable CBSA selector with Richmond, VA (`40060`) as the default
- query DuckDB read-only and keep DuckDB as the canonical data layer
- use `mo.ui.dataframe(...)` for exploratory data surfaces and
  `mo.ui.table(...)` for compact summaries
- keep one main visual per cell when practical
- avoid redefining the same variable name in multiple cells because Marimo
  treats assignments as graph definitions
- do not require notebook exports; the separate QA script owns durable HTML
  validation outputs

## Validation Rule

At this layer, visuals are for inspection, not publication.

That means we want:

- simple charts
- HTML outputs we can reopen later
- no attempt yet to match final visual-library standards

The issue layer can later select the strongest outputs and restyle them for
publication.

## Current Position Analyses

- `profile/`
  Implemented exploration notebook for the Act 1 identity base: separate
  identity, percentile, topic-score, raw-KPI, and benchmark surfaces. Its
  remaining work is interactive review and headless-QA reconciliation.
- `peers/`
  Implemented exploration notebook for long peer retrieval, transparent
  frame overlap, position comparison, and governed featured-peer metrics. Its
  remaining work is interactive review and headless-QA reconciliation.
- `trajectory/`
  Implemented thin consumer of the Time-Series engine. It queries the
  `mart_intelligence` trajectory tables and produces selected-market evidence,
  national context, turn-status, and coverage surfaces without rebuilding the
  shared method. Its remaining work is interactive review and contract freeze.
- `internal_structure/`
  Planned two-part market-anatomy notebook. Part 1 relates counties, Census
  Places, tracts, ZCTAs, and Phase 7 zones. Part 2 examines POIs, employment
  centers, and major Infrastructure, with local-neighborhood mappings as a
  contextual overlay. Corridor exploration is question-led analysis, not an
  engine-produced geography.
- `candidate_scan/`
  Planned Marimo-only port of the legacy Research Tool Candidate List. It
  updates the market-selection workflow to the current Profile and Time-Series
  contracts while keeping ranking logic transparent and analysis-local.

## Dependency Summary

| Analysis | Build readiness | Remaining dependency |
|---|---|---|
| Candidate Scan | Ready to build | No new engine; use the current Intelligence Framework and Time-Series marts |
| Internal Structure Part 1 | Ready for a first market slice | Select governed Place/tract/ZCTA relationships, display geometry, scale metrics, and Phase 7 fields |
| Internal Structure Part 2 | POI, Infrastructure, and job-center capabilities exist | Select declared market inputs; local-neighborhood mappings are the next geographic dependency, while corridor exploration remains optional |

Candidate Scan is an analysis, not an engine. Its first ranking method remains
visible and local to the notebook. Corridor Intelligence is paused after its
pilot: its structural candidates are preserved as method artifacts, not a
canonical local-geography product. The next shared geography work is sourced
local-neighborhood mapping and its tract/ZCTA relationships.

`Similarity neighborhood` is retired as a Position analysis. CBSA similarity
remains in Peers and the separate similarity-method study; national tract and
ZCTA classifications remain in the Intelligence Framework; sourced local
neighborhood mappings belong in Geography; and corridor questions belong in
Internal Structure analysis.

## What Not To Do Here

- do not rebuild frame scoring or similarity logic
- do not create a second competing contract beneath the engine
- do not overfit outputs to one market's issue packaging
- do not polish validation visuals as if they are final issue charts
- do not merge the three exploratory notebooks into the shared Act 1 issue
  assembly notebook; issue assembly remains a separate downstream consumer
- do not use `similarity neighborhood` as a catch-all name for CBSA peers,
tract zone types, ZCTA rollups, local neighborhoods, or analysis-local
corridor explorations
