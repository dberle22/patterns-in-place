phase6_build_opportunity_turn_signals <- function(core_bundle) {
  core_bundle$frame_window_summary |>
    dplyr::filter(frame_id == "opportunity", window_years %in% c(1L, 5L)) |>
    dplyr::select(
      cbsa_code,
      cbsa_name,
      census_division,
      window_years,
      frame_momentum_z,
      frame_trajectory_score,
      frame_trajectory_strength,
      frame_direction,
      metrics_included
    ) |>
    dplyr::mutate(window_label = paste0("window_", window_years, "yr")) |>
    dplyr::select(-window_years) |>
    tidyr::pivot_wider(
      names_from = window_label,
      values_from = c(
        frame_momentum_z,
        frame_trajectory_score,
        frame_trajectory_strength,
        frame_direction,
        metrics_included
      )
    ) |>
    dplyr::mutate(
      opp_turn_signal = dplyr::case_when(
        is.na(frame_momentum_z_window_1yr) | is.na(frame_momentum_z_window_5yr) ~ NA,
        frame_momentum_z_window_1yr > 0 & frame_momentum_z_window_5yr < 0 ~ TRUE,
        frame_momentum_z_window_1yr < 0 & frame_momentum_z_window_5yr > 0 ~ TRUE,
        TRUE ~ FALSE
      ),
      opp_turn_signal_type = dplyr::case_when(
        is.na(opp_turn_signal) ~ NA_character_,
        frame_momentum_z_window_1yr > 0 & frame_momentum_z_window_5yr < 0 ~ "short_run_improving_vs_medium_term_declining",
        frame_momentum_z_window_1yr < 0 & frame_momentum_z_window_5yr > 0 ~ "short_run_declining_vs_medium_term_improving",
        TRUE ~ "aligned"
      )
    ) |>
    dplyr::arrange(
      dplyr::desc(opp_turn_signal),
      dplyr::desc(abs(frame_momentum_z_window_1yr - frame_momentum_z_window_5yr)),
      cbsa_name
    )
}

cli::cli_h1("Phase 6 Opportunity Turn Signals")

phase6_opportunity_turn_signals <- phase6_build_opportunity_turn_signals(
  phase6_trajectory_core_bundle
)

readr::write_csv(
  phase6_opportunity_turn_signals,
  phase6_config$opp_turn_signals_path
)

phase6_trajectory_core_bundle$trajectory_scores <- phase6_trajectory_core_bundle$trajectory_scores |>
  dplyr::left_join(
    phase6_opportunity_turn_signals |>
      dplyr::select(cbsa_code, opp_turn_signal, opp_turn_signal_type),
    by = "cbsa_code"
  )

arrow::write_parquet(
  phase6_trajectory_core_bundle$trajectory_scores,
  phase6_config$trajectory_scores_path
)

cli::cli_alert_info(
  "Flagged {.val {sum(phase6_opportunity_turn_signals$opp_turn_signal %in% TRUE, na.rm = TRUE)}} Opportunity turn-signal metros."
)
cli::cli_alert_success(
  "Opportunity turn-signal output is ready for pattern and candidate enrichment."
)
