library(here)

source(here("exploration/intelligence_framework/phase_5_cross_frame_integration/R/run_phase5_cross_frame.R"))

run_phase5_cross_frame_aqi_median_review <- function() {
  review_config <- phase5_cross_frame_config(
    output_dir_name = "outputs_aqi_median_review",
    livability_score_path = here::here(
      "exploration",
      "intelligence_framework",
      "phase_3_livability_calibration",
      "outputs_aqi_median_review",
      "livability_scores.parquet"
    ),
    livability_decision_path = here::here(
      "exploration",
      "intelligence_framework",
      "phase_3_livability_calibration",
      "outputs_aqi_median_review",
      "livability_phase3_clustering_metric_decisions.csv"
    )
  )

  run_phase5_cross_frame(config = review_config)
}

if (sys.nframe() == 0) {
  invisible(run_phase5_cross_frame_aqi_median_review())
}
