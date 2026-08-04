## 2026-07-28 — Implement D1 first pass
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 2 turns after the planning pass
- **Key decisions made:** deferred Parcat and shipped `bump_chart` for v1 change-over-time
- **Key decisions made:** kept employment-share and GDP-share as equal UI views without forcing one harmonized taxonomy
- **Key decisions made:** treated QCEW as the canonical employment source and ACS as an explicit fallback only
- **Notes:** shared `bar_chart` tooltip support had to be extended slightly so stacked D1 bars could surface year, source, and raw value instead of only share

## 2026-07-28 — D1 stabilization, benchmarks, and close-out
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** follow-on implementation pass after the first D1 build
- **Key decisions made:** simplified the app runtime path by preparing separate employment-share and GDP-share data frames rather than relying on one shared basis surface inside the UI
- **Key decisions made:** reverted from rendering both basis panels together to rendering one selected basis at a time for better Streamlit stability
- **Key decisions made:** added lightweight D1 benchmark context for `US` and `Division`, derived from aggregated state rows because `gold.economics_industry_wide` does not currently ship native `us` or `division` rows
- **Key decisions made:** chose not to force an ACS fallback test because no current CBSA appears to require it under the live D1 coverage rule
- **Key decisions made:** standardized validation around `.venv312` and confirmed `.venv312/bin/python -m pytest metro-deep-dive/tests/test_industry_d1.py` passes
- **Notes:** Richmond validated cleanly for both bases; broader visual polish and broader multi-market review remain future work once more section visuals are complete

## 2026-07-28 — Implement D2 interactive maps
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 implementation pass after the D2 planning review
- **Key decisions made:** treated `patterns_in_place.geo.tracts_all_us` as the canonical tract geometry source and kept file-based geometry as fallback-only, not the primary app interface
- **Key decisions made:** collapsed raw tract LODES industries into the broader D1 sector taxonomy so the map speaks the same sector language as D1 charts
- **Key decisions made:** used interactive `pydeck` maps instead of static visual-library choropleths because scrolling and zooming are required for D2
- **Key decisions made:** started the county comparison surface as selected-sector GDP share, while keeping the tract surface on workplace employment share
- **Key decisions made:** kept tract jobs-intensity diagnostics inside D2 rather than pushing them to a later section, because absolute jobs, jobs per resident, and jobs per square mile are part of the same tract-interpretation workflow as the cluster map
- **Key decisions made:** avoided adding new GIS Python dependencies because DuckDB spatial export plus `pydeck` was sufficient in the current `.venv312` runtime
- **Notes:** `.venv312` currently has `streamlit`, `pydeck`, and `duckdb`, but not `geopandas` or `shapely`; those are still listed in `metro-deep-dive/requirements.txt` but were not required for this first D2 implementation

## 2026-07-28 — Refine D3 regional role spec before build
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 2 revision passes from user review notes
- **Key decisions made:** reframed D3 away from a thin inflow/outflow stat tile and then further narrowed it to internal CBSA job centers and employment pull
- **Key decisions made:** separated D3 analytically from D1 by defining D1 as external specialization/benchmarking and D3 as internal job-center interpretation built from workplace-versus-resident imbalance
- **Key decisions made:** treated `gold.economics_lodes_wide` as sufficient for a first-pass ranked industry imbalance view because it already exposes `jobs_total`, `workers_total`, and `pct_point_gap_ind_*`
- **Key decisions made:** moved broader regional fit and `jobs_to_workers_ratio` benchmarking to D5 so D3 can stay focused on where the job centers are within the CBSA
- **Key decisions made:** explicitly deferred true commute-shed / tract-to-tract flow views until LODES OD ingestion exists, rather than implying those claims can be made from WAC/RAC alone
- **Notes:** open implementation choices now center on D3 tract-ranking filters and how broad the D5 benchmark set should be (peers only vs. peers plus division/nation)

## 2026-07-28 — Document deferred LODES OD follow-on scope
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 revision pass from user review notes
- **Key decisions made:** documented OD as an explicit future Foundations path rather than an implied app-layer enhancement
- **Key decisions made:** kept the current Industry build scoped to WAC/RAC because those surfaces are sufficient for job-center and peer-benchmark analysis
- **Key decisions made:** spelled out the OD-only questions we want later: commute sheds, cross-boundary inflow/outflow corridors, and explicit origin-destination labor-shed mapping
- **Notes:** the main unresolved Foundations choice is the first managed OD grain, with tract-to-tract, county-to-county, and mixed rollups all still viable

