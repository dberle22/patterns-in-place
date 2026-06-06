# QA Tuning Log

Tracks every QA loop: what was fixed, what cases changed, and what to fix next.

---

## Loop Scoreboard

| Loop | Date | Cases | Pass | Partial | Fail | Notes |
|------|------|-------|------|---------|------|-------|
| Loop 1 | 2026-04-30 | 10 | 2 | 6 | 2 | Baseline run. 10-case suite. |
| Loop 2 | 2026-05-01 | 10 | 5 | 4 | 1 | Bar chart sort fixed. Distribution answer improved. |
| Loop 3 | 2026-05-02 | 20 | 10 | 6 | 4 | Suite expanded to 20 cases. New templates added. |
| Loop 4 | 2026-05-08 | 20 | — | — | — | Fix implementation and validation pass completed; review loop not logged here. |
| Loop 5 | 2026-05-11 | 20 | 15 | 3 | 2 | Most chart/data paths are stable; remaining issues are parser defaults, growth semantics, comparison framing, and outlier handling. |

---

## Case Trend Table

Each cell shows the review outcome: ✅ pass · ⚠️ partial · ❌ fail · — not in suite

| Case ID | Question | Loop 1 | Loop 2 | Loop 3 | Loop 5 |
|---------|----------|--------|--------|--------|--------|
| qa_b_001 | Compare Florida's population to the US in 2024 | ⚠️ partial | ⚠️ partial | ❌ fail | ⚠️ partial |
| qa_b_002 | How does Texas household income stack up against the national average? | ⚠️ partial | ⚠️ partial | ❌ fail | ❌ fail |
| qa_b_003 | Is California's median home value above the US average in 2024? | ❌ fail | ❌ fail | ❌ fail | ❌ fail |
| qa_c_001 | What are the fastest growing places? | ❌ fail | ⚠️ partial | ⚠️ partial | ✅ pass |
| qa_c_002 | Show me how income compares | ✅ pass | ✅ pass | ✅ pass | ✅ pass |
| qa_r_001 | Which states had the highest total population in 2024? | ⚠️ partial | ✅ pass | ✅ pass | ✅ pass |
| qa_r_002 | What are the top 10 metros by median household income in 2024? | ⚠️ partial | ✅ pass | ✅ pass | ✅ pass |
| qa_t_001 | Show housing unit growth over time in California, Texas, and Florida. | ✅ pass | ✅ pass | ✅ pass | ✅ pass |
| qa_t_002 | How has median household income changed over time for states between 2015 and 2024? | ⚠️ partial | ⚠️ partial | ✅ pass | ✅ pass |
| qa_d_001 | Show the distribution of state home values in 2024. | ⚠️ partial | ✅ pass | ✅ pass | ✅ pass |
| qa_d_002 | What does the spread of median household income look like across states in 2024? | — | — | ✅ pass | ✅ pass |
| qa_d_003 | Show how vacancy rates are distributed across metros in 2023. | — | — | ✅ pass | ✅ pass |
| qa_g_001 | Which states had the fastest population growth over 5 years ending in 2024? | — | — | ⚠️ partial | ✅ pass |
| qa_g_002 | What are the fastest-growing states by population over the last five years? | — | — | ⚠️ partial | ⚠️ partial |
| qa_g_003 | Which metros had the biggest gains in median household income over the past 5 years? | — | — | ❌ fail | ❌ fail |
| qa_g_004 | Rank states by housing unit growth since 2019. | — | — | ⚠️ partial | ✅ pass |
| qa_g_005 | Which places are growing the fastest? | — | — | ✅ pass | ✅ pass |
| qa_comp_001 | Compare California, Texas, and Florida on median household income in 2024. | — | — | ⚠️ partial | ✅ pass |
| qa_comp_002 | How do New York, Illinois, and Washington compare on median home values in 2024? | — | — | ⚠️ partial | ✅ pass |
| qa_comp_003 | Show me a side-by-side comparison of population trends for Austin, Nashville, and Raleigh. | — | — | ✅ pass | ⚠️ partial |

---

## Loop 1 — 2026-04-30

**Score: 2 pass / 6 partial / 2 fail (10 cases)**

### What Was Learned

