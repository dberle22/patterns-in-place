# Industry Explorer — v1 Review Fix Plan

**Last updated:** 2026-08-09
**Scope:** Remediation plan following the first full walkthrough of the Industry section explorer (D1–D6), Richmond as spotlight market
**Primary goal:** Give an agent a concrete execution plan to close the v1 review findings without re-deriving the review from chat history

## Phase 0 — Baseline archive

**Status:** complete on 2026-08-08

Before any remediation work begins, preserve the current workbook app as the comparison baseline for the development series.

- Archived the live section app from `metro-deep-dive/metro-area-explorer/industry/` to `metro-deep-dive/archive/metro-area-explorer/industry_v0_2026-08-08/`
- Preserved the section-local app shell, page modules, prep code, specs, reference data, and cached outputs so v0 can be run and compared against v1 later
- Excluded runtime clutter only: `__pycache__/` and `.DS_Store`

**Use:** treat the archived copy as read-only unless we explicitly discover the snapshot itself is incomplete.

## Purpose decision — read this first

This plan was restructured after the v1 review resolved a question the original build never answered: **what is this app for?**

**Decision: the Industry explorer is a research workbench, not a reader-facing artifact.** It exists so the author can surface claims worth writing about, and so the research apparatus itself can be described and shipped. Reader-facing outputs are built downstream from what the workbench finds — they are not this.

**The done bar follows from that:**

- Does it surface claims that can be written from?
- Can the numbers be trusted?

It is explicitly **not** "is this presentable to a stranger." The sole user is the author.

**Three consequences that reorder everything below:**

1. **Correctness outranks polish.** A workbench that lies is worse than one that is ugly. Wrong counts and stale joins go first; pixel-level layout work is only in scope where it blocks the author's own reading.
2. **The one-question guardrail does not apply here.** That guardrail governs shipped artifacts. A workbench is permitted a broad orienting question — *where does this market fit into the broader US regional economy* — and is permitted many entry points into it.
3. **D6 does not belong in this app.** AI exposure is a specific question with its own entry point and its own geographic arc (regional → market → submarket). It is a report, not a tab. Five deliverables share the workbench purpose and the sixth does not — which is most of why the section read as six pages rather than one thing.

**What this decision retires:** the original Phase 5 "decide what D4 claims." A workbench is allowed an exploratory surface without a thesis. D4's manifest panel is appropriate for this audience and its road-network density is tolerable. What remains is that its counts are wrong — a correctness item, not a scope decision.

## Context

This plan follows `CLOSEOUT_PLAN.md`, not replaces it. That plan covered building the remaining deliverables. This plan covers what the first end-to-end review of the built section found.

The headline finding: **almost nothing in the review was an analytical failure.** The analytical substance was validated nearly everywhere. What failed was correctness in a small number of places, and legibility in many.

The second finding: **complaints reported page-by-page are systemic issues.** They must be fixed once, centrally, not six times per page:

| Systemic issue | Surfaces on | Correct fix location |
|---|---|---|
| Tract IDs are not human-readable | D2, D3, D4 | One tract→place label crosswalk in prep |
| Charts clipped by narrow side-by-side columns | D1, D5, D6 | Page layout convention |
| Legends render color codes, not colors | D2, D3 | Chart engine / map legend builder |
| Tooltips have competing schemas | D4 | Single hover contract |
| Metrics have no benchmark | D6 (and implicitly D2/D3) | Reuse the D5 peer set |

The third finding: **the views praised without qualification are the Richmond `S04a` spine** — D1 specialization, D3 sector share of local jobs, D5 peer comparison, D6 sector scorecard.

## Guardrails

- Keep every prep path parameterized by `market_id`. Richmond remains the proving ground, not a target.
- Fix systemic issues once at the shared layer. Do not patch the same defect independently on each page.
- **Judge every task against the workbench done bar.** If a task only makes the app nicer for a hypothetical stranger, it is out of scope. Say so and move on.
- Do not present D4 buffer proximity as travel time or network access.
- Do not add LODES OD work in this pass.
- Do not build a second application in this pass. The Economics-app question is recorded as deferred.
- Do not invent an occupation taxonomy. Use SOC major groups.
- Where a finding is deferred rather than fixed, say so explicitly in `SPEC.md` and in page copy rather than leaving ambiguous partial work.
- Append a `decisions.md` entry for each meaningful build pass.

