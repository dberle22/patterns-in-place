#!/usr/bin/env Rscript

# This visual opens up the composite by plotting two of its most interpretable
# families directly: momentum and affordability strain. That makes it easier to
# see which markets are hot because prices are still running, because households
# are already stretched, or because both are happening at once.

source("publisher/content/housing/04_overheating/visuals/_shared_overheating_visuals.R")

script_path <- overheating_get_script_path("publisher/content/housing/04_overheating/visuals/cbsa_overheating_scatter.R")
ctx <- overheating_build_context(script_path)
output_path <- file.path(ctx$output_dir, "cbsa_overheating_scatter.png")

overheating_load_visual_library(ctx$foundations_dir, chart_types = c("scatter"))

con <- overheating_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

scatter_df <- overheating_run_sql_file(con, ctx$sql_dir, "cbsa_overheating_scatter.sql")
scatter_df <- prep_scatter(
  scatter_df,
  time_window = "2024_snapshot",
  require_single_geo_level = TRUE,
  drop_missing_xy = TRUE
)

scatter_df$group[is.na(scatter_df$group) | !nzchar(scatter_df$group)] <- "Unknown"
scatter_df$group <- factor(
  scatter_df$group,
  levels = c("Northeast", "Midwest", "South", "West", "Unknown")
)

if ("size_value" %in% names(scatter_df)) {
  finite_sizes <- scatter_df$size_value[is.finite(scatter_df$size_value)]
  if (length(finite_sizes) > 0) {
    scatter_df$size_value[!is.finite(scatter_df$size_value)] <- stats::median(finite_sizes, na.rm = TRUE)
  }
}

label_df <- scatter_df[scatter_df$label_flag %in% TRUE, , drop = FALSE]
median_x <- stats::median(scatter_df$x_value, na.rm = TRUE)
median_y <- stats::median(scatter_df$y_value, na.rm = TRUE)

caption_text <- build_chart_notes(
  source = "mart_housing.overheating_matrix",
  vintage = "2026-07-05",
  side_note = "Points are major CBSAs sized by 2024 population. Labels highlight the hottest composite markets plus a few of the calmest large-metro cases.",
  methodology_note = "Both axes are component scores scaled to 0-100. Dashed lines mark the median major-CBSA value on each dimension."
)

scatter_plot <- ggplot(
  scatter_df,
  aes(x = x_value, y = y_value, color = group, size = size_value)
) +
  geom_vline(
    xintercept = median_x,
    linetype = "dashed",
    linewidth = 0.45,
    color = visual_neutral_palette()$outline
  ) +
  geom_hline(
    yintercept = median_y,
    linetype = "dashed",
    linewidth = 0.45,
    color = visual_neutral_palette()$outline
  ) +
  geom_point(alpha = 0.78) +
  scale_color_brewer(palette = "Set2", na.translate = FALSE, name = NULL) +
  scale_size_continuous(
    range = c(2.2, 11),
    labels = scales::label_comma(),
    name = "2024 population"
  ) +
  scale_x_continuous(
    labels = scales::label_number(accuracy = 1),
    expand = expansion(mult = c(0.04, 0.1))
  ) +
  scale_y_continuous(
    labels = scales::label_number(accuracy = 1),
    expand = expansion(mult = c(0.05, 0.14))
  ) +
  labs(
    title = "Overheating is strongest where momentum and affordability strain overlap",
    subtitle = paste(
      "Major CBSAs, 2024 | The upper-right quadrant combines stronger recent momentum with stronger affordability strain",
      "| Markets closer to the lower-left look calmer on both dimensions"
    ),
    x = unique(scatter_df$x_label)[1],
    y = unique(scatter_df$y_label)[1],
    caption = caption_text
  ) +
  visual_theme(base_size = 12.5, mode = "presentation", legend_position = "bottom")

if (nrow(label_df) > 0) {
  if (requireNamespace("ggrepel", quietly = TRUE)) {
    scatter_plot <- scatter_plot +
      ggrepel::geom_label_repel(
        data = label_df,
        aes(label = geo_name),
        size = 3.1,
        label.size = 0.15,
        seed = 123,
        min.segment.length = 0,
        max.overlaps = Inf,
        show.legend = FALSE
      )
  } else {
    scatter_plot <- scatter_plot +
      geom_text(
        data = label_df,
        aes(label = geo_name),
        size = 3,
        hjust = -0.1,
        show.legend = FALSE
      )
  }
}

overheating_save_plot(
  scatter_plot,
  output_path = output_path,
  width = 10.8,
  height = 7.4
)

message(sprintf("Saved %s", output_path))
