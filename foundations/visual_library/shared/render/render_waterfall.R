# Render waterfall chart.

source("visual_library/shared/chart_utils.R")

render_waterfall <- function(data, config = list(), theme = NULL) {
  # Combine visual-library defaults with waterfall-specific display options.
  # Callers usually override titles, units, label format, and optional faceting.
  cfg <- merge_chart_config(
    chart_default_config("waterfall"),
    merge_chart_config(
      list(
        value_label = NULL,
        label_style = "number",
        label_accuracy = NULL,
        show_value_labels = TRUE,
        show_connector_lines = TRUE,
        positive_label = "Increase",
        negative_label = "Decrease",
        total_label = "Total",
        total_fill = "#36454F",
        total_text_color = "#FFFFFF",
        connector_color = "#8A96A3",
        connector_linewidth = 0.3,
        label_compact = FALSE,
        bar_width = 0.68,
        facet_by = NULL,
        facet_ncol = NULL,
        rotate_x_labels = TRUE,
        subtitle_wrap_width = 110,
        caption_wrap_width = 125
      ),
      config
    )
  )

  # The renderer expects prep_waterfall() output, not raw contract data. These
  # fields define the cumulative path and the component-vs-total bar behavior.
  ensure_columns(
    data,
    c("component_label", "plot_value", "cumulative_start", "cumulative_end", "waterfall_position", "row_type"),
    chart_type = "waterfall"
  )

  # Freeze component labels in their prepared order and classify bars for the
  # legend/color scale: positive contribution, negative contribution, or total.
  plot_data <- data
  plot_data$component_label <- factor(
    plot_data$component_label,
    levels = unique(plot_data$component_label[order(plot_data$waterfall_position)])
  )
  plot_data$direction <- ifelse(
    plot_data$row_type == "total",
    "total",
    ifelse(plot_data$plot_value >= 0, "positive", "negative")
  )
  plot_data$direction <- factor(
    plot_data$direction,
    levels = c("positive", "negative", "total"),
    labels = c(cfg$positive_label, cfg$negative_label, cfg$total_label)
  )

  # Build reusable value labels and position them just outside each bar. The
  # offset is data-scaled so labels remain legible for both small and large units.
  label_format <- value_label_formatter(
    style = cfg$label_style %||% "number",
    accuracy = cfg$label_accuracy,
    compact = isTRUE(cfg$label_compact)
  )
  plot_data$value_label <- label_format(plot_data$plot_value)
  plot_data$label_y <- ifelse(
    plot_data$cumulative_end >= plot_data$cumulative_start,
    pmax(plot_data$cumulative_start, plot_data$cumulative_end),
    pmin(plot_data$cumulative_start, plot_data$cumulative_end)
  )
  label_offset <- diff(range(c(plot_data$cumulative_start, plot_data$cumulative_end), na.rm = TRUE)) * 0.025
  if (!is.finite(label_offset) || label_offset == 0) {
    label_offset <- max(abs(plot_data$plot_value), na.rm = TRUE) * 0.04
  }
  if (!is.finite(label_offset) || label_offset == 0) {
    label_offset <- 1
  }
  plot_data$label_y <- plot_data$label_y + ifelse(plot_data$plot_value >= 0, label_offset, -label_offset)
  plot_data$label_vjust <- ifelse(plot_data$plot_value >= 0, 0, 1)
  plot_data$bar_ymin <- pmin(plot_data$cumulative_start, plot_data$cumulative_end)
  plot_data$bar_ymax <- pmax(plot_data$cumulative_start, plot_data$cumulative_end)

  # Connector lines show where one component ends and the next begins. Total bars
  # are excluded because they summarize the path rather than continue it.
  connector_data <- plot_data[plot_data$row_type != "total", , drop = FALSE]
  if (nrow(connector_data) > 1) {
    connector_data$x <- connector_data$waterfall_position + (cfg$bar_width / 2)
    connector_data$xend <- connector_data$waterfall_position + 1 - (cfg$bar_width / 2)
    connector_data$y <- connector_data$cumulative_end
    connector_data$yend <- connector_data$cumulative_end
    connector_data <- connector_data[connector_data$xend <= max(plot_data$waterfall_position), , drop = FALSE]
  }

  # Draw waterfall bars as rectangles so each component can start and end at
  # arbitrary cumulative y-values instead of always starting at zero.
  p <- ggplot2::ggplot(plot_data, ggplot2::aes(x = .data$waterfall_position)) +
    ggplot2::geom_rect(
      ggplot2::aes(
        xmin = .data$waterfall_position - (cfg$bar_width / 2),
        xmax = .data$waterfall_position + (cfg$bar_width / 2),
        ymin = .data$bar_ymin,
        ymax = .data$bar_ymax,
        fill = .data$direction
      ),
      color = "white"
    )

  # Add light dashed connectors to reinforce the running-total read without
  # competing with the bar values.
  if (isTRUE(cfg$show_connector_lines) && nrow(connector_data) > 1) {
    p <- p + ggplot2::geom_segment(
      data = connector_data,
      ggplot2::aes(x = .data$x, xend = .data$xend, y = .data$y, yend = .data$yend),
      inherit.aes = FALSE,
      color = cfg$connector_color,
      linewidth = cfg$connector_linewidth,
      linetype = "22"
    )
  }

  # Value labels are optional, but enabled by default because these samples are
  # review artifacts where component magnitudes need to be immediately visible.
  if (isTRUE(cfg$show_value_labels)) {
    p <- p + ggplot2::geom_text(
      ggplot2::aes(
        y = .data$label_y,
        label = .data$value_label,
        vjust = .data$label_vjust
      ),
      size = cfg$label_size,
      color = "#24313F",
      show.legend = FALSE
    )
  }

  # Use numeric x positions for stable bar geometry, then label those positions
  # with the prepared component names. The zero line anchors positive/negative reads.
  p <- p +
    ggplot2::scale_x_continuous(
      breaks = plot_data$waterfall_position,
      labels = as.character(plot_data$component_label),
      expand = ggplot2::expansion(mult = c(0.02, 0.04))
    ) +
    ggplot2::scale_fill_manual(
      values = stats::setNames(
        c(cfg$positive_fill, cfg$negative_fill, cfg$total_fill),
        c(cfg$positive_label, cfg$negative_label, cfg$total_label)
      ),
      name = NULL,
      drop = FALSE
    ) +
    ggplot2::geom_hline(yintercept = 0, color = "#6B7280", linewidth = 0.3)

  # Faceting supports benchmark comparisons by drawing separate cumulative paths
  # for each group rather than mixing them into one additive sequence.
  if (!is.null(cfg$facet_by) && cfg$facet_by %in% names(plot_data)) {
    p <- p + ggplot2::facet_wrap(stats::as.formula(paste("~", cfg$facet_by)), ncol = cfg$facet_ncol)
  }

  # Delegate title/subtitle/caption construction to shared standards helpers so
  # source, vintage, and notes match the rest of the visual library.
  p <- apply_plot_labels(
    p,
    data = plot_data,
    title = cfg$title %||% default_chart_title("waterfall", unique(plot_data$total_label)[1] %||% NULL),
    subtitle = cfg$subtitle,
    x = NULL,
    y = cfg$value_label %||% cfg$y_label,
    caption = chart_caption_from_config(plot_data, cfg)
  )

  # Resolve the shared theme last so caller-provided themes still win, while
  # waterfall-specific readability tweaks such as rotated labels are preserved.
  final_theme <- theme %||% resolve_chart_theme(cfg)
  if (isTRUE(cfg$rotate_x_labels)) {
    final_theme <- final_theme + ggplot2::theme(
      axis.text.x = ggplot2::element_text(angle = 30, hjust = 1)
    )
  }
  if (!is.null(cfg$plot_margin)) {
    final_theme <- final_theme + ggplot2::theme(plot.margin = cfg$plot_margin)
  }

  p + final_theme
}
