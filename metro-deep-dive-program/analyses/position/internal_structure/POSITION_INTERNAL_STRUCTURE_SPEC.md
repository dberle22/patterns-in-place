# Position Internal Structure Spec

**Status:** Part 1 initial implementation; Phase 7, Geography, POI, Infrastructure, and existing
job-center work provide the underlying capabilities. The next geography
priority is sourced local-neighborhood mapping. Corridor Intelligence is
deprecated and is not an input to this analysis.

**Default market:** Richmond, VA (`40060`)

**Primary surfaces:** `POSITION_INTERNAL_STRUCTURE_NOTEBOOK.py` (Part 1) and
`POSITION_INTERNAL_STRUCTURE_PART2_NOTEBOOK.py` (Part 2)

## Goal

Build one reusable Position notebook that provides a broad review of how a
selected metro is assembled below the CBSA level.

The notebook has two parts:

1. **Market Geography and Zone Structure** — establish the relationship among
   the CBSA, counties, Census Places, tracts, ZCTAs, and Phase 7 zone types.
2. **Activity, Infrastructure, and Structural Patterns** — examine how POIs,
   major anchors, employment centers, and physical networks relate to those
   geographies and local-neighborhood mappings.

Local neighborhoods provide orientation and narrative context, but do not
replace tract or ZCTA taxonomies. The primary question is:
**How is this metro assembled, and how do its Places and systems relate?**

The notebook is exploratory. It describes spatial anatomy and routes deeper
questions; it does not claim that proximity proves access, integration,
causation, or investment opportunity.

## Analytical Objects

| Object | Meaning in this analysis |
|---|---|
| CBSA and county | The governed market frame and its major administrative components |
| Census Place | A named incorporated place or Census-designated place; useful for orientation but not automatically a functional market |
| Tract | The primary small-area analytical grain and carrier of Phase 7 zone assignments |
| ZCTA | A supporting Census presentation geography derived from tract-zone composition; not a USPS postal ZIP |
| Zone type | A nationally consistent Phase 7 tract classification, not a locally named neighborhood |
| POI or anchor | A governed place record or selected major institution/activity anchor |
| Employment center | Existing tract-level job-concentration evidence reused for orientation, not a commuting-flow claim |
| Local neighborhood | A sourced, vintaged contextual geography related explicitly to tracts and ZCTAs |

No one object substitutes for another. In particular, a Census Place boundary,
POI cluster, and zone type can overlap without representing the same thing.

## Architecture Boundary

| Component | Owns |
|---|---|
| Intelligence Framework | National Phase 7 tract zone assignments, scores, benchmarks, and ZCTA rollup |
| Geography | CBSA, county, Place, tract, ZCTA, and local-neighborhood identities; allocation relationships; vintages; source mappings; and map geometry |
| Foundations and existing job-center work | Governed population and housing measures plus reusable tract job-center evidence |
| POI | Source-faithful classified place points and geography assignments |
| Infrastructure | Source-faithful classified line and polygon features with geometry QA |
| Internal Structure | Market-scoped joins, descriptive aggregation, cross-geography comparison, and exploratory display |
| Issue layer | Featured-area selection, editorial names, stat blocks, opportunity framing, and publication styling |

The notebook must not rerun Phase 7, invent functional Place boundaries, or
rewrite POI or Infrastructure classifications. A repeated analytical method
should be promoted only after reuse demonstrates that it belongs outside this
notebook.

## Inputs

Market-geography and zone inputs:

- `mart_intelligence.intelligence_zones`
- `mart_intelligence.intelligence_zones_zcta`
- governed CBSA, county, Census Place, tract, and ZCTA identities and
  relationships from Geography
- market-scoped display geometry where a planned map requires it
- a small declared set of additive population and housing fields needed to
  describe the scale of Places and zones

Activity and structure inputs:

- a declared POI Engine source run and classified-place handoff
- a declared Infrastructure Engine source run and feature handoff
- existing D3 tract job-center evidence where its interface can be reused
- a selected local-neighborhood mapping when it is available

The analysis should consume the narrowest useful market slice. It should not
load national geometry or raw source extracts merely because they exist.

## Part 1 — Market Geography and Zone Structure

Part 1 answers:

- Which counties, Census Places, and unincorporated areas make up the metro?
- Where are population and housing concentrated across those geographies?
- Which Phase 7 zone types make up the market, and how unusual is that mix?
- How is each Place composed of zone types, and where is each zone type located
  across Places?
- What additional orientation does the ZCTA view provide without replacing
  tract or Place geography?

Planned surfaces:

| Surface | Purpose |
|---|---|
| Market coverage summary | Confirm identity, allocation, metric, zone, and geometry coverage before interpretation |
| Geography hierarchy map | Orient the analyst to CBSA, county, Census Place, and tract boundaries; show unincorporated coverage explicitly |
| Place inventory | Compare the largest Places using a small set of population, housing, and land-context measures |
| Tract zone map and composition | Show Phase 7 assignments and compare the market's zone mix with a declared national baseline |
| Place × Zone matrix | Show both the zone composition within each Place and the distribution of each market zone across Places |
| Place profile | Inspect one selected Place's scale, zone mixture, tract evidence, and relationship to the rest of the CBSA |
| ZCTA rollup | Provide a supporting reader-friendly view while preserving dominant-share and mixed-zone evidence |

