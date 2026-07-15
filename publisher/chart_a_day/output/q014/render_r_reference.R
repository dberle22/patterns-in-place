suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q014")
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
    question_id = "q014",
    time_window = "2018_2023_growth",
    metric_id = "per_capita_income_growth_5yr",
    sort_desc = TRUE,
    top_n = 15
  )
)

bar_plot <- render_bar(
  bar_df,
  config = list(
    output_mode = "presentation",
    title = "Which metros have seen the fastest per capita income growth over the last 5 years?",
    subtitle = "Top 15 CBSAs by 2018-2023 per capita income growth | Population filter: 250k+",
    y_label = "Five-year per capita income growth (%)",
    label_style = "number",
    label_accuracy = 0.1,
    show_labels = TRUE,
    show_axis_labels = TRUE,
    caption_side_note = side_note,
    caption_methodology_note = "Growth compares 2018 vs 2023 per capita income from gold.housing_core_wide."
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
