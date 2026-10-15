# Site Intelligence Build Plan

**Status:** Active

**Updated:** 2026-10-07

## Delivery shape

Build two Marimo-authored surfaces from one site-bundle adapter layer:

- `SITE_INTELLIGENCE_WORKBOOK.py` for internal, interactive review.
- `SITE_INTELLIGENCE_CLIENT_BRIEF.py` for one-site static HTML/PDF delivery.

The plan deliberately keeps incomplete D4/D5/market and method sections in
the workbook's section registry. A client brief receives only sections that
have passed their stated client-readiness gate.

## Epic 1 — Freeze the compatibility contract

- [x] Inventory one complete legacy bundle and record exact schemas, source
  years, null behavior, and file sizes for every product the new surfaces need.
- [x] Define program-owned typed/read-only adapters for identity, overview,
  people, place, market, methods, map manifest, and section status.
- [x] Add contract tests for missing files, missing columns, empty products,
  source/vintage propagation, and adapter-to-artifact value reconciliation.
- [x] Record the legacy bundle manifest/build timestamp in every adapter result.
- [x] Decide and document the temporary bundle discovery rule without adding
  machine-specific paths.

**Done when:** a test can load one complete bundle and a controlled incomplete
bundle, with explicit availability states for both.

**Completed 2026-10-07:** `site_bundle_adapter.py` freezes the read-only
compatibility boundary, and `test_site_bundle_adapter.py` verifies the complete
Baymeadows reference bundle plus controlled missing, invalid, and empty cases.
`LEGACY_BUNDLE_CONTRACT.md` records the observed inventory and temporary
discovery rule.

## Epic 2 — Establish the section registry and map products

- [x] Implement the section registry specified in
  `SITE_INTELLIGENCE_SPEC.md`; add a work-card renderer for `withheld` and
  `method_candidate` sections.
- [x] Assign every current Streamlit section a source contract, readiness
  status, known issue, owner, and promotion gate.
- [x] Split map loading into manifest-first and layer-specific reads.
- [x] Create display-only, size-bounded map assets for the client brief; retain
  analytical geometries unchanged.
- [x] Add map tests for layer selection, display-geometry provenance, and no
  eager read of unselected layers.

**Done when:** the internal surface can list all planned sections, including
incomplete ones, without loading every map asset or fabricating a result.

**Completed 2026-10-07:** `site_section_registry.py` owns the declared
readiness, source contracts, promotion gates, and deferred work-cards.
`site_map_products.py` reads the small map manifest before opening a selected
layer, and creates explicitly bounded display-only GeoJSON derivatives without
rewriting source geometry. Focused tests prove selected-layer loading,
display-asset provenance, and non-eager handling of an invalid unselected
layer.

## Epic 3 — Build the internal workbook

- [x] Create a Marimo notebook with an explicit selected-site control and
  dependent control-value cells.
- [x] Render run status, provenance, limitations, and a client-readiness
  summary before analytical sections.
- [x] Port overview, people/daytime, commercial/physical, market, methods/QA,
  and deferred-ledger sections through adapters only.
- [x] Make maps lazy and purpose-specific; do not port the shared all-layers
  Streamlit map.
- [x] Make every provisional or withheld section visibly explain its missing
  input, known problem, and promotion gate.
- [x] Keep the notebook read-only with respect to DuckDB and artifacts.

**Done when:** an analyst can switch between two built sites, inspect all
section states, and trace any displayed value or caveat to its adapter result.

**Completed 2026-10-07:** `SITE_INTELLIGENCE_WORKBOOK.py` uses one cell for
selected-site, ring, map-layer, and display-metric controls. It reads adapters
only, renders provenance and readiness before the analytical sections, loads
one selected map layer on demand, and exposes provisional/withheld work with
its registered limitation and promotion gate. `marimo check --strict` passes.

## Epic 4 — Build the static client brief

- [x] Create a separate Marimo-authored client brief with one explicit render
  configuration: site id, title, audience, and selected client-ready sections.
- [x] Add narrative copy blocks that distinguish direct observation,
  apportionment, and contextual screening.
- [x] Add static charts and maps with captions, source systems, vintages, and
  limitations.
- [x] Exclude controls, raw diagnostics, provisional/withheld sections, and
  local paths from client output.
- [x] Add an appendix with method, provenance, and availability notes.
- [x] Implement deterministic static HTML and PDF render commands and a
  delivery manifest.

**Done when:** the brief is forwardable as HTML/PDF and can be understood
without a local server, a database, or interactive controls.

**Completed 2026-10-07:** `SITE_INTELLIGENCE_CLIENT_BRIEF.py` has a fixed
Baymeadows render configuration and includes only the two adapter-reconciled
client-ready sections. It provides apportioned people/daytime charts, a
self-contained rings orientation map, source/vintage captions, and a methods
appendix. `render_client_brief.py` produces deterministic HTML/PDF files plus
a checksum-bearing `delivery_manifest.json`; a temporary end-to-end render
succeeded for both formats.

## Epic 5 — Validate, promote, and hand off

- [x] Run the complete path for Baymeadows and a second Jacksonville site with
  no code changes between sites.
- [x] Reconcile every client-visible KPI, table row, chart value, and map
  caption against the adapter contract.
- [ ] Review actual HTML/PDF for layout, page breaks, chart labels, map
  readability, citations, missingness, and no absolute local paths.
- [x] Run focused tests, `marimo check --strict` for both notebooks, and
  `git diff --check`.
- [x] Revisit every provisional section and either promote it to
  `client_ready`, keep it in the workbook with a gate, or remove only the
  unsupported claim—not the registry entry.
- [x] Document remaining legacy dependencies and propose, but do not silently
  perform, source/method promotion into program engines or Foundations.

**Done when:** the two-surface product is reproducible for two sites, client
delivery is static and reviewable, and the workbook retains a truthful ledger
of unfinished sections.

**Validated 2026-10-07:** the same render command produced HTML, PDF, and
checksum manifests for Baymeadows and 12187 Beach Blvd. Client-ready population
and daytime series reconciled to the adapter rows for both sites; the rings
caption reconciled to the map-layer manifest. A regression test preserves the
legacy null `benchmark_level` convention for native catchment rows. The client
brief continues to exclude provisional and withheld registry entries; their
promotion gates and the legacy-bundle migration boundary remain documented in
`site_section_registry.py` and `LEGACY_BUNDLE_CONTRACT.md`. Final
client-facing layout and narrative acceptance remains a human review gate.

## Explicit follow-on work

These are retained as workbook work items, not dropped scope:

- validate and render frontage traffic trends;
- resolve market GDP mix source/units/shares;
- restore and validate CBSA housing/rent series;
- make a method decision on barrier/water companion views;
- test buildings-based dasymetric weighting against areal weighting;
- specify and validate a routed reach method before any access claim.
