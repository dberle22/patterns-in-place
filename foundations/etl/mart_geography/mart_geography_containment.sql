-- Geography mart. Exact containment, explicitly weighted allocation, temporal
-- harmonization, and geometry discovery remain separate interfaces by design.
create schema if not exists mart_geography;

-- The current selector follows the approved 2020 Census backbone and the 2023
-- OMB CBSA delineation. Historical rows remain available in the next view.
create or replace view mart_geography.identity_current as
select geo_level, geo_id, boundary_vintage, geo_name, display_name,
       containment_parent_level, containment_parent_id, stability_class,
       land_area_sqm, water_area_sqm, source_release_year, source
from silver.dim_geo
where (geo_level in ('tract', 'county', 'state') and boundary_vintage = 2020)
   or (geo_level = 'cbsa' and boundary_vintage = 2023)
   or (geo_level in ('us', 'region', 'division') and boundary_vintage = 2023)
   or (geo_level in ('place', 'zcta') and boundary_vintage = 2020);

create or replace view mart_geography.identity_vintaged as
select geo_level, geo_id, boundary_vintage, geo_name, display_name,
       containment_parent_level, containment_parent_id, stability_class,
       land_area_sqm, water_area_sqm, source_release_year, source
from silver.dim_geo;

-- Exact edges only. This type boundary prevents an allocation from being used
-- as an exact parent relationship.
create or replace view mart_geography.exact_relationships as
select child_geo_id, child_geo_level, parent_geo_id, parent_geo_level,
       boundary_vintage, relationship_quality, source
from silver.xwalk_containment;

-- Named views are the initial rollup interface. They supply the declared
-- relationship only; consumers retain metric-aware aggregation responsibility.
create or replace view mart_geography.rollup_tract_to_county as
select child_geo_id as tract_geoid, parent_geo_id as county_geoid,
       boundary_vintage, source
from mart_geography.exact_relationships
where child_geo_level = 'tract'
  and parent_geo_level = 'county'
  and boundary_vintage = 2020;

create or replace view mart_geography.rollup_county_to_cbsa as
select child_geo_id as county_geoid, parent_geo_id as cbsa_code,
       boundary_vintage, source
from mart_geography.exact_relationships
where child_geo_level = 'county'
  and parent_geo_level = 'cbsa'
  and boundary_vintage = 2023;

create or replace view mart_geography.rollup_tract_to_cbsa as
select tract.tract_geoid, county.cbsa_code,
       tract.boundary_vintage as tract_boundary_vintage,
       county.boundary_vintage as cbsa_boundary_vintage,
       tract.source as tract_county_source, county.source as county_cbsa_source
from mart_geography.rollup_tract_to_county as tract
inner join mart_geography.rollup_county_to_cbsa as county
    on tract.county_geoid = county.county_geoid;

create or replace view mart_geography.zip_allocation_catalog as
select 'zip_to_county' as relationship_id, 'zip' as source_geo_level,
       'county' as target_geo_level, source_release_year, source_release, source,
       'residential_addresses,business_addresses,other_addresses,total_addresses' as supported_bases,
       count(*) as edge_count
from silver.xwalk_zip_county
group by 1, 2, 3, 4, 5, 6, 7
union all
select 'zip_to_cbsa', 'zip', 'cbsa', source_release_year, source_release, source,
       'residential_addresses,business_addresses,other_addresses,total_addresses', count(*)
from silver.xwalk_zip_cbsa
group by 1, 2, 3, 4, 5, 6, 7
union all
select 'zip_to_tract', 'zip', 'tract', source_release_year, source_release, source,
       'residential_addresses,business_addresses,other_addresses,total_addresses', count(*)
from silver.xwalk_zip_tract
group by 1, 2, 3, 4, 5, 6, 7;

-- Allocation edges never become exact relationships. Callers must filter an
-- explicit basis before joining a metric at tract grain to Place or ZCTA.
create or replace view mart_geography.allocation_edges as
select source_geo_id, source_geo_level, target_geo_id, target_geo_level,
       source_boundary_vintage, target_boundary_vintage, weight_basis, weight,
       source_denominator, target_numerator, allocated_weight_sum, quality_flag,
       source
from silver.xwalk_allocation;

