# Visual Library Agent

## Purpose
Define how an agent should help build and refine chart types in the visual library using the workflow patterns that worked well for bar and line charts.

The agent should optimize for:

- starting from the chart contract, not ad hoc implementation
- improving shared chart functions before patching sample scripts
- using real DuckDB-backed sample data for review
- producing reviewable PNG outputs early and often
- moving repeated styling or logic into shared standards

## Recommendation
This should behave like an implementation-oriented chart builder with built-in QA, not a general research assistant and not a fully autonomous pipeline runner.

The agent should:

1. read the chart spec and question coverage first
2. align shared `prep_<chart>.R` and `render_<chart>.R` functions to the spec and standards
3. build one real sample query per canonical business question
4. create or update a sample runner with explicit query, prep, render, and export blocks
5. render PNG outputs for review
6. iterate based on correctness and visual QA
7. promote repeated decisions into shared defaults when appropriate

## Roles
- `User`
  - chooses the chart type and sets the priority
  - reviews business meaning, output quality, and design tradeoffs
  - approves non-obvious organization decisions or workflow changes
- `Agent`
  - builds and updates chart assets
  - keeps implementation aligned to specs and standards
  - validates chart input data before rendering
  - produces reviewable outputs and summarizes decisions
  - recommends when logic belongs in chart-local code vs shared code

## Operating Principles
- Start from the chart contract:
  - Read the chart spec and `question_coverage.md` before changing code.
- Improve the shared layer first:
  - Prefer updating `prep_<chart>.R` and `render_<chart>.R` before adding one-off logic in the test harness.
- Use real sample data:
  - Build DuckDB-backed queries tied to canonical business questions.
- Keep review artifacts explicit:
  - Each sample output should have a visible query block, prep block, render block, and export path.
- Render early:
  - PNG review is part of implementation, not a final afterthought.
- Standardize repeated decisions:
  - If a styling or palette choice starts repeating, move it toward `visual_library/shared/` instead of solving it chart by chart.
- Preserve chart-specific nuance:
  - Do not over-generalize defaults that only fit one chart variant.

## Preferred Workflow

### 1. Confirm chart type and create the workspace
- Confirm the target chart type and intended scope.
- Ensure the chart folder exists at `visual_library/charts/<chart_type>/`.
- Ensure expected starter structure exists:
  - `<chart_type>_spec.md`
  - `question_coverage.md`
  - `sample_sql/`
  - `sample_output/`
  - `test_<chart_type>_render.R`
- Path rule:
  - keep executable runners at chart root, for example `visual_library/charts/<chart_type>/test_<chart_type>_render.R`
  - keep review artifacts in `sample_output/`, including PNGs and optional review markdown
  - do not introduce a second generic `output/` folder for the same chart unless there is a documented non-review publishing workflow
- Create a chart-local decisions file when the implementation requires chart-specific notes or tradeoffs.

### 2. Read the governing docs first
- Read:
  - the chart spec
  - `question_coverage.md`
  - `visual_style_guide_and_standards.md`
  - `sample_library.md` when chart-family guidance is needed
- Summarize the implementation target:
  - chart variants to support
  - required contract fields
  - canonical business questions
  - likely reusable patterns from nearby chart types

### 3. Update shared chart functions
- Adjust `prep_<chart>.R` to match the chart contract.
- Adjust `render_<chart>.R` to match visual standards.
- Prefer changes that improve reuse across canonical question patterns.
- Watch for changes that should move into shared defaults, palettes, subtitle helpers, benchmark helpers, or standards-aware config.

This step should usually cover:

- filtering and selection rules
- ordering or ranking logic
- benchmark or comparison handling
- metadata needed for rendering
- title, subtitle, caption, and unit behavior
- spacing, margins, labels, legends, and baseline defaults

### 4. Build sample SQL for canonical questions
- Build one real DuckDB-backed query per canonical business question.
- Save chart-specific SQL in `sample_sql/`.
- Prefer sample queries that make the chart contract and review intent obvious.
- When data constraints require a workaround, document it in the chart folder.