## Recommended build order

1. Phase 0 — Baseline archive
2. Phase 1 — Correctness pass
3. Phase 2 — Reading blockers
4. Phase 3 — Tract legibility crosswalk
5. Phase 4 — D6 extraction
6. Phase 5 — Workbench instruments
7. Phase 6 — Validation and spec closeout

Why this order: archive first so the current workbook remains available as a stable v0 comparison point for the development write-up. Correctness comes next because an untrustworthy workbench is worse than an unpolished one. Legibility follows because it gates honest evaluation of everything else. Extraction fourth because D6 needs the corrected data from Phase 1 before it leaves. Instruments last because they add claim-generating capacity to a surface that should already be trustworthy and readable.

## Level of effort

- Phase 1 — correctness: `1–2` working days
- Phase 2 — reading blockers: `1` working day
- Phase 3 — tract legibility: `1–2` working days
- Phase 4 — D6 extraction: `1–2` working days for the extraction itself
- Phase 5 — workbench instruments: `4–8` working days if built in full
- Phase 6 — validation and closeout: `1` working day

Expected total for Phases 1–4 and 6: roughly `5–9` working days. Phase 5 is separable and should be taken partially.

---

## Phase 1 — Correctness pass

**Goal:** Make the workbench trustworthy. Nothing else matters until this is done.

**Progress note — 2026-08-08 build pass 1**

- Completed: D4 tract enrichment now counts distinct nearby entities instead of raw cached geometry rows, and it no longer uses noisy Overture `port` / infrastructure POIs for first-pass infrastructure counts
- Completed: D5 no longer treats CBSA jobs-to-workers as the broad comparison benchmark; the comparison slot now uses market-level GDP and income context across the selected peer set
- Completed: D3 no longer promotes CBSA jobs-to-workers as a top-line metric, while tract-grain ratio interpretation remains intact
- Completed: D2 now explicitly treats jobs density as an all-jobs surface instead of implying it follows the sector selector
- Completed: D6 notes now name the Felten appendix / code-system split directly in page-facing prep notes
- Still open in Phase 1: D1 aggregated `sector_id` cleanup, explicit page-by-page vintage audit, and any additional D4 institutional-POI dedupe refinement if later review still finds the counts too busy

**Progress note — 2026-08-09 build pass 2**

- Completed: explicit vintage captions now appear on D1 benchmark context, D4 cached-overlay context, and D6 sector / occupation panels so the user no longer has to infer panel timing from surrounding copy
- Completed: D1 sector count now keys off displayed sector labels rather than internal sector IDs
- Still open in Phase 1: any deeper D4 institutional-POI dedupe refinement if later review still finds the shortlist counts too busy

**Files to inspect first**

- `metro-deep-dive/metro-area-explorer/industry/data_prep.py`
- `metro-deep-dive/metro-area-explorer/industry/SPEC.md`
- `foundations/data_dictionary/layers/gold/gold__economics_occupation_wide.md`
- the D4 buffer enrichment logic and the OSM/Overture cached overlay reader

**Build tasks**

- **D4 buffer counts — highest priority in the entire plan.** The interpretation panel reported `121` ports within a 2-mile buffer of a single Richmond tract. This is not plausible. Diagnose whether the counts are summing geometry fragments, multi-tagged features, or duplicated OSM/Overture entities rather than distinct facilities. Until resolved, treat every count in the D4 shortlist table as suspect.
- **D6 occupation match data.** Matched employment reports `77.9%`, believed to predate corrected match work already completed elsewhere. Trace whether the corrected data reaches this prep path; rerun the join and report resulting coverage. Do this before Phase 4 extraction so the report seed starts clean.
- **D6 sector join basis.** Confirm and document in-app whether the sector scorecard joins on NAICS via the Felten industry appendix (AIIE) or on SOC. Sector- and occupation-level logic must never be silently mixed.
- **Jobs-to-workers grain correction.** At CBSA level the ratio pins near `1.0` by construction — the review confirmed US and South Atlantic both read `1.0`. Demote it from D3 top-line metrics and remove it as the subject of the D5 benchmark table. Retain at tract grain, where it is informative. Record as a spec correction in `SPEC.md`.
- **D5 benchmark table replacement.** With jobs-to-workers demoted, populate that slot with market-level economic context: total GDP, GDP per capita, income measures. Keep these as context rows on an industry page.
- **D1 `sector_id` column.** Null throughout because these are aggregated sectors. Drop it.
- **D2 job-density scope.** Density is all-jobs but sits beneath an industry selector. Either make it respond to the selector or move it out from under it. Labeling alone is a patch.
- **Vintage labeling.** `SPEC.md` requires per-panel vintage labels because QCEW, BEA, LODES, and OEWS vintages do not align. This went unverified in review. Confirm every panel states its own source year, with particular attention to D5 where three sources sit side by side.

