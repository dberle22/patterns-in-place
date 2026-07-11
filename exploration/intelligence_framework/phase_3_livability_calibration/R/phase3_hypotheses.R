build_phase3_hypothesis_bundle <- function(livability_scores, config) {
  health_affordability_test <- livability_scores |>
    dplyr::transmute(
      cbsa_code,
      cbsa_name,
      livability_cluster_name,
      affordability_score = subject_score_affordability,
      health_score = subject_score_health_and_safety,
      livability_percentile,
      health_minus_affordability = subject_score_health_and_safety - subject_score_affordability
    ) |>
    dplyr::mutate(
      affordability_rank = dplyr::percent_rank(affordability_score),
      health_rank = dplyr::percent_rank(health_score),
      affordability_positive_health_negative = affordability_score > 0 & health_score < 0
    )

  health_affordability_summary <- tibble::tibble(
    correlation = cor(
      health_affordability_test$affordability_score,
      health_affordability_test$health_score
    ),
    metros_affordable_but_weaker_health = sum(health_affordability_test$affordability_positive_health_negative),
    top_quartile_affordability_and_bottom_quartile_health = sum(
      health_affordability_test$affordability_rank >= 0.75 &
        health_affordability_test$health_rank <= 0.25
    )
  )

  health_affordability_outliers <- health_affordability_test |>
    dplyr::filter(affordability_positive_health_negative) |>
    dplyr::arrange(desc(affordability_score), health_score) |>
    dplyr::slice_head(n = 20)

  environment_axis_test <- livability_scores |>
    dplyr::transmute(
      cbsa_code,
      cbsa_name,
      livability_cluster_name,
      aqi_metric_id = config$aqi_metric_id,
      aqi_value = .data[[paste0("imputed_", config$aqi_metric_id)]],
      fema_risk_score = imputed_fema_risk_score,
      scored_aqi = .data[[paste0("scored_", config$aqi_metric_id)]],
      scored_fema = scored_fema_risk_score,
      environment_gap = scored_fema_risk_score - .data[[paste0("scored_", config$aqi_metric_id)]]
    )

  environment_axis_summary <- tibble::tibble(
    raw_correlation = cor(
      environment_axis_test$aqi_value,
      environment_axis_test$fema_risk_score
    ),
    scoring_correlation = cor(
      environment_axis_test$scored_aqi,
      environment_axis_test$scored_fema
    )
  )

  environment_axis_outliers <- environment_axis_test |>
    dplyr::mutate(abs_environment_gap = abs(environment_gap)) |>
    dplyr::arrange(desc(abs_environment_gap)) |>
    dplyr::slice_head(n = 20)

  list(
    health_affordability_test = health_affordability_test,
    health_affordability_summary = health_affordability_summary,
    health_affordability_outliers = health_affordability_outliers,
    environment_axis_test = environment_axis_test,
    environment_axis_summary = environment_axis_summary,
    environment_axis_outliers = environment_axis_outliers
  )
}
