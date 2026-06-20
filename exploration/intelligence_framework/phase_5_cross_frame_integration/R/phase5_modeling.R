build_phase5_cluster_calibration_bundle <- function(redundancy_bundle, config) {
  candidate_metric_sets <- dplyr::bind_rows(
    phase5_build_candidate_metric_set(
      kpi_decisions = redundancy_bundle$kpi_decisions,
      communality_threshold = config$low_communality_threshold,
      loading_threshold = config$low_loading_threshold,
      metric_set_name = "lean_18_kpi_set"
    ),
    phase5_build_candidate_metric_set(
      kpi_decisions = redundancy_bundle$kpi_decisions,
      communality_threshold = config$moderate_communality_threshold,
      loading_threshold = config$moderate_loading_threshold,
      metric_set_name = "moderate_35_kpi_set"
    )
  )

  standardized_wide <- redundancy_bundle$standardized_wide

  calibration_summary <- purrr::map_dfr(
    unique(candidate_metric_sets$metric_set),
    \(metric_set_name) {
      metric_ids <- candidate_metric_sets |>
        dplyr::filter(metric_set == metric_set_name, keep_for_candidate) |>
        dplyr::pull(feature_id)

      cluster_input_wide <- standardized_wide |>
        dplyr::select(cbsa_code, dplyr::all_of(metric_ids)) |>
        dplyr::arrange(cbsa_code)

      cluster_input_matrix <- cluster_input_wide |>
        dplyr::select(-cbsa_code) |>
        as.matrix()

      row.names(cluster_input_matrix) <- cluster_input_wide$cbsa_code
      cluster_distance <- stats::dist(cluster_input_matrix)
      hclust_fit <- stats::hclust(cluster_distance, method = "ward.D2")

      purrr::map_dfr(config$candidate_k, \(k) {
        h_clusters <- stats::cutree(hclust_fit, k = k)
        h_sizes <- as.integer(table(h_clusters))
        h_silhouette <- cluster::silhouette(h_clusters, cluster_distance)

        set.seed(20270619 + k + ncol(cluster_input_matrix))
        kmeans_fit <- stats::kmeans(
          cluster_input_matrix,
          centers = k,
          nstart = 100,
          iter.max = 100
        )
        k_sizes <- as.integer(kmeans_fit$size)
        k_silhouette <- cluster::silhouette(kmeans_fit$cluster, cluster_distance)

        tibble::tibble(
          metric_set = metric_set_name,
          metric_count = ncol(cluster_input_matrix),
          k = k,
          hierarchical_avg_silhouette = mean(h_silhouette[, 3]),
          kmeans_avg_silhouette = mean(k_silhouette[, 3]),
          hierarchical_median_silhouette = stats::median(h_silhouette[, 3]),
          kmeans_median_silhouette = stats::median(k_silhouette[, 3]),
          hierarchical_min_cluster = min(h_sizes),
          hierarchical_max_cluster = max(h_sizes),
          kmeans_min_cluster = min(k_sizes),
          kmeans_max_cluster = max(k_sizes),
          hierarchical_clusters_under_10 = sum(h_sizes < 10),
          kmeans_clusters_under_10 = sum(k_sizes < 10),
          hierarchical_singletons = sum(h_sizes == 1),
          kmeans_singletons = sum(k_sizes == 1),
          kmeans_tot_withinss = kmeans_fit$tot.withinss,
          kmeans_betweenss_ratio = kmeans_fit$betweenss / kmeans_fit$totss
        )
      })
    }
  )

  calibration_sizes <- purrr::map_dfr(
    unique(candidate_metric_sets$metric_set),
    \(metric_set_name) {
      metric_ids <- candidate_metric_sets |>
        dplyr::filter(metric_set == metric_set_name, keep_for_candidate) |>
        dplyr::pull(feature_id)

      cluster_input_wide <- standardized_wide |>
        dplyr::select(cbsa_code, dplyr::all_of(metric_ids)) |>
        dplyr::arrange(cbsa_code)

      cluster_input_matrix <- cluster_input_wide |>
        dplyr::select(-cbsa_code) |>
        as.matrix()

      row.names(cluster_input_matrix) <- cluster_input_wide$cbsa_code
      cluster_distance <- stats::dist(cluster_input_matrix)
      hclust_fit <- stats::hclust(cluster_distance, method = "ward.D2")

      purrr::map_dfr(config$candidate_k, \(k) {
        h_clusters <- stats::cutree(hclust_fit, k = k)
        h_sizes <- tibble::tibble(
          metric_set = metric_set_name,
          method = "hierarchical",
          k = k,
          cluster = seq_along(table(h_clusters)),
          cluster_size = as.integer(table(h_clusters))
        )

        set.seed(20270619 + k + ncol(cluster_input_matrix))
        kmeans_fit <- stats::kmeans(
          cluster_input_matrix,
          centers = k,
          nstart = 100,
          iter.max = 100
        )
        k_sizes <- tibble::tibble(
          metric_set = metric_set_name,
          method = "kmeans",
          k = k,
          cluster = seq_along(kmeans_fit$size),
          cluster_size = as.integer(kmeans_fit$size)
        )

        dplyr::bind_rows(h_sizes, k_sizes)
      })
    }
  )

  list(
    candidate_metric_sets = candidate_metric_sets,
    calibration_summary = calibration_summary,
    calibration_sizes = calibration_sizes
  )
}

