# Prepare choropleth data.

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

prep_choropleth <- function(data, config = list()) {
  cfg <- merge_chart_config(
    list(
      question_id = NULL,
      time_window = NULL,
      geo_ids = NULL,
      group_values = NULL,
      metric_id = NULL,
      value_field = NULL,
      benchmark_field = "benchmark_value",
      bins = NULL,
      bin_labels = NULL,
      bin_style = c("quantile", "fixed"),
      variant = c("continuous", "binned", "diverging"),
      require_single_geo_level = TRUE,
      require_single_time_window = FALSE,
      drop_missing_metric = FALSE,
      crs = 4326
    ),
    config
  )
  cfg$variant <- match.arg(cfg$variant, c("continuous", "binned", "diverging"))
  cfg$bin_style <- match.arg(cfg$bin_style, c("quantile", "fixed"))

  geometry_col <- NULL
  if ("geometry" %in% names(data)) {
    geometry_col <- "geometry"
  } else if ("geom_wkt" %in% names(data)) {
    geometry_col <- "geom_wkt"
  }

  required <- visual_contracts$choropleth$required_fields
  if (!is.null(cfg$value_field) && cfg$value_field %in% names(data)) {
    required <- unique(c(required, cfg$value_field))
  }
  if (!is.null(cfg$benchmark_field) && cfg$benchmark_field %in% names(data)) {
    required <- unique(c(required, cfg$benchmark_field))
  }

  validate_choropleth_contract(data)
  out <- prepare_long_metric_frame(
    data,
    required = required,
    value_columns = c("metric_value", "benchmark_value"),
    chart_type = "choropleth",
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

  validation <- validate_choropleth_contract(
    out,
    require_single_geo_level = isTRUE(cfg$require_single_geo_level),
    require_single_time_window = isTRUE(cfg$require_single_time_window),
    require_non_empty = TRUE
  )
  if (!isTRUE(validation$pass)) {
    stop("Choropleth prep filters produced a contract-invalid dataset.")
  }

  if ("highlight_flag" %in% names(out)) {
    out$highlight_flag <- coerce_logical_column(out$highlight_flag)
  } else {
    out$highlight_flag <- FALSE
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

  if (isTRUE(cfg$drop_missing_metric)) {
    out <- out[is.finite(out$metric_value), , drop = FALSE]
  }

  if ("geom_wkt" %in% names(out) && requireNamespace("sf", quietly = TRUE)) {
    out <- sf::st_as_sf(out, wkt = "geom_wkt", crs = cfg$crs)
  } else if ("geometry" %in% names(out) &&
             !inherits(out, "sf") &&
             requireNamespace("sf", quietly = TRUE)) {
    out <- sf::st_as_sf(out, sf_column_name = "geometry", crs = cfg$crs)
  }

  out$fill_value <- out$metric_value
  if (identical(cfg$variant, "diverging") && "benchmark_value" %in% names(out)) {
    out$fill_value <- out$metric_value - out$benchmark_value
  }

  if (!"bin" %in% names(out) || all(is.na(out$bin))) {
    fill_values <- suppressWarnings(as.numeric(out$fill_value))
    unique_values <- unique(stats::na.omit(fill_values))
    if (!is.null(cfg$bins) && length(unique_values) > 1) {
      if (identical(cfg$bin_style, "quantile")) {
        probs <- unique(cfg$bins)
        breaks <- stats::quantile(fill_values, probs = probs, na.rm = TRUE, names = FALSE, type = 7)
      } else {
        breaks <- cfg$bins
      }
      breaks <- unique(as.numeric(breaks))
      if (length(breaks) >= 2) {
        out$bin <- cut(
          fill_values,
          breaks = breaks,
          include.lowest = TRUE,
          labels = cfg$bin_labels
        )
      }
    }
  }

  if (!is.null(geometry_col) && !("geometry" %in% names(out)) && inherits(out, "sf")) {
    names(out)[names(out) == attr(out, "sf_column")] <- "geometry"
    attr(out, "sf_column") <- "geometry"
  }

  if (nrow(out) == 0) {
    stop("No rows left after choropleth prep filtering; adjust config.")
  }

  out
}
