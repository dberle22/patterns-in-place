# Chart Engine — Execution Plan

**Goal:** Ship an installable Python chart package first (`chart-engine`), then repackage the existing R implementation as `pip.charts`. Python is the real port and the first production target for the chatbot, publisher, and Deep Dive. R is follow-on packaging work for the library that already exists in `shared/`.

**Working rules**
- `visual_library/charts/<type>/` and `visual_library/docs/visual_style_guide_and_standards.md` remain the human-authored source of truth.
- `chart_engine_py/chart_engine/chart_specs/*.md` are generated machine-readable artifacts.
- `visual_library/shared/` keeps running during the migration and is not replaced in-place.
- Python ships first. R repackaging starts after the Python package shape is proven.

---

## Status Snapshot

### Overall milestones
- [x] Phase 1 complete: Python theme and shared standards layer is stable
- [x] Phase 2 complete: generated Python specs exist for all 16 chart types
- [x] Phase 3 complete: Python prep/render coverage exists for all 16 chart types
- [x] Phase 4 complete: Python tests are in place and reliable
- [ ] Phase 5 complete: manual publisher content runs pass visual review
- [ ] Phase 6 complete: chatbot and publisher are wired to `chart_engine_py`
- [ ] Phase 7 complete: Python package is publishable
- [ ] R repackaging complete

### Current package status
- [x] Core request/orchestrator/registry skeleton exists
- [x] `bar_chart` and `line_chart` exist in Python
- [x] Phase 1 Python theme, formatter, caption, and packaged theme groundwork has started
- [x] Python test harness exists
- [x] Generated spec workflow exists
- [x] Remaining 5 Python chart types exist
- [ ] Real consuming-app integration exists

---

## Task Board

### Phase 1 — Python Theme and Standards

**Goal:** every Python render function reads from the same theme, formatter, and caption system before we add more chart types.

**Deliverables**
- [x] Expand `chart_engine/theme.py` into a semantic theme object
- [x] Add `chart_engine/formatters.py`
- [x] Add `chart_engine/captions.py`
- [x] Add packaged default theme file `chart_engine/pip_theme.yml`
- [x] Export the Phase 1 public helpers from `chart_engine/__init__.py`
- [x] Update existing examples to use the packaged default theme
- [x] Move `render/bar.py` and `render/line.py` onto the Phase 1 helper surface cleanly enough that they become templates for the rest of the port
- [x] Remove any remaining placeholder theme assumptions from existing Python renderers
- [x] Confirm packaged-data loading works in an editable install
- [x] Confirm render import path works without a nonessential front-matter dependency
- [x] Add a first Python test harness before porting more chart types

**Verification**
- [x] `py_compile` passes for the touched Python files
- [x] `pip install -e foundations/visual_library/chart_engine_py` works in a clean environment
- [x] A smoke test can import `Theme.default()` and render `bar_chart` and `line_chart`
- [x] A first `unittest` suite runs cleanly against the current package

**Notes**
- The spec loader now parses generated YAML front matter directly, so Phase 1 no longer depends on `python-frontmatter` at runtime.
- Altair regression coverage now uses shared deterministic fixtures in `tests/fixtures.py` and committed goldens under `tests/golden/`.
- Geo chart coverage now uses pure-Python geometry helpers plus lazy matplotlib imports, so the package can still import and validate cleanly in environments that do not yet have plotting extras installed.
- Supported dependency bounds are now pinned to the validated range in `pyproject.toml`: `altair>=4.2,<5` and `pandas>=2,<3`.
- Editable install and full test discovery both pass in the repo's Python 3.12 environment (`.venv312`) when run with a writable `MPLCONFIGDIR`.
- Phase 5 prep cleanup is in place: Matplotlib-backed charts now fall back cleanly when `Inter` is not installed locally, and the bivariate choropleth no longer relies on a `tight_layout()` call that emitted warnings during regression runs.

---

### Phase 2 — Generated Specs and Data Contracts

**Goal:** every Python chart type has a package-local runtime spec generated from the human-authored chart docs.

**Shared workflow tasks**
- [x] Decide where the spec-generation script lives
- [x] Write the spec-generation script
- [x] Document the spec-generation workflow in this folder README or plan notes
- [x] Ensure generated specs are easy to diff and deterministic
- [x] Ensure generated specs are treated as artifacts, not hand-edited files