-- Temporal edges restate a 2010 tract metric to the 2020 tract backbone. The
-- population and housing edges are area-interpolated through Census block
-- intersections; callers should retain change_type/quality_flag in outputs.
create or replace view mart_geography.temporal_edges as
select from_geo_id, from_geo_level, from_boundary_vintage,
       to_geo_id, to_geo_level, to_boundary_vintage, weight_basis, weight,
       source_denominator, target_numerator, allocated_weight_sum,
       change_type, quality_flag, source
from silver.xwalk_temporal;

create or replace view mart_geography.allocation_coverage_audit as
select audit_name, boundary_vintage, source_unit_count,
       source_unit_with_edges_count, unmatched_source_count,
       fully_allocated_source_count, partial_source_count,
       zero_denominator_source_count, max_weight_sum_deviation
from silver.geography_allocation_audit;

-- Geometry discovery separates the approved, seeded display products from
-- future role-tagged materializations. The three approved products were built
-- by the former Census cartographic-boundary `tigris(..., cb = TRUE, year =
-- 2024)` job and are intentionally retained as read-only display inputs; this
-- catalog records their provenance without rewriting their existing rows.
create or replace view mart_geography.geometry_catalog as
select table_name,
       regexp_extract(table_name, '^tracts_([a-z]{2})_display$', 1) as state_scope,
       case
         when table_name like '%_analysis' then 'analysis'
         when table_name in ('tracts_all_us', 'counties', 'cbsas')
           or table_name like '%_display' then 'display'
         else 'legacy_unclassified'
       end as geometry_role,
       case
         when table_name in ('states_analysis', 'cbsas_analysis') then '2023_tiger_line'
         when table_name in ('tracts_all_us', 'counties', 'cbsas')
           then '2024_census_cartographic_boundary'
         when table_name like '%_display' then 'recorded_in_table'
         else 'unknown_legacy_vintage'
       end as boundary_vintage_status,
       case
         when table_name = 'states_analysis' then 'state'
         when table_name = 'cbsas_analysis' then 'cbsa'
         when table_name like 'tracts%' then 'tract'
         when table_name like 'states%' then 'state'
         when table_name like 'counties%' then 'county'
         when table_name like 'cbsas%' then 'cbsa'
       end as geo_level,
       case
         when table_name = 'states_analysis' then 'state_fips'
         when table_name = 'cbsas_analysis' then 'cbsa_code'
         when table_name = 'tracts_all_us' then 'tract_geoid'
         when table_name = 'counties' then 'county_geoid'
         when table_name = 'cbsas' then 'cbsa_code'
         else null
       end as stable_join_key,
       case
         when table_name in ('states_analysis', 'cbsas_analysis') then 'Census TIGER/Line 2023 via tigris'
         when table_name in ('tracts_all_us', 'counties', 'cbsas')
           then 'Census cartographic boundary via tigris; source year 2024'
         when table_name like '%_display' then 'Recorded in table metadata'
         else 'Unknown legacy source'
       end as source_vintage,
       case
         when table_name in ('states_analysis', 'cbsas_analysis') then 'materialized_analysis'
         when table_name in ('tracts_all_us', 'counties', 'cbsas')
           then 'approved_read_only_display'
         when table_name like '%_display' then 'materialized_display'
         else 'legacy_unclassified'
       end as consumer_status,
       case
         when table_name in ('states_analysis', 'cbsas_analysis') then
           'Approved only for declared state adjacency, CBSA centroid, and scoped downstream spatial work at the recorded boundary vintage; do not substitute it for display geometry or a different vintage.'
         when table_name in ('tracts_all_us', 'counties', 'cbsas') then
           'Map display and geometry export only; not analytical geometry, not a boundary-vintage authority, and not valid for spatial allocation, containment, area, or distance calculations.'
         when table_name like '%_display' then
           'Display only; use a role-tagged analytical product for spatial analysis.'
         else 'Not approved for governed consumer use until provenance is recorded.'
       end as limitations
from information_schema.tables
where table_schema = 'geo'
  and (
    table_name in ('states', 'counties', 'cbsas', 'tracts_all_us',
                   'states_display', 'counties_display', 'cbsas_display',
                   'tracts_all_us_display', 'states_analysis', 'cbsas_analysis')
    or regexp_matches(table_name, '^tracts_[a-z]{2}_display$')
  );

create or replace view mart_geography.coverage_audit as
select audit_name, boundary_vintage, row_count, distinct_key_count, duplicate_key_count
from silver.geography_coverage_audit;
