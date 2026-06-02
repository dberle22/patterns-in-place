# Render strength strip.

source("visual_library/shared/chart_utils.R")

strength_strip_palette <- function(data, cfg) {
  geo_names <- unique(as.character(data$geo_name))
  geo_names <- geo_names[!is.na(geo_names)]

  if (length(geo_names) <= 1) {
    return(stats::setNames(cfg$highlight_color, geo_names))
  }

  palette <- stats::setNames(
    resolve_peer_palette(length(geo_names), palette = cfg$peer_palette),
    geo_names
  )

  if ("highlight_flag" %in% names(data) && any(data$highlight_flag %in% TRUE, na.rm = TRUE)) {
    highlight_names <- unique(as.character(data$geo_name[data$highlight_flag %in% TRUE]))
    palette[highlight_names] <- cfg$highlight_color
  }

  palette
}

render_strength_strip <- function(data, config = list(), theme = NULL) {
  cfg <- resolve_chart_config(
    "strength_strip",
    merge_chart_config(
      list(
        title = NULL,
        subtitle = NULL,
        x_label = "Percentile within comparison universe",
        facet_by = NULL,
        show_benchmark = TRUE,
        show_legend = NULL,
        show_missing_labels = TRUE,
        strip_linewidth = 5,
        value_linewidth = 5,
        point_size = 3.4,
        benchmark_size = 7,
        missing_label = "Missing",
        missing_label_x = 103,
        right_margin_pt = 26
      ),
      config
    )
  )

  ensure_columns(
    data,
    c("metric_label", "metric_display_label", "normalized_value", "geo_name"),
    chart_type = "strength_strip"
  )

  plot_data <- data
  metric_levels <- unique(as.character(plot_data$metric_display_label[order(plot_data$metric_order)]))
  plot_data$metric_display_label <- factor(
    plot_data$metric_display_label,
    levels = rev(metric_levels)
  )

  facet_by <- cfg$facet_by
  if (is.null(facet_by) && "time_window" %in% names(plot_data)) {
    facet_values <- unique(stats::na.omit(plot_data$time_window))
    if (length(facet_values) > 1) {
      facet_by <- "time_window"
    }
  }

  strip_data <- unique(plot_data[, intersect(
    c("metric_display_label", "time_window", "benchmark_normalized_value", "benchmark_label"),
    names(plot_data)
  ), drop = FALSE])
  strip_data$x_start <- 0
  strip_data$x_end <- 100

  palette <- strength_strip_palette(plot_data, cfg)
  show_legend <- cfg$show_legend %||% (length(unique(as.character(plot_data$geo_name))) > 1)
  single_geo <- length(unique(as.character(plot_data$geo_name))) == 1

  p <- ggplot2::ggplot() +
    ggplot2::geom_segment(
      data = strip_data,
      ggplot2::aes(
        x = .data$x_start,
        xend = .data$x_end,
        y = .data$metric_display_label,
        yend = .data$metric_display_label
      ),
      linewidth = cfg$strip_linewidth,
      color = cfg$neutral_color,
      alpha = 0.45,
      lineend = "round"
    )

  if (isTRUE(single_geo)) {
    value_data <- plot_data[is.finite(plot_data$normalized_value), , drop = FALSE]
    p <- p +
      ggplot2::geom_segment(
        data = value_data,
        ggplot2::aes(
          x = 0,
          xend = .data$normalized_value,
          y = .data$metric_display_label,
          yend = .data$metric_display_label,
          color = .data$geo_name
        ),
        linewidth = cfg$value_linewidth,
        lineend = "round",
        show.legend = show_legend
      )
  }

  p <- p +
    ggplot2::geom_point(
      data = plot_data[is.finite(plot_data$normalized_value), , drop = FALSE],
      ggplot2::aes(
        x = .data$normalized_value,
        y = .data$metric_display_label,
        color = .data$geo_name
      ),
      size = cfg$point_size,
      alpha = 0.95,
      show.legend = show_legend
    )

  if (isTRUE(cfg$show_benchmark) && "benchmark_normalized_value" %in% names(strip_data)) {
    benchmark_data <- strip_data[is.finite(strip_data$benchmark_normalized_value), , drop = FALSE]
    if (nrow(benchmark_data) > 0) {
      p <- p +
        ggplot2::geom_point(
          data = benchmark_data,
          ggplot2::aes(
            x = .data$benchmark_normalized_value,
            y = .data$metric_display_label
          ),
          inherit.aes = FALSE,
          shape = 124,
          size = cfg$benchmark_size,
          stroke = 1,
          color = cfg$benchmark_color
        )
    }
  }

  if (isTRUE(cfg$show_missing_labels)) {
    missing_data <- plot_data[plot_data$missing_flag %in% TRUE, , drop = FALSE]
    if (nrow(missing_data) > 0) {
      missing_data$missing_label_text <- if (single_geo) {
        cfg$missing_label
      } else {
        paste(as.character(missing_data$geo_name), "missing")
      }

      p <- p +
        ggplot2::geom_text(
          data = missing_data,
          ggplot2::aes(
            x = cfg$missing_label_x,
            y = .data$metric_display_label,
            label = .data$missing_label_text
          ),
          inherit.aes = FALSE,
          hjust = 0,
          color = visual_neutral_palette()$text_muted,
          size = cfg$label_size * 0.9
        )
    }
  }

  p <- p +
    ggplot2::scale_color_manual(values = palette, drop = FALSE) +
    ggplot2::scale_x_continuous(
      limits = c(0, 112),
      breaks = c(0, 25, 50, 75, 100),
      labels = scales::label_number(accuracy = 1),
      expand = ggplot2::expansion(mult = c(0, 0))
    )

  if (!is.null(facet_by) && facet_by %in% names(plot_data)) {
    p <- p + ggplot2::facet_wrap(stats::as.formula(paste("~", facet_by)), ncol = 1, scales = "fixed")
  }

  p <- apply_plot_labels(
    p,
    data = plot_data,
    title = cfg$title %||% "Strength Strip",
    subtitle = cfg$subtitle,
    x = cfg$x_label,
    y = NULL,
    side_note = cfg$caption_side_note,
    footer_note = cfg$caption_footer_note,
    methodology_note = cfg$caption_methodology_note
  )

  p + (theme %||% resolve_chart_theme(cfg)) +
    ggplot2::theme(
      axis.title.y = ggplot2::element_blank(),
      panel.grid.major.y = ggplot2::element_blank(),
      panel.grid.minor = ggplot2::element_blank(),
      legend.title = ggplot2::element_blank(),
      plot.margin = ggplot2::margin(t = 12, r = cfg$right_margin_pt, b = 12, l = 12)
    )
}
