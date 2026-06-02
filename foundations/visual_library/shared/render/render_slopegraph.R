# Render slopegraph.

source("visual_library/shared/chart_utils.R")

slopegraph_axis_formatter <- function(label_style = "number", accuracy = NULL) {
  if (identical(label_style, "dollar")) {
    return(scales::label_dollar(accuracy = accuracy %||% 1))
  }

  value_label_formatter(
    style = label_style,
    accuracy = accuracy
  )
}

slopegraph_value_labeler <- function(values, label_style = "number", accuracy = NULL) {
  if (identical(label_style, "dollar")) {
    return(scales::label_dollar(accuracy = accuracy %||% 1)(values))
  }

  format_value_vector(
    values,
    style = label_style,
    accuracy = accuracy,
    compact = TRUE
  )
}

build_slopegraph_title <- function(data, config) {
  if (is_nonempty_string(config$title)) {
    return(config$title)
  }

  metric_label <- unique(stats::na.omit(data$metric_label))
  metric_label <- if (length(metric_label) > 0) metric_label[[1]] else "Slopegraph"
  geo_levels <- unique(stats::na.omit(data$geo_level))
  geo_label <- if (length(geo_levels) == 1) paste0(geo_levels[[1]], "s") else "geographies"
  paste(metric_label, "change across selected", geo_label)
}

build_slopegraph_subtitle <- function(data, config) {
  if (is_nonempty_string(config$subtitle)) {
    return(config$subtitle)
  }

  periods <- sort(unique(stats::na.omit(data$period)))
  parts <- c()
  if (length(periods) == 2) {
    parts <- c(parts, paste("Change window:", format_year_range(periods[[1]], periods[[2]])))
  }

  variant <- unique(stats::na.omit(data$variant))
  variant <- if (length(variant) > 0) variant[[1]] else "value"
  if (identical(variant, "indexed")) {
    parts <- c(parts, paste0("Indexed to ", periods[[1]], " = 100"))
  } else if (identical(variant, "rank")) {
    parts <- c(parts, "Rank view; lower rank is better")
  }

  groups <- if ("group" %in% names(data)) unique(stats::na.omit(data$group)) else character()
  if (length(groups) == 1 && nzchar(groups[[1]])) {
    parts <- c(parts, paste("Scope:", groups[[1]]))
  }

  paste(parts, collapse = " | ")
}

build_slopegraph_caption_note <- function(data, config) {
  notes <- c()

  if ("complete_endpoint_flag" %in% names(data) && any(!data$complete_endpoint_flag, na.rm = TRUE)) {
    notes <- c(notes, "Rows with missing endpoints are excluded from the plotted comparison.")
  }
  if (isTRUE(any(data$highlight_flag %in% TRUE, na.rm = TRUE))) {
    notes <- c(notes, "Highlighted lines mark selected geographies.")
  }
  if (isTRUE(any(data$benchmark_flag %in% TRUE, na.rm = TRUE))) {
    notes <- c(notes, "Benchmark line is styled as a dashed reference series.")
  }
  if (identical(unique(stats::na.omit(data$variant))[1] %||% NULL, "indexed")) {
    notes <- c(notes, "Indexed values emphasize relative movement rather than absolute levels.")
  }

  paste(compact_chr(c(config$caption_side_note, notes)), collapse = " ")
}

