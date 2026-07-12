# Python vs R Parity Audit Framework

**Purpose:** run one broad, disciplined audit of `chart_engine_py` against the current R visual library before using Chart Engine CE runs as the main discovery path.

This is not a rendering sprint by itself. It is an audit sprint that produces a gap register, clear severity calls, and an execution order for follow-up fixes.

---

## Goal

For every chart type that exists in both systems, answer:

1. Does the Python chart spec describe the same contract as the R chart spec?
2. Does the Python prep function preserve the same business logic as the R prep function?
3. Does the Python render function produce the same visual semantics as the R render function?
4. Do theme defaults, labels, benchmarks, notes, and export behavior match closely enough for Python to be considered a real parity candidate?

The output of this audit is a written parity register, not just code opinions.

---

## Scope

Audit these 16 chart types:

- `bar_chart`
- `line_chart`
- `scatter`
- `slopegraph`
- `boxplot`
- `heatmap_table`
- `bump_chart`
- `waterfall`
- `strength_strip`
- `correlation_heatmap`
- `age_pyramid`
- `choropleth`
- `hexbin`
- `highlight_context_map`
- `proportional_symbol_map`
- `bivariate_choropleth`

Audit these layers for each chart type:

- spec parity
- prep parity
- render parity
- theme/default parity
- export/runtime parity
- question coverage parity

Do not broaden scope into chatbot integration, publisher runner automation, or speculative refactors.

---

## Source Of Truth

Treat the current R visual library as the reference implementation unless an intentional deviation is already documented.

Primary Python sources:

- `foundations/visual_library/chart_engine_py/chart_engine/chart_specs/`
- `foundations/visual_library/chart_engine_py/chart_engine/prep/`
- `foundations/visual_library/chart_engine_py/chart_engine/render/`
- `foundations/visual_library/chart_engine_py/chart_engine/pip_theme.yml`
- `foundations/visual_library/chart_engine_py/tests/`

Primary R sources:

- `foundations/visual_library/charts/<chart>/`
- `foundations/visual_library/shared/prep/`
- `foundations/visual_library/shared/render/`
- `foundations/visual_library/shared/`

Supporting docs:

- `foundations/visual_library/chart_engine_py/PLAN.md`
- `foundations/visual_library/chart_engine_py/SPEC.md`
- `publisher/PUBLISHER_ROADMAP.md`

---

## Required Outputs

Create or update these audit artifacts:

1. `foundations/visual_library/chart_engine_py/parity_audit/PARITY_REGISTER.md`
2. `foundations/visual_library/chart_engine_py/parity_audit/<chart_type>.md` for each audited chart type
3. `foundations/visual_library/chart_engine_py/parity_audit/EXECUTION_ORDER.md`

The audit is not complete until all three exist and are internally consistent.

---

## Folder Convention

Use this structure:

```text
foundations/visual_library/chart_engine_py/parity_audit/
├── PARITY_REGISTER.md
├── EXECUTION_ORDER.md
├── bar_chart.md
├── line_chart.md
├── scatter.md
├── slopegraph.md
├── boxplot.md
├── heatmap_table.md
├── bump_chart.md
├── waterfall.md
├── strength_strip.md
├── correlation_heatmap.md
├── age_pyramid.md
├── choropleth.md
├── hexbin.md
├── highlight_context_map.md
├── proportional_symbol_map.md
└── bivariate_choropleth.md
```

Do not create chart-specific scratch files elsewhere unless the user asks.

---

## Audit Workflow

Run the audit chart by chart, but keep findings normalized so they can be compared across the full library.

### Step 1: Establish the mapping

For each chart type, identify:

- Python spec file
- Python prep file
- Python render file
- R chart spec doc
- R question coverage doc
- R shared prep function
- R shared render function

If any expected source is missing, log that immediately as a parity gap instead of working around it.

### Step 2: Audit spec parity

Compare:

- required fields
- optional fields
- benchmark expectations
- variants
- documented QA rules
- documented canonical question types

Record whether the Python spec is:

- `match`
- `partial`
- `missing`
- `drifted`

### Step 3: Audit prep parity

Compare the prep layers for:

- column normalization
- filtering
- ranking / ordering
- benchmark derivation
- highlight logic
- subtitle/note propagation
- truncation behavior
- variant-specific transforms

Call out whether the Python prep is:

- functionally equivalent
- simplified but acceptable
- missing required behavior
- materially different

### Step 4: Audit render parity

Compare:

- mark type and orientation
- sorting
- axis labeling
- direct labels
- benchmark lines or bands
- annotations
- legends
- captions / notes / methodology text
- facet behavior
- treatment of long labels
- behavior for negative values or diverging modes

Do not stop at “looks similar.” The question is whether the same story is being told with the same semantics.

### Step 5: Audit theme and defaults parity

Compare:

- fonts
- base dimensions
- title sizing
- subtitle behavior
- caption behavior
- palette defaults
- benchmark styling
- highlight styling
- grid behavior

If Python differs only because of a practical export/runtime limitation, document that explicitly.

### Step 6: Audit export/runtime parity

Check:

- HTML render behavior
- PNG export behavior
- SVG export behavior if relevant
- known `vl-convert` or matplotlib limitations
- missing font/runtime dependencies

