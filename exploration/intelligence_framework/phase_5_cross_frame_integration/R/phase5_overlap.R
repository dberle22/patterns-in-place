build_phase5_overlap_bundle <- function(cross_frame_scores) {
  overlap_flags <- cross_frame_scores |>
    dplyr::transmute(
      cbsa_code,
      cbsa_name,
      cross_frame_cluster_name,
      cross_frame_score,
      cross_frame_percentile,
      character_percentile = character__character_percentile,
      livability_percentile = livability__livability_percentile,
      opportunity_percentile = opportunity__opportunity_percentile
    ) |>
    tidyr::pivot_longer(
      cols = c(character_percentile, livability_percentile, opportunity_percentile),
      names_to = "frame_percentile_column",
      values_to = "frame_percentile"
    ) |>
    dplyr::mutate(frame_id = stringr::str_remove(frame_percentile_column, "_percentile$")) |>
    dplyr::group_by(cbsa_code, cbsa_name, cross_frame_cluster_name, cross_frame_score, cross_frame_percentile) |>
    dplyr::summarise(
      top_frame = frame_id[which.max(frame_percentile)],
      top_frame_percentile = max(frame_percentile),
      bottom_frame = frame_id[which.min(frame_percentile)],
      bottom_frame_percentile = min(frame_percentile),
      frame_percentile_gap = max(frame_percentile) - min(frame_percentile),
      frame_percentile_sd = stats::sd(frame_percentile),
      mean_frame_percentile = mean(frame_percentile),
      same_top_half_all_frames = all(frame_percentile >= 50),
      same_bottom_half_all_frames = all(frame_percentile < 50),
      .groups = "drop"
    ) |>
    dplyr::mutate(
      overlap_profile = dplyr::case_when(
        frame_percentile_gap >= 50 ~ "highly_divergent",
        frame_percentile_gap >= 30 ~ "divergent",
        frame_percentile_gap >= 15 ~ "mixed",
        TRUE ~ "coherent"
      ),
      half_alignment = dplyr::case_when(
        same_top_half_all_frames ~ "all_top_half",
        same_bottom_half_all_frames ~ "all_bottom_half",
        TRUE ~ "split_halves"
      ),
      signature = paste0(top_frame, "_over_", bottom_frame)
    ) |>
    dplyr::arrange(dplyr::desc(frame_percentile_gap), dplyr::desc(frame_percentile_sd), cbsa_name)

  overlap_summary <- overlap_flags |>
    dplyr::count(overlap_profile, half_alignment, signature, name = "metros") |>
    dplyr::arrange(dplyr::desc(metros), overlap_profile, signature)

  cluster_overlap_summary <- overlap_flags |>
    dplyr::group_by(cross_frame_cluster_name) |>
    dplyr::summarise(
      metros = dplyr::n(),
      avg_cross_frame_percentile = mean(cross_frame_percentile),
      avg_frame_gap = mean(frame_percentile_gap),
      median_frame_gap = stats::median(frame_percentile_gap),
      highly_divergent_metros = sum(overlap_profile == "highly_divergent"),
      divergent_metros = sum(overlap_profile %in% c("highly_divergent", "divergent")),
      .groups = "drop"
    ) |>
    dplyr::arrange(dplyr::desc(avg_frame_gap), dplyr::desc(avg_cross_frame_percentile))

  list(
    overlap_flags = overlap_flags,
    overlap_summary = overlap_summary,
    cluster_overlap_summary = cluster_overlap_summary
  )
}
