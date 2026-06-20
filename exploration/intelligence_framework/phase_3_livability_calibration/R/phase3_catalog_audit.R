build_phase3_catalog_bundle <- function(config) {
  catalog_text <- readr::read_file(here::here("foundations/semantic_layer/metric_catalog.yml"))
  metric_catalog <- yaml::yaml.load(catalog_text)$metrics |>
    purrr::map_dfr(\(metric) tibble::tibble(
      metric_id = metric$metric_id,
      source_table = metric$source_table %fallback% NA_character_,
      source_column = metric$source_column %fallback% NA_character_,
      status = metric$status %fallback% NA_character_
    ))

  intelligence_text <- readr::read_file(here::here("foundations/semantic_layer/intelligence_catalog.yml"))
  livability_frame <- yaml::yaml.load(intelligence_text)$frames |>
    purrr::keep(\(frame) identical(frame$frame_id, "livability")) |>
    purrr::pluck(1)

  intelligence_catalog <- livability_frame$subjects |>
    purrr::map_dfr(\(subject) {
      purrr::map_dfr(or_empty(subject$topics), \(topic) {
        purrr::map_dfr(or_empty(topic$kpis), \(kpi) {
          tibble::tibble(
            subject_id = subject$subject_id,
            topic_id = topic$topic_id,
            reliability = topic$reliability,
            metric_id = kpi$metric_id,
            polarity = kpi$polarity,
            model_role = kpi$model_role
          )
        })
      })
    })

  catalog_check <- config$expected_kpis |>
    dplyr::left_join(metric_catalog, by = "metric_id") |>
    dplyr::left_join(
      intelligence_catalog |>
        dplyr::select(metric_id, subject_id, topic_id, reliability, polarity, model_role),
      by = "metric_id"
    ) |>
    dplyr::mutate(
      in_metric_catalog = !is.na(source_table),
      in_intelligence_catalog = !is.na(subject_id),
      source_column_matches = is.na(source_column) | source_column == expected_source_column
    ) |>
    dplyr::arrange(audit_bucket, metric_id)

  polarity_audit <- catalog_check |>
    dplyr::transmute(
      metric_id,
      subject_id,
      topic_id,
      polarity,
      model_role,
      polarity_present = !is.na(polarity)
    ) |>
    dplyr::arrange(subject_id, topic_id, metric_id)

  list(
    metric_catalog = metric_catalog,
    livability_frame = livability_frame,
    intelligence_catalog = intelligence_catalog,
    catalog_check = catalog_check,
    polarity_audit = polarity_audit
  )
}
