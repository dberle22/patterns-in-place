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
- Place-to-County and Place-to-CBSA use
  `mart_geography.place_to_{county,cbsa}_membership` with an explicit
  population, housing-unit, or land-area basis. They are weighted membership,
  never exact containment. `target_share_in_place` is the share of a Place in
  the selected County/CBSA; `place_share_in_target` is the share of that
  County/CBSA in the Place.
- `mart_geography.place_primary_cbsa_association` selects the CBSA with the
  largest 2020 population share for each Place. It is a selection label only:
  use `association_status` and the complete membership surface to retain
  split, partial, and no-CBSA associations. Direct Place measures may be used
  whole only for `whole_cbsa_membership`; otherwise allocate explicitly or
  retain a whole-Place caveat.
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

### Census Place spatial assignment

For POI, Infrastructure, and Q6 spatial work, request
`get_geometry(con, "places_analysis", role="analysis")`; never substitute
`geo.places_display`. Build the bounded product with
`GEOGRAPHY_PLACE_ANALYSIS_STATE_SCOPE=ALL Rscript
foundations/etl/geo/build_places_analysis.R`. The table stores WGS84 geometry
for interchange. Transform to its recorded `EPSG:5070` analytical CRS before
calculating length or area, for example
`ST_Transform(geom, 'EPSG:4326', 'EPSG:5070', true)`.

`assign_point_to_place(con, longitude, latitude)` is the governed WGS84
point-assignment interface. Its statuses are `within`, `boundary`, `overlap`,
and `no_place`; the last is expected for unincorporated territory and must not
be coerced to a nearby Place. `place_line_intersections(con, wkb)` returns all
Places intersected by a WGS84 line or polygon. Inspect
`geo.places_analysis_qa` after each build; Virginia-scoped builds include
Richmond point and line smoke checks.

## Regional Role lenses

Read `mart_geography.region_lens_membership` rather than recreating a regional
boundary in a notebook. It includes `census_division`, `primary_state`,
`primary_state_adjacent`, and `cbsa_centroid_250mi`; the last stores declared
200-, 250-, and 300-mile parameter values plus `distance_miles`. Primary state
uses the first state in the official CBSA label (`gold.dim_geo.state_fips`).

`mart_geography.state_adjacency` is symmetric and land-only.
`mart_geography.cbsa_centroids` is a geographic-proximity reference point, not
a travel-time or commuting proxy. A consumer needing the approved full-TIGER
CBSA boundary must explicitly request
`get_geometry(con, "cbsas_analysis", role="analysis")`.

## QA boundary

The current release has structural coverage and weight-sum audits. Full
metric-level allocation and temporal QA is deferred until a named consumer
specifies its metric, direction, basis, and interpretation requirements.
