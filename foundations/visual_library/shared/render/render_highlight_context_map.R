# Render highlight-context map or fallback panel.

source("visual_library/shared/chart_utils.R")

render_highlight_context_map <- function(data, config = list(), theme = NULL) {
  cfg <- merge_chart_config(
    chart_default_config("map"),
    merge_chart_config(
      list(
        variant = c("focus_only", "continuous", "binned", "diverging"),
        fill_field = NULL,
        fill_label = NULL,
        legend_title = NULL,
        context_layers = NULL,
        context_data = NULL,
        context_fill = "#EEF2F6",
        context_color = "#C6D1DB",
        context_linewidth = 0.22,
        border_color = "white",
        border_linewidth = 0.12,
        highlight_fill = NULL,
        highlight_outline_color = NULL,
        highlight_outline_linewidth = 0.8,
        neighbor_fill = "#D9E1E8",
        neighbor_outline_color = "#6B7C8F",
        neighbor_outline_linewidth = 0.45,
        show_outline_halo = TRUE,
        outline_halo_color = "white",
        outline_halo_linewidth_add = 0.45,
        highlight_halo_linewidth = NULL,
        neighbor_halo_linewidth = NULL,
        focus_legend_title = "Map role",
        label_field = "geo_name",
        trim_quantiles = NULL,
        midpoint = 0,
        facet_by = NULL,
        facet_ncol = NULL,
        xlim = NULL,
        ylim = NULL
      ),
      config
    )
  )
  cfg$variant <- match.arg(cfg$variant, c("focus_only", "continuous", "binned", "diverging"))
  cfg <- merge_chart_config(
    cfg,
    resolve_map_composition_preset(
      preset = cfg$composition_preset %||% "none",
      data = data,
      config = cfg
    )
  )

  if (is.null(cfg$xlim) && is.null(cfg$ylim)) {
    extent_limits <- map_extent_limits(cfg$map_extent %||% "data")
    cfg$xlim <- extent_limits$xlim
    cfg$ylim <- extent_limits$ylim
  }

  if (!("geometry" %in% names(data)) || !inherits(data, "sf") || !requireNamespace("sf", quietly = TRUE)) {
    return(
      render_placeholder_panel(
        data = data,
        chart_type = "highlight_context_map",
        title = cfg$title %||% "Highlight + Context Map Scaffold",
        subtitle = cfg$subtitle,
        detail_lines = c("Geometry-backed rendering requires an sf object in the geometry column.")
      )
    )
  }

  plot_data <- data
  fill_field <- cfg$fill_field %||% if (identical(cfg$variant, "binned")) "bin" else "fill_value"

  if (!identical(cfg$variant, "focus_only")) {
    if (!(fill_field %in% names(plot_data))) {
      stop(sprintf("Highlight + context fill field '%s' not found.", fill_field))
    }
    if (!is.null(cfg$trim_quantiles) && is.numeric(plot_data[[fill_field]])) {
      bounds <- stats::quantile(
        plot_data[[fill_field]],
        probs = cfg$trim_quantiles,
        na.rm = TRUE,
        names = FALSE,
        type = 7
      )
      plot_data[[fill_field]] <- pmin(pmax(plot_data[[fill_field]], bounds[[1]]), bounds[[2]])
    }
  }

  attr(plot_data, "chart_config") <- resolve_chart_config(config = cfg)

  p <- ggplot2::ggplot(plot_data)

  if (!is.null(cfg$context_layers) && length(cfg$context_layers) > 0) {
    for (layer_cfg in cfg$context_layers) {
      if (is.null(layer_cfg$data) || !inherits(layer_cfg$data, "sf")) {
        next
      }
      p <- p + ggplot2::geom_sf(
        data = layer_cfg$data,
        inherit.aes = FALSE,
        fill = layer_cfg$fill %||% NA,
        color = layer_cfg$color %||% cfg$context_color,
        linewidth = layer_cfg$linewidth %||% cfg$context_linewidth
      )
    }
  }

  if (!is.null(cfg$context_data) && inherits(cfg$context_data, "sf")) {
    p <- p + ggplot2::geom_sf(
      data = cfg$context_data,
      inherit.aes = FALSE,
      fill = cfg$context_fill,
      color = cfg$context_color,
      linewidth = cfg$context_linewidth
    )
  }

  if (identical(cfg$variant, "focus_only")) {
    focus_levels <- c("Background context", "Neighbor context", "Highlighted geography")
    focus_palette <- c(
      "Background context" = cfg$context_fill,
      "Neighbor context" = cfg$neighbor_fill,
      "Highlighted geography" = cfg$highlight_fill %||% cfg$highlight_color
    )

    plot_data$focus_role <- factor(plot_data$focus_role, levels = focus_levels)
    p <- p + ggplot2::geom_sf(
      ggplot2::aes(fill = .data$focus_role),
      color = cfg$border_color,
      linewidth = cfg$border_linewidth
    ) +
      ggplot2::scale_fill_manual(
        values = focus_palette,
        drop = TRUE,
        na.value = cfg$na_fill,
        name = cfg$focus_legend_title
      )
  } else {
    p <- p + ggplot2::geom_sf(
      ggplot2::aes(fill = .data[[fill_field]]),
      color = cfg$border_color,
      linewidth = cfg$border_linewidth
    )

    if (identical(cfg$variant, "binned")) {
      fill_levels <- sort(unique(stats::na.omit(as.character(plot_data[[fill_field]]))))
      palette_values <- if (identical(cfg$binned_palette, "viridis")) {
        viridisLite::viridis(max(length(fill_levels), 3))
      } else {
        grDevices::hcl.colors(max(length(fill_levels), 3), palette = cfg$binned_palette)
      }
      p <- p + ggplot2::scale_fill_manual(
        values = stats::setNames(palette_values[seq_along(fill_levels)], fill_levels),
        na.value = cfg$na_fill,
        drop = FALSE,
        name = cfg$legend_title %||% cfg$fill_label %||% NULL
      )
    } else if (identical(cfg$variant, "diverging")) {
      p <- p + ggplot2::scale_fill_gradient2(
        low = cfg$diverging_low,
        mid = cfg$diverging_mid,
        high = cfg$diverging_high,
        midpoint = cfg$midpoint,
        na.value = cfg$na_fill,
        name = cfg$legend_title %||% cfg$fill_label %||% NULL
      )
    } else {
      p <- p + ggplot2::scale_fill_viridis_c(
        option = "viridis",
        na.value = cfg$na_fill,
        name = cfg$legend_title %||% cfg$fill_label %||% NULL
      )
    }

    overlay_levels <- c("Neighbor context", "Highlighted geography")
    overlay_data <- plot_data[!is.na(plot_data$outline_role), , drop = FALSE]
    if (nrow(overlay_data) > 0) {
      overlay_data$outline_role <- factor(overlay_data$outline_role, levels = overlay_levels)
      neighbor_data <- overlay_data[overlay_data$outline_role == "Neighbor context", , drop = FALSE]
      highlight_data <- overlay_data[overlay_data$outline_role == "Highlighted geography", , drop = FALSE]
      neighbor_halo_linewidth <- cfg$neighbor_halo_linewidth %||%
        (cfg$neighbor_outline_linewidth + cfg$outline_halo_linewidth_add)
      highlight_halo_linewidth <- cfg$highlight_halo_linewidth %||%
        (cfg$highlight_outline_linewidth + cfg$outline_halo_linewidth_add)

      if (nrow(neighbor_data) > 0) {
        if (isTRUE(cfg$show_outline_halo)) {
          p <- p + ggplot2::geom_sf(
            data = neighbor_data,
            inherit.aes = FALSE,
            fill = NA,
            color = cfg$outline_halo_color,
            linewidth = neighbor_halo_linewidth,
            show.legend = FALSE
          )
        }
        p <- p + ggplot2::geom_sf(
          data = neighbor_data,
          ggplot2::aes(color = .data$outline_role),
          fill = NA,
          linewidth = cfg$neighbor_outline_linewidth,
          show.legend = TRUE
        )
      }
      if (nrow(highlight_data) > 0) {
        if (isTRUE(cfg$show_outline_halo)) {
          p <- p + ggplot2::geom_sf(
            data = highlight_data,
            inherit.aes = FALSE,
            fill = NA,
            color = cfg$outline_halo_color,
            linewidth = highlight_halo_linewidth,
            show.legend = FALSE
          )
        }
        p <- p + ggplot2::geom_sf(
          data = highlight_data,
          ggplot2::aes(color = .data$outline_role),
          fill = NA,
          linewidth = cfg$highlight_outline_linewidth,
          show.legend = TRUE
        )
      }

      p <- p +
        ggplot2::scale_color_manual(
          values = c(
            "Neighbor context" = cfg$neighbor_outline_color,
            "Highlighted geography" = cfg$highlight_outline_color %||% cfg$highlight_color
          ),
          drop = TRUE,
          name = cfg$focus_legend_title,
          na.translate = FALSE
        )
    }
  }

  if ("label_flag" %in% names(plot_data) &&
      any(plot_data$label_flag %in% TRUE, na.rm = TRUE)) {
    label_data <- plot_data[plot_data$label_flag %in% TRUE, , drop = FALSE]
    label_points <- if (isTRUE(sf::st_is_longlat(label_data))) {
      suppressWarnings(
        sf::st_transform(
          sf::st_point_on_surface(sf::st_transform(label_data, 5070)),
          sf::st_crs(label_data)
        )
      )
    } else {
      suppressWarnings(sf::st_point_on_surface(label_data))
    }
    label_coords <- sf::st_coordinates(label_points)
    label_frame <- cbind(
      sf::st_drop_geometry(label_points),
      x = label_coords[, "X"],
      y = label_coords[, "Y"]
    )
    label_col <- if (cfg$label_field %in% names(label_frame)) cfg$label_field else "geo_name"
    p <- p + ggplot2::geom_text(
      data = label_frame,
      ggplot2::aes(x = .data$x, y = .data$y, label = .data[[label_col]]),
      inherit.aes = FALSE,
      size = cfg$label_size %||% 3.5,
      color = "#243746",
      family = cfg$base_family,
      check_overlap = TRUE
    )
  }

  if (!is.null(cfg$facet_by) && cfg$facet_by %in% names(plot_data)) {
    p <- p + ggplot2::facet_wrap(stats::as.formula(paste("~", cfg$facet_by)), ncol = cfg$facet_ncol)
  }

  p <- apply_plot_labels(
    p,
    data = plot_data,
    title = cfg$title %||% "Highlight + Context Map",
    subtitle = cfg$subtitle,
    caption = chart_caption_from_config(plot_data, cfg)
  )

  final_theme <- theme %||% resolve_chart_theme(cfg, map = TRUE)
  if (!is.null(cfg$plot_margin)) {
    final_theme <- final_theme + ggplot2::theme(plot.margin = cfg$plot_margin)
  }

  p + ggplot2::coord_sf(datum = NA, xlim = cfg$xlim, ylim = cfg$ylim) + final_theme
}
