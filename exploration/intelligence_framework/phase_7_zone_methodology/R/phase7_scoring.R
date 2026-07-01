build_phase7_scoring_bundle <- function(phase7_model_df, cluster_bundle, config) {
  character_metrics <- config$expected_kpis |>
    dplyr::filter(theme == "character") |>
    dplyr::pull(metric_id)
  livability_metrics <- config$expected_kpis |>
    dplyr::filter(theme == "livability") |>
    dplyr::pull(metric_id)
  opportunity_metrics <- config$expected_kpis |>
    dplyr::filter(theme == "opportunity") |>
    dplyr::pull(metric_id)

  standardized_wide <- cluster_bundle$modeling_long |>
    dplyr::select(tract_geoid, metric_id, scoring_z) |>
    tidyr::pivot_wider(
      names_from = metric_id,
      values_from = scoring_z,
      names_prefix = "standardized_"
    )

  scores <- standardized_wide |>
    dplyr::mutate(
      character_score = rowMeans(dplyr::pick(dplyr::all_of(paste0("standardized_", character_metrics)))),
      livability_score = rowMeans(dplyr::pick(dplyr::all_of(paste0("standardized_", livability_metrics)))),
      opportunity_score = rowMeans(dplyr::pick(dplyr::all_of(paste0("standardized_", opportunity_metrics)))),
      composite_score = (character_score + livability_score + opportunity_score) / 3
    ) |>
    dplyr::left_join(cluster_bundle$final_cluster_assignments, by = "tract_geoid") |>
    dplyr::left_join(cluster_bundle$provisional_label_map, by = "zone_kmeans_cluster") |>
    dplyr::left_join(cluster_bundle$gmm_probabilities, by = "tract_geoid") |>
    dplyr::left_join(
      phase7_model_df |>
        dplyr::select(
          tract_geoid,
          cbsa_code,
          county_geoid,
          geo_name,
          cbsa_name,
          county_name,
          is_opportunity_zone,
          dplyr::starts_with("imputed_")
        ),
      by = "tract_geoid"
    ) |>
    dplyr::mutate(
      national_character_percentile = phase7_percent_rank(character_score),
      national_livability_percentile = phase7_percent_rank(livability_score),
      national_opportunity_percentile = phase7_percent_rank(opportunity_score),
      national_composite_percentile = phase7_percent_rank(composite_score)
    ) |>
    dplyr::group_by(cbsa_code) |>
    dplyr::mutate(
      cbsa_character_percentile = phase7_percent_rank(character_score),
      cbsa_livability_percentile = phase7_percent_rank(livability_score),
      cbsa_opportunity_percentile = phase7_percent_rank(opportunity_score),
      cbsa_composite_percentile = phase7_percent_rank(composite_score)
    ) |>
    dplyr::ungroup() |>
    dplyr::group_by(provisional_zone_type) |>
    dplyr::mutate(
      zone_peer_character_percentile = phase7_percent_rank(character_score),
      zone_peer_livability_percentile = phase7_percent_rank(livability_score),
      zone_peer_opportunity_percentile = phase7_percent_rank(opportunity_score),
      zone_peer_composite_percentile = phase7_percent_rank(composite_score)
    ) |>
    dplyr::ungroup() |>
    dplyr::mutate(
      selected_k_for_run = cluster_bundle$provisional_k,
      zone_type = provisional_zone_type
    ) |>
    dplyr::select(
      tract_geoid,
      cbsa_code,
      county_geoid,
      geo_name,
      cbsa_name,
      county_name,
      zone_type,
      zone_kmeans_cluster,
      zone_hclust_cluster,
      zone_gmm_cluster,
      zone_type_name_status,
      selected_k_for_run,
      dplyr::starts_with("zone_type_prob_k"),
      character_score,
      livability_score,
      opportunity_score,
      composite_score,
      national_character_percentile,
      national_livability_percentile,
      national_opportunity_percentile,
      national_composite_percentile,
      cbsa_character_percentile,
      cbsa_livability_percentile,
      cbsa_opportunity_percentile,
      cbsa_composite_percentile,
      zone_peer_character_percentile,
      zone_peer_livability_percentile,
      zone_peer_opportunity_percentile,
      zone_peer_composite_percentile,
      is_opportunity_zone,
      dplyr::starts_with("standardized_"),
      dplyr::starts_with("imputed_")
    ) |>
    dplyr::arrange(tract_geoid)

  list(
    zone_scores = scores
  )
}