**Verification**

- D4 buffer counts are reproducible and match a manual spot-check of distinct facilities for at least one Richmond tract.
- D6 occupation coverage is reported from corrected data and stated in-app.
- Each exposure panel names its appendix and code system.
- No CBSA-grain jobs-to-workers figure appears as a headline metric.
- No panel implies a common vintage across sources.

**Definition of done**

- Nothing in the section displays a number the author cannot verify, and each remaining limitation is stated in page copy.

---

## Phase 2 — Reading blockers

**Goal:** Fix presentation defects that impede the author's own reading. Scoped tighter than the original plan — this is not a polish pass.

**Progress note — 2026-08-08 build pass 1**

- Completed: D1 current-mix chart now gets the full row, with takeaway stacked below instead of competing for width beside the primary chart
- Completed: D5 peer comparison now renders as a full-width vertical stacked bar chart instead of the tighter side-by-side presentation
- Completed: D4 map hover now uses one tooltip contract built per feature type, so the map no longer mixes tract fields with layer fields in one null-heavy tooltip
- Still open in Phase 2: shared legend swatch rendering for D2/D3 and the D6 responsive panel collision noted in the review

**Progress note — 2026-08-08 build pass 2**

- Completed: D2 and D3 legends now render visible color swatches instead of raw hex codes
- Completed: D6 occupation view no longer relies on the side-by-side table layout that was colliding below fullscreen width; the detailed ranking and family summary now stack vertically
- Phase 2 status: the specific reading blockers called out in this plan are now addressed in the live app

**Files to inspect first**

- `metro-deep-dive/metro-area-explorer/industry/app.py`
- `metro-deep-dive/metro-area-explorer/industry/pages/` (all page modules)
- the chart engine map/legend builder and its `chart_rules.yml`

**In scope**

- **Legends:** map legends render a color *code* rather than a swatch. Fix in the shared legend builder so D2 and D3 are both repaired by one change. This makes the maps unreadable, not merely unpolished.
- **D5 orientation:** rotate the peer comparison from horizontal bars to vertical bars at full width so peers sit side by side without vertical scrolling. Apply identically to the GDP-share view. Highest value-per-hour fix in the section.
- **D1 current-mix bar:** currently cut off roughly halfway. Give primary charts full container width and stack supporting copy below rather than beside.
- **D4 tooltips:** unify into a single hover contract. A tract hover currently returns GEOID, dominant sector, and workplace jobs with `layer_feature` and `layer_group` null; an infrastructure hover returns layer fields with tract fields blank. One tooltip should resolve what is under the cursor and render only relevant fields, with no null rows.
- **D6 responsive break:** detailed-occupation and family-summary panels collapse into each other below fullscreen width. Fix before extraction so the defect does not follow D6 out.

**Explicitly out of scope under the workbench standard**

- D1 truncated source label — cosmetic, author knows the source.
- D6 clipped manufacturing/mining axis label — cosmetic.
- D4 road-network density thresholds — tolerable for this audience.
- D4 manifest panel — appropriate for a workbench; leave it visible.

**Verification**

- Every map legend shows swatches; no raw color codes in the UI.
- D5 peer comparison is fully visible without scrolling at default peer-set size.
- D4 hover shows no null-valued fields regardless of what is hovered.

**Definition of done**

- No chart or map in the section is unreadable to the person using it.

---