**Chart spec tasks**
- [x] `bar_chart`
- [x] `line_chart`
- [x] `scatter`
- [x] `slopegraph`
- [x] `boxplot`
- [x] `heatmap_table`
- [x] `bump_chart`
- [x] `waterfall`
- [x] `strength_strip`
- [x] `correlation_heatmap`
- [x] `age_pyramid`
- [x] `choropleth`
- [x] `hexbin`
- [x] `highlight_context_map`
- [x] `proportional_symbol_map`
- [x] `bivariate_choropleth`

**Verification**
- [x] Every registry entry points to a generated spec file that loads successfully
- [x] Regenerating specs without source changes produces no diff

---

### Phase 3 — Python Prep and Render Port

**Goal:** port the remaining chart types into Python using the new standards layer.

**Parity rollout model (updated)**
- We are no longer treating parity closure as strictly one chart per turn.
- Shared infrastructure lands first when the same gap repeats across chart types.
- Chart-family follow-up comes second:
  - ranking/comparison
  - trend/comparison
  - matrix/distribution
  - demographic/map
- Chart a Day becomes the refinement and QA layer after the shared code paths exist.

**Shared infrastructure**
- [ ] Create final Python renderer folder structure: `prep/`, `charts/`, `geo/`
- [ ] Add shared Altair helper module
- [ ] Add shared matplotlib/geopandas helper module
- [ ] Move existing bar and line renderers from `render/` into `charts/`
- [ ] Update `registry.py` to point at the final module layout

**Altair chart tasks**
- [x] `bar_chart`
- [x] `line_chart`
- [x] `scatter`
- [x] `slopegraph`
- [x] `boxplot`
- [x] `heatmap_table`
- [x] `bump_chart`
- [x] `waterfall`
- [x] `strength_strip`
- [x] `correlation_heatmap`
- [x] `age_pyramid`

**Matplotlib / geo chart tasks**
- [x] `choropleth`
- [x] `hexbin`
- [x] `highlight_context_map`
- [x] `proportional_symbol_map`
- [x] `bivariate_choropleth`

**Per-chart checklist**
- [ ] Generate package spec
- [ ] Port prep function
- [ ] Port render function
- [ ] Register chart in `registry.py`
- [ ] Add or update example fixture data if needed
- [ ] Add chart-level tests before moving to the next type

**Recommended build order**
1. [x] `scatter`
2. [x] `slopegraph`
3. [x] `boxplot`
4. [x] `heatmap_table`
5. [x] `bump_chart`
6. [x] `waterfall`
7. [x] `strength_strip`
8. [x] `correlation_heatmap`
9. [x] `age_pyramid`
10. [x] `choropleth`
11. [x] `hexbin`
12. [x] `highlight_context_map`
13. [x] `proportional_symbol_map`
14. [x] `bivariate_choropleth`

**Verification**
- [x] Each completed chart renders successfully from a fixed fixture input
- [x] Each completed chart uses theme defaults rather than hardcoded styles

---

### Phase 4 — Python Tests

**Goal:** make the Python package safe to extend chart by chart.

**Harness tasks**
- [x] Create `tests/` folder structure
- [x] Choose an initial test runner and workflow
- [x] Add fixture organization for sample input data
- [x] Add golden output storage convention

**Core test files**
- [x] `test_contracts.py`
- [x] `test_registry.py`
- [x] `test_orchestrator.py`
- [x] `test_skill.py`

**Chart coverage tasks**
- [x] `bar_chart` golden test
- [x] `line_chart` golden test
- [x] `scatter` golden test
- [x] `slopegraph` golden test
- [x] `boxplot` golden test
- [x] `heatmap_table` golden test
- [x] `bump_chart` golden test
- [x] `waterfall` golden test
- [x] `strength_strip` golden test
- [x] `correlation_heatmap` golden test
- [x] `age_pyramid` golden test
- [x] `choropleth` snapshot/structural test
- [x] `hexbin` snapshot/structural test
- [x] `highlight_context_map` snapshot/structural test
- [x] `proportional_symbol_map` snapshot/structural test
- [x] `bivariate_choropleth` snapshot/structural test

**Verification**
- [x] Core tests pass
- [x] Golden tests are stable across reruns
- [x] Matplotlib tests use tolerant snapshots or structural assertions rather than brittle exact pixel hashes

---

### Phase 5 — Manual Publisher Content Runs

**Goal:** prove the Python package works against real content before wiring it into consuming apps, using the current R visual library output as the parity reference on every manual run.

**Parity audit prerequisite**
- [x] Run the broad Python-vs-R parity audit described in `PARITY_AUDIT_FRAMEWORK.md`
- [x] Create `parity_audit/PARITY_REGISTER.md`
- [x] Create `parity_audit/EXECUTION_ORDER.md`
- [x] Create one per-chart audit file for all 16 chart types
- [ ] Review the audit findings before treating CE runs as parity validation instead of discovery

