# Shared helpers used across visual library prep/render functions.

source("visual_library/shared/standards.R")

ensure_columns <- function(data, required, chart_type = "chart") {
  stopifnot(is.data.frame(data))
  missing <- setdiff(required, names(data))
  if (length(missing) > 0) {
    stop(
      sprintf(
        "%s is missing required columns: %s",
        chart_type,
        paste(missing, collapse = ", ")
      ),
      call. = FALSE
    )
  }
  invisible(TRUE)
}

coerce_numeric_columns <- function(data, columns) {
  for (col in intersect(columns, names(data))) {
    data[[col]] <- suppressWarnings(as.numeric(data[[col]]))
  }
  data
}

coerce_logical_column <- function(x) {
  if (is.logical(x)) {
    return(x)
  }
  if (is.numeric(x)) {
    return(x != 0)
  }
  tolower(as.character(x)) %in% c("true", "t", "1", "yes", "y")
}

prepare_long_metric_frame <- function(data,
                                      required,
                                      value_columns = NULL,
                                      chart_type = "chart",
                                      config = NULL) {
  ensure_columns(data, required, chart_type = chart_type)
  out <- data
  if (!is.null(value_columns)) {
    out <- coerce_numeric_columns(out, value_columns)
  }
  attr(out, "chart_config") <- resolve_chart_config(chart_type = chart_type, config = config)
  out
}

compute_percentile <- function(x, higher_is_better = TRUE) {
  values <- suppressWarnings(as.numeric(x))
  ranks <- rank(values, na.last = "keep", ties.method = "average")
  n <- sum(is.finite(values))
  if (n <= 1) {
    pct <- rep(50, length(values))
    pct[!is.finite(values)] <- NA_real_
  } else {
    pct <- ((ranks - 1) / (n - 1)) * 100
  }
  if (!isTRUE(higher_is_better)) {
    pct <- 100 - pct
  }
  pct
}

rank_direction_flag <- function(direction = NULL, higher_is_better = NULL) {
  if (!is.null(higher_is_better)) {
    return(isTRUE(higher_is_better))
  }
  direction <- tolower(as.character(direction %||% "higher_is_better"))
  !(direction %in% c("lower_is_better", "lower-better", "lower", "low_is_good", "low-good"))
}

compute_deterministic_ranks <- function(data,
                                        value_col = "metric_value",
                                        rank_col = "rank",
                                        group_cols = NULL,
                                        higher_is_better = TRUE,
                                        rank_method = "row_number",
                                        tie_cols = c("geo_name", "geo_id")) {
  stopifnot(is.data.frame(data))
  ensure_columns(data, value_col, chart_type = "rank helper")
  rank_method <- match.arg(rank_method, c("row_number", "dense", "min"))

  out <- data
  out[[rank_col]] <- NA_real_

  if (length(group_cols) > 0) {
    ensure_columns(out, group_cols, chart_type = "rank helper")
    group_key <- interaction(out[, group_cols, drop = FALSE], drop = TRUE, lex.order = TRUE)
    groups <- split(seq_len(nrow(out)), group_key)
  } else {
    groups <- list(seq_len(nrow(out)))
  }

  for (idx in groups) {
    values <- suppressWarnings(as.numeric(out[[value_col]][idx]))
    finite <- is.finite(values)
    if (!any(finite)) {
      next
    }

    finite_idx <- idx[finite]
    finite_values <- values[finite]
    order_value <- if (isTRUE(higher_is_better)) -finite_values else finite_values
    order_args <- list(order_value)
    for (col in tie_cols) {
      if (col %in% names(out)) {
        order_args[[length(order_args) + 1]] <- as.character(out[[col]][finite_idx])
      }
    }
    order_args$na.last <- TRUE
    ord <- do.call(order, order_args)
    ordered_idx <- finite_idx[ord]
    ordered_values <- finite_values[ord]

    if (identical(rank_method, "row_number")) {
      out[[rank_col]][ordered_idx] <- seq_along(ordered_idx)
    } else if (identical(rank_method, "min")) {
      out[[rank_col]][ordered_idx] <- rank(
        if (isTRUE(higher_is_better)) -ordered_values else ordered_values,
        ties.method = "min",
        na.last = "keep"
      )
    } else {
      unique_values <- sort(unique(ordered_values), decreasing = isTRUE(higher_is_better))
      out[[rank_col]][ordered_idx] <- match(ordered_values, unique_values)
    }
  }

  out
}