## Phase 3 — Tract legibility crosswalk

**Goal:** Resolve the most-repeated complaint in the review with one build.

**Context:** Tract identity was flagged five separate times across D2, D3, and D4. This stays fully scoped despite the workbench standard — bare GEOIDs are not a unit the author thinks in either, which makes every tract-keyed table dead weight regardless of the quality of the data behind it.

**Progress note — 2026-08-09 build pass 1**

- Completed: pulled the official Richmond neighborhood boundary GeoJSON from the city's ArcGIS service into section-owned reference data for a bounded local areal-overlap fix
- Completed: added a Richmond-only tract labeling pass in shared prep that assigns each Richmond city tract the neighborhood with the largest polygon overlap, while preserving tract IDs as secondary context in the display label
- Completed: kept non-Richmond tracts transparent by falling back to county or independent-city naming instead of implying a governed tract-to-place crosswalk that does not yet exist
- Completed: added county boundary outlines to the D2, D3, and D4 tract maps so the tract surface has a stable metro frame
- Completed: applied the new tract display labels across D2, D3, and D4 map hovers, tract tables, D3 job-center copy, and the D4 shortlist/detail read
- Still open in Phase 3: a governed multi-market tract-to-place strategy remains deferred; this build is intentionally a Richmond-specific short-term fix rather than the final crosswalk architecture

**Files to inspect first**

- `metro-deep-dive/metro-area-explorer/industry/data_prep.py`
- existing tract-level geography assets in `foundations/`
- the D2, D3, and D4 page modules for every table and label surface keyed on tract

**Build tasks**

- Build a tract→place label crosswalk in prep, parameterized by `market_id`. Prefer an existing governed geography asset; fall back to a Census place or county-subdivision relationship file.
  Completed in this build as a Richmond-only areal-overlap label pass using official neighborhood polygons plus county / independent-city fallback elsewhere in the Richmond CBSA.
- Produce a display label leading with the human-readable place or neighborhood name, retaining the GEOID as secondary context.
  Completed in this build as `Neighborhood or county name (Tract ###)` style labels.
- Apply to every tract-keyed table and map hover across D2, D3, and D4: top mapped tracts, top tracts by total jobs, largest tract job centers, highest jobs-to-workers tracts, selected-sector workplace centers, and the D4 shortlist table.
  Completed in this build.
- Add county boundary outlines to the D2 and D3 tract maps so the tract surface has an orienting frame.
  Completed in this build, and extended to D4 as well so the overlay view shares the same geographic frame.
- Where a tract cannot be resolved, display the GEOID with an explicit unmatched marker rather than silently falling back.
  Partially completed in this build via transparent county / independent-city fallback and hover copy that states the label basis; a stronger unmatched marker should remain part of the longer-term governed crosswalk design.

**Verification**

- Crosswalk coverage is computed and reported; unmatched tracts are surfaced transparently.
- Richmond build status on Sunday, August 9, 2026: all `75` Richmond city tracts matched to a neighborhood by largest overlap; many are split tracts, so overlap share is now shown in hover/detail copy for transparency.
- Every tract-keyed table shows a place name.
- Completed for D2, D3, and D4 in this build.
- The crosswalk runs for a non-Richmond CBSA without modification.
- Deferred: this build intentionally stops at the Richmond-only areal-overlap fix because the repo still lacks a governed tract-to-place surface.

**Definition of done**

- Tract-level findings can be read and written from without a separate lookup.

---

## Phase 4 — D6 extraction

**Goal:** Move AI exposure out of the workbench and into the seed of its own report.

**Context:** AI exposure is a specific question with a different entry point and its own geographic arc — regional, then market, then submarket. It is the publishable output of theme one. Keeping it as a tab inside a general-purpose workbench mismatches the audience and is most of why the section read as six disconnected pages.

**Progress note — 2026-08-09 build pass 1**

- Completed: removed D6 from the live workbook shell so the Industry explorer now runs as a five-deliverable workbench again
- Completed: updated workbook shell copy to point D6 toward the separate notebook / report path rather than keeping a duplicate live workbook surface
- Deferred by explicit user direction: no additional D6 extraction or notebook/report implementation happened in this pass because another agent owns that downstream path

**Build tasks**

