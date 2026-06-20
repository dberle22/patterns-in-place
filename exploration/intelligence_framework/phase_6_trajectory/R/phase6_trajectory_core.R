phase6_safe_zscore <- function(x) {
  x_sd <- stats::sd(x, na.rm = TRUE)

  if (is.na(x_sd) || x_sd == 0) {
    return(rep(0, length(x)))
  }

  as.numeric((x - mean(x, na.rm = TRUE)) / x_sd)
}

phase6_mean_or_na <- function(x) {
  if (all(is.na(x))) {
    return(NA_real_)
  }

  mean(x, na.rm = TRUE)
}

phase6_classify_direction <- function(position_z, momentum_z) {
  dplyr::case_when(
    is.na(position_z) | is.na(momentum_z) ~ NA_character_,
    position_z >= 0 & momentum_z >= 0 ~ "diverging-improving",
    position_z < 0 & momentum_z < 0 ~ "diverging-declining",
    position_z < 0 & momentum_z >= 0 ~ "converging-improving",
    TRUE ~ "converging-declining"
  )
}

phase6_window_vector <- function(trajectory_window) {
  if (identical(trajectory_window, "1yr_and_5yr")) {
    return(c(1L, 5L))
  }

  if (identical(trajectory_window, "5yr")) {
    return(5L)
  }

  if (identical(trajectory_window, "1yr")) {
    return(1L)
  }

  integer()
}

phase6_window_table <- function(metric_df) {
  metric_df |>
    dplyr::distinct(
      cbsa_code,
      cbsa_name,
      census_division,
      pop_total,
      spine_year,
      frame_id,
      metric_id,
      trajectory_window,
      polarity,
      polarity_multiplier,
      ct_exclusion_flag,
      zori_coverage_flag
    ) |>
    dplyr::mutate(
      window_years = purrr::map(trajectory_window, phase6_window_vector)
    ) |>
    tidyr::unnest(window_years)
}

phase6_build_polarity_map <- function(config) {
  intelligence_text <- readr::read_file(
    here::here("foundations/semantic_layer/intelligence_catalog.yml")
  )

  yaml::yaml.load(intelligence_text)$frames |>
    purrr::keep(\(frame) frame$frame_id %in% unique(config$trajectory_metrics$frame_id)) |>
    purrr::map_dfr(\(frame) {
      purrr::map_dfr(frame$subjects, \(subject) {
        purrr::map_dfr(subject$topics, \(topic) {
          purrr::map_dfr(topic$kpis, \(kpi) {
            tibble::tibble(
              frame_id = frame$frame_id,
              metric_id = kpi$metric_id,
              polarity = kpi$polarity %fallback% NA_character_
            )
          })
        })
      })
    }) |>
    dplyr::semi_join(
      config$trajectory_metrics |>
        dplyr::select(frame_id, metric_id) |>
        dplyr::distinct(),
      by = c("frame_id", "metric_id")
    ) |>
    dplyr::mutate(
      polarity_multiplier = dplyr::case_when(
        polarity == "positive" ~ 1,
        polarity == "negative" ~ -1,
        TRUE ~ NA_real_
      )
    ) |>
    dplyr::arrange(frame_id, metric_id)
}

phase6_load_frame_score_context <- function(config) {
  purrr::pmap_dfr(
    config$frame_output_paths,
    \(frame_id, score_path, percentile_column, score_column) {
      score_name <- paste0(frame_id, "_current_score")
      percentile_name <- paste0(frame_id, "_current_percentile")
      cluster_name <- paste0(frame_id, "_current_cluster_name")

      score_df <- arrow::read_parquet(score_path) |>
        tibble::as_tibble() |>
        dplyr::select(
          cbsa_code,
          cbsa_name,
          !!rlang::sym(score_column),
          !!rlang::sym(percentile_column),
          dplyr::any_of(c(
            paste0(frame_id, "_cluster_name"),
            paste0(frame_id, "_cluster_label")
          ))
        )

      cluster_col <- setdiff(names(score_df), c("cbsa_code", "cbsa_name", score_column, percentile_column))

      score_df |>
        dplyr::transmute(
          cbsa_code,
          cbsa_name,
          !!score_name := .data[[score_column]],
          !!percentile_name := .data[[percentile_column]],
          !!cluster_name := if (length(cluster_col) == 0) NA_character_ else .data[[cluster_col[[1]]]]
        )
    }
  ) |>
    dplyr::group_by(cbsa_code, cbsa_name) |>
    dplyr::summarise(dplyr::across(dplyr::everything(), dplyr::first), .groups = "drop")
}

