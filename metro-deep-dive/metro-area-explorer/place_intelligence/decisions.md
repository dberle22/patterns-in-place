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
