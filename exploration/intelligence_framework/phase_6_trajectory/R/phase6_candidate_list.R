phase6_build_phase5_overlap_rank <- function(overlap_flags) {
  overlap_flags |>
    dplyr::arrange(
      dplyr::desc(frame_percentile_gap),
      dplyr::desc(frame_percentile_sd),
      cbsa_name
    ) |>
    dplyr::mutate(
      phase5_overlap_rank = dplyr::row_number(),
      phase5_overlap_pct = phase6_rank_pct(frame_percentile_gap)
    )
}

phase6_build_candidate_list <- function(config, trajectory_scores) {
  phase5_overlap <- readr::read_csv(
    config$phase5_overlap_flags_path,
    show_col_types = FALSE
  ) |>
    dplyr::mutate(
      cbsa_code = as.character(cbsa_code)
    ) |>
    phase6_build_phase5_overlap_rank()

  trajectory_scores |>
    dplyr::left_join(
      phase5_overlap |>
        dplyr::select(
          cbsa_code,
          overlap_profile,
          half_alignment,
          signature,
          frame_percentile_gap,
          frame_percentile_sd,
          phase5_overlap_rank,
          phase5_overlap_pct
        ),
      by = "cbsa_code"
    ) |>
    dplyr::mutate(
      overall_trajectory_strength = purrr::pmap_dbl(
        list(
          character_trajectory_strength,
          livability_trajectory_strength,
          opportunity_trajectory_strength
        ),
        \(character_strength, livability_strength, opportunity_strength) {
          phase6_mean_or_na(c(character_strength, livability_strength, opportunity_strength))
        }
      ),
      overall_trajectory_strength_pct = phase6_rank_pct(overall_trajectory_strength),
      pattern_signal_score =
        20 * as.integer(is_bounce_back) +
        20 * as.integer(is_hidden_livability_winner) +
        20 * as.integer(is_diverging_from_themselves) +
        20 * as.integer(is_fast_demographic_changer) +
        20 * as.integer(is_environmental_risk_outlier),
      candidate_score =
        pattern_signal_score * (0.5 + overall_trajectory_strength_pct) +
        15 * dplyr::coalesce(phase5_overlap_pct, 0),
      candidate_score_method = "recommended_default_equal_pattern_weights_times_trajectory_strength_plus_smaller_phase5_overlap_bonus",
      candidate_score_sensitivity_note = paste(
        "Equal pattern weights keep the list balanced across the five trajectory narratives.",
        "Increasing one pattern weight will make that narrative dominate the top ranks.",
        "Reducing the overlap bonus will downweight metros that were already unusual in Phase 5, while increasing it will favor cross-frame contradiction over pure trajectory movement."
      )
    ) |>
    dplyr::arrange(
      dplyr::desc(candidate_score),
      dplyr::desc(pattern_signal_score),
      dplyr::desc(overall_trajectory_strength),
      cbsa_name
    ) |>
    dplyr::mutate(candidate_rank = dplyr::row_number()) |>
    dplyr::select(
      cbsa_code,
      cbsa_name,
      census_division,
      character_trajectory_score,
      character_direction,
      livability_trajectory_score,
      livability_direction,
      opportunity_trajectory_score,
      opportunity_direction,
      opp_turn_signal,
      opp_turn_signal_type,
      overlap_profile,
      half_alignment,
      signature,
      frame_percentile_gap,
      frame_percentile_sd,
      phase5_overlap_rank,
      is_bounce_back,
      is_hidden_livability_winner,
      is_diverging_from_themselves,
      is_fast_demographic_changer,
      is_environmental_risk_outlier,
      pattern_count,
      pattern_signal_score,
      overall_trajectory_strength,
      overall_trajectory_strength_pct,
      cross_frame_percentile,
      candidate_score,
      candidate_rank,
      candidate_score_method,
      candidate_score_sensitivity_note,
      ct_exclusion_flag,
      zori_coverage_flag
    )
}

cli::cli_h1("Phase 6 Candidate Ranking")

phase6_candidate_list <- phase6_build_candidate_list(
  config = phase6_config,
  trajectory_scores = phase6_trajectory_core_bundle$trajectory_scores
)

readr::write_csv(
  phase6_candidate_list,
  phase6_config$candidate_list_path
)

phase6_trajectory_core_bundle$trajectory_scores <- phase6_trajectory_core_bundle$trajectory_scores |>
  dplyr::left_join(
    phase6_candidate_list |>
      dplyr::select(cbsa_code, phase5_overlap_rank, candidate_score, candidate_rank),
    by = "cbsa_code"
  )

arrow::write_parquet(
  phase6_trajectory_core_bundle$trajectory_scores,
  phase6_config$trajectory_scores_path
)

cli::cli_alert_info(
  "Top candidate now ranks {.val {phase6_candidate_list$cbsa_name[[1]]}} at score {.val {round(phase6_candidate_list$candidate_score[[1]], 1)}}."
)
cli::cli_alert_success(
  "Phase 6 candidate list output is complete."
)
