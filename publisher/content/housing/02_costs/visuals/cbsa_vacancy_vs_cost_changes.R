#!/usr/bin/env Rscript

# This visual tests a central Costs-section question:
# where did vacancy ease or tighten while rents and home values were still
# moving up? The chart uses one panel for rent growth and one for home-value
# growth so we can avoid inventing a composite cost-change metric too early.

source("publisher/content/housing/02_costs/visuals/_shared_costs_visuals.R")

script_path <- costs_get_script_path("publisher/content/housing/02_costs/visuals/cbsa_vacancy_vs_cost_changes.R")
ctx <- costs_build_context(script_path)
output_path <- file.path(ctx$output_dir, "cbsa_vacancy_vs_cost_changes.png")

costs_load_visual_library(ctx$foundations_dir, chart_types = c("scatter"))

con <- costs_connect_duckdb(ctx$db_path)
on.exit(dbDisconnect(con, shutdown = TRUE), add = TRUE)

scatter_df <- costs_run_sql_file(con, ctx$sql_dir, "cbsa_vacancy_vs_cost_changes.sql")
scatter_df <- prep_scatter(
  scatter_df,
  time_window = "2019_to_2024_change",
  require_single_geo_level = TRUE,
  drop_missing_xy = TRUE
)

if ("size_value" %in% names(scatter_df)) {
  finite_sizes <- scatter_df$size_value[is.finite(scatter_df$size_value)]
  if (length(finite_sizes) > 0) {
    scatter_df$size_value[!is.finite(scatter_df$size_value)] <- stats::median(finite_sizes, na.rm = TRUE)
  }
}

region_levels <- c("Northeast", "Midwest", "South", "West")
if ("region_name" %in% names(scatter_df)) {
  scatter_df$region_name[is.na(scatter_df$region_name) | !nzchar(scatter_df$region_name)] <- "Unknown"
  region_levels <- c(region_levels, "Unknown")
  scatter_df$region_name <- factor(scatter_df$region_name, levels = region_levels)
}

label_df <- scatter_df[scatter_df$label_flag %in% TRUE, , drop = FALSE]
quad_df <- unique(data.frame(group = scatter_df$group, stringsAsFactors = FALSE))
quad_df$x_intercept <- 0
quad_df$y_intercept <- 0

caption_text <- build_chart_notes(
  source = "mart_housing.core_metrics",
  vintage = "2026-07-05",
  side_note = "Points are major CBSAs sized by 2024 population. Labels highlight the strongest falling-vacancy/rising-cost markets plus a few rising-vacancy/rising-cost contradictions.",
  methodology_note = "Change window is 2019 to 2024. The vertical zero line marks no vacancy-rate change; the horizontal zero line marks no cost growth."
)

scatter_plot <- ggplot(
  scatter_df,
  aes(x = x_value, y = y_value, color = region_name, size = size_value)
) +
  geom_vline(
    data = quad_df,
    aes(xintercept = x_intercept),
    linetype = "dashed",
    linewidth = 0.45,
    color = visual_neutral_palette()$outline
  ) +
  geom_hline(
    data = quad_df,
    aes(yintercept = y_intercept),
    linetype = "dashed",
    linewidth = 0.45,
    color = visual_neutral_palette()$outline
  ) +
  geom_point(alpha = 0.78) +
  facet_wrap(~group, scales = "free_y") +
  scale_color_brewer(palette = "Set2", na.translate = FALSE, name = NULL) +
  scale_size_continuous(
    range = c(2.2, 11),
    labels = scales::label_comma(),
    name = "2024 population"
  ) +
  scale_x_continuous(
    labels = scales::label_number(accuracy = 0.1),
    expand = expansion(mult = c(0.04, 0.08))
  ) +
  scale_y_continuous(
    labels = scales::label_number(accuracy = 1, suffix = "%"),
    expand = expansion(mult = c(0.05, 0.12))
  ) +
  labs(
    title = "Falling vacancy usually still came with rising housing costs",
    subtitle = paste(
      "Major CBSAs, 2019 to 2024 | Left-of-zero metros tightened, while right-of-zero metros added vacancy",
      "| The upper-right quadrant is the clearest contradiction to a simple supply-relief story"
    ),
    x = unique(scatter_df$x_label)[1],
    y = NULL,
    caption = caption_text
  ) +
  visual_theme(base_size = 12.5, mode = "presentation", legend_position = "bottom") +
  theme(
    strip.text = element_text(face = "bold"),
    legend.box = "vertical"
  )

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

costs_save_plot(
  scatter_plot,
  output_path = output_path,
  width = 11.2,
  height = 7.8
)

message(sprintf("Saved %s", output_path))
