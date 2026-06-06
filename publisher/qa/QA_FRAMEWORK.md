# QA Framework

Last updated: 2026-04-30

## Purpose

This document defines the recommended QA framework for the Metro Deep Dive Chatbot before more frontend work is done.

The goal is to make QA:

- structured
- repeatable
- attributable to the correct pipeline layer
- easy for another agent or human reviewer to analyze

This is intentionally a framework document, not an implementation doc. It is meant to guide the next round of QA tooling and review workflows.

---

## Why We Need This

The current project can produce end-to-end outputs, but review is still too ad hoc.

Right now, a single bad run could be caused by:

- intent parsing
- LLM/provider behavior
- query planning
- SQL template generation
- SQL validation
- result-shape interpretation
- chart selection
- chart rendering
- answer-text assembly

If QA is only done at the “did a chart render?” level, it is hard to tell which layer is responsible for a problem.

The QA framework should separate those layers cleanly.

---

## QA Principles

1. Review the pipeline in layers, not only end to end.
2. Save one structured record per QA run.
3. Use the same review contract for success cases and clarification cases.
4. Keep golden regression examples separate from LLM paraphrase evaluation.
5. Build QA data structures first, then build a frontend on top of them.

---

## QA Layers

Each run should be evaluated across these layers.

### 1. Intent QA

Questions:

- Did the system choose the correct question type?
- Did it choose the correct metric?
- Did it choose the correct geography level?
- Did it resolve the right geography IDs?
- Did it infer the right year, time window, or benchmark intent?
- If the prompt was underspecified, did it ask for the right clarification?

### 2. Query Plan QA

Questions:

- Is the structured plan complete?
- Does it map cleanly to an approved template?
- Are all slots valid under the semantic layer rules?
- Is the plan specific enough to produce a safe SQL query?

### 3. SQL QA

Questions:

- Does the generated SQL match the plan?
- Does it use the correct table and metric column?
- Does it apply the right filters?
- Does it use the intended query template?
- Is the SQL valid and read-only?

### 4. Data / Result QA

Questions:

- Did the query return rows?
- Did it return the expected shape?
- Are the values plausible?
- Are nulls handled correctly?
- Do benchmark rows or growth rows behave correctly?

### 5. Chart QA

Questions:

- Is the selected chart type appropriate?
- Does the rendering match the result shape?
- Are labels, scales, and formatting correct?
- Are percent, currency, and benchmark conventions correct?
- Are highlight behaviors correct when applicable?

### 6. Answer Text QA

Questions:

- Does the written answer match the result?
- Is it specific enough to be useful?
- Does it avoid saying more than the data supports?
- Does it handle clarification cases properly?

### 7. End-to-End Regression QA

Questions:

- Does the full pipeline behave consistently across known prompts?
- Do new changes improve target behavior without breaking stable cases?
- Are timing and runtime stability acceptable?

---

## Required Saved Data Per Run

Every QA run should save a single structured artifact that can be reviewed later.

Recommended top-level fields:

- `run_id`
- `question`
- `provider`
- `provider_mode`
  `example_match`, `heuristic`, `llm_forced`, `llm_optional`
- `matched_example_id`
- `force_provider`
- `parse_status`
  `parsed`, `clarification`, `error`
- `query_plan`
- `clarification`
- `rendered_sql`
- `validation_result`
- `result_row_count`
- `result_preview`
- `result_profile`
- `chart_type`
- `chart_path`
- `answer_text`
- `timings_ms`
- `expected_outcome`
- `review_status`
  `unreviewed`, `pass`, `partial`, `fail`
- `qa_notes`

This should become the canonical `qa_run.json` contract.

---

## Clarification Cases Must Also Be First-Class QA Artifacts

Clarification cases are not just failures.

They should be saved and reviewed with the same seriousness as successful runs.

For clarification cases, we still want to know:

- what question was asked
- what the model inferred correctly
- what fields were missing
- whether the clarification request was appropriate
- whether the wording was useful to the reviewer or user

That means the QA contract should support:

- successful runs
- clarification runs
- hard error runs

without using different ad hoc file formats.

---

## Recommended QA Prompt Sets

Before building more UI, define a stable QA prompt library with three categories.

### 1. Golden Examples

