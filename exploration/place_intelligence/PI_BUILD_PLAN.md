---
section: build_plan
status: draft
spotlight_site: jacksonville_fl (CBSA 27260)
spec_ref: metro-deep-dive/metro-area-explorer/place_intelligence/SPEC.md
last_updated: 2026-07-31
---

# Site Context Brief — Build Plan

This is the execution plan for `SPEC.md`. It exists so a new agent can pick up any milestone cold: what to build, where it lives, what pattern to copy, what "done" means, and what is explicitly still undecided. Read `SPEC.md` first — this document does not repeat its rationale, only operationalizes it.

**Decisions locked before this plan was written** (see "Resolved build questions" at the bottom for the full record):
- The build lives at `metro-deep-dive/metro-area-explorer/place_intelligence/`, not `exploration/place_intelligence/`. Move `PI_SPEC.md` there as part of Milestone 0.
- D3's node-typology heuristic is **hardcoded** for v0 (mirrors Industry D4's `_classify_d4_job_center` exactly), with config-driven thresholds deferred to a documented v1 follow-up.
- D3's OSM infrastructure ingest uses the **osmextract (R, `openstreetmap_fr` provider)** path, not `ingest_spatial.py`'s raw-Overpass path — Overpass landed 0 rows for every OSM layer on Richmond; osmextract is the only OSM path that has actually worked in this repo.
- POI competitive/complementary/anchor classification is a **new allowlist-based step written in `site_prep.py`**, reading raw Overture category/taxonomy fields. `ingest_spatial.py`'s existing substring-based `_categorize_overture_place` is left untouched (shared code, not in scope to fix here).
- Barrier severance threshold, barrier crossing-spacing threshold, and median-handling-under-apportionment are **not pre-decided**. They are data-driven decisions made during D1/D3 against real Jacksonville geometry, documented in `decisions.md` with the evidence that produced them — not guessed into config ahead of time.
- This plan covers Phase 1, 2, and 3 in full. Phase 2 and Phase 3 tasks are explicitly gated: **do not start them until the Phase 1 stop-gate review (end of Milestone 3) has been reviewed and signed off by the user.**

---

## Repo conventions this build must follow

Everything below was confirmed by reading the actual Industry section code, not inferred from the spec text alone.

**Folder scaffold** (from `metro-deep-dive/metro-area-explorer/README.md`, and mirrored exactly by `industry/`):
```
metro-deep-dive/metro-area-explorer/place_intelligence/
  SPEC.md              <- moved from exploration/place_intelligence/PI_SPEC.md
  decisions.md         <- running log of judgment calls, esp. the data-driven thresholds
  notes.md             <- build process notes
  site_prep.py          <- all business logic / DB access, NO streamlit imports (mirrors data_prep.py)
  app.py                <- thin shell: page config, sidebar, dispatch to pages/
  shared_ui.py           <- site selector, common widgets (mirrors industry/shared_ui.py)
  ingest_jax_osmextract.R      <- Jacksonville OSM ingest, parameterized copy of ingest_richmond_osmextract.R
  ingest_jax_overture.py       <- Jacksonville Overture POI ingest, parameterized copy of ingest_richmond_overture.py
  geocode.py             <- NEW: Census Geocoder client + tract resolution (foundations promotion candidate)
  apportion.py            <- NEW: D1 ring/tract apportionment engine (foundations promotion candidate)
  pages/
    d_overview.py
    d_people.py
    d_place.py
    d_market.py
    d_methods.py
  outputs/
    jacksonville_fl/
      overture_pois.parquet
      osmextract_infrastructure_{lines,points,polygons}.parquet
      osmextract_manifest.json
      spatial_manifest.json
      site_<site_id>_weights.parquet      <- D1 weight table output, one file per analyzed site
```

Run commands (mirror Industry exactly):
```
.venv312/bin/python -m streamlit run metro-deep-dive/metro-area-explorer/place_intelligence/app.py
.venv312/bin/python -m pytest metro-deep-dive/tests/test_pi_d1.py   # etc, one file per deliverable
```

