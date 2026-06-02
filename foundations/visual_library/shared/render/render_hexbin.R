# Render hexbin or 2D binned scatter.

source("visual_library/shared/chart_utils.R")

hexbin_axis_formatter <- function(style = "number", accuracy = NULL) {
  value_label_formatter(
    style = style,
    accuracy = accuracy
  )
}

hexbin_method_label <- function(method) {
  if (identical(method, "hex")) {
    return("Hexbin")
  }
  "2D bins"
}

hexbin_uses_weights <- function(data, config) {
  if (!is.null(config$use_weights)) {
    return(isTRUE(config$use_weights))
  }
  if (!("weight_value" %in% names(data))) {
    return(FALSE)
  }

  weights <- suppressWarnings(as.numeric(data$weight_value))
  weights <- weights[is.finite(weights)]
  length(weights) > 0 && any(abs(weights - 1) > 1e-9)
}

build_hexbin_title <- function(data, config) {
  if (is_nonempty_string(config$title)) {
    return(config$title)
  }

  x_label <- unique(stats::na.omit(data$x_label))
  y_label <- unique(stats::na.omit(data$y_label))
  x_label <- if (length(x_label) > 0) x_label[[1]] else "X"
  y_label <- if (length(y_label) > 0) y_label[[1]] else "Y"

  paste("Density of", y_label, "vs", x_label)
}

build_hexbin_subtitle <- function(data, config, method, weighted) {
  if (is_nonempty_string(config$subtitle)) {
    return(config$subtitle)
  }

  windows <- unique(stats::na.omit(data$time_window))
  groups <- if (!is.null(config$facet_by) && config$facet_by %in% names(data)) {
    unique(stats::na.omit(data[[config$facet_by]]))
  } else {
    character()
  }

  parts <- c()

  if (length(windows) == 1) {
    parts <- c(parts, paste("Time window:", windows[[1]]))
  }

  parts <- c(
    parts,
    paste(
      hexbin_method_label(method),
      "| Fill =",
      if (isTRUE(weighted)) config$weight_label %||% "weighted sum" else "count"
    )
  )

  if (length(groups) > 1 && !is.null(config$facet_by)) {
    parts <- c(parts, paste("Faceted by", gsub("_", " ", config$facet_by)))
  }

  paste(parts, collapse = " | ")
}

build_hexbin_caption_note <- function(data, config, weighted) {
  notes <- c(config$caption_side_note)

  if (isTRUE(weighted)) {
    notes <- c(notes, "Color intensity reflects weighted mass rather than raw observation count.")
  }
  if ("highlight_flag" %in% names(data) && any(data$highlight_flag %in% TRUE, na.rm = TRUE)) {
    notes <- c(notes, "Highlighted points are overlaid for a small selected subset.")
  }

  paste(compact_chr(notes), collapse = " ")
}

