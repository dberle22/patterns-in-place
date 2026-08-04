# Place Intelligence Decisions

## 2026-07-31 — Milestone 0 scaffold
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** single-pass
- **Key decisions made:** moved the spec into the Metro Area Explorer section folder; typed `lat`/`lon` as optional floats in the site loader because Milestone 0 allows blank coordinates before geocoding
- **Notes:** Milestone 0 only. Geocoder benchmark/vintage and downstream methodology choices remain open for Milestone 1+.

## 2026-07-31 — Milestone 1 geocoding
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** single-pass plus live smoke verification
- **Key decisions made:** used the Census geographies endpoint with `benchmark=4` / `vintage=4` (`Public_AR_Current` / `Current_Current` as returned by the live API); recorded `match_type` as `address_range` because the current Census payload does not expose a rooftop/interpolated label and the official API docs describe the engine as calculating coordinates along an address range; preferred the tract from the local spatial point-in-polygon lookup when it disagrees with the geocoder tract
- **Notes:** live smoke test for `3832 Baymeadows Road, Jacksonville, FL 32217` returned tract `12031016603`. The test needed one unsandboxed run because Python DNS resolution to the Census host was blocked inside the sandbox even though `curl` succeeded.

## 2026-07-31 — Milestone 2 D1 apportionment
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** single-pass plus synthetic and real-data smoke tests
- **Key decisions made:** implemented the 1/3/5 distances as non-overlapping ring bands rather than nested circles because the acceptance criteria require per-tract weights to sum to `<= 1`; used a site-local projected CRS via `estimate_utm_crs()` rather than a Jacksonville-specific CRS so `apportion.py` stays reusable for any site; cut dasymetric weighting for v0 because the current Overture path is hardcoded to `theme=places` and a place-shaped schema (`names.primary`, `categories.primary`, `taxonomy.*`), so building footprints are not a cheap parameter flip
- **Notes:** D1 now passes synthetic invariants plus a real Jacksonville smoke test against CBSA `27260`.

## 2026-08-01 — Milestone 3 D2 catchment profile
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** single-pass plus synthetic contract tests
- **Key decisions made:** built D2 around one shared metric-surface query helper so catchment rows, percentiles, and benchmark rows all come from the same Gold query path; limited the first metric catalog to tract-grain metrics that are already present through 2024 in the five named Gold tables; used the site's containing county for the county benchmark row
- **Notes:** D2 now returns a long-format catchment profile, benchmark table, and structured skip reasons. Tests cover source-year labeling, percentile denominator, dropped-metric reasons, and shared-query-path parity.

## 2026-08-01 — Milestone 3 D3 first slice
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** single-pass scaffold + tests
- **Key decisions made:** added Jacksonville-specific `ingest_jax_overture.py` and `ingest_jax_osmextract.R` entrypoints instead of mutating the shared Industry scripts; implemented a new allowlist-based POI classifier in `site_prep.py` using the Richmond review's recommended field priority (`basic_category` -> `taxonomy_primary` -> `taxonomy_hierarchy` -> `primary_category`); mirrored the current Industry D4 node typology heuristic in prep code as the v0 site-node classifier
- **Notes:** this is intentionally the first D3 slice only. The heavier daytime-population, barrier, and severance logic remains to be implemented before the Phase 1 stop gate is truly complete.

## 2026-08-01 — Milestone 3 D3 barrier refactor in progress
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** iterative live-data debugging against Jacksonville caches
- **Key decisions made:** kept the Jacksonville OSM source path and promoted the cached GeoPackage into normalized `osm_infrastructure_{lines,points,polygons}.parquet` outputs instead of continuing to depend on the brittle direct `osmextract` layer exports; treated the St. Johns/data issue as a geometry-construction problem rather than a missing-data problem after confirming that the Jacksonville cache contains named `Saint Johns River` line features plus abundant water polygons; changed severed-population-share estimation from tract centroids to tract-overlap weighting so a river can sever part of a tract without requiring the centroid to fall on the far side
- **Notes:** as of Saturday, August 1, 2026, the barrier code has been refactored so water barriers are built from consolidated named water features rather than raw fragmented water polygons, and `test_pi_d3.py` now covers the null-barrier case, synthetic crossing-spacing math, and day/night payload shape. The remaining open work is threshold validation on at least one real Jacksonville river-adjacent site, plus writing the final parity/threshold note once that validation is stable.

