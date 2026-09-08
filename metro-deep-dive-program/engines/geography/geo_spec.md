---
track: geography-crosswalk
status: draft
scope: foundations (platform-wide)
last_updated: 2026-09-07
---

# Geography Crosswalk Infrastructure — Track Spec

Standing specification for how Patterns in Place represents, relates, and versions geographic units. This is the spec of record for the geography layer — `geography_catalog.yml`, the `silver.xwalk_*` tables, and any query surface that crosses geographic grains are built to satisfy it.

This is foundations work, not section work. No Metro Deep Dive market and no Explorer section owns it.

## Purpose

Every analytical claim in the platform is a claim about a place. The unit that place is measured in is not stable, and the relationships between units are not all the same kind of relationship. Today the platform treats them as if they were: `dim_geo` is unvintaged, and `silver.xwalk_*` tables mix exact parent-child nesting with approximate areal overlap under one naming convention and one set of join semantics.

That works until it silently doesn't. A tract-level growth series across 2010 and 2020 vintages is not wrong in any way the query engine can detect. A ZIP-keyed table joined to a ZCTA-keyed table returns rows. This is the platform's clearest instance of the silent-failure problem: correctness has no runtime signal and must be defined upstream.

The goal is a geography layer where:
1. Every grain declares its vintage authority and stability behavior
2. Every crosswalk declares which of three join types it is
3. Allocation quality travels with the result rather than being lost at the join
4. Temporal harmonization is an explicit, named operation rather than an assumption

## Conceptual model

### The nesting is narrower than it looks

Exact containment holds for one chain only:

```
block → block group → tract → county → state → division → region → US
```

Everything else is a **block-level aggregation**, not a nesting:

| Grain | Relationship to the chain | Crosses |
|---|---|---|
| Census Place | Built from blocks | County lines |
| ZCTA | Built from blocks | County and state lines |
| CBSA | Built from whole counties | State lines |
| School district | Built from blocks | County lines |

CBSA is the one partial case: it nests cleanly *above* county (whole counties, no splitting) but has no exact relationship to any sub-county grain except through blocks. Not all counties belong to a CBSA.

**The Census block is the common denominator.** Any relationship between two grains that do not sit on the same containment chain resolves through blocks or not at all.

### Stability classes

The platform currently has no vocabulary for how a grain changes. It needs four:

| Class | Behavior | Grains |
|---|---|---|
| `stable` | Effectively never changes | US, region, division, state |
| `decennial` | Redrawn on the decennial clock; documented breaks | Block, block group, tract, ZCTA |
| `periodic` | Redefined on an irregular published schedule | CBSA (OMB delineation updates) |
| `continuous` | Changes annually with no break announcement | Census Place (annexation via BAS), county (rare but real — e.g. Connecticut planning regions, 2022) |

The `continuous` class is the one currently unmodeled and the most dangerous. A 2015 and a 2023 Richmond city boundary are not guaranteed to be the same polygon, and nothing in the pipeline would surface that.

### Tract redistricting is a measurement artifact, not just a nuisance

Tracts target a population band and are split when they exceed it, merged when they fall below. That rule means the *fastest-growing tracts are the most likely to have been redrawn*, and the redraw is caused by the growth being measured. Any uncorrected tract-level change series is partly measuring the Census Bureau's response to growth rather than growth itself.

This is a methods point with a real editorial payoff (see Editorial output below) and it is the reason `harmonize()` is a first-class verb rather than a utility function.

### ZIP is not ZCTA

These are distinct objects and the platform must not conflate them.

- **ZCTA**: areal, block-built, produced decennially by Census, ~33k units
- **ZIP Code**: a USPS delivery-route construct, ~41k units, changes continuously, not inherently areal (point ZIPs, PO-box-only ZIPs, single-building ZIPs)

Most vendor data — including Zillow — arrives keyed to ZIP, not ZCTA. Every such join needs a stated method. The defensible one is the HUD USPS ZIP crosswalk, which publishes quarterly ZIP↔tract/county/CBSA ratios split by residential, business, other, and total address counts. The choice of ratio column is an analytical decision and must be recorded, not defaulted.

## The three crosswalk types

This is the central design distinction. Each type has different join semantics, different failure modes, and belongs in a different physical table.