rank_method_note <- function(rank_source = "derived",
                             rank_method = "row_number",
                             tie_cols = c("metric value", "geography name", "geography id")) {
  if (!identical(rank_source, "derived")) {
    return("Ranks use the precomputed rank field supplied by the data.")
  }
  if (identical(rank_method, "row_number")) {
    return(paste0("Ties are broken deterministically by ", paste(tie_cols, collapse = ", "), "."))
  }
  paste0("Ties use ", rank_method, " ranking.")
}

endpoint_label_plan <- function(data,
                                period_col = "period",
                                label_mode = "highlight_or_all",
                                highlight_col = "highlight_flag",
                                rank_col = "rank",
                                label_all_max_n = 12,
                                label_top_n = 8,
                                endpoint = c("end", "start")) {
  # Placeholder shared policy for endpoint-label selection. Current callers can
  # use it directly; future chart-specific helpers can wrap it for label text.
  stopifnot(is.data.frame(data))
  endpoint <- match.arg(endpoint)
  ensure_columns(data, period_col, chart_type = "endpoint label helper")

  periods <- sort(unique(stats::na.omit(data[[period_col]])))
  if (length(periods) == 0) {
    return(data[0, , drop = FALSE])
  }
  endpoint_period <- if (identical(endpoint, "start")) periods[[1]] else periods[[length(periods)]]
  out <- data[data[[period_col]] == endpoint_period, , drop = FALSE]

  if (highlight_col %in% names(out)) {
    out[[highlight_col]] <- coerce_logical_column(out[[highlight_col]])
  } else {
    out[[highlight_col]] <- FALSE
  }

  if (identical(label_mode, "highlight")) {
    return(out[out[[highlight_col]] %in% TRUE, , drop = FALSE])
  }
  if (identical(label_mode, "top_n") && rank_col %in% names(out)) {
    out <- out[order(out[[rank_col]], out$geo_name %||% seq_len(nrow(out))), , drop = FALSE]
    return(utils::head(out, label_top_n))
  }
  if (identical(label_mode, "all")) {
    return(out)
  }

  has_highlight <- any(out[[highlight_col]] %in% TRUE, na.rm = TRUE)
  if (has_highlight) {
    return(out[out[[highlight_col]] %in% TRUE, , drop = FALSE])
  }
  if (nrow(out) > label_all_max_n && rank_col %in% names(out)) {
    out <- out[order(out[[rank_col]], out$geo_name %||% seq_len(nrow(out))), , drop = FALSE]
    return(utils::head(out, label_all_max_n))
  }
  out
}

default_chart_title <- function(chart_type, metric_label = NULL, geo_name = NULL) {
  parts <- c(metric_label, geo_name)
  parts <- parts[!is.na(parts) & nzchar(parts)]
  if (length(parts) == 0) {
    return(tools::toTitleCase(gsub("_", " ", chart_type)))
  }
  paste(parts, collapse = ": ")
}

resolve_output_mode <- function(config = NULL, default = "notebook") {
  visual_output_mode((config %||% list())$output_mode %||% default)
}

resolve_label_box <- function(config = NULL, default = NULL) {
  mode <- resolve_output_mode(config)
  if (!is.null((config %||% list())$label_box)) {
    return(isTRUE(config$label_box))
  }
  if (!is.null(default)) {
    return(isTRUE(default))
  }
  identical(mode, "presentation")
}

value_label_formatter <- function(style = c("number", "percent", "dollar", "integer", "rank"),
                                  accuracy = NULL,
                                  compact = TRUE) {
  style <- match.arg(style)

  if (identical(style, "percent")) {
    return(format_percent(accuracy = accuracy %||% 0.1))
  }
  if (identical(style, "dollar")) {
    return(format_dollar(
      accuracy = accuracy %||% 1,
      scale_cut = if (isTRUE(compact)) scales::cut_short_scale() else NULL
    ))
  }
  if (identical(style, "integer")) {
    return(format_integer())
  }
  if (identical(style, "rank")) {
    return(format_rank())
  }

  format_number(
    accuracy = accuracy %||% if (isTRUE(compact)) 0.1 else 1,
    scale_cut = if (isTRUE(compact)) scales::cut_short_scale() else NULL
  )
}

