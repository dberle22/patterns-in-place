# Shared visual standards helpers for chart rendering.

library(ggplot2)
library(scales)

`%||%` <- function(x, y) {
  if (is.null(x)) y else x
}

is_nonempty_string <- function(x) {
  is.character(x) && length(x) > 0 && !is.na(x[[1]]) && nzchar(x[[1]])
}

compact_chr <- function(x) {
  x <- unlist(x, use.names = FALSE)
  x <- x[!is.na(x)]
  x <- trimws(as.character(x))
  x[nzchar(x)]
}

visual_font_family <- function() {
  "Inter"
}

visual_output_mode <- function(mode = NULL) {
  mode <- tolower(mode %||% "notebook")
  if (!mode %in% c("notebook", "presentation")) {
    stop("mode must be one of 'notebook' or 'presentation'.")
  }
  mode
}

visual_neutral_palette <- function() {
  list(
    text = "#1F2933",
    text_muted = "#52606D",
    axis = "#5B6770",
    grid_major = "#D9E2EC",
    grid_minor = "#EEF2F6",
    outline = "#7B8794",
    border = "#CBD2D9",
    background = "#F7FAFC",
    background_white = "#FFFFFF",
    comparison_fill = "#A7B4C2",
    missing_fill = "#E6EBF1"
  )
}

visual_palette_defaults <- function() {
  neutrals <- visual_neutral_palette()
  list(
    sequential = "viridis",
    binned = "viridis",
    highlight = list(
      selection = "#2C7FB8",
      opportunity = "#1D7F5F",
      strength = "#1B6CA8",
      risk = "#C44536"
    ),
    diverging = list(
      better = "#0C7C78",
      midpoint = "#F7F7F5",
      worse = "#D66A4E"
    ),
    quadrant = list(
      high_high = "#1D7F5F",
      high_low = "#2C7FB8",
      low_low = "#C44536",
      low_high = "#B07D00"
    ),
    context = list(
      road = "#AAB7C4",
      water = "#DCEAF7",
      boundary = neutrals$outline,
      internal_boundary = neutrals$border,
      cluster = "#5F6C7B"
    ),
    comparison = list(
      peers = c("#AEBECD", "#6E859E", "#8C9472", "#9A7F6B"),
      neutral = neutrals$comparison_fill,
      benchmark = neutrals$text_muted
    )
  )
}

resolve_highlight_color <- function(meaning = c("selection", "opportunity", "strength", "risk", "neutral"),
                                    fallback = NULL) {
  meaning <- match.arg(meaning)
  palette <- visual_palette_defaults()$highlight
  key <- if (identical(meaning, "neutral")) "selection" else meaning
  palette[[key]] %||% fallback %||% palette$selection
}

visual_mode_defaults <- function(mode = "notebook") {
  mode <- visual_output_mode(mode)
  neutrals <- visual_neutral_palette()

  if (identical(mode, "presentation")) {
    return(list(
      mode = mode,
      base_size = 12.5,
      subtitle_size = 11.2,
      caption_size = 8.9,
      label_size = 3.5,
      show_boxed_map_labels = TRUE,
      annotation_density = "rich",
      benchmark_labels_default = TRUE,
      grid = "y",
      background = neutrals$background
    ))
  }

  list(
    mode = mode,
    base_size = 11.8,
    subtitle_size = 10.4,
    caption_size = 8.3,
    label_size = 3.1,
    show_boxed_map_labels = FALSE,
    annotation_density = "light",
    benchmark_labels_default = FALSE,
    grid = "minimal",
    background = neutrals$background
  )
}

benchmark_style_defaults <- function(mode = "notebook") {
  mode_defaults <- visual_mode_defaults(mode)
  neutrals <- visual_neutral_palette()

  list(
    color = neutrals$text_muted,
    linewidth = 0.5,
    linetype = "22",
    alpha = 0.9,
    text_color = neutrals$text_muted,
    text_size = if (identical(mode_defaults$mode, "presentation")) 3.1 else 2.8,
    text_face = "plain",
    label = isTRUE(mode_defaults$benchmark_labels_default)
  )
}