### 5. Build or update the sample runner
- Create or update `test_<chart_type>_render.R`.
- Structure it so each business question has:
  - a query block
  - a prep block
  - a render block
  - an export path
- Validate the dataframe contract before rendering.
- Save outputs into `sample_output/` with stable names that are easy to review.
- If a chart already has legacy outputs in `output/`, migrate or replace them so one chart does not maintain both `output/` and `sample_output/` for the same review workflow.

### 6. Run and inspect outputs
- Run the sample runner end to end.
- Review the rendered PNGs against the business questions and the spec.
- Use the outputs to iterate on:
  - data correctness
  - metric scaling
  - title, subtitle, and caption wording
  - axis and baseline behavior
  - spacing, labels, and legend placement
  - readability of highlight, peer, and benchmark treatment

### 7. Standardize what repeats
- If a decision starts repeating across chart types, move it into shared infrastructure when that improves maintainability.
- Good candidates include:
  - palette defaults
  - benchmark colors
  - subtitle and caption helpers
  - theme defaults
  - config resolution helpers
- Keep chart-local behavior local when the logic is specific to one chart family or one variant.

### 8. Finalize chart artifacts
- Confirm the folder structure is clean and consistent.
- Confirm sample SQL and output files are in the intended locations.
- Update documentation or chart decisions notes where useful.
- Confirm the chart can be rerun end to end from the chart folder workflow.

## Review Checkpoints For The User
The agent should not stop after every small step. Instead, it should pause for user input at the points where human judgment matters most:

1. after the first spec-aligned implementation target is summarized, if scope is unclear
2. after the first set of rendered PNGs is available for review
3. when a change appears to belong in shared standards rather than chart-local code
4. when organization or file-placement choices have non-obvious downstream consequences

## Expected Artifacts Per Chart Type
- `<chart_type>_spec.md`
- `question_coverage.md`
- `sample_sql/build_<chart_type>_sample.sql` or multiple question-specific SQL files
- `test_<chart_type>_render.R`
- `sample_output/test_<chart_type>_business_questions.md` when maintaining a written review summary
- PNG outputs in `sample_output/`

## Reference Order
1. `README.md` for library navigation
2. chart spec and `question_coverage.md` for chart-specific contract
3. `visual_style_guide_and_standards.md` for cross-chart visual rules
4. `sample_library.md` for chart-family guidance
5. nearby chart folders for proven implementation patterns

## Agent Checklist
- chart type and scope confirmed
- chart workspace exists and is organized correctly
- spec and question coverage reviewed first
- shared prep and render functions updated before sample-runner patching
- one real sample query exists per canonical business question
- contract validation happens before rendering
- PNG outputs are generated for review
- repeated decisions are evaluated for promotion into shared standards
- chart-local decisions are documented when needed
- workflow runs end to end cleanly

## What Still Needs User Input
The agent can execute most of the workflow, but a few decisions still benefit from your direction:

- how strict the folder contract should be across all chart types
- whether every chart must maintain a written business-question review markdown file
- when to split sample SQL into multiple files vs one consolidated builder
- how aggressively to promote chart-specific improvements into `visual_library/shared/`
- whether the agent should work in a continuous iteration loop by default or pause after the first render set

## Agent Or Skill?
This workflow is closer to a skill than a standalone agent and has been migrated into the local Codex skill `visual-chart-builder`.

Local skill path:

- `~/.codex/skills/visual-chart-builder/SKILL.md`

Why:

- the work is procedural and repeatable
- it benefits from a strong checklist and clear step order
- the user still provides judgment on chart quality and tradeoffs
- the implementation usually happens inside the current coding session rather than as a long-running autonomous worker

A good practical model would be:

- `visual-chart-builder` as a skill that Codex uses when asked to build or refine a chart type
- optional narrower supporting skills for contract validation, visual QA, or function scaffolding

An agent only becomes the better abstraction if you want a reusable autonomous role that:

- owns multi-turn chart delivery across sessions
- manages several chart types in parallel
- enforces process state and approvals as part of a broader production workflow
