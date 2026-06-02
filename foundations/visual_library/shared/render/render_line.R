# Render line chart from prepared line data.

source("visual_library/shared/chart_utils.R")

line_axis_formatter <- function(label_style = "number", accuracy = NULL) {
  if (identical(label_style, "dollar")) {
    return(scales::label_dollar(accuracy = accuracy %||% 1))
  }

  value_label_formatter(
    style = label_style,
    accuracy = accuracy
  )
}

build_line_title <- function(data, config) {
  if (is_nonempty_string(config$title)) {
    return(config$title)
  }

  metric_label <- unique(stats::na.omit(data$metric_label))
  metric_label <- if (length(metric_label) > 0) metric_label[[1]] else "Line Chart"

  geo_names <- unique(stats::na.omit(data$geo_name))
  highlight_names <- if ("highlight_flag" %in% names(data)) {
    unique(stats::na.omit(data$geo_name[coerce_logical_column(data$highlight_flag)]))
  } else {
    character()
  }

  if (length(geo_names) == 1) {
    return(paste(metric_label, geo_names[[1]], sep = ": "))
  }
  if (length(highlight_names) == 1) {
    return(paste(metric_label, paste0(highlight_names[[1]], " vs peers"), sep = ": "))
  }

  paste(metric_label, "selected geographies", sep = ": ")
}

build_line_subtitle <- function(data, config) {
  if (is_nonempty_string(config$subtitle)) {
    return(config$subtitle)
  }

  periods <- sort(unique(stats::na.omit(data$period)))
  parts <- c()

  if (length(periods) > 0) {
    parts <- c(parts, paste("Period:", format_year_range(min(periods), max(periods))))
  }

  variant <- unique(stats::na.omit(data$variant))
  variant <- if (length(variant) > 0) variant[[1]] else NULL
  if (identical(variant, "indexed")) {
    base_period <- unique(stats::na.omit(data$index_base_period))
    if (length(base_period) > 0) {
      parts <- c(parts, paste("Indexed to", base_period[[1]], "= 100"))
    } else {
      parts <- c(parts, "Indexed series")
    }
  } else if (identical(variant, "rolling")) {
    time_window <- unique(stats::na.omit(data$time_window))
    if (length(time_window) > 0) {
      parts <- c(parts, paste("Transform:", time_window[[1]]))
    }
  }

  groups <- unique(stats::na.omit(data$group))
  if (length(groups) == 1) {
    parts <- c(parts, paste("Scope:", groups[[1]]))
  }

  paste(parts, collapse = " | ")
}

build_line_caption_note <- function(data, config) {
  notes <- c()

  if ("highlight_flag" %in% names(data) && any(data$highlight_flag %in% TRUE, na.rm = TRUE) &&
      length(unique(stats::na.omit(data$geo_name))) > 1) {
    notes <- c(notes, "Selected metro highlighted.")
  }

  if (identical(unique(stats::na.omit(data$variant))[1] %||% NULL, "indexed")) {
    notes <- c(notes, "Indexed lines show pace of change rather than absolute level.")
  }

  missing_rows <- sum(!is.finite(data$plot_value %||% data$metric_value))
  if (missing_rows > 0) {
    notes <- c(notes, "Missing periods are left as gaps.")
  }

  paste(compact_chr(c(config$caption_side_note, notes)), collapse = " ")
}