comparison_palette_defaults <- function() {
  visual_palette_defaults()$comparison
}

map_extent_limits <- function(extent = c("data", "contiguous_us")) {
  extent <- match.arg(extent)
  switch(
    extent,
    data = list(xlim = NULL, ylim = NULL),
    contiguous_us = list(xlim = c(-125, -66), ylim = c(24, 50))
  )
}

build_map_context_layers <- function(us_outline = NULL,
                                     state_outlines = NULL,
                                     show_us_outline = TRUE,
                                     show_state_outlines = TRUE,
                                     us_outline_color = "#8FA1B3",
                                     state_outline_color = "#C4CFD9",
                                     us_outline_linewidth = 0.45,
                                     state_outline_linewidth = 0.2) {
  layers <- list()

  if (isTRUE(show_us_outline) && inherits(us_outline, "sf")) {
    layers <- c(layers, list(list(
      data = us_outline,
      fill = NA,
      color = us_outline_color,
      linewidth = us_outline_linewidth
    )))
  }

  if (isTRUE(show_state_outlines) && inherits(state_outlines, "sf")) {
    layers <- c(layers, list(list(
      data = state_outlines,
      fill = NA,
      color = state_outline_color,
      linewidth = state_outline_linewidth
    )))
  }

  layers
}

resolve_map_composition_preset <- function(preset = NULL, data = NULL, config = list()) {
  preset <- preset %||% "none"
  if (identical(preset, "none")) {
    return(list())
  }

  if (identical(preset, "national_compact")) {
    return(list(
      map_extent = "contiguous_us",
      subtitle_wrap_width = 85,
      caption_wrap_width = 110,
      plot_margin = ggplot2::margin(8, 8, 8, 8),
      border_linewidth = config$border_linewidth %||% 0.12
    ))
  }

  if (identical(preset, "facet_national")) {
    return(list(
      map_extent = "contiguous_us",
      subtitle_wrap_width = 80,
      caption_wrap_width = 110,
      plot_margin = ggplot2::margin(8, 8, 8, 8),
      border_linewidth = config$border_linewidth %||% 0.14,
      state_outline_linewidth = config$state_outline_linewidth %||% 0.18,
      us_outline_linewidth = config$us_outline_linewidth %||% 0.4
    ))
  }

  if (identical(preset, "local_focus")) {
    if (!inherits(data, "sf") || !requireNamespace("sf", quietly = TRUE)) {
      return(list(
        map_extent = "data",
        subtitle_wrap_width = 85,
        caption_wrap_width = 110,
        plot_margin = ggplot2::margin(8, 8, 8, 8)
      ))
    }

    bbox <- sf::st_bbox(data)
    pad_x <- as.numeric((bbox$xmax - bbox$xmin) * (config$local_padding_x %||% 0.04))
    pad_y <- as.numeric((bbox$ymax - bbox$ymin) * (config$local_padding_y %||% 0.04))

    return(list(
      map_extent = "data",
      xlim = c(bbox$xmin - pad_x, bbox$xmax + pad_x),
      ylim = c(bbox$ymin - pad_y, bbox$ymax + pad_y),
      subtitle_wrap_width = 85,
      caption_wrap_width = 110,
      plot_margin = ggplot2::margin(8, 8, 8, 8)
    ))
  }

  stop(sprintf("Unknown map composition preset: %s", preset))
}

resolve_peer_palette <- function(n, palette = NULL) {
  palette <- palette %||% comparison_palette_defaults()$peers
  if (n <= length(palette)) {
    return(palette[seq_len(n)])
  }
  grDevices::colorRampPalette(palette)(n)
}

