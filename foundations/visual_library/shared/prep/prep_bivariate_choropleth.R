# Prepare bivariate choropleth data.
#
# How to use this file:
# - Call prep_bivariate_choropleth(raw_df, config = list(...)) before rendering.
# - raw_df must satisfy the bivariate contract in data_contracts.R:
#     geo_level, geo_id, geo_name, time_window, x_value, y_value,
#     x_label, y_label, source, vintage, and either geometry or geom_wkt
#     when you want a real map.
# - The prep step filters rows, converts numeric values, converts WKT to sf,
#   computes x_bin/y_bin when they are not supplied, and creates bivar_class.
# - Render code expects bivar_class values like "1-1", "2-3", "3-3".

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

bivariate_quantile_bins <- function(values, n_bins = 3, labels = NULL) {
  # Quantile bins use ranks rather than cut(quantile(...)) so tied values do
  # not collapse the breaks and break the legend/classes.
  values <- suppressWarnings(as.numeric(values))
  labels <- labels %||% as.character(seq_len(n_bins))
  out <- rep(NA_integer_, length(values))
  finite <- is.finite(values)

  if (!any(finite)) {
    return(factor(out, levels = seq_len(n_bins), labels = labels))
  }

  ranks <- rank(values[finite], na.last = "keep", ties.method = "average")
  pct <- (ranks - 0.5) / sum(finite)
  binned <- pmin(pmax(floor(pct * n_bins) + 1, 1), n_bins)
  out[finite] <- binned

  factor(out, levels = seq_len(n_bins), labels = labels)
}

bivariate_fixed_bins <- function(values, breaks, labels = NULL) {
  # Use fixed bins when business thresholds matter more than balanced counts.
  # Example: x_breaks = c(-Inf, 0, 0.05, Inf).
  values <- suppressWarnings(as.numeric(values))
  breaks <- unique(as.numeric(breaks))
  breaks <- breaks[is.finite(breaks)]
  if (length(breaks) < 2) {
    stop("Fixed bivariate bins require at least two finite break values.")
  }

  n_bins <- length(breaks) - 1
  labels <- labels %||% as.character(seq_len(n_bins))
  cut(values, breaks = breaks, include.lowest = TRUE, labels = labels)
}

