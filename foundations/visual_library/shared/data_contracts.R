# Data contract standards and validators for visual artifacts.

source("visual_library/shared/chart_utils.R")

visual_contracts <- list(
  line = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "period", "metric_id", "metric_label", "metric_value", "source", "vintage"),
    optional_fields = c("time_window", "group", "highlight_flag", "benchmark_value", "index_base_period", "note")
  ),
  scatter = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "time_window", "x_value", "y_value", "x_label", "y_label"),
    optional_fields = c("source", "vintage", "group", "size_value", "label_flag", "note", "x_metric_id", "y_metric_id")
  ),
  bar = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "time_window", "metric_id", "metric_label", "metric_value", "source", "vintage"),
    optional_fields = c("rank", "group", "series", "share_value", "highlight_flag", "benchmark_value", "note")
  ),
  choropleth = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "time_window", "metric_value", "metric_label", "source", "vintage"),
    optional_fields = c("geometry", "bin", "benchmark_value", "highlight_flag", "group", "note")
  ),
  boxplot = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "time_window", "metric_id", "metric_label", "metric_value", "source", "vintage"),
    optional_fields = c("group", "highlight_flag", "label_flag", "weight_value", "benchmark_value", "note")
  ),
  hexbin = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "time_window", "x_value", "y_value", "x_label", "y_label", "source", "vintage"),
    optional_fields = c("group", "weight_value", "highlight_flag", "note")
  ),
  strength_strip = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "time_window", "metric_id", "metric_label", "metric_value", "source", "vintage"),
    optional_fields = c("metric_group", "direction", "normalized_value", "benchmark_value", "benchmark_normalized_value", "benchmark_label", "highlight_flag", "note")
  ),
  correlation_heatmap = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "time_window", "metric_id", "metric_label", "metric_value", "source", "vintage"),
    optional_fields = c("group", "include_flag", "weight")
  ),
  highlight_context_map = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "time_window", "source", "vintage", "highlight_flag"),
    optional_fields = c("metric_value", "metric_label", "geometry", "context_group", "neighbor_flag", "benchmark_value", "bin", "group", "label_flag", "label_text", "note")
  ),
  slopegraph = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "period", "metric_id", "metric_label", "metric_value", "source", "vintage"),
    optional_fields = c("group", "highlight_flag", "benchmark_label", "rank", "note")
  ),
  heatmap_table = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "metric_id", "metric_label", "metric_value", "source", "vintage"),
    optional_fields = c("time_window", "period", "metric_group", "normalized_value", "direction", "group", "highlight_flag", "note")
  ),
  age_pyramid = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "period", "age_bin", "sex", "pop_value", "source", "vintage"),
    optional_fields = c("pop_total", "pop_share", "benchmark_label", "highlight_flag", "note")
  ),
  bump_chart = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "period", "metric_id", "metric_label", "metric_value", "source", "vintage"),
    optional_fields = c("rank", "group", "highlight_flag", "peer_flag", "note")
  ),
  waterfall = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "time_window", "total_label", "component_id", "component_label", "component_value", "source", "vintage"),
    optional_fields = c("start_period", "end_period", "component_delta", "unit_label", "component_group", "benchmark_label", "highlight_flag", "sort_order", "note")
  ),
  bivariate_choropleth = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "time_window", "x_value", "y_value", "x_label", "y_label", "source", "vintage"),
    optional_fields = c("geometry", "x_bin", "y_bin", "bivar_class", "highlight_flag", "group", "note")
  ),
  proportional_symbol_map = list(
    required_fields = c("geo_level", "geo_id", "geo_name", "time_window", "size_value", "size_label", "source", "vintage"),
    optional_fields = c("geometry", "lon", "lat", "color_group", "highlight_flag", "label_flag", "note")
  )
)

