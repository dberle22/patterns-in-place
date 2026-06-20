build_phase2_model_bundle <- function(character_model_df, character_frame, catalog_check, config) {
  flatten_cutree <- function(hclust_fit, k) {
    cutree_output <- stats::cutree(hclust_fit, k = k)

    if (is.matrix(cutree_output)) {
      return(as.integer(cutree_output[, 1]))
    }

    as.integer(cutree_output)
  }

  topic_metadata <- character_frame$subjects |>
    purrr::map_dfr(\(subject) {
      purrr::map_dfr(or_empty(subject$topics), \(topic) {
        tibble::tibble(
          subject_id = subject$subject_id,
          subject_display_name = subject$display_name,
          subject_weight = subject$subject_weight,
          topic_id = topic$topic_id,
          topic_display_name = topic$display_name,
          reliability = topic$reliability,
          coverage = topic$coverage
        )
      })
    })

  selected_metric_metadata <- catalog_check |>
    dplyr::select(metric_id, subject_id, topic_id, reliability, polarity, model_role) |>
    dplyr::filter(metric_id %in% config$expected_kpis$metric_id)

  topic_weight_reference <- topic_metadata |>
    dplyr::inner_join(
      selected_metric_metadata |>
        dplyr::count(subject_id, topic_id, name = "n_selected_kpis"),
      by = c("subject_id", "topic_id")
    ) |>
    dplyr::mutate(
      reliability_factor = 1.00,
      raw_topic_weight = coverage * reliability_factor
    ) |>
    dplyr::group_by(subject_id) |>
    dplyr::mutate(topic_weight_within_subject = raw_topic_weight / sum(raw_topic_weight)) |>
    dplyr::ungroup()

  modeling_long <- character_model_df |>
    dplyr::select(
      cbsa_code,
      cbsa_name,
      pop_total,
      dplyr::all_of(paste0("imputed_", config$expected_kpis$metric_id))
    ) |>
    tidyr::pivot_longer(
      cols = dplyr::all_of(paste0("imputed_", config$expected_kpis$metric_id)),
      names_to = "metric_column",
      values_to = "imputed_value"
    ) |>
    dplyr::mutate(metric_id = stringr::str_remove(metric_column, "^imputed_")) |>
    dplyr::select(-metric_column) |>
    dplyr::left_join(
      character_model_df |>
        dplyr::select(cbsa_code, dplyr::all_of(paste0("scored_", config$expected_kpis$metric_id))) |>
        tidyr::pivot_longer(
          cols = dplyr::all_of(paste0("scored_", config$expected_kpis$metric_id)),
          names_to = "score_column",
          values_to = "scoring_value"
        ) |>
        dplyr::mutate(metric_id = stringr::str_remove(score_column, "^scored_")) |>
        dplyr::select(cbsa_code, metric_id, scoring_value),
      by = c("cbsa_code", "metric_id")
    ) |>
    dplyr::left_join(selected_metric_metadata, by = "metric_id") |>
    dplyr::group_by(metric_id) |>
    dplyr::mutate(
      clustering_z = safe_zscore(imputed_value),
      scoring_z = safe_zscore(scoring_value)
    ) |>
    dplyr::ungroup()

  standardization_audit <- modeling_long |>
    dplyr::group_by(metric_id, polarity, reliability, model_role) |>
    dplyr::summarise(
      clustering_mean = mean(clustering_z),
      clustering_sd = stats::sd(clustering_z),
      scoring_mean = mean(scoring_z),
      scoring_sd = stats::sd(scoring_z),
      .groups = "drop"
    ) |>
    dplyr::arrange(metric_id)

  cluster_metric_ids <- config$clustering_metric_decisions |>
    dplyr::filter(use_for_clustering) |>
    dplyr::pull(metric_id)

  cluster_input_wide <- modeling_long |>
    dplyr::filter(metric_id %in% cluster_metric_ids) |>
    dplyr::select(cbsa_code, metric_id, clustering_z) |>
    tidyr::pivot_wider(
      names_from = metric_id,
      values_from = clustering_z,
      names_prefix = "cluster_z_"
    ) |>
    dplyr::arrange(cbsa_code)

  cluster_input_matrix <- cluster_input_wide |>
    dplyr::select(-cbsa_code) |>
    as.matrix()

  row.names(cluster_input_matrix) <- cluster_input_wide$cbsa_code
  cluster_distance <- stats::dist(cluster_input_matrix)
  hclust_fit <- stats::hclust(cluster_distance, method = "ward.D2")

  cluster_count_calibration <- purrr::map_dfr(config$candidate_k_extended, \(k) {
    hierarchical_clusters <- flatten_cutree(hclust_fit, k)
    hierarchical_sizes <- as.integer(table(hierarchical_clusters))
    hierarchical_silhouette <- cluster::silhouette(hierarchical_clusters, cluster_distance)

    set.seed(20270618 + k + ncol(cluster_input_matrix))
    kmeans_fit <- stats::kmeans(cluster_input_matrix, centers = k, nstart = 100, iter.max = 100)
    kmeans_sizes <- as.integer(kmeans_fit$size)
    kmeans_silhouette <- cluster::silhouette(kmeans_fit$cluster, cluster_distance)

    tibble::tibble(
      k = k,
      metric_set = "full_17_kpi_set",
      metric_count = length(cluster_metric_ids),
      hierarchical_avg_silhouette = mean(hierarchical_silhouette[, 3]),
      kmeans_avg_silhouette = mean(kmeans_silhouette[, 3]),
      hierarchical_median_silhouette = stats::median(hierarchical_silhouette[, 3]),
      kmeans_median_silhouette = stats::median(kmeans_silhouette[, 3]),
      hierarchical_min_cluster = min(hierarchical_sizes),
      hierarchical_max_cluster = max(hierarchical_sizes),
      kmeans_min_cluster = min(kmeans_sizes),
      kmeans_max_cluster = max(kmeans_sizes),
      hierarchical_clusters_under_10 = sum(hierarchical_sizes < 10),
      kmeans_clusters_under_10 = sum(kmeans_sizes < 10),
      hierarchical_singletons = sum(hierarchical_sizes == 1),
      kmeans_singletons = sum(kmeans_sizes == 1),
      kmeans_tot_withinss = kmeans_fit$tot.withinss,
      kmeans_betweenss_ratio = kmeans_fit$betweenss / kmeans_fit$totss
    )
  })

  cluster_count_sizes <- purrr::map_dfr(config$candidate_k_extended, \(k) {
    hierarchical_clusters <- flatten_cutree(hclust_fit, k)
    hierarchical_sizes <- tibble::tibble(
      method = "hierarchical",
      k = k,
      cluster = seq_along(table(hierarchical_clusters)),
      cluster_size = as.integer(table(hierarchical_clusters))
    )

    set.seed(20270618 + k + ncol(cluster_input_matrix))
    kmeans_fit <- stats::kmeans(cluster_input_matrix, centers = k, nstart = 100, iter.max = 100)
    kmeans_sizes <- tibble::tibble(
      method = "kmeans",
      k = k,
      cluster = seq_along(kmeans_fit$size),
      cluster_size = as.integer(kmeans_fit$size)
    )

    dplyr::bind_rows(hierarchical_sizes, kmeans_sizes)
  })

  comparison_assignments <- purrr::map_dfr(config$comparison_k, \(k) {
    set.seed(20270618 + k + ncol(cluster_input_matrix))
    kmeans_fit <- stats::kmeans(cluster_input_matrix, centers = k, nstart = 100, iter.max = 100)

    tibble::tibble(
      cbsa_code = cluster_input_wide$cbsa_code,
      k = k,
      hierarchical_cluster = flatten_cutree(hclust_fit, k),
      kmeans_cluster = kmeans_fit$cluster
    )
  }) |>
    dplyr::left_join(
      character_model_df |>
        dplyr::select(cbsa_code, cbsa_name),
      by = "cbsa_code"
    )

  representative_metros <- purrr::map_dfr(config$comparison_k, \(k) {
    set.seed(20270618 + k + ncol(cluster_input_matrix))
    fit <- stats::kmeans(cluster_input_matrix, centers = k, nstart = 100, iter.max = 100)
    centers <- fit$centers
    assignments <- fit$cluster
    distance_to_center <- purrr::map_dbl(seq_len(nrow(cluster_input_matrix)), \(i) {
      center_row <- centers[assignments[i], , drop = TRUE]
      sqrt(sum((cluster_input_matrix[i, ] - center_row) ^ 2))
    })

    tibble::tibble(
      cbsa_code = row.names(cluster_input_matrix),
      k = k,
      kmeans_cluster = assignments,
      distance_to_center = distance_to_center
    ) |>
      dplyr::left_join(
        character_model_df |>
          dplyr::select(cbsa_code, cbsa_name),
        by = "cbsa_code"
      ) |>
      dplyr::group_by(k, kmeans_cluster) |>
      dplyr::arrange(distance_to_center, .by_group = TRUE) |>
      dplyr::slice_head(n = 8) |>
      dplyr::ungroup()
  })

  final_k <- config$final_k

  set.seed(20270618 + final_k + ncol(cluster_input_matrix))
  final_kmeans_fit <- stats::kmeans(
    cluster_input_matrix,
    centers = final_k,
    nstart = 100,
    iter.max = 100
  )

  final_gmm_fit <- fit_diagonal_gmm(
    x = cluster_input_matrix,
    k = final_k,
    init_clusters = final_kmeans_fit$cluster
  )

  final_cluster_assignments <- tibble::tibble(
    cbsa_code = cluster_input_wide$cbsa_code,
    character_hclust_cluster = flatten_cutree(hclust_fit, final_k),
    character_kmeans_cluster = final_kmeans_fit$cluster,
    character_gmm_cluster = final_gmm_fit$cluster
  )

  colnames(final_gmm_fit$responsibilities) <- paste0("character_prob_cluster_", seq_len(final_k))

  gmm_probabilities <- tibble::as_tibble(final_gmm_fit$responsibilities) |>
    dplyr::mutate(cbsa_code = cluster_input_wide$cbsa_code, .before = 1)

  gmm_cluster_summary <- gmm_probabilities |>
    dplyr::left_join(final_cluster_assignments, by = "cbsa_code") |>
    tidyr::pivot_longer(
      cols = dplyr::starts_with("character_prob_cluster_"),
      names_to = "probability_column",
      values_to = "membership_probability"
    ) |>
    dplyr::mutate(gmm_cluster = readr::parse_number(probability_column)) |>
    dplyr::group_by(gmm_cluster) |>
    dplyr::summarise(
      avg_membership_probability = mean(membership_probability),
      max_membership_probability = max(membership_probability),
      metros_as_top_membership = sum(gmm_cluster == character_gmm_cluster),
      .groups = "drop"
    )

  topic_scores_long <- modeling_long |>
    dplyr::group_by(cbsa_code, cbsa_name, topic_id) |>
    dplyr::summarise(topic_score = mean(scoring_z), .groups = "drop") |>
    dplyr::left_join(topic_weight_reference, by = "topic_id")

  subject_scores_long <- topic_scores_long |>
    dplyr::group_by(cbsa_code, cbsa_name, subject_id, subject_display_name, subject_weight) |>
    dplyr::summarise(
      subject_score = stats::weighted.mean(topic_score, topic_weight_within_subject),
      .groups = "drop"
    )

  frame_scores <- subject_scores_long |>
    dplyr::group_by(cbsa_code, cbsa_name) |>
    dplyr::summarise(
      character_score = stats::weighted.mean(subject_score, subject_weight),
      .groups = "drop"
    ) |>
    dplyr::mutate(character_percentile = dplyr::percent_rank(character_score) * 100)

  topic_scores_wide <- topic_scores_long |>
    dplyr::select(cbsa_code, topic_id, topic_score) |>
    tidyr::pivot_wider(names_from = topic_id, values_from = topic_score, names_prefix = "topic_score_")

  subject_scores_wide <- subject_scores_long |>
    dplyr::select(cbsa_code, subject_id, subject_score) |>
    tidyr::pivot_wider(names_from = subject_id, values_from = subject_score, names_prefix = "subject_score_")

  character_scores <- character_model_df |>
    dplyr::left_join(final_cluster_assignments, by = "cbsa_code") |>
    dplyr::left_join(gmm_probabilities, by = "cbsa_code") |>
    dplyr::left_join(topic_scores_wide, by = "cbsa_code") |>
    dplyr::left_join(subject_scores_wide, by = "cbsa_code") |>
    dplyr::left_join(frame_scores, by = c("cbsa_code", "cbsa_name"))

  subject_centroids <- character_scores |>
    dplyr::group_by(character_kmeans_cluster) |>
    dplyr::summarise(
      metros_in_cluster = dplyr::n(),
      dplyr::across(dplyr::starts_with("subject_score_"), mean),
      character_score = mean(character_score),
      character_percentile = mean(character_percentile),
      .groups = "drop"
    )

  metric_cluster_profile <- modeling_long |>
    dplyr::filter(metric_id %in% cluster_metric_ids) |>
    dplyr::select(cbsa_code, metric_id, scoring_z) |>
    dplyr::left_join(
      final_cluster_assignments |>
        dplyr::select(cbsa_code, character_kmeans_cluster),
      by = "cbsa_code"
    ) |>
    dplyr::group_by(character_kmeans_cluster, metric_id) |>
    dplyr::summarise(avg_metric_score = mean(scoring_z), .groups = "drop")

  cluster_metric_extremes <- dplyr::bind_rows(
    metric_cluster_profile |>
      dplyr::group_by(character_kmeans_cluster) |>
      dplyr::slice_max(avg_metric_score, n = 4, with_ties = FALSE) |>
      dplyr::mutate(extreme_direction = "top"),
    metric_cluster_profile |>
      dplyr::group_by(character_kmeans_cluster) |>
      dplyr::slice_min(avg_metric_score, n = 4, with_ties = FALSE) |>
      dplyr::mutate(extreme_direction = "bottom")
  ) |>
    dplyr::ungroup() |>
    dplyr::arrange(character_kmeans_cluster, extreme_direction, dplyr::desc(avg_metric_score))

  cluster_signature <- metric_cluster_profile |>
    tidyr::pivot_wider(names_from = metric_id, values_from = avg_metric_score)

  global_cluster <- cluster_signature |>
    dplyr::mutate(
      global_signature = pct_ba_plus + pop_weighted_density_sqmi + pct_foreign_born
    ) |>
    dplyr::slice_max(global_signature, n = 1, with_ties = FALSE) |>
    dplyr::pull(character_kmeans_cluster)

  retirement_cluster <- cluster_signature |>
    dplyr::filter(character_kmeans_cluster != global_cluster) |>
    dplyr::slice_max(pct_age_over_64, n = 1, with_ties = FALSE) |>
    dplyr::pull(character_kmeans_cluster)

  remaining_clusters <- cluster_signature |>
    dplyr::filter(!character_kmeans_cluster %in% c(global_cluster, retirement_cluster))

  college_cluster <- remaining_clusters |>
    dplyr::mutate(
      college_signature = pct_ba_plus + civic_engagement_volunteering_rate + nonprofits_per_100k
    ) |>
    dplyr::slice_max(college_signature, n = 1, with_ties = FALSE) |>
    dplyr::pull(character_kmeans_cluster)

  remaining_clusters <- remaining_clusters |>
    dplyr::filter(character_kmeans_cluster != college_cluster)

  southern_cluster <- remaining_clusters |>
    dplyr::slice_max(pct_black_nh, n = 1, with_ties = FALSE) |>
    dplyr::pull(character_kmeans_cluster)

  remaining_clusters <- remaining_clusters |>
    dplyr::filter(character_kmeans_cluster != southern_cluster)

  immigrant_growth_cluster <- remaining_clusters |>
    dplyr::mutate(
      immigrant_growth_signature = pct_hispanic + pct_foreign_born + pct_struct_multifam
    ) |>
    dplyr::slice_max(immigrant_growth_signature, n = 1, with_ties = FALSE) |>
    dplyr::pull(character_kmeans_cluster)

  remaining_clusters <- remaining_clusters |>
    dplyr::filter(character_kmeans_cluster != immigrant_growth_cluster)

  rooted_cluster <- remaining_clusters |>
    dplyr::mutate(
      rooted_signature = -(diversity_index + pct_foreign_born + pct_struct_multifam + pct_moved_diff_st)
    ) |>
    dplyr::slice_max(rooted_signature, n = 1, with_ties = FALSE) |>
    dplyr::pull(character_kmeans_cluster)

  interior_cluster <- remaining_clusters |>
    dplyr::filter(character_kmeans_cluster != rooted_cluster) |>
    dplyr::pull(character_kmeans_cluster)

  cluster_name_map <- tibble::tibble(
    character_kmeans_cluster = c(
      global_cluster,
      retirement_cluster,
      college_cluster,
      southern_cluster,
      immigrant_growth_cluster,
      rooted_cluster,
      interior_cluster
    ),
    character_cluster_name = c(
      "Global Knowledge Capitals",
      "Retirement And Lifestyle Havens",
      "College And Civic Anchors",
      "Established Community Anchors",
      "Immigrant Growth Corridors",
      "Rooted Heartland Centers",
      "Interior Family Opportunity Hubs"
    ),
    cluster_interpretation = c(
      "Large, globally connected metros with high education, density, and foreign-born shares.",
      "Older amenity-oriented metros with elevated retirement-age populations and lower civic-mobility churn.",
      "Highly educated, civic-rich, and institution-heavy college or state-capital style metros.",
      "More established community metros with higher Black population share, lower density, and stronger legacy civic-anchor structure than the broader interior family-growth cluster.",
      "Fast-changing and heavily Hispanic or immigrant-linked growth metros with denser multifamily form.",
      "More rooted interior metros with lower diversity, lower mobility, and comparatively stable built form.",
      "Broad interior metros with moderate education, family-market scale, and less extreme demographic signatures."
    )
  )

  character_scores <- character_scores |>
    dplyr::left_join(cluster_name_map, by = "character_kmeans_cluster")

  cluster_centroids_output <- subject_centroids |>
    dplyr::left_join(cluster_name_map, by = "character_kmeans_cluster")

  cluster_representatives <- representative_metros |>
    dplyr::filter(k == final_k) |>
    dplyr::transmute(
      character_kmeans_cluster = kmeans_cluster,
      cbsa_code,
      cbsa_name,
      distance_to_center
    ) |>
    dplyr::left_join(
      character_scores |>
        dplyr::select(cbsa_code, character_score, character_percentile),
      by = "cbsa_code"
    ) |>
    dplyr::left_join(cluster_name_map, by = "character_kmeans_cluster")

  gmm_hybrids <- character_scores |>
    dplyr::select(
      cbsa_code,
      cbsa_name,
      character_cluster_name,
      character_gmm_cluster,
      dplyr::starts_with("character_prob_cluster_")
    ) |>
    tidyr::pivot_longer(
      cols = dplyr::starts_with("character_prob_cluster_"),
      names_to = "probability_column",
      values_to = "membership_probability"
    ) |>
    dplyr::mutate(gmm_cluster = readr::parse_number(probability_column)) |>
    dplyr::arrange(cbsa_code, desc(membership_probability)) |>
    dplyr::group_by(cbsa_code, cbsa_name, character_cluster_name, character_gmm_cluster) |>
    dplyr::mutate(probability_rank = dplyr::row_number()) |>
    dplyr::filter(probability_rank <= 2) |>
    dplyr::summarise(
      top_gmm_cluster = dplyr::first(gmm_cluster),
      top_gmm_probability = dplyr::first(membership_probability),
      second_gmm_cluster = dplyr::nth(gmm_cluster, 2),
      second_gmm_probability = dplyr::nth(membership_probability, 2),
      membership_gap = top_gmm_probability - second_gmm_probability,
      .groups = "drop"
    ) |>
    dplyr::arrange(membership_gap)

  row_norms <- sqrt(rowSums(cluster_input_matrix ^ 2))
  row_norms[row_norms == 0] <- 1
  cosine_normalized <- cluster_input_matrix / row_norms
  cosine_similarity <- cosine_normalized %*% t(cosine_normalized)

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
      character_scores |>
        dplyr::select(cbsa_code, cbsa_name),
      by = "cbsa_code"
    ) |>
    dplyr::left_join(
      character_scores |>
        dplyr::select(peer_cbsa_code = cbsa_code, peer_cbsa_name = cbsa_name),
      by = "peer_cbsa_code"
    ) |>
    dplyr::select(cbsa_code, cbsa_name, peer_rank, peer_cbsa_code, peer_cbsa_name, cosine_similarity)

  list(
    topic_metadata = topic_metadata,
    selected_metric_metadata = selected_metric_metadata,
    topic_weight_reference = topic_weight_reference,
    modeling_long = modeling_long,
    standardization_audit = standardization_audit,
    cluster_metric_ids = cluster_metric_ids,
    cluster_input_wide = cluster_input_wide,
    cluster_input_matrix = cluster_input_matrix,
    cluster_count_calibration = cluster_count_calibration,
    cluster_count_sizes = cluster_count_sizes,
    cluster_assignments = comparison_assignments,
    representative_metros = representative_metros,
    final_cluster_assignments = final_cluster_assignments,
    gmm_probabilities = gmm_probabilities,
    gmm_cluster_summary = gmm_cluster_summary,
    cluster_name_map = cluster_name_map,
    metric_cluster_profile = metric_cluster_profile,
    cluster_metric_extremes = cluster_metric_extremes,
    character_scores = character_scores,
    cluster_centroids_output = cluster_centroids_output,
    cluster_representatives = cluster_representatives,
    gmm_hybrids = gmm_hybrids,
    similarity_top10 = similarity_top10
  )
}
