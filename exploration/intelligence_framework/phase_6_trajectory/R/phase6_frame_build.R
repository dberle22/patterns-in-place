`%fallback%` <- function(x, y) {
  if (is.null(x)) y else x
}

phase6_has_year_column <- function(con, source_table) {
  sql <- sprintf(
    "select count(*) as n
     from information_schema.columns
     where table_schema = 'gold'
       and table_name = '%s'
       and column_name = 'year'",
    source_table
  )

  DBI::dbGetQuery(con, sql)$n[[1]] > 0
}

phase6_pull_metric_series <- function(
  con,
  metric_id,
  source_table,
  source_column,
  frame_id,
  trajectory_window,
  trajectory_role,
  coverage_rule,
  ct_cbsa_codes
) {
  has_year_column <- phase6_has_year_column(con, source_table)

  if (trajectory_role == "trajectory" && !has_year_column) {
    stop(sprintf(
      "Phase 6 trajectory metric '%s' from gold.%s is missing a year column.",
      metric_id,
      source_table
    ))
  }

  if (has_year_column) {
    sql <- sprintf(
      "select
         geo_id as cbsa_code,
         year,
         cast(%s as double) as metric_value
       from gold.%s
       where geo_level = 'cbsa'",
      source_column,
      source_table
    )
  } else {
    sql <- sprintf(
      "select
         geo_id as cbsa_code,
         cast(null as integer) as year,
         cast(%s as double) as metric_value
       from gold.%s
       where geo_level = 'cbsa'",
      source_column,
      source_table
    )
  }

  DBI::dbGetQuery(con, sql) |>
    dplyr::mutate(
      metric_id = metric_id,
      frame_id = frame_id,
      source_table = source_table,
      source_column = source_column,
      trajectory_window = trajectory_window,
      trajectory_role = trajectory_role,
      coverage_rule = coverage_rule,
      ct_exclusion_flag = coverage_rule == "exclude_all_ct_for_acs_5yr" &
        cbsa_code %in% ct_cbsa_codes,
      zori_coverage_flag = coverage_rule == "annotate_zori_coverage" &
        is.na(metric_value),
      metric_value = dplyr::if_else(
        ct_exclusion_flag,
        NA_real_,
        metric_value
      )
    ) |>
    dplyr::select(
      cbsa_code,
      year,
      frame_id,
      metric_id,
      metric_value,
      source_table,
      source_column,
      trajectory_window,
      trajectory_role,
      coverage_rule,
      ct_exclusion_flag,
      zori_coverage_flag
    )
}

phase6_build_metric_catalog <- function(config) {
  metric_catalog_text <- readr::read_file(
    here::here("foundations/semantic_layer/metric_catalog.yml")
  )

  yaml::yaml.load(metric_catalog_text)$metrics |>
    purrr::map_dfr(\(metric) tibble::tibble(
      metric_id = metric$metric_id,
      source_table = metric$source_table %fallback% NA_character_,
      source_column = metric$source_column %fallback% NA_character_,
      status = metric$status %fallback% NA_character_
    )) |>
    dplyr::right_join(config$frame_metric_spec, by = "metric_id") |>
    dplyr::mutate(
      in_metric_catalog = !is.na(source_table),
      source_column_matches = is.na(source_column) | source_column == expected_source_column
    ) |>
    dplyr::select(
      frame_id,
      metric_id,
      expected_source_column,
      source_table,
      source_column,
      status,
      trajectory_window,
      trajectory_role,
      coverage_rule,
      in_metric_catalog,
      source_column_matches
    ) |>
    dplyr::arrange(frame_id, trajectory_role, metric_id)
}

phase6_build_cbsa_spine <- function(con, config) {
  DBI::dbGetQuery(
    con,
    sprintf(
      "select
         pop.geo_id as cbsa_code,
         pop.geo_name as cbsa_name,
         pop.pop_total,
         pop.year as spine_year,
         geo.division_name as census_division
       from gold.population_demographics pop
       left join gold.dim_geo geo
         on pop.geo_id = geo.geo_id
        and geo.geo_level = 'cbsa'
       where pop.geo_level = 'cbsa'
         and pop.year = %d
         and pop.pop_total >= %d
         and pop.geo_name not like '%%, PR'
       order by pop.pop_total desc",
      config$target_year,
      config$min_pop
    )
  )
}

