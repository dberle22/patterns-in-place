# Geography Engine Contract

Status: Epics 2–7 implemented. Analytical geometry and consumer migrations
remain intentionally on-demand.

## Governing decisions

- `silver.dim_geo` is the future vintaged identity authority. Its key is
  (`geo_level`, `geo_id`, `boundary_vintage`); `data_year` and
  `source_release_year` are distinct fields.
- `gold.dim_geo` remains the backward-compatible, current-only serving
  dimension. It is not the historical identity authority.
- Exact containment, weighted allocation, and temporal harmonization are
  separate table types and separate query operations.
- `zip` and `zcta` are distinct levels. The existing `xwalk_zcta_*` tables are
  HUD-USPS ZIP crosswalks and will become `xwalk_zip_*`; compatibility views
  retain their old names during migration.
- ZCTA-native data, including ACS, joins to the Census ZCTA identity directly.
  USPS ZIP is retained only as a versioned source-identifier bridge through
  HUD-USPS allocation tables; it is not a `dim_geo` identity or geometry.
- Census 2020 PL 94-171 plus block assignment files are the block-registry
  authority. LODES is reconciliation-only.

## Existing warehouse baseline

The inspected DuckDB baseline has the following nationwide current coverage:

| Surface | Rows | Status |
|---|---:|---|
| `gold.dim_geo` | 88,356 | Current-only IDs for US, region, division, state, CBSA, county, and tract |
| `silver.xwalk_tract_county` | 84,121 | Exact current tract-to-county; TIGRIS 2023 |
| `silver.xwalk_county_state` | 3,235 | Exact current county-to-state; TIGRIS 2023 |
| `silver.xwalk_cbsa_county` | 1,915 | Exact-subset county-to-CBSA; OMB 2023 |
| `silver.xwalk_zcta_*` | 291,494 | HUD-USPS ZIP allocations, vintage 2025 Q1; misnamed |
| `geo.tracts_all_us` | 84,119 | Cartographic-boundary geometry, without a stored vintage/role |
| `geo.counties`, `geo.cbsas`, `geo.states` | 3,235 / 935 / 56 | Cartographic-boundary geometry, without a stored vintage/role |

The baseline lacked `silver.block_registry`, `silver.dim_geo`, typed crosswalk
tables, a `mart_geography` schema, Place/ZCTA geometry, and analytical
TIGER/Line geometry. Identity, containment, allocation, temporal, and mart
surfaces are now materialized; Place/ZCTA display geometry and analytical
TIGER/Line geometry remain on-demand.

## Locked future managed surfaces

| Surface | Grain / rule |
|---|---|
| `silver.dim_geo` | (`geo_level`, `geo_id`, `boundary_vintage`) identity history |
| `silver.block_registry` | (`block_geoid`, `boundary_vintage`), no block geometry |
| `silver.xwalk_containment` | Child-to-parent exact edges; no weight column |
| `silver.xwalk_allocation` | One row per source, target, basis, and vintage; weight plus denominator and quality |
| `silver.xwalk_temporal` | Historical-to-current edges with basis, weight, and change type |
| `silver.xwalk_zip_{tract,county,cbsa}` | Versioned HUD-USPS ZIP allocations; temporary `xwalk_zcta_*` compatibility views |
| `geo.<level>_analysis` | Full TIGER/Line geometry, keyed by level, ID, and boundary vintage |
| `geo.<level>_display` | Census cartographic display geometry, keyed identically |
| `mart_geography.*` | Read-only current/vintaged identity, relationship, geometry-catalog, and audit views |

## Source and vintage contract

| Need | Authority | Locked treatment |
|---|---|---|
| Current tract/counties | Census 2020 tabulation geography | Current production tract backbone is 2020; 2023 current crosswalk is a migration input only |
| Block memberships and weights | 2020 PL 94-171 + Place BAF + ZCTA/block relationship | Ingest state by state: PL population/housing records plus Place BAF assignments. The national Census ZCTA-to-block relationship file supplies complete 2020 ZCTA membership. Do not ingest block polygons. |
| 2010→2020 tract harmonization | Census block relationship files | Derive population/HU allocation by carrying decennial block counts through block intersections; use relationship-file intersection land area for land basis. |
| CBSA current boundary | OMB Bulletin 23-01 (July 2023) | Store every bulletin as its own vintage. A later approved bulletin adds rows and changes the mart's `is_current` selection; it never overwrites history. |
| ZIP allocation | HUD-USPS quarterly files | Preserve release quarter, address-ratio basis, source denominator where published, and `99999` non-CBSA handling. |
| Display geometry | Census cartographic boundary | Use 1:500,000 as the default tract-map display product; permit 1:5,000,000 only for nationwide overview maps. |

The national 2020 tract relationship file is approximately 18 MB, but block
inputs are state-based and substantially larger. Download, stage, validate, and
materialize one state at a time; DuckDB writes remain sequential.

## Geometry build policy

`foundations/etl/geo/get_tiger_geos.R` is an on-demand cartographic display
builder. It requires `GEOGRAPHY_TIGER_STATE_SCOPE`; a state-scoped run writes
only `geo.tracts_<state>_display` with `geometry_role = 'display'` and a
`boundary_vintage`. `ALL` additionally writes the national tract display table.
Set `GEOGRAPHY_TIGER_REFERENCE=true` only when state, county, and CBSA display
products are needed. It never replaces the legacy `geo.*` products and never
creates full TIGER/Line analytical geometry.

## Operations

- The containment-first `rollup()` interface is implemented as transparent
  `mart_geography.rollup_*` views, not a metric-aggregating function. Current
  tract-to-CBSA output exposes both `tract_boundary_vintage = 2020` and
  `cbsa_boundary_vintage = 2023`.
- `rollup()` accepts declared containment edges only.
- `allocate()` requires an explicit basis: `population`, `housing_units`, or
  `land_area`; it carries `quality_flag`.
- `harmonize()` restates from an older boundary vintage to the latest approved
  target and carries `change_type`.
- `get_geometry()` discovers and returns a materialized `display` table only;
  it does not silently fall back to legacy geometry or create analysis shapes.
- `export_geometry()` produces scoped local artifacts only.

No helper may imply that a rate, median, or index is additive.

## Containment-first mart

The current implementation exposes `identity_current`, `identity_vintaged`,
`exact_relationships`, exact rollup views, `zip_allocation_catalog`,
`allocation_edges`, `temporal_edges`, allocation/identity audit views, and a
geometry catalog in `mart_geography`. The Python relationship helpers and SQL
examples preserve explicit basis selection. They deliberately do not aggregate
metrics: a rate-safe consumer must reconstruct its numerator and denominator.
