suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q002")
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
side_note <- unique(stats::na.omit(result_df$note))[[1]]

bar_df <- prep_bar(
  result_df,
  config = list(
    question_id = "q002",
    time_window = "2023_snapshot",
    metric_id = "median_hh_income",
    sort_desc = TRUE,
    top_n = 10
  )
)

bar_plot <- render_bar(
  bar_df,
  config = list(
    output_mode = "presentation",
    title = "Which states have the highest median household income in 2023?",
    subtitle = "Top 10 states by median household income | District of Columbia included",
    y_label = "Median household income ($)",
    label_style = "dollar",
    label_accuracy = 1,
    show_labels = TRUE,
    show_axis_labels = TRUE,
    caption_side_note = side_note,
    caption_methodology_note = "Metric from gold.economics_income_wide; region labels from gold.dim_geo.",
    right_margin_pt = 72
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