## 2026-08-01 — Milestone 3 D3 validation and closeout
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** live Jacksonville validation on two sites plus full test rerun
- **Key decisions made:** kept `D3_BARRIER_SPACING_THRESHOLD_MI = 1.0` as the first-pass highway/rail screening threshold; kept `D3_SITE_CARD_SEVERED_POP_SHARE_THRESHOLD = 0.2` as the first-pass site-card promotion threshold; added a dual-ring output so D3 now returns both the baseline straight-line rings and a water-adjusted companion geometry that removes far-side areas cut off by qualifying water barriers
- **Notes:** Jacksonville cache parity looks plausible rather than silently empty: `107,489` Overture POIs versus Richmond's `76,913`, plus normalized OSM outputs with `25,431` lines (`7,227` highways, `15,926` major roads, `1,632` rail, `646` water), `36` points, and `20,201` polygons (`19,892` water). Live validation on `1 E Independent Dr, Jacksonville, FL 32202` showed the new water-adjusted ring removing `35.8%` of the 3-mile ring area and `41.5%` of the 5-mile ring area, while `3832 Baymeadows Road, Jacksonville, FL 32217` showed essentially no adjustment until a negligible `0.0066%` change at 5 miles. The downtown `Saint Johns River` crossing spacing read `0.80` miles in the 1-mile ring, `0.93` in the 3-mile ring, and `1.60` in the 5-mile ring, which supports the choice to treat dense sub-mile crossings as friction and reserve >1-mile spacing for stronger non-water barrier suspicion. Under the current tract-overlap population method, neither validation site exceeded the `0.2` severed-population-share site-card threshold, so no site-card barrier flag fired. The dual-ring geometry is therefore the more legible D3 teaching artifact for v0, while the severed-population threshold remains implemented and test-covered but empirically conservative.

## 2026-08-01 — Milestone 5 D6 app shell
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** single-pass implementation plus D6 smoke-test follow-up
- **Key decisions made:** followed the Industry pattern literally with a thin `app.py`, page modules in `pages/`, and a `shared_ui.py` layer that owns site selection, cached payload loading, the reusable context map, and chart-engine rendering helpers; populated `site_jacksonville_v0.yaml` with the already-validated Baymeadows coordinates so the app can run without a live geocoder dependency; kept the Market tab intentionally compact and flagged it as a candidate for a reusable Metro Deep Dive summary component rather than growing a Place Intelligence-specific one-off
- **Notes:** `metro-deep-dive/tests/test_pi_d6.py` now smoke-tests each tab against both populated and incomplete payloads. The remaining manual D6 validation is to run the Streamlit app against a second Jacksonville address and confirm the output changes correctly with no code changes.

## 2026-08-01 — Second-site config follow-up
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** validation hardening
- **Key decisions made:** added `site_jacksonville_downtown_v0.yaml` as a second manual-override Jacksonville config using Census geocoder coordinates for `1 E Independent Dr, Jacksonville, FL 32202`; extended the site-config tests so the D6 shell cannot silently stop discovering multi-site configs
- **Notes:** this makes the app and artifact builder concretely multi-site at the config layer, which is the precondition for the final live downtown run. The remaining unchecked piece is still the full end-to-end artifact/Streamlit validation for the downtown config against live inputs.

## 2026-08-03 — Baymeadows integrated UI QA review
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** manual reviewer feedback capture after the page-contract refactor
- **Key decisions made:** recorded the first integrated UI review directly in the repo before another implementation pass so design, data, and performance issues can be triaged separately instead of getting mixed together during QA.
- **Notes:** reviewer feedback grouped by page:
  - Overview:
    - top metric row is visually cramped and should use smaller typography and/or a two-line layout
    - node typology needs a clear definition because it is heuristic, not parcel-assessor land use
    - population percentile benchmark is misleading because a multi-tract ring total is being compared to tract rows
    - homepage map should likely suppress tract fill, flood, and severed-area overlays by default
    - POIs should move closer to reader-facing Overture categories rather than only internal competitive/complementary/anchor groupings
    - roads need clearer taxonomy and AADT context
    - county boundaries would help map readability
    - headline-table sources should show actual source systems rather than internal table names
    - flood interpretation can likely be folded into plain-language copy rather than a separate flags/caveats section
  - People:
    - benchmark table should move to the top
    - KPI source labels should use actual source systems
    - jobs/workers divergence section needs clearer explanatory copy
  - Place:
    - shared map currently exceeds Streamlit message limits when too many layers/features are included
    - POI mix should move closer to reader-facing Overture categories
    - frontage trend chart is empty and needs either a fix or removal
    - barrier/severance table is too long and should be removed until the severance story is redesigned
    - flood section reads as broader environmental risk and should be renamed accordingly
  - Market:
    - employment shares are mis-scaled in the UI
    - housing and rent trend visuals are empty despite underlying CBSA data being present
    - GDP mix is unavailable and needs investigation before it can be trusted on-page
  - Methods:
    - no major issues flagged in the first review pass

## 2026-08-03 — Streamlit Cloud publish bundle for Baymeadows v0
- **Agent / model:** Codex GPT-5
- **Turns / iterations:** deployment-prep refactor
- **Key decisions made:** kept the app on a file-artifact contract rather than packaging a publish DuckDB because the page-contract JSONs and slim map assets are already small and easier to debug on Streamlit Cloud; added a read-side auto-detect path so the app prefers `cloud_bundle/site_artifacts/<site_id>/` when present; added `build_cloud_bundle.py` to materialize a slim deployment bundle and intentionally excluded `map/flood.geojson` because it drove nearly all artifact size without adding value to the current UI.
- **Notes:** the Baymeadows `cloud_bundle/` is about 12 MB versus roughly 166 MB for the full local artifact tree. The cloud bundle keeps page JSONs, small map assets, and copied site config metadata while leaving the heavier intermediate build products behind.
