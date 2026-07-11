phase5_cross_frame_config <- function(
  output_dir_name = "outputs",
  livability_score_path = NULL,
  livability_decision_path = NULL
) {
  phase_dir <- here::here(
    "exploration",
    "intelligence_framework",
    "phase_5_cross_frame_integration"
  )

  if (is.null(livability_score_path)) {
    livability_score_path <- here::here(
      "exploration",
      "intelligence_framework",
      "phase_3_livability_calibration",
      "outputs",
      "livability_scores.parquet"
    )
  }

  if (is.null(livability_decision_path)) {
    livability_decision_path <- here::here(
      "exploration",
      "intelligence_framework",
      "phase_3_livability_calibration",
      "outputs",
      "livability_phase3_clustering_metric_decisions.csv"
    )
  }

  output_dir <- file.path(phase_dir, output_dir_name)
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  list(
    phase_dir = phase_dir,
    output_dir = output_dir,
    output_dir_name = output_dir_name,
    target_year = 2024L,
    min_pop = 100000L,
    reference_spine_size = 396L,
    frames = tibble::tribble(
      ~frame_id, ~score_path, ~decision_path, ~frame_priority,
      "character",
      here::here(
        "exploration",
        "intelligence_framework",
        "phase_2_character_calibration",
        "outputs",
        "character_scores.parquet"
      ),
      here::here(
        "exploration",
        "intelligence_framework",
        "phase_2_character_calibration",
        "outputs",
        "character_phase2_clustering_metric_decisions.csv"
      ),
      3L,
      "livability",
      livability_score_path,
      livability_decision_path,
      2L,
      "opportunity",
      here::here(
        "exploration",
        "intelligence_framework",
        "phase_4_opportunity_calibration",
        "outputs",
        "opportunity_scores.parquet"
      ),
      here::here(
        "exploration",
        "intelligence_framework",
        "phase_4_opportunity_calibration",
        "outputs",
        "opportunity_phase4_clustering_metric_decisions.csv"
      ),
      1L
    ),
    correlation_flag_threshold = 0.75,
    correlation_drop_threshold = 0.85,
    target_cumulative_variance = 0.80,
    low_communality_threshold = 0.35,
    low_loading_threshold = 0.30,
    moderate_communality_threshold = 0.25,
    moderate_loading_threshold = 0.25,
    candidate_k = 3:10,
    selected_metric_set = "moderate_35_kpi_set",
    selected_metric_count = 35L,
    final_k = 7L
  )
}
