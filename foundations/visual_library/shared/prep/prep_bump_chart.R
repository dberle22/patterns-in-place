# Prepare bump chart data.

source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")

bump_rank_direction_flag <- function(direction = NULL, higher_is_better = NULL) {
  rank_direction_flag(direction = direction, higher_is_better = higher_is_better)
}

bump_compute_period_ranks <- function(data,
                                      metric_higher_is_better = TRUE,
                                      rank_method = "row_number") {
  compute_deterministic_ranks(
    data = data,
    value_col = "metric_value",
    rank_col = "rank",
    group_cols = "period",
    higher_is_better = metric_higher_is_better,
    rank_method = rank_method,
    tie_cols = c("geo_name", "geo_id")
  )
}

select_bump_entities <- function(data, cfg) {
  strategy <- cfg$entity_strategy %||% "fixed_top_n"
  periods <- sort(unique(stats::na.omit(data$period)))
  if (length(periods) == 0) {
    stop("Bump chart prep requires at least one period.")
  }

  selection_period <- cfg$selection_period %||% if (identical(cfg$selection_period_role %||% "end", "start")) {
    periods[[1]]
  } else {
    periods[[length(periods)]]
  }

  keep_geo <- character()
  if (identical(strategy, "peer_set")) {
    if ("peer_flag" %in% names(data) && any(data$peer_flag %in% TRUE, na.rm = TRUE)) {
      keep_geo <- unique(data$geo_id[data$peer_flag %in% TRUE])
    }
    if (!is.null(cfg$geo_ids)) {
      keep_geo <- unique(c(keep_geo, cfg$geo_ids))
    }
  } else if (identical(strategy, "rolling_top_n")) {
    top_n <- cfg$top_n %||% 10
    keep_geo <- unique(data$geo_id[is.finite(data$rank) & data$rank <= top_n])
  } else if (identical(strategy, "all")) {
    keep_geo <- unique(data$geo_id)
  } else {
    top_n <- cfg$top_n %||% 10
    selection_rows <- data[data$period == selection_period & is.finite(data$rank), , drop = FALSE]
    selection_rows <- selection_rows[order(selection_rows$rank, selection_rows$geo_name, selection_rows$geo_id), , drop = FALSE]
    keep_geo <- utils::head(selection_rows$geo_id, top_n)
  }

  if (!is.null(cfg$include_geo_ids)) {
    keep_geo <- unique(c(keep_geo, cfg$include_geo_ids))
  }
  if (isTRUE(cfg$include_highlighted) && "highlight_flag" %in% names(data)) {
    keep_geo <- unique(c(keep_geo, data$geo_id[data$highlight_flag %in% TRUE]))
  }
  if (length(keep_geo) == 0) {
    stop("No entities selected for bump chart display; adjust entity_strategy, top_n, or peer flags.")
  }

  out <- data[data$geo_id %in% keep_geo, , drop = FALSE]
  out$selection_period <- selection_period
  out$entity_strategy <- strategy
  out$display_entity_n <- length(unique(out$geo_id))
  out
}

add_bump_endpoint_fields <- function(data) {
  out <- data
  periods <- sort(unique(stats::na.omit(out$period)))
  start_period <- periods[[1]]
  end_period <- periods[[length(periods)]]

  start_rows <- out[out$period == start_period, c("geo_id", "rank"), drop = FALSE]
  names(start_rows)[names(start_rows) == "rank"] <- "start_rank"
  end_rows <- out[out$period == end_period, c("geo_id", "rank", "metric_value"), drop = FALSE]
  names(end_rows)[names(end_rows) == "rank"] <- "end_rank"
  names(end_rows)[names(end_rows) == "metric_value"] <- "end_metric_value"

  out <- merge(out, start_rows, by = "geo_id", all.x = TRUE, sort = FALSE)
  out <- merge(out, end_rows, by = "geo_id", all.x = TRUE, sort = FALSE)
  out$rank_change <- out$start_rank - out$end_rank
  out$complete_endpoint_flag <- is.finite(out$start_rank) & is.finite(out$end_rank)
  out$is_start_period <- out$period == start_period
  out$is_end_period <- out$period == end_period
  out
}

prep_bump_chart <- function(data, config = list()) {
  cfg <- merge_chart_config(
    list(
      question_id = NULL,
      metric_id = NULL,
      geo_ids = NULL,
      period_min = NULL,
      period_max = NULL,
      periods = NULL,
      entity_strategy = "fixed_top_n",
      selection_period = NULL,
      selection_period_role = "end",
      top_n = 10,
      include_geo_ids = NULL,
      include_highlighted = TRUE,
      use_precomputed_rank = TRUE,
      rank_method = "row_number",
      metric_higher_is_better = TRUE,
      direction = NULL,
      complete_periods = FALSE,
      drop_missing_rank = TRUE
    ),
    config
  )

  validate_bump_chart_contract(data)
  out <- prepare_long_metric_frame(
    data,
    required = visual_contracts$bump_chart$required_fields,
    value_columns = c("period", "metric_value", "rank"),
    chart_type = "bump_chart",
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
  if (!is.null(cfg$periods)) {
    out <- out[as.character(out$period) %in% as.character(cfg$periods), , drop = FALSE]
  }
  if (!is.null(cfg$period_min)) {
    out <- out[out$period >= cfg$period_min, , drop = FALSE]
  }
  if (!is.null(cfg$period_max)) {
    out <- out[out$period <= cfg$period_max, , drop = FALSE]
  }
  if (nrow(out) == 0) {
    stop("No rows left after bump chart prep filtering; adjust config.")
  }

  if ("highlight_flag" %in% names(out)) {
    out$highlight_flag <- coerce_logical_column(out$highlight_flag)
  } else {
    out$highlight_flag <- FALSE
  }
  if ("peer_flag" %in% names(out)) {
    out$peer_flag <- coerce_logical_column(out$peer_flag)
  } else {
    out$peer_flag <- FALSE
  }
  if ("note" %in% names(out)) {
    out$note <- as.character(out$note)
  }

  key <- paste(out$geo_id, out$metric_id, out$period, sep = "::")
  if (anyDuplicated(key) > 0) {
    stop("Bump chart prep expects one row per geo_id, metric_id, and period after filtering.")
  }

  higher_is_better <- bump_rank_direction_flag(cfg$direction, cfg$metric_higher_is_better)
  needs_rank <- !("rank" %in% names(out)) || all(!is.finite(out$rank)) || !isTRUE(cfg$use_precomputed_rank)
  if (isTRUE(needs_rank)) {
    out <- bump_compute_period_ranks(
      out,
      metric_higher_is_better = higher_is_better,
      rank_method = cfg$rank_method
    )
    out$rank_source <- "derived"
  } else {
    out$rank <- suppressWarnings(as.numeric(out$rank))
    out$rank_source <- "precomputed"
  }

  if (isTRUE(cfg$drop_missing_rank)) {
    out <- out[is.finite(out$rank), , drop = FALSE]
  }
  if (nrow(out) == 0) {
    stop("No finite ranks remain for bump chart rendering.")
  }

  out <- select_bump_entities(out, cfg)
  out <- add_bump_endpoint_fields(out)
  out$rank_method <- ifelse(out$rank_source == "precomputed", "precomputed", cfg$rank_method)
  out$rank_higher_is_better <- higher_is_better

  out <- out[order(out$rank, out$geo_name, out$period), , drop = FALSE]
  attr(out, "chart_config") <- resolve_chart_config("bump_chart", cfg)
  out
}
