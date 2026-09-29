# Position Profile Analysis

This analysis is the first downstream consumer of the Intelligence Framework
engine.

Its job is to define the reusable Act 1 profile query surfaces for any metro
from the promoted framework marts.

## What It Reads

- `mart_intelligence.intelligence_character`
- `mart_intelligence.intelligence_livability`
- `mart_intelligence.intelligence_opportunity`
- `mart_intelligence.intelligence_cross_frame`

It also reuses the engine-level starter SQL for the headline label surface and
breaks the profile into smaller Act 1-facing query surfaces.

## What It Produces

Planned primary exploration surface:

- `POSITION_PROFILE_NOTEBOOK.py`
  Marimo notebook for interactive identity, frame, topic, KPI, vintage, and
  benchmark review.

Reusable query surfaces:

- `queries/profile_identity.sql`
- `queries/profile_percentiles.sql`
- `queries/profile_topic_scores.sql`
- `queries/profile_raw_kpis.sql`

Validation visuals:

- `figures/<cbsa_code>/profile_frame_percentiles.html`
- `figures/<cbsa_code>/profile_topic_strengths.html`

These HTML files remain the responsibility of the separate `profile.py`
headless QA runner. The Marimo notebook renders in place and is not required to
export files.

## Run the notebook

The notebook uses the shared `pip_benchmarking` package for governed
comparison-set and benchmark results. Install it into the Marimo environment
from the repository root before opening the notebook:

```bash
.venv-marimo/bin/python -m pip install -e foundations/benchmarking_py
.venv-marimo/bin/marimo edit metro-deep-dive-program/analyses/position/profile/POSITION_PROFILE_NOTEBOOK.py
```

This is a repo-relative editable install, so no machine-specific import path is
needed. Set `DB_PATH` or add it to the repo-level `.Renviron`; the notebook
opens that DuckDB database read-only.

## Why This Exists

We need one stable analysis surface that turns the framework marts into
notebook-friendly queries before we decide which pieces become issue assets.

This keeps us from binding the engine contract directly to final issue
presentation too early.

The saved artifacts are validation visuals from a parameterized analysis. They
help us inspect one CBSA at a time without turning this folder into the market-
specific issue layer or creating a parallel exported data layer.

See [POSITION_PROFILE_SPEC.md](POSITION_PROFILE_SPEC.md) for the agreed SQL
plan, notebook flow, visuals, guardrails, and build checklist.