format_value_vector <- function(values,
                                style = "number",
                                accuracy = NULL,
                                compact = TRUE) {
  value_label_formatter(
    style = style,
    accuracy = accuracy,
    compact = compact
  )(values)
}

derive_reference_value <- function(data,
                                   value_col,
                                   method = c("median", "mean", "zero", "value"),
                                   value = NULL,
                                   subset = NULL) {
  method <- match.arg(method)
  values <- data[[value_col]]
  if (!is.null(subset)) {
    values <- values[subset]
  }
  values <- suppressWarnings(as.numeric(values))

  if (identical(method, "zero")) {
    return(0)
  }
  if (identical(method, "value")) {
    return(as.numeric(value))
  }
  if (identical(method, "mean")) {
    return(mean(values, na.rm = TRUE))
  }

  stats::median(values, na.rm = TRUE)
}

benchmark_label_text <- function(label = NULL,
                                 value = NULL,
                                 value_style = "number",
                                 accuracy = NULL,
                                 prefix = NULL) {
  pieces <- compact_chr(c(label, prefix))
  if (!is.null(value) && is.finite(value)) {
    formatted <- format_value_vector(
      value,
      style = value_style,
      accuracy = accuracy
    )
    if (length(pieces) == 0) {
      return(formatted)
    }
    return(paste0(paste(pieces, collapse = " "), ": ", formatted))
  }
  paste(pieces, collapse = " ")
}

benchmark_layer <- function(data,
                            orientation = c("horizontal", "vertical"),
                            intercept,
                            label = NULL,
                            value = NULL,
                            value_style = "number",
                            accuracy = NULL,
                            config = list(),
                            position = NULL,
                            show_label = NULL) {
  orientation <- match.arg(orientation)
  cfg <- resolve_chart_config(config = config)
  bench <- benchmark_style_defaults(cfg$output_mode)
  show_label <- show_label %||% cfg$benchmark_label_default
  label_text <- benchmark_label_text(
    label = label,
    value = value %||% intercept,
    value_style = value_style,
    accuracy = accuracy
  )

  line <- if (identical(orientation, "horizontal")) {
    ggplot2::geom_hline(
      yintercept = intercept,
      color = cfg$benchmark_color %||% bench$color,
      linewidth = cfg$benchmark_linewidth %||% bench$linewidth,
      linetype = cfg$benchmark_linetype %||% bench$linetype,
      alpha = cfg$benchmark_alpha %||% bench$alpha
    )
  } else {
    ggplot2::geom_vline(
      xintercept = intercept,
      color = cfg$benchmark_color %||% bench$color,
      linewidth = cfg$benchmark_linewidth %||% bench$linewidth,
      linetype = cfg$benchmark_linetype %||% bench$linetype,
      alpha = cfg$benchmark_alpha %||% bench$alpha
    )
  }

  if (!isTRUE(show_label) || !is_nonempty_string(label_text)) {
    return(list(line = line, label = NULL))
  }

  pos <- position %||% if (identical(orientation, "horizontal")) {
    list(
      x = Inf,
      y = intercept,
      hjust = 1.02,
      vjust = -0.4
    )
  } else {
    list(
      x = intercept,
      y = Inf,
      hjust = -0.1,
      vjust = 1.1
    )
  }

  label_df <- data.frame(
    x = pos$x %||% Inf,
    y = pos$y %||% intercept,
    label = label_text,
    hjust = pos$hjust %||% 1.02,
    vjust = pos$vjust %||% -0.4
  )

  label_layer <- ggplot2::geom_text(
    data = label_df,
    ggplot2::aes(x = .data$x, y = .data$y, label = .data$label),
    inherit.aes = FALSE,
    color = bench$text_color,
    size = bench$text_size,
    hjust = label_df$hjust[[1]],
    vjust = label_df$vjust[[1]]
  )

  list(line = line, label = label_layer)
}

apply_benchmark_layer <- function(plot, benchmark) {
  if (is.null(benchmark)) {
    return(plot)
  }
  if (!is.null(benchmark$line)) {
    plot <- plot + benchmark$line
  }
  if (!is.null(benchmark$label)) {
    plot <- plot + benchmark$label
  }
  plot
}

