# Geography Engine Research Notes

## Inventory completed 2026-09-07

The build code already provides nationwide current hierarchy and display-ready
geometry, but it is not yet a governed geography engine.

- `foundations/etl/silver/geo_crosswalks_silver.R` writes the current exact
  hierarchy and three HUD-USPS ZIP crosswalks. The latter are incorrectly
  named `xwalk_zcta_*`, even though their key column is `zip_geoid`.
- `foundations/etl/gold/gold_dim_geo.sql` builds a compatible, current-only
  `gold.dim_geo`; its existing consumers include the Silver EJScreen/FEMA/IRS
  builds, Gold subject marts, the benchmarking engine, and visual-library SQL.
- The former geometry build uses `tigris(..., cb = TRUE, year = 2024)`, so the
  existing geometry is Census cartographic boundary—not full TIGER/Line
  analytical geometry. `mart_geography.geometry_catalog` records that
  provenance and approved display role for the tract, county, and CBSA
  products without altering their physical tables.
- `geo.tracts_all_us`, `geo.counties`, and `geo.cbsas` are approved read-only
  display inputs for current market-analysis consumers. `geo.states` remains
  visible but is outside this approval.

## Research conclusions

- Census block-assignment files contain all blocks for a state for a specific
  entity type, including blocks with no assignment. Paired with PL 94-171
  block population/housing counts, the Place BAF, and the national Census
  ZCTA-to-block relationship file are the smallest authoritative registry
  bundle.
- The 2020 tract relationship file has land-area intersections but no
  population or housing counts. A valid population/HU 2010→2020 harmonization
  must use 2010→2020 block relationships plus the decennial block counts.
- HUD-USPS ratios are ZIP-address allocations. `RES_RATIO`, `BUS_RATIO`, and
  `TOT_RATIO` are not ZCTA weights and must stay basis-specific.
- OMB Bulletin 23-01 is the approved current CBSA vintage. Later bulletins
  append a new vintage; the mart selects the approved current vintage rather
  than rewriting older rows.

## Deliberately deferred from Task 1

No source data was downloaded, no DuckDB table changed, and no consumers were
migrated. Those are subsequent build tasks.

## Containment-first mart (2026-09-08)

`mart_geography` now provides governed current/vintaged identity views, exact
relationship views, named tract/county/CBSA rollup views, a ZIP allocation
catalog, and coverage audits. Its rollup views return relationships only; they
never choose an aggregation for a metric. Initial checks confirmed current-key
uniqueness and one county parent per 2020 tract. Metric-specific behavior is
deferred until the first downstream consumer uses each operation.

## ZIP, ZCTA, and geometry port (2026-09-08)

ACS ZCTA records are Census ZCTA data and should join directly to the ZCTA
identity. USPS ZIP is retained solely for sources that actually publish ZIPs;
the HUD-USPS crosswalk supplies its explicitly weighted translation and does
not make ZIP a geometry or `dim_geo` level.

The former staging `get_tiger_geos.R` is now a compatibility entry point for
`foundations/etl/geo/get_tiger_geos.R`. The new builder is deliberately
on-demand and state-scoped, writes role-tagged cartographic display products,
and has not been run as part of this port. Existing national `geo.*` tables
therefore remain the current consumer surface until one is migrated.

## Allocation and temporal crosswalks (2026-09-08)

The repaired 2020 ZCTA relationship assigns 7,988,781 blocks to 33,642 Census
ZCTAs; 144,187 blocks have no ZCTA assignment and remain null. This correction
supersedes the earlier count derived before incomplete PL-header values were
cleared.

`silver.xwalk_allocation` stores tract-to-Place and tract-to-ZCTA edges for all
three approved bases. `silver.xwalk_temporal` restates 2010 tracts to the 2020
backbone: land uses the direct tract relationship file, while population and
housing are areal interpolations of 2010 PL block counts through the Census
block relationship. Coverage audits deliberately retain gaps, partial weights,
and zero denominators. Metric-specific validation is still a downstream
consumer responsibility.

## Corridor Intelligence geometry follow-up (2026-09-08; superseded 2026-09-11)

Corridor Intelligence verified that `geo.tracts_all_us` has exactly one
non-null geometry for each current Phase 7 tract in its first two markets: 340
for Jacksonville (`27260`) and 332 for Richmond (`40060`). The catalog now
approves this source as `approved_read_only_display` with the 2024 Census
cartographic-boundary provenance and `tract_geoid` join key. Corridor and
other market-analysis consumers may use it directly for map display and scoped
exports; that approval does not make it analytical geometry.

## Local-neighborhood mapping direction (2026-09-09)

The program is pausing Corridor Intelligence as a canonical grouping engine.
Its pilot candidates are not neighborhood boundaries and must not be promoted
as one. The next geographic priority is a governed local-neighborhood overlay
for analysis and orientation.

This is a source-and-mapping task, not a request to algorithmically invent
neighborhoods. Before implementation, identify the source, license, market
coverage, vintage, identifier stability, geometry role, and update cadence.
The product must retain source neighborhoods as supplied and provide explicit
tract-to-neighborhood and ZCTA-to-neighborhood relationship edges (including
partial and many-to-many overlaps where applicable). Tract Phase 7 types and
ZCTA rollups remain separate taxonomies; a local neighborhood is a contextual
overlay, not a replacement classification.
