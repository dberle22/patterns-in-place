# Position Candidate Scan Build Plan

**Status:** Epics 1–2 and the Discovery companion complete; Epic 3 interactive review pending; Epic 4 planned

This is a light notebook port, not a new engine project.

## Epic 1 — Audit the Legacy Port

- [x] Trace the Candidate List behavior from the Research Tool roadmap,
  component, and Phase 6 candidate artifacts.
- [x] Identify which legacy inputs still map directly to current Profile and
  Time-Series fields.
- [x] Record the fields or pattern flags that are obsolete rather than carrying
  them forward implicitly.
- [x] Define `candidate_scan_v1` and retain the persisted legacy ordering as a
  read-only comparison baseline.

The audit is recorded in
[`POSITION_CANDIDATE_SCAN_LEGACY_AUDIT.md`](POSITION_CANDIDATE_SCAN_LEGACY_AUDIT.md).
It corrects one material roadmap assumption: both the persisted legacy list
and the current contract contain 396 CBSAs, not 401. It also makes the port
boundary explicit: the five legacy Phase 6 pattern flags are retired because
their computations are not carried by the current Time-Series contract.

**Done:** the notebook method is a short list of current signals with visible
source fields and an explicit relationship to the old scan. Six markets without
eligible five-year coverage are retained in coverage reporting rather than
scored as zero.

## Epic 2 — Build the Marimo Surface

- [x] Add the all-market input and coverage summary.
- [x] Add the filterable ranked table.
- [x] Add one selected-market explanation and a small shortlist comparison.
- [x] Add compact weight sensitivity and in-notebook QA.
- [x] Add a light Discovery companion for first-look market discussion without
  duplicating or replacing the transparent v1 method.

**Done:** the useful workflow begins in the read-only
`POSITION_CANDIDATE_DISCOVERY_NOTEBOOK.py` and moves to
`POSITION_CANDIDATE_SCAN_NOTEBOOK.py` for detailed review. Current evidence
comes from DuckDB; the legacy CSV is comparison-only.

## Epic 3 — Review the Ranking

- [x] Compare the updated scan with the legacy ordering.
- [x] Review Richmond, Jacksonville, and several contrasting metros in the
  quantitative review.
- [x] Check that high ranks have legible contributing signals and are not
  driven by missingness, duplicated rows, or one accidental scale choice.
- Adjust and document the analysis-local method only when the review identifies
  a concrete problem.

The quantitative findings and interactive-review prompts are recorded in
[`POSITION_CANDIDATE_SCAN_EPIC3_REVIEW.md`](POSITION_CANDIDATE_SCAN_EPIC3_REVIEW.md).
No method adjustment is recommended before interactive analyst review.

**Done when:** an analyst can explain both stable and materially changed ranks
without reverse-engineering the notebook.

## Epic 4 — Close the Port

- Document the final method version and remaining caveats in the notebook.
- Update the Position and program documentation to point to the Marimo surface.
- Leave promotion deferred unless a second consumer needs the same candidate
  method unchanged.

**Done when:** the legacy Candidate List can remain frozen and the Marimo
notebook is the active market-selection surface.
