# Geography Engine Usage

## Choose the source geography first

ACS ZCTA data is already Census ZCTA data: join it directly to
`mart_geography.identity_current` at `geo_level = 'zcta'`. Do not translate it
through USPS ZIP. A source that actually publishes USPS ZIP uses the versioned
HUD-USPS `silver.xwalk_zip_*` allocation tables and must name an address basis.

## Operations

- Exact rollups use `mart_geography.rollup_*` views and only additive metrics.
- Place/ZCTA allocation uses `mart_geography.allocation_edges` with an explicit
  `population`, `housing_units`, or `land_area` basis. Preserve `quality_flag`.
- 2010 tract values restated to 2020 use `mart_geography.temporal_edges` with
  an explicit basis. Preserve `change_type` and `quality_flag`.
- Rates, medians, percentages, and indices are not additive. Reconstruct them
  from appropriate numerator/denominator inputs rather than summing values.

## Geometry

Geometry is optional and separate from identities. The approved current
read-only display products are `geo.tracts_all_us` (`tract_geoid`),
`geo.counties` (`county_geoid`), and `geo.cbsas` (`cbsa_code`). They use Census
2024 cartographic-boundary source geometry and may be joined by those stable
keys for market maps and scoped geometry exports. No separate materialization
is needed for that display use.

Discover approved and role-tagged display tables through
`mart_geography.geometry_catalog`, then use `get_geometry()` or
`export_geometry()` from `geography.py`. Filter the catalog to
`consumer_status IN ('approved_read_only_display', 'materialized_display')`
when a consumer needs an explicit eligibility check. These display products
are not valid for point containment, overlays/intersections, allocation,
area, distance, or historical-boundary analysis; request a role-tagged
`geo.<level>_analysis` table for those operations. Other legacy `geo.*` tables
remain unapproved unless the catalog says otherwise.

## QA boundary

The current release has structural coverage and weight-sum audits. Full
metric-level allocation and temporal QA is deferred until a named consumer
specifies its metric, direction, basis, and interpretation requirements.