- **Bar chart sort order inverted** — ranked charts rendered with the highest value at the bottom. Affects qa_r_001 and qa_r_002.
- **Benchmark template completely broken** — qa_b_001 ran but compared Florida only to itself (wrong shape). The US level has no row in the source table and there was no reference benchmark table yet.
- **Unnecessary clarification on benchmark paraphrases** — qa_b_002 and qa_b_003 both triggered clarification even though geo and metric were named in the question.
- **"Places" not recognized as a geo level** — qa_c_001 asked for places and got an unnecessary clarification instead of routing to `geo_level=place`. Reviewer also noted that when no specific geography is given, the system should default to all geographies rather than clarifying.
- **Clarification message language is too technical** — qa_c_002 correctly asked for clarification but the message exposed internal field names (`geo_level`, `geo_ids`, `year`) that a non-technical user would not understand. Language should map to plain English equivalents.
- **Answer text never analyzes the data** — qa_d_001 and qa_t_002 showed correct data but the answer text described nothing from the result. Distribution should call out top, bottom, and median. Trend should name the leading geography.
- **Default Florida highlight in distribution chart** — qa_d_001 had Florida highlighted as a reference state with no reason tied to the question. Highlight should only appear when a specific geography was named in the prompt.
- **Result preview sort unhelpful for time-series** — qa_t_001 passed but the 5-row result preview in `qa_run.json` showed rows from only one geography because data was not sorted by year first. For trend results the preview should sort by year then geo_name.
- **qa_t_001 passed cleanly** — multi-geo trend line end-to-end was solid on first run.

### Fixes Applied Before Loop 2

- [x] Fixed bar chart sort order so highest value renders at the top of horizontal bars (`sort_desc=TRUE` wired through to R renderer).
- [x] Added `place` / `places` / `cities` / `city` / `towns` / `town` geo level patterns to `_infer_geo_level` in `parser.py`.
- [x] Improved `ResponseAssembler` distribution branch to call out top, bottom, and median values.
- [x] Created `gold.benchmark_reference` ETL view (`etl/gold/benchmark_reference_view.sql`) and began populating US-level reference rows for ranking metrics.
- [x] Removed hardcoded Florida default highlight from distribution chart renderer.
- [x] Fixed result preview sort order in `build_qa_run_json` to sort by year then geo_name when `has_time_series=True`.
- [ ] Clarification message language — plain-English field name mapping deferred. qa_c_002 continued to pass so this was not blocking. Tracked as Fix 2C in Loop 4 plan.

---

## Loop 2 — 2026-05-01

**Score: 5 pass / 4 partial / 1 fail (10 cases)**

### What Was Learned

- **Bar chart sort fix confirmed** — qa_r_001 and qa_r_002 moved from partial to pass. ✅
- **Distribution answer fix confirmed** — qa_d_001 moved from partial to pass. ✅
- **Benchmark still broken across all three qa_b cases.**
  - qa_b_001 regressed from partial → unnecessary clarification. The parser now correctly identifies it as benchmark but the named geo "Florida" is not being extracted to populate `target_geo_id`.
  - qa_b_002 still asks for unnecessary clarification. LLM extracts intent correctly but falls through to clarification because `year` is missing and the heuristic fallback uses `calc_income_pc` instead of `median_hh_income`.
  - qa_b_003 still fails — intent is classified as ranking, not benchmark. Heuristic does not detect "above the US average" as a benchmark signal consistently.
- **qa_t_002 answer still vague** — passes data/chart but answer text does not surface any insight from 51-state trend.
- **Clarification language still technical** — not addressed before Loop 2. qa_c_002 continues to pass (the clarification is appropriate) but the message wording remains internal-facing. Carried forward to Loop 4 Fix 2C.

### Fixes Applied Before Loop 3

- [x] Strengthened `_benchmark_signals` in `_heuristic_parse`: added "above the" + ("average" OR "us" OR "national") pattern.
- [x] Improved `_infer_target_geo_id` to also set `target_geo_level="state"` on the heuristic benchmark plan.
- [x] Added `median_hh_income` → `calc_income_pc` disambiguation note in the metric patterns (the LLM was choosing per-capita income for "household income" questions).
- [x] Expanded QA suite from 10 → 20 cases (added growth, comparison, distribution paraphrases).
- [x] Improved `ResponseAssembler` trend branch to name the leading geography at the final period.

---

## Loop 3 — 2026-05-02

**Score: 10 pass / 6 partial / 4 fail (20 cases)**

### What Was Learned

