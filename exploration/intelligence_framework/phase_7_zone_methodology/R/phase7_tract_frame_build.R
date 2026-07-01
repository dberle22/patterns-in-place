build_phase7_tract_frame <- function(con, config) {
  metric_ids <- config$expected_kpis$metric_id
  source_year_cols <- c(
    "population_demographics_year",
    "migration_wide_year",
    "housing_core_wide_year",
    "social_infra_wide_year",
    "transport_built_form_wide_year",
    "transport_built_form_sld_year",
    "environment_ejs_year",
    "environment_fema_year",
    "economics_income_wide_year",
    "economics_labor_wide_year",
    "economics_lodes_wide_year"
  )

  # The governed Gold table is the Phase 7 source of truth for the tract KPI
  # surface. Sprint 2 intentionally reads that shared table rather than
  # re-implementing the wide join in R, then adds the tract metadata and policy
  # flags needed for labeling, benchmarks, and downstream review.
  tract_frame <- DBI::dbGetQuery(con, "
    with latest_policy as (
      select
        geo_id as tract_geoid,
        is_opportunity_zone,
        year,
        row_number() over (
          partition by geo_id
          order by year desc
        ) as rn
      from gold.dim_policy_designations
      where geo_level = 'tract'
    )
    select
      dim_geo.geo_name,
      dim_geo.cbsa_name,
      coalesce(dim_geo.county_name_long, dim_geo.county_name) as county_name,
      coalesce(latest_policy.is_opportunity_zone, false) as is_opportunity_zone,
      zone_inputs.*
    from gold.intelligence_zone_inputs as zone_inputs
    left join gold.dim_geo as dim_geo
      on dim_geo.geo_level = 'tract'
     and dim_geo.geo_id = zone_inputs.tract_geoid
    left join latest_policy
      on latest_policy.tract_geoid = zone_inputs.tract_geoid
     and latest_policy.rn = 1
    order by zone_inputs.tract_geoid
  ") |>
    dplyr::relocate(
      tract_geoid,
      cbsa_code,
      county_geoid,
      geo_name,
      cbsa_name,
      county_name,
      is_opportunity_zone
    ) |>
    dplyr::mutate(
      pct_unemployment_rate = dplyr::if_else(
        pct_unemployment_rate < 0,
        NA_real_,
        pct_unemployment_rate
      )
    )

  stopifnot(nrow(tract_frame) == dplyr::n_distinct(tract_frame$tract_geoid))

  coverage_audit <- config$expected_kpis |>
    dplyr::mutate(
      tract_count = nrow(tract_frame),
      non_null_tracts = purrr::map_int(metric_id, \(metric_id) sum(!is.na(tract_frame[[metric_id]]))),
      missing_tracts = tract_count - non_null_tracts,
      completeness_pct = non_null_tracts / tract_count,
      missing_gt_20_pct = completeness_pct < 0.80,
      median_value = purrr::map_dbl(metric_id, \(metric_id) median(tract_frame[[metric_id]], na.rm = TRUE))
    ) |>
    dplyr::arrange(completeness_pct, metric_id)

  tract_frame_selected <- tract_frame |>
    dplyr::select(
      tract_geoid,
      cbsa_code,
      county_geoid,
      geo_name,
      cbsa_name,
      county_name,
      is_opportunity_zone,
      dplyr::all_of(metric_ids),
      dplyr::all_of(source_year_cols)
    )

  list(
    tract_frame = tract_frame_selected,
    coverage_audit = coverage_audit
  )
}
