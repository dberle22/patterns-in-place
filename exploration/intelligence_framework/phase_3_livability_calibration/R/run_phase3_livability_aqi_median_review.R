library(here)

source(here("exploration/intelligence_framework/phase_3_livability_calibration/R/run_phase3_livability.R"))

run_phase3_livability_aqi_median_review <- function() {
  review_config <- phase3_livability_config(
    aqi_metric_id = "aqi_median",
    aqi_source_column = "aqi_median",
    output_dir_name = "outputs_aqi_median_review"
  )

  run_phase3_livability(config = review_config)
}

if (sys.nframe() == 0) {
  invisible(run_phase3_livability_aqi_median_review())
}
