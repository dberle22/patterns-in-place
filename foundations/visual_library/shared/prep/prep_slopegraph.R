# Prepare slopegraph data.

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

prep_slopegraph <- function(data, config = list()) {
  cfg <- merge_chart_config(
    list(
      question_id = NULL,
      metric_id = NULL,
      geo_ids = NULL,
      periods = NULL,
      start_period = NULL,
      end_period = NULL,
      variant = "value",
      base_period = NULL,
      order_by = "end_value",
      sort_desc = TRUE,
      top_n = NULL,
      include_geo_ids = NULL,
      include_highlighted = TRUE,
      drop_incomplete = TRUE,
      rank_higher_is_better = TRUE
    ),
    config
  )

  validate_slopegraph_contract(data)
  out <- prepare_long_metric_frame(
    data,
    required = visual_contracts$slopegraph$required_fields,
    value_columns = c("period", "metric_value", "rank"),
    chart_type = "slopegraph",
    config = cfg
  )

  if (!is.null(cfg$question_id) && "question_id" %in% names(out)) {
    out <- out[out$question_id == cfg$question_id, , drop = FALSE]
  }
  if (!is.null(cfg$metric_id)) {
    out <- out[out$metric_id == cfg$metric_id, , drop = FALSE]
  }
  if (!is.null(cfg$geo_ids)) {
    out <- out[out$geo_id %in% cfg$geo_ids, , drop = FALSE]
  }

  periods <- cfg$periods %||% compact_chr(c(cfg$start_period, cfg$end_period))
  if (length(periods) == 0) {
    periods <- sort(unique(stats::na.omit(out$period)))
  }
  if (length(periods) != 2) {
    stop("Slopegraph requires exactly two periods.")
  }
  out <- out[out$period %in% periods, , drop = FALSE]
  if (nrow(out) == 0) {
    stop("No rows left after slopegraph prep filtering; adjust config.")
  }

  start_period <- periods[[1]]
  end_period <- periods[[2]]
  out$period_role <- ifelse(out$period == start_period, "start", "end")
  out$period_label <- as.character(out$period)

  if ("highlight_flag" %in% names(out)) {
    out$highlight_flag <- coerce_logical_column(out$highlight_flag)
  } else {
    out$highlight_flag <- FALSE
  }

  if ("benchmark_label" %in% names(out)) {
    out$benchmark_label <- as.character(out$benchmark_label)
    out$benchmark_flag <- !is.na(out$benchmark_label) & nzchar(out$benchmark_label)
  } else {
    out$benchmark_label <- NA_character_
    out$benchmark_flag <- FALSE
  }

  key <- paste(out$geo_id, out$period, out$metric_id, sep = "::")
  if (anyDuplicated(key) > 0) {
    stop("Slopegraph prep expects one row per geo_id, period, and metric_id after filtering.")
  }

  endpoint <- stats::reshape(
    out[, c("geo_id", "period_role", "metric_value"), drop = FALSE],
    idvar = "geo_id",
    timevar = "period_role",
    direction = "wide"
  )
  names(endpoint) <- sub("^metric_value\\.", "", names(endpoint))
  endpoint$start_value <- endpoint$start
  endpoint$end_value <- endpoint$end
  endpoint$delta_value <- endpoint$end_value - endpoint$start_value
  endpoint$pct_change <- ifelse(
    is.finite(endpoint$start_value) & endpoint$start_value != 0,
    endpoint$delta_value / endpoint$start_value,
    NA_real_
  )
  endpoint$complete_endpoint_flag <- is.finite(endpoint$start_value) & is.finite(endpoint$end_value)
  endpoint <- endpoint[, c("geo_id", "start_value", "end_value", "delta_value", "pct_change", "complete_endpoint_flag"), drop = FALSE]

  out <- merge(out, endpoint, by = "geo_id", all.x = TRUE, sort = FALSE)
  if (isTRUE(cfg$drop_incomplete)) {
    out <- out[out$complete_endpoint_flag %in% TRUE, , drop = FALSE]
  }
  if (nrow(out) == 0) {
    stop("No complete two-period entities remain for slopegraph rendering.")
  }

  out$variant <- cfg$variant
  out$plot_value <- out$metric_value
  if (identical(cfg$variant, "indexed")) {
    out$plot_value <- ifelse(
      is.finite(out$start_value) & out$start_value != 0,
      (out$metric_value / out$start_value) * 100,
      NA_real_
    )
    out$index_base_period <- cfg$base_period %||% start_period
  } else if (identical(cfg$variant, "rank")) {
    if (!("rank" %in% names(out)) || all(!is.finite(out$rank))) {
      parts <- split(out, out$period)
      parts <- lapply(parts, function(df) {
        rank_input <- if (isTRUE(cfg$rank_higher_is_better)) -df$metric_value else df$metric_value
        df$rank <- rank(rank_input, ties.method = "first", na.last = "keep")
        df
      })
      out <- do.call(rbind, parts)
    }
    out$plot_value <- out$rank
  }

  end_rows <- out[out$period_role == "end", , drop = FALSE]
  sort_value <- switch(
    cfg$order_by,
    start_value = end_rows$start_value,
    end_value = end_rows$end_value,
    delta_value = end_rows$delta_value,
    abs_delta = abs(end_rows$delta_value),
    pct_change = end_rows$pct_change,
    abs_pct_change = abs(end_rows$pct_change),
    rank = end_rows$rank,
    geo_name = end_rows$geo_name,
    end_rows$end_value
  )
  end_rows$sort_value <- sort_value
  end_rows <- end_rows[order(end_rows$sort_value, decreasing = isTRUE(cfg$sort_desc), end_rows$geo_name), , drop = FALSE]

  if (!is.null(cfg$top_n)) {
    trimmed <- utils::head(end_rows, cfg$top_n)

    if (!is.null(cfg$include_geo_ids)) {
      extras <- end_rows[end_rows$geo_id %in% cfg$include_geo_ids & !(end_rows$geo_id %in% trimmed$geo_id), , drop = FALSE]
      if (nrow(extras) > 0) {
        trimmed <- rbind(trimmed, extras)
      }
    }

    if (isTRUE(cfg$include_highlighted)) {
      extras <- end_rows[end_rows$highlight_flag %in% TRUE & !(end_rows$geo_id %in% trimmed$geo_id), , drop = FALSE]
      if (nrow(extras) > 0) {
        trimmed <- rbind(trimmed, extras)
      }
    }

    end_rows <- trimmed[order(trimmed$sort_value, decreasing = isTRUE(cfg$sort_desc), trimmed$geo_name), , drop = FALSE]
  }

  display_lookup <- data.frame(
    geo_id = end_rows$geo_id,
    display_order = seq_len(nrow(end_rows)),
    sort_value = end_rows$sort_value,
    stringsAsFactors = FALSE
  )
  out <- out[out$geo_id %in% display_lookup$geo_id, , drop = FALSE]
  out <- merge(out, display_lookup, by = "geo_id", all.x = TRUE, sort = FALSE)
  out <- out[order(out$display_order, out$period), , drop = FALSE]
  attr(out, "chart_config") <- resolve_chart_config("slopegraph", cfg)
  out
}