| Type | Semantics | Weight | Example |
|---|---|---|---|
| **Containment** | Exact parent-child; every child has exactly one parent | Always 1.0 | tract → county, county → state, county → CBSA |
| **Allocation** | Many-to-many areal overlap requiring a share denominator | 0.0–1.0, sums to 1.0 per source unit per basis | tract ↔ ZCTA, tract ↔ place, ZIP ↔ tract |
| **Temporal** | Same grain, different vintage | 0.0–1.0 per basis | 2010 tract → 2020 tract, 2013 CBSA → 2023 CBSA |

Two rules follow:

1. **A containment crosswalk may never be used to justify an allocation join.** Today, sharing the `silver.xwalk_*` prefix implies they are interchangeable. They are not.
2. **An allocation crosswalk has no single correct weight.** Population, housing units, and land area produce different answers and are correct for different questions. The basis is a query-time choice, not a build-time one.

## Architecture

Four layers. Each is buildable and testable independently, and layers 1–2 should not begin until layer 1's contract is written.

### Layer 0 — Block atom registry

The substrate. One row per Census block per vintage, carrying its membership in every higher grain.

Two candidate sources:

| Option | Pros | Cons |
|---|---|---|
| **LODES `xwalk` files** | Already ingested; one file per state; carries block → county, tract, CBSA, place, ZCTA, congressional district, WIB in a single table; near-zero marginal cost | Carries LODES' vintage rather than an arbitrary one; coverage tied to LODES state-year availability; not a Census-authoritative product |
| **Census Block Assignment Files (BAF) + PL block records** | Census-authoritative; vintage chosen explicitly; complete national coverage independent of LODES | Separate file per grain per state; more ingestion surface; more maintenance |

**Decision (2026-09-07): use the Census backbone.** The governed registry will
use 2020 PL 94-171 block population and housing-unit records, Census
block-assignment files for Place membership, and the national Census
ZCTA-to-block relationship file for ZCTA membership. This gives the engine an
explicit, Census-authoritative 2020 vintage. LODES crosswalks remain a
reconciliation input, not the registry authority.

Block population and housing-unit counts come from decennial PL 94-171 and are required for weight computation. Block land area comes from TIGER.

**Required outputs:**
- `staging.census_blocks` — raw registry rows as ingested
- `silver.block_registry` — normalized, one row per `(block_geoid, vintage)`, with membership columns per grain and `pop`, `housing_units`, `land_area_sqm` attached

### Layer 1 — Semantic contract (`geography_catalog.yml`)

Written before any table is built. Extends the existing catalog so every supported grain declares:

```yaml
grains:
  census_tract:
    geoid_length: 11
    containment_parent: county
    vintage_authority: decennial
    stability_class: decennial
    available_vintages: [2010, 2020]
    default_vintage: 2020
    block_built: true
    notes: >
      Split when population exceeds the target band; merged when below.
      Growth-correlated redistricting — see harmonize() requirement.

  census_place:
    geoid_length: 7
    containment_parent: none      # crosses county lines
    vintage_authority: annual_bas
    stability_class: continuous
    block_built: true
    notes: >
      Boundaries change annually via the Boundary and Annexation Survey.
      No break announcement. Any multi-year place series requires an
      explicit vintage statement.

  zcta:
    geoid_length: 5
    containment_parent: none
    vintage_authority: decennial
    stability_class: decennial
    block_built: true
    notes: >
      Distinct from USPS ZIP. Vendor data keyed to ZIP requires the
      HUD USPS crosswalk and a stated ratio basis.
```

And declares the legal edges:

```yaml
crosswalks:
  - source: census_tract
    target: county
    type: containment
    direction: up

  - source: census_tract
    target: zcta
    type: allocation
    bases: [population, housing_units, land_area]
    default_basis: population

  - source: census_tract
    target: census_tract
    type: temporal
    from_vintage: 2010
    to_vintage: 2020
    bases: [population, housing_units, land_area]
```

Any grain pair not declared here is not a legal join. The validator enforces this.

### Layer 2 — Physical tables

**`silver.dim_geo` becomes vintaged.** The current unvintaged table is silently asserting that geographies are stable. New key:

| Column | Notes |
|---|---|
| `geo_id` | |
| `geo_level` | |
| `vintage` | Year of the boundary definition, not the data year |
| `name` | |
| `valid_from`, `valid_to` | For `continuous`-class grains |
| `containment_parent_id` | Null where no exact parent exists |
| `stability_class` | Denormalized from the catalog for query convenience |
| `land_area_sqm`, `water_area_sqm` | |

This is a breaking change to every query that joins `dim_geo`. Migration path: add `vintage` with a default that reproduces current behavior, then remove the default once callers are updated.

**`silver.xwalk_containment`**

