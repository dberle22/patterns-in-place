# Position Analyses

`position/` holds the first consumer layer on top of the Intelligence
Framework engine.

These analyses should stay thin. They consume the engine contract from
`metro-deep-dive-program/engines/intelligence_framework/` and turn it into
usable Act 1 and early Act 3 analysis surfaces without rebuilding framework
logic here.

## Build Rule

Every analysis folder in `position/` should produce these things:

- a named README that explains what the analysis is for
- a named SPEC that defines its inputs, outputs, and scope
- a Marimo `.py` notebook as the primary human exploration surface
- a separate runnable `.py` entrypoint for repeatable headless QA
- reusable SQL query surfaces
- lightweight validation artifacts so we can inspect whether the analysis is
  behaving correctly before any issue-layer cleanup

Use the same folder shape for the first three Position analyses:

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

## What Not To Do Here

- do not rebuild frame scoring or similarity logic
- do not create a second competing contract beneath the engine
- do not overfit outputs to one market's issue packaging
- do not polish validation visuals as if they are final issue charts
- do not merge the three exploratory notebooks into the shared Act 1 issue
  assembly notebook; issue assembly remains a separate downstream consumer