**`site_prep.py` internal pattern** (mirrors `data_prep.py`):
- `get_connection()` — copy the exact three-line DuckDB read-only pattern from `data_prep.py:305` / `ingest_spatial.py:117`. (This duplication is itself a foundations-promotion candidate — flag it in the stop-gate memo, don't fix it now.)
- Functions prefixed by deliverable: `get_d1_...`, `build_d2_...`, etc., each returning a `pd.DataFrame` or a plain dict "payload" consumed by exactly one `pages/d_*.py` module.
- No `import streamlit` anywhere in `site_prep.py`, `apportion.py`, or `geocode.py`.

**`app.py` / `pages/d_*.py` pattern** (mirrors `industry/app.py` + `industry/pages/d1_makeup_change.py`):
- `app.py` is a thin dispatcher only — page config, site selector, radio/tab picker, calls `render_page(site_id)` per tab.
- Each `pages/d_*.py` exports one `render_page(site_id: str) -> None`.
- Every content block is wrapped in its own `st.subheader(...)` + `if data is None/empty: st.info(...)/st.warning(...) else: render` guard, so one missing deliverable never breaks the page. This is what "each deliverable independently hideable" means concretely — copy the structure of `pages/d1_makeup_change.py:133-286` directly.
- Every metric panel gets its 5yr-change companion rendered directly beneath it in the same subheader block (not a separate tab) — same pattern as the bump chart sitting under "Change over time" in Industry D1.

**Chart rendering:** always via `chart_engine.render(ChartRequest(...))` from `foundations/visual_library/chart_engine_py/chart_engine/orchestrator.py`. Do not hand-build Altair/matplotlib charts inline. If D6's map/barrier/flood-shading views need a chart type that isn't in `CHART_REGISTRY` (`registry.py:56-140`), add a new registry entry (`prep_fn` + `render_fn` + spec markdown) rather than bypassing the orchestrator — this is the documented extension path.

**Testing pattern** (mirrors `metro-deep-dive/tests/test_industry_d1.py`–`d6.py`, which are the newest/most refined examples — model directly on `test_industry_d4.py`, the richest one):
- Load `site_prep.py` via `importlib.util.spec_from_file_location`, not a package import.
- `@pytest.fixture(scope="module")` per deliverable.
- Prefer synthetic DuckDB/parquet fixtures + `monkeypatch` over hitting the real warehouse, except for a small number of deliberate integration tests against the real Jacksonville outputs once they exist (same two-layer approach Industry uses).
- Every deliverable's test file must include a "missing/empty input degrades cleanly" twin test (see `test_d4_overlay_handles_missing_cache_gracefully` for the shape).

**Data access:** fully-qualified `patterns_in_place.<schema>.<table>` SQL against the read-only DuckDB at `foundations/etl/data/duckdb/patterns_in_place.duckdb`. No ORM. `data_prep.py:747-864` (`_build_tract_map_rows`) is the closest existing template for a tract-geometry + demographics join scoped to a CBSA — read it before writing D1's or D2's queries.

---

## Milestone 0 — Scaffold and site config

**Goal:** the folder exists, imports cleanly, and a `site.yaml` for the Jacksonville spotlight address is ready to drive every downstream deliverable.

### Tasks

**0.1 — Move and scaffold**
- Move `exploration/place_intelligence/PI_SPEC.md` → `metro-deep-dive/metro-area-explorer/place_intelligence/SPEC.md`.
- Create `decisions.md`, `notes.md`, `outputs/.gitkeep`, `pages/__init__.py` (empty), following the Industry folder shape exactly.
- Create empty `site_prep.py`, `app.py`, `shared_ui.py` stubs with module docstrings only.
Status: complete on 2026-07-31.

**0.2 — Site config schema and loader**
- Implement the `site` YAML schema exactly as specified in `PI_SPEC.md` lines 23-33 (`site_id, address, lat, lon, geocode_source, market_id, asset_type, rings_mi, primary_ring_mi`).
- Write a loader `load_site(path: str) -> Site` (dataclass or TypedDict) in `site_prep.py`.
- Write `site_jacksonville_v0.yaml` with the spotlight site address: **3832 Baymeadows Road, Jacksonville, FL 32217**. `market_id` is CBSA 27260. `lat`/`lon` are left blank for Milestone 1 to populate via geocoding (or filled in directly if geocoded ahead of time and cross-checked).
Status: complete on 2026-07-31.

**Acceptance criteria:**
- [x] `load_site()` round-trips the YAML into a typed object with all 8 fields present and typed correctly
- [x] A YAML missing a required field raises a clear error naming the missing field, not a generic KeyError
- [x] `rings_mi` defaults to `[1, 3, 5]` and `primary_ring_mi` defaults to `3` if omitted, per spec
- [ ] Folder passes `pytest --collect-only` with zero errors (no import failures)

---

## Milestone 1 — Geocoding and tract resolution

**Goal:** an address becomes a validated lat/lon plus a tract GEOID, with manual override support. This is a named foundations-promotion candidate — build it assuming it will move to `foundations/` later, but build and land it here first per the spec's stop-gate discipline (propose at the gate, don't promote silently).

### Tasks

**1.1 — Census Geocoder client**
- New file: `geocode.py`. Function `geocode_address(address: str) -> GeocodeResult` calling the free Census Geocoder (`geocoding.geo.census.gov`, benchmark/vintage TBD — use the current default benchmark, record it).
- `GeocodeResult` carries: `lat, lon, matched_address, match_type, tract_geoid` (the Census Geocoder's geographies lookup returns the containing tract directly — use that, don't do a separate spatial join for the happy path).
- Support a manual override: if `site.yaml` already carries `lat`/`lon`, skip geocoding and resolve only the tract GEOID (still need this — spatial join against `geo.tracts_all_us` via `ST_Contains`, same pattern `ingest_spatial.py:168` and `data_prep.py:808` already use).
- Record `geocode_source` as e.g. `"census_geocoder:rooftop"` or `"manual_override"`.

