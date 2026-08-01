# Industry Section Closeout Plan

**Last updated:** 2026-07-29  
**Scope:** Remaining work to close out the current `industry/` spec after first-pass D1, D2, D3, D4 ingest, and D5 implementation  
**Primary goal:** Give a new agent a concrete execution plan for finishing the remaining deliverables without having to reconstruct the section history from scratch

## What is already done

The following are already built in first pass and should be treated as existing surfaces to extend, not rebuild:

- `D1` current mix + change-over-time
- `D1` specialization companion
- `D2` tract/county spatial views
- `D3` job centers and internal employment pull
- `D4` job-center interpretation layer
- `D4` OSM/Overture ingestion + cached overlay reader
- `D5` regional fit and peer benchmarking

The remaining closeout work is concentrated in:

- `D6` AI exposure setup and scorecard
- cross-deliverable validation, copy, and spec closeout

## Recommended build order

Work in this order unless the user explicitly reprioritizes:

1. `D6` sector exposure scorecard
2. `D6` occupation exposure companion
3. final validation, copy pass, and spec checkbox cleanup

Why this order:

- `D1` specialization and `D4` interpretation are now in place, so the remaining net-new analytical work is concentrated in `D6`.
- `D6` is still the largest remaining build, so it is safer to split it into sector first, occupation second.

## Level of effort

Approximate remaining effort for one focused agent:

- `D4` interpretation: `3–5` working days
- `D1` specialization: `1–2` working days
- `D6` sector + occupation exposure: `4–7` working days
- validation and closeout: `1–2` working days

Expected total: roughly `9–16` working days depending on how clean the first-pass exposure joins are.

## Guardrails

- Treat Richmond as the proving ground, but keep every prep path parameterized by `market_id`.
- Do not rebuild D2/D3/D5 from scratch; extend the existing `data_prep.py` and page patterns.
- Keep D4 first-pass interpretation on simple geometric buffers and feature counts/flags.
- Do not present D4 proximity as travel-time or network access.
- Do not add LODES OD work in this closeout pass.
- Keep Felten appendix inputs as section-owned reference data in first pass unless the user explicitly asks to promote them into Foundations now.

## Deliverable plan

### Phase 1 — D4 job-center interpretation

**Goal:** Turn the current D4 overlay into an analytical interpretation layer for the job centers surfaced in D3.

**Files to inspect first**

- `metro-deep-dive/metro-area-explorer/industry/SPEC.md`
- `metro-deep-dive/metro-area-explorer/industry/data_prep.py`
- `metro-deep-dive/metro-area-explorer/industry/pages/d3_job_centers.py`
- `metro-deep-dive/metro-area-explorer/industry/pages/d4_infrastructure_overlay.py`
- `metro-deep-dive/metro-area-explorer/industry/POI_INFRA_PROPOSAL.md`
- `metro-deep-dive/metro-area-explorer/industry/RICHMOND_POI_INFRA_REVIEW.md`

**Build tasks**

- Define a reusable D3 job-center shortlist payload in `data_prep.py`.
- Build a tract-enrichment prep layer for the shortlist using simple buffers around shortlisted tracts or tract centroids.
- Count or flag nearby:
  - highways
  - rail
  - airport features
  - port features
  - warehouse/logistics polygons
  - hospitals
  - universities
  - schools
  - groceries
- Create a first-pass interpretation heuristic that labels a tract as one of:
  - infrastructure/logistics-led
  - institutional
  - office/professional
  - mixed
- Add a D4 review table or card surface that presents the shortlist, counts/flags, and interpretation before the map.
- Keep the current D4 map as companion context rather than the primary output.
- Add copy that states the method is geometric proximity and that network-access analysis is a future follow-on.

**Verification**

- Confirm D4 still renders when one or more spatial layers are empty.
- Confirm D4 can run fully from cached outputs without re-querying sources.
- Confirm the interpretation surface updates from the same market-scoped cache and D3 shortlist.
- Do a Richmond visual review and check whether the resulting tract reads are actually editorially useful for S04.

**Definition of done**

- D4 produces a tract-level interpretation surface, not just a layer browser.
- A new user can tell why a tract looks institutional, logistics-led, office-heavy, or mixed without reading raw manifests.
- The page makes no network-access claims.

### Phase 2 — D1 specialization companion

**Status:** Complete on 2026-07-29

**Goal:** Extend D1 so the explorer supports the Richmond `S04a` specialization spine rather than only mix and change.

**Files to inspect first**

- `metro-deep-dive/metro-area-explorer/industry/SPEC.md`
- `metro-deep-dive/metro-area-explorer/industry/data_prep.py`
- `metro-deep-dive/metro-area-explorer/industry/pages/d1_makeup_change.py`

**Build tasks**

- Add prep logic for latest-year sector specialization using `lq_*` fields from `gold.economics_industry_wide`.
- Compute recent employment growth using the latest two comparable QCEW years when available.
- Build an LQ-vs-growth companion view for the employment basis.
- Add a fallback ranked specialization table when LQ is available but the growth pair is not.
- Add short copy tying specialization back to the current mix and change story.

**Verification**

