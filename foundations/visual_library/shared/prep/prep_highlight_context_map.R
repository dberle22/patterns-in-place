# Prepare highlight-context map data.

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

prep_highlight_context_map <- function(data, config = list()) {
  cfg <- merge_chart_config(
    list(
      question_id = NULL,
      time_window = NULL,
      geo_ids = NULL,
      group_values = NULL,
      value_field = NULL,
      benchmark_field = "benchmark_value",
      variant = c("focus_only", "continuous", "binned", "diverging"),
      require_single_geo_level = TRUE,
      require_single_time_window = FALSE,
      require_highlight = TRUE,
      drop_missing_metric = FALSE,
      crs = 4326
    ),
    config
  )
  cfg$variant <- match.arg(cfg$variant, c("focus_only", "continuous", "binned", "diverging"))

  required <- visual_contracts$highlight_context_map$required_fields
  if (!is.null(cfg$value_field) && cfg$value_field %in% names(data)) {
    required <- unique(c(required, cfg$value_field))
  }
  if (!is.null(cfg$benchmark_field) && cfg$benchmark_field %in% names(data)) {
    required <- unique(c(required, cfg$benchmark_field))
  }

  validate_highlight_context_map_contract(data)
  out <- prepare_long_metric_frame(
    data,
    required = required,
    value_columns = c("metric_value", "benchmark_value"),
    chart_type = "highlight_context_map",
    config = cfg
  )

  if (!is.null(cfg$question_id) && "question_id" %in% names(out)) {
    out <- out[out$question_id == cfg$question_id, , drop = FALSE]
  }
  if (!is.null(cfg$time_window) && "time_window" %in% names(out)) {
    out <- out[out$time_window == cfg$time_window, , drop = FALSE]
  }
  if (!is.null(cfg$geo_ids)) {
    out <- out[out$geo_id %in% cfg$geo_ids, , drop = FALSE]
  }
  if (!is.null(cfg$group_values) && "group" %in% names(out)) {
    out <- out[out$group %in% cfg$group_values, , drop = FALSE]
  }

  validation <- validate_highlight_context_map_contract(
    out,
    require_single_geo_level = isTRUE(cfg$require_single_geo_level),
    require_single_time_window = isTRUE(cfg$require_single_time_window),
    require_non_empty = TRUE
  )
  if (!isTRUE(validation$pass)) {
    stop("Highlight + context prep filters produced a contract-invalid dataset.")
  }

  out$highlight_flag <- coerce_logical_column(out$highlight_flag)
  if ("neighbor_flag" %in% names(out)) {
    out$neighbor_flag <- coerce_logical_column(out$neighbor_flag)
  } else {
    out$neighbor_flag <- FALSE
  }
  if ("label_flag" %in% names(out)) {
    out$label_flag <- coerce_logical_column(out$label_flag)
  }

  if (!is.null(cfg$value_field) && cfg$value_field %in% names(out)) {
    out$metric_value <- suppressWarnings(as.numeric(out[[cfg$value_field]]))
  }
  if (!is.null(cfg$benchmark_field) && cfg$benchmark_field %in% names(out)) {
    out$benchmark_value <- suppressWarnings(as.numeric(out[[cfg$benchmark_field]]))
  }

  if (isTRUE(cfg$drop_missing_metric) && "metric_value" %in% names(out)) {
    out <- out[is.finite(out$metric_value), , drop = FALSE]
  }

  if ("geom_wkt" %in% names(out) && requireNamespace("sf", quietly = TRUE)) {
    out <- sf::st_as_sf(out, wkt = "geom_wkt", crs = cfg$crs)
  } else if ("geometry" %in% names(out) &&
             !inherits(out, "sf") &&
             requireNamespace("sf", quietly = TRUE)) {
    out <- sf::st_as_sf(out, sf_column_name = "geometry", crs = cfg$crs)
  }

  if ("geom_wkt" %in% names(out) && inherits(out, "sf")) {
    names(out)[names(out) == attr(out, "sf_column")] <- "geometry"
    attr(out, "sf_column") <- "geometry"
  }

  out$fill_value <- if ("metric_value" %in% names(out)) out$metric_value else NA_real_
  if (identical(cfg$variant, "diverging") && "benchmark_value" %in% names(out)) {
    out$fill_value <- out$metric_value - out$benchmark_value
  }

  if (identical(cfg$variant, "focus_only")) {
    out$focus_role <- ifelse(
      out$highlight_flag %in% TRUE,
      "Highlighted geography",
      ifelse(out$neighbor_flag %in% TRUE, "Neighbor context", "Background context")
    )
  } else {
    out$outline_role <- ifelse(
      out$highlight_flag %in% TRUE,
      "Highlighted geography",
      ifelse(out$neighbor_flag %in% TRUE, "Neighbor context", NA_character_)
    )
  }

  if (isTRUE(cfg$require_highlight) && !any(out$highlight_flag %in% TRUE, na.rm = TRUE)) {
    stop("Highlight + context maps require at least one highlighted geography.")
  }

  if (nrow(out) == 0) {
    stop("No rows left after highlight + context prep filtering; adjust config.")
  }

  out
}
