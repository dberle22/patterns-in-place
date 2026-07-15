# Render the q011 Miami-vs-US renter-burden comparison through the existing R
# visual library so the Python benchmark candidate has a direct parity reference.

suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q011")
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
    question_id = "q011",
    time_window = "2023_snapshot",
    metric_id = "pct_rent_burden_30plus",
    sort_desc = TRUE,
    top_n = 1
  )
)

bar_plot <- render_bar(
  bar_df,
  config = list(
    output_mode = "presentation",
    title = "How does Miami's share of cost-burdened renters compare to the national average in 2023?",
    subtitle = "Miami-Fort Lauderdale-West Palm Beach, FL | 2023 snapshot | US benchmark shown for reference",
    y_label = "Share of renter households spending 30%+ of income on rent",
    label_style = "number",
    label_accuracy = 0.1,
    show_labels = TRUE,
    show_axis_labels = TRUE,
    show_benchmark = TRUE,
    benchmark_value = benchmark_value,
    benchmark_label = sprintf("US: %.1f%%", benchmark_value),
    caption_side_note = side_note,
    caption_methodology_note = "Metric from gold.housing_core_wide; geography labels from gold.dim_geo.",
    right_margin_pt = 88
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = bar_plot,
  width = 11,
  height = 6,
  dpi = 300,
  bg = "white"
)