## 2026-07-28 — Implement D3 job-centers page
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 implementation pass after the D3 spec refinement
- **Key decisions made:** followed the existing page-per-deliverable pattern by adding a dedicated `pages/d3_job_centers.py` page and wiring it into the combined `industry/app.py` shell
- **Key decisions made:** reused the existing D2 tract surface and enriched it with tract-level resident-worker counts so D2 and D3 interpret the same latest-year LODES geography
- **Key decisions made:** set the first-pass tract jobs floor to `2,500` workplace jobs for the jobs-to-workers ranking to avoid tiny-tract artifacts
- **Key decisions made:** kept D3 focused on tract rankings, CBSA labor-pull summary, and industry imbalance, without introducing OD-style flow claims
- **Notes:** focused validation now covers D1, D2, and D3 via `.venv312/bin/python -m pytest metro-deep-dive/tests/test_industry_d1.py metro-deep-dive/tests/test_industry_d2.py metro-deep-dive/tests/test_industry_d3.py`

## 2026-07-28 — Implement D4 ingestion split and overlay reader
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 implementation pass after the D4 ingest/overlay plan was approved
- **Key decisions made:** kept raw acquisition in a new `ingest_spatial.py` entrypoint so `data_prep.py` stays focused on cached app prep rather than source querying
- **Key decisions made:** treated OSM as the first-pass infrastructure geometry source and Overture as a first-class POI/place source, with separate cached outputs for each
- **Key decisions made:** kept short-term storage app-local under `industry/outputs/<market_id>/`, but shaped the schema and manifest so the flow can later promote into Foundations Track 17
- **Key decisions made:** rendered D4 as an overlay on the existing D2 tract surface, then added population-center and job-center markers from existing D2/D3 prep instead of creating a separate map stack
- **Notes:** live OSM/Overture extraction still depends on network availability and a configured Overture parquet path; automated validation in this pass focuses on the cache reader contract, manifest handling, and app wiring

## 2026-07-28 — Add D3 tract map after visual review
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 follow-up revision pass
- **Key decisions made:** changed D3 from a table-first surface to a map-first surface with highlighted tract job centers
- **Key decisions made:** confirmed the current DuckDB geo layer does not yet materialize place boundary geometry, so the new D3 map remains tract-based for now
- **Key decisions made:** kept the map implementation on the existing tract geometry surface so a future place overlay can be added without replacing the D3 data prep path
- **Notes:** a future place overlay will require a governed place-geometry table; the current repo only exposes place identifiers and the `silver.xwalk_cbsa_primary_city` crosswalk, not place polygons

## 2026-07-29 — Lock first-pass D5 benchmark and peer decisions
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 planning-and-spec alignment pass before D5 implementation
- **Key decisions made:** proceed with D5 now rather than waiting for D4, because the current governed industry and LODES surfaces are already sufficient for first-pass regional benchmarking
- **Key decisions made:** keep national and division benchmark context in the D5 plan, but document that the current Gold marts do not yet provide the full native benchmark surface D5 ultimately wants
- **Key decisions made:** for first pass, derive D5 industry U.S. and division benchmark rows from state rows the same way D1 already does, and record as follow-on platform work that these benchmark rows should eventually be added to Gold rather than rebuilt in app prep
- **Key decisions made:** keep independent latest-year labels per D5 panel rather than forcing one harmonized year across QCEW employment, BEA GDP, and LODES job-pull comparisons
- **Key decisions made:** record the long-term follow-on that we still need a reusable comparable-year strategy for D1/D5 instead of relying indefinitely on panel-by-panel vintage handling
- **Key decisions made:** first-pass peer defaults can come from either a manual market config or the promoted Cross-Frame Intelligence mart `mart_intelligence.intelligence_cross_frame`, which already exposes a widened top-10 cosine-similarity peer bundle per CBSA
- **Key decisions made:** treat the current widened Cross-Frame peer bundle as sufficient for default D5 peer suggestions, while noting that a long-form peer mart would be a cleaner reusable product surface later
- **Notes:** Richmond (`40060`) currently has live Cross-Frame peers in DuckDB, with Baltimore (`12580`) and Virginia Beach (`47260`) appearing at the top of the current similarity bundle; that is enough to support D5 defaulting without inventing a new peer-selection system first

## 2026-07-29 — Implement D5 regional-fit page
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 implementation pass after the D5 planning lock
- **Key decisions made:** resolved D5 peer defaults directly from `mart_intelligence.intelligence_cross_frame` rather than inventing a section-local peer heuristic
- **Key decisions made:** moved first-pass national and division benchmark logic into reusable section-owned SQL files so D1 and D5 can share the same benchmark derivation path
- **Key decisions made:** kept the D5 mix panel on the existing chart-engine stacked bar path and used a lightweight Plotly bar for the jobs-to-workers comparison panel
- **Key decisions made:** kept D5 panel vintages independent in the live UI, with the mix panel following its selected basis year and the LODES panel holding to its own latest available year
- **Key decisions made:** exposed the top Cross-Frame peer bundle as an editable multiselect in the page so users can keep the intelligence defaults or trim the comparison set manually
- **Notes:** targeted validation passed on Wednesday, July 29, 2026 via `.venv312/bin/python -m pytest metro-deep-dive/tests/test_industry_d5.py metro-deep-dive/tests/test_industry_d1.py`, and D5 is now wired into the combined `industry/app.py` shell