Place allocations must retain their selected population, housing-unit, or land
basis and quality flags. Tracts that are partly or wholly outside a Census Place
must remain visible rather than being silently assigned to the nearest name.
Tract jobs must not be allocated with a population, housing, or land basis; use
the existing tract job-center lens unless a direct or separately validated
Place-grain employment method is available.

## Part 2 — Activity, Infrastructure, and Structural Patterns

Part 2 answers:

- How are POIs and major anchors distributed across Places and zone types?
- Which Places or zones specialize in particular activity categories relative
  to the market?
- Where do existing employment centers and major institutional or civic
  anchors sit within the Place and zone structure?
- How do roads, rail, waterways, airports, and ports organize or complicate
  the observed spatial pattern?
- What deeper questions should be routed to access, job-proximity,
  polycentricity, housing, or regional-role analyses?

Planned surfaces:

| Surface | Purpose |
|---|---|
| Activity coverage summary | Show POI source, mapping, assignment, and denominator coverage before comparing areas |
| POI by Place and Zone | Compare counts, normalized rates or density where valid, and category composition without treating raw counts as access |
| Major anchors and employment centers | Locate selected institutions and existing job-center evidence within the market hierarchy |
| Infrastructure skeleton | Show approved roads, rail, waterways, airports, ports, and other named structural features |
| Integrated market map | Combine selected Places, zones, anchors, centers, and infrastructure layers for exploratory review |
| Market synthesis and routing | Summarize the strongest structural observations and direct unresolved functional questions to their owning analyses |

POI comparisons should keep raw counts, per-resident or area-normalized values,
and category shares distinct. The notebook should not create an activity-center
classification in its first pass; it can compare existing job centers and
visible POI concentrations descriptively.

POI-by-Place requires a direct governed point-to-Place assignment. Until
Geography publishes that relationship, the notebook must display the gap and
must not allocate point counts through tract population, housing, or land
weights.


## Parameters

| Parameter | Role |
|---|---|
| `cbsa_code` | Select one covered metro; Richmond is the default first-review market |
| `geography_view` | Focus the map on Place, tract, or supporting ZCTA geography where available |
| `place_id` | Inspect one Census Place without hiding the rest of the market |
| `zone_type` | Focus Place/tract composition review without changing the model |
| `poi_categories` | Choose governed categories approved for the declared POI run |
| `poi_measure` | Switch among count, category share, and a valid normalized measure |
| `infrastructure_groups` | Choose from the declared Infrastructure consumer handoff |
| `neighborhood_mapping_version` | Select a governed local-neighborhood source and vintage when available |

Controls should be populated from live contracts rather than market-specific
hard-coded lists.

## Outputs

The primary output is two interactive Marimo notebooks, one for each part. Any
later headless QA bundle should validate stable query and map expectations only;
it is not required to begin the exploratory review.

The notebook does not write replacement geography, tract-zone, POI,
Infrastructure, employment-center, or structural-candidate products.

## Validation Rules

- every tract row is unique for the selected Phase 7 model output
- geography joins retain the declared level and boundary vintage and expose
  misses
- Place allocations retain their basis and quality flag and do not double-count
  market totals
- unincorporated or unallocated market shares remain explicit
- ZCTA displays retain mixed-zone and dominant-share evidence and are never
  labeled as USPS ZIP assignments
- Place × Zone summaries reconcile to both their Place and market totals
- POI comparisons expose mapping, geography-assignment, and denominator
  coverage
- raw POI counts are not presented as equivalent to density, access, or
  functional importance
- employment-center evidence retains its source grain and does not imply
  commuting flows
- local-neighborhood displays retain their declared source, vintage, and
  relationship basis
- changing markets updates every displayed layer without writing to DuckDB or
  engine artifacts

## Interpretation Guardrails

- Census Places are administrative or statistical geographies, not complete
  functional submarkets
- zone types are national tract types, not locally named neighborhoods
- ZCTAs are population-weighted rollups, not independently modeled
  classifications or postal delivery areas
- POI concentration does not by itself establish a center, access, demand, or
  economic importance
- employment concentration does not establish commuting integration
- proximity or intersection with Infrastructure does not prove access,
  causation, or economic impact
- local neighborhoods are contextual overlays, not replacements for tract or
  ZCTA taxonomies
- claims about monocentricity, polycentricity, daily-needs access, commuting,
  housing demand, or job proximity belong to their named downstream analyses
- formal Census Place names come from Geography; editorial area/candidate
  names, selections, stat blocks, and prose remain issue-owned

## Out of Scope

- rerunning or revising the Phase 7 national model
- algorithmically inventing a local neighborhood or submarket boundary system;
  sourced neighborhood mappings belong in Geography
- building a new activity-center or downtown typology
- consuming the deprecated Corridor Intelligence engine or defining a
  replacement corridor method inside the notebook
- commuting-flow or causal market-integration claims
- daily-needs access scoring, routing, travel time, or catchments
- Investment Scores or parcel screening
- final Act 4 composition and publication-ready styling

## Success Check

Internal Structure is ready for exploratory use when an analyst can select a
covered metro, understand its hierarchy of counties and Census Places, compare
Place and zone composition across tracts and ZCTAs, inspect how POIs,
employment centers, and Infrastructure relate to that geography, and route
unanswered functional questions without conflating the underlying objects.