visual_theme <- function(base_size = 12,
                         base_family = visual_font_family(),
                         mode = "notebook",
                         background = NULL,
                         grid = NULL,
                         legend_position = NULL) {
  mode_defaults <- visual_mode_defaults(mode)
  neutrals <- visual_neutral_palette()
  background <- background %||% mode_defaults$background
  grid <- grid %||% mode_defaults$grid
  legend_position <- legend_position %||% "right"

  theme <- theme_minimal(base_size = base_size, base_family = base_family) +
    theme(
      plot.background = element_rect(fill = background, color = NA),
      panel.background = element_rect(fill = background, color = NA),
      legend.background = element_rect(fill = background, color = NA),
      legend.box.background = element_blank(),
      legend.key = element_rect(fill = background, color = NA),
      legend.position = legend_position,
      legend.justification = c(1, 0),
      legend.title = element_text(
        color = neutrals$text,
        face = "plain",
        size = rel(0.9)
      ),
      legend.text = element_text(
        color = neutrals$text_muted,
        size = rel(0.86)
      ),
      plot.title.position = "plot",
      plot.caption.position = "plot",
      plot.title = element_text(
        color = neutrals$text,
        face = "bold",
        hjust = 0,
        margin = margin(b = 5)
      ),
      plot.subtitle = element_text(
        color = neutrals$text_muted,
        hjust = 0,
        margin = margin(b = 10),
        size = rel(0.92)
      ),
      plot.caption = element_text(
        color = neutrals$text_muted,
        hjust = 0,
        lineheight = 1.15,
        margin = margin(t = 8),
        size = rel(0.78)
      ),
      axis.title = element_text(color = neutrals$text, face = "plain"),
      axis.title.x = element_text(margin = margin(t = 10)),
      axis.title.y = element_text(margin = margin(r = 10)),
      axis.text = element_text(color = neutrals$axis, size = rel(0.86)),
      axis.ticks = element_blank(),
      strip.text = element_text(color = neutrals$text, face = "plain"),
      strip.background = element_rect(fill = background, color = NA),
      panel.grid.major = element_blank(),
      panel.grid.minor = element_blank(),
      panel.spacing = grid::unit(12, "pt"),
      plot.margin = margin(t = 12, r = 16, b = 12, l = 12)
    )

  if (grid %in% c("minimal", "y", "both")) {
    theme <- theme + theme(
      panel.grid.major.y = element_line(color = neutrals$grid_major, linewidth = 0.35)
    )
  }
  if (grid %in% c("x", "both")) {
    theme <- theme + theme(
      panel.grid.major.x = element_line(color = neutrals$grid_major, linewidth = 0.35)
    )
  }
  if (grid %in% c("minor", "both_minor")) {
    theme <- theme + theme(
      panel.grid.minor = element_line(color = neutrals$grid_minor, linewidth = 0.25)
    )
  }

  theme
}

visual_map_theme <- function(base_size = 12,
                             base_family = visual_font_family(),
                             mode = "notebook",
                             background = NULL,
                             legend_position = NULL) {
  visual_theme(
    base_size = base_size,
    base_family = base_family,
    mode = mode,
    background = background,
    grid = "none",
    legend_position = legend_position %||% "right"
  ) +
    theme(
      axis.text = element_blank(),
      axis.title = element_blank(),
      axis.ticks = element_blank(),
      panel.grid = element_blank()
    )
}

format_percent <- function(accuracy = 0.1, scale = 100, suffix = "%") {
  scales::label_number(accuracy = accuracy, scale = scale, suffix = suffix)
}

format_dollar <- function(accuracy = 1,
                          scale_cut = scales::cut_short_scale(),
                          largest_with_cents = 0) {
  scales::label_dollar(
    accuracy = accuracy,
    scale_cut = scale_cut,
    largest_with_cents = largest_with_cents
  )
}

format_number <- function(accuracy = 0.1,
                          scale_cut = scales::cut_short_scale(),
                          big.mark = ",") {
  scales::label_number(
    accuracy = accuracy,
    scale_cut = scale_cut,
    big.mark = big.mark
  )
}

format_integer <- function() {
  scales::label_comma(accuracy = 1)
}

format_rank <- function() {
  function(x) paste0("#", scales::label_number(accuracy = 1)(x))
}