- Run Phase 1 corrections against D6 first so what leaves is clean.
- Extract the D6 prep logic into `foundations/` so both the future report and any residual app surface call the same functions rather than duplicating.
- Stand up a report stub — location and format to be confirmed with the user — carrying the sector scorecard and occupation companion as its starting content.
- **Carry the benchmarking requirement with it.** The scorecard currently reports professional services at `20.2%` of Richmond private employment, exposure `0.85`, LQ `1.19`. In isolation this means nothing; the finding only exists relative to peers. If peers run `30%`, Richmond is unremarkable; if `15%`, it is the story. This is the AI disruption thesis itself — the claim is not that Richmond is exposed but that it is *more* exposed than its peer set because it won the knowledge-economy transition.
- Reuse the D5 peer set rather than building a second peer mechanism. Factor the peer selection for reuse if it is not already.
- **Middle-grain occupation summary.** Four family buckets are too coarse; 598 detailed occupations are unusable. Implement SOC major groups. Confirm against the grouping Felten and comparable studies use — do not invent one.
- Reduce overplotting in the occupation bubble chart: render at middle grain by default with detail on demand, or filter to an employment relevance floor. Do not simply shrink the marks.
- Decide whether any exposure surface remains in the workbench. A minimal pointer is acceptable; a duplicate is not.
  Completed in this build as a shell-level pointer only: D6 no longer appears as a workbook page.

**Verification**

- Extracted functions are called from one place, not copied.
- Sector-level and occupation-level exposure remain clearly distinguished.
- The workbench no longer contains a full second copy of the exposure logic.

**Definition of done**

- Exposure work lives where its audience is, and the workbench is five coherent deliverables rather than five plus an orphan.

---

## Phase 5 — Workbench instruments

**Goal:** Add claim-generating capacity. These were surfaced by the v1 review through omission rather than complaint — none was raised as a defect; all of it is missing.

**Sequencing note:** every item here earns its place under the workbench standard because each generates claims that can be written from. Build in the order listed; stop when the theme timebox says stop.

**Files to inspect first**

- `foundations/etl/gold/gold_economics_industry_wide.sql`
- `foundations/data_dictionary/layers/gold/gold__economics_occupation_wide.md`
- `metro-deep-dive/metro-area-explorer/industry/data_prep.py`

**Progress note — 2026-08-09 build pass 1**

- Completed: added a D1 employment shift-share companion that decomposes private-employment change into national growth, industry mix, and local competitive effect
- Completed: added D1 wage context from BEA earnings totals divided by same-year QCEW employment so sector mix can be read alongside estimated earnings per job
- Completed: carried wage and diversification context into D5 by adding wages-per-private-job, compensation-per-private-job, and the existing Gold concentration HHI to the peer context panel
- Completed: added a GDP-basis specialization companion in D1 by deriving GDP location quotients from market share versus U.S. GDP share, with comparable-growth logic mirroring the employment companion
- Notes: the plan originally called for promoting these instruments into `foundations/`; this build implemented them in the section-owned prep layer first so the workbook can be reviewed immediately, with later promotion still available if we want these instruments shared more broadly

### 5A — Shift-share decomposition

**Why:** D1 shows mix and change. The standard economics move is decomposing employment change into national growth, industry mix, and local competitive effects. This is the single addition that most makes the section read as economic research rather than as a dashboard — which matters for how the apparatus itself reads, not only for what it shows.

**Build tasks**

- Implement standard three-component shift-share on the QCEW employment series, parameterized by `market_id` and period.
  Completed in this build.
- Place it in `foundations/` so the Richmond Quarto section can call the same function.
  Deferred: first implemented in section-owned prep for speed of workbook review.
- Surface as a D1 companion, not a new deliverable.
  Completed in this build.
- Document the period-selection choice and its sensitivity — results move with chosen endpoints.
  Completed in page-facing copy and prep notes.

**Definition of done:** the workbench can say whether employment change came from national tailwinds, inherited industry mix, or local competitive performance.

### 5B — Wages

**Why:** Wages are absent from the entire section. Industry mix without wages is half a market — a metro can be specialized in a sector that employs many and pays poorly, and nothing in D1–D5 would reveal it. "Won the knowledge economy" is a wage claim the section currently cannot evidence.