`(child_geo_id, child_level, parent_geo_id, parent_level, vintage)` — no weight column, because the weight is definitionally 1.0. Absence of the column is the type signal.

**`silver.xwalk_allocation`**

| Column | Notes |
|---|---|
| `source_geo_id`, `source_level` | |
| `target_geo_id`, `target_level` | |
| `vintage` | |
| `weight_basis` | `population` / `housing_units` / `land_area` |
| `weight` | Share of source falling in target under this basis; sums to 1.0 per `(source, basis)` |
| `source_denominator` | Raw count backing the weight — needed for audit and for zero-population cases |
| `quality_flag` | See below |

Weights for all bases are stored as **separate rows**, not separate columns and not one blessed value. This forces the caller to choose.

**`silver.xwalk_temporal`**

| Column | Notes |
|---|---|
| `from_geo_id`, `from_vintage` | |
| `to_geo_id`, `to_vintage` | |
| `weight_basis`, `weight` | |
| `change_type` | `unchanged` / `split` / `merge` / `redrawn` / `new` / `retired` |

`change_type` is what makes the growth-artifact problem visible. A tract series where every unit is `unchanged` is trustworthy; one containing `split` rows is not, without harmonization.

Source: Census tract relationship and 2010→2020 block relationship files. The
tract relationship file supplies intersection land area, but Census documents
that 2020 relationship files do not include population or housing counts;
population and housing-unit weights must therefore be calculated by allocating
2010 block counts through the block relationship file. CBSA temporal crosswalks
come from retained OMB delineation bulletins.

### Layer 3 — Query surface

Three verbs, exposed as SQL macros/views and as Python helpers, mirroring the existing chart-engine pattern of a single narrow entry point.

**`rollup(source_level, target_level, vintage)`**
Containment only. Fails loudly if the requested pair is not a containment edge in the catalog. No weights, no ambiguity.

**`allocate(source_level, target_level, vintage, basis)`**
Weighted overlay. `basis` is required — no default at the call site, even though the catalog declares one, so the choice appears in the query text. Returns the allocated value plus the aggregate `quality_flag` for the operation.

**`harmonize(grain, from_vintage, to_vintage, basis)`**
Temporal. Returns values restated on the target vintage, plus a per-row `change_type` so a chart can mark or exclude redrawn units.

**Validator enforcement.** The existing `QueryValidator` (approved tables / metrics / joins / read-only / geo level) gains a geography rule set:
- Reject any join between grains not declared as a crosswalk edge
- Reject any allocation join without an explicit basis
- Reject any multi-vintage comparison of a `decennial` or `continuous` grain that has not passed through `harmonize()`
- Warn on any `continuous`-class grain used in a multi-year series

This is where the track pays for itself. The point is not to build crosswalk tables — it is to make the incorrect query impossible to write silently.

### Layer 4 — Governance and quality

**Allocation quality flag.** Every allocation result carries a flag computed from the weight distribution:

| Flag | Condition |
|---|---|
| `exact` | Single target with weight 1.0 (allocation degenerated to containment) |
| `clean` | Dominant target ≥ 0.95 |
| `split` | No target ≥ 0.95, all mass allocated |
| `partial` | Source mass not fully allocated (target geography does not cover source) |
| `undefined` | Source denominator is zero under this basis (e.g. zero-population tract allocated by population) |

The `undefined` case is not rare — parks, industrial tracts, and water-heavy blocks all produce it — and must be surfaced rather than dropped. Same pattern as the D6 Felten join, where unmatched share was kept visible as a transparent limitation.

**Coverage audit.** One audit output per crosswalk, per vintage, recording: total source units, units with at least one edge, units unmatched, weight-sum deviation from 1.0 beyond tolerance. Written beside the table as a reviewable artifact, not just a test assertion.

**Source contracts.** New `foundations/data_dictionary/sources/` entries for the block registry source, the Census relationship files, and the HUD USPS crosswalk, following the existing source contract format.

## What this unblocks

Named open issues in the current question bank and analysis program that this track closes:

| Blocked item | Current open issue | Resolved by |
|---|---|---|
| Q2 — What does proximity to jobs cost? | "requires the tract→place crosswalk to be readable; price data grain may not match tract grain and the join needs a stated method" | `allocate()` with declared basis; HUD ZIP contract for price data |
| Q3 — Where is growth actually landing? | "tract boundary changes across vintages must be handled explicitly or the change series is unreliable" | `harmonize()` with `change_type` |
| A5 | "tract→place crosswalk for readability" | `allocate()` |
| D2 / D3 place overlay | "current repo only exposes place identifiers and `silver.xwalk_cbsa_primary_city`, not place polygons" | Vintaged `dim_geo` + place geometry |
| Open dataset release | `geo_dim` is one of the three tables planned for public release | Vintaging must land before publication, or v1 ships a known defect |