- Confirm the specialization view uses the same sector taxonomy as the existing D1 employment view.
- Confirm missing growth history falls back cleanly to the table rather than erroring.
- Confirm Richmond renders both the chart and fallback paths correctly if inputs are toggled or sparse.

**Definition of done**

- D1 now answers both “what is large?” and “what is specialized?”
- The page can support downstream S04a composition without requiring a second specialization-only prep path elsewhere.

### Phase 3 — D6 sector exposure scorecard

**Status:** Complete on 2026-07-30

**Goal:** Build the first half of the AI exposure setup so the explorer can produce the sector scorecard needed downstream in Richmond S04a.

**Files to inspect first**

- `metro-deep-dive/metro-area-explorer/industry/SPEC.md`
- `metro-deep-dive/metro-area-explorer/industry/data_prep.py`
- `metro-deep-dive/markets/richmond_va/SPEC.md`
- `foundations/etl/gold/gold_economics_occupation_wide.sql`
- `foundations/data_dictionary/layers/gold/gold__economics_occupation_wide.md`

**Build tasks**

- Decide and document the section-local storage path for Felten appendix inputs if it does not already exist.
- Join sector employment share and specialization context to the Felten industry appendix scores.
- Build the first-pass sector scorecard with:
  - sector
  - employment share
  - specialization context
  - AI exposure score
  - optional policy/context flags if implemented in the same pass
- Add synthesis linking high-exposure sectors back to D1 specialization and D3/D4 job-center interpretations.

**Verification**

- Confirm sector joins are coverage-checked and unmatched rows are surfaced transparently.
- Confirm the scorecard does not silently mix sector- and occupation-level logic.
- Confirm Richmond produces a usable first-pass scorecard without Richmond-only hardcoding.

**Definition of done**

- D6 sector output is strong enough that downstream Quarto work does not need to rebuild the entire scorecard scaffold.

### Phase 4 — D6 occupation exposure companion

**Status:** Complete on 2026-07-30

**Goal:** Finish the second half of D6 by adding the detailed occupation-level exposure view using OEWS.

**Files to inspect first**

- `metro-deep-dive/metro-area-explorer/industry/SPEC.md`
- `metro-deep-dive/metro-area-explorer/industry/data_prep.py`
- `foundations/etl/silver/bls_oews_silver.R`
- `foundations/data_dictionary/layers/silver/silver__bls_oews.md`

**Build tasks**

- Pull detailed SOC rows from `silver.bls_oews` for CBSA markets.
- Join detailed occupation rows to the Felten occupation appendix.
- Build a ranked exposure table or chart for occupations by exposure and employment relevance.
- Add a lighter family summary that uses `gold.economics_occupation_wide` where useful for compact context.
- Write synthesis that explains how occupation exposure complements, rather than duplicates, the sector scorecard.

**Verification**

- Confirm D6 clearly distinguishes sector-level and occupation-level exposure.
- Confirm SOC join coverage is reported.
- Confirm the page stays usable if some SOC rows are unmatched or suppressed.

**Definition of done**

- D6 produces both a sector scorecard and an occupation companion that are analytically connected and coverage-transparent.

### Phase 5 — Validation and closeout

**Goal:** Close the section cleanly once the remaining analytical work lands.

**Build tasks**

- Add or update targeted tests for the D1 specialization logic, D4 interpretation logic, and D6 exposure joins.
- Run the industry test suite.
- Do one full Richmond visual QA pass across D1 through D6.
- Update `SPEC.md` acceptance checkboxes to reflect actual implementation state.
- Append `decisions.md` entries for each meaningful build pass.
- If anything remains intentionally deferred, say so explicitly in the spec and page copy rather than leaving ambiguous partial work.

**Verification**

- Programmatic validation passes for the changed pages and prep logic.
- Visual review confirms the pages read as one coherent section rather than isolated widgets.
- The remaining open decisions in `SPEC.md` match reality.

## Suggested task breakdown for separate agent turns

If the work is split across multiple turns or agents, use this breakdown:

1. `D4 interpretation data prep`
2. `D4 interpretation page UI`
3. `D1 specialization prep + page`
4. `D6 sector exposure prep + page`
5. `D6 occupation exposure prep + page`
6. `tests + visual QA + spec checkbox cleanup`

Each turn should end with:

- updated `decisions.md`
- explicit verification notes
- any unresolved ambiguity added back to `SPEC.md` if it changes the contract

## What not to do in this closeout pass

- Do not ingest or model LODES OD.
- Do not promote OSM/Overture or Felten inputs into Foundations unless the user asks for that platform work specifically.
- Do not overcomplicate D4 with network-routing or accessibility metrics in first pass.
- Do not introduce a new sector taxonomy that breaks comparability across D1, D2, D4, and D5.
- Do not make Richmond-only assumptions in page logic or prep functions.

## Exit criteria for the section

The section is ready to call “substantially closed out” when:

- `D1` includes specialization context
- `D4` interprets job centers rather than only showing overlays
- `D6` exists as a usable first-pass exposure setup surface
- tests and visual review pass
- `SPEC.md` checkboxes and `Open decisions` accurately reflect the built state
