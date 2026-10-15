# Site Intelligence Workbook and Client Brief

Site Intelligence is the product layer that turns a completed site analysis
into an internal review workbook and a forwardable client brief. It consumes
read-only, site-scoped analytical products; it does not run geocoding,
apportionment, live-service queries, or DuckDB writes at notebook load.

## Status

**Status:** Active

**Updated:** 2026-10-07

## How to run it

Epic 1 freezes a read-only adapter over the existing legacy site bundles. Run
the Epic 1--2 focused contract tests with:

```sh
.venv312/bin/python -m pytest metro-deep-dive-program/analyses/explanation/catchment/site_intelligence/test_site_bundle_adapter.py -q
```

The future workbook and static brief will use `.venv-marimo`, `DB_PATH` for
any approved read-only DuckDB checks, and built site bundles selected by an
explicit site identifier.

Start the internal workbook with:

```sh
.venv-marimo/bin/marimo edit metro-deep-dive-program/analyses/explanation/catchment/site_intelligence/SITE_INTELLIGENCE_WORKBOOK.py
```

It reads only site artifacts. It does not open DuckDB, run legacy builders, or
load an unselected map layer.

Render the fixed client brief to an explicit delivery directory with:

```sh
.venv312/bin/python metro-deep-dive-program/analyses/explanation/catchment/site_intelligence/render_client_brief.py --output-dir /tmp/site-intelligence-delivery
```

Use `--site-id jacksonville_fl_12187_beach_blvd_v0` to render the second
validated Jacksonville bundle with the same notebook and renderer.

The command exports static HTML and PDF, then writes `delivery_manifest.json`
with output sizes and SHA-256 checksums. It requires Marimo's local PDF export
dependencies (`nbconvert`, Playwright, and Chromium).

The build-plan acceptance commands are deliberately not executable until the
new notebook and render scripts exist.

## Key docs

1. [SITE_INTELLIGENCE_SPEC.md](SITE_INTELLIGENCE_SPEC.md) — approved product,
   content, data, and delivery contract.
2. [SITE_INTELLIGENCE_BUILD_PLAN.md](SITE_INTELLIGENCE_BUILD_PLAN.md) —
   sequenced handoff tasks and verification gates.
3. [ROADMAP.md](ROADMAP.md) — current next work and deferred-section ledger.
4. [../README.md](../README.md) — the upstream Catchment analytical method.
5. [LEGACY_BUNDLE_CONTRACT.md](LEGACY_BUNDLE_CONTRACT.md) — Epic 1 observed
   legacy schemas, availability behavior, and bundle discovery rule.
6. [site_section_registry.py](site_section_registry.py) — authoritative
   readiness, ownership, promotion gates, and internal deferred-work cards.
7. [site_map_products.py](site_map_products.py) — manifest-first map readers
   and bounded display-only GeoJSON derivatives.
8. [SITE_INTELLIGENCE_WORKBOOK.py](SITE_INTELLIGENCE_WORKBOOK.py) — internal,
   read-only Marimo workbook for selected bundle evidence and deferred work.
9. [SITE_INTELLIGENCE_CLIENT_BRIEF.py](SITE_INTELLIGENCE_CLIENT_BRIEF.py) —
   fixed-configuration, client-safe static brief.

## Depends on / depended on by

Depends on:

- the program Catchment helper and its governed, read-only evidence products;
- temporarily, the legacy Place Intelligence site YAML and materialized
  `site_artifacts/<site_id>/` bundles during migration;
- program-owned POI and Infrastructure source authorities, without rewriting
  their classifications;
- Marimo for workbook review and static delivery export.

The internal workbook and client brief will depend on this folder. No other
analysis should depend on client-rendered tables or maps; reusable methods and
source contracts remain owned by Catchment, Geography, POI, and Infrastructure.
