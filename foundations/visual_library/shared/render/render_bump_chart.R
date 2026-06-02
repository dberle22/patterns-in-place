# Render bump chart.

source("visual_library/shared/chart_utils.R")

bump_chart_title <- function(data, config) {
  if (is_nonempty_string(config$title)) {
    return(config$title)
  }

  metric_label <- unique(stats::na.omit(data$metric_label))
  metric_label <- if (length(metric_label) > 0) metric_label[[1]] else "Metric"
  geo_levels <- unique(stats::na.omit(data$geo_level))
  geo_label <- if (length(geo_levels) == 1) paste0(geo_levels[[1]], " rank") else "rank"
  paste(metric_label, geo_label, "over time")
}

bump_chart_subtitle <- function(data, config) {
  if (is_nonempty_string(config$subtitle)) {
    return(config$subtitle)
  }

  periods <- sort(unique(stats::na.omit(data$period)))
  parts <- c()
  if (length(periods) > 0) {
    parts <- c(parts, paste("Period:", format_year_range(periods[[1]], periods[[length(periods)]])))
  }

  strategy <- unique(stats::na.omit(data$entity_strategy))
  strategy <- if (length(strategy) > 0) strategy[[1]] else config$entity_strategy %||% "fixed_top_n"
  selection_period <- unique(stats::na.omit(data$selection_period))
  selection_period <- if (length(selection_period) > 0) selection_period[[1]] else NULL
  display_n <- length(unique(stats::na.omit(data$geo_id)))
  entity_text <- switch(
    strategy,
    fixed_top_n = paste0("Fixed top ", display_n, " selected in ", selection_period),
    rolling_top_n = paste0("Entities that entered the rolling top ", config$top_n %||% display_n),
    peer_set = paste0("Fixed peer set, n = ", display_n),
    all = paste0("All filtered entities, n = ", display_n),
    paste0("Displayed entities, n = ", display_n)
  )
  parts <- c(parts, entity_text)

  rank_method <- unique(stats::na.omit(data$rank_method))
  rank_method <- if (length(rank_method) > 0) rank_method[[1]] else "row_number"
  rank_source <- unique(stats::na.omit(data$rank_source))
  rank_source <- if (length(rank_source) > 0) rank_source[[1]] else "derived"
  parts <- c(parts, paste("Rank:", paste(rank_source, rank_method)))

  groups <- if ("group" %in% names(data)) unique(stats::na.omit(data$group)) else character()
  if (length(groups) == 1 && nzchar(groups[[1]])) {
    parts <- c(parts, paste("Universe:", groups[[1]]))
  }

  paste(parts, collapse = " | ")
}

bump_chart_caption_note <- function(data, config) {
  notes <- c()

  if (any(data$highlight_flag %in% TRUE, na.rm = TRUE)) {
    notes <- c(notes, "Highlighted lines mark selected geographies.")
  }
  missing_endpoint_n <- if ("complete_endpoint_flag" %in% names(data)) {
    length(unique(data$geo_id[!(data$complete_endpoint_flag %in% TRUE)]))
  } else {
    0
  }
  if (missing_endpoint_n > 0) {
    notes <- c(notes, paste0(missing_endpoint_n, " displayed entities have a missing start or end rank."))
  }
  rank_method <- unique(stats::na.omit(data$rank_method))
  rank_method <- if (length(rank_method) > 0) rank_method[[1]] else "row_number"
  rank_source <- unique(stats::na.omit(data$rank_source))
  rank_source <- if (length(rank_source) > 0) rank_source[[1]] else "derived"
  if (identical(rank_source, "derived") && identical(rank_method, "row_number")) {
    notes <- c(notes, rank_method_note(rank_source = rank_source, rank_method = rank_method))
  }
  notes <- c(notes, "Rank 1 is plotted at the top; upward movement means moving toward rank 1.")

  paste(compact_chr(c(config$caption_side_note, notes)), collapse = " ")
}

