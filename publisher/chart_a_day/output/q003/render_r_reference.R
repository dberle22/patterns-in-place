# Render the q003 cost-burden ranking through the existing R visual library so
# CE-2 has a true reference artifact to compare against the Python candidate.

suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

`%||%` <- function(x, y) {
  if (is.null(x)) y else x
}

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q003")
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
if (!"source" %in% names(result_df)) {
  result_df$source <- "gold.housing_core_wide; gold.population_demographics"
}
if (!"vintage" %in% names(result_df)) {
  result_df$vintage <- "2026-07-11"
}
benchmark_value <- unique(stats::na.omit(result_df$benchmark_value))[[1]]
side_note <- unique(stats::na.omit(result_df$note))[[1]]

bar_df <- prep_bar(
  result_df,
  config = list(
    question_id = "q003",
    time_window = "2023 level",
    metric_id = "pct_rent_burden_30plus",
    sort_desc = TRUE,
    top_n = 20
  )
)

bar_plot <- render_bar(
  bar_df,
  config = list(
    output_mode = "presentation",
    title = "Which metros have the highest share of cost-burdened renters in 2023?",
    subtitle = "Top 20 CBSAs by renter burden | Population filter: 250k+ | US benchmark shown for reference",
    y_label = "Share of renter households spending 30%+ of income on rent",
    label_style = "number",
    label_accuracy = 0.1,
    show_labels = TRUE,
    show_axis_labels = TRUE,
    show_benchmark = TRUE,
    benchmark_value = benchmark_value,
    benchmark_label = sprintf("US benchmark: %.1f", benchmark_value),
    caption_side_note = side_note,
    caption_methodology_note = "Metric from gold.housing_core_wide; population filter from gold.population_demographics.",
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