Purpose:

- regression anchors
- exact cases we expect to work perfectly
- useful for deterministic and template-level testing

Recommended contents:

- one or more prompts for each supported question type
- these may be exact prompts from the existing example library

### 2. Provider Paraphrases

Purpose:

- evaluate real LLM performance
- test whether the model can generalize beyond exact examples

Recommended contents:

- reworded versions of golden examples
- should be run with `--force-provider`
- should avoid exact wording from the example library

### 3. Failure / Clarification Cases

Purpose:

- evaluate whether the system asks good questions when user intent is incomplete
- identify recurring LLM weaknesses

Recommended contents:

- ambiguous benchmark phrasing
- incomplete geography references
- underspecified growth questions
- vague distribution prompts
- prompts that mix multiple question types

---

## Recommended Initial QA Coverage

Suggested starting set:

- 5 ranking prompts
- 5 trend prompts
- 4 distribution prompts
- 4 benchmark prompts
- 4 growth prompts
- 3 clarification-oriented prompts

Total: about 25 prompts

This is enough to identify patterns while staying small enough for manual review.

---

## Scoring Framework

Each run should be scored at the layer level.

Recommended fields:

- `intent_score`
- `plan_score`
- `sql_score`
- `result_score`
- `chart_score`
- `answer_score`
- `clarification_score`

Scoring can start simple:

- `1` = correct
- `0` = incorrect
- `null` = not applicable

And then summarize each run as:

- `pass`
- `partial`
- `fail`

This lightweight scoring is enough for early QA and easy for another agent to analyze.

---

## Recommended Review Questions Per Run

Every reviewer should be able to answer these quickly:

1. Did the system understand the question correctly?
2. Did it choose the right structured plan?
3. Did the SQL reflect that plan faithfully?
4. Did the results look right?
5. Was the chart appropriate and correctly formatted?
6. Did the final answer describe the output accurately?
7. If there was a clarification, was it the right clarification?

If those questions cannot be answered from the saved artifact set, then the QA contract is incomplete.

---

## Recommended Build Order

This should be the implementation order for QA tooling.

### Step 1. Define `qa_run.json`

Create a single canonical machine-readable schema for one QA run.

### Step 2. Create `qa_prompt_library.yml`

Store prompt sets, expected behavior, and tags in one version-controlled file.

Suggested metadata per prompt:

- `qa_case_id`
- `question`
- `category`
  `golden`, `provider_paraphrase`, `clarification`
- `question_type_expected`
- `metric_expected`
- `geo_level_expected`
- `template_expected`
- `notes`

### Step 3. Update the CLI / runner to always write `qa_run.json`

The current artifact-saving behavior should be unified behind the canonical QA record.

### Step 4. Build a batch QA runner

It should:

- run many prompts in sequence
- save one folder per run
- emit a summary CSV/JSON
- track pass/partial/fail and review status

### Step 5. Add a review surface

Only after the QA contract and batch runner exist should a Streamlit review app be treated as important.

At that point, the frontend will be reading a stable contract rather than improvising over multiple file types.

---

## What A Reviewer or Agent Should Analyze Next

Another agent reviewing this framework should focus on these questions:

1. Is the proposed `qa_run.json` contract sufficient?
2. What exact fields should be required versus optional?
3. What should the first `qa_prompt_library.yml` contain?
4. What should count as `pass`, `partial`, and `fail`?
5. How should benchmark and clarification cases be evaluated?
6. Should the batch runner score runs automatically, manually, or hybrid?
7. Which current known failure modes should be encoded first as QA cases?

---

## Known Current Signals From Recent QA

Recent Groq-backed QA suggests:

- ranking works well
- trend works well
- distribution works, but may miss optional highlight context
- growth may use a valid precomputed growth metric instead of the explicit growth template
- benchmark behavior is the weakest and needs more targeted QA
- clarification behavior should be preserved and reviewed, not discarded

This means benchmark and clarification cases should be emphasized in the first formal QA library.

---

## Immediate Recommendation

Before building more frontend:

1. define the canonical `qa_run.json` schema
2. define the first `qa_prompt_library.yml`
3. define the pass/partial/fail scoring rules
4. build the batch runner

After those exist, a QA frontend will be much easier to build correctly.
