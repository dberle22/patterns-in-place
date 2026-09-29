# Build explicitly weighted 2020 allocation and 2010-to-2020 temporal edges.
# These tables only describe a relationship; consumers must still decide whether
# their metric is additive and choose a basis explicitly at query time.
source(here::here("foundations", "etl", "utils.R"))

if (file.exists(".Renviron")) readRenviron(".Renviron")

library(DBI)
library(duckdb)

db_path <- get_env_path("DB_PATH")
con <- dbConnect(duckdb::duckdb(), dbdir = db_path, read_only = FALSE)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)
dbExecute(con, "CREATE SCHEMA IF NOT EXISTS silver")

# Place and ZCTA membership is assigned at the 2020 block level. Summing each
# basis by source tract and target produces independent population, housing,
# and land-area weights rather than one falsely universal allocation weight.
dbExecute(con, "
  CREATE OR REPLACE TABLE silver.xwalk_allocation AS
  WITH tract_totals AS (
    SELECT tract_geoid AS source_geo_id,
           sum(population_2020) AS population_denominator,
           sum(housing_units_2020) AS housing_units_denominator,
           sum(land_area_sqm) AS land_area_denominator
    FROM silver.block_registry
    GROUP BY 1
  ),
  target_edges AS (
    SELECT tract_geoid AS source_geo_id, 'tract' AS source_geo_level,
           concat(state_fips, place_geoid) AS target_geo_id, 'place' AS target_geo_level,
           sum(population_2020) AS population_numerator,
           sum(housing_units_2020) AS housing_units_numerator,
           sum(land_area_sqm) AS land_area_numerator
    FROM silver.block_registry
    WHERE place_geoid IS NOT NULL
    GROUP BY 1, 2, 3, 4
    UNION ALL
    SELECT tract_geoid, 'tract', zcta_geoid, 'zcta',
           sum(population_2020), sum(housing_units_2020), sum(land_area_sqm)
    FROM silver.block_registry
    WHERE zcta_geoid IS NOT NULL
    GROUP BY 1, 2, 3, 4
  ),
  basis_edges AS (
    SELECT edge.source_geo_id, edge.source_geo_level, edge.target_geo_id, edge.target_geo_level,
           2020 AS source_boundary_vintage, 2020 AS target_boundary_vintage,
           'population' AS weight_basis, edge.population_numerator AS numerator,
           total.population_denominator AS source_denominator
    FROM target_edges AS edge JOIN tract_totals AS total USING (source_geo_id)
    UNION ALL
    SELECT edge.source_geo_id, edge.source_geo_level, edge.target_geo_id, edge.target_geo_level,
           2020, 2020, 'housing_units', edge.housing_units_numerator, total.housing_units_denominator
    FROM target_edges AS edge JOIN tract_totals AS total USING (source_geo_id)
    UNION ALL
    SELECT edge.source_geo_id, edge.source_geo_level, edge.target_geo_id, edge.target_geo_level,
           2020, 2020, 'land_area', edge.land_area_numerator, total.land_area_denominator
    FROM target_edges AS edge JOIN tract_totals AS total USING (source_geo_id)
  ),
  weighted AS (
    SELECT *, numerator / nullif(source_denominator, 0) AS weight
    FROM basis_edges
  ),
  audited AS (
    SELECT *, sum(coalesce(weight, 0)) OVER source_window AS allocated_weight_sum,
           max(coalesce(weight, 0)) OVER source_window AS dominant_weight,
           count(*) OVER source_window AS target_count
    FROM weighted
    WINDOW source_window AS (PARTITION BY source_geo_id, source_geo_level, target_geo_level, weight_basis,
                             source_boundary_vintage, target_boundary_vintage)
  )
  SELECT source_geo_id, source_geo_level, target_geo_id, target_geo_level,
         source_boundary_vintage, target_boundary_vintage, weight_basis, weight,
         source_denominator, numerator AS target_numerator, allocated_weight_sum,
         CASE
           WHEN source_denominator = 0 THEN 'undefined'
           WHEN allocated_weight_sum < 0.999999 THEN 'partial'
           WHEN target_count = 1 AND dominant_weight >= 0.999999 THEN 'exact'
           WHEN dominant_weight >= 0.95 THEN 'clean'
           ELSE 'split'
         END AS quality_flag,
         'CENSUS_2020_PL94_171_BAF' AS source
  FROM audited
")

# Population and housing use areal interpolation from each 2010 block through
# its Census-provided block intersections. Land area instead uses the direct
# tract relationship file, which is the published tract-level authority.
dbExecute(con, "
  CREATE OR REPLACE TABLE silver.xwalk_temporal AS
  WITH block_intersections AS (
    SELECT relationship.from_block_geoid, relationship.to_block_geoid,
           relationship.intersection_land_area_sqm,
           sum(relationship.intersection_land_area_sqm) OVER (PARTITION BY relationship.from_block_geoid) AS block_intersection_denominator,
           source.tract_geoid AS from_tract_geoid, target.tract_geoid AS to_tract_geoid,
           source.population_2010, source.housing_units_2010
    FROM staging.census_block_relationship_2010_2020 AS relationship
    INNER JOIN staging.census_pl2010_blocks AS source
      ON relationship.from_block_geoid = source.block_geoid
    INNER JOIN silver.block_registry AS target
      ON relationship.to_block_geoid = target.block_geoid
  ),
  tract_totals AS (
    SELECT tract_geoid AS from_tract_geoid, sum(population_2010) AS population_denominator,
           sum(housing_units_2010) AS housing_units_denominator
    FROM staging.census_pl2010_blocks
    GROUP BY 1
  ),
  count_edges AS (
    SELECT from_tract_geoid, to_tract_geoid,
           sum(population_2010 * intersection_land_area_sqm / nullif(block_intersection_denominator, 0)) AS population_numerator,
           sum(housing_units_2010 * intersection_land_area_sqm / nullif(block_intersection_denominator, 0)) AS housing_units_numerator
    FROM block_intersections
    GROUP BY 1, 2
  ),
  basis_edges AS (
    SELECT edge.from_tract_geoid, edge.to_tract_geoid, 'population' AS weight_basis,
           edge.population_numerator AS numerator, total.population_denominator AS source_denominator,
           'CENSUS_2010_PL94_171 + CENSUS_2020_BLOCK_RELATIONSHIP' AS source
    FROM count_edges AS edge JOIN tract_totals AS total USING (from_tract_geoid)
    UNION ALL
    SELECT edge.from_tract_geoid, edge.to_tract_geoid, 'housing_units',
           edge.housing_units_numerator, total.housing_units_denominator,
           'CENSUS_2010_PL94_171 + CENSUS_2020_BLOCK_RELATIONSHIP'
    FROM count_edges AS edge JOIN tract_totals AS total USING (from_tract_geoid)
    UNION ALL
    SELECT relationship.from_tract_geoid, relationship.to_tract_geoid, 'land_area',
           relationship.intersection_land_area_sqm, relationship.from_land_area_sqm,
           'CENSUS_2020_TRACT_RELATIONSHIP'
    FROM staging.census_tract_relationship_2010_2020 AS relationship
    -- The national tract file also includes territories. V1 is the 50 states
    -- plus DC, so retain only source tracts present in staged 2010 PL data.
    INNER JOIN tract_totals AS total USING (from_tract_geoid)
  ),
  weighted AS (
    SELECT *, numerator / nullif(source_denominator, 0) AS weight
    FROM basis_edges
  ),
  audited AS (
    SELECT *, sum(coalesce(weight, 0)) OVER source_window AS allocated_weight_sum,
           count(*) OVER source_window AS target_count
    FROM weighted
    WINDOW source_window AS (PARTITION BY from_tract_geoid, weight_basis)
  )
  SELECT from_tract_geoid AS from_geo_id, 'tract' AS from_geo_level, 2010 AS from_boundary_vintage,
         to_tract_geoid AS to_geo_id, 'tract' AS to_geo_level, 2020 AS to_boundary_vintage,
         weight_basis, weight, source_denominator, numerator AS target_numerator, allocated_weight_sum,
         CASE
           WHEN source_denominator = 0 THEN 'undefined'
           WHEN allocated_weight_sum < 0.999999 THEN 'partial'
           WHEN target_count = 1 AND allocated_weight_sum >= 0.999999 THEN 'unchanged'
           WHEN target_count > 1 THEN 'split'
           ELSE 'redrawn'
         END AS change_type,
         CASE
           WHEN source_denominator = 0 THEN 'undefined'
           WHEN allocated_weight_sum < 0.999999 THEN 'partial'
           ELSE 'complete'
         END AS quality_flag,
         source
  FROM audited
")

# Census Places are not administrative children of counties or CBSAs. Build
# their relationships from 2020 blocks and retain all overlaps as weighted
# membership rows. County-to-CBSA membership is current OMB 2023 membership,
# while the Place and county numerators remain 2020 Census geography.
dbExecute(con, "
  CREATE OR REPLACE TABLE silver.xwalk_place_membership AS
  WITH place_blocks AS (
    SELECT concat(state_fips, place_geoid) AS place_geoid, county_geoid,
           population_2020, housing_units_2020, land_area_sqm
    FROM silver.block_registry
    WHERE place_geoid IS NOT NULL
  ),
  place_totals AS (
    SELECT place_geoid, sum(population_2020) AS population_denominator,
           sum(housing_units_2020) AS housing_units_denominator,
           sum(land_area_sqm) AS land_area_denominator
    FROM place_blocks GROUP BY 1
  ),
  county_targets AS (
    SELECT county_geoid AS target_geo_id, 'county' AS target_geo_level,
           sum(population_2020) AS population_denominator,
           sum(housing_units_2020) AS housing_units_denominator,
           sum(land_area_sqm) AS land_area_denominator
    FROM silver.block_registry GROUP BY 1, 2
  ),
  current_cbsa_counties AS (
    SELECT DISTINCT county_geoid, cbsa_code
    FROM silver.xwalk_cbsa_county
  ),
  cbsa_targets AS (
    SELECT cbsa.cbsa_code AS target_geo_id, 'cbsa' AS target_geo_level,
           sum(block.population_2020) AS population_denominator,
           sum(block.housing_units_2020) AS housing_units_denominator,
           sum(block.land_area_sqm) AS land_area_denominator
    FROM silver.block_registry AS block
    INNER JOIN current_cbsa_counties AS cbsa USING (county_geoid)
    GROUP BY 1, 2
  ),
  county_membership AS (
    SELECT place_geoid, county_geoid AS target_geo_id, 'county' AS target_geo_level,
           sum(population_2020) AS population_numerator,
           sum(housing_units_2020) AS housing_units_numerator,
           sum(land_area_sqm) AS land_area_numerator
    FROM place_blocks GROUP BY 1, 2, 3
  ),
  cbsa_membership AS (
    SELECT block.place_geoid, cbsa.cbsa_code AS target_geo_id, 'cbsa' AS target_geo_level,
           sum(block.population_2020) AS population_numerator,
           sum(block.housing_units_2020) AS housing_units_numerator,
           sum(block.land_area_sqm) AS land_area_numerator
    FROM place_blocks AS block
    INNER JOIN current_cbsa_counties AS cbsa USING (county_geoid)
    GROUP BY 1, 2, 3
  ),
  membership AS (
    SELECT * FROM county_membership UNION ALL SELECT * FROM cbsa_membership
  ),
  target_totals AS (
    SELECT * FROM county_targets UNION ALL SELECT * FROM cbsa_targets
  ),
  basis_rows AS (
    SELECT membership.place_geoid, membership.target_geo_id, membership.target_geo_level,
           2020 AS place_boundary_vintage,
           CASE WHEN membership.target_geo_level = 'county' THEN 2020 ELSE 2023 END AS target_boundary_vintage,
           'population' AS weight_basis, membership.population_numerator AS target_numerator,
           place.population_denominator AS place_denominator,
           target.population_denominator AS target_denominator
    FROM membership
    JOIN place_totals AS place USING (place_geoid)
    JOIN target_totals AS target USING (target_geo_id, target_geo_level)
    UNION ALL
    SELECT membership.place_geoid, membership.target_geo_id, membership.target_geo_level,
           2020, CASE WHEN membership.target_geo_level = 'county' THEN 2020 ELSE 2023 END,
           'housing_units', membership.housing_units_numerator,
           place.housing_units_denominator, target.housing_units_denominator
    FROM membership
    JOIN place_totals AS place USING (place_geoid)
    JOIN target_totals AS target USING (target_geo_id, target_geo_level)
    UNION ALL
    SELECT membership.place_geoid, membership.target_geo_id, membership.target_geo_level,
           2020, CASE WHEN membership.target_geo_level = 'county' THEN 2020 ELSE 2023 END,
           'land_area', membership.land_area_numerator,
           place.land_area_denominator, target.land_area_denominator
    FROM membership
    JOIN place_totals AS place USING (place_geoid)
    JOIN target_totals AS target USING (target_geo_id, target_geo_level)
  ),
  weighted AS (
    SELECT *, target_numerator / nullif(place_denominator, 0) AS target_share_in_place,
           target_numerator / nullif(target_denominator, 0) AS place_share_in_target
    FROM basis_rows
  ),
  audited AS (
    SELECT *, sum(coalesce(target_share_in_place, 0)) OVER place_window AS allocated_place_share,
           max(coalesce(target_share_in_place, 0)) OVER place_window AS dominant_target_share,
           count(*) OVER place_window AS target_count
    FROM weighted
    WINDOW place_window AS (PARTITION BY place_geoid, target_geo_level, weight_basis)
  ),
  primary_cbsa AS (
    SELECT place_geoid, target_geo_id AS primary_cbsa_code,
           target_share_in_place AS primary_population_share
    FROM (
      SELECT *, row_number() OVER (
        PARTITION BY place_geoid ORDER BY target_share_in_place DESC, target_geo_id
      ) AS association_rank
      FROM audited
      WHERE target_geo_level = 'cbsa' AND weight_basis = 'population'
        AND target_share_in_place IS NOT NULL
    )
    WHERE association_rank = 1
  )
  SELECT audited.place_geoid, audited.target_geo_id, audited.target_geo_level,
         audited.place_boundary_vintage, audited.target_boundary_vintage,
         audited.weight_basis, audited.target_numerator, audited.place_denominator,
         audited.target_denominator, audited.target_share_in_place,
         audited.place_share_in_target, audited.allocated_place_share,
         CASE
           WHEN audited.place_denominator = 0 THEN 'undefined'
           WHEN audited.allocated_place_share < 0.999999 THEN 'partial'
           WHEN audited.target_count = 1 THEN 'whole'
           ELSE 'split'
         END AS membership_status,
         CASE
           WHEN audited.place_denominator = 0 THEN 'undefined'
           WHEN audited.allocated_place_share < 0.999999 THEN 'partial'
           WHEN audited.target_count = 1 THEN 'exact'
           WHEN audited.dominant_target_share >= 0.95 THEN 'clean'
           ELSE 'split'
         END AS quality_flag,
         primary_assoc.primary_cbsa_code,
         primary_assoc.primary_population_share,
         audited.target_geo_level = 'cbsa'
           AND audited.weight_basis = 'population'
           AND audited.target_geo_id = primary_assoc.primary_cbsa_code AS is_primary_cbsa,
         'CENSUS_2020_PL94_171_BAF + OMB_2023_COUNTY_CBSA' AS source
  FROM audited
  LEFT JOIN primary_cbsa AS primary_assoc USING (place_geoid)
")

# Every Census Place receives a declared primary-CBSA record, including Places
# with no current CBSA block membership. A primary association is a label for
# selection only; it does not collapse or erase split membership rows.
dbExecute(con, "
  CREATE OR REPLACE TABLE silver.place_primary_cbsa_association AS
  WITH places AS (
    SELECT DISTINCT concat(state_fips, place_geoid) AS place_geoid
    FROM silver.block_registry WHERE place_geoid IS NOT NULL
  ),
  population_summary AS (
    SELECT place_geoid, count(*) AS cbsa_count,
           max(place_denominator) AS population_denominator,
           max(allocated_place_share) AS cbsa_coverage_share
    FROM silver.xwalk_place_membership
    WHERE target_geo_level = 'cbsa' AND weight_basis = 'population'
    GROUP BY 1
  ),
  primary_membership AS (
    SELECT place_geoid, primary_cbsa_code, primary_population_share
    FROM silver.xwalk_place_membership
    WHERE is_primary_cbsa
  )
  SELECT places.place_geoid, primary_assoc.primary_cbsa_code,
         primary_assoc.primary_population_share, coalesce(summary.cbsa_coverage_share, 0.0) AS cbsa_coverage_share,
         coalesce(summary.cbsa_count, 0) AS cbsa_count,
         CASE
           WHEN coalesce(summary.cbsa_count, 0) = 0 THEN 'no_cbsa_membership'
           WHEN summary.population_denominator = 0 THEN 'undefined_population_basis'
           WHEN primary_assoc.primary_cbsa_code IS NULL THEN 'no_cbsa_membership'
           WHEN summary.cbsa_coverage_share < 0.999999 THEN 'partial_cbsa_membership'
           WHEN summary.cbsa_count = 1 THEN 'whole_cbsa_membership'
           ELSE 'split_cbsa_membership'
         END AS association_status,
         2020 AS place_boundary_vintage, 2023 AS cbsa_boundary_vintage,
         'population' AS selection_basis,
         'CENSUS_2020_PL94_171_BAF + OMB_2023_COUNTY_CBSA' AS source
  FROM places
  LEFT JOIN population_summary AS summary USING (place_geoid)
  LEFT JOIN primary_membership AS primary_assoc USING (place_geoid)
")

# These national structural diagnostics make complete, split, partial, and
# unassociated Place memberships inspectable without pretending the rows are
# exact containment edges.
dbExecute(con, "
  CREATE OR REPLACE TABLE silver.geography_place_membership_audit AS
  WITH places AS (
    SELECT DISTINCT concat(state_fips, place_geoid) AS place_geoid
    FROM silver.block_registry WHERE place_geoid IS NOT NULL
  ),
  catalog AS (
    SELECT target_geo_level, weight_basis
    FROM silver.xwalk_place_membership GROUP BY 1, 2
  ),
  place_summary AS (
    SELECT place_geoid, target_geo_level, weight_basis,
           max(membership_status) AS membership_status,
           max(allocated_place_share) AS allocated_place_share
    FROM silver.xwalk_place_membership
    GROUP BY 1, 2, 3
  )
  SELECT catalog.target_geo_level, catalog.weight_basis,
         count(*) AS place_count,
         count(summary.place_geoid) AS place_with_membership_count,
         count(*) - count(summary.place_geoid) AS place_without_membership_count,
         count(CASE WHEN summary.membership_status = 'whole' THEN 1 END) AS whole_place_count,
         count(CASE WHEN summary.membership_status = 'split' THEN 1 END) AS split_place_count,
         count(CASE WHEN summary.membership_status = 'partial' THEN 1 END) AS partial_place_count,
         count(CASE WHEN summary.membership_status = 'undefined' THEN 1 END) AS undefined_place_count,
         max(CASE WHEN summary.membership_status <> 'undefined'
                  THEN abs(summary.allocated_place_share - 1.0) END) AS max_allocation_gap,
         2020 AS place_boundary_vintage,
         CASE WHEN catalog.target_geo_level = 'county' THEN 2020 ELSE 2023 END AS target_boundary_vintage
  FROM places
  CROSS JOIN catalog
  LEFT JOIN place_summary AS summary
    ON places.place_geoid = summary.place_geoid
   AND catalog.target_geo_level = summary.target_geo_level
   AND catalog.weight_basis = summary.weight_basis
  GROUP BY 1, 2
")

# Fail fast on type and selection regressions. Split Places must remain rows,
# while a Place with a CBSA membership must have exactly one population-based
# primary association.
duplicate_memberships <- dbGetQuery(con, "
  SELECT count(*) AS n FROM (
    SELECT place_geoid, target_geo_id, target_geo_level, weight_basis, count(*) AS row_count
    FROM silver.xwalk_place_membership
    GROUP BY 1, 2, 3, 4 HAVING count(*) > 1
  )
")$n[[1]]
if (duplicate_memberships != 0) stop("Place membership build produced duplicate typed edges.", call. = FALSE)

missing_primary <- dbGetQuery(con, "
  SELECT count(*) AS n
  FROM silver.place_primary_cbsa_association
  WHERE cbsa_count > 0 AND association_status <> 'undefined_population_basis'
    AND primary_cbsa_code IS NULL
")$n[[1]]
if (missing_primary != 0) stop("A Place with CBSA membership has no primary association.", call. = FALSE)

# Coverage records make gaps and denominator failures queryable. They are
# structural evidence only; downstream metric QA remains intentionally deferred.
dbExecute(con, "
  CREATE OR REPLACE TABLE silver.geography_allocation_audit AS
  WITH current_tracts AS (
    SELECT DISTINCT tract_geoid AS source_geo_id FROM silver.block_registry
  ),
  allocation_catalog AS (
    SELECT target_geo_level, weight_basis
    FROM silver.xwalk_allocation GROUP BY 1, 2
  ),
  allocation_source_summary AS (
    SELECT source_geo_id, target_geo_level, weight_basis,
           max(quality_flag) AS quality_flag, max(allocated_weight_sum) AS allocated_weight_sum
    FROM silver.xwalk_allocation
    GROUP BY 1, 2, 3
  ),
  temporal_catalog AS (
    SELECT DISTINCT weight_basis FROM silver.xwalk_temporal
  ),
  temporal_sources AS (
    SELECT DISTINCT tract_geoid AS from_geo_id FROM staging.census_pl2010_blocks
  ),
  temporal_source_summary AS (
    SELECT from_geo_id, weight_basis, max(quality_flag) AS quality_flag,
           max(allocated_weight_sum) AS allocated_weight_sum
    FROM silver.xwalk_temporal
    GROUP BY 1, 2
  )
  SELECT concat('tract_to_', catalog.target_geo_level, '_', catalog.weight_basis) AS audit_name,
         2020 AS boundary_vintage,
         count(*) AS source_unit_count,
         count(summary.source_geo_id) AS source_unit_with_edges_count,
         count(*) - count(summary.source_geo_id) AS unmatched_source_count,
         count(CASE WHEN summary.quality_flag IN ('exact', 'clean', 'split') THEN 1 END) AS fully_allocated_source_count,
         count(CASE WHEN summary.quality_flag = 'partial' THEN 1 END) AS partial_source_count,
         count(CASE WHEN summary.quality_flag = 'undefined' THEN 1 END) AS zero_denominator_source_count,
         max(CASE WHEN summary.quality_flag <> 'undefined' THEN abs(summary.allocated_weight_sum - 1.0) END) AS max_weight_sum_deviation
  FROM current_tracts AS source
  CROSS JOIN allocation_catalog AS catalog
  LEFT JOIN allocation_source_summary AS summary
    ON source.source_geo_id = summary.source_geo_id
   AND catalog.target_geo_level = summary.target_geo_level
   AND catalog.weight_basis = summary.weight_basis
  GROUP BY 1, 2
  UNION ALL
  SELECT concat('tract_2010_to_tract_2020_', catalog.weight_basis), 2010,
         count(*), count(summary.from_geo_id), count(*) - count(summary.from_geo_id),
         count(CASE WHEN summary.quality_flag = 'complete' THEN 1 END),
         count(CASE WHEN summary.quality_flag = 'partial' THEN 1 END),
         count(CASE WHEN summary.quality_flag = 'undefined' THEN 1 END),
         max(CASE WHEN summary.quality_flag <> 'undefined' THEN abs(summary.allocated_weight_sum - 1.0) END)
  FROM temporal_sources AS source
  CROSS JOIN temporal_catalog AS catalog
  LEFT JOIN temporal_source_summary AS summary
    ON source.from_geo_id = summary.from_geo_id
   AND catalog.weight_basis = summary.weight_basis
  GROUP BY 1, 2
")

message("Built governed allocation, temporal, and coverage-audit tables.")