- **Distribution template is solid** — qa_d_001, qa_d_002, qa_d_003 all pass cleanly.
- **Ranking and trend templates stable** — qa_r_001, qa_r_002, qa_t_001, qa_t_002 all pass.
- **Comparison template mostly works** — qa_comp_003 (multi-geo trend) passes; qa_comp_001 and qa_comp_002 are partial only because the answer text gives no insight.
- **Growth queries mostly work** — qa_g_001 and qa_g_005 run correctly; chart for qa_g_001 is broken because growth percentages display as near-zero.
- **Benchmark still broken** — qa_b_001 now errors with empty result set (progressed from clarification → it attempts to run but `benchmark_reference` lacks `pop_total` at US level). qa_g_003 also errors with empty result (CBSA income growth returns no rows).
- **Unnecessary clarification still a pattern** — qa_b_002, qa_b_003, qa_g_002, qa_g_004 all ask for things already present in the question. Main triggers: missing `year` default on benchmark, "last N years" not resolving to a concrete date, "since YYYY" not extracting start year, `question_type` appearing as an exposed field.
- **Comparison answer text is a placeholder** — qa_comp_001 and qa_comp_002 both say "The result summarizes X for the requested comparison." No data is surfaced.
- **Percentage formatting bug on growth bar charts** — `growth_value` is a decimal ratio (e.g., 0.126) but `_label_style` returns "number" because it reads from the base metric's `unit_format`, not the growth result column. Bars render as near-zero.

---

## Loop 4 — Fix Plan

**Target: 20 cases → 16+ pass**

The four fix areas below are ordered by expected impact.

### Verification Status — 2026-05-08

- [x] Fix 1 validated in code and runtime data: benchmark SQL includes reference-plus-inline fallback, `gold.benchmark_reference` contains `us` `pop_total` rows, and CBSA `median_hh_income` growth returns non-empty 2019→2024 results.
- [x] Fix 2 validated in parser behavior: benchmark questions default to `year=2024`, relative phrases like "over the last five years" resolve to `end_year=2024`, and "since 2019" growth questions infer `window_years=5` without clarification.
- [x] Fix 3 validated in chart config/render path: growth queries force `label_style="percent"` in Python, and the R bar renderer routes percent labels through `format_value_vector(..., style = "percent")`.
- [x] Fix 4 validated in response assembly: comparison answers now name the leader and gaps, and benchmark answers explicitly state whether the target is above or below the benchmark.
- [x] Validation pass completed with `.venv/bin/python -m unittest tests.test_pipeline.test_loop4_fixes -v` on 2026-05-08.

---

### Fix 1 — Benchmark Empty Results

**Failing cases: qa_b_001, qa_g_003**
**Root cause:** The `_benchmark_cte_from_reference` queries `gold.benchmark_reference` but that table lacks rows for `pop_total` at `benchmark_level='us'`. Similarly, the growth template on CBSA-level `median_hh_income` returns 0 rows (either missing CBSA income data for the 5-year window, or wrong metric ID resolved).

- [ ] Run `SELECT DISTINCT benchmark_level, metric_id, source_table FROM metro_deep_dive.gold.benchmark_reference` — confirm which metrics are covered at the `us` level.
- [ ] Update `etl/gold/benchmark_reference_view.sql` to include `pop_total` aggregated at `benchmark_level='us'` so qa_b_001 can find a US row.
- [ ] Add a fallback in `_render_benchmark` ([app/query/generator.py:188](app/query/generator.py)) — if `benchmark_type='us'` and `_benchmark_cte_from_reference` returns 0 rows, fall back to `_benchmark_cte_inline` computing `AVG()` at `geo_level='us'` from the source table directly.
- [ ] Debug qa_g_003 — run the growth SQL manually for `geo_level='cbsa'`, `base_metric_id='median_hh_income'`, `end_year=2024`, `window_years=5`. Confirm CBSA income data covers both 2019 and 2024. If the 5-year lag is all NULL, add a `window_years=3` fallback retry in the orchestrator.
- [ ] Confirm `_default_growth_metric` ([app/intent/parser.py:487](app/intent/parser.py)) resolves "biggest gains in median household income" to `median_hh_income` (not `calc_income_pc`) when `geo_level='cbsa'`.

---

### Fix 2 — Unnecessary Clarifications

