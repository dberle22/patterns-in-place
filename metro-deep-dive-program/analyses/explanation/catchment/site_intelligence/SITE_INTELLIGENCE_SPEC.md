# Site Intelligence Workbook and Client Brief Spec

**Status:** Active

**Updated:** 2026-10-07

## Decision and goal

Replace the legacy Streamlit Place Intelligence app with two Marimo-authored
surfaces that share one read-only site bundle:

| Surface | User | Purpose | Delivery |
|---|---|---|---|
| Internal Site Intelligence workbook | analyst | inspect evidence, methods, diagnostics, maps, and unfinished sections | local Marimo notebook |
| Client Site Brief | client or investor | read a clear, source-traceable site context brief for one selected site | static HTML and PDF |

The internal surface is a workbook, not a production data builder. The client
surface is a rendered brief, not an interactive app. Both must be reusable for
another site by changing a declared input, not by changing application code.

## Ownership and boundary

This folder is a downstream product of `catchment/`, not a second Catchment
method. The existing Catchment helper remains the authority for point-centered
tract contributions and its stated limitations. Geography owns boundaries,
POI owns classified places, and Infrastructure owns physical features.

During V1 migration, adapters may read the legacy per-site artifact bundle:

```text
legacy site YAML + artifact build
  -> site_artifacts/<site_id>/
  -> program-owned read-only adapters
  -> internal workbook and client brief
```

This is an interim compatibility boundary. The notebooks must not import
Streamlit, call legacy page renderers, or perform calculation on page load.
Replacing upstream sources with governed program products is a separately
approved migration, not hidden scope in the renderer port.

## Site bundle contract

The adapter layer exposes named, independently testable products. It records
the source artifact manifest and does not silently fill missing fields.

| Product | Required content | Initial source |
|---|---|---|
| `site_identity` | site id, address, configured rings, primary ring, resolved coordinates, geocode provenance | `site.json`, `resolved_site.json` |
| `overview` | approved headline rows, status flags, source/vintage labels | `overview.json` |
| `people` | ring profile, compatible benchmarks, daytime jobs/workers | `people.json` and Catchment-compatible evidence where available |
| `place` | POI mix, current AADT context, environmental screening | `place.json` |
| `market` | employment mix and validated housing context | `market_page.json` |
| `methods` | apportionment diagnostics, unavailable reasons, vintages, limitations | `methods.json` |
| `map_manifest` | available display layers, size, provenance, and reader-facing labels | map metadata plus layer-specific assets |
| `section_status` | readiness, client eligibility, dependency, caveat, and promotion gate for every section | program-owned registry |

Rows keep their source year and source system. An unavailable source stays
unavailable; it is never displayed as zero or substituted with a different
geography. A multi-tract catchment total must never be benchmarked against a
single-tract distribution.

## Workbook content

The workbook has these sections in order:

1. **Run and site identity** — bundle status, input site, build timestamp,
   coordinate/geocode provenance, ring definition, and visible limitations.
2. **Overview** — client-safe headline values and a lightweight orientation
   map.
3. **People and daytime context** — ring gradient, compatible benchmarks,
   jobs/workers, and selected workplace industries.
4. **Commercial and physical context** — reader-facing POI categories,
   current corridor/AADT evidence, environmental screening, and purpose-built
   maps.
5. **Metro context** — employment mix and only market series whose contract
   passes validation.
6. **Methods and QA** — contribution diagnostics, source vintages, omitted
   metrics, and explanation limits.
7. **Deferred-section ledger** — every withheld or method-candidate section,
   why it is withheld, its upstream dependency, and its promotion gate.

Controls are read-only: selected built site, ring/reach, supported map layer,
and display metric. Controls are created in one Marimo cell and read in
dependent cells. No notebook control may invoke a build or write to DuckDB.

## Client brief content

The client brief is a one-site, narrative-first subset of the workbook:

1. Site and catchment orientation.
2. People in range and daytime context.
3. Commercial and physical context.
4. Validated metro context.
5. Methods, sources, and limitations appendix.

It uses a fixed render configuration and static, display-optimized maps and
charts. It carries source/vintage labels and distinguishes apportioned from
directly observed evidence. It does not expose the workbook's exploratory
controls, raw diagnostics, developer-facing paths, or a section whose status
is not `client_ready`.

The delivery targets are static HTML and a print-tested PDF. A client brief
must be readable without a live database, a running server, or a third-party
map style service.

## Map contract

The legacy app eagerly loads multiple large GeoJSON/CSV layers. The new
surfaces must instead use a layer manifest and load only the selected layer.

- The internal workbook starts with site point and rings only; optional POI,
  road, tract-fill, severance, and flood layers load only on selection.
- The client brief receives a small, declared set of static maps. It does not
  embed the all-layers interactive map.
- Display geometry may be simplified or clipped for rendering, but analytical
  geometry and values remain unchanged.
- A map caption names the layer, source, vintage, geometry limitation, and
  whether the measurement is direct or apportioned.

## Section registry and deferred work

The section registry is authoritative for both surfaces. Each section has:

```text
section_id
workbook_label
status: client_ready | provisional | withheld | method_candidate
client_eligible
source_contract
known_issue
promotion_gate
owner
```

`withheld` and `method_candidate` sections must render in the internal
workbook as a compact work-card. They remain visible work to complete; they do
not produce a blank chart, fabricated zero, or client-facing claim.

Initial registry entries are:

| Section | Status | V1 treatment |
|---|---|---|
| Catchment profile and compatible benchmarks | `client_ready` after adapter reconciliation | client brief and workbook |
| Daytime jobs/workers | `client_ready` after adapter reconciliation | client brief and workbook |
| POI mix and current AADT | `provisional` | workbook first; promote after source/label review |
| Environmental screening | `provisional` | workbook first; client wording only after method review |
| Market employment mix | `provisional` | workbook first; promote after unit/scale QA |
| Housing/rent trend | `withheld` | explicit work-card until non-empty validated series exists |
| GDP mix | `withheld` | explicit work-card until source and share contract is approved |
| Frontage traffic trend | `withheld` | explicit work-card until trend contract renders and reconciles |
| Barrier/water adjustment | `withheld` | explicit work-card; no access/routing claim |
| Dasymetric weighting | `method_candidate` | method work-card, not an alternative default result |
| Routed reach | `method_candidate` | method work-card, not an alternative default result |

## Non-goals

- Porting Streamlit widgets or restoring Streamlit Cloud deployment.
- Rebuilding D1–D5 in the notebook.
- Treating straight-line proximity as travel time, access, or commuting.
- Publishing aggregated tract medians as true catchment medians.
- Introducing a composite site score, site ranking, or multi-site comparison.
- Promoting legacy source caches or methods into Foundations without a separate
  ownership decision.

## Acceptance criteria

- One Baymeadows and one different Jacksonville site render from the same
  notebook code and adapter interfaces.
- Every client-visible value reconciles to an identified bundle product and
  carries source/vintage metadata.
- Internal and client surfaces agree on all shared values for the same site.
- A missing bundle product yields an explicit status, never a stale or invented
  value.
- Internal map selection does not read unselected heavy layers.
- Static HTML and PDF render without a running app, database connection, or
  external basemap dependency.
- `marimo check --strict`, focused adapter tests, render checks, and
  `git diff --check` pass.