format_year_range <- function(start_year, end_year = NULL) {
  if (is.null(end_year) || identical(start_year, end_year)) {
    return(as.character(start_year))
  }
  paste0(start_year, "-", end_year)
}

build_source_caption <- function(source, vintage) {
  parts <- compact_chr(c(
    if (is_nonempty_string(source)) paste0("Source: ", source),
    if (is_nonempty_string(vintage)) paste0("Vintage: ", vintage)
  ))
  paste(parts, collapse = " | ")
}

build_chart_notes <- function(source = NULL,
                              vintage = NULL,
                              side_note = NULL,
                              footer_note = NULL,
                              methodology_note = NULL,
                              prefix_note = NULL) {
  parts <- compact_chr(c(
    if (is_nonempty_string(source)) paste0("Source: ", source),
    if (is_nonempty_string(vintage)) paste0("Vintage: ", vintage),
    if (is_nonempty_string(prefix_note)) prefix_note,
    if (is_nonempty_string(side_note)) paste0("Note: ", side_note),
    if (is_nonempty_string(methodology_note)) paste0("Method: ", methodology_note),
    if (is_nonempty_string(footer_note)) footer_note
  ))

  paste(parts, collapse = " | ")
}

extract_chart_metadata <- function(data, field) {
  if (is.null(data) || !(field %in% names(data))) {
    return(NULL)
  }

  values <- unique(stats::na.omit(data[[field]]))
  if (length(values) == 0) {
    return(NULL)
  }

  as.character(values[[1]])
}