## 2026-07-29 — Prototype OSM infrastructure ingest with `osmextract`
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 exploratory implementation pass after Overpass and state-scale `pyrosm` proved operationally awkward
- **Key decisions made:** installed `osmextract` and tested a Richmond-first R script instead of continuing to invest in Overpass retries
- **Key decisions made:** switched the prototype to the `openstreetmap_fr` provider because it exposes a dedicated `richmond-latest.osm.pbf` extract rather than forcing a Virginia-scale fallback
- **Key decisions made:** filtered the translated Richmond extract to infrastructure-only families: highways, major roads, rail, airports, ports, and warehouses/logistics
- **Key decisions made:** kept the prototype outputs separate under `industry/outputs/richmond_va_osmextract/` so they can be reviewed without disturbing the existing D4 cache path
- **Notes:** the Richmond `osmextract` run completed on Wednesday, July 29, 2026 and landed real infra counts (`5,300` highways, `16,572` major roads, `1,374` rail, `115` airport point/polygon features, `7` port point/polygon features, `114` warehouse/logistics polygons); the remaining question is source footprint fit and quality review, not whether OSM can be landed at all

## 2026-07-29 — Harden D4 ingestion contract for Richmond
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 hardening pass after the successful `osmextract` prototype
- **Key decisions made:** treated `osmextract` as the practical Richmond OSM geometry source of record and stopped investing in the unstable Overpass path for D4 readiness
- **Key decisions made:** added a Python promotion bridge so the successful Richmond `osmextract` outputs are normalized into the same `osm_infrastructure_*` cache contract that `data_prep.py` already reads
- **Key decisions made:** preserved the existing `richmond_va/` cache layout and added a `40060 -> richmond_va` output-dir alias in `data_prep.py` so the D4 reader can find the hardened cache reliably
- **Key decisions made:** tightened Overture category mapping logic to support first-wave education categories and to avoid the loose grocery substring behavior that previously created false positives
- **Notes:** validated on Wednesday, July 29, 2026 that `get_d4_overlay_payload(market_id='40060')` now loads `23,246` OSM line rows, `179` OSM polygon rows, `57` OSM point rows, and `76,913` Overture POIs from the hardened Richmond cache; ingestion is now in a good enough state to hand off to D4 analytics work

## 2026-07-29 — Revise spec for job-center interpretation and AI exposure
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 revision pass after user review
- **Key decisions made:** expanded D1 so the explorer spec now includes specialization context rather than stopping at mix and change
- **Key decisions made:** reframed D4 as a job-center interpretation layer, with the overlay map treated as support for a tract-enrichment summary rather than the whole analytical output
- **Key decisions made:** locked first-pass D4 interpretation to simple buffer-based counts/flags and recorded network-access analysis as a future follow-on rather than a blocker
- **Key decisions made:** added a new D6 deliverable so the explorer absorbs the Richmond Act 2 AI exposure setup work instead of leaving it entirely to downstream Quarto composition
- **Key decisions made:** updated the open-decisions table to reflect newly resolved choices around D3 floors, D4 interpretation scope, and D6 ownership
- **Notes:** the new D6 spec keeps Felten appendix inputs as section-owned reference data for now; promoting those lookups into a shared governed layer is still future platform work

## 2026-07-29 — Add closeout handoff plan
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 planning pass after user request
- **Key decisions made:** created `industry/CLOSEOUT_PLAN.md` as the concrete handoff artifact for the remaining section work rather than burying the plan in chat
- **Key decisions made:** prioritized the remaining closeout sequence as D4 interpretation, then D1 specialization, then D6 sector and occupation exposure work, followed by validation and spec cleanup
- **Key decisions made:** kept D4 on a simple buffer-and-count interpretation method for first pass and explicitly excluded OD and network-access expansion from the closeout scope
- **Notes:** the plan assumes D1, D2, D3, D4 ingest, and D5 remain extension points rather than rebuild targets; if later review changes that assumption, the handoff plan should be revised rather than silently worked around