**Post-audit implementation progress**
- [x] Close the shared spec-body generation gap in `scripts/generate_chart_specs.py`
- [x] Align the packaged Python theme font default with the R standard
- [x] Add `line_chart` golden regression coverage and close the highest-risk `line_chart` prep/render parity tranche
- [x] Close the `age_pyramid` benchmark/facet parity tranche
- [x] Extend visible Altair caption handling across the regression-backed analytical charts touched in this pass
- [x] Expand `bar_chart` beyond ranked-only rendering with diverging and stacked composition support
- [x] Close the `scatter` single-geo-level prep guardrail and add opt-in reference-line/quadrant/highlight controls
- [x] Add shared prep helper infrastructure for repeated field-selection and type-guard patterns
- [x] Add shared Altair render helper infrastructure for repeated variant and reference-line behavior
- [x] Close the `slopegraph` parity tranche with request-driven prep config, variant handling, curated entity selection, and richer subtitle/label behavior
- [x] Advance the ranking/comparison family across `bump_chart` and `strength_strip` with shared comparison metadata, selection, and benchmark semantics
- [x] Advance the matrix/distribution family across `boxplot`, `heatmap_table`, `waterfall`, and `correlation_heatmap` with shared matrix ordering, benchmark/facet composition, and richer regression coverage
- [x] Advance the map family across `choropleth`, `highlight_context_map`, `proportional_symbol_map`, and `bivariate_choropleth` with shared map variants, facet semantics, and stronger geo test coverage
- [x] Close the `hexbin` specialized tail with weight validation, request-driven filtering, faceted comparison rendering, and stronger geo coverage

**Handoff sprint**
- [x] Publisher handoff sprint has been defined in `publisher/docs/chart_engine_py_handoff_sprint.md`
- [x] Chart Engine CE-0 queue scaffold exists under `publisher/chart_a_day/`
- [x] Chart Engine CE-1 manual skill prompts exist under `publisher/chart_a_day/skills/`

**Manual run tracker**
- [ ] `q001` — `bar_chart` parity run (`ranking`)
- [ ] `q002` — `bar_chart` parity run (`ranking`)
- [ ] `q003` — `bar_chart` parity run (`ranking`)
- [ ] `q004` — `line_chart` parity run (`trend`)
- [ ] `q005` — `line_chart` parity run (`trend`)
- [ ] `q006` — `line_chart` parity run (`trend`)
- [ ] `q007` — `bar_chart` parity run (`compare_selected`)
- [ ] `q008` — `line_chart` parity run (`compare_selected`)
- [ ] `q009` — `boxplot` parity run (`distribution`)
- [ ] `q010` — `boxplot` parity run (`distribution`)
- [ ] `q011` — `bar_chart` parity run (`benchmark`)
- [ ] `q012` — `bar_chart` parity run (`benchmark`)
- [ ] `q013` — `bar_chart` parity run (`growth`)
- [ ] `q014` — `bar_chart` parity run (`growth`)
- [ ] `q015` — `bar_chart` parity run (`ranking`)
- [ ] `q016` — `scatter` parity run (`correlation`)
- [ ] `q017` — `slopegraph` parity run (`rank_change`)
- [ ] `q018` — `bump_chart` parity run (`rank_change`)
- [ ] `q019` — `heatmap_table` parity run (`composition`)
- [ ] `q020` — `waterfall` parity run (`composition`)
- [ ] `q021` — `strength_strip` parity run (`benchmark` / `composition`)
- [ ] `q022` — `correlation_heatmap` parity run (`correlation`)
- [ ] `q023` — `age_pyramid` parity run (`demographic`)
- [ ] `q024` — `choropleth` parity run (`map`)
- [ ] `q025` — `highlight_context_map` parity run (`map`)
- [ ] `q026` — `proportional_symbol_map` parity run (`map`)
- [ ] `q027` — `bivariate_choropleth` parity run (`map`)
- [ ] `q028` — `hexbin` parity run (`correlation`)

Legacy `status: ran` entries in `backlog.yaml` do not automatically count as complete here. Check an item off only when the dual-render workflow has produced both the R reference artifact and the Python parity artifact, and the parity review has been logged.

**Vacancy rate content run tasks**
- [ ] Install `chart_engine_py` in editable mode
- [ ] Run `metro_rankings` through both stacks and save `chart_r.*` plus `chart_py.*`
- [ ] Run `national_trend` through both stacks and save `chart_r.*` plus `chart_py.*`
- [ ] Run `regional_trends` through both stacks and save `chart_r.*` plus `chart_py.*`
- [ ] Save output artifacts for review
- [ ] Record issues and fixes needed, classifying each Python gap by `spec`, `prep`, `render`, `theme`, or export

