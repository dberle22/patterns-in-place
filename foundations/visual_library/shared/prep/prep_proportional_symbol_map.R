# Prepare proportional symbol map data.

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

prep_proportional_symbol_map <- function(data, config = list()) {
  cfg <- merge_chart_config(
    list(
      question_id = NULL,
      time_window = NULL,
      geo_ids = NULL,
      color_groups = NULL,
      top_n = NULL,
      top_n_by_group = FALSE,
      label_top_n = 8,
      label_strategy = c("provided_or_top_n", "top_n", "provided", "none"),
      drop_missing_size = TRUE,
      drop_missing_coordinates = TRUE,
      derive_coordinates = TRUE,
      require_single_geo_level = TRUE,
      require_single_time_window = FALSE,
      crs = 4326
    ),
    config
  )
  cfg$label_strategy <- match.arg(
    cfg$label_strategy,
    c("provided_or_top_n", "top_n", "provided", "none")
  )

  # Start from the chart contract, then apply question-specific filters below.
  # The final dataset is revalidated after Top-N and coordinate filtering.
  out <- prepare_long_metric_frame(
    data,
    required = visual_contracts$proportional_symbol_map$required_fields,
    value_columns = c("size_value", "lon", "lat"),
    chart_type = "proportional_symbol_map",
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
  if (!is.null(cfg$color_groups) && "color_group" %in% names(out)) {
    out <- out[out$color_group %in% cfg$color_groups, , drop = FALSE]
  }

  if ("highlight_flag" %in% names(out)) {
    out$highlight_flag <- coerce_logical_column(out$highlight_flag)
  } else {
    out$highlight_flag <- FALSE
  }
  if ("label_flag" %in% names(out)) {
    out$label_flag <- coerce_logical_column(out$label_flag)
  } else {
    out$label_flag <- FALSE
  }

  # Accept either explicit lon/lat or geometry. Geometry-backed inputs are
  # converted to sf so point-on-surface coordinates can be derived consistently.
  if ("geom_wkt" %in% names(out) && requireNamespace("sf", quietly = TRUE)) {
    out <- sf::st_as_sf(out, wkt = "geom_wkt", crs = cfg$crs)
  } else if ("geometry" %in% names(out) &&
             !inherits(out, "sf") &&
             requireNamespace("sf", quietly = TRUE)) {
    out <- sf::st_as_sf(out, sf_column_name = "geometry", crs = cfg$crs)
  }

  # Point-on-surface is safer than centroid for irregular polygons because the
  # plotted symbol stays inside the source geography.
  if (isTRUE(cfg$derive_coordinates) &&
      (!all(c("lon", "lat") %in% names(out)) ||
       any(!is.finite(out$lon) | !is.finite(out$lat))) &&
      inherits(out, "sf") &&
      requireNamespace("sf", quietly = TRUE)) {
    point_geom <- sf::st_point_on_surface(sf::st_geometry(out))
    coords <- sf::st_coordinates(point_geom)
    out$lon <- as.numeric(coords[, "X"])
    out$lat <- as.numeric(coords[, "Y"])
  }

  # Bubbles represent positive totals. Missing or nonpositive totals are removed
  # by default so the size legend and area scaling stay interpretable.
  if (isTRUE(cfg$drop_missing_size)) {
    out <- out[is.finite(out$size_value) & out$size_value > 0, , drop = FALSE]
  }
  if (isTRUE(cfg$drop_missing_coordinates) && all(c("lon", "lat") %in% names(out))) {
    out <- out[is.finite(out$lon) & is.finite(out$lat), , drop = FALSE]
  }

  if (nrow(out) == 0) {
    stop("No rows left after proportional symbol map prep filtering; adjust config.")
  }

  # Ranking powers Top-N clutter control, default labels, and cumulative-share
  # diagnostics used by "which places account for most of the total" questions.
  rank_groups <- if (isTRUE(cfg$top_n_by_group) && "color_group" %in% names(out)) "color_group" else NULL
  out <- compute_deterministic_ranks(
    out,
    value_col = "size_value",
    rank_col = "size_rank",
    group_cols = rank_groups,
    higher_is_better = TRUE
  )

  total_size <- sum(out$size_value, na.rm = TRUE)
  out$size_share <- if (is.finite(total_size) && total_size > 0) out$size_value / total_size else NA_real_
  out <- out[order(out$size_rank, out$geo_name, out$geo_id), , drop = FALSE]
  out$cumulative_size_share <- cumsum(out$size_value) / total_size

  if (!is.null(cfg$top_n) && is.finite(cfg$top_n)) {
    out <- out[out$size_rank <= cfg$top_n, , drop = FALSE]
  }

  # Label strategy is intentionally separate from highlight styling: a dense map
  # can highlight many bubbles while labeling only the top few.
  if (identical(cfg$label_strategy, "none")) {
    out$label_flag <- FALSE
  } else if (identical(cfg$label_strategy, "top_n")) {
    out$label_flag <- if (!is.null(cfg$label_top_n) && is.finite(cfg$label_top_n)) {
      out$size_rank <= cfg$label_top_n
    } else {
      FALSE
    }
  } else if (identical(cfg$label_strategy, "provided_or_top_n") &&
             !any(out$label_flag %in% TRUE, na.rm = TRUE) &&
             !is.null(cfg$label_top_n) &&
             is.finite(cfg$label_top_n)) {
    out$label_flag <- out$size_rank <= cfg$label_top_n
  }

  validation <- validate_proportional_symbol_map_contract(
    out,
    require_single_geo_level = isTRUE(cfg$require_single_geo_level),
    require_single_time_window = isTRUE(cfg$require_single_time_window),
    require_non_empty = TRUE
  )
  if (!isTRUE(validation$pass)) {
    stop("Proportional symbol map prep filters produced a contract-invalid dataset.")
  }

  attr(out, "chart_config") <- resolve_chart_config(
    chart_type = "proportional_symbol_map",
    config = cfg
  )

  out
}
