build_phase7_national_cluster_bundle <- function(phase7_model_df, config) {
  metric_ids <- config$expected_kpis$metric_id
  cluster_metric_ids <- config$clustering_metric_decisions |>
    dplyr::filter(use_for_clustering) |>
    dplyr::pull(metric_id)

  modeling_long <- phase7_model_df |>
    dplyr::select(
      tract_geoid,
      geo_name,
      cbsa_code,
      cbsa_name,
      county_geoid,
      county_name,
      dplyr::all_of(paste0("imputed_", metric_ids))
    ) |>
    tidyr::pivot_longer(
      cols = dplyr::all_of(paste0("imputed_", metric_ids)),
      names_to = "metric_column",
      values_to = "imputed_value"
    ) |>
    dplyr::mutate(metric_id = stringr::str_remove(metric_column, "^imputed_")) |>
    dplyr::select(-metric_column) |>
    dplyr::left_join(
      phase7_model_df |>
        dplyr::select(tract_geoid, dplyr::all_of(paste0("scored_", metric_ids))) |>
        tidyr::pivot_longer(
          cols = dplyr::all_of(paste0("scored_", metric_ids)),
          names_to = "score_column",
          values_to = "scoring_value"
        ) |>
        dplyr::mutate(metric_id = stringr::str_remove(score_column, "^scored_")) |>
        dplyr::select(tract_geoid, metric_id, scoring_value),
      by = c("tract_geoid", "metric_id")
    ) |>
    dplyr::left_join(
      config$expected_kpis |>
        dplyr::select(metric_id, theme, polarity, audit_bucket, use_for_clustering),
      by = "metric_id"
    ) |>
    dplyr::group_by(metric_id) |>
    dplyr::mutate(
      clustering_z = safe_zscore(imputed_value),
      scoring_z = safe_zscore(scoring_value)
    ) |>
    dplyr::ungroup()

  standardization_audit <- modeling_long |>
    dplyr::group_by(metric_id, theme, polarity, audit_bucket, use_for_clustering) |>
    dplyr::summarise(
      clustering_mean = mean(clustering_z),
      clustering_sd = stats::sd(clustering_z),
      scoring_mean = mean(scoring_z),
      scoring_sd = stats::sd(scoring_z),
      .groups = "drop"
    ) |>
    dplyr::arrange(metric_id)

  cluster_input_wide <- modeling_long |>
    dplyr::filter(metric_id %in% cluster_metric_ids) |>
    dplyr::select(tract_geoid, metric_id, clustering_z) |>
    tidyr::pivot_wider(
      names_from = metric_id,
      values_from = clustering_z,
      names_prefix = "cluster_z_"
    ) |>
    dplyr::arrange(tract_geoid)

  cluster_input_matrix <- cluster_input_wide |>
    dplyr::select(-tract_geoid) |>
    as.matrix()

  row.names(cluster_input_matrix) <- cluster_input_wide$tract_geoid
  calibration_sample_size <- min(config$calibration_sample_size, nrow(cluster_input_matrix))
  set.seed(20270701 + calibration_sample_size)
  calibration_index <- sort(sample.int(nrow(cluster_input_matrix), calibration_sample_size))
  calibration_matrix <- cluster_input_matrix[calibration_index, , drop = FALSE]
  calibration_tract_geoid <- row.names(cluster_input_matrix)[calibration_index]
  calibration_distance <- stats::dist(calibration_matrix)
  hclust_fit <- stats::hclust(calibration_distance, method = "ward.D2")

  cluster_count_calibration <- purrr::map_dfr(config$candidate_k, \(k) {
    hierarchical_clusters <- flatten_cutree(hclust_fit, k)
    hierarchical_sizes <- as.integer(table(hierarchical_clusters))
    hierarchical_silhouette <- cluster::silhouette(hierarchical_clusters, calibration_distance)

    set.seed(20270701 + k + ncol(calibration_matrix))
    kmeans_fit <- stats::kmeans(calibration_matrix, centers = k, nstart = 25, iter.max = 50)
    kmeans_sizes <- as.integer(kmeans_fit$size)
    kmeans_silhouette <- cluster::silhouette(kmeans_fit$cluster, calibration_distance)

    tibble::tibble(
      k = k,
      metric_set = "phase7_default_22_kpi_set",
      metric_count = length(cluster_metric_ids),
      calibration_sample_size = calibration_sample_size,
      hierarchical_avg_silhouette = mean(hierarchical_silhouette[, 3]),
      kmeans_avg_silhouette = mean(kmeans_silhouette[, 3]),
      hierarchical_median_silhouette = stats::median(hierarchical_silhouette[, 3]),
      kmeans_median_silhouette = stats::median(kmeans_silhouette[, 3]),
      hierarchical_min_cluster = min(hierarchical_sizes),
      hierarchical_max_cluster = max(hierarchical_sizes),
      kmeans_min_cluster = min(kmeans_sizes),
      kmeans_max_cluster = max(kmeans_sizes),
      hierarchical_clusters_under_100 = sum(hierarchical_sizes < 100),
      kmeans_clusters_under_100 = sum(kmeans_sizes < 100),
      kmeans_tot_withinss = kmeans_fit$tot.withinss,
      kmeans_betweenss_ratio = kmeans_fit$betweenss / kmeans_fit$totss
    )
  })

  cluster_count_sizes <- purrr::map_dfr(config$candidate_k, \(k) {
    hierarchical_clusters <- flatten_cutree(hclust_fit, k)
    hierarchical_sizes <- tibble::tibble(
      method = "hierarchical",
      k = k,
      calibration_sample_size = calibration_sample_size,
      cluster = seq_along(table(hierarchical_clusters)),
      cluster_size = as.integer(table(hierarchical_clusters))
    )

    set.seed(20270701 + k + ncol(calibration_matrix))
    kmeans_fit <- stats::kmeans(calibration_matrix, centers = k, nstart = 25, iter.max = 50)
    kmeans_sizes <- tibble::tibble(
      method = "kmeans",
      k = k,
      calibration_sample_size = calibration_sample_size,
      cluster = seq_along(kmeans_fit$size),
      cluster_size = as.integer(kmeans_fit$size)
    )

    dplyr::bind_rows(hierarchical_sizes, kmeans_sizes)
  })

  provisional_k <- cluster_count_calibration |>
    dplyr::arrange(dplyr::desc(kmeans_avg_silhouette), k) |>
    dplyr::slice_head(n = 1) |>
    dplyr::pull(k)

  set.seed(20270701 + provisional_k + ncol(cluster_input_matrix))
  provisional_kmeans_fit <- stats::kmeans(
    cluster_input_matrix,
    centers = provisional_k,
    nstart = 100,
    iter.max = 100
  )

  if (isTRUE(config$run_gmm)) {
    provisional_gmm_fit <- fit_diagonal_gmm(
      x = cluster_input_matrix,
      k = provisional_k,
      init_clusters = provisional_kmeans_fit$cluster
    )
    gmm_cluster <- provisional_gmm_fit$cluster
    gmm_probability_matrix <- provisional_gmm_fit$responsibilities
  } else {
    gmm_cluster <- rep(NA_integer_, nrow(cluster_input_matrix))
    gmm_probability_matrix <- matrix(
      NA_real_,
      nrow = nrow(cluster_input_matrix),
      ncol = provisional_k
    )
  }

  final_cluster_assignments <- tibble::tibble(
    tract_geoid = cluster_input_wide$tract_geoid,
    zone_hclust_cluster = NA_integer_,
    zone_kmeans_cluster = provisional_kmeans_fit$cluster,
    zone_gmm_cluster = gmm_cluster
  )

  colnames(gmm_probability_matrix) <- paste0("zone_type_prob_k", seq_len(provisional_k))

  gmm_probabilities <- tibble::as_tibble(gmm_probability_matrix) |>
    dplyr::mutate(tract_geoid = cluster_input_wide$tract_geoid, .before = 1)

  gmm_cluster_summary <- if (isTRUE(config$run_gmm)) {
    gmm_probabilities |>
      dplyr::left_join(final_cluster_assignments, by = "tract_geoid") |>
      tidyr::pivot_longer(
        cols = dplyr::starts_with("zone_type_prob_k"),
        names_to = "probability_column",
        values_to = "membership_probability"
      ) |>
      dplyr::mutate(gmm_cluster = readr::parse_number(probability_column)) |>
      dplyr::group_by(gmm_cluster) |>
      dplyr::summarise(
        avg_membership_probability = mean(membership_probability),
        max_membership_probability = max(membership_probability),
        tracts_as_top_membership = sum(gmm_cluster == zone_gmm_cluster),
        .groups = "drop"
      )
  } else {
    tibble::tibble(
      gmm_cluster = integer(),
      avg_membership_probability = double(),
      max_membership_probability = double(),
      tracts_as_top_membership = integer()
    )
  }

  standardized_kpis_wide <- modeling_long |>
    dplyr::select(tract_geoid, metric_id, scoring_z) |>
    tidyr::pivot_wider(
      names_from = metric_id,
      values_from = scoring_z,
      names_prefix = "standardized_"
    )

  subject_centroids <- final_cluster_assignments |>
    dplyr::left_join(standardized_kpis_wide, by = "tract_geoid") |>
    dplyr::group_by(zone_kmeans_cluster) |>
    dplyr::summarise(
      tracts_in_cluster = dplyr::n(),
      subject_score_character = mean(rowMeans(dplyr::pick(dplyr::all_of(paste0("standardized_", config$expected_kpis$metric_id[config$expected_kpis$theme == "character"]))))),
      subject_score_livability = mean(rowMeans(dplyr::pick(dplyr::all_of(paste0("standardized_", config$expected_kpis$metric_id[config$expected_kpis$theme == "livability"]))))),
      subject_score_opportunity = mean(rowMeans(dplyr::pick(dplyr::all_of(paste0("standardized_", config$expected_kpis$metric_id[config$expected_kpis$theme == "opportunity"]))))),
      dplyr::across(dplyr::starts_with("standardized_"), mean),
      .groups = "drop"
    ) |>
    dplyr::rename_with(
      \(x) stringr::str_remove(x, "^standardized_"),
      dplyr::starts_with("standardized_")
    )

  provisional_label_map <- build_phase7_provisional_label_map(subject_centroids, config)

  cluster_centroids <- subject_centroids |>
    dplyr::left_join(provisional_label_map, by = "zone_kmeans_cluster") |>
    dplyr::mutate(
      selected_k_for_run = provisional_k,
      labeling_status = "provisional_pending_review"
    ) |>
    dplyr::arrange(zone_kmeans_cluster)

  cluster_member_distances <- tibble::tibble(
    tract_geoid = row.names(cluster_input_matrix),
    zone_kmeans_cluster = provisional_kmeans_fit$cluster,
    distance_to_center = phase7_cluster_distance_to_center(
      cluster_input_matrix = cluster_input_matrix,
      assignments = provisional_kmeans_fit$cluster,
      centers = provisional_kmeans_fit$centers
    )
  )

  representative_tracts <- cluster_member_distances |>
    dplyr::left_join(
      phase7_model_df |>
        dplyr::select(tract_geoid, geo_name, cbsa_code, cbsa_name, county_geoid, county_name),
      by = "tract_geoid"
    ) |>
    dplyr::left_join(provisional_label_map, by = "zone_kmeans_cluster") |>
    dplyr::group_by(zone_kmeans_cluster) |>
    dplyr::arrange(distance_to_center, .by_group = TRUE) |>
    dplyr::slice_head(n = 5) |>
    dplyr::ungroup()

  light_validation <- final_cluster_assignments |>
    dplyr::left_join(
      phase7_model_df |>
        dplyr::select(tract_geoid, cbsa_name),
      by = "tract_geoid"
    ) |>
    dplyr::left_join(provisional_label_map, by = "zone_kmeans_cluster") |>
    dplyr::filter(cbsa_name %in% config$light_validation_cbsa_names) |>
    dplyr::count(cbsa_name, provisional_zone_type, name = "tract_count") |>
    dplyr::group_by(cbsa_name) |>
    dplyr::mutate(cbsa_zone_share = tract_count / sum(tract_count)) |>
    dplyr::ungroup() |>
    dplyr::arrange(cbsa_name, dplyr::desc(tract_count))

  list(
    modeling_long = modeling_long,
    standardization_audit = standardization_audit,
    cluster_input_wide = cluster_input_wide,
    cluster_count_calibration = cluster_count_calibration,
    cluster_count_sizes = cluster_count_sizes,
    calibration_tract_geoid = calibration_tract_geoid,
    provisional_k = provisional_k,
    final_cluster_assignments = final_cluster_assignments,
    gmm_probabilities = gmm_probabilities,
    gmm_cluster_summary = gmm_cluster_summary,
    cluster_centroids = cluster_centroids,
    representative_tracts = representative_tracts,
    provisional_label_map = provisional_label_map,
    light_validation = light_validation
  )
}
