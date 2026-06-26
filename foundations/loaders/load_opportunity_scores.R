source(here::here("foundations", "loaders", "_shared_intelligence_loader.R"))

opportunity_peers <- build_peer_wide(
  "exploration/intelligence_framework/phase_4_opportunity_calibration/outputs/opportunity_phase4_similarity_top10.csv"
)

write_intelligence_datamart(
  parquet_rel_path = "exploration/intelligence_framework/phase_4_opportunity_calibration/outputs/opportunity_scores.parquet",
  table_name = "intelligence_opportunity",
  transform_fn = function(df) {
    df |>
      left_join(opportunity_peers, by = "cbsa_code") |>
      mutate(
        opportunity_cluster = opportunity_cluster_name,
        opportunity_percentile_rank = as.integer(round(opportunity_percentile)),
        resident_opportunity_score = subject_score_resident_opportunity,
        market_opportunity_score = subject_score_market_opportunity,
        business_and_industry_score = subject_score_business_and_industry_opportunity
      )
  }
)