chart_default_config <- function(chart_type = NULL) {
  mode_defaults <- visual_mode_defaults("notebook")
  neutrals <- visual_neutral_palette()
  palettes <- visual_palette_defaults()

  base <- list(
    output_mode = mode_defaults$mode,
    export_format = "png",
    base_family = visual_font_family(),
    base_size = mode_defaults$base_size,
    subtitle_size = mode_defaults$subtitle_size,
    caption_size = mode_defaults$caption_size,
    background_fill = mode_defaults$background,
    legend_position = "right",
    grid = mode_defaults$grid,
    palette = palettes$sequential,
    binned_palette = palettes$binned,
    point_alpha = 0.78,
    line_alpha = 0.9,
    base_color = palettes$highlight$selection,
    highlight_color = palettes$highlight$selection,
    highlight_meaning = "selection",
    neutral_color = palettes$comparison$neutral,
    peer_palette = palettes$comparison$peers,
    series_palette = palettes$comparison$peers,
    missing_fill = neutrals$missing_fill,
    positive_fill = palettes$diverging$better,
    negative_fill = palettes$diverging$worse,
    diverging_low = palettes$diverging$worse,
    diverging_mid = palettes$diverging$midpoint,
    diverging_high = palettes$diverging$better,
    benchmark_color = palettes$comparison$benchmark,
    benchmark_linetype = benchmark_style_defaults()$linetype,
    benchmark_linewidth = benchmark_style_defaults()$linewidth,
    benchmark_alpha = benchmark_style_defaults()$alpha,
    benchmark_label_default = benchmark_style_defaults()$label,
    size_range = c(2, 10),
    label_size = mode_defaults$label_size,
    label_box = identical(mode_defaults$mode, "presentation"),
    label_max = NULL,
    title = NULL,
    subtitle = NULL,
    subtitle_wrap_width = 120,
    y_label = NULL,
    caption_side_note = NULL,
    caption_footer_note = NULL,
    caption_methodology_note = NULL,
    caption_wrap_width = 135,
    composition_preset = "none",
    plot_margin = ggplot2::margin(12, 16, 12, 12),
    map_extent = "data",
    show_us_outline = FALSE,
    show_state_outlines = FALSE,
    us_outline_color = "#8FA1B3",
    state_outline_color = "#C4CFD9",
    us_outline_linewidth = 0.45,
    state_outline_linewidth = 0.2
  )

  chart_specific <- switch(
    chart_type %||% "",
    scatter = list(
      trend_line_linetype = "22",
      trend_line_alpha = 0.7,
      trend_line_color = neutrals$text_muted,
      show_benchmark_labels = FALSE
    ),
    line = list(
      show_points = TRUE,
      show_benchmark_labels = FALSE
    ),
    bar = list(
      flip = TRUE,
      grid = "x",
      show_end_labels = TRUE
    ),
    boxplot = list(
      flip = TRUE,
      grid = "x",
      legend_position = "none",
      show_highlights = TRUE,
      show_highlight_labels = TRUE,
      show_jitter = FALSE,
      order_groups = "median_desc",
      box_width = 0.58,
      box_alpha = 0.78,
      point_alpha = 0.5,
      outlier_alpha = 0.45,
      outlier_size = 1.3,
      jitter_width = 0.12,
      subtitle_wrap_width = 105,
      caption_wrap_width = 125
    ),
    strength_strip = list(
      grid = "x",
      legend_position = "bottom",
      highlight_meaning = "strength"
    ),
    correlation_heatmap = list(
      tile_color = neutrals$background_white,
      grid = "none",
      label_box = FALSE,
      subtitle_wrap_width = 105,
      legend_position = "right",
      cell_label_size = 3
    ),
    heatmap_table = list(tile_color = neutrals$background_white, grid = "none"),
    bump_chart = list(
      grid = "both",
      legend_position = "none",
      show_points = TRUE,
      show_endpoint_labels = TRUE,
      label_mode = "highlight_or_all",
      label_all_max_n = 12,
      label_top_n = 8,
      label_max_chars = 34,
      label_include_value = FALSE,
      label_style = "number",
      label_accuracy = NULL,
      comparison_linewidth = 0.75,
      highlight_linewidth = 1.25,
      comparison_alpha = 0.42,
      peer_alpha = 0.6,
      point_size = 1.6,
      highlight_point_size = 2.1,
      right_margin_pt = 138,
      y_breaks = NULL,
      x_breaks = NULL,
      rank_band_n = NULL
    ),
    waterfall = list(
      grid = "y",
      legend_position = "bottom",
      label_box = FALSE,
      positive_fill = palettes$diverging$better,
      negative_fill = palettes$diverging$worse,
      subtitle_wrap_width = 110,
      caption_wrap_width = 125
    ),
    map = list(
      na_fill = neutrals$missing_fill,
      legend_position = "right",
      label_box = FALSE,
      grid = "none",
      subtitle_wrap_width = 95,
      map_extent = "contiguous_us",
      show_us_outline = TRUE,
      show_state_outlines = TRUE
    ),
    list()
  )

  utils::modifyList(base, chart_specific)
}

merge_chart_config <- function(defaults, config = NULL) {
  if (is.null(config)) {
    return(defaults)
  }
  utils::modifyList(defaults, config)
}

resolve_chart_config <- function(chart_type = NULL, config = NULL) {
  base <- merge_chart_config(chart_default_config(chart_type), config)
  mode_defaults <- visual_mode_defaults(base$output_mode %||% "notebook")

  base$base_size <- base$base_size %||% mode_defaults$base_size
  base$subtitle_size <- base$subtitle_size %||% mode_defaults$subtitle_size
  base$caption_size <- base$caption_size %||% mode_defaults$caption_size
  base$label_size <- base$label_size %||% mode_defaults$label_size
  base$background_fill <- base$background_fill %||% mode_defaults$background
  base$grid <- base$grid %||% mode_defaults$grid
  base$label_box <- base$label_box %||% identical(mode_defaults$mode, "presentation")

  if (is.null(base$highlight_color) || !nzchar(base$highlight_color)) {
    base$highlight_color <- resolve_highlight_color(base$highlight_meaning %||% "selection")
  }

  base
}