The last row is the sequencing constraint worth noting: publishing an unvintaged `geo_dim` under a DOI creates a versioned public artifact with the silent-failure problem baked in.

## Build sequence

Ordered by dependency, not by value.

| Phase | Work | Gate |
|---|---|---|
| 0 | **Lock the Census block-registry source** (PL 94-171 + BAF) and write the source contract | Complete |
| 1 | Write the `geography_catalog.yml` extension — grains, stability classes, legal edges | Before any table build |
| 2 | Build `silver.block_registry` with pop / HU / area attached | Needs 0 |
| 3 | Vintage `silver.dim_geo`; migrate callers | Needs 1; independent of 2 |
| 4 | Build `xwalk_containment` — the easy one, validates the pattern | Needs 2, 3 |
| 5 | Build `xwalk_allocation` for tract↔place and tract↔ZCTA, all three bases | Needs 2, 3 |
| 6 | Build `xwalk_temporal` for 2010→2020 tracts | Needs 2, 3 |
| 7 | Ship `rollup()` / `allocate()` / `harmonize()` | Needs 4–6 |
| 8 | Validator geography rules | Needs 1, 7 |
| 9 | Coverage audits + quality flag plumbing | Needs 4–6 |
| 10 | HUD USPS ZIP crosswalk ingestion (unblocks Zillow-keyed joins) | Independent of 4–9; can run in parallel |

Phases 0–1 are specification work and should be done before any code. Phase 4 is deliberately first among the builds because containment is trivial — it validates the table pattern, the audit format, and the query surface against a case where the right answer is known.

## Open decisions

| Decision | Blocks | Status |
|---|---|---|
| Block registry source | Everything downstream — weights inherit its vintage | **Decided.** Census 2020 PL 94-171 + BAF; LODES is reconciliation only. |
| Default `weight_basis` per crosswalk in the catalog | Whether `allocate()` can have a call-site default | Open. Leaning population for demographic measures, housing units for housing measures, and no global default |
| Whether `harmonize()` restates backward (old→new) or forward | Chart and series semantics | **Decided.** Restate historical observations to the latest approved target vintage. |
| Whether `continuous`-class grains (place) get annual vintages or a single snapshot | Storage size vs. fidelity | Open. Annual is correct but expensive; snapshot-per-decade with a documented caveat may be the honest v1 |
| Whether zero-denominator allocation rows are stored or omitted | Audit completeness vs. table size | **Decided.** Store them with `quality_flag = 'undefined'`. |
| Whether `dim_geo` vintaging ships before or after the open dataset release | Public artifact correctness | Open — but see sequencing note above |

## Editorial output

This track produces a strong standalone methods piece, and probably a better positioning piece than the CBSA similarity study.

**Working thesis:** the units being compared were redrawn between the two dates being compared across, and the redraw was *caused by* the thing being measured. Tracts are split when they grow past the target band — so the fastest-growing tracts are exactly the ones most likely to have changed shape, which means an uncorrected "fastest-growing tract" chart is partly measuring the Census Bureau's response to growth rather than growth itself.

**Why it lands:** the mechanism is simple enough to explain in two sentences, almost nobody outside the field knows it, and it invalidates a chart type that appears constantly. It is a methods contribution with a visual payoff — show the same tract series harmonized and unharmonized.

**Secondary angle:** ZIP is not a place. The ZIP/ZCTA distinction plus the HUD ratio-basis choice is a second, shorter piece with the same structure — a widely used join that is quietly undefined.

**Channel:** Substack, analytical rather than technical framing. The contract-driven build story belongs in the LinkedIn technical series; the measurement-artifact story is analytical and belongs in the research channel. This keeps the 3:1 analytical-to-technical ratio intact.

## Non-goals

- Geometry implementation details beyond the governed roles. The contract requires
  full TIGER/Line analytical geometry and display geometry simplified from
  Census cartographic boundaries; their physical build remains in `geo.*`.
- Network distance or travel-time. Proximity work stays with the POI/infrastructure track.
- Sub-block allocation. Blocks are the atom; nothing below.
- Non-US geography.
- Retrofitting published Deep Dive issues. Published issues are dated artifacts and do not get re-run when the geography layer lands.
