build_phase4_model_bundle <- function(opportunity_model_df, opportunity_frame, catalog_check, config) {
  topic_metadata <- opportunity_frame$subjects |>
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
      reliability_factor = dplyr::case_when(
        reliability == "core" ~ 1.00,
        reliability == "supplemental_baseline" ~ 0.75,
        reliability == "coverage_caution" ~ 0.60,
        TRUE ~ 1.00
      ),
      raw_topic_weight = coverage * reliability_factor
    ) |>
    dplyr::group_by(subject_id) |>
    dplyr::mutate(topic_weight_within_subject = raw_topic_weight / sum(raw_topic_weight)) |>
    dplyr::ungroup()

  modeling_long <- opportunity_model_df |>
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
      opportunity_model_df |>
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
      opportunity_score = stats::weighted.mean(subject_score, subject_weight),
      .groups = "drop"
    ) |>
    dplyr::mutate(opportunity_percentile = dplyr::percent_rank(opportunity_score) * 100)

  topic_scores_wide <- topic_scores_long |>
    dplyr::select(cbsa_code, topic_id, topic_score) |>
    tidyr::pivot_wider(names_from = topic_id, values_from = topic_score, names_prefix = "topic_score_")

  subject_scores_wide <- subject_scores_long |>
    dplyr::select(cbsa_code, subject_id, subject_score) |>
    tidyr::pivot_wider(names_from = subject_id, values_from = subject_score, names_prefix = "subject_score_")

  frame_only_scores <- opportunity_model_df |>
    dplyr::left_join(topic_scores_wide, by = "cbsa_code") |>
    dplyr::left_join(subject_scores_wide, by = "cbsa_code") |>
    dplyr::left_join(frame_scores, by = c("cbsa_code", "cbsa_name"))

  comparison_summary <- purrr::map_dfr(config$comparison_k, \(k) {
    h_clusters <- stats::cutree(hclust_fit, k = k)
    h_sizes <- as.integer(table(h_clusters))
    h_silhouette <- cluster::silhouette(h_clusters, cluster_distance)

    set.seed(20270618 + k + ncol(cluster_input_matrix))
    kmeans_fit <- stats::kmeans(cluster_input_matrix, centers = k, nstart = 100, iter.max = 100)
    k_sizes <- as.integer(kmeans_fit$size)
    k_silhouette <- cluster::silhouette(kmeans_fit$cluster, cluster_distance)

    tibble::tibble(
      k = k,
      metric_set = "reduced_kpi_set",
      metric_count = length(cluster_metric_ids),
      hierarchical_avg_silhouette = mean(h_silhouette[, 3]),
      kmeans_avg_silhouette = mean(k_silhouette[, 3]),
      hierarchical_min_cluster = min(h_sizes),
      hierarchical_max_cluster = max(h_sizes),
      kmeans_min_cluster = min(k_sizes),
      kmeans_max_cluster = max(k_sizes),
      hierarchical_clusters_under_10 = sum(h_sizes < 10),
      kmeans_clusters_under_10 = sum(k_sizes < 10)
    )
  })

  comparison_sizes <- purrr::map_dfr(config$comparison_k, \(k) {
    h_clusters <- stats::cutree(hclust_fit, k = k)
    h_sizes <- tibble::tibble(
      method = "hierarchical",
      k = k,
      cluster = seq_along(table(h_clusters)),
      cluster_size = as.integer(table(h_clusters))
    )

    set.seed(20270618 + k + ncol(cluster_input_matrix))
    kmeans_fit <- stats::kmeans(cluster_input_matrix, centers = k, nstart = 100, iter.max = 100)
    k_sizes <- tibble::tibble(
      method = "kmeans",
      k = k,
      cluster = seq_along(kmeans_fit$size),
      cluster_size = as.integer(kmeans_fit$size)
    )

    dplyr::bind_rows(h_sizes, k_sizes)
  })

  comparison_assignments <- purrr::map_dfr(config$comparison_k, \(k) {
    set.seed(20270618 + k + ncol(cluster_input_matrix))
    kmeans_fit <- stats::kmeans(cluster_input_matrix, centers = k, nstart = 100, iter.max = 100)
    hierarchical_clusters <- as.integer(stats::cutree(hclust_fit, k = k))

    tibble::tibble(
      cbsa_code = cluster_input_wide$cbsa_code,
      k = k,
      hierarchical_cluster = hierarchical_clusters,
      kmeans_cluster = kmeans_fit$cluster
    )
  }) |>
    dplyr::left_join(
      frame_only_scores |>
        dplyr::select(cbsa_code, cbsa_name, opportunity_score, opportunity_percentile, dplyr::starts_with("subject_score_")),
      by = "cbsa_code"
    )

  comparison_centroids <- purrr::map_dfr(config$comparison_k, \(k) {
    comparison_assignments |>
      dplyr::filter(k == !!k) |>
      dplyr::group_by(k, kmeans_cluster) |>
      dplyr::summarise(
        metros_in_cluster = dplyr::n(),
        opportunity_score = mean(opportunity_score),
        opportunity_percentile = mean(opportunity_percentile),
        dplyr::across(dplyr::starts_with("subject_score_"), mean),
        .groups = "drop"
      ) |>
      dplyr::mutate(metric_set = "reduced_kpi_set", .before = 1)
  })

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
        frame_only_scores |>
          dplyr::select(cbsa_code, cbsa_name, opportunity_percentile, opportunity_score),
        by = "cbsa_code"
      ) |>
      dplyr::group_by(k, kmeans_cluster) |>
      dplyr::arrange(distance_to_center, .by_group = TRUE) |>
      dplyr::slice_head(n = 8) |>
      dplyr::ungroup() |>
      dplyr::mutate(metric_set = "reduced_kpi_set", .before = 1)
  })

  split_summary <- comparison_assignments |>
    dplyr::filter(k %in% c(5, 6)) |>
    dplyr::select(cbsa_code, cbsa_name, k, kmeans_cluster) |>
    tidyr::pivot_wider(names_from = k, values_from = kmeans_cluster, names_prefix = "k") |>
    dplyr::count(k5, k6, name = "metros_in_split") |>
    dplyr::arrange(k5, k6)

  k6_majority_crosswalk <- split_summary |>
    dplyr::group_by(k6) |>
    dplyr::slice_max(order_by = metros_in_split, n = 1, with_ties = FALSE) |>
    dplyr::ungroup() |>
    dplyr::select(k6, majority_k5 = k5)

  changed_metros_k5_k6 <- comparison_assignments |>
    dplyr::filter(k %in% c(5, 6)) |>
    dplyr::select(cbsa_code, cbsa_name, opportunity_score, opportunity_percentile, k, kmeans_cluster) |>
    tidyr::pivot_wider(names_from = k, values_from = kmeans_cluster, names_prefix = "k") |>
    dplyr::left_join(k6_majority_crosswalk, by = "k6") |>
    dplyr::mutate(changed_under_k6 = k5 != majority_k5) |>
    dplyr::arrange(dplyr::desc(changed_under_k6), k5, k6, cbsa_name)

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
    opportunity_hclust_cluster = as.integer(stats::cutree(hclust_fit, k = final_k)),
    opportunity_kmeans_cluster = final_kmeans_fit$cluster,
    opportunity_gmm_cluster = final_gmm_fit$cluster
  )

  colnames(final_gmm_fit$responsibilities) <- paste0("opportunity_prob_cluster_", seq_len(final_k))

  gmm_probabilities <- tibble::as_tibble(final_gmm_fit$responsibilities) |>
    dplyr::mutate(cbsa_code = cluster_input_wide$cbsa_code, .before = 1)

  gmm_cluster_summary <- gmm_probabilities |>
    dplyr::left_join(final_cluster_assignments, by = "cbsa_code") |>
    tidyr::pivot_longer(
      cols = dplyr::starts_with("opportunity_prob_cluster_"),
      names_to = "probability_column",
      values_to = "membership_probability"
    ) |>
    dplyr::mutate(gmm_cluster = readr::parse_number(probability_column)) |>
    dplyr::group_by(gmm_cluster) |>
    dplyr::summarise(
      avg_membership_probability = mean(membership_probability),
      max_membership_probability = max(membership_probability),
      metros_as_top_membership = sum(gmm_cluster == opportunity_gmm_cluster),
      .groups = "drop"
    )

  opportunity_scores <- frame_only_scores |>
    dplyr::left_join(final_cluster_assignments, by = "cbsa_code") |>
    dplyr::left_join(gmm_probabilities, by = "cbsa_code")

  subject_centroids <- opportunity_scores |>
    dplyr::group_by(opportunity_kmeans_cluster) |>
    dplyr::summarise(
      metros_in_cluster = dplyr::n(),
      dplyr::across(dplyr::starts_with("subject_score_"), mean),
      opportunity_score = mean(opportunity_score),
      opportunity_percentile = mean(opportunity_percentile),
      .groups = "drop"
    )

  metric_cluster_profile <- modeling_long |>
    dplyr::filter(metric_id %in% cluster_metric_ids) |>
    dplyr::select(cbsa_code, metric_id, scoring_z) |>
    dplyr::left_join(
      final_cluster_assignments |>
        dplyr::select(cbsa_code, opportunity_kmeans_cluster),
      by = "cbsa_code"
    ) |>
    dplyr::group_by(opportunity_kmeans_cluster, metric_id) |>
    dplyr::summarise(avg_metric_score = mean(scoring_z), .groups = "drop")

  cluster_metric_extremes <- dplyr::bind_rows(
    metric_cluster_profile |>
      dplyr::group_by(opportunity_kmeans_cluster) |>
      dplyr::slice_max(avg_metric_score, n = 4, with_ties = FALSE) |>
      dplyr::mutate(extreme_direction = "top"),
    metric_cluster_profile |>
      dplyr::group_by(opportunity_kmeans_cluster) |>
      dplyr::slice_min(avg_metric_score, n = 4, with_ties = FALSE) |>
      dplyr::mutate(extreme_direction = "bottom")
  ) |>
    dplyr::ungroup() |>
    dplyr::arrange(opportunity_kmeans_cluster, extreme_direction, dplyr::desc(avg_metric_score))

  subject_lookup <- topic_metadata |>
    dplyr::distinct(subject_id, subject_display_name)

  cluster_labels <- subject_centroids |>
    tidyr::pivot_longer(
      cols = dplyr::starts_with("subject_score_"),
      names_to = "subject_column",
      values_to = "subject_score"
    ) |>
    dplyr::mutate(subject_id = stringr::str_remove(subject_column, "^subject_score_")) |>
    dplyr::left_join(subject_lookup, by = "subject_id") |>
    dplyr::group_by(opportunity_kmeans_cluster) |>
    dplyr::summarise(
      top_subject = subject_display_name[which.max(subject_score)],
      bottom_subject = subject_display_name[which.min(subject_score)],
      opportunity_cluster_label = paste0(
        "Type ",
        dplyr::first(opportunity_kmeans_cluster),
        ": ",
        top_subject,
        " strength, ",
        bottom_subject,
        " drag"
      ),
      .groups = "drop"
    )

  # K-means cluster IDs can reshuffle across reruns, so assign published
  # Opportunity names from the observed centroid and metric pattern rather
  # than from the raw numeric label.
  elite_cluster <- subject_centroids |>
    dplyr::slice_max(opportunity_score, n = 1, with_ties = FALSE) |>
    dplyr::pull(opportunity_kmeans_cluster)

  distressed_cluster <- subject_centroids |>
    dplyr::slice_min(opportunity_score, n = 1, with_ties = FALSE) |>
    dplyr::pull(opportunity_kmeans_cluster)

  remaining_clusters <- subject_centroids |>
    dplyr::filter(!opportunity_kmeans_cluster %in% c(elite_cluster, distressed_cluster))

  growth_cluster <- remaining_clusters |>
    dplyr::slice_max(subject_score_market_opportunity, n = 1, with_ties = FALSE) |>
    dplyr::pull(opportunity_kmeans_cluster)

  remaining_clusters <- remaining_clusters |>
    dplyr::filter(opportunity_kmeans_cluster != growth_cluster)

  balanced_cluster <- remaining_clusters |>
    dplyr::slice_max(opportunity_score, n = 1, with_ties = FALSE) |>
    dplyr::pull(opportunity_kmeans_cluster)

  remaining_clusters <- remaining_clusters |>
    dplyr::filter(opportunity_kmeans_cluster != balanced_cluster)

  industrial_value_cluster <- metric_cluster_profile |>
    dplyr::filter(
      opportunity_kmeans_cluster %in% remaining_clusters$opportunity_kmeans_cluster,
      metric_id == "lq_manufacturing"
    ) |>
    dplyr::slice_max(avg_metric_score, n = 1, with_ties = FALSE) |>
    dplyr::pull(opportunity_kmeans_cluster)

  transition_cluster <- remaining_clusters |>
    dplyr::filter(opportunity_kmeans_cluster != industrial_value_cluster) |>
    dplyr::pull(opportunity_kmeans_cluster)

  cluster_name_map <- tibble::tibble(
    opportunity_kmeans_cluster = c(
      elite_cluster,
      growth_cluster,
      balanced_cluster,
      industrial_value_cluster,
      transition_cluster,
      distressed_cluster
    ),
    opportunity_cluster_name = c(
      "Superstar Knowledge Capitals",
      "Broad-Based Opportunity Hubs",
      "Emerging Momentum Markets",
      "Industrial Rebound Markets",
      "Uneven Transition Markets",
      "Thin-Base Distressed Markets"
    ),
    cluster_interpretation = c(
      "High-wage, knowledge-heavy metros with elite business depth and strong overall opportunity despite thinner near-term housing appreciation.",
      "Diversified metros with above-average scores across resident, market, and business dimensions rather than one extreme advantage.",
      "Fast-growing and upward-moving markets with strong population, income, and business-formation momentum.",
      "Manufacturing-leaning and legacy-oriented markets where industrial specialization and housing rebound are relative strengths, even as knowledge and human-capital signals run weaker.",
      "Markets showing selective migration and business-formation upside while labor-market tightness, housing appreciation, and resident fundamentals remain uneven.",
      "Small and mid-sized markets with the weakest business-base depth and below-average resident opportunity, even when a few short-run market signals hold up."
    )
  )

  opportunity_scores <- opportunity_scores |>
    dplyr::left_join(cluster_labels, by = "opportunity_kmeans_cluster") |>
    dplyr::left_join(cluster_name_map, by = "opportunity_kmeans_cluster")

  changed_metros_k5_k6 <- changed_metros_k5_k6 |>
    dplyr::left_join(
      opportunity_scores |>
        dplyr::select(cbsa_code, cbsa_name, opportunity_score, opportunity_percentile),
      by = c("cbsa_code", "cbsa_name", "opportunity_score", "opportunity_percentile")
    )

  cluster_centroids_output <- subject_centroids |>
    dplyr::left_join(cluster_labels, by = "opportunity_kmeans_cluster") |>
    dplyr::left_join(cluster_name_map, by = "opportunity_kmeans_cluster")

  cluster_representatives <- representative_metros |>
    dplyr::filter(k == final_k) |>
    dplyr::transmute(
      opportunity_kmeans_cluster = kmeans_cluster,
      cbsa_code,
      cbsa_name,
      distance_to_center,
      opportunity_score,
      opportunity_percentile
    ) |>
    dplyr::left_join(cluster_name_map, by = "opportunity_kmeans_cluster")

  gmm_hybrids <- opportunity_scores |>
    dplyr::select(
      cbsa_code,
      cbsa_name,
      opportunity_cluster_name,
      opportunity_gmm_cluster,
      dplyr::starts_with("opportunity_prob_cluster_")
    ) |>
    tidyr::pivot_longer(
      cols = dplyr::starts_with("opportunity_prob_cluster_"),
      names_to = "probability_column",
      values_to = "membership_probability"
    ) |>
    dplyr::mutate(gmm_cluster = readr::parse_number(probability_column)) |>
    dplyr::arrange(cbsa_code, desc(membership_probability)) |>
    dplyr::group_by(cbsa_code, cbsa_name, opportunity_cluster_name, opportunity_gmm_cluster) |>
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
      opportunity_scores |>
        dplyr::select(cbsa_code, cbsa_name),
      by = "cbsa_code"
    ) |>
    dplyr::left_join(
      opportunity_scores |>
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
    cluster_input_wide = cluster_input_wide,
    cluster_input_matrix = cluster_input_matrix,
    comparison_summary = comparison_summary,
    comparison_sizes = comparison_sizes,
    cluster_assignments = comparison_assignments,
    cluster_centroids = comparison_centroids,
    representative_metros = representative_metros,
    split_summary = split_summary,
    changed_metros_k5_k6 = changed_metros_k5_k6,
    cluster_name_map = cluster_name_map,
    metric_cluster_profile = metric_cluster_profile,
    cluster_metric_extremes = cluster_metric_extremes,
    final_cluster_assignments = final_cluster_assignments,
    gmm_probabilities = gmm_probabilities,
    gmm_cluster_summary = gmm_cluster_summary,
    opportunity_scores = opportunity_scores,
    cluster_centroids_output = cluster_centroids_output,
    cluster_representatives = cluster_representatives,
    gmm_hybrids = gmm_hybrids,
    similarity_top10 = similarity_top10
  )
}