**Build tasks**

- Add sector wage context to D1 using `bea_earnings_*`, `bea_compensation_total`, `bea_wages_salaries`.
  Completed in this build via a D1 sector wage companion.
- Carry wages into the D5 peer comparison so peer similarity can be read on pay as well as mix.
  Completed in this build.
- Export wage context to the extracted D6 report so exposure can be weighted by wage level rather than headcount alone.
  Deferred with D6 extraction work.

**Definition of done:** the workbench distinguishes a high-wage concentration from a high-employment one.

### 5C — Concentration measure

**Why:** No measure of diversification exists. HHI or entropy over sector shares answers a natural one-line question — is this market diversified or dependent on one thing — and pairs directly with the existing LQ work.

**Build tasks**

- Compute HHI (and optionally entropy) over sector employment shares and GDP shares.
  Completed in this build by surfacing the existing Gold `industry_concentration_hhi` diagnostic in D5.
- Add to D5 as a peer-comparable metric.
  Completed in this build.

**Definition of done:** diversification is a comparable number rather than an impression from the stacked bar.

### 5D — GDP-basis specialization companion

**Why:** The specialization companion exists only on the employment basis because no LQ is precomputed for GDP. It is derivable.

**Build tasks**

- Derive LQ from `pct_real_gdp_*` against the national sector share using the same logic as the employment basis.
  Completed in this build.
- Surface the same LQ-vs-growth companion on the GDP basis.
  Completed in this build.

---

## Phase 6 — Validation and closeout

**Goal:** Close the review cleanly.

**Build tasks**

- Add or update targeted tests for the tract crosswalk coverage, the D4 buffer count logic, and any extracted D6 functions.
- Run the industry test suite.
- Do one full Richmond visual QA pass across the remaining deliverables.
- Re-run for one non-Richmond CBSA. **Known state from v1 review:** market switching already works across the analytical deliverables. The exception is D4 maps and POI surfaces, which fail for non-Richmond markets because spatial ingestion has only been run for Richmond. This is an ingestion gap, not a parameterization defect — do not "fix" it by adding market-specific logic.
- Update `SPEC.md` acceptance checkboxes and open-decisions table to match reality, including the workbench purpose decision.
- Append `decisions.md` entries for each phase.

**Definition of done**

- The workbench is trustworthy and readable, and remaining deferred items are named rather than implied.

---

## Split-out pipeline

**Moved.** The national cross-theme analyses now live in `ANALYSIS_PROGRAM.md`, which supersedes the table that was here. Do not maintain a second list in this file.

What remains relevant to this plan: **Phase 4 extraction feeds entry A1 (the AI inversion)**, which is the only `active` entry in the program. Nothing else in the program depends on this plan.

For within-market questions — where the comparison unit is places inside one metro rather than metros against each other — see `DEEP_DIVE_QUESTION_BANK.md`.

## Deferred — not in scope

| Item | Why deferred |
|---|---|
| GDP↔employment sector crosswalk | Real problem — the basis toggle silently swaps taxonomies and a reader cannot detect it. Substantial mapping build; does not block anything here. Protect it; do not lose it. |
| QCEW private-only basis | Understated in review as a Richmond quirk. It is platform-wide: private-only coverage distorts every capital, military metro, and university town, and because LQs are computed against a private-only national base, specialization ranking is affected everywhere. Full fix is QCEW government ownership ingestion and belongs in Foundations. **Interim mitigation belongs in Phase 1 if cheap:** a labeled disclosure plus a public-administration figure from LODES `jobs_ind_public_admin` or ACS `acs_ind_*`, neither requiring new ingestion. |
| ACS sparse-market fallback path | Untriggered in the v1 review and explicitly not a current concern. Leave untested rather than pretending it is verified. |
| Separate Economics application | A real product decision that should not be made to solve a table-slot problem. Record and move on. |
| Peer-methodology explainer | Prerequisite for showing the peer set externally and for the CBSA similarity research article. Should be written as research prose, which places it outside this build plan. |
| LODES OD work | Out of scope by standing guardrail. |
| ZIP/place-level GDP | No source at that grain. Not actionable. |