render_slopegraph <- function(data, config = list(), theme = NULL) {
  cfg <- resolve_chart_config(
    "slopegraph",
    merge_chart_config(
      list(
        label_style = "number",
        label_accuracy = NULL,
        show_endpoint_labels = TRUE,
        label_mode = "end",
        label_max_chars = 36,
        show_delta_labels = TRUE,
        delta_label_style = NULL,
        delta_label_accuracy = NULL,
        show_points = TRUE,
        x_expand = c(0.25, 0.44),
        y_limits = NULL,
        start_at_zero = FALSE,
        legend_position = "bottom",
        comparison_linewidth = 0.85,
        highlight_linewidth = 1.25,
        benchmark_linewidth = 1,
        right_margin_pt = 130
      ),
      config
    )
  )

  ensure_columns(data, c("geo_id", "geo_name", "period", "metric_value"), chart_type = "slopegraph")
  plot_data <- data
  y_var <- if ("plot_value" %in% names(plot_data)) "plot_value" else "metric_value"
  if (!("highlight_flag" %in% names(plot_data))) plot_data$highlight_flag <- FALSE
  if (!("benchmark_flag" %in% names(plot_data))) plot_data$benchmark_flag <- FALSE
  plot_data$highlight_flag <- coerce_logical_column(plot_data$highlight_flag)
  plot_data$benchmark_flag <- coerce_logical_column(plot_data$benchmark_flag)
  plot_data$period_label <- if ("period_label" %in% names(plot_data)) as.character(plot_data$period_label) else as.character(plot_data$period)

  periods <- sort(unique(stats::na.omit(plot_data$period)))
  if (length(periods) != 2) {
    stop("render_slopegraph() requires exactly two periods in the prepared data.")
  }

  plot_data$x_pos <- ifelse(plot_data$period == periods[[1]], 1, 2)

  comparison_df <- plot_data[!plot_data$highlight_flag & !plot_data$benchmark_flag, , drop = FALSE]
  highlight_df <- plot_data[plot_data$highlight_flag & !plot_data$benchmark_flag, , drop = FALSE]
  benchmark_df <- plot_data[plot_data$benchmark_flag, , drop = FALSE]

  p <- ggplot2::ggplot(plot_data, ggplot2::aes(x = .data$x_pos, y = .data[[y_var]], group = .data$geo_id))

  if (nrow(comparison_df) > 0) {
    p <- p +
      ggplot2::geom_line(
        data = comparison_df,
        color = cfg$neutral_color,
        linewidth = cfg$comparison_linewidth,
        alpha = 0.78,
        na.rm = FALSE
      )
    if (isTRUE(cfg$show_points)) {
      p <- p +
        ggplot2::geom_point(
          data = comparison_df,
          color = cfg$neutral_color,
          size = 1.8,
          alpha = 0.82,
          na.rm = FALSE
        )
    }
  }

  if (nrow(benchmark_df) > 0) {
    p <- p +
      ggplot2::geom_line(
        data = benchmark_df,
        color = cfg$benchmark_color,
        linewidth = cfg$benchmark_linewidth,
        linetype = cfg$benchmark_linetype,
        alpha = cfg$benchmark_alpha,
        na.rm = FALSE
      )
    if (isTRUE(cfg$show_points)) {
      p <- p +
        ggplot2::geom_point(
          data = benchmark_df,
          color = cfg$benchmark_color,
          size = 2,
          alpha = cfg$benchmark_alpha,
          na.rm = FALSE
        )
    }
  }

  if (nrow(highlight_df) > 0) {
    p <- p +
      ggplot2::geom_line(
        data = highlight_df,
        color = cfg$highlight_color,
        linewidth = cfg$highlight_linewidth,
        alpha = 1,
        na.rm = FALSE
      )
    if (isTRUE(cfg$show_points)) {
      p <- p +
        ggplot2::geom_point(
          data = highlight_df,
          color = cfg$highlight_color,
          size = 2.2,
          alpha = 1,
          na.rm = FALSE
        )
    }
  }

  if (isTRUE(cfg$show_endpoint_labels)) {
    shorten_label <- function(x, max_chars = NULL) {
      x <- as.character(x)
      if (is.null(max_chars) || !is.finite(max_chars) || max_chars <= 4) {
        return(x)
      }
      ifelse(nchar(x) > max_chars, paste0(substr(x, 1, max_chars - 3), "..."), x)
    }

    label_data <- plot_data
    if (identical(cfg$label_mode, "end")) {
      label_data <- label_data[label_data$period == periods[[2]], , drop = FALSE]
    } else if (identical(cfg$label_mode, "highlight_end")) {
      label_data <- label_data[label_data$period == periods[[2]] & (label_data$highlight_flag | label_data$benchmark_flag), , drop = FALSE]
    } else if (identical(cfg$label_mode, "highlight_both")) {
      label_data <- label_data[label_data$highlight_flag | label_data$benchmark_flag, , drop = FALSE]
    }

    label_data$value_label <- slopegraph_value_labeler(
      label_data[[y_var]],
      label_style = cfg$label_style,
      accuracy = cfg$label_accuracy
    )
    label_data$delta_label <- slopegraph_value_labeler(
      label_data$delta_value,
      label_style = cfg$delta_label_style %||% cfg$label_style,
      accuracy = cfg$delta_label_accuracy %||% cfg$label_accuracy
    )
    label_data$label_name <- shorten_label(label_data$geo_name, cfg$label_max_chars)
    label_data$label_text <- ifelse(
      label_data$period == periods[[2]] & isTRUE(cfg$show_delta_labels) & is.finite(label_data$delta_value),
      paste0(label_data$label_name, " (", ifelse(label_data$delta_value > 0, "+", ""), label_data$delta_label, ")"),
      paste0(label_data$label_name, " (", label_data$value_label, ")")
    )
    label_data$hjust <- ifelse(label_data$x_pos == 1, 1, 0)
    label_data$nudge_x <- ifelse(label_data$x_pos == 1, -0.045, 0.045)

    label_mapping <- ggplot2::aes(
      x = .data$x_pos + .data$nudge_x,
      y = .data[[y_var]],
      label = .data$label_text
    )

    if (requireNamespace("ggrepel", quietly = TRUE)) {
      p <- p +
        ggrepel::geom_text_repel(
          data = label_data,
          label_mapping,
          inherit.aes = FALSE,
          hjust = label_data$hjust,
          direction = "y",
          min.segment.length = Inf,
          seed = 123,
          force = 0.8,
          force_pull = 0.15,
          box.padding = 0.08,
          point.padding = 0.05,
          max.overlaps = Inf,
          size = cfg$label_size,
          color = visual_neutral_palette()$text,
          lineheight = 0.95,
          na.rm = TRUE
        )
    } else {
      p <- p +
        ggplot2::geom_text(
        data = label_data,
        label_mapping,
        inherit.aes = FALSE,
        hjust = label_data$hjust,
        size = cfg$label_size,
        color = visual_neutral_palette()$text,
        lineheight = 0.95,
        na.rm = TRUE
      )
    }
  }

  formatter <- slopegraph_axis_formatter(cfg$label_style, cfg$label_accuracy)
  variant <- unique(stats::na.omit(plot_data$variant))
  variant <- if (length(variant) > 0) variant[[1]] else "value"

  y_limits <- cfg$y_limits
  if (is.null(y_limits) && isTRUE(cfg$start_at_zero) && !identical(variant, "rank")) {
    y_limits <- c(min(0, min(plot_data[[y_var]], na.rm = TRUE)), NA_real_)
  }

  p <- p +
    ggplot2::scale_x_continuous(
      breaks = c(1, 2),
      labels = as.character(periods),
      expand = ggplot2::expansion(mult = cfg$x_expand)
    ) +
    ggplot2::scale_y_continuous(
      labels = formatter,
      limits = y_limits,
      trans = if (identical(variant, "rank")) "reverse" else "identity",
      expand = ggplot2::expansion(mult = c(0.08, 0.08))
    ) +
    ggplot2::coord_cartesian(clip = "off")

  p <- apply_plot_labels(
    p,
    data = data,
    title = build_slopegraph_title(plot_data, cfg),
    subtitle = build_slopegraph_subtitle(plot_data, cfg),
    x = NULL,
    y = cfg$y_label %||% if (identical(variant, "indexed")) {
      paste0(unique(stats::na.omit(plot_data$metric_label))[1] %||% "Index", " (", periods[[1]], " = 100)")
    } else if (identical(variant, "rank")) {
      "Rank"
    } else {
      unique(stats::na.omit(plot_data$metric_label))[1] %||% NULL
    },
    side_note = build_slopegraph_caption_note(plot_data, cfg),
    footer_note = cfg$caption_footer_note,
    methodology_note = cfg$caption_methodology_note
  )

  p + (theme %||% resolve_chart_theme(cfg)) +
    ggplot2::theme(
      axis.title.x = ggplot2::element_blank(),
      panel.grid.major.x = ggplot2::element_blank(),
      panel.grid.minor = ggplot2::element_blank(),
      legend.position = "none",
      plot.margin = ggplot2::margin(t = 12, r = cfg$right_margin_pt, b = 12, l = 12)
    )
}
