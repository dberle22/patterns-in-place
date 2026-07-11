# Chart Engine Python Handoff Sprint

**Owner:** next implementation agent in `publisher/`

**Purpose:** move `publisher` from the legacy R render bridge to validated use of `foundations/visual_library/chart_engine_py` without losing the existing content workflow while the migration is still being proven.

## Sprint Outcome

At the end of this sprint:

- manual Publisher content runs have been exercised against the Python chart package
- known gaps are written down with concrete fixes or deferrals
- the automated `chatbot/` render path has a clear migration shape
- we know whether `publisher` is ready for the actual renderer swap in Phase 6

This sprint is a handoff sprint, not a packaging sprint. The goal is to prove the consuming app path in `publisher/`.

## Current State

- `foundations/visual_library/chart_engine_py/` exists and all 16 chart types have Python coverage
- package tests are passing in `.venv312`
- `publisher/chatbot/charts/renderer.py` still renders through an R subprocess bridge
- `publisher/content/` still documents the manual R render path
- Phase 5 and Phase 6 in `chart_engine_py/PLAN.md` are the remaining migration steps that matter here

## Scope

### In scope

- manual content validation inside `publisher/content/`
- a migration design for `publisher/chatbot/charts/renderer.py`
- identifying contract mismatches between Publisher-shaped data and `chart_engine_py`
- documenting exact follow-up work required for the actual renderer cutover

### Out of scope

- publishing the Python package externally
- repackaging the R chart library
- broad refactors across unrelated Publisher modules
- changing editorial questions or rewriting content strategy

## Success Criteria

- at least one real Publisher content topic runs through the Python chart path
- the vacancy workflow has reviewed artifacts for `metro_rankings`, `national_trend`, and `regional_trends`
- one additional topic or question exercises a non-vacancy chart type
- a migration recommendation exists for each current R-backed chart type in `publisher/chatbot/charts/renderer.py`
- the sprint leaves behind clear checked tasks, not just notes

## Working Assumptions

- `.venv312` is the validated Python environment unless the user explicitly changes that decision
- `chart_engine_py` remains the source of the Python render implementation
- `publisher` should consume `chart_engine_py` directly rather than copying render logic locally
- the R render path remains available as fallback until the Python path is visually accepted

## Task Board

### Phase A — Publisher Readiness

**Goal:** make sure a new agent can run the migration work without rediscovering setup details.

- [ ] Confirm `FOUNDATIONS_PATH` and any required Publisher env vars for local runs
- [ ] Confirm `chart_engine_py` editable install works from the active Publisher environment
- [ ] Write down the exact command set for rerunning chart-engine tests and manual Publisher checks
- [ ] Identify which current Publisher docs still describe R-only rendering and mark them for update

**Verify**

- [ ] Another agent could reproduce the setup without asking where the package lives

### Phase B — Manual Content Proving Runs

**Goal:** prove the package against the manual Publisher content workflow before touching the automated renderer.

**Vacancy runs**

- [ ] Audit `publisher/content/vacancy_rates/` to confirm the expected outputs and chart types
- [ ] Run `metro_rankings` through the Python chart path
- [ ] Run `national_trend` through the Python chart path
- [ ] Run `regional_trends` through the Python chart path
- [ ] Save rendered artifacts in a reviewable location
- [ ] Compare Python output against the existing content intent and note any visual regressions

**Second validation case**

- [ ] Pick one non-vacancy content question under `publisher/content/housing/`
- [ ] Prefer a chart type that is not just `bar` or `line`
- [ ] Build the request payload by hand from the real content result shape
- [ ] Render with `chart_engine_py`
- [ ] Record whether the package contract matches the content workflow cleanly

**Verify**

- [ ] Titles, subtitles, labels, captions, and benchmark behavior are acceptable
- [ ] The chart still tells the intended story from `question.md` and `findings.md`

### Phase C — Chatbot Render Path Audit

**Goal:** define the exact work needed to replace the R bridge safely.

- [ ] Review [`publisher/chatbot/charts/renderer.py`](../chatbot/charts/renderer.py) end to end
- [ ] List every chart type currently supported by the R bridge
- [ ] Map each supported Publisher chart type to the Python registry equivalent
- [ ] Identify data-shaping logic in `_prepare_dataframe()` that should stay in Publisher vs move into chart-engine prep
- [ ] Identify config fields in `_build_config()` that need a `ChartRequest` equivalent
- [ ] Note any R-only behavior that does not yet have a Python analogue

**Verify**

- [ ] There is a concrete migration table for chart type, data prep, config mapping, and blockers

### Phase D — Integration Design

**Goal:** leave behind an implementation-ready plan for the actual Phase 6 swap.

- [ ] Propose the narrowest first cut for replacing the R renderer
- [ ] Decide whether to keep a temporary dual-renderer switch during rollout
- [ ] Define the minimal adapter layer from `ChartSelection` + `QueryPlan` + dataframe into `chart_engine_py`
- [ ] Identify where output artifacts should be saved so Publisher behavior stays stable
- [ ] Define what automated regression should exist before removing the R subprocess path

**Verify**

- [ ] Another agent could start coding the renderer swap from the sprint output alone

### Phase E — Documentation and Handoff

**Goal:** close the sprint with a clean package of evidence and next actions.

- [ ] Update this sprint file with completed checks and short notes
- [ ] Add a short migration summary to `foundations/visual_library/chart_engine_py/PLAN.md`
- [ ] Update Publisher docs that are now misleading about Python vs R rendering
- [ ] Leave a final recommendation: proceed to Phase 6 now, or hold for more manual review

**Verify**

- [ ] The repo contains both the evidence and the recommendation for the next agent

## Deliverables

- reviewed manual-run artifacts
- a chart-type migration table for the automated renderer
- documentation updates in `publisher/` and `chart_engine_py/PLAN.md`
- a go or no-go recommendation for the renderer cutover

## Suggested Execution Order

1. Environment and doc readiness
2. Manual vacancy proving runs
3. One non-vacancy proving run
4. Chatbot render-path audit
5. Integration design write-up
6. Final recommendation

## Files The Next Agent Will Likely Touch

- [`publisher/chatbot/charts/renderer.py`](../chatbot/charts/renderer.py)
- [`publisher/content/README.md`](../content/README.md)
- [`publisher/content/vacancy_rates/README.md`](../content/vacancy_rates/README.md)
- `foundations/visual_library/chart_engine_py/PLAN.md`
- `publisher/content/housing/**/visuals/*`

## Known Risks To Watch

- Publisher’s current render config shape may not map one-to-one onto `ChartRequest`
- some content workflows may rely on R-side formatting assumptions that were never documented explicitly
- the automated renderer currently supports only a subset of chart types, so migration might uncover hidden one-off behavior
- visual acceptance may fail even when tests pass, especially for benchmark labeling and subtitle phrasing

## Recommended First Command Set

```bash
MPLCONFIGDIR=/tmp/mplconfig_chart_engine MPLBACKEND=Agg .venv312/bin/python -m unittest discover -s foundations/visual_library/chart_engine_py/tests -p 'test_*.py'
```

```bash
sed -n '1,260p' publisher/chatbot/charts/renderer.py
```

```bash
sed -n '1,220p' publisher/content/README.md
```

## Definition Of Done

This sprint is done when:

- the manual Publisher path has been exercised with Python renders
- the remaining migration work is reduced to a bounded implementation task
- the next agent does not need to reverse-engineer why the migration stopped here