build_phase5_final_model_bundle <- function(input_bundle, redundancy_bundle, modeling_bundle, config) {
  selected_metric_ids <- modeling_bundle$candidate_metric_sets |>
    dplyr::filter(
      metric_set == config$selected_metric_set,
      keep_for_candidate
    ) |>
    dplyr::pull(feature_id)

  standardized_wide <- redundancy_bundle$standardized_wide

  cluster_input_wide <- standardized_wide |>
    dplyr::select(cbsa_code, dplyr::all_of(selected_metric_ids)) |>
    dplyr::arrange(cbsa_code)

  cluster_input_matrix <- cluster_input_wide |>
    dplyr::select(-cbsa_code) |>
    as.matrix()

  row.names(cluster_input_matrix) <- cluster_input_wide$cbsa_code
  cluster_distance <- stats::dist(cluster_input_matrix)
  hclust_fit <- stats::hclust(cluster_distance, method = "ward.D2")

  set.seed(20270619 + config$final_k + ncol(cluster_input_matrix))
  final_kmeans_fit <- stats::kmeans(
    cluster_input_matrix,
    centers = config$final_k,
    nstart = 100,
    iter.max = 100
  )

  final_gmm_fit <- fit_diagonal_gmm(
    x = cluster_input_matrix,
    k = config$final_k,
    init_clusters = final_kmeans_fit$cluster
  )

  final_cluster_assignments <- tibble::tibble(
    cbsa_code = cluster_input_wide$cbsa_code,
    cross_frame_hclust_cluster = as.integer(stats::cutree(hclust_fit, k = config$final_k)),
    cross_frame_kmeans_cluster = final_kmeans_fit$cluster,
    cross_frame_gmm_cluster = final_gmm_fit$cluster
  )

  colnames(final_gmm_fit$responsibilities) <- paste0("cross_frame_prob_cluster_", seq_len(config$final_k))

  gmm_probabilities <- tibble::as_tibble(final_gmm_fit$responsibilities) |>
    dplyr::mutate(cbsa_code = cluster_input_wide$cbsa_code, .before = 1)

  base_scores <- input_bundle$context_bundle |>
    dplyr::left_join(final_cluster_assignments, by = "cbsa_code") |>
    dplyr::left_join(gmm_probabilities, by = "cbsa_code") |>
    dplyr::mutate(
      cross_frame_score = rowMeans(cluster_input_matrix),
      cross_frame_percentile = dplyr::percent_rank(cross_frame_score) * 100
    )

  distance_table <- {
    centers <- final_kmeans_fit$centers
    assignments <- final_kmeans_fit$cluster
    distance_to_center <- purrr::map_dbl(seq_len(nrow(cluster_input_matrix)), \(i) {
      center_row <- centers[assignments[i], , drop = TRUE]
      sqrt(sum((cluster_input_matrix[i, ] - center_row) ^ 2))
    })

    tibble::tibble(
      cbsa_code = row.names(cluster_input_matrix),
      cross_frame_kmeans_cluster = assignments,
      distance_to_center = distance_to_center
    ) |>
      dplyr::left_join(
        base_scores |>
          dplyr::select(cbsa_code, cbsa_name, cross_frame_score, cross_frame_percentile),
        by = "cbsa_code"
      )
  }

  representative_metros <- distance_table |>
      dplyr::group_by(cross_frame_kmeans_cluster) |>
      dplyr::arrange(distance_to_center, .by_group = TRUE) |>
      dplyr::slice_head(n = 8) |>
      dplyr::ungroup()

  cluster_centroids <- base_scores |>
    dplyr::group_by(cross_frame_kmeans_cluster) |>
    dplyr::summarise(
      metros_in_cluster = dplyr::n(),
      cross_frame_score = mean(cross_frame_score),
      cross_frame_percentile = mean(cross_frame_percentile),
      character_percentile = mean(character__character_percentile),
      livability_percentile = mean(livability__livability_percentile),
      opportunity_percentile = mean(opportunity__opportunity_percentile),
      .groups = "drop"
    )

  cluster_labels <- cluster_centroids |>
    tidyr::pivot_longer(
      cols = c(character_percentile, livability_percentile, opportunity_percentile),
      names_to = "frame_column",
      values_to = "frame_percentile"
    ) |>
    dplyr::mutate(frame_id = stringr::str_remove(frame_column, "_percentile$")) |>
    dplyr::group_by(cross_frame_kmeans_cluster) |>
    dplyr::summarise(
      top_frame = frame_id[which.max(frame_percentile)],
      bottom_frame = frame_id[which.min(frame_percentile)],
      frame_order = paste(frame_id[order(frame_percentile, decreasing = TRUE)], collapse = " > "),
      cross_frame_cluster_label = paste0(
        "Type ",
        dplyr::first(cross_frame_kmeans_cluster),
        ": ",
        stringr::str_to_title(top_frame),
        " lead, ",
        stringr::str_to_title(bottom_frame),
        " lag"
      ),
      .groups = "drop"
    )

  cluster_name_map <- cluster_centroids |>
    dplyr::left_join(cluster_labels, by = "cross_frame_kmeans_cluster") |>
    dplyr::mutate(
      cross_frame_cluster_name = dplyr::case_when(
        cross_frame_kmeans_cluster == 1 ~ "High-Amenity Knowledge Civics",
        cross_frame_kmeans_cluster == 2 ~ "Entrepreneurial Strain Markets",
        cross_frame_kmeans_cluster == 3 ~ "Aging Amenity Expansion Markets",
        cross_frame_kmeans_cluster == 4 ~ "Stable Affordable Heartland Markets",
        cross_frame_kmeans_cluster == 5 ~ "Inland Strain Corridors",
        cross_frame_kmeans_cluster == 6 ~ "Sun Belt Opportunity Engines",
        TRUE ~ paste0("Combined Type ", cross_frame_kmeans_cluster)
      ),
      cluster_interpretation = paste0(
        "Cross-frame profile ordered as ",
        frame_order,
        ", with average frame percentiles of ",
        "Character ",
        round(character_percentile, 1),
        ", Livability ",
        round(livability_percentile, 1),
        ", Opportunity ",
        round(opportunity_percentile, 1),
        "."
      )
    ) |>
    dplyr::select(
      cross_frame_kmeans_cluster,
      cross_frame_cluster_name,
      cross_frame_cluster_label,
      cluster_interpretation,
      frame_order
    )

  metric_cluster_profile <- standardized_wide |>
    dplyr::select(cbsa_code, dplyr::all_of(selected_metric_ids)) |>
    tidyr::pivot_longer(
      cols = dplyr::all_of(selected_metric_ids),
      names_to = "feature_id",
      values_to = "clustering_z"
    ) |>
    dplyr::left_join(
      final_cluster_assignments |>
        dplyr::select(cbsa_code, cross_frame_kmeans_cluster),
      by = "cbsa_code"
    ) |>
    dplyr::group_by(cross_frame_kmeans_cluster, feature_id) |>
    dplyr::summarise(avg_metric_score = mean(clustering_z), .groups = "drop") |>
    dplyr::left_join(
      redundancy_bundle$kpi_decisions |>
        dplyr::select(feature_id, frame_id, metric_id),
      by = "feature_id"
    )

  cluster_metric_extremes <- dplyr::bind_rows(
    metric_cluster_profile |>
      dplyr::group_by(cross_frame_kmeans_cluster) |>
      dplyr::slice_max(avg_metric_score, n = 5, with_ties = FALSE) |>
      dplyr::mutate(extreme_direction = "top"),
    metric_cluster_profile |>
      dplyr::group_by(cross_frame_kmeans_cluster) |>
      dplyr::slice_min(avg_metric_score, n = 5, with_ties = FALSE) |>
      dplyr::mutate(extreme_direction = "bottom")
  ) |>
    dplyr::ungroup() |>
    dplyr::arrange(cross_frame_kmeans_cluster, extreme_direction, dplyr::desc(avg_metric_score))

  gmm_hybrids <- gmm_probabilities |>
    tidyr::pivot_longer(
      cols = dplyr::starts_with("cross_frame_prob_cluster_"),
      names_to = "probability_column",
      values_to = "membership_probability"
    ) |>
    dplyr::mutate(gmm_cluster = readr::parse_number(probability_column)) |>
    dplyr::arrange(cbsa_code, dplyr::desc(membership_probability)) |>
    dplyr::group_by(cbsa_code) |>
    dplyr::mutate(probability_rank = dplyr::row_number()) |>
    dplyr::filter(probability_rank <= 2) |>
    dplyr::summarise(
      top_gmm_cluster = dplyr::first(gmm_cluster),
      top_gmm_probability = dplyr::first(membership_probability),
      second_gmm_cluster = dplyr::nth(gmm_cluster, 2),
      second_gmm_probability = dplyr::nth(membership_probability, 2),
      hybrid_membership_gap = top_gmm_probability - second_gmm_probability,
      .groups = "drop"
    )

  cosine_similarity <- phase5_normalize_matrix_rows(cluster_input_matrix) %*% t(phase5_normalize_matrix_rows(cluster_input_matrix))

  similarity_top10 <- purrr::map_dfr(seq_len(nrow(cosine_similarity)), \(i) {
    similarity_values <- cosine_similarity[i, ]
    ranking <- order(similarity_values, decreasing = TRUE)
    ranking <- ranking[ranking != i][1:10]

    tibble::tibble(
      cbsa_code = row.names(cosine_similarity)[i],
      peer_rank = seq_along(ranking),
      peer_cbsa_code = row.names(cosine_similarity)[ranking],
      cosine_similarity = similarity_values[ranking]
    )
  }) |>
    dplyr::left_join(
      base_scores |>
        dplyr::select(cbsa_code, cbsa_name),
      by = "cbsa_code"
    ) |>
    dplyr::left_join(
      base_scores |>
        dplyr::select(peer_cbsa_code = cbsa_code, peer_cbsa_name = cbsa_name),
      by = "peer_cbsa_code"
    ) |>
    dplyr::select(cbsa_code, cbsa_name, peer_rank, peer_cbsa_code, peer_cbsa_name, cosine_similarity)

  cross_frame_scores <- base_scores |>
    dplyr::left_join(cluster_name_map, by = "cross_frame_kmeans_cluster") |>
    dplyr::left_join(gmm_hybrids, by = "cbsa_code") |>
    dplyr::left_join(
      distance_table |>
        dplyr::select(cbsa_code, distance_to_center),
      by = "cbsa_code"
    ) |>
    dplyr::left_join(
      similarity_top10 |>
        dplyr::filter(peer_rank == 1) |>
        dplyr::transmute(
          cbsa_code,
          peer_1_code = peer_cbsa_code,
          peer_1_name = peer_cbsa_name,
          peer_1_similarity = cosine_similarity
        ),
      by = "cbsa_code"
    )

  cluster_representatives <- representative_metros |>
    dplyr::left_join(cluster_name_map, by = "cross_frame_kmeans_cluster")

  gmm_cluster_summary <- cross_frame_scores |>
    dplyr::select(cbsa_code, cross_frame_gmm_cluster, dplyr::starts_with("cross_frame_prob_cluster_")) |>
    tidyr::pivot_longer(
      cols = dplyr::starts_with("cross_frame_prob_cluster_"),
      names_to = "probability_column",
      values_to = "membership_probability"
    ) |>
    dplyr::mutate(gmm_cluster = readr::parse_number(probability_column)) |>
    dplyr::group_by(gmm_cluster) |>
    dplyr::summarise(
      avg_membership_probability = mean(membership_probability),
      metros_as_top_membership = sum(gmm_cluster == cross_frame_gmm_cluster),
      .groups = "drop"
    )

  list(
    selected_metric_ids = selected_metric_ids,
    cluster_input_wide = cluster_input_wide,
    cluster_input_matrix = cluster_input_matrix,
    final_cluster_assignments = final_cluster_assignments,
    gmm_probabilities = gmm_probabilities,
    cross_frame_scores = cross_frame_scores,
    cluster_centroids = cluster_centroids,
    cluster_name_map = cluster_name_map,
    cluster_metric_extremes = cluster_metric_extremes,
    cluster_representatives = cluster_representatives,
    gmm_hybrids = gmm_hybrids,
    gmm_cluster_summary = gmm_cluster_summary,
    similarity_top10 = similarity_top10
  )
}