**Failing cases: qa_b_002, qa_b_003, qa_g_002, qa_g_004**
**Root cause:** Three distinct sub-issues in the parser.

**A. Missing year default on benchmark**
- [ ] In `_hydrate_plan_defaults` ([app/intent/parser.py:566](app/intent/parser.py)), add `payload.setdefault("year", 2024)` for `template_id="benchmark"`. Year should never be a clarification field for benchmark — default to the latest data year.

**B. Relative date phrases not resolving to concrete years**
- [ ] Extend `_infer_latest_year_reference` ([app/intent/parser.py:551](app/intent/parser.py)) to return `2024` when the question contains phrases like "last N years", "past N years", "over the last", "over the past". This gives a default `end_year` without asking.
- [ ] For "since YYYY" growth questions (qa_g_004 "since 2019"), add a regex `r"\bsince\s+(20\d{2})\b"` to the heuristic growth branch ([app/intent/parser.py:403](app/intent/parser.py)) to extract `start_year` and compute `window_years = end_year - start_year`.

**C. `question_type` exposed as a clarification field**
- [ ] Remove `question_type` from the fields that can appear in `missing_fields`. It is an internal concept. If ambiguous, default to `"ranking"` rather than asking the user ([app/intent/parser.py:559](app/intent/parser.py)).
- [ ] Confirm "rank" and "ranked" in a question trigger the growth-ranking path in `_infer_question_type` ([app/intent/parser.py:454](app/intent/parser.py)).

---

### Fix 3 — Percentage Formatting on Growth Bar Charts

**Failing cases: qa_c_001 (chart), qa_g_001 (chart)**
**Root cause:** `_label_style` ([app/charts/renderer.py:246](app/charts/renderer.py)) reads the base metric's `unit_format` to decide label format. For growth queries, `base_metric_id` is a count metric (e.g., `pop_total` with `unit_format='integer'`), so it returns "number". But `growth_value` is a ratio (0.126) that must display as a percentage (12.6%).

- [ ] In `_label_style` ([app/charts/renderer.py:246](app/charts/renderer.py)), add: `if query_plan.template_id == "growth": return "percent"` before the `unit_format` lookup. Growth results are always a ratio regardless of the base metric.
- [ ] Verify the R `bar_value_labeler` in [visual_library/shared/render/render_bar.R](visual_library/shared/render/render_bar.R) correctly applies `scales::label_percent()` (which multiplies by 100 and appends %) when `label_style = "percent"`. Trace through `format_value_vector` in `chart_utils.R` to confirm.

---

### Fix 4 — Comparison Answer Text Missing Insight

**Failing cases: qa_comp_001, qa_comp_002**
**Root cause:** The `else` catch-all in `ResponseAssembler.assemble` ([app/response/assembler.py:108](app/response/assembler.py)) handles `comparison` question type with a static string: *"The result summarizes X for the requested comparison."* No data is read.

- [ ] Add a dedicated `comparison` branch in `ResponseAssembler.assemble` ([app/response/assembler.py:106](app/response/assembler.py)). Sort the dataframe by `metric_value` descending. Name the top geography and its value. Express each other geography as a signed percent difference from the top (e.g., *"Texas leads at $73,035 — 12% above California ($65,149) and 18% above Florida ($61,777)."*).
- [ ] Also improve the `benchmark` answer branch ([app/response/assembler.py:106](app/response/assembler.py)) — read target vs benchmark rows from `comparison_group` column and state explicitly whether the target is above or below and by how much.

---

## Known Data-Layer Issues (Not LLM Fixes)

These were called out in reviews but are data or ETL problems, not pipeline logic.

| Issue | Observed In | Notes |
|-------|-------------|-------|
| Vacancy rate percentages stored inconsistently | qa_d_003 (Loop 3) | Some rows scaled 0–100, others 0–1. ETL standardization needed in the gold layer. |
| 51-state line chart unreadable | qa_t_002 (all loops) | Technically correct but visually unusable. Future: add a default entity limit (e.g., top 10) for time-series with no explicit geo filter, with a note to the user. |
| Outlier small places inflate growth rankings | qa_c_001, qa_g_005 | Very small-population places show extreme growth rates. Need a minimum population threshold filter in the growth template. |

---

## Loop 5 — 2026-05-11

**Score: 15 pass / 3 partial / 2 fail (20 cases)**

### What Was Learned

