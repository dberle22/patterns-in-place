phase6_rank_pct <- function(x) {
  dplyr::percent_rank(dplyr::coalesce(x, -Inf))
}

phase6_extract_metric_window <- function(kpi_trajectory_long, metric_id, window_years) {
  kpi_trajectory_long |>
    dplyr::filter(metric_id == !!metric_id, window_years == !!window_years) |>
    dplyr::select(
      cbsa_code,
      cbsa_name,
      metric_id,
      window_years,
      aligned_position_z,
      aligned_change_z,
      metric_trajectory_strength,
      metric_trajectory_score,
      metric_direction
    )
}

phase6_top_examples <- function(df, score_col, n = 10) {
  if (nrow(df) == 0) {
    return(NA_character_)
  }

  df |>
    dplyr::arrange(dplyr::desc(.data[[score_col]]), cbsa_name) |>
    dplyr::slice_head(n = n) |>
    dplyr::pull(cbsa_name) |>
    paste(collapse = " | ")
}

phase6_build_patterns_bundle <- function(config, core_bundle, opportunity_turn_signals) {
  trajectory_disagreement_sd <- core_bundle$trajectory_scores |>
    dplyr::select(
      character_trajectory_score,
      livability_trajectory_score,
      opportunity_trajectory_score
    ) |>
    as.matrix() |>
    apply(1, stats::sd, na.rm = TRUE)

  trajectory_scores <- core_bundle$trajectory_scores |>
    dplyr::mutate(
      character_strength_pct = phase6_rank_pct(character_trajectory_strength),
      livability_strength_pct = phase6_rank_pct(livability_trajectory_strength),
      opportunity_strength_pct = phase6_rank_pct(opportunity_trajectory_strength),
      opportunity_1yr_strength_pct = phase6_rank_pct(opportunity_trajectory_strength_1yr),
      trajectory_disagreement_sd = trajectory_disagreement_sd,
      trajectory_disagreement_pct = phase6_rank_pct(trajectory_disagreement_sd),
      improving_frame_count =
        as.integer(grepl("improving", character_direction)) +
        as.integer(grepl("improving", livability_direction)) +
        as.integer(grepl("improving", opportunity_direction)),
      declining_frame_count =
        as.integer(grepl("declining", character_direction)) +
        as.integer(grepl("declining", livability_direction)) +
        as.integer(grepl("declining", opportunity_direction))
    )

  environmental_metrics <- core_bundle$kpi_trajectory_long |>
    dplyr::filter(
      frame_id == "livability",
      metric_id %in% c("aqi_median", "fema_risk_score"),
      window_years == 5
    ) |>
    dplyr::mutate(
      worsening_magnitude = dplyr::if_else(
        is.na(aligned_change_z),
        NA_real_,
        -aligned_change_z
      )
    ) |>
    dplyr::group_by(metric_id) |>
    dplyr::mutate(
      worsening_rank_pct = phase6_rank_pct(worsening_magnitude)
    ) |>
    dplyr::ungroup() |>
    dplyr::select(cbsa_code, metric_id, worsening_magnitude, worsening_rank_pct) |>
    tidyr::pivot_wider(
      names_from = metric_id,
      values_from = c(worsening_magnitude, worsening_rank_pct)
    )

  pattern_flags <- trajectory_scores |>
    dplyr::left_join(environmental_metrics, by = "cbsa_code") |>
    dplyr::mutate(
      is_bounce_back =
        opportunity_direction == "converging-improving" &
        opportunity_strength_pct >= 0.9 &
        opportunity_current_percentile <= 50,
      is_hidden_livability_winner =
        livability_direction == "diverging-improving" &
        livability_strength_pct >= 0.9 &
        dplyr::between(cross_frame_percentile, 35, 70),
      is_diverging_from_themselves =
        improving_frame_count >= 1 &
        declining_frame_count >= 1 &
        trajectory_disagreement_pct >= 0.9,
      is_fast_demographic_changer =
        character_strength_pct >= 0.9,
      is_environmental_risk_outlier =
        livability_direction == "diverging-declining" &
        worsening_rank_pct_aqi_median >= 0.9 &
        worsening_rank_pct_fema_risk_score >= 0.9
    ) |>
    dplyr::mutate(
      pattern_count = rowSums(
        dplyr::pick(dplyr::all_of(config$pattern_flag_columns)),
        na.rm = TRUE
      ),
      pattern_threshold_method = "recommended_default_top_decile_national_rank",
      pattern_sensitivity_note = paste(
        "Tightening the cutoff above the 90th percentile will surface fewer metros and push the outputs toward the most extreme outliers.",
        "Loosening it below the 90th percentile will broaden pattern membership and make the candidate list less selective."
      )
    )

  pattern_specs <- tibble::tribble(
    ~pattern_flag, ~pattern_label, ~sort_score_col,
    "is_bounce_back", "Bounce Back", "opportunity_trajectory_strength",
    "is_hidden_livability_winner", "Hidden Livability Winners", "livability_trajectory_strength",
    "is_diverging_from_themselves", "Diverging From Themselves", "trajectory_disagreement_sd",
    "is_fast_demographic_changer", "Fast Demographic Changers", "character_trajectory_strength",
    "is_environmental_risk_outlier", "Environmental Risk Outliers", "worsening_magnitude_fema_risk_score"
  )

  pattern_summary <- purrr::pmap_dfr(
    pattern_specs,
    \(pattern_flag, pattern_label, sort_score_col) {
      matches <- pattern_flags |>
        dplyr::filter(.data[[pattern_flag]])

      tibble::tibble(
        pattern_flag = pattern_flag,
        pattern_label = pattern_label,
        cbsa_count = nrow(matches),
        top_10_examples = phase6_top_examples(matches, score_col = sort_score_col),
        threshold_method = "recommended_default_top_decile_national_rank",
        sensitivity_note = paste(
          "Changing the top-decile default changes both membership count and rank stability.",
          "A stricter cutoff produces fewer but more extreme metros; a looser cutoff produces broader review surfaces."
        )
      )
    }
  )

  list(
    pattern_flags = pattern_flags,
    pattern_summary = pattern_summary
  )
}

cli::cli_h1("Phase 6 Pattern Scan")

phase6_patterns_bundle <- phase6_build_patterns_bundle(
  config = phase6_config,
  core_bundle = phase6_trajectory_core_bundle,
  opportunity_turn_signals = phase6_opportunity_turn_signals
)

readr::write_csv(
  phase6_patterns_bundle$pattern_summary,
  phase6_config$pattern_summary_path
)

phase6_trajectory_core_bundle$trajectory_scores <- phase6_patterns_bundle$pattern_flags

arrow::write_parquet(
  phase6_trajectory_core_bundle$trajectory_scores,
  phase6_config$trajectory_scores_path
)

cli::cli_alert_info(
  "Pattern counts: bounce-back {.val {sum(phase6_patterns_bundle$pattern_flags$is_bounce_back, na.rm = TRUE)}}, hidden winners {.val {sum(phase6_patterns_bundle$pattern_flags$is_hidden_livability_winner, na.rm = TRUE)}}, diverging {.val {sum(phase6_patterns_bundle$pattern_flags$is_diverging_from_themselves, na.rm = TRUE)}}, demographic changers {.val {sum(phase6_patterns_bundle$pattern_flags$is_fast_demographic_changer, na.rm = TRUE)}}, environmental outliers {.val {sum(phase6_patterns_bundle$pattern_flags$is_environmental_risk_outlier, na.rm = TRUE)}}."
)
cli::cli_alert_success(
  "Phase 6 pattern summary output is ready for candidate ranking."
)
