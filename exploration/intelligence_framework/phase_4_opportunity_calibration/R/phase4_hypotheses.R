build_phase4_hypothesis_bundle <- function(opportunity_scores, con) {
  industry_leading_indicator_test <- DBI::dbGetQuery(
    con,
    "
    WITH industry_base AS (
      SELECT
        geo_id AS cbsa_code,
        geo_name AS cbsa_name,
        lq_professional,
        lq_information,
        lq_manufacturing,
        pct_qcew_private_emp_professional,
        pct_qcew_private_emp_information,
        pct_qcew_private_emp_manufacturing
      FROM gold.economics_industry_wide
      WHERE geo_level = 'cbsa'
        AND year = 2015
    ),
    income_outcome AS (
      SELECT
        geo_id AS cbsa_code,
        income_pc_growth_5yr
      FROM gold.economics_income_wide
      WHERE geo_level = 'cbsa'
        AND year = 2022
    )
    SELECT
      industry_base.cbsa_code,
      industry_base.cbsa_name,
      industry_base.lq_professional,
      industry_base.lq_information,
      industry_base.lq_manufacturing,
      industry_base.pct_qcew_private_emp_professional,
      industry_base.pct_qcew_private_emp_information,
      industry_base.pct_qcew_private_emp_manufacturing,
      income_outcome.income_pc_growth_5yr
    FROM industry_base
    INNER JOIN income_outcome
      ON industry_base.cbsa_code = income_outcome.cbsa_code
    WHERE income_outcome.income_pc_growth_5yr IS NOT NULL
      AND industry_base.lq_professional IS NOT NULL
      AND industry_base.lq_information IS NOT NULL
      AND industry_base.lq_manufacturing IS NOT NULL
    "
  ) |>
    tibble::as_tibble() |>
    dplyr::left_join(
      opportunity_scores |>
        dplyr::select(cbsa_code, opportunity_cluster_name, opportunity_percentile),
      by = "cbsa_code"
    )

  industry_leading_indicator_lm <- stats::lm(
    income_pc_growth_5yr ~ lq_professional + lq_information + lq_manufacturing,
    data = industry_leading_indicator_test
  )

  industry_leading_indicator_summary <- tibble::tibble(
    sample_size = nrow(industry_leading_indicator_test),
    lq_professional_beta = unname(stats::coef(industry_leading_indicator_lm)[["lq_professional"]]),
    lq_professional_p_value = summary(industry_leading_indicator_lm)$coefficients["lq_professional", "Pr(>|t|)"],
    lq_information_beta = unname(stats::coef(industry_leading_indicator_lm)[["lq_information"]]),
    lq_information_p_value = summary(industry_leading_indicator_lm)$coefficients["lq_information", "Pr(>|t|)"],
    lq_manufacturing_beta = unname(stats::coef(industry_leading_indicator_lm)[["lq_manufacturing"]]),
    lq_manufacturing_p_value = summary(industry_leading_indicator_lm)$coefficients["lq_manufacturing", "Pr(>|t|)"],
    adjusted_r_squared = summary(industry_leading_indicator_lm)$adj.r.squared
  )

  industry_leading_indicator_outliers <- industry_leading_indicator_test |>
    dplyr::mutate(
      fitted_income_growth = stats::predict(industry_leading_indicator_lm),
      growth_residual = income_pc_growth_5yr - fitted_income_growth,
      abs_growth_residual = abs(growth_residual)
    ) |>
    dplyr::arrange(dplyr::desc(abs_growth_residual)) |>
    dplyr::slice_head(n = 20)

  social_capital_test <- opportunity_scores |>
    dplyr::transmute(
      cbsa_code,
      cbsa_name,
      opportunity_cluster_name,
      economic_connectedness = imputed_economic_connectedness,
      income_pc_growth_5yr = imputed_income_pc_growth_5yr,
      business_score = subject_score_business_and_industry_opportunity,
      market_score = subject_score_market_opportunity,
      resident_score = subject_score_resident_opportunity,
      opportunity_score,
      opportunity_percentile
    )

  social_capital_lm <- stats::lm(
    income_pc_growth_5yr ~ economic_connectedness + business_score,
    data = social_capital_test
  )

  social_capital_summary <- tibble::tibble(
    raw_correlation = cor(
      social_capital_test$economic_connectedness,
      social_capital_test$income_pc_growth_5yr
    ),
    business_adjusted_connectedness_beta = unname(stats::coef(social_capital_lm)[["economic_connectedness"]]),
    business_adjusted_connectedness_p_value = summary(social_capital_lm)$coefficients["economic_connectedness", "Pr(>|t|)"],
    adjusted_r_squared = summary(social_capital_lm)$adj.r.squared
  )

  social_capital_outliers <- social_capital_test |>
    dplyr::mutate(
      fitted_income_growth = stats::predict(social_capital_lm),
      growth_residual = income_pc_growth_5yr - fitted_income_growth,
      abs_growth_residual = abs(growth_residual)
    ) |>
    dplyr::arrange(dplyr::desc(abs_growth_residual)) |>
    dplyr::slice_head(n = 20)

  signal_divergence_test <- opportunity_scores |>
    dplyr::transmute(
      cbsa_code,
      cbsa_name,
      opportunity_cluster_name,
      market_short_run = scored_hpi_yoy_pct,
      market_long_run = scored_hpi_5yr_pct,
      resident_short_run = scored_pct_unemployment_rate,
      resident_long_run = scored_income_pc_growth_5yr,
      market_signal_gap = scored_hpi_yoy_pct - scored_hpi_5yr_pct,
      resident_signal_gap = scored_pct_unemployment_rate - scored_income_pc_growth_5yr,
      absolute_signal_gap = abs(market_signal_gap) + abs(resident_signal_gap),
      opportunity_percentile
    )

  signal_divergence_summary <- tibble::tibble(
    market_short_long_correlation = cor(
      signal_divergence_test$market_short_run,
      signal_divergence_test$market_long_run
    ),
    resident_short_long_correlation = cor(
      signal_divergence_test$resident_short_run,
      signal_divergence_test$resident_long_run
    ),
    metros_with_large_market_gap = sum(abs(signal_divergence_test$market_signal_gap) >= 1),
    metros_with_large_resident_gap = sum(abs(signal_divergence_test$resident_signal_gap) >= 1)
  )

  signal_divergence_outliers <- signal_divergence_test |>
    dplyr::arrange(dplyr::desc(absolute_signal_gap)) |>
    dplyr::slice_head(n = 20)

  oz_overlay <- DBI::dbGetQuery(
    con,
    "
    SELECT
      geo_id AS cbsa_code,
      oz_tract_count,
      total_tract_count,
      pct_oz_tracts,
      oz_population,
      total_population,
      pct_population_in_oz
    FROM gold.dim_policy_designations
    WHERE geo_level = 'cbsa'
      AND year IS NULL
    "
  ) |>
    tibble::as_tibble()

  livability_scores <- arrow::read_parquet(
    here::here(
      "exploration",
      "intelligence_framework",
      "phase_3_livability_calibration",
      "outputs",
      "livability_scores.parquet"
    )
  ) |>
    dplyr::select(
      cbsa_code,
      cbsa_name,
      livability_score,
      livability_percentile,
      livability_cluster_name
    )

  livability_opportunity_scatter <- opportunity_scores |>
    dplyr::select(
      cbsa_code,
      cbsa_name,
      opportunity_score,
      opportunity_percentile,
      opportunity_cluster_name
    ) |>
    dplyr::left_join(livability_scores, by = c("cbsa_code", "cbsa_name")) |>
    dplyr::left_join(oz_overlay, by = "cbsa_code") |>
    dplyr::mutate(
      livability_opportunity_quadrant = dplyr::case_when(
        livability_percentile >= 50 & opportunity_percentile >= 50 ~ "high_livability_high_opportunity",
        livability_percentile >= 50 & opportunity_percentile < 50 ~ "high_livability_lower_opportunity",
        livability_percentile < 50 & opportunity_percentile >= 50 ~ "lower_livability_high_opportunity",
        TRUE ~ "lower_livability_lower_opportunity"
      )
    )

  livability_opportunity_summary <- livability_opportunity_scatter |>
    dplyr::count(livability_opportunity_quadrant, name = "metros") |>
    dplyr::arrange(dplyr::desc(metros))

  livability_opportunity_outliers <- livability_opportunity_scatter |>
    dplyr::mutate(
      livability_opportunity_gap = opportunity_percentile - livability_percentile,
      abs_gap = abs(livability_opportunity_gap)
    ) |>
    dplyr::arrange(dplyr::desc(abs_gap)) |>
    dplyr::slice_head(n = 25)

  oz_high_opportunity_context <- livability_opportunity_scatter |>
    dplyr::filter(opportunity_percentile >= 75) |>
    dplyr::arrange(dplyr::desc(pct_population_in_oz), dplyr::desc(pct_oz_tracts), dplyr::desc(opportunity_percentile)) |>
    dplyr::slice_head(n = 25)

  list(
    industry_leading_indicator_test = industry_leading_indicator_test,
    industry_leading_indicator_summary = industry_leading_indicator_summary,
    industry_leading_indicator_outliers = industry_leading_indicator_outliers,
    social_capital_test = social_capital_test,
    social_capital_summary = social_capital_summary,
    social_capital_outliers = social_capital_outliers,
    signal_divergence_test = signal_divergence_test,
    signal_divergence_summary = signal_divergence_summary,
    signal_divergence_outliers = signal_divergence_outliers,
    livability_opportunity_scatter = livability_opportunity_scatter,
    livability_opportunity_summary = livability_opportunity_summary,
    livability_opportunity_outliers = livability_opportunity_outliers,
    oz_high_opportunity_context = oz_high_opportunity_context
  )
}