validate_visual_contract <- function(data,
                                     chart_type,
                                     require_single_geo_level = FALSE,
                                     require_single_time_window = FALSE,
                                     numeric_fields = NULL,
                                     require_non_empty = TRUE) {
  stopifnot(is.data.frame(data))
  contract <- visual_contracts[[chart_type]]
  if (is.null(contract)) {
    stop(sprintf("Unknown chart_type: %s", chart_type))
  }

  required <- contract$required_fields
  optional <- contract$optional_fields %||% character()
  missing_required <- setdiff(required, names(data))

  result <- list(
    chart_type = chart_type,
    pass = TRUE,
    rows = nrow(data),
    missing_required = missing_required,
    present_optional = intersect(optional, names(data)),
    checks = list()
  )

  if (length(missing_required) > 0) {
    result$pass <- FALSE
  }

  result$checks$non_empty <- nrow(data) > 0
  if (isTRUE(require_non_empty) && nrow(data) == 0) {
    result$pass <- FALSE
  }

  if ("geo_level" %in% names(data)) {
    geo_levels <- unique(stats::na.omit(data$geo_level))
    result$checks$geo_level_count <- length(geo_levels)
    if (isTRUE(require_single_geo_level) && length(geo_levels) != 1) {
      result$pass <- FALSE
    }
  }

  if ("time_window" %in% names(data)) {
    windows <- unique(stats::na.omit(data$time_window))
    result$checks$time_window_count <- length(windows)
    if (isTRUE(require_single_time_window) && length(windows) != 1) {
      result$pass <- FALSE
    }
  }

  if (length(numeric_fields) > 0) {
    for (field in intersect(numeric_fields, names(data))) {
      missing_n <- sum(!is.finite(suppressWarnings(as.numeric(data[[field]]))))
      result$checks[[paste0(field, "_missing_numeric")]] <- missing_n
      if (missing_n > 0) {
        result$pass <- FALSE
      }
    }
  }

  class(result) <- c(paste0(chart_type, "_contract_validation"), "visual_contract_validation", class(result))
  result
}

validate_line_contract <- function(data, ...) {
  validate_visual_contract(data, "line", numeric_fields = "metric_value", ...)
}

validate_scatter_contract <- function(data, ...) {
  validate_visual_contract(data, "scatter", numeric_fields = c("x_value", "y_value"), ...)
}

validate_bar_contract <- function(data, ...) {
  validate_visual_contract(data, "bar", numeric_fields = "metric_value", ...)
}

validate_choropleth_contract <- function(data, ...) {
  validate_visual_contract(data, "choropleth", numeric_fields = "metric_value", ...)
}

validate_boxplot_contract <- function(data, ...) {
  validate_visual_contract(data, "boxplot", numeric_fields = "metric_value", ...)
}

validate_hexbin_contract <- function(data, ...) {
  validate_visual_contract(data, "hexbin", numeric_fields = c("x_value", "y_value"), ...)
}

validate_strength_strip_contract <- function(data, ...) {
  validate_visual_contract(data, "strength_strip", numeric_fields = NULL, ...)
}

validate_correlation_heatmap_contract <- function(data, ...) {
  validate_visual_contract(data, "correlation_heatmap", numeric_fields = "metric_value", ...)
}

validate_highlight_context_map_contract <- function(data, ...) {
  validate_visual_contract(data, "highlight_context_map", ...)
}

validate_slopegraph_contract <- function(data, ...) {
  validate_visual_contract(data, "slopegraph", numeric_fields = "metric_value", ...)
}

validate_heatmap_table_contract <- function(data, ...) {
  validate_visual_contract(data, "heatmap_table", numeric_fields = NULL, ...)
}

validate_age_pyramid_contract <- function(data, ...) {
  validate_visual_contract(data, "age_pyramid", numeric_fields = "pop_value", ...)
}

validate_bump_chart_contract <- function(data, ...) {
  validate_visual_contract(data, "bump_chart", numeric_fields = "metric_value", ...)
}

validate_waterfall_contract <- function(data, ...) {
  numeric_fields <- "component_value"
  if ("component_delta" %in% names(data) && any(!is.na(data$component_delta))) {
    numeric_fields <- c(numeric_fields, "component_delta")
  }
  validate_visual_contract(data, "waterfall", numeric_fields = numeric_fields, ...)
}

validate_bivariate_choropleth_contract <- function(data, ...) {
  validate_visual_contract(data, "bivariate_choropleth", numeric_fields = c("x_value", "y_value"), ...)
}

validate_proportional_symbol_map_contract <- function(data, ...) {
  validate_visual_contract(data, "proportional_symbol_map", numeric_fields = c("size_value", "lon", "lat"), ...)
}