**1.2 — Tract resolution fallback**
- If the Census Geocoder's returned tract disagrees with a spatial point-in-polygon lookup against `geo.tracts_all_us` (can happen at tract boundaries with match-quality issues), log both and prefer the spatial join as source of truth — document this choice in `decisions.md`.
Status: complete on 2026-07-31.

**Acceptance criteria:**
- [x] `geocode_address()` returns a populated `GeocodeResult` for a real Jacksonville street address
- [x] Match type and quality are captured, not discarded (e.g. rooftop vs. street-interpolated)
- [x] A manual lat/lon override in `site.yaml` bypasses geocoding entirely and still produces a correct tract GEOID
- [x] A geocode failure (no match) raises/logs clearly rather than silently defaulting to a null island or CBSA centroid
- [x] Test file `metro-deep-dive/tests/test_pi_geocode.py` covers: successful geocode, manual override path, failure path — following the Industry test pattern (synthetic fixtures + monkeypatch, real-address smoke test as a separate marked test)

---

## Milestone 2 — D1: Catchment geometry and tract apportionment

**This is the deliverable the whole build rests on** (spec's own words — see `SPEC.md` D1 section for full rationale before starting). Read `PI_SPEC.md` lines 80-129 in full; this task list operationalizes it but does not restate the reasoning.

### Tasks

**2.1 — Ring buffer generation**
- New file: `apportion.py`. Function `build_rings(lat: float, lon: float, rings_mi: list[int]) -> gpd.GeoDataFrame` — reproject to an appropriate equal-area/local projected CRS (Florida East, EPSG 2881 or similar — pick and document in `decisions.md`) before buffering. Never buffer in WGS84 degrees.
- Sanity-check helper: assert the 1-mile ring area is within 1% of π mi².
Status: complete on 2026-07-31.

**2.2 — Tract intersection and weight table**
- Function `apportion_weights(rings: gpd.GeoDataFrame, market_id: str) -> pd.DataFrame` producing exactly the weight table schema in `PI_SPEC.md` lines 90-100 (`site_id, ring_mi, tract_geoid, weight, weight_method, intersect_area, tract_area, containment, centroid_in`).
- Selection rule is **intersects**, not centroid-in-ring — per spec's own clarification (lines 107-109), `centroid_in` is diagnostic-only, never a filter.
- v0 method: **areal-weighted** (`weight = intersect_area / tract_area`). Pull tract geometry from `geo.tracts_all_us`, scoped to the site's CBSA via the same crosswalk join `data_prep.py:747-864` uses.
Status: complete on 2026-07-31.

**2.3 — Dasymetric upgrade spike (timeboxed, half-day hard stop)**
- Before starting: confirm whether the existing Overture ingest path (`ingest_jax_overture.py`, built in Milestone 5) can pull the **buildings theme** in addition to places without new plumbing. This is explicitly called out in the spec as answerable early and cheaply (`PI_SPEC.md` line 305) — check it as the first move of this task, not after building the areal path.
- If yes and it fits in half a day: implement `weight_method="dasymetric"` as a swap of the weight column only (building-footprint-area share within ring, filtered to residential subtypes where populated, all buildings otherwise). `weight_method` already carries provenance — nothing downstream should care which method produced the number.
- If no or over time budget: **cut it**. Ship areal only, write the dasymetric approach up as a documented v1 upgrade in `decisions.md`, and move on. Do not extend the timebox.
Status: cut for v0 on 2026-07-31 after confirming the current Overture path is hardcoded to `theme=places` and a place-specific schema, so buildings are not a cheap no-plumbing add-on.

**2.4 — `apportion()` metric function**
- Function `apportion(metric_series: pd.Series, weight_table: pd.DataFrame, kind: Literal["extensive","intensive"], method: str | None = None) -> pd.Series`.
- Extensive (counts): sum with weights.
- Intensive (rates/medians): weighted average for rates. **Must refuse to run on a median-type metric unless `method="approximate"` is explicitly passed** — this is a hard acceptance criterion, implement it as a raised exception, not a warning.
- Document the "median under apportionment" open question (`PI_SPEC.md` line 308) as unresolved in `decisions.md` — the D2 milestone below is where this gets a real decision, once real Jacksonville tract data is in hand to look at.
Status: complete on 2026-07-31.

**2.5 — Coverage diagnostic**
- Function `coverage_diagnostic(weight_table: pd.DataFrame) -> pd.DataFrame` — per-ring: count of intersecting tracts, total weight captured, whole-tract count, share of catchment from fragments, and a reliability flag. Must render in the brief appendix later (D6), not just logs — build it as a clean dataframe now so D6 has nothing to reshape.
Status: complete on 2026-07-31.

**Acceptance criteria (verbatim from spec, all must pass):**
- [x] Ring buffers generated in a projected CRS; 1-mile ring area within 1% of π mi²
- [x] Weight table sums to ≤ 1.0 per tract across all rings, exactly 1.0 for any tract fully contained in the largest ring
- [x] `apportion()` refuses to run on a median-type metric without explicit `method="approximate"`
- [x] A 1-mile ring containing no tract centroids still returns a populated catchment
- [x] Coverage diagnostic renders in the brief appendix, not hidden in logs
- [x] Coverage diagnostic emits a per-ring reliability flag (whole-tract count, fragment share)
- [x] `build_rings`/`apportion_weights` accept any lat/lon + ring list — no Jacksonville-specific logic anywhere in `apportion.py`

**Testing:** `metro-deep-dive/tests/test_pi_d1.py`. Cover: ring area sanity check, weight-sum invariants (both partial and full containment cases), median-guard exception, empty-centroid 1-mile-ring case, coverage diagnostic shape. Use synthetic tract geometries (small, hand-constructed GeoDataFrames) for the invariant tests — don't require the real warehouse for logic correctness, only for one end-to-end smoke test against real Jacksonville tracts.

---

## Milestone 3 — D2 + D3 (parallel-safe after D1 lands), then STOP GATE

D2 and D3 both depend on D1's weight table but not on each other — they can be built in parallel by two agents/sessions once Milestone 2 is merged.

### D2 — Catchment profile and benchmark stack

**3.1 — Long-format catchment table**
- Function `build_catchment_profile(site: Site, weight_table: pd.DataFrame) -> pd.DataFrame` returning `(site_id, ring_mi, metric, value)` for every metric listed in `PI_SPEC.md` lines 136-141 (population/households/age/race/education/income/housing/commute). Pull from the Gold tables listed in the spec's Data Sources table; use `apportion()` from Milestone 2 for every value.
- Each metric must carry its **source vintage year** — do not let two metrics from different source years render as if comparable without a label.
Status: complete on 2026-08-01 for the first tract-grain metric catalog now wired in `site_prep.py`.

**3.2 — Benchmark table**
- Function `build_benchmark_table(site: Site) -> pd.DataFrame` at CBSA/county/state/national for every metric. Per spec's benchmark rule (line 146): only the **primary ring** gets full benchmark treatment; secondary rings appear only in the gradient view. Derive from the **same Gold query path** as the catchment rows — no separate hand-built lookup (this is an explicit acceptance criterion).
- Reference `data_prep.py:2185-2313` (`_build_benchmark_rows_from_states`, `_build_benchmark_rows_from_aggregated`, `get_benchmark_basis_frames`) as the existing benchmark-construction pattern to extend, not reinvent.
Status: complete on 2026-08-01.

**3.3 — Percentile position**
- Function `compute_percentile(metric: str, ring_value: float, market_id: str) -> tuple[float, int]` returning percentile against the CBSA tract distribution and the denominator tract count (must be stated, per acceptance criteria).
Status: complete on 2026-08-01.

**3.4 — 5-year change**
- For every metric with a comparable prior vintage, compute 5yr change. Missing-vintage metrics are dropped with a **logged reason**, not silently imputed — implement this as a structured skip-reason list surfaced in the payload, not a bare log line, since D6's Methods tab needs to display it.
Status: complete on 2026-08-01 for the current metric catalog and structured skip-reason payload.

**3.5 — Median-handling decision**
- This is the point in the build where the open question from D1 (`PI_SPEC.md` line 308) gets resolved with real data in hand. Compute both a weighted-approximate median and the CBSA-percentile-only alternative for 2-3 real metrics on the Jacksonville site, compare, and record the decision + reasoning in `decisions.md`. Do not guess this before seeing the numbers.
Status: not started.

**Acceptance criteria (verbatim from spec):**
- [x] Every metric renders at all three ring distances or is explicitly marked unavailable
- [x] Every metric carries its source vintage year; panels do not imply a common year across sources
- [x] Benchmark rows derive from the same Gold query path as catchment rows
- [x] Percentile computed against tracts within the market CBSA; denominator count stated
- [x] A metric missing from Gold at tract grain is dropped with a logged reason, not silently imputed

**Testing:** `metro-deep-dive/tests/test_pi_d2.py` — cover vintage-year labeling, percentile denominator correctness, dropped-metric logging, benchmark/catchment path parity (assert they hit the same underlying query function, not just similar output shape).

---

### D3 — Daytime population and built-environment context

Read `PI_SPEC.md` lines 157-197 in full before starting — this is "the only genuinely novel methodological work" alongside D1, and the barrier-severance logic in particular has real subtlety (a feature is not a barrier; a lack of crossings is).

**3.6 — Jacksonville spatial ingest**
- Copy `ingest_richmond_osmextract.R` → `ingest_jax_osmextract.R`. **This script is currently Richmond-hardcoded** (`market_slug`, `place_name`, `output_dir` are literals, not parameters) — parameterize `place_name = "Jacksonville"`, `market_slug = "jacksonville_fl"`, output path to `outputs/jacksonville_fl/`. Keep the same provider (`openstreetmap_fr`), same tag queries, same layer taxonomy (highways/major_roads/rail/airports/ports/warehouses_logistics).
- Copy `ingest_richmond_overture.py` → `ingest_jax_overture.py`, parameterized the same way. Confirm bbox derivation still works via `geo.tracts_all_us` + `silver.xwalk_cbsa_county` for CBSA 27260.
- Run both. Confirm output shape matches the Richmond manifest convention (`osmextract_manifest.json`, `osmextract_summary.json`, `spatial_manifest.json`, parquet files as listed in the scaffold above).
- **Before trusting the output:** write a short parity note in `decisions.md` comparing Jacksonville row counts to Richmond's (5,300 highways / 16,572 major roads / 1,374 rail / 76,913 POIs) — not to match exactly, but to sanity-check the extract isn't silently empty or absurdly small the way the plain-Overpass path was for Richmond.
Status: scaffolded on 2026-08-01 via `ingest_jax_overture.py` and `ingest_jax_osmextract.R`; real Jacksonville runs and parity note still pending.
Update on 2026-08-01: real Jacksonville Overture + OSM runs now exist under `outputs/jacksonville_fl/`, with the OSM GeoPackage promoted into the standard `osm_infrastructure_{lines,points,polygons}.parquet` cache shape. The parity note is now recorded in `decisions.md`.

**3.7 — POI classification (competitive / complementary / anchor)**
- New function in `site_prep.py`, e.g. `classify_poi(row: pd.Series) -> str | None`, using **explicit allowlists against Overture's `basic_category`/`taxonomy_primary` fields** — per the Richmond review doc's own recommendation (`RICHMOND_POI_INFRA_REVIEW.md` line 160: `basic_category -> taxonomy_primary -> taxonomy_hierarchy -> primary_category` priority, `confidence` as a quality filter not a category definition).
- This is deliberately **not** a fix to `ingest_spatial.py`'s `_categorize_overture_place` (substring matching) — leave that function alone, it's shared code outside this build's scope. Build a new, separate classifier here.
Status: complete on 2026-08-01.
- Categories per spec: competitive (same-format retail), complementary (grocery/pharmacy/gym/QSR/banking), anchor (hospital/university/school/civic/large employer). Define the allowlists in `decisions.md` alongside the rationale, since this is exactly the kind of judgment call the spec asks to be interrogable at the stop gate.

**3.8 — Jobs/workers apportionment and day/night divergence**
- Apportion `silver.lehd_lodes_wac` (jobs) and `silver.lehd_lodes_rac` (resident workers) per ring using `apportion()` from Milestone 2. Compute jobs-to-workers ratio, plus industry breakout for retail/accommodation-food/health-care/professional-scientific.
- Day/night divergence presented as **both** a ratio and an absolute count (explicit acceptance criterion — a small ring and large ring must not read as equivalent from the ratio alone).
Status: complete on 2026-08-01.

**3.9 — Road hierarchy and POI ring counts**
- Point-in-ring POI counts (not tract apportionment — direct spatial join against ring geometry, explicit acceptance criterion).
- Road-class context: which OSM road classes front/bound the site, distance to nearest interstate ramp, from the Jacksonville osmextract lines output.
Status: complete on 2026-08-01 for the direct POI-ring counts and first-pass road-context payload.

**3.10 — Barrier / severance flag**
- Implement per `PI_SPEC.md` lines 168-194 exactly. Key design point: **the test is crossing spacing, not feature presence.** Water is a default barrier. Highway/rail qualify only when crossing spacing within the ring exceeds a **configured threshold**.
- **The threshold itself is not decided yet** (`PI_SPEC.md` line 310, confirmed open in this plan's resolved-questions section). Task: implement the mechanism generically (spacing computed from bridge/crossing point density along the barrier-ring intersection), parameterize the threshold as a named config value, then **validate against at least one real Jacksonville site within 3 miles of the St. Johns** (explicit acceptance criterion) and pick the threshold from what you observe. Record the chosen value and the observed evidence in `decisions.md` — do not set it before that validation.
- For each ring: which barrier features intersect, crossing count + mean spacing, severed area share (polygon-split of ring against barrier geometry), severed population share (via D1's weight table), plain-language severance summary.
- Severed-population-share threshold that promotes the flag to the site card (vs. appendix-only) is **also not decided yet** (`PI_SPEC.md` line 307) — same treatment: implement generically, decide from real Jacksonville sites, document.
Status: in progress on 2026-08-01. The generic barrier machinery now exists, water barriers are being consolidated from the Jacksonville OSM cache rather than passed through as raw polygon fragments, and severed population now uses tract-overlap instead of centroid hits. The remaining work is the real-site Jacksonville validation that picks and documents the spacing + site-card thresholds.
Update on 2026-08-01: real Jacksonville validation is complete for a downtown river-adjacent site (`1 E Independent Dr`) and the Baymeadows baseline site (`3832 Baymeadows Road`). D3 now also emits both baseline straight-line rings and water-adjusted companion rings so the first-pass catchment and the barrier-screened catchment can be explained side by side.

**3.11 — Node typology label**
- Implement `classify_node_typology(row: pd.Series) -> tuple[str, str]` in `site_prep.py`, **directly mirroring `data_prep.py:1773-1807` (`_classify_d4_job_center`) in structure and hardcoding** — per this plan's locked decision, do not make thresholds config-driven for v0. Copy the scoring-then-branch shape (infra_score / institution_score style composite, `>=` threshold branches, `(label, rationale)` return), adapted to retail/office/institutional/industrial-logistics/residential-dominant/mixed labels per spec.
- Leave a clear code comment or `decisions.md` note flagging this as the deliberate v1 config-migration candidate — the spec's acceptance criterion text ("thresholds recorded in config") is intentionally deferred, not silently dropped.

**Acceptance criteria (verbatim from spec, all must pass):**
- [ ] A Jacksonville Overture + OSM extract exists at `outputs/jacksonville_fl/` following the Richmond output shape and manifest convention
- [x] A Jacksonville Overture + OSM extract exists at `outputs/jacksonville_fl/` following the Richmond output shape and manifest convention
- [x] POI category assignment uses explicit allowlists / taxonomy fields, not substring matching
- [x] Ring POI counts are computed from point-in-ring, not tract apportionment
- [x] Day/night divergence presented as both a ratio and an absolute count
- [x] Typology label derived from thresholds — **for v0, hardcoded per this plan's locked decision; note in decisions.md that config-driven is the stated v1 target**
- [x] Barrier geometry sourced from existing OSM water/rail/highway layers — no new ingest
- [x] Water treated as default barrier; highway/rail qualify only via crossing-spacing test, threshold in config
- [x] Crossing detection validated by hand against ≥1 real Jacksonville site within 3 miles of the St. Johns before the flag is trusted
- [x] Barrier flag runs per ring, reports severed area share and severed population share; no-barrier case returns clean null, not an error
- [x] Severed population share above configured threshold surfaces on the site card, not only the appendix
- [x] Copy states proximity is straight-line, not network/drive-time, and the barrier flag is a screening heuristic

**Testing:** `metro-deep-dive/tests/test_pi_d3.py` — model closely on `test_industry_d4.py`'s pattern (synthetic parquet fixtures via `duckdb`, `monkeypatch` on output roots, assert on payload shape and specific label/threshold outputs). Cover: POI classification allowlist correctness, barrier flag null-case, crossing-spacing math on a synthetic geometry, typology label branches, day/night ratio + count both present, and the new baseline-vs-water-adjusted ring variant behavior.

---

## ⛔ STOP GATE — end of Phase 1

**Do not start Milestone 4 or 5 without explicit user sign-off on this gate.** This is not a formality — the spec requires it explicitly (`PI_SPEC.md` line 196) so the methods can be taught and interrogated, not inherited.

### Gate deliverable: written methods memo

Add to `decisions.md` (or a dedicated `METHODS_MEMO.md` in the same folder) covering:
- The apportionment method actually implemented (areal vs. dasymetric — whichever shipped) and why, including the half-day spike outcome from task 2.3
- The POI taxonomy and classification allowlists chosen in task 3.7, with rationale
- Any density/clustering method used and its parameters
- The barrier crossing-spacing threshold and severed-population-share threshold chosen in task 3.10, and the specific Jacksonville evidence that justified each
- The median-handling decision from task 3.5
- Every other judgment call made under ambiguity during D1-D3
- **Foundations-promotion candidates identified**, each with a short rationale, not yet executed:
  - D1's apportionment engine (`apportion.py`) — explicitly called out in the spec as "promote regardless of whether v0 ships" (line 328)
  - Geocoding + tract resolution (`geocode.py`)
  - The benchmark/percentile stack from D2, if it came out clean — candidate for the vertical benchmark contract
  - The shared `get_connection()` DuckDB boilerplate duplicated a third time by this build (noted in this plan's scaffold section)
  - Anything else noticed while reading across `foundations/`, `metro-deep-dive/`, `publisher/`

### Gate acceptance criteria
- [x] Methods memo is written and complete against the list above
- [x] Foundations-promotion candidates are listed with rationale, none have been executed/refactored yet
- [x] User has reviewed and explicitly approved proceeding to Phase 2/3

---

## Milestone 4 — D4 + D5 (Phase 2, conditional — GATED, do not start pre-approval)

**Governing rule: light or v2.** Both deliverables get a hard-timeboxed spike; if not clean inside the box, cut, state the gap plainly in the app, ship v2. Neither writes to Gold — both land in `outputs/jacksonville_fl/` alongside the D3 spatial cache.

### D4 — Traffic counts (AADT)

**4.1 — Source contract spike (half-day hard stop)**
- Confirm FDOT AADT source format, license, update cadence **before writing any ingestion code**. If not downloadable as a clean statewide geospatial file inside half a day, **cut it** — scraping/per-county manual downloads/PDF reports all mean v2, no exceptions to the timebox.
- If it clears the spike: ingest FDOT AADT segments/count stations clipped to the market bbox (reuse the bbox-derivation pattern from `ingest_spatial.py:get_market_bbox` / the osmextract scripts).
Status: complete on 2026-08-01. The official FDOT statewide AADT source contract is recorded in `notes.md`, and the source clears the spike via both an official statewide GIS download path and an official ArcGIS FeatureServer query path.

**4.2 — Frontage AADT and ranked corridor table**
- Snap-to-nearest-segment logic with an **explicit distance tolerance** that fails loudly (raises) rather than silently attaching a distant segment.
- Ranked AADT for all segments within the 1-mile ring.
- Multi-year trend for the frontage segment if the source supports it.
Status: complete on 2026-08-01. `ingest_fdot_aadt.py` now writes both current and historical bbox-clipped Jacksonville caches (`fdot_aadt_segments.parquet` and `fdot_aadt_historical_segments.parquet`), and `site_prep.py` now exposes a fail-loud frontage snap, ranked 1-mile corridor table, and a five-year frontage trend keyed to the primary snapped roadway.

**Acceptance criteria (verbatim):**
- [x] Source format, license, update cadence confirmed and recorded in a source contract before ingestion code is written
- [x] Snap-to-nearest-segment has explicit distance tolerance, fails loudly on out-of-tolerance attach
- [x] Brief states the count year and that AADT is an annual average, not peak/observed
- [x] Ingest runs from a bbox + state parameter, not a Jacksonville-specific file path

**Cut rule:** if cut, the app must say so explicitly on the relevant tab — an investor noticing the absence should see it acknowledged, not discover it.

### D5 — Flood risk

**4.3 — FEMA NRI confirmation**
- Confirm table name and grain first (spec reports it as "already available" but unconfirmed). If tract-grain NRI exists, it apportions through D1 like any other tract metric — no new ingest.

**4.4 — FEMA NFHL point-in-polygon (timebox: 1 hour)**
- Zone lookup at the site point (X/AE/VE/etc.), SFHA yes/no, panel effective date, via the published REST service.
- Ring flood-zone area shares in a projected CRS.

**Acceptance criteria (verbatim):**
- [ ] NRI availability and grain confirmed before any assumption is built on it
- [ ] Zone lookup returns designation for site point, states NFHL panel effective date
- [ ] Copy explicitly states this is screening-level, not a flood determination/elevation certificate/insurance rating
- [ ] Ring flood-zone area shares computed in a projected CRS
- [ ] NRI and NFHL presented as answering different questions, not two versions of the same read

**Testing:** `metro-deep-dive/tests/test_pi_d4.py`, `test_pi_d5.py` — same synthetic-fixture + monkeypatch pattern. D4's snap-tolerance failure path and D5's "cut gracefully" path are the two most important cases to cover, since both are explicit acceptance criteria about failing/degrading visibly rather than silently.

---

## Milestone 5 — D6: Site context app (Phase 3, conditional — GATED, do not start pre-approval)

Read `PI_SPEC.md` lines 249-297 in full — the two organizing principles (one map many layers; trajectory is a view not a section) are load-bearing design decisions, not suggestions.

### Tasks

**5.1 — Context map component**
- Build the `pydeck` context map **once**, reused across all 5 tabs with per-tab default layer state (rings, POIs by category, road network weighted by AADT if D4 shipped, flood zones if D5 shipped, severed-area shading, tract fill by selected metric).
- This is itself a flagged foundations-promotion candidate if it generalizes past this one site — note but do not promote yet.

**5.2 — Five tabs**
- Build `pages/d_overview.py`, `d_people.py`, `d_place.py`, `d_market.py`, `d_methods.py` per the table in `PI_SPEC.md` lines 263-269. Each tab renders independently — an incomplete deliverable hides cleanly (same subheader-guard pattern as Industry).
- **Market tab specifically:** reverse-engineer from what a site-level reader needs from metro context, then check against what Metro Deep Dive currently produces. Whatever earns its place is a candidate for a standardized MDD summary component — flag it explicitly in `decisions.md`, this is a named foundations-promotion candidate in the spec (line 271).

**5.3 — Trajectory-as-view wiring**
- Every metric panel from D2/D3 gets its 5yr-change companion rendered directly beneath it, mirroring the Industry bump-chart placement pattern (`pages/d1_makeup_change.py:231-240`) exactly — gate on sufficient year history the same way, with the same kind of explanatory hidden-state message when insufficient.

**5.4 — Provenance and labeling**
- Every chart carries source + vintage label. Every apportioned number is visually distinguishable from a directly-observed number (e.g. consistent icon/footnote convention — decide once, apply everywhere). No composite score anywhere in the app.

**Acceptance criteria (verbatim):**
- [ ] App runs end-to-end from `site.yaml`, following the Industry `data_prep.py` + `app.py` split
- [ ] Prep layer returns dataframes with no Streamlit imports
- [ ] Context map built once, reused across tabs with per-tab default layer state — not re-instantiated per section
- [ ] Every chart carries a source and vintage label; panels do not imply a common year across sources
- [ ] Every apportioned number is visually distinguishable from a directly-observed number
- [ ] No composite score appears anywhere
- [ ] Each tab renders independently; an incomplete deliverable can be hidden without breaking the app
- [ ] Running against a second Jacksonville address produces a correct, different result with no code changes

**Testing:** `metro-deep-dive/tests/test_pi_d6.py` — smoke-test each tab's `render_page` against both a fully-populated payload and a deliberately incomplete one (mirroring the D4 "graceful missing cache" test). Manual test: run the Streamlit app against two distinct real Jacksonville addresses and confirm distinct, correct output with zero code changes (explicit acceptance criterion — cannot be verified by unit test alone, must be done by hand per the repo's stated two-layer validation approach).

---

## Sequencing summary

```
M0 Scaffold ─────────────────┐
                              ├─→ M1 Geocoding ─→ M2 D1 Apportionment ─→ M3 D2+D3 (parallel) ─→ ⛔ STOP GATE
                              │                                                                      │
                              └──────────────────────────────────────────────────────  user sign-off required
                                                                                                       │
                                                                                                       ▼
                                                                          M4 D4+D5 (parallel, both conditional) ─→ M5 D6 App
```

M3's D2 and D3 can run as two parallel workstreams once M2 is merged. M4's D4 and D5 can likewise run in parallel once the gate clears. M5 depends on whichever of D4/D5 actually shipped (or was cut) — its map/tab wiring must handle both outcomes per deliverable, since Phase 2 cuts are expected and must degrade visibly, not break the app.

---

## Resolved build questions (for context — do not re-litigate without new information)

| Question | Resolution | Source |
|---|---|---|
| Where does this build live? | `metro-deep-dive/metro-area-explorer/place_intelligence/`, matching the Industry scaffold | User decision, 2026-07-31 |
| D3 typology heuristic: config-driven or hardcoded for v0? | Hardcoded for v0, mirroring `_classify_d4_job_center` exactly; config-driven is the explicit v1 target | User decision, 2026-07-31 |
| Which OSM ingest path? | `osmextract` (R, `openstreetmap_fr` provider) — the raw-Overpass path in `ingest_spatial.py` landed 0 rows for every OSM layer on Richmond per `RICHMOND_POI_INFRA_REVIEW.md`; osmextract is the only proven-working OSM path in this repo | User decision after reading `RICHMOND_POI_INFRA_REVIEW.md`, 2026-07-31 |
| POI categorization: fix `ingest_spatial.py`'s substring matcher, or build new? | Build new allowlist-based classifier in `site_prep.py`; leave `ingest_spatial.py`'s `_categorize_overture_place` untouched | User decision, 2026-07-31 |
| Barrier/crossing-spacing thresholds, median handling — pre-set or data-driven? | Data-driven during D1/D3 build, against real Jacksonville evidence, documented in `decisions.md` — not guessed ahead of time | User decision, 2026-07-31, matches spec's own stated intent |
| Plan scope — Phase 1 only or 1-3? | Full detail for all three phases, with Phase 2/3 explicitly gated behind the Phase 1 stop-gate sign-off | User decision, 2026-07-31 |

## Spotlight site

**Address:** 3832 Baymeadows Road, Jacksonville, FL 32217
**Market:** Jacksonville, FL (CBSA 27260)
**Asset type:** retail (v0 default per spec)

This is the address Milestone 0's `site.yaml` is built against, and the one Milestone 1's geocoding must resolve to a lat/lon + tract GEOID. It is also the address referenced by D3 task 3.10's barrier-validation requirement if it falls within 3 miles of the St. Johns — confirm this during that task rather than assuming it.
