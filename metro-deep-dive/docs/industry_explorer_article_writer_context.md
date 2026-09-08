# Industry Explorer — Status Reconciliation Prompt

**Drop location:** `metro-deep-dive/metro-area-explorer/industry/`
**Use:** Run this at the start of any session before building. It produces a status report, not code.

---

## Task

Reconcile what this section's documents claim is built against what the code actually does. Report the gaps. Do not build anything in this pass.

## Read first, in this order

Standing contracts (the vocabulary this section is written against):

- `foundations/semantic_layer/` — metric, theme, and table definitions used by this section
- `foundations/data_dictionary/layers/gold/` — entries for any table referenced in `SPEC.md`
- `visual_library/README.md` and `visual_library/contracts/data_contract_dictionary.md`

Build contract and history:

- `industry/SPEC.md` — deliverables, acceptance criteria, open decisions
- `industry/CLOSEOUT_PLAN.md` — the last documented plan and its phase statuses
- `industry/decisions.md` — full log, most recent entries first
- `industry/POI_INFRA_PROPOSAL.md`, `industry/RICHMOND_POI_INFRA_REVIEW.md`

Implementation:

- `industry/data_prep.py`
- `industry/app.py`
- `industry/pages/` — every page module
- `metro-deep-dive/tests/test_industry_*.py`
- Cached outputs under `industry/outputs/`

## What to produce

### 1. Deliverable status table

One row per deliverable D1–D6. Columns: deliverable, what `SPEC.md` requires, what `CLOSEOUT_PLAN.md` claims, what the code actually implements, status.

Status is one of: `built and verified`, `built but unverified`, `partial`, `not started`, `documented but absent`.

Ground every "built" claim in a named function or page module. If you cannot point to the code that does it, it is not built.

### 2. Drift report

Where the documents and the code disagree. Specifically:

- Acceptance criteria in `SPEC.md` marked complete that the code does not satisfy
- Behavior in the code that no acceptance criterion covers
- `CLOSEOUT_PLAN.md` phases marked complete or incomplete inconsistently with `decisions.md`
- Anything in `decisions.md` recorded as deferred that has since been silently implemented, or vice versa

### 3. Open decisions — current state

Take the open-decisions table in `SPEC.md` and mark each entry: still open, resolved in code but not in the doc, resolved in the doc, or no longer relevant. Flag any decision that appears to have been resolved by implementation default rather than by an explicit choice.

### 4. Contract coverage check

For every Gold or Silver table this section queries, confirm it is defined in the semantic layer and the data dictionary. List any table, metric, or join used in `data_prep.py` that has no standing definition upstream.

### 5. Remaining work

Ordered list of what is left to close out the section, with the acceptance criterion each item satisfies. Flag any item where the criterion is missing or too vague to check against.

### 6. Readability flags

For each built page, note anything an outside reader could not interpret without internal knowledge — raw geographic identifiers, unlabeled codes, undefined field names, charts with no stated takeaway. This is a separate list from correctness. Something can be fully correct and still belong here.

## Constraints

- Read before concluding. Do not infer implementation state from documentation.
- Do not write, edit, or refactor code in this pass.
- Do not propose new deliverables or scope.
- Do not treat `CLOSEOUT_PLAN.md` as authoritative — it is dated and may be stale. The code is the source of truth for what exists; `SPEC.md` is the source of truth for what was agreed.
- Where the two conflict, report the conflict rather than resolving it yourself.

## Output

A single markdown report at `industry/STATUS_<YYYY-MM-DD>.md`. End it with the three things you are least certain about and what you would need to check to resolve them.