## 2026-07-29 — Close out D4 interpretation layer
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 implementation pass following the closeout plan
- **Key decisions made:** promoted the D3 top-job-center ranking into a reusable shortlist payload in `data_prep.py` so D4 no longer depends on manual tract hand-picking
- **Key decisions made:** kept the first-pass D4 enrichment on centroid-based straight-line buffers around shortlisted tract centroids rather than introducing geometry clipping or network analysis
- **Key decisions made:** treated the D4 interpretation surface as the primary page output by adding a shortlist table, selected-tract detail read, and transparent tract typology ahead of the companion overlay map
- **Key decisions made:** widened warehouse/logistics enrichment to count both point and polygon cache rows so sparse OSM tagging does not disappear from the first-pass interpretation
- **Notes:** targeted validation passed on Wednesday, July 29, 2026 via `.venv312/bin/python -m pytest metro-deep-dive/tests/test_industry_d4.py`; a Richmond smoke read now returns an 8-tract shortlist with the current lead tract reading as `Institutional`

## 2026-07-29 — Close out D1 specialization companion
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 implementation pass following the closeout plan
- **Key decisions made:** kept specialization on the existing D1 employment taxonomy by reading latest-year `lq_*` fields directly from `gold.economics_industry_wide` rather than creating a parallel sector surface
- **Key decisions made:** defined recent growth as the latest comparable QCEW year pair with usable sector coverage and rendered the primary view as an LQ-versus-growth scatter only when that pair exists
- **Key decisions made:** added a ranked specialization-table fallback with explicit missing-growth copy so sparse or incomplete QCEW history does not break the page
- **Key decisions made:** kept the specialization prep in `data_prep.py` as one reusable payload that carries both scatter and fallback modes for the page and tests
- **Notes:** targeted validation passed on Wednesday, July 29, 2026 via `.venv312/bin/python -m pytest metro-deep-dive/tests/test_industry_d1.py`; Richmond now renders the specialization scatter from 2024 LQs with 2023-to-2024 employment growth

## 2026-07-30 — Close out D6 AI exposure page
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 implementation pass following the closeout plan
- **Key decisions made:** stored the Felten workbook section-locally at `industry/reference_data/AIOE_DataAppendix.xlsx` and parsed Appendix A/B directly from workbook XML rather than adding an `openpyxl` dependency to the app/test environment
- **Key decisions made:** preserved true Appendix B fidelity by rolling 4-digit QCEW industry groups from `staging.bls_qcew_county` through `silver.xwalk_cbsa_county`, then collapsed those detailed rows back to the existing D1 broad sector taxonomy for the live scorecard
- **Key decisions made:** added a small explicit NAICS fallback map for known appendix-vintage and aggregate-code mismatches instead of widening Foundations first or silently dropping those rows
- **Key decisions made:** kept the occupation companion on `silver.bls_oews` detailed `2025` SOC rows, added the requested ranked table plus bubble-scatter companion, and treated the remaining unmatched share as a transparent SOC-vintage limitation rather than inventing a synthetic crosswalk
- **Key decisions made:** shipped D6 as one dedicated page with a sector/occupation toggle and a dropdown explanation companion that exposes the underlying 4-digit industry rows and coverage notes
- **Notes:** targeted validation passed on Thursday, July 30, 2026 via `.venv312/bin/python -m pytest metro-deep-dive/tests/test_industry_d6.py metro-deep-dive/tests/test_industry_d1.py metro-deep-dive/tests/test_industry_d4.py metro-deep-dive/tests/test_industry_d5.py`; first-pass Richmond coverage now lands around `85%` for the sector join after the NAICS fallback map and about `77%` for the occupation join with explicit SOC-vintage notes in the UI

## 2026-08-02 — Finalize D6 reviewed Felten crosswalk workflow
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** 1 implementation pass to lock reviewed NAICS/SOC decisions into runtime crosswalks
- **Key decisions made:** preserved the raw Felten appendix inputs as the canonical score source, but promoted reviewed final NAICS and SOC crosswalk CSVs into the app-facing runtime join shape
- **Key decisions made:** locked section-owned manual override artifacts for both code systems and generated final resolved crosswalk tables in `industry/outputs/national/d6_coverage_review/`
- **Key decisions made:** updated D6 runtime prep to join `our_code -> final_felten_code -> Felten score` rather than relying on the earlier first-pass audit join logic
- **Key decisions made:** tightened the NAICS audit candidate logic so structurally missing Felten concepts stay transparent instead of surfacing unrelated global title-similarity matches
- **Notes:** targeted validation passed on Sunday, August 2, 2026 via `.venv312/bin/python -m pytest metro-deep-dive/tests/test_industry_d6.py`; D6 now uses the reviewed final crosswalk shape for both the sector scorecard and the occupation companion while preserving the full audit trail beside it