resolve_chart_theme <- function(config = list(), map = FALSE) {
  cfg <- resolve_chart_config(config = config)
  if (isTRUE(map)) {
    return(visual_map_theme(
      base_size = cfg$base_size,
      base_family = cfg$base_family,
      mode = cfg$output_mode,
      background = cfg$background_fill,
      legend_position = cfg$legend_position
    ))
  }

  visual_theme(
    base_size = cfg$base_size,
    base_family = cfg$base_family,
    mode = cfg$output_mode,
    background = cfg$background_fill,
    grid = cfg$grid,
    legend_position = cfg$legend_position
  )
}

apply_plot_labels <- function(plot,
                              data = NULL,
                              title = NULL,
                              subtitle = NULL,
                              x = NULL,
                              y = NULL,
                              caption = NULL,
                              side_note = NULL,
                              footer_note = NULL,
                              methodology_note = NULL) {
  wrap_text <- function(text, width = 120) {
    if (!is_nonempty_string(text) || is.null(width) || !is.finite(width) || width <= 0) {
      return(text)
    }
    paste(strwrap(text, width = width), collapse = "\n")
  }

  cfg <- if (!is.null(data) && !is.null(attr(data, "chart_config"))) {
    attr(data, "chart_config")
  } else {
    chart_default_config()
  }

  if (is.null(caption)) {
    caption <- build_chart_notes(
      source = extract_chart_metadata(data, "source"),
      vintage = extract_chart_metadata(data, "vintage"),
      side_note = side_note,
      footer_note = footer_note,
      methodology_note = methodology_note
    )
  }

  plot + ggplot2::labs(
    title = wrap_text(title, width = cfg$title_wrap_width %||% NULL),
    subtitle = wrap_text(subtitle, width = cfg$subtitle_wrap_width %||% 120),
    x = x,
    y = y,
    caption = if (is_nonempty_string(caption)) {
      wrap_text(caption, width = cfg$caption_wrap_width %||% 135)
    } else {
      NULL
    }
  )
}

render_placeholder_panel <- function(data,
                                     chart_type,
                                     title,
                                     subtitle = NULL,
                                     detail_lines = NULL,
                                     config = list()) {
  cfg <- resolve_chart_config(config = config)
  detail_lines <- detail_lines %||% c()
  lines <- c(
    paste("Chart type:", chart_type),
    paste("Rows:", nrow(data)),
    detail_lines
  )

  p <- ggplot2::ggplot(data.frame(x = 1, y = 1), ggplot2::aes(x = x, y = y)) +
    ggplot2::geom_label(
      label = paste(lines, collapse = "\n"),
      size = 4,
      label.size = 0.2,
      fill = visual_neutral_palette()$background_white,
      color = visual_neutral_palette()$text
    ) +
    ggplot2::xlim(0.5, 1.5) +
    ggplot2::ylim(0.5, 1.5)

  p <- apply_plot_labels(
    plot = p,
    title = title,
    subtitle = subtitle,
    data = data
  )

  p +
    visual_theme(
      base_size = cfg$base_size,
      base_family = cfg$base_family,
      mode = cfg$output_mode,
      background = cfg$background_fill,
      grid = "none"
    ) +
    ggplot2::theme(
      axis.text = ggplot2::element_blank(),
      axis.title = ggplot2::element_blank(),
      axis.ticks = ggplot2::element_blank(),
      panel.grid = ggplot2::element_blank()
    )
}

# Standard scatter styling defaults shared across chart implementations.
scatter_style_defaults <- local({
  cfg <- resolve_chart_config("scatter")
  list(
    point_alpha = cfg$point_alpha,
    palette = cfg$palette,
    base_color = cfg$base_color,
    highlight_color = cfg$highlight_color,
    trend_line_linetype = cfg$trend_line_linetype,
    trend_line_alpha = cfg$trend_line_alpha,
    trend_line_color = cfg$trend_line_color,
    benchmark_color = cfg$benchmark_color,
    benchmark_linetype = cfg$benchmark_linetype,
    size_range = cfg$size_range,
    size_breaks = c(1000, 10000, 100000, 1000000),
    label_size = cfg$label_size,
    label_outline_size = 0.18
  )
})