pick_label_rows <- function(data,
                            flag_col = "label_flag",
                            highlight_col = "highlight_flag",
                            value_col = NULL,
                            top_n = NULL) {
  out <- data
  keep <- rep(FALSE, nrow(out))

  if (flag_col %in% names(out)) {
    keep <- keep | coerce_logical_column(out[[flag_col]])
  }
  if (highlight_col %in% names(out)) {
    keep <- keep | coerce_logical_column(out[[highlight_col]])
  }
  if (!is.null(top_n) && !is.null(value_col) && value_col %in% names(out)) {
    ord <- order(out[[value_col]], decreasing = TRUE, na.last = NA)
    keep[utils::head(ord, top_n)] <- TRUE
  }

  out[keep %in% TRUE, , drop = FALSE]
}

label_layer <- function(data,
                        mapping,
                        config = list(),
                        boxed = NULL,
                        repel = TRUE,
                        ...) {
  cfg <- resolve_chart_config(config = config)
  boxed <- boxed %||% resolve_label_box(cfg)

  if (nrow(data) == 0) {
    return(NULL)
  }

  if (isTRUE(boxed) && repel && requireNamespace("ggrepel", quietly = TRUE)) {
    return(ggrepel::geom_label_repel(
      data = data,
      mapping = mapping,
      size = cfg$label_size,
      label.size = 0.15,
      label.padding = grid::unit(0.12, "lines"),
      fill = visual_neutral_palette()$background_white,
      color = visual_neutral_palette()$text,
      box.padding = 0.25,
      min.segment.length = 0,
      seed = 123,
      ...
    ))
  }

  if (isTRUE(boxed)) {
    return(ggplot2::geom_label(
      data = data,
      mapping = mapping,
      size = cfg$label_size,
      label.size = 0.15,
      fill = visual_neutral_palette()$background_white,
      color = visual_neutral_palette()$text,
      ...
    ))
  }

  if (repel && requireNamespace("ggrepel", quietly = TRUE)) {
    return(ggrepel::geom_text_repel(
      data = data,
      mapping = mapping,
      size = cfg$label_size,
      color = visual_neutral_palette()$text,
      box.padding = 0.25,
      min.segment.length = 0,
      seed = 123,
      ...
    ))
  }

  ggplot2::geom_text(
    data = data,
    mapping = mapping,
    size = cfg$label_size,
    color = visual_neutral_palette()$text,
    ...
  )
}

annotation_note_label <- function(text,
                                  x,
                                  y,
                                  boxed = TRUE,
                                  config = list(),
                                  hjust = 0,
                                  vjust = 1) {
  if (!is_nonempty_string(text)) {
    return(NULL)
  }

  cfg <- resolve_chart_config(config = config)
  note_df <- data.frame(x = x, y = y, label = text)

  if (isTRUE(boxed)) {
    return(ggplot2::geom_label(
      data = note_df,
      ggplot2::aes(x = .data$x, y = .data$y, label = .data$label),
      inherit.aes = FALSE,
      hjust = hjust,
      vjust = vjust,
      size = cfg$label_size,
      label.size = 0.15,
      fill = visual_neutral_palette()$background_white,
      color = visual_neutral_palette()$text
    ))
  }

  ggplot2::geom_text(
    data = note_df,
    ggplot2::aes(x = .data$x, y = .data$y, label = .data$label),
    inherit.aes = FALSE,
    hjust = hjust,
    vjust = vjust,
    size = cfg$label_size,
    color = visual_neutral_palette()$text
  )
}

chart_caption_from_config <- function(data = NULL, config = list(), caption = NULL) {
  wrap_caption <- function(text, width = NULL) {
    if (!is_nonempty_string(text) || is.null(width) || !is.finite(width) || width <= 0) {
      return(text)
    }
    paste(strwrap(text, width = width), collapse = "\n")
  }

  if (!is.null(caption)) {
    cfg <- resolve_chart_config(config = config)
    return(wrap_caption(caption, cfg$caption_wrap_width))
  }

  cfg <- resolve_chart_config(config = config)
  wrap_caption(build_chart_notes(
    source = extract_chart_metadata(data, "source"),
    vintage = extract_chart_metadata(data, "vintage"),
    side_note = cfg$caption_side_note,
    footer_note = cfg$caption_footer_note,
    methodology_note = cfg$caption_methodology_note
  ), cfg$caption_wrap_width)
}