Separate “visual library logic gap” from “environment/export gap.”

### Step 7: Audit question coverage parity

Compare the Python surface against the R chart’s documented question coverage.

Answer:

- Which R question patterns are already supported in Python?
- Which are missing?
- Which are only partially supported?

### Step 8: Assign severity and ownership

Every gap must get:

- severity
- layer
- recommended fix location

Allowed severities:

- `blocking`
- `major`
- `minor`
- `acceptable`

Allowed layers:

- `spec`
- `prep`
- `render`
- `theme`
- `export`
- `tests`
- `docs`

---

## Severity Rules

Use these rules consistently.

`blocking`
- Python cannot tell the same story as R for the chart’s primary use case.
- Export path drops critical text or marks.
- Required benchmark, ordering, or label behavior is absent.
- Contract mismatch means the CE/manual run would produce misleading output.

`major`
- Core chart is usable but materially weaker than R.
- Important context like note text, annotations, or highlight behavior is missing.
- One or more canonical question patterns from the R chart are unsupported.

`minor`
- Semantics are basically correct, but polish or secondary behavior differs.
- Theme, sizing, legend placement, or truncation differs without changing interpretation.

`acceptable`
- Difference is intentional, documented, and low-risk.
- Difference is runtime-specific but does not alter the analytical story.

---

## Per-Chart Audit Template

Each `parity_audit/<chart_type>.md` should use this structure:

```md
# <chart_type>

## Source Map
- Python spec:
- Python prep:
- Python render:
- R spec:
- R question coverage:
- R prep:
- R render:

## Verdict
- Overall parity status: `blocking | major | minor | acceptable`
- Primary missing layer:
- Recommended fix order:

## Spec Parity
- Match:
- Gaps:

## Prep Parity
- Match:
- Gaps:

## Render Parity
- Match:
- Gaps:

## Theme / Defaults Parity
- Match:
- Gaps:

## Export / Runtime Parity
- Match:
- Gaps:

## Question Coverage Parity
- Supported:
- Partial:
- Missing:

## Gap Register
- [severity] [layer] short title
  Evidence:
  Why it matters:
  Fix location:

## Recommended Follow-Up
- First:
- Second:
- Later:
```

Keep entries concise but concrete. Evidence should cite files and behaviors, not vague impressions.

---

## Master Register Template

`PARITY_REGISTER.md` should include:

1. A summary table with one row per chart type
2. A gap count by severity
3. A gap count by layer
4. A short section on repeated cross-chart problems
5. A short section on audit assumptions and known limits

Recommended summary table:

| Chart type | Overall status | Primary gap layer | Blocking gaps | Major gaps | Notes |
|---|---|---:|---:|---:|---|

Recommended repeated-problems section headings:

- repeated spec drift
- repeated prep drift
- repeated render drift
- repeated theme drift
- repeated export/runtime drift

This is the document the user should be able to read first.

---

## Execution Order Rules

`EXECUTION_ORDER.md` should group fixes by leverage, not by the order the audit was performed.

Recommended sections:

1. Shared cross-chart fixes first
2. High-volume chart families second
3. Single-purpose chart types third
4. Validation sequence through CE/manual runs last

Prioritize in this order:

1. shared export/runtime issues
2. shared theme/default issues
3. `bar_chart` and `line_chart`
4. other high-reuse analytical charts
5. map and single-purpose charts

The point is to fix repeated problems once before attacking tail cases.

---

## Agent Instructions

Use these instructions for the agent running the audit:

1. Read this file completely before starting.
2. Read `PLAN.md` Phase 5 and `PUBLISHER_ROADMAP.md` CE track before writing findings.
3. Treat the R implementation as the parity reference unless a deviation is already documented.
4. Do not start fixing code during the audit pass unless the user explicitly changes scope.
5. Do not collapse multiple gaps into a single vague note. Log each materially distinct gap separately.
6. Prefer concrete evidence from code and rendered behavior over general statements.
7. When uncertain whether something is a true gap, classify it as a question in the chart’s audit file rather than silently deciding.
8. If a missing behavior appears across multiple chart types, log it once in the chart files and again in the master repeated-problems section.
9. If you find a chart type where Python is ahead of R in a clearly beneficial way, note it, but do not automatically classify R as wrong.
10. Stop after the audit packet is complete. Do not begin implementation work.

---

## Stop Conditions

The audit agent should stop and hand back work when:

- all 16 chart files have been audited
- `PARITY_REGISTER.md` exists and summarizes them
- `EXECUTION_ORDER.md` exists and prioritizes follow-up
- the docs state any assumptions or unresolved questions clearly

The audit agent should also stop early if:

- key source files needed for comparison are missing
- the R reference path is too ambiguous to establish parity responsibly
- a required manual artifact is unavailable and blocks a credible comparison

In that case, log the blocker in the master register instead of guessing.

---

## What Success Looks Like

Success is not “everything is fixed.”

Success is:

- we know exactly where Python differs from R
- we know which gaps are structural versus cosmetic
- we know which shared fixes unlock the most parity fastest
- the later CE/manual runs can be used as validation instead of discovery