- **Core data and chart paths are now mostly stable** — ranking, trend, distribution, and most comparison cases pass cleanly.
- **Benchmark parsing is still the weakest parser area** — qa_b_002 and qa_b_003 should parse without clarification, but benchmark slot filling and yes/no benchmark phrasing are still brittle.
- **Some LLM parses are correct in raw form but fail during normalization/finalization** — qa_b_002, qa_g_002, and qa_g_003 all show `raw_llm_response` payloads with `clarification_needed=false`, yet the saved run ends up as clarification. This points to plan normalization or required-slot validation rather than pure intent failure.
- **Growth semantics still need cleanup** — qa_g_002 and qa_g_003 expose confusion between precomputed growth metrics, explicit growth templates, latest-year defaults, and household-vs-per-capita income mapping.
- **Comparison framing over time is still semantically off** — qa_comp_003 returns the right multi-metro trend data and chart, but the answer is written like a generic trend summary instead of a side-by-side comparison.
- **Outlier handling is now the main quality issue on place-level growth** — qa_c_001 and qa_g_005 pass operationally, but the results are still dominated by tiny places with implausibly large percentage changes.
- **“Metro” likely still maps too broadly to all CBSAs** — qa_r_002 passes structurally, but top results such as Los Alamos and Nantucket suggest metro/micro filtering may be mixed.
- **Wide trend charts need readability rules even when technically correct** — qa_t_002 passes, but a 52-line state chart is too dense to be useful without an automatic entity cap or display simplification.
- **QA artifact hygiene is messy** — several parsed runs still contain stale `clarification.json` files, which makes review harder because the artifact directory implies both outcomes at once.

### Fix Backlog From Loop 5

Priority order is parser and plan correctness first, then answer quality, then review ergonomics.

1. [x] **Normalize benchmark target slots from provider output** — provider benchmark payloads now map `geo_id` / `geo_level` onto `target_geo_id` / `target_geo_level` before validation so benchmark plans like qa_b_002 do not degrade into clarification during finalization.
2. [x] **Default benchmark and latest-period questions to the most recent year** — benchmark questions no longer clarify for missing `year`, and relative growth prompts like “over the last five years” resolve to `end_year=2024` automatically.
3. [x] **Strengthen benchmark detection for yes/no average phrasing** — benchmark fallbacks now still work when provider mode is forced but unavailable, so prompts like qa_b_003 can resolve through heuristics instead of collapsing into clarification.
4. [x] **Fix household income metric selection across growth logic** — growth inference now prefers `median_hh_income` when the user explicitly asks for household income instead of falling back to `calc_income_pc`.
5. [x] **Unify precomputed growth metrics with growth-template semantics** — provider plans that emit `pop_growth_5yr` or `income_pc_growth_5yr` now normalize into valid latest-period growth plans with `base_metric_id`, `end_year`, and `window_years`.
6. [x] **Separate comparison intent from trend rendering more clearly** — side-by-side over-time comparisons can now preserve comparison semantics while still rendering with the trend template, and the answer text reflects trajectory differences instead of only the final leader.
7. [x] **Make benchmark answers smarter for additive totals** — national-total benchmark answers like qa_b_001 now use share-of-US framing for additive metrics such as total population and housing units.
8. [x] **Add outlier controls for place-level growth rankings** — place-level growth SQL now filters out tiny-baseline places so extreme percentage spikes from very small denominators do not dominate qa_c_001 and qa_g_005.
9. [ ] **Filter “metros” to metro-only records** — still open. The current semantic layer does not expose a clean metro/micro classifier in the planner path, so this needs a data-model decision before code changes.
10. [x] **Add readability limits for large trend charts** — chart rendering now trims broad unfiltered trend views to the top 10 geographies by latest-period value while preserving the full query result for tables and QA artifacts.
11. [x] **Decide whether to prefer stored growth metrics or computed growth SQL** — current implementation standardizes on the growth template by converting provider-selected precomputed growth metrics into a computed growth plan, keeping downstream behavior consistent.
12. [x] **Clean up QA run artifacts on success** — successful parsed runs now remove stale `clarification.json` files so each run directory reflects a single final outcome.

### Suggested Next Execution Order

- **Phase 1: parser/planner correctness** — backlog items 1 through 5
- **Phase 2: answer and chart quality** — backlog items 6 through 10
- **Phase 3: architecture and QA hygiene** — backlog items 11 and 12
