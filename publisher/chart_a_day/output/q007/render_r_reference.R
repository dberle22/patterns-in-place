# Render the q007 selected-metro rent comparison through the existing R visual
# library so the Python bar-chart candidate has a direct parity reference.

suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q007")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_bar.R")
source("visual_library/shared/render/render_bar.R")

result_df <- readr::read_csv(result_path, show_col_types = FALSE)
benchmark_value <- unique(stats::na.omit(result_df$benchmark_value))[[1]]
side_note <- unique(stats::na.omit(result_df$note))[[1]]

bar_df <- prep_bar(
  result_df,
  config = list(
    question_id = "q007",
    time_window = "2023_snapshot",
    metric_id = "median_gross_rent",
    sort_desc = TRUE,
    top_n = 4
  )
)

bar_plot <- render_bar(
  bar_df,
  config = list(
    output_mode = "presentation",
    title = "Compare median gross rent in Austin, Nashville, Denver, and Charlotte in 2023.",
    subtitle = "Selected high-migration CBSAs | 2023 snapshot | US major-metro benchmark shown for reference",
    y_label = "Median gross rent",
    label_style = "dollar",
    label_accuracy = 1,
    show_labels = TRUE,
    show_axis_labels = TRUE,
    show_benchmark = TRUE,
    benchmark_value = benchmark_value,
    benchmark_label = sprintf("US major-metro avg: $%s", format(round(benchmark_value), big.mark = ",")),
    caption_side_note = side_note,
    caption_methodology_note = "Metric from gold.housing_core_wide; geography labels from gold.dim_geo.",
    right_margin_pt = 92
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = bar_plot,
  width = 12,
  height = 8,
  dpi = 300,
  bg = "white"
)
