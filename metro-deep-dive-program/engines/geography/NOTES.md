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
- `foundations/etl/staging/get_tiger_geos.R` uses `tigris(..., cb = TRUE)`, so
  the existing `geo` tables are cartographic boundaries—not full TIGER/Line
  analytical shapes—and do not persist a boundary vintage or geometry role.
- Current geometry consumers are primarily visual-library map samples and
  render tests. Preserve legacy `geo.states`, `geo.counties`, `geo.cbsas`, and
  `geo.tracts_all_us` until migration to role-specific tables is complete.

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

## Corridor Intelligence geometry follow-up (2026-09-08)

Corridor Intelligence verified that the existing `geo.tracts_all_us` table
has exactly one non-null geometry for each current Phase 7 tract in its first
two markets: 340 for Jacksonville (`27260`) and 332 for Richmond (`40060`).
The first Corridor build declares this table directly as
`legacy_cartographic_tract_geometry_v1`, retaining its
`unknown_legacy_vintage` status in run provenance. It does not infer that the
table is a formal analytical geometry product.

This is a usable current consumer surface, not a reason to block corridor
work. The outstanding Geography follow-up is metadata promotion: materialize
or register a vintaged, role-tagged tract geometry product in
`mart_geography.geometry_catalog`, then migrate Corridor Intelligence through
an unchanged-input compatibility check. Do not replace or relabel the legacy
table in place.

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
