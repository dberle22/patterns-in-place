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
- [ ] `bar_chart` golden test
- [ ] `line_chart` golden test
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

**Goal:** prove the Python package works against real content before wiring it into consuming apps.

**Handoff sprint**
- [x] Publisher handoff sprint has been defined in `publisher/docs/chart_engine_py_handoff_sprint.md`

**Vacancy rate content run tasks**
- [ ] Install `chart_engine_py` in editable mode
- [ ] Run `metro_rankings`
- [ ] Run `national_trend`
- [ ] Run `regional_trends`
- [ ] Save output artifacts for review
- [ ] Record issues and fixes needed

**Second-content validation**
- [ ] Pick one housing content question that exercises a different chart type
- [ ] Build the `ChartRequest` by hand
- [ ] Render and save the chart
- [ ] Review against `question.md` and `findings.md`

**Verification**
- [ ] Charts match the visual hypothesis in the content docs
- [ ] Benchmarks appear where expected
- [ ] Axis labels, captions, and formatting are acceptable
- [ ] Someone reading the findings would recognize the chart as the same story

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

- [ ] Finish Phase 1 verification by running a real editable install with dependencies available
- [ ] Port `slopegraph` as the next Phase 3 chart on top of the new standards layer
- [ ] Add the first chart-output regression tests before porting too many more charts

---

## Change Log For This Plan

- [x] Reframed the plan as a task board with checkboxes and verification gates
- [x] Split Python-first execution from the later R repackaging backlog
- [x] Broke chart work into per-type tasks so progress can be ticked off visibly