phase6_load_cross_frame_context <- function(config) {
  arrow::read_parquet(config$phase5_scores_path) |>
    tibble::as_tibble() |>
    dplyr::transmute(
      cbsa_code,
      cbsa_name,
      cross_frame_score,
      cross_frame_percentile,
      cross_frame_cluster_name,
      hybrid_membership_gap,
      distance_to_center
    )
}

phase6_build_trajectory_core_bundle <- function(config, frame_build_bundle) {
  polarity_map <- phase6_build_polarity_map(config)
  stopifnot(!any(is.na(polarity_map$polarity_multiplier)))

  metric_history <- frame_build_bundle$metric_series_long |>
    dplyr::filter(trajectory_role == "trajectory") |>
    dplyr::left_join(polarity_map, by = c("frame_id", "metric_id"))

  metric_windows <- phase6_window_table(metric_history)

  non_missing_history <- metric_history |>
    dplyr::filter(!is.na(metric_value), !is.na(year))

  current_values <- non_missing_history |>
    dplyr::group_by(
      cbsa_code,
      cbsa_name,
      census_division,
      pop_total,
      spine_year,
      frame_id,
      metric_id,
      polarity,
      polarity_multiplier
    ) |>
    dplyr::arrange(year, .by_group = TRUE) |>
    dplyr::summarise(
      current_year = max(year),
      current_value = dplyr::last(metric_value),
      available_year_count = dplyr::n(),
      .groups = "drop"
    ) |>
    dplyr::right_join(
      metric_windows,
      by = c(
        "cbsa_code",
        "cbsa_name",
        "census_division",
        "pop_total",
        "spine_year",
        "frame_id",
        "metric_id",
        "polarity",
        "polarity_multiplier"
      )
    ) |>
    dplyr::mutate(
      lag_year = current_year - window_years
    )

  lag_values <- non_missing_history |>
    dplyr::select(
      cbsa_code,
      frame_id,
      metric_id,
      year,
      metric_value
    ) |>
    dplyr::rename(
      lag_year = year,
      lag_value = metric_value
    )

  kpi_trajectory_long <- current_values |>
    dplyr::left_join(
      lag_values,
      by = c("cbsa_code", "frame_id", "metric_id", "lag_year")
    ) |>
    dplyr::mutate(
      change_raw = current_value - lag_value,
      available_year_count = dplyr::coalesce(available_year_count, 0L)
    ) |>
    dplyr::group_by(frame_id, metric_id, window_years) |>
    dplyr::mutate(
      position_z = phase6_safe_zscore(current_value),
      change_z = phase6_safe_zscore(change_raw),
      aligned_position_z = polarity_multiplier * position_z,
      aligned_change_z = polarity_multiplier * change_z,
      metric_trajectory_strength = 0.5 * abs(aligned_position_z) + 0.5 * abs(aligned_change_z),
      metric_trajectory_score = 0.5 * aligned_position_z + 0.5 * aligned_change_z,
      metric_direction = phase6_classify_direction(aligned_position_z, aligned_change_z)
    ) |>
    dplyr::ungroup() |>
    dplyr::arrange(frame_id, metric_id, cbsa_code, window_years)

  frame_window_summary <- kpi_trajectory_long |>
    dplyr::group_by(
      cbsa_code,
      cbsa_name,
      census_division,
      pop_total,
      spine_year,
      frame_id,
      window_years
    ) |>
    dplyr::summarise(
      metrics_included = sum(!is.na(change_raw)),
      frame_position_z = phase6_mean_or_na(aligned_position_z),
      frame_momentum_z = phase6_mean_or_na(aligned_change_z),
      frame_trajectory_strength = phase6_mean_or_na(metric_trajectory_strength),
      frame_trajectory_score = 0.5 * frame_position_z + 0.5 * frame_momentum_z,
      frame_direction = phase6_classify_direction(frame_position_z, frame_momentum_z),
      ct_exclusion_flag = any(ct_exclusion_flag),
      zori_coverage_flag = any(zori_coverage_flag),
      .groups = "drop"
    ) |>
    dplyr::arrange(frame_id, window_years, cbsa_code)

  frame_window_wide <- frame_window_summary |>
    dplyr::mutate(
      frame_window_key = paste0(frame_id, "_", window_years, "yr")
    ) |>
    dplyr::select(
      cbsa_code,
      cbsa_name,
      census_division,
      pop_total,
      spine_year,
      frame_window_key,
      metrics_included,
      frame_position_z,
      frame_momentum_z,
      frame_trajectory_strength,
      frame_trajectory_score,
      frame_direction,
      ct_exclusion_flag,
      zori_coverage_flag
    ) |>
    tidyr::pivot_wider(
      names_from = frame_window_key,
      values_from = c(
        metrics_included,
        frame_position_z,
        frame_momentum_z,
        frame_trajectory_strength,
        frame_trajectory_score,
        frame_direction,
        ct_exclusion_flag,
        zori_coverage_flag
      )
    )

  trajectory_scores <- frame_build_bundle$spine |>
    dplyr::left_join(frame_window_wide, by = c("cbsa_code", "cbsa_name", "census_division", "pop_total", "spine_year")) |>
    dplyr::left_join(phase6_load_frame_score_context(config), by = c("cbsa_code", "cbsa_name")) |>
    dplyr::left_join(phase6_load_cross_frame_context(config), by = c("cbsa_code", "cbsa_name")) |>
    dplyr::transmute(
      cbsa_code,
      cbsa_name,
      census_division,
      pop_total,
      spine_year,
      character_trajectory_score = frame_trajectory_score_character_5yr,
      character_trajectory_strength = frame_trajectory_strength_character_5yr,
      character_direction = frame_direction_character_5yr,
      livability_trajectory_score = frame_trajectory_score_livability_5yr,
      livability_trajectory_strength = frame_trajectory_strength_livability_5yr,
      livability_direction = frame_direction_livability_5yr,
      opportunity_trajectory_score = frame_trajectory_score_opportunity_5yr,
      opportunity_trajectory_strength = frame_trajectory_strength_opportunity_5yr,
      opportunity_direction = frame_direction_opportunity_5yr,
      opportunity_trajectory_score_1yr = frame_trajectory_score_opportunity_1yr,
      opportunity_trajectory_strength_1yr = frame_trajectory_strength_opportunity_1yr,
      opportunity_direction_1yr = frame_direction_opportunity_1yr,
      character_current_score,
      character_current_percentile,
      character_current_cluster_name,
      livability_current_score,
      livability_current_percentile,
      livability_current_cluster_name,
      opportunity_current_score,
      opportunity_current_percentile,
      opportunity_current_cluster_name,
      cross_frame_score,
      cross_frame_percentile,
      cross_frame_cluster_name,
      hybrid_membership_gap,
      distance_to_center,
      ct_exclusion_flag =
        dplyr::coalesce(ct_exclusion_flag_character_5yr, FALSE) |
        dplyr::coalesce(ct_exclusion_flag_livability_5yr, FALSE) |
        dplyr::coalesce(ct_exclusion_flag_opportunity_5yr, FALSE),
      zori_coverage_flag =
        dplyr::coalesce(zori_coverage_flag_opportunity_1yr, FALSE) |
        dplyr::coalesce(zori_coverage_flag_opportunity_5yr, FALSE)
    ) |>
    dplyr::arrange(dplyr::desc(pop_total), cbsa_name)

  list(
    polarity_map = polarity_map,
    kpi_trajectory_long = kpi_trajectory_long,
    frame_window_summary = frame_window_summary,
    trajectory_scores = trajectory_scores
  )
}

