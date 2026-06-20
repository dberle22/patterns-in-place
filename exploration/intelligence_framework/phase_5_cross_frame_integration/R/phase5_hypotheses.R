build_phase5_hypothesis_bundle <- function(cross_frame_scores) {
  frame_alignment_scatter <- cross_frame_scores |>
    dplyr::transmute(
      cbsa_code,
      cbsa_name,
      cross_frame_cluster_name,
      cross_frame_percentile,
      character_percentile = character__character_percentile,
      livability_percentile = livability__livability_percentile,
      opportunity_percentile = opportunity__opportunity_percentile
    ) |>
    dplyr::mutate(
      character_livability_gap = character_percentile - livability_percentile,
      character_opportunity_gap = character_percentile - opportunity_percentile,
      livability_opportunity_gap = livability_percentile - opportunity_percentile,
      absolute_gap_sum =
        abs(character_livability_gap) +
        abs(character_opportunity_gap) +
        abs(livability_opportunity_gap)
    )

  frame_alignment_summary <- tibble::tibble(
    character_livability_correlation = cor(
      frame_alignment_scatter$character_percentile,
      frame_alignment_scatter$livability_percentile
    ),
    character_opportunity_correlation = cor(
      frame_alignment_scatter$character_percentile,
      frame_alignment_scatter$opportunity_percentile
    ),
    livability_opportunity_correlation = cor(
      frame_alignment_scatter$livability_percentile,
      frame_alignment_scatter$opportunity_percentile
    ),
    mean_absolute_gap_sum = mean(frame_alignment_scatter$absolute_gap_sum),
    metros_with_very_large_gap_sum = sum(frame_alignment_scatter$absolute_gap_sum >= 100)
  )

  frame_alignment_outliers <- frame_alignment_scatter |>
    dplyr::arrange(dplyr::desc(absolute_gap_sum), cbsa_name) |>
    dplyr::slice_head(n = 25)

  candidate_list <- frame_alignment_scatter |>
    dplyr::transmute(
      cbsa_code,
      cbsa_name,
      cross_frame_cluster_name,
      cross_frame_percentile,
      character_percentile,
      livability_percentile,
      opportunity_percentile,
      absolute_gap_sum
    ) |>
    dplyr::left_join(
      cross_frame_scores |>
        dplyr::select(
          cbsa_code,
          hybrid_membership_gap,
          distance_to_center,
          nearest_peer_1 = peer_1_name
        ),
      by = "cbsa_code"
    ) |>
    dplyr::mutate(
      gap_rank = dplyr::percent_rank(absolute_gap_sum) * 100,
      hybrid_rank = dplyr::percent_rank(dplyr::desc(hybrid_membership_gap)) * 100,
      outlier_rank = dplyr::percent_rank(distance_to_center) * 100,
      candidate_score_method = "cross_frame_divergence_heuristic",
      candidate_score_interpretation = "Higher means a metro is more useful for reviewing cross-frame tension, hybrid membership, and distance from its assigned combined cluster; it is not a general market quality score.",
      divergence_candidate_score = 0.5 * gap_rank + 0.25 * hybrid_rank + 0.25 * outlier_rank
    ) |>
    dplyr::arrange(dplyr::desc(divergence_candidate_score), dplyr::desc(absolute_gap_sum), cbsa_name) |>
    dplyr::mutate(divergence_candidate_rank = dplyr::row_number())

  list(
    frame_alignment_scatter = frame_alignment_scatter,
    frame_alignment_summary = frame_alignment_summary,
    frame_alignment_outliers = frame_alignment_outliers,
    candidate_list = candidate_list
  )
}
