# Legacy Bundle Compatibility Contract

**Status:** Active

**Updated:** 2026-10-07

This is the Epic 1 compatibility boundary for Site Intelligence. The adapter
in `site_bundle_adapter.py` is read-only: it never imports a Streamlit page,
rebuilds an artifact, calls a live service, or opens DuckDB.

## Temporary discovery rule

The future workbook supplies an explicit site identifier. The adapter resolves
it in this order:

1. An explicitly passed artifact root, with the bundle at `<root>/<site_id>/`.
2. `SITE_INTELLIGENCE_ARTIFACT_ROOT`, with the same child layout.
3. The legacy publishable cloud bundle in the repository.
4. Exactly one local legacy `outputs/<market>/site_artifacts/<site_id>/` match.

Every candidate must have `manifest.json`. Multiple local-output matches are
unavailable rather than arbitrarily selecting a market. This is an interim
reader rule only; it neither changes legacy discovery nor establishes a
long-term program artifact location.

## Observed complete-bundle inventory

The frozen reference is the built `jacksonville_fl_baymeadows_v0` local bundle.
Its manifest identifies a build at `2026-08-03T01:58:03.106705+00:00`, uses
site config `site_jacksonville_v0.yaml`, and records all completed build steps.
File sizes are observed bytes, not limits.

| Adapter product | Legacy file(s) | Observed bytes | Required top-level contract | Observed year/source behavior |
| --- | --- | ---: | --- | --- |
| manifest metadata | `manifest.json` | 2,588 | `site_id`, `market_id`, `site_config_filename`, `built_at_utc`, `completed_steps`, `step_timings_seconds` | build timestamp and step list are attached to every result |
| site identity | `site.json`, `resolved_site.json` | 316 + 230 | authored site id/address/rings/primary ring/coordinates/geocode source; resolved coordinates/address/match type/geocode source | coordinates and geocoding remain source-provided |
| overview | `overview.json` | 2,765 | `site`, `resolved_site`, `page_meta`, `site_cards`, `headline_table`, `flags` | headline rows carry `primary_year` and `source_table`; nulls remain null |
| people | `people.json` | 68,973 | `site`, `metric_summary`, `catchment_profile`, `daytime_population` | 2024 profile rows and 2023 daytime rows; source tables include population, income, housing, and transport products |
| place | `place.json` | 163,423 | POI, barriers, ring variants, traffic, NRI/NFHL, and D4/D5 metadata fields | observed 2021--2025 rows; FDOT source system; empty `nfhl_ring_shares` is retained as an empty legacy field, not zero |
| market | `market_page.json` | 8,446 | `employment_mix`, `gdp_mix`, `housing_context`, `meta` | observed 2016--2025 values; employment source is retained row-by-row |
| methods | `methods.json` | 4,596 | `site`, `resolved_site`, `coverage_diagnostic`, `skip_reasons`, `source_vintages`, `method_notes` | 2024 source vintages and availability/skip reasons remain visible |
| map manifest | `map/meta.json` | 762 | site point, view state, tract-fill years/sources, NFHL status/error | metadata only; map layers are not read in Epic 1 |
| section status | program-owned (Epic 2) | — | unavailable result with reason | no status is inferred from legacy page presence |

The full reference bundle also contains CSV and GeoJSON layers. They are not
eagerly loaded by Epic 1; the map and section registry contracts own their
selection in Epic 2.

## Epic 2 section and map products

`site_section_registry.py` is the authority for all eleven specified sections.
It records the source contract, readiness, client eligibility, known issue,
promotion gate, and owner; it also maps every legacy page to the adapter
products it consumes. Only `withheld` and `method_candidate` entries render as
deferred-work cards, so unfinished work remains visible internally without a
client-facing claim.

`site_map_products.py` reads `map/meta.json` first and returns lightweight file
descriptors. It opens a GeoJSON or CSV only after its layer is selected. A
client renderer can call `write_display_geojson` with an explicit destination,
feature cap, and byte cap; the derived asset records those limits and never
overwrites the analytical source layer. Tract-fill layers are always labelled
as tract context—not a catchment total or catchment median.

## Availability and comparison rules

Each result is `available`, `unavailable`, `invalid`, or `empty`, carries the
unaltered artifact payload when it is inspectable, and includes the full
manifest, build timestamp, extracted source years, and source/provenance
labels. Missing files have no payload. Missing required keys are `invalid`;
an emitted product with an empty required row collection is `empty`.

The adapter does not calculate catchment metrics or benchmarks. Consumers must
use the declared compatible benchmark rows only. In particular, a multi-tract
catchment total is never comparable to a tract distribution, and unavailable
or empty evidence is never rendered as zero.