**Second-content validation**
- [ ] Pick one housing content question that exercises a different chart type
- [ ] Build the `ChartRequest` by hand
- [ ] Render and save both the R reference chart and the Python parity chart
- [ ] Review against `question.md`, `findings.md`, and the R reference output

**Verification**
- [ ] Python charts match the visual hypothesis in the content docs
- [ ] Python charts match the current R reference closely enough to be considered parity candidates
- [ ] Benchmarks appear where expected in both outputs
- [ ] Axis labels, captions, and formatting are acceptable in the Python output
- [ ] Someone reading the findings would recognize the Python chart as the same story as the R chart

**Notes**
- CE-0 and CE-1 are complete in `publisher/`: the backlog, queue scaffold, and manual prompt skills are in place, and the first real Phase 5 proof point is now the CE-2 manual run for `q003` (fallback `q006` if the Gold data is missing).
- The shared semantic chart rules remain chatbot-compatible for now, so the manual Chart Engine prompt normalizes legacy `bar` / `line` rule outputs to `bar_chart` / `line_chart` only when calling the Python package. Full catalog normalization waits for Phase 6 / CH-1 when the chatbot swaps off the R renderer.
- Phase 5 now uses a dual-render workflow: every manual content run should emit an R reference chart and a Python parity candidate from the same result set, with the differences logged explicitly. The question is not just "does Python render?" but "does Python match the current visual contract closely enough to replace R for this chart/question pair?"

---

### Phase 6 — Integration: Chatbot and Publisher

**Goal:** replace app-specific chart wiring with `chart_engine_py`.

**Chatbot tasks**
- [ ] Audit current chart selection and render path
- [ ] Replace R subprocess rendering bridge with Python `render()`
- [ ] Replace chart selector logic with `question_to_chart_request()`
- [ ] Ensure result profiler still feeds the skill correctly
- [ ] Validate HTML chart output in the chatbot UI

**Publisher tasks**
- [ ] Audit current chart packaging flow
- [ ] Call `question_to_chart_request()` after `QueryExecutor`
- [ ] Route output persistence through `OutputConfig`
- [ ] Embed chart output in publisher output directly
- [ ] Validate at least one real packaged run end to end

**Verification**
- [ ] Chatbot renders charts without shelling out to R
- [ ] Publisher packaging works without the old chart bridge
- [ ] One end-to-end run in each consumer is reviewed successfully

---

### Phase 7 — Publish Python Package

**Goal:** make the Python package installable, documented, and releasable.

**Packaging tasks**
- [ ] Choose final package name
- [ ] Add public `README.md`
- [ ] Add `CHANGELOG.md`
- [ ] Review package metadata and dependencies
- [ ] Confirm packaged assets include specs and theme file

**CI/CD tasks**
- [ ] Add Python test workflow
- [ ] Add release workflow
- [ ] Validate versioning approach
- [ ] Tag `v0.1.0`

**Verification**
- [ ] Fresh install works
- [ ] Examples run from the installed package
- [ ] Release flow is documented

---

## R Repackaging Backlog

**Goal:** package the existing R implementation after the Python package shape is stable.

**Scaffolding**
- [ ] Create `chart_engine_r/`
- [ ] Add `DESCRIPTION`
- [ ] Add roxygen/NAMESPACE workflow
- [ ] Add `README.md`

**Code migration**
- [ ] Flatten package source under `R/`
- [ ] Port theme/palette/formatter/caption/config helpers
- [ ] Port prep files
- [ ] Port chart files
- [ ] Port geo files

**Tests**
- [ ] Add `testthat` harness
- [ ] Add contract tests
- [ ] Add prep tests
- [ ] Add render tests
- [ ] Add `vdiffr` snapshots

**Verification**
- [ ] Package loads
- [ ] Representative charts render
- [ ] Package layout is valid for normal R tooling

---

## Immediate Next Tasks

- [ ] Start the Chart a Day parity QA loop with `q001` to `q015`
- [ ] Continue the Chart a Day parity QA loop across `q016` to `q028`, including the new `hexbin` path
- [ ] Log analytical or visual drift discovered in QA as refinement work instead of reopening the structural parity tranche

---

## Change Log For This Plan

- [x] Reframed the plan as a task board with checkboxes and verification gates
- [x] Split Python-first execution from the later R repackaging backlog
- [x] Broke chart work into per-type tasks so progress can be ticked off visibly