bump_endpoint_labeler <- function(data,
                                  label_style = "number",
                                  label_accuracy = NULL,
                                  max_chars = 34,
                                  include_value = FALSE) {
  shorten_label <- function(x) {
    x <- as.character(x)
    ifelse(nchar(x) > max_chars, paste0(substr(x, 1, max_chars - 3), "..."), x)
  }

  rank_delta <- data$rank_change
  delta_label <- ifelse(
    is.finite(rank_delta) & rank_delta > 0,
    paste0("+", abs(rank_delta)),
    ifelse(is.finite(rank_delta) & rank_delta < 0, paste0("-", abs(rank_delta)), "0")
  )
  base <- paste0(shorten_label(data$geo_name), " (#", round(data$rank), ", ", delta_label, ")")

  if (!isTRUE(include_value)) {
    return(base)
  }

  value_label <- format_value_vector(
    data$metric_value,
    style = label_style,
    accuracy = label_accuracy,
    compact = TRUE
  )
  paste0(base, " ", value_label)
}

render_bump_chart <- function(data, config = list(), theme = NULL) {
  cfg <- resolve_chart_config(
    "bump_chart",
    merge_chart_config(
      list(),
      config
    )
  )

  ensure_columns(data, c("geo_id", "geo_name", "period", "rank"), chart_type = "bump_chart")
  plot_data <- data[order(data$geo_id, data$period), , drop = FALSE]
  plot_data$highlight_flag <- if ("highlight_flag" %in% names(plot_data)) coerce_logical_column(plot_data$highlight_flag) else FALSE
  plot_data$peer_flag <- if ("peer_flag" %in% names(plot_data)) coerce_logical_column(plot_data$peer_flag) else FALSE

  comparison_df <- plot_data[!plot_data$highlight_flag, , drop = FALSE]
  peer_df <- comparison_df[comparison_df$peer_flag %in% TRUE, , drop = FALSE]
  context_df <- comparison_df[!(comparison_df$peer_flag %in% TRUE), , drop = FALSE]
  highlight_df <- plot_data[plot_data$highlight_flag, , drop = FALSE]

  p <- ggplot2::ggplot(plot_data, ggplot2::aes(x = .data$period, y = .data$rank, group = .data$geo_id))

  max_rank <- max(plot_data$rank, na.rm = TRUE)
  if (!is.null(cfg$rank_band_n) && is.finite(cfg$rank_band_n) && cfg$rank_band_n > 0) {
    periods <- range(plot_data$period, na.rm = TRUE)
    band_df <- data.frame(
      xmin = periods[[1]],
      xmax = periods[[2]],
      ymin = 0.5,
      ymax = min(cfg$rank_band_n + 0.5, max_rank + 0.5)
    )
    p <- p +
      ggplot2::geom_rect(
        data = band_df,
        ggplot2::aes(xmin = .data$xmin, xmax = .data$xmax, ymin = .data$ymin, ymax = .data$ymax),
        inherit.aes = FALSE,
        fill = visual_neutral_palette()$background_white,
        color = NA,
        alpha = 0.55
      )
  }

  if (nrow(context_df) > 0) {
    p <- p +
      ggplot2::geom_line(
        data = context_df,
        color = cfg$neutral_color,
        linewidth = cfg$comparison_linewidth,
        alpha = cfg$comparison_alpha,
        na.rm = FALSE
      )
  }
  if (nrow(peer_df) > 0) {
    p <- p +
      ggplot2::geom_line(
        data = peer_df,
        color = cfg$neutral_color,
        linewidth = cfg$comparison_linewidth,
        alpha = cfg$peer_alpha,
        na.rm = FALSE
      )
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
  }

  if (isTRUE(cfg$show_points)) {
    point_df <- plot_data[!plot_data$highlight_flag, , drop = FALSE]
    if (nrow(point_df) > 0) {
      p <- p +
        ggplot2::geom_point(
          data = point_df,
          color = cfg$neutral_color,
          size = cfg$point_size,
          alpha = pmax(ifelse(point_df$peer_flag, cfg$peer_alpha, cfg$comparison_alpha), 0.35),
          na.rm = FALSE
        )
    }
    if (nrow(highlight_df) > 0) {
      p <- p +
        ggplot2::geom_point(
          data = highlight_df,
          color = cfg$highlight_color,
          size = cfg$highlight_point_size,
          alpha = 1,
          na.rm = FALSE
        )
    }
  }

  if (isTRUE(cfg$show_endpoint_labels)) {
    label_df <- endpoint_label_plan(
      plot_data,
      period_col = "period",
      label_mode = cfg$label_mode,
      highlight_col = "highlight_flag",
      rank_col = "rank",
      label_all_max_n = cfg$label_all_max_n,
      label_top_n = cfg$label_top_n,
      endpoint = "end"
    )

    if (nrow(label_df) > 0) {
      label_df$label_text <- bump_endpoint_labeler(
        label_df,
        label_style = cfg$label_style,
        label_accuracy = cfg$label_accuracy,
        max_chars = cfg$label_max_chars,
        include_value = cfg$label_include_value
      )
      x_range <- range(plot_data$period, na.rm = TRUE)
      nudge_x <- max(diff(x_range) * 0.015, 0.12)

      if (requireNamespace("ggrepel", quietly = TRUE)) {
        p <- p +
          ggrepel::geom_text_repel(
            data = label_df,
            ggplot2::aes(x = .data$period + nudge_x, y = .data$rank, label = .data$label_text),
            inherit.aes = FALSE,
            direction = "y",
            hjust = 0,
            min.segment.length = Inf,
            seed = 123,
            force = 0.8,
            force_pull = 0.12,
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
            data = label_df,
            ggplot2::aes(x = .data$period + nudge_x, y = .data$rank, label = .data$label_text),
            inherit.aes = FALSE,
            hjust = 0,
            size = cfg$label_size,
            color = visual_neutral_palette()$text,
            lineheight = 0.95,
            na.rm = TRUE
          )
      }
    }
  }

  periods <- sort(unique(stats::na.omit(plot_data$period)))
  x_breaks <- cfg$x_breaks %||% if (length(periods) <= 10) periods else pretty(periods, n = 6)
  y_breaks <- cfg$y_breaks %||% unique(round(pretty(c(1, max_rank), n = min(max_rank, 8))))
  y_breaks <- y_breaks[y_breaks >= 1 & y_breaks <= max_rank]

  p <- p +
    ggplot2::scale_x_continuous(
      breaks = x_breaks,
      expand = ggplot2::expansion(mult = c(0.015, 0.18))
    ) +
    ggplot2::scale_y_reverse(
      breaks = y_breaks,
      labels = format_rank(),
      limits = c(max_rank + 0.5, 0.5),
      expand = ggplot2::expansion(mult = c(0.02, 0.02))
    ) +
    ggplot2::coord_cartesian(clip = "off")

  p <- apply_plot_labels(
    plot = p,
    data = plot_data,
    title = bump_chart_title(plot_data, cfg),
    subtitle = bump_chart_subtitle(plot_data, cfg),
    x = NULL,
    y = cfg$y_label %||% "Rank (1 = top)",
    side_note = bump_chart_caption_note(plot_data, cfg),
    footer_note = cfg$caption_footer_note,
    methodology_note = cfg$caption_methodology_note
  )

  p + (theme %||% resolve_chart_theme(cfg)) +
    ggplot2::theme(
      axis.title.x = ggplot2::element_blank(),
      legend.position = cfg$legend_position,
      panel.grid.minor = ggplot2::element_blank(),
      plot.margin = ggplot2::margin(t = 12, r = cfg$right_margin_pt, b = 12, l = 12)
    )
}
