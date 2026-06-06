# QA Testing & Tuning Strategy

## The Two Systems Under Test

The pipeline has two distinct parsing paths with completely different failure modes:

| Path | Trigger | What can go wrong |
|---|---|---|
| **Heuristic** | Pattern match in `_heuristic_parse()` | Wrong routing, missing geo, wrong metric, silent wrong output |
| **LLM** | `force_provider=True` or heuristic fails | Misclassification, wrong slots, hallucinated geo IDs, unnecessary clarification |

These two paths need different test strategies. Mixing them in one undifferentiated batch makes it hard to know which layer broke.

---

## Category Definitions

### `golden`
**Purpose:** Regression anchors for the heuristic path.
**Behavior:** The batch runner does NOT force the LLM. These cases should resolve through exact example matching or heuristic parsing without touching the LLM at all.
**What to watch:** If a golden case fails after a code change, something in the heuristic or example library broke. This is a blocker.
**How many:** 1–2 per question type. Keep this set small and stable.

### `provider_paraphrase`
**Purpose:** Generalization tests for the LLM.
**Behavior:** The batch runner sets `force_provider=True`, which bypasses heuristics entirely. The LLM must parse the question from scratch using only the system prompt and few-shot examples.
**What to watch:** This is where system prompt tuning and few-shot example changes show up. A failing `provider_paraphrase` case after a system prompt edit means the LLM is not generalizing correctly.
**How many:** 3–5 per question type, covering different phrasings, different metrics, different geo levels.

### `clarification`
**Purpose:** Verify the system asks good questions instead of guessing.
**Behavior:** Underspecified prompts that are missing required slots. The system should return a readable clarification, not a broken query.
**What to watch:** Clarification message quality (plain English, not internal field names), and that the system doesn't guess when it should ask.
**How many:** 1–2 per failure mode (missing geo, missing metric, ambiguous intent).

---

## Why Run Golden Cases At All?

Golden cases are regression tests. They are not meant to stress the LLM — they confirm that deterministic behavior hasn't broken. If you change `_heuristic_parse()` and a golden case fails, you know immediately what broke. Run them in every loop but don't interpret them as LLM quality signals.

To test only the LLM, run:
```bash
.venv/bin/python -m app.scripts.qa_batch --collection loop3 --category provider_paraphrase --render-chart
```

To run just regression checks:
```bash
.venv/bin/python -m app.scripts.qa_batch --collection loop3 --category golden
```

---

## How New Questions Get Into the Batch

The batch runner reads **only** from `qa/qa_prompt_library.yml`. Nothing is auto-discovered. To add a new test case:

1. Open `qa/qa_prompt_library.yml`.
2. Add a new entry under `cases:` following the schema below.
3. The next batch run will include it automatically.

```yaml
- qa_case_id: qa_b_004                        # unique ID, format: qa_<type>_<nnn>
  question: "Your natural language question"
  category: provider_paraphrase                # golden | provider_paraphrase | clarification
  question_type_expected: benchmark            # ranking | trend | distribution | benchmark | growth
  metric_expected: median_hh_income           # metric_id from metric_catalog.yml, or null
  geo_level_expected: state                    # geo_level from geography_catalog.yml, or null
  template_expected: benchmark                 # template_id from query_templates.yml, or null
  benchmark_type_expected: us                  # us | region | division | peers | null
  notes: "What this case is testing."
```

---

## Coverage Targets

The library should eventually cover:

| Question type | Golden | Provider paraphrase | Clarification |
|---|---|---|---|
| benchmark | 1 | 4–5 | 1 |
| ranking | 1 | 3–4 | 0 |
| trend | 1 | 3–4 | 1 |
| distribution | 1 | 2–3 | 0 |
| growth | 1 | 3–4 | 1 |
| comparison | 0 | 2–3 | 1 |

**Current gaps (as of loop 2):**
- `growth` has zero provider_paraphrase cases — the LLM path for growth questions is completely untested.
- `distribution` has no paraphrase cases.
- `comparison` is entirely absent.
- Benchmark only has 2 paraphrase cases; needs more metric and geo variety.

---

## Tuning Loop Workflow

```
1. Run batch (provider_paraphrase + render-chart)
2. Check batch_summary.json — note parsed vs clarification vs error counts
3. Open qa_review app — read qa_run.json for each failure
4. Identify root cause:
     - Wrong question_type  → fix system prompt guidance or few-shot examples
     - Right type, wrong slots → fix slot-filling examples or heuristic fallback
     - Unnecessary clarification → add a few-shot example covering that phrasing
     - Correct parse, wrong SQL → fix generator or planner
     - Correct SQL, wrong chart → fix selector or renderer
     - Correct chart, shallow answer → fix assembler templates
5. Write fix brief (qa/loop<N>_fix_brief.md)
6. Make fixes
7. Increment collection label, re-run
```

## Interpreting Results

| Signal | What it means |
|---|---|
| Golden fails, paraphrase passes | Heuristic or example match was broken by a code change |
| Paraphrase fails, golden passes | LLM isn't generalizing — improve system prompt or few-shots |
| All benchmark fails | `benchmark_type` or `target_geo_id` not being set — check heuristic and few-shots |
| Unnecessary clarification | Missing slot inference — check heuristic or add a few-shot for that phrasing |
| Parse correct but wrong result | SQL generator or Gold data issue — check rendered SQL in `result.sql` |
| Parse + SQL correct but shallow answer | Assembler needs a richer template for that question type |

---

## A Note On LLM Non-Determinism

LLM results are not fully reproducible. A `provider_paraphrase` case that passes in one loop may fail in another with no code changes, just due to model variance. Treat a single failure as a signal, not a verdict — confirm with 2–3 re-runs before writing a fix brief. Sustained failures across runs are the real signal.