phase6_build_frame_series <- function(con, config, catalog_check, spine) {
  ct_cbsa_codes <- config$ct_cbsa_exclusion$cbsa_code

  metric_series_long <- purrr::pmap_dfr(
    catalog_check |>
      dplyr::filter(in_metric_catalog, source_column_matches) |>
      dplyr::select(
        metric_id,
        source_table,
        expected_source_column,
        frame_id,
        trajectory_window,
        trajectory_role,
        coverage_rule
      ),
    \(metric_id, source_table, expected_source_column, frame_id, trajectory_window, trajectory_role, coverage_rule) {
      phase6_pull_metric_series(
        con = con,
        metric_id = metric_id,
        source_table = source_table,
        source_column = expected_source_column,
        frame_id = frame_id,
        trajectory_window = trajectory_window,
        trajectory_role = trajectory_role,
        coverage_rule = coverage_rule,
        ct_cbsa_codes = ct_cbsa_codes
      )
    }
  ) |>
    dplyr::inner_join(
      spine |>
        dplyr::select(cbsa_code, cbsa_name, census_division, pop_total, spine_year),
      by = "cbsa_code"
    ) |>
    dplyr::arrange(frame_id, metric_id, cbsa_code, year)

  coverage_summary <- metric_series_long |>
    dplyr::group_by(frame_id, metric_id, trajectory_role, trajectory_window, coverage_rule) |>
    dplyr::summarise(
      min_year = suppressWarnings(min(year, na.rm = TRUE)),
      max_year = suppressWarnings(max(year, na.rm = TRUE)),
      n_rows = dplyr::n(),
      n_cbsa = dplyr::n_distinct(cbsa_code),
      n_non_missing = sum(!is.na(metric_value)),
      n_missing = sum(is.na(metric_value)),
      n_ct_excluded = sum(ct_exclusion_flag),
      n_zori_flagged = sum(zori_coverage_flag),
      .groups = "drop"
    ) |>
    dplyr::mutate(
      min_year = dplyr::if_else(is.infinite(min_year), NA_integer_, as.integer(min_year)),
      max_year = dplyr::if_else(is.infinite(max_year), NA_integer_, as.integer(max_year))
    ) |>
    dplyr::arrange(frame_id, trajectory_role, metric_id)

  list(
    metric_series_long = metric_series_long,
    coverage_summary = coverage_summary
  )
}

if (!exists("phase6_config")) {
  phase6_config <- phase6_trajectory_config()
}

cli::cli_h1("Phase 6 Frame Build")

phase6_catalog_check <- phase6_build_metric_catalog(phase6_config)

stopifnot(all(phase6_catalog_check$in_metric_catalog))
stopifnot(all(phase6_catalog_check$source_column_matches))

phase6_catalog_check <- phase6_catalog_check |>
  dplyr::mutate(
    has_year_column = purrr::map_lgl(source_table, \(source_table) {
      phase6_has_year_column(con, source_table)
    }),
    annual_series_ready = trajectory_role == "context_only" | has_year_column
  )

stopifnot(all(phase6_catalog_check$annual_series_ready))

phase6_cbsa_spine <- phase6_build_cbsa_spine(con, phase6_config)
stopifnot(nrow(phase6_cbsa_spine) == phase6_config$reference_spine_size)

phase6_frame_build <- phase6_build_frame_series(
  con = con,
  config = phase6_config,
  catalog_check = phase6_catalog_check,
  spine = phase6_cbsa_spine
)

phase6_frame_build_bundle <- list(
  catalog_check = phase6_catalog_check,
  spine = phase6_cbsa_spine,
  metric_series_long = phase6_frame_build$metric_series_long,
  coverage_summary = phase6_frame_build$coverage_summary
)

cli::cli_alert_info(
  "Built {.val {nrow(phase6_frame_build_bundle$metric_series_long)}} long metric-year rows across {.val {nrow(phase6_catalog_check)}} Phase 6 metrics."
)
cli::cli_alert_info(
  "Coverage summary spans {.val {nrow(phase6_frame_build_bundle$coverage_summary)}} metric specifications across the {.val {nrow(phase6_cbsa_spine)}}-CBSA modeling universe."
)
cli::cli_alert_info(
  "Connecticut exclusion rows tagged: {.val {sum(phase6_frame_build_bundle$metric_series_long$ct_exclusion_flag)}}. ZORI coverage flags tagged: {.val {sum(phase6_frame_build_bundle$metric_series_long$zori_coverage_flag)}}."
)
cli::cli_alert_success(
  "Phase 6 frame build bundle is ready for trajectory scoring."
)