prep_bivariate_choropleth <- function(data, config = list()) {
  cfg <- merge_chart_config(
    list(
      # Common filters. Leave NULL to keep all rows.
      question_id = NULL,
      time_window = NULL,
      geo_ids = NULL,
      group_values = NULL,
      # Use x_field/y_field when your incoming columns have different names;
      # the output is always normalized back to x_value/y_value.
      x_field = "x_value",
      y_field = "y_value",
      # Binning controls. Default is the library-standard 3x3 quantile grid.
      n_bins = 3,
      bin_method = c("quantile", "fixed"),
      x_breaks = NULL,
      y_breaks = NULL,
      x_bin_labels = NULL,
      y_bin_labels = NULL,
      # bin_by lets each facet/group get its own bins. Leave NULL when panels
      # should be comparable against one shared binning universe.
      bin_by = NULL,
      # Set TRUE to recompute bins even if SQL supplied x_bin/y_bin columns.
      overwrite_bins = FALSE,
      require_single_geo_level = TRUE,
      require_single_time_window = FALSE,
      drop_missing_values = FALSE,
      crs = 4326
    ),
    config
  )
  cfg$bin_method <- match.arg(cfg$bin_method, c("quantile", "fixed"))

  validate_bivariate_choropleth_contract(data)
  out <- prepare_long_metric_frame(
    data,
    required = visual_contracts$bivariate_choropleth$required_fields,
    value_columns = c("x_value", "y_value"),
    chart_type = "bivariate_choropleth",
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

  validation <- validate_bivariate_choropleth_contract(
    out,
    require_single_geo_level = isTRUE(cfg$require_single_geo_level),
    require_single_time_window = isTRUE(cfg$require_single_time_window),
    require_non_empty = TRUE
  )
  if (!isTRUE(validation$pass)) {
    stop("Bivariate choropleth prep filters produced a contract-invalid dataset.")
  }

  out$x_value <- suppressWarnings(as.numeric(out[[cfg$x_field]]))
  out$y_value <- suppressWarnings(as.numeric(out[[cfg$y_field]]))

  if ("highlight_flag" %in% names(out)) {
    out$highlight_flag <- coerce_logical_column(out$highlight_flag)
  } else {
    out$highlight_flag <- FALSE
  }
  if ("label_flag" %in% names(out)) {
    out$label_flag <- coerce_logical_column(out$label_flag)
  }

  if (isTRUE(cfg$drop_missing_values)) {
    # Default keeps missing values so no-data areas remain visible on maps.
    # Use this only for samples where missingness is not part of the review.
    out <- out[is.finite(out$x_value) & is.finite(out$y_value), , drop = FALSE]
  }

  if ("geom_wkt" %in% names(out) && requireNamespace("sf", quietly = TRUE)) {
    # SQL samples usually emit geom_wkt because it travels cleanly through
    # DuckDB/DBI. Convert it here so render_bivariate_choropleth() can map it.
    out <- sf::st_as_sf(out, wkt = "geom_wkt", crs = cfg$crs)
  } else if ("geometry" %in% names(out) &&
             !inherits(out, "sf") &&
             requireNamespace("sf", quietly = TRUE)) {
    out <- sf::st_as_sf(out, sf_column_name = "geometry", crs = cfg$crs)
  }

  if (inherits(out, "sf") && requireNamespace("sf", quietly = TRUE)) {
    # Normalize the active sf column name to geometry. The render function
    # checks for this conventional name before drawing a real map.
    active_geometry <- attr(out, "sf_column")
    if (!identical(active_geometry, "geometry")) {
      names(out)[names(out) == active_geometry] <- "geometry"
      attr(out, "sf_column") <- "geometry"
    }
  }

  needs_bins <- isTRUE(cfg$overwrite_bins) ||
    !("x_bin" %in% names(out)) ||
    !("y_bin" %in% names(out)) ||
    all(is.na(out$x_bin)) ||
    all(is.na(out$y_bin))

  if (isTRUE(needs_bins)) {
    # If SQL already computed bins, this block is skipped unless
    # overwrite_bins = TRUE. That lets production queries own threshold logic.
    out$x_bin <- NA
    out$y_bin <- NA

    group_cols <- intersect(cfg$bin_by %||% character(), names(out))
    if (length(group_cols) > 0) {
      group_key <- interaction(out[, group_cols, drop = FALSE], drop = TRUE, lex.order = TRUE)
      groups <- split(seq_len(nrow(out)), group_key)
    } else {
      groups <- list(seq_len(nrow(out)))
    }

    for (idx in groups) {
      if (identical(cfg$bin_method, "fixed")) {
        out$x_bin[idx] <- as.character(bivariate_fixed_bins(out$x_value[idx], cfg$x_breaks, cfg$x_bin_labels))
        out$y_bin[idx] <- as.character(bivariate_fixed_bins(out$y_value[idx], cfg$y_breaks, cfg$y_bin_labels))
      } else {
        out$x_bin[idx] <- as.character(bivariate_quantile_bins(out$x_value[idx], cfg$n_bins, cfg$x_bin_labels))
        out$y_bin[idx] <- as.character(bivariate_quantile_bins(out$y_value[idx], cfg$n_bins, cfg$y_bin_labels))
      }
    }
  }

  out$x_bin <- as.character(out$x_bin)
  out$y_bin <- as.character(out$y_bin)
  out$bivar_class <- ifelse(
    # bivar_class is the only fill class the renderer needs.
    is.na(out$x_bin) | is.na(out$y_bin),
    NA_character_,
    paste(out$x_bin, out$y_bin, sep = "-")
  )

  if (nrow(out) == 0) {
    stop("No rows left after bivariate choropleth prep filtering; adjust config.")
  }

  attr(out, "bivariate_bin_config") <- list(
    # Keep bin metadata attached for debugging and future QA summaries.
    method = cfg$bin_method,
    n_bins = cfg$n_bins,
    bin_by = cfg$bin_by,
    x_label = unique(stats::na.omit(out$x_label))[1] %||% "X metric",
    y_label = unique(stats::na.omit(out$y_label))[1] %||% "Y metric"
  )

  out
}