render_line <- function(data, config = list(), theme = NULL) {
  cfg <- resolve_chart_config(
    "line",
    merge_chart_config(
      list(
        color_mode = NULL,
        facet_by = NULL,
        show_points = TRUE,
        add_benchmark = FALSE,
        label_style = "number",
        label_accuracy = NULL,
        legend_position = NULL,
        start_at_zero = TRUE,
        y_limits = NULL,
        x_breaks = NULL
      ),
      config
    )
  )
  ensure_columns(data, c("period", "geo_name"), chart_type = "line")

  plot_data <- data[order(data$geo_name, data$period), , drop = FALSE]
  y_var <- if ("plot_value" %in% names(plot_data)) "plot_value" else "metric_value"
  variant <- unique(stats::na.omit(plot_data$variant))
  variant <- if (length(variant) > 0) variant[[1]] else NULL

  if (is.null(cfg$legend_position)) {
    cfg$legend_position <- if (length(unique(stats::na.omit(plot_data$geo_name))) <= 1) "none" else "bottom"
  }

  color_mode <- cfg$color_mode %||% "geo_name"

  p <- ggplot2::ggplot(plot_data, ggplot2::aes(x = .data$period, y = .data[[y_var]]))

  if (identical(color_mode, "highlight_flag") && "highlight_flag" %in% names(plot_data)) {
    plot_data$highlight_flag <- coerce_logical_column(plot_data$highlight_flag)
    comparison_df <- plot_data[!plot_data$highlight_flag, , drop = FALSE]
    highlight_df <- plot_data[plot_data$highlight_flag, , drop = FALSE]

    if (nrow(comparison_df) > 0) {
      p <- p +
        ggplot2::geom_line(
          data = comparison_df,
          ggplot2::aes(group = .data$geo_name, color = "Comparison"),
          linewidth = 0.9,
          alpha = 0.7,
          na.rm = FALSE
        )
      if (isTRUE(cfg$show_points)) {
        p <- p +
          ggplot2::geom_point(
            data = comparison_df,
            ggplot2::aes(group = .data$geo_name, color = "Comparison"),
            size = 1.6,
            alpha = 0.7,
            na.rm = FALSE
          )
      }
    }

    if (nrow(highlight_df) > 0) {
      p <- p +
        ggplot2::geom_line(
          data = highlight_df,
          ggplot2::aes(group = .data$geo_name, color = "Selected"),
          linewidth = 1.25,
          alpha = 1,
          na.rm = FALSE
        )
      if (isTRUE(cfg$show_points)) {
        p <- p +
          ggplot2::geom_point(
            data = highlight_df,
            ggplot2::aes(group = .data$geo_name, color = "Selected"),
            size = 2,
            alpha = 1,
            na.rm = FALSE
          )
      }
    }

    p <- p + ggplot2::scale_color_manual(
      values = c("Comparison" = cfg$neutral_color, "Selected" = cfg$highlight_color),
      name = NULL
    )
  } else {
    has_highlight <- "highlight_flag" %in% names(plot_data) && any(plot_data$highlight_flag %in% TRUE, na.rm = TRUE)

    if (has_highlight) {
      plot_data$highlight_flag <- coerce_logical_column(plot_data$highlight_flag)
    } else {
      plot_data$highlight_flag <- FALSE
    }

    peer_names <- unique(stats::na.omit(plot_data$geo_name[!plot_data$highlight_flag]))
    peer_palette <- resolve_peer_palette(
      max(length(peer_names), 1),
      palette = cfg$peer_palette
    )
    color_values <- stats::setNames(peer_palette[seq_along(peer_names)], peer_names)

    highlight_names <- unique(stats::na.omit(plot_data$geo_name[plot_data$highlight_flag]))
    if (length(highlight_names) > 0) {
      color_values[highlight_names] <- cfg$highlight_color
    }

    comparison_df <- plot_data[!plot_data$highlight_flag, , drop = FALSE]
    highlight_df <- plot_data[plot_data$highlight_flag, , drop = FALSE]

    if (nrow(comparison_df) > 0) {
      p <- p +
        ggplot2::geom_line(
          data = comparison_df,
          ggplot2::aes(color = .data$geo_name, group = .data$geo_name),
          linewidth = 0.95,
          alpha = 0.82,
          na.rm = FALSE
        )
      if (isTRUE(cfg$show_points)) {
        p <- p +
          ggplot2::geom_point(
            data = comparison_df,
            ggplot2::aes(color = .data$geo_name, group = .data$geo_name),
            size = 1.7,
            alpha = 0.8,
            na.rm = FALSE
          )
      }
    }

    if (nrow(highlight_df) > 0) {
      p <- p +
        ggplot2::geom_line(
          data = highlight_df,
          ggplot2::aes(color = .data$geo_name, group = .data$geo_name),
          linewidth = 1.25,
          alpha = 1,
          na.rm = FALSE
        )
      if (isTRUE(cfg$show_points)) {
        p <- p +
          ggplot2::geom_point(
            data = highlight_df,
            ggplot2::aes(color = .data$geo_name, group = .data$geo_name),
            size = 2,
            alpha = 1,
            na.rm = FALSE
          )
      }
    }

    p <- p + ggplot2::scale_color_manual(values = color_values, name = NULL)
  }

  if (!is.null(cfg$facet_by) && cfg$facet_by %in% names(plot_data)) {
    p <- p + ggplot2::facet_wrap(stats::as.formula(paste("~", cfg$facet_by)), scales = "free_y")
  }

  if (isTRUE(cfg$add_benchmark) && "benchmark_value" %in% names(plot_data)) {
    bench <- plot_data[is.finite(plot_data$benchmark_value), c("period", "benchmark_value")]
    if (nrow(bench) > 0) {
      bench <- stats::aggregate(benchmark_value ~ period, data = bench, FUN = mean)
      p <- p + ggplot2::geom_line(
        data = bench,
        ggplot2::aes(x = .data$period, y = .data$benchmark_value),
        inherit.aes = FALSE,
        linewidth = cfg$benchmark_linewidth,
        linetype = cfg$benchmark_linetype,
        color = cfg$benchmark_color,
        alpha = cfg$benchmark_alpha
      )
    }
  }

  x_breaks <- cfg$x_breaks
  if (is.null(x_breaks)) {
    periods <- sort(unique(stats::na.omit(plot_data$period)))
    x_breaks <- if (length(periods) <= 12) periods else pretty(periods, n = 6)
  }

  p <- p + ggplot2::scale_x_continuous(
    breaks = x_breaks,
    expand = ggplot2::expansion(mult = c(0.01, 0.03))
  )

  p <- p + ggplot2::scale_y_continuous(
    labels = line_axis_formatter(cfg$label_style, cfg$label_accuracy),
    limits = cfg$y_limits %||% c(
      if (isTRUE(cfg$start_at_zero)) {
        min(0, min(plot_data[[y_var]], na.rm = TRUE))
      } else {
        NA_real_
      },
      NA_real_
    ),
    expand = ggplot2::expansion(mult = c(0.04, if (identical(variant, "indexed")) 0.08 else 0.06))
  )

  p <- apply_plot_labels(
    plot = p,
    data = plot_data,
    title = build_line_title(plot_data, cfg),
    subtitle = build_line_subtitle(plot_data, cfg),
    x = NULL,
    y = cfg$y_label %||% if (identical(variant, "indexed")) {
      paste0(unique(stats::na.omit(plot_data$metric_label))[1] %||% "Index", " (", unique(stats::na.omit(plot_data$index_base_period))[1] %||% "base", " = 100)")
    } else {
      unique(stats::na.omit(plot_data$metric_label))[1] %||% NULL
    },
    side_note = build_line_caption_note(plot_data, cfg),
    footer_note = cfg$caption_footer_note,
    methodology_note = cfg$caption_methodology_note
  )

  p + (theme %||% resolve_chart_theme(cfg)) +
    ggplot2::theme(
      axis.title.x = ggplot2::element_blank(),
      legend.title = ggplot2::element_blank(),
      panel.grid.minor = ggplot2::element_blank()
    )
}
