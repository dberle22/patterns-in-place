build_phase5_reference_spine <- function(con, config) {
  spine <- DBI::dbGetQuery(
    con,
    glue::glue(
      "
      select
        geo_id as cbsa_code,
        geo_name as cbsa_name,
        pop_total,
        year as spine_year
      from gold.population_demographics
      where geo_level = 'cbsa'
        and year = {config$target_year}
        and pop_total >= {config$min_pop}
        and geo_name not like '%, PR'
      order by pop_total desc
      "
    )
  )

  stopifnot(nrow(spine) == config$reference_spine_size)
  spine
}

build_phase5_input_audit_bundle <- function(con, config) {
  spine <- build_phase5_reference_spine(con, config)

  frame_artifacts <- purrr::pmap(
    config$frames,
    function(frame_id, score_path, decision_path, frame_priority) {
      scores <- arrow::read_parquet(score_path)
      decisions <- readr::read_csv(decision_path, show_col_types = FALSE) |>
        dplyr::filter(use_for_clustering) |>
        dplyr::mutate(
          frame_id = frame_id,
          frame_priority = frame_priority,
          feature_id = paste(frame_id, metric_id, sep = "__"),
          imputed_column = paste0("imputed_", metric_id),
          scored_column = paste0("scored_", metric_id)
        )

      missing_imputed_cols <- setdiff(decisions$imputed_column, names(scores))
      if (length(missing_imputed_cols) > 0) {
        stop(
          sprintf(
            "Phase 5 input audit is missing expected imputed columns for %s: %s",
            frame_id,
            paste(missing_imputed_cols, collapse = ", ")
          ),
          call. = FALSE
        )
      }

      context_cols <- names(scores)[
        grepl(
          "(_score$|_percentile$|_cluster_(name|label)$|_prob_cluster_|^topic_score_|^subject_score_|^cluster_interpretation$|^top_subject$|^bottom_subject$)",
          names(scores)
        )
      ]

      list(
        frame_id = frame_id,
        frame_priority = frame_priority,
        scores = scores,
        decisions = decisions,
        context_cols = unique(context_cols)
      )
    }
  )

  names(frame_artifacts) <- config$frames$frame_id

  frame_coverage <- purrr::map_dfr(frame_artifacts, \(artifact) {
    scores <- artifact$scores
    tibble::tibble(
      frame_id = artifact$frame_id,
      spine_rows = nrow(spine),
      score_rows = nrow(scores),
      unique_cbsa_codes = dplyr::n_distinct(scores$cbsa_code),
      missing_from_spine = nrow(dplyr::anti_join(scores, spine, by = "cbsa_code")),
      missing_from_scores = nrow(dplyr::anti_join(spine, scores, by = "cbsa_code")),
      kept_metric_count = nrow(artifact$decisions)
    )
  })

  missing_from_scores <- purrr::map_dfr(frame_artifacts, \(artifact) {
    dplyr::anti_join(spine, artifact$scores, by = "cbsa_code") |>
      dplyr::transmute(
        frame_id = artifact$frame_id,
        cbsa_code,
        cbsa_name,
        pop_total
      )
  })

  feature_spec <- purrr::map_dfr(frame_artifacts, "decisions") |>
    dplyr::select(
      frame_id,
      frame_priority,
      feature_id,
      metric_id,
      imputed_column,
      scored_column,
      decision_reason
    )

  model_inputs <- purrr::map(frame_artifacts, \(artifact) {
    artifact$scores |>
      dplyr::select(
        cbsa_code,
        cbsa_name,
        pop_total,
        dplyr::all_of(artifact$decisions$imputed_column)
      ) |>
      dplyr::rename_with(
        .fn = \(x) {
          renamed <- artifact$decisions$feature_id[
            match(x, artifact$decisions$imputed_column)
          ]
          dplyr::coalesce(renamed, x)
        },
        .cols = dplyr::all_of(artifact$decisions$imputed_column)
      )
  })

  combined_model_df <- purrr::reduce(
    .x = model_inputs,
    .f = \(x, y) dplyr::left_join(x, y, by = c("cbsa_code", "cbsa_name", "pop_total")),
    .init = spine |>
      dplyr::select(cbsa_code, cbsa_name, pop_total, spine_year)
  )

  context_bundle <- purrr::imap(frame_artifacts, \(artifact, frame_name) {
    artifact$scores |>
      dplyr::select(cbsa_code, cbsa_name, dplyr::all_of(artifact$context_cols)) |>
      dplyr::rename_with(
        .fn = \(x) ifelse(
          x %in% c("cbsa_code", "cbsa_name"),
          x,
          paste(frame_name, x, sep = "__")
        )
      )
  }) |>
    purrr::reduce(\(x, y) dplyr::left_join(x, y, by = c("cbsa_code", "cbsa_name")))

  stopifnot(nrow(combined_model_df) == config$reference_spine_size)

  list(
    spine = spine,
    frame_coverage = frame_coverage,
    missing_from_scores = missing_from_scores,
    feature_spec = feature_spec,
    combined_model_df = combined_model_df,
    context_bundle = context_bundle
  )
}
