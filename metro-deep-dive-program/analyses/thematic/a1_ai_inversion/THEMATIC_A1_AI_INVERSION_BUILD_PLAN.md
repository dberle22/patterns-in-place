# Thematic A1 — AI Inversion Build Plan

**Status:** Provisional; Epic 1 is the only authorized starting work

## Epic 1 — Audit prior work and revise the spec

- [ ] Inventory every legacy A1 notebook, query, crosswalk, output, dependency,
  and unresolved decision.
- [ ] Run or inspect the legacy Marimo analysis against the current read-only
  DuckDB and record failures, stale assumptions, row counts, and coverage.
- [ ] Reconcile the conceptual national universe with the live 2025 OEWS
  393-CBSA universe and the program’s other 396/401-CBSA cohorts.
- [ ] Verify the SOC and NAICS crosswalk lineage, reviewed mappings, duplicate
  behavior, denominators, and citations.
- [ ] Review H1–H3 findings and decide which claims remain live, which were
  weakened, and which should be retired.
- [ ] Separate reusable analysis surfaces from notebook-only construction and
  from issue-owned outputs.
- [ ] Decide whether legacy assets are migrated, referenced in place, or
  archived after replacement; do not duplicate them silently.
- [ ] Revise the spec and this plan with the audit findings before writing code.

**Done when:** the current A1 state is reproducible and the revised spec names
the exact national claim, universe, crosswalk contract, notebook sequence, and
migration disposition.

## Epic 2 — Stabilize shared A1 inputs

- [ ] Establish the reviewed, versioned SOC and NAICS lookup inputs.
- [ ] Define named coverage and metro-exposure query surfaces.
- [ ] Keep metric construction outside presentation cells where reuse is real.
- [ ] Validate keys, suppression flags, denominators, and Richmond by an
  independent calculation.

## Epic 3 — Build the national notebook

- [ ] Implement the reviewed national decision sequence.
- [ ] Show coverage and decomposition before hypothesis results.
- [ ] Evaluate each claim against declared alternatives and sensitivities.
- [ ] Produce the national finding ledger and candidate market hooks.

## Epic 4 — Build the parameterized market notebook

- [ ] Add the standard searchable CBSA selector.
- [ ] Build rank, peer/division context, occupation/industry decomposition,
  weighting, and concentration views approved by the national review.
- [ ] Test Richmond and at least two structurally different CBSAs.
- [ ] Preserve a no-distinctive-local-finding result.

## Epic 5 — Review and hand off

- [ ] Confirm the two notebooks agree on shared definitions and national
  context.
- [ ] Document stable result surfaces and any promotion candidate.
- [ ] Hand candidate findings and caveats to the relevant issue folder without
  moving issue narrative into this analysis.

