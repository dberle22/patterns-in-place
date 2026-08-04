---
section: industry
status: draft
spotlight_market: richmond_va (CBSA 40060)
last_updated: 2026-07-29
---

# Industry — Section Spec

Analytical content and tool requirements for the Industry section of Metro Area Explorer, in one document. This is the spec of record for this section — `data_prep.py` and `app.py` are built to satisfy it.

## Purpose

Show the major industries and occupations in a market, how that makeup has changed over time, where industrial/economic activity concentrates spatially, and how the market compares regionally. Built market-agnostic: Richmond is the first market run through it, not a hardcoded target. A market is a CBSA GEOID (`market_id`) plus a small config (peer CBSAs, county/tract scope) — every deliverable below must accept that as an input, not assume Richmond.

## Data sources

| Source | Table | Grain | Notes |
|---|---|---|---|
| QCEW private employment (LQ) | `gold.economics_industry_wide` | geo_level/geo_id/year | `lq_ag_mining`, `lq_construction`, `lq_manufacturing`, `lq_wholesale`, `lq_retail`, `lq_transport_util`, `lq_information`, `lq_finance_real`, `lq_professional`, `lq_educ_health`, `lq_arts_accomm_food`, `lq_other_services` — LQ vs. national already computed |
| BEA real GDP by sector | `gold.economics_industry_wide` | geo_level/geo_id/year | `real_gdp_total`, `real_gdp_manufacturing`, `real_gdp_construction`, `real_gdp_trade`, `real_gdp_transportation`, `real_gdp_information`, `real_gdp_fire`, `real_gdp_professional`, `real_gdp_edu_health`, `real_gdp_leisure`, `real_gdp_gov`, plus `pct_real_gdp_*` shares. Multi-year — supports time series. BEA vintage lags QCEW by ~1 year. |
| BEA earnings by sector | `gold.economics_industry_wide` | geo_level/geo_id/year | `bea_earnings_*` by sector, `bea_compensation_total`, `bea_wages_salaries` |
| ACS industry employment (fallback/cross-check) | `gold.economics_industry_wide` | geo_level/geo_id/year | `acs_ind_*`, `pct_acs_ind_*` — broader geography coverage than QCEW; use if a market/year is QCEW-sparse |
| Occupation mix (OEWS) | `gold.economics_occupation_wide` | geo_level/geo_id/year | 4-bucket rollup (`oews_emp_stem`, `oews_emp_management_professional`, `oews_emp_service`, `oews_emp_production_transportation`, `oews_emp_other`) with LQ vs. national and mean wages. Coarse grain — fine for makeup, too coarse for a NAICS↔SOC exposure crosswalk if we add one later. |
| LEHD LODES (workplace vs. residence, industry mix, regional role) | `gold.economics_lodes_wide` | geo_level/geo_id/year (tract in `silver.lehd_lodes_wac`/`rac`) | `jobs_ind_*` (workplace-side, WAC) and `workers_ind_*` (residence-side, RAC) at matching industry cuts (construction, manufacturing, wholesale, retail, transport/warehouse, information, finance/insurance, real estate, professional/scientific/technical, admin/support, educational, health care, arts/entertainment, accommodation/food, other, public admin). `jobs_to_workers_ratio` and `pct_point_gap_ind_*` fields already computed — this is the regional-role and industrial-cluster input. Gold grain here is not tract; tract-level WAC/RAC pull is a direct query to `silver.lehd_lodes_wac`/`rac` filtered to the market's tracts. |
| Infrastructure POIs (roads, ports, airports, warehouses) | Not yet in Gold | — | No existing table. OSM/Overpass is the likely source (same as the Richmond Deep Dive spec's deferred Pass 2 POI layer). Treated as a stretch build below — do not block the section on it. |

No new ingestion is required for the core makeup, change, and regional-role deliverables. Infrastructure POIs are the one open gap.

## Deliverables

Each deliverable lists what it produces, its data source, and acceptance criteria — the definition of done an agent's output can be checked against.

### D1 — Industry makeup, change, and specialization

**What it produces:**
- Stacked bar: current industry mix by sector share, with equal UI treatment for the employment-share and GDP-share views
- Bump chart: sector rank movement over time within the selected basis, using all comparable years available for that source
- Specialization companion view for the employment basis:
  - latest-year LQ vs. recent employment-growth scatter when the latest two comparable employment years exist
  - fallback ranked specialization table when the latest-year LQ exists but a comparable growth pair does not
- One-line takeaway sentence identifying the largest share gainer/loser

**Data source:** `gold.economics_industry_wide` — QCEW `qcew_private_emp_*` / `pct_qcew_private_emp_*` for the primary employment-share view, sector LQs (`lq_*`) plus the latest two comparable QCEW years for the specialization companion, BEA `real_gdp_*` / `pct_real_gdp_*` for the GDP-share view, and ACS `acs_ind_*` / `pct_acs_ind_*` only as an explicit fallback when QCEW is too sparse for a market.

**Acceptance criteria:**
- [x] Stacked bar renders for any valid `market_id` with at least 8 of the 12 sector categories present (some sparsity is expected/acceptable per source notes above)
- [x] Employment-share and GDP-share toggle both render without error
- [x] Bump chart renders across at least 3 distinct years of data for the selected basis when that history exists; otherwise the app hides it with an "insufficient history" message
- [x] D1 can render a latest-year specialization view from `lq_*` without introducing a second sector taxonomy
- [x] If the latest two comparable QCEW years exist, D1 renders an LQ-vs-growth companion view; otherwise it falls back to a ranked specialization table with clear copy about the missing growth comparison
- [x] Takeaway sentence is generated from the actual largest positive/negative share delta, not hardcoded
- [x] Any ACS fallback is surfaced clearly in the app copy and chart metadata if it is ever used; as of July 28, 2026 no current CBSA appears to require this path under the live D1 coverage rule

**Build status:** Reuses `chart_engine.prep/render.bar` for current mix and `chart_engine.prep/render.bump_chart` for change-over-time. The specialization companion is now in place as a small net-new addition on the employment basis: latest-year `lq_*` values drive an LQ-vs-growth scatter when the latest comparable QCEW pair exists, and otherwise D1 falls back to a ranked specialization table with explicit missing-growth copy. Parcat is **deferred companion work**, not part of the first ship.

---

### D2 — Industrial and GDP clusters (spatial)

**What it produces:**
- Interactive tract map with two modes:
  - dominant-industry categorical view, where each tract is colored by the harmonized D1 sector with the highest workplace job count
  - selected-industry choropleth, where tract fill shows the selected sector's share of tract workplace jobs
- Interactive county map showing selected-sector GDP share, using the same D1 sector taxonomy for the selector so tract employment and county GDP can be compared without changing the vocabulary
- Jobs-intensity companion view for tract interpretation:
  - a bubble/scatter view that shows raw tract jobs alongside jobs-per-resident and jobs-per-square-mile intensity
  - a ranked tract table that can sort by total jobs, jobs per resident, or jobs per square mile to surface the biggest absolute and relative employment concentrations

**Data source:** `silver.lehd_lodes_wac` (tract grain, `jobs_ind_*` fields) for the tract map; `gold.population_demographics` for tract population context; `geo.tracts_all_us` for tract land area; `gold.economics_industry_wide` (county grain) for the county-level GDP view.

**Acceptance criteria:**
- [x] Tract map renders for all tracts within the market's CBSA boundary, no missing-geometry errors
- [x] Tract map supports both dominant-sector and selected-sector-share modes without requiring a separate data-prep path per mode
- [x] County GDP-share map renders using the same sector categories as D1 for direct comparability
- [x] Jobs-intensity companion view surfaces tract-level total jobs, jobs per resident, and jobs per square mile from the same D2 tract surface without a separate manual export
- [x] Map legend/binning is consistent (same breaks logic) across markets, not manually tuned per market
- [ ] Handles a market with sparse LODES coverage without crashing (documented fallback: county-only view)

**Build status:** Built as an interactive Streamlit `pydeck` map rather than a static chart-engine map, because scrolling and zooming are part of the requirement. Geometry should come first from `patterns_in_place.geo.tracts_all_us`; a file-based Richmond fallback is acceptable only as a test-path backup if DuckDB geometry export fails in the app runtime.

---

### D3 — Job centers and internal employment pull

**What it produces:**
- Job-center summary built from tract LODES:
  - ranked table of top tracts by total workplace jobs
  - ranked table of top tracts by jobs-to-resident-workers ratio, with a minimum jobs floor so tiny tracts do not dominate
  - optional selected-sector version to show where a chosen industry is most concentrated as a workplace center
- CBSA labor-pull summary card:
  - CBSA `jobs_to_workers_ratio`
  - raw `jobs_minus_workers` count so the user sees scale as well as ratio
  - short synthesis sentence tying the CBSA-wide ratio to the major tract job centers
- Industry imbalance view showing which industries are more workplace-heavy versus residence-heavy within the CBSA:
  - ranked bar chart of `pct_point_gap_ind_*` values
  - companion table with workplace jobs, resident workers, and share gap for the selected industries
- Job-center shortlist that is explicitly designed to feed D4 interpretation:
  - a small, review-friendly set of leading tracts that D4 can enrich with nearby infrastructure and institutional context
  - synthesis copy that frames each shortlisted tract as a candidate logistics, institutional, office/professional, or mixed job center rather than just a high-value row in a table

**Data source:** tract-level `silver.lehd_lodes_wac` and `silver.lehd_lodes_rac` for internal job-center identification; `gold.economics_lodes_wide` for the CBSA summary card and industry imbalance surface (`jobs_total`, `workers_total`, `jobs_minus_workers`, `jobs_to_workers_ratio`, `jobs_ind_*`, `workers_ind_*`, `pct_point_gap_ind_*`).

**Acceptance criteria:**
- [x] D3 surfaces tract job centers from the existing tract WAC/RAC data without requiring a separate geometry ingestion path
- [x] The tract job-center view can rank both by raw workplace jobs and by jobs-to-resident-workers ratio, with a documented floor/filter to avoid tiny-tract artifacts
- [x] The CBSA summary card renders for any `market_id` present in `gold.economics_lodes_wide`
- [x] The app shows both ratio and raw jobs-minus-workers count so a small market and large market with the same ratio are not presented as equivalent in scale
- [x] Industry imbalance chart renders from the existing `pct_point_gap_ind_*` fields without requiring OD ingestion
- [x] Positive/negative sign conventions are explained in the UI copy so users can tell whether a sector is workplace-heavy or resident-worker-heavy
- [x] D3 copy explicitly distinguishes this section from D2: D2 maps the spatial distribution of jobs; D3 interprets which tracts function as the CBSA's job centers and which industries create that pull
- [x] D3 does not rely on attractor/bedroom threshold labels at tract or CBSA level in the first pass
- [x] D3 exposes a reusable top-job-center shortlist that D4 can read without a manual export or tract hand-picking step

**Build status:** Core D3 is a small net-new synthesis layer on top of existing tract WAC/RAC queries plus the CBSA Gold LODES surface. No OD ingestion required.

---

### D4 — Infrastructure and POI overlay

**What it produces:**
- Interactive overlay map that keeps the existing D2 tract fill as the base surface, then layers in:
  - OSM infrastructure and site geometry for highways, major roads, rail, airports, ports, warehouse/logistics features, and other large-footprint industrial or campus-like features where tagging is usable
  - Overture POI/place records as labeled point overlays, including first-wave amenities such as hospitals, groceries, universities, and schools
  - population-center and job-center markers from the existing D2/D3 prep surfaces
- Job-center interpretation companion built on top of the D3 shortlist:
  - tract-level enrichment table that counts or flags nearby highways, rail, airport/port features, warehouse/logistics polygons, hospitals, universities, schools, and groceries within a simple first-pass buffer
  - lightweight job-center typology read that helps distinguish infrastructure/logistics-led, institutional, office/professional, and mixed employment centers
- Layer summary / manifest review so the app user can see what was actually extracted for the market before interpreting the map

**Data source:** App-local cached market extracts written by `ingest_spatial.py`. OSM is the primary geometry source for corridors, footprints, and site polygons; Overture is a first-class POI/place source for labeled place records and amenities. Neither source is in Gold yet; this implementation is a practical precursor to Foundations Track 17, not the final governed storage path.

**Acceptance criteria:**
- [x] `ingest_spatial.py` accepts `market_id` or `bbox`, extracts OSM infrastructure layers, and writes separate cached parquet outputs for point, line, and polygon geometry families
- [x] `ingest_spatial.py` extracts Overture place/POI rows as a distinct first-class output rather than folding them into the OSM cache
- [x] A `spatial_manifest.json` is written beside the cached outputs and records source, layer, query config, row count, geometry type, and sparse/missing-layer notes
- [x] `data_prep.py` reads cached spatial outputs without re-querying OSM or Overture at app runtime
- [x] D4 renders on the existing D2 map surface without requiring a separate map component or a separate tract geometry prep path
- [x] D4 can overlay cached OSM and Overture layers together with existing population and tract job-center markers from D2/D3
- [x] D4 can compute a first-pass tract enrichment summary for the D3 shortlist using simple buffers and feature counts/flags rather than requiring network analysis in v1
- [x] D4 surfaces a reviewable job-center interpretation table or card set so the map is a supplement to the analysis, not the only analytical output
- [x] D4 copy clearly labels the first-pass enrichment method as geometric proximity, not travel-time or network access
- [x] Sparse or missing layers fail gracefully and are surfaced in the manifest / app notes rather than crashing the page

**Build status:** The overlay/cache reader and first-pass interpretation layer are now in place. D4 keeps the existing D2 map surface, reads only cached OSM/Overture extracts at runtime, and adds a D3-powered shortlist enrichment pass with transparent centroid-buffer counts/flags and a lightweight tract typology. The ingest logic remains separate from `data_prep.py` so it can later be promoted into Foundations Track 17-style reusable scripts.

---

### D5 — Regional fit and peer benchmarking

**What it produces:**
- Stacked bar (or small multiples) comparing the market's industry/GDP mix against 3–5 peer CBSAs and the national baseline
- Jobs-to-workers benchmark tile or small comparison chart showing where the CBSA sits versus:
  - selected peer CBSAs
  - Census division
  - national baseline if available from the same governed surface or from a documented first-pass derived benchmark path
- Short regional-fit takeaway that answers how the CBSA fits into the broader region after D3 has already established where the internal job centers are

**Data source:** `gold.economics_industry_wide` filtered to `market_id` + peer CBSA list for industry/GDP mix, with first-pass U.S. and division benchmark rows derived from state rows because the current Gold mart does not yet ship native `us` or `division` rows; `gold.economics_lodes_wide` for `jobs_to_workers_ratio`, `jobs_minus_workers`, and related benchmark context across peer CBSAs plus the governed `division` surface, with any first-pass national LODES comparison treated as a documented derived benchmark rather than a native Gold row. Peer defaults can come from a manual market config or the promoted Cross-Frame Intelligence mart `mart_intelligence.intelligence_cross_frame`, which already carries the widened top-10 cosine-similarity peer bundle per CBSA.

**Acceptance criteria:**
- [x] Renders for market + arbitrary peer list of 3–5 CBSAs without code changes
- [x] National baseline row/bar always present for the industry/GDP mix view, even if it is first synthesized from state rows rather than read as a native Gold row
- [x] Same sector taxonomy and share basis (employment or GDP) as D1, so the two are visually comparable
- [x] Jobs-to-workers benchmark renders for the market and peer list from the governed LODES surface without a custom one-off prep path per market
- [x] Each D5 panel carries its own latest-year label and source note rather than forcing one harmonized year across industry, GDP, and LODES benchmark surfaces
- [x] D5 copy explicitly distinguishes this section from D3: D3 asks where jobs concentrate within the CBSA; D5 asks how the whole CBSA compares with peers and the broader region

**Build status:** Reuses `chart_engine.prep/render.bar` for the mix comparison and adds a small net-new benchmark comparison for the `jobs_to_workers_ratio`. First pass should keep independent latest-year labels per panel, use a manual peer list or the existing Cross-Frame Intelligence peer bundle for default peer suggestions, and document any derived U.S. or division benchmark rows clearly in the UI metadata.

---

### D6 — AI exposure setup and scorecard

**What it produces:**
- Sector-level exposure scorecard that the explorer can hand off to Richmond S04a:
  - sector employment share
  - sector specialization context
  - sector AI exposure score from the Felten industry appendix
  - optional policy/context flags if we decide to keep the S04a scorecard structure intact here
- Occupation-level exposure companion that begins the Richmond S04b setup inside the explorer:
  - ranked detailed occupations by employment and exposure
  - summary view of which broad occupation families dominate the highest-exposure footprint in the selected market
- Short synthesis connecting D6 back to D1/D3/D4:
  - which specialized sectors appear most exposed
  - whether the highest-exposure footprint appears concentrated in institutional, office/professional, or other job-center types

**Data source:** `gold.economics_industry_wide` for market sector shares and specialization context; `silver.bls_oews` for detailed SOC employment at CBSA grain; `gold.economics_occupation_wide` for broad occupation-family context where a lighter summary is useful; Felten et al. Data Appendix B for 4-digit NAICS industry AIIE scores and Appendix A for 6-digit SOC occupation AIOE scores, treated as section-owned external reference inputs until a governed shared storage path exists.

**Acceptance criteria:**
- [x] D6 renders a sector exposure scorecard for any market with D1 employment coverage plus a valid industry-exposure lookup, without hardcoding Richmond-only sector assumptions
- [x] D6 can read detailed OEWS occupations from `silver.bls_oews` and produce a ranked exposure view without requiring ACS occupation-by-industry cross-tabs
- [x] D6 explains when exposure scores come from sector-level NAICS logic versus occupation-level SOC logic so the two views are not presented as interchangeable
- [x] D6 synthesis explicitly connects the exposure view back to D1 specialization and D3/D4 job-center interpretation instead of acting as a detached thematic appendix
- [x] Missing or partially matched NAICS/SOC crosswalk rows fail with transparent coverage notes rather than silent dropping

**Build status:** D6 is now live as a dedicated `industry/` page with a sector/occupation toggle and app-facing final crosswalk tables. The raw Felten workbook remains section-owned at `metro-deep-dive/metro-area-explorer/industry/reference_data/AIOE_DataAppendix.xlsx`, while the runtime join now resolves through reviewed final crosswalk CSVs in `metro-deep-dive/metro-area-explorer/industry/outputs/national/d6_coverage_review/`. Sector exposure uses the final NAICS crosswalk to connect 4-digit QCEW industry groups rolled from `staging.bls_qcew_county` through `silver.xwalk_cbsa_county` back to Felten Appendix B scores, then collapses those detailed rows to the broad D1 sector taxonomy for comparability. The occupation companion uses the final SOC crosswalk against detailed `silver.bls_oews` rows for `2025`, adds a ranked table plus a bubble-scatter companion, and uses `gold.economics_occupation_wide` for the lighter family summary. Audit trail files preserve the original appendix rows, review queues, locked manual overrides, and final crosswalk outputs so the page uses the agreed shape while the methods trail stays inspectable.

---

### Deferred follow-on — LODES OD flow layer

This is **not** required for the current Industry app build. The existing WAC/RAC surfaces are sufficient for D2-D5. This subsection records what OD would add later so we do not have to rediscover the scope when Deep Dive labor-flow work becomes a priority.

**What OD would add beyond WAC/RAC:**
- WAC tells us where jobs are located and RAC tells us where workers live, but neither one identifies the actual origin-destination pair.
- OD adds the flow itself: home geography to work geography, with worker-count payloads for each pair.
- That means OD answers questions WAC/RAC cannot:
  - which outside counties or tracts send the most workers into the CBSA's main job centers
  - which tracts inside the CBSA export the most workers to other internal job centers
  - whether a tract is a job center for nearby neighborhoods versus a true regional draw across the metro edge
  - which corridors or cross-boundary pairs matter most for a selected industry or earnings band

**What it would produce in this section:**
- Commute-shed view for the CBSA's largest job centers:
  - top origin tracts or counties feeding a selected workplace tract, county, or CBSA
  - top destination tracts or counties for workers living in a selected origin tract
- Cross-boundary inflow/outflow summary:
  - worker flows entering the CBSA from outside counties or adjacent CBSAs
  - worker flows leaving the CBSA for external job centers
  - ranked import/export corridor table with worker counts and flow share
- Flow map or desire-line map:
  - weighted lines connecting the largest origin-destination pairs
  - filters for internal-only, external-only, or selected-industry / selected-earnings-band flows if supported by the chosen OD grain
- Stronger regional-role interpretation in D5:
  - not just "the CBSA has more jobs than workers," but "the CBSA draws from these specific external labor sheds and sends workers to these others"

**Foundations work required first:**
- Add a dedicated OD staging path in `foundations/etl/` rather than widening the current WAC/RAC scripts.
- The existing source contract already documents OD as deferred in `foundations/data_dictionary/sources/source__lehd_lodes.md`; this future work should promote that deferred path into a managed staging contract.
- Expected first-pass Foundations work:
  - write a staging script for state-based LODES OD files, likely as a new script such as `foundations/etl/staging/get_lehd_lodes_od.R`
  - decide the managed analytical grain before writing Silver:
    - block-level pairs are too large for direct app use
    - tract-to-tract, county-to-county, or tract-to-county rollups are the realistic first candidates
  - keep `main` and `aux` OD parts explicit because external-residence handling matters for cross-boundary labor-shed analysis
  - document state-year coverage exceptions separately from WAC/RAC because OD availability is not identical across all state-years
  - add a dedicated staging markdown contract and a matching Silver contract instead of folding OD into the current WAC/RAC tables

**Recommended first-pass OD product shape for Metro Deep Dive:**
- `staging.lehd_lodes_od`: managed raw-or-near-raw OD batch at the chosen reduced grain for selected states and years
- `silver.lehd_lodes_od`: canonical flow table with normalized `origin_geo_id`, `destination_geo_id`, `year`, flow counts, and retained segmentation fields
- optional Deep Dive-facing mart:
  - either a narrow `gold.economics_lodes_od_summary`
  - or a section-owned prep path that queries the Silver OD table directly for selected markets

**Build status:** Deferred foundational follow-on. Do not block the Industry section on this. Revisit when we want true commute-shed, corridor-flow, or external labor-supply analysis rather than workplace/residence imbalance alone.

## Tool requirements (Streamlit app)

- **Market selector:** dropdown or text input for `market_id` (CBSA GEOID), defaulting to Richmond (40060) but not restricted to it
- **Year/year-range selector:** single-year selector for the D1 stacked bar; D1 bump chart uses the full comparable history for the selected basis and is bounded to years actually available per source (QCEW/BEA vintages differ)
- **View toggle:** employment-share vs. GDP-share for D1/D5
- **Per-panel vintage labels:** D5 should show the latest available year independently for each panel rather than pretending industry, GDP, and LODES benchmarks are all from one common year
- **Grain toggle:** tract vs. county for D2
- **Industry selector:** optional sector filter for D3 so the user can isolate one imbalance story after seeing the full ranked view
- **Ranking toggle:** total workplace jobs vs. jobs-to-resident-workers ratio for the D3 tract job-center view
- **D4 overlay toggles:** source/layer toggles for OSM lines, OSM polygons, Overture POIs, population centers, and job centers
- **D4 interpretation controls:** selected job-center shortlist item plus buffer-distance control for the first-pass tract enrichment summary, with copy that this is straight-line proximity rather than network access
- **Peer list input:** editable list of comparison CBSAs for D5, pre-filled either from a manual market config or from the best-fit peers in `mart_intelligence.intelligence_cross_frame`; exact fallback order is now a first-pass build decision, while the longer-term reusable peer-query surface remains open
- **D6 exposure controls:** sector vs. occupation exposure view, selected basis/context labels, and clear coverage/source notes for the Felten joins
- **Layout:** single-page, section-ordered D1 → D2 → D3 → D4 → D5 → D6, each in its own container so any deliverable can be hidden/shown independently while build is in progress

## Open decisions

| Decision | Blocks | Status |
|---|---|---|
| Employment-share vs. GDP-share as the D1/D5 default view | D1, D5 | Resolved for first pass — equal dual view in the UI, with independent latest-year behavior by source |
| Tract ranking floor/filter for D3 jobs-to-resident-workers ratio view | D3 | Resolved for first pass — current implementation uses a `2,500` workplace-jobs floor; revisit only if multi-market review shows it is distorting the rankings |
| Whether D5 should benchmark `jobs_to_workers_ratio` against peers only or peers plus division and nation | D5 | Resolved for first pass — peers plus division, and nation only when a documented derived benchmark path is available |
| Long-term benchmark storage path for D5 national/division rows | D5, Foundations | Open follow-on — first pass can derive benchmark rows in app prep, but we should add governed U.S./division benchmark support to the relevant Gold marts |
| What managed grain the future LODES OD path should use (tract-tract, county-county, tract-county, or CBSA summary) | Deferred OD follow-on | Open — needs a deliberate Foundations decision before ingestion work starts |
| When to ingest LODES OD for a real commute-shed or cross-boundary flow view | Deferred OD follow-on | Deferred companion work — do not block the current build |
| Long-term year-alignment strategy across D1/D5 benchmark panels | D1, D5 | Open follow-on — first pass keeps independent latest-year labels per panel, but we should decide a reusable comparable-year strategy later |
| Peer CBSA default selection logic for D5 | D5 | Resolved for first pass — editable peer list with defaults from manual market config or `mart_intelligence.intelligence_cross_frame` top peers |
| Long-term peer-query surface for products beyond the widened top-10 bundle | D5, Intelligence Layer | Open follow-on — current mart is enough for defaults, but a long-form peer mart would be cleaner for reusable querying |
| D4 source split and short-term storage path | D4 | Resolved for first pass — OSM owns infrastructure geometry, Overture is first-class for POIs, and app-local cached outputs sit behind a separate `ingest_spatial.py` entrypoint |
| D4 job-center interpretation method | D4 | Resolved for first pass — use simple buffer-based counts/flags around the D3 shortlist; document network-access analysis as a future follow-on rather than blocking v1 |
| D4 first-wave interpretation emphasis | D4 | Resolved for Richmond first pass — include hospitals and universities alongside freight/logistics and corridor infrastructure so institutional and infrastructure-led job centers can both be interpreted |
| D4 cross-source deduplication policy | D4 | Deferred — first pass can use source-priority display behavior rather than full OSM/Overture entity resolution |
| D6 scope relative to Richmond S04a/S04b | D6 | Resolved for first pass — the explorer should absorb the setup work for both the sector scorecard and the occupation-exposure companion rather than leaving all exposure prep to the downstream Quarto section |
| Long-term storage path for the Felten appendix lookup tables | D6, Foundations | Open follow-on — first pass can keep the appendix files as section-owned reference inputs, but a shared governed lookup would be cleaner once the theme is reused across markets |
| First-pass D6 policy/context flags | D6 | Open — we have the Richmond S04a scorecard shape, but still need to decide whether the explorer should ship with the full policy-flag column set or start with exposure + employment context only |
| Parcat build approach (custom vs. existing plotting lib wrapped into chart_engine) | D1 | Deferred — revisit only if Richmond plus one additional market show a tier-migration story that the bump chart misses |

## Relationship to the Richmond Deep Dive

This section's output is the interactive/exploratory layer for the analysis that ultimately populates `metro-deep-dive/markets/richmond_va/act2_engine_fabric/s04_industry.qmd` (Richmond SPEC.md §S04a/§S04b). Any engine built here is built in `foundations/` so the Quarto section can call the same functions rather than duplicating logic. This section is broader in scope than S04a/S04b, but it now intentionally absorbs more of that spine setup work: D1 should support specialization context, D4 should help interpret the job centers that D3 surfaces, and D6 should prepare the AI exposure scaffolding that Richmond S04a/S04b needs downstream. It still should not contradict the Deep Dive spec, and OD-style commute-shed claims remain deferred until managed LODES OD work exists.