render_hexbin <- function(data, config = list(), theme = NULL) {
  cfg <- resolve_chart_config(
    "hexbin",
    merge_chart_config(
      list(
        method = "hex",
        bins = 28,
        binwidth = NULL,
        facet_by = NULL,
        use_weights = NULL,
        weight_label = NULL,
        overlay_highlights = TRUE,
        add_reference_lines = FALSE,
        reference_method = "median",
        legend_title = NULL,
        label_style_x = "number",
        label_style_y = "number",
        label_accuracy_x = NULL,
        label_accuracy_y = NULL,
        x_limits = NULL,
        y_limits = NULL
      ),
      config
    )
  )

  ensure_columns(data, c("x_value", "y_value", "x_label", "y_label"), chart_type = "hexbin")

  plot_data <- data
  method <- if (identical(cfg$method, "rect")) "rect" else "hex"
  weighted <- hexbin_uses_weights(plot_data, cfg)

  if ("highlight_flag" %in% names(plot_data)) {
    plot_data$highlight_flag <- coerce_logical_column(plot_data$highlight_flag)
  } else {
    plot_data$highlight_flag <- FALSE
  }
  if ("label_flag" %in% names(plot_data)) {
    plot_data$label_flag <- coerce_logical_column(plot_data$label_flag)
  }

  mapping <- ggplot2::aes(x = .data$x_value, y = .data$y_value)
  if (isTRUE(weighted)) {
    mapping$weight <- quote(.data$weight_value)
  }

  p <- ggplot2::ggplot(plot_data, mapping)

  if (identical(method, "hex") && requireNamespace("hexbin", quietly = TRUE)) {
    if (is.null(cfg$binwidth)) {
      p <- p + ggplot2::stat_bin_hex(bins = cfg$bins)
    } else {
      p <- p + ggplot2::stat_bin_hex(binwidth = cfg$binwidth)
    }
  } else {
    if (is.null(cfg$binwidth)) {
      p <- p + ggplot2::geom_bin_2d(bins = cfg$bins)
    } else {
      p <- p + ggplot2::geom_bin_2d(binwidth = cfg$binwidth)
    }
    method <- "rect"
  }

  p <- p + ggplot2::scale_fill_viridis_c(
    option = "C",
    name = cfg$legend_title %||%
      if (isTRUE(weighted)) cfg$weight_label %||% "Weighted sum" else "Count"
  )

  if (isTRUE(cfg$add_reference_lines)) {
    x_ref <- derive_reference_value(plot_data, "x_value", method = cfg$reference_method)
    y_ref <- derive_reference_value(plot_data, "y_value", method = cfg$reference_method)
    p <- p +
      ggplot2::geom_vline(
        xintercept = x_ref,
        color = cfg$benchmark_color,
        linewidth = cfg$benchmark_linewidth,
        linetype = cfg$benchmark_linetype,
        alpha = cfg$benchmark_alpha
      ) +
      ggplot2::geom_hline(
        yintercept = y_ref,
        color = cfg$benchmark_color,
        linewidth = cfg$benchmark_linewidth,
        linetype = cfg$benchmark_linetype,
        alpha = cfg$benchmark_alpha
      )
  }

  if (isTRUE(cfg$overlay_highlights) &&
      ("highlight_flag" %in% names(plot_data) || "label_flag" %in% names(plot_data))) {
    highlight_df <- pick_label_rows(plot_data)
    if (nrow(highlight_df) > 0) {
      p <- p +
        ggplot2::geom_point(
          data = highlight_df,
          ggplot2::aes(x = .data$x_value, y = .data$y_value),
          inherit.aes = FALSE,
          shape = 21,
          size = 2.3,
          stroke = 0.8,
          fill = visual_neutral_palette()$background_white,
          color = cfg$highlight_color
        )

      label_map <- ggplot2::aes(
        x = .data$x_value,
        y = .data$y_value,
        label = .data$geo_name
      )
      p <- p + label_layer(
        data = highlight_df,
        mapping = label_map,
        config = cfg,
        boxed = TRUE,
        repel = TRUE
      )
    }
  }

  if (!is.null(cfg$facet_by) && cfg$facet_by %in% names(plot_data)) {
    p <- p + ggplot2::facet_wrap(
      stats::as.formula(paste("~", cfg$facet_by)),
      ncol = cfg$facet_ncol %||% NULL
    )
  }

  p <- p +
    ggplot2::scale_x_continuous(
      labels = hexbin_axis_formatter(cfg$label_style_x, cfg$label_accuracy_x),
      expand = ggplot2::expansion(mult = c(0.02, 0.03))
    ) +
    ggplot2::scale_y_continuous(
      labels = hexbin_axis_formatter(cfg$label_style_y, cfg$label_accuracy_y),
      expand = ggplot2::expansion(mult = c(0.02, 0.04))
    ) +
    ggplot2::coord_cartesian(
      xlim = cfg$x_limits,
      ylim = cfg$y_limits,
      clip = "off"
    )

  p <- apply_plot_labels(
    p,
    data = plot_data,
    title = build_hexbin_title(plot_data, cfg),
    subtitle = build_hexbin_subtitle(plot_data, cfg, method = method, weighted = weighted),
    x = unique(stats::na.omit(plot_data$x_label))[1] %||% NULL,
    y = unique(stats::na.omit(plot_data$y_label))[1] %||% NULL,
    side_note = build_hexbin_caption_note(plot_data, cfg, weighted = weighted),
    footer_note = cfg$caption_footer_note,
    methodology_note = cfg$caption_methodology_note
  )

  p + (theme %||% resolve_chart_theme(cfg)) +
    ggplot2::theme(
      legend.title = ggplot2::element_text(color = visual_neutral_palette()$text),
      panel.grid.minor = ggplot2::element_blank()
    )
}