cli::cli_h1("Phase 6 Trajectory Core")

phase6_trajectory_core_bundle <- phase6_build_trajectory_core_bundle(
  config = phase6_config,
  frame_build_bundle = phase6_frame_build_bundle
)

arrow::write_parquet(
  phase6_trajectory_core_bundle$trajectory_scores,
  phase6_config$trajectory_scores_path
)

readr::write_csv(
  phase6_trajectory_core_bundle$kpi_trajectory_long,
  phase6_config$kpi_trajectory_long_path
)

cli::cli_alert_info(
  "Built {.val {nrow(phase6_trajectory_core_bundle$kpi_trajectory_long)}} CBSA-metric-window trajectory rows."
)
cli::cli_alert_info(
  "Wrote {.val {nrow(phase6_trajectory_core_bundle$trajectory_scores)}} CBSA trajectory score rows to {.file {phase6_config$trajectory_scores_path}}."
)
cli::cli_alert_info(
  "Character 5-year rows: {.val {sum(phase6_trajectory_core_bundle$kpi_trajectory_long$frame_id == 'character' & phase6_trajectory_core_bundle$kpi_trajectory_long$window_years == 5)}}. Livability 5-year rows: {.val {sum(phase6_trajectory_core_bundle$kpi_trajectory_long$frame_id == 'livability' & phase6_trajectory_core_bundle$kpi_trajectory_long$window_years == 5)}}. Opportunity rows across both windows: {.val {sum(phase6_trajectory_core_bundle$kpi_trajectory_long$frame_id == 'opportunity')}}."
)
cli::cli_alert_success(
  "Phase 6 trajectory core outputs are ready for the Opportunity turn-signal pass."
)
