suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q009")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_boxplot.R")
source("visual_library/shared/render/render_boxplot.R")

result_df <- readr::read_csv(result_path, show_col_types = FALSE)
side_note <- unique(stats::na.omit(result_df$note))[[1]]

box_df <- prep_boxplot(
  result_df,
  config = list(
    question_id = "q009",
    time_window = "2023_snapshot",
    metric_id = "rent_to_income",
    require_single_time_window = TRUE
  )
)

box_plot <- render_boxplot(
  box_df,
  config = list(
    output_mode = "presentation",
    title = "How is rent-to-income distributed across US metros in 2023?",
    subtitle = "CBSAs with population >= 250k | 2023 snapshot",
    group_label = NULL,
    value_label = "Rent-to-income (%)",
    label_style = "number",
    label_accuracy = 0.1,
    caption_side_note = side_note,
    caption_methodology_note = "Metric from gold.housing_core_wide; geography labels from gold.dim_geo."
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = box_plot,
  width = 11,
  height = 8,
  dpi = 300,
  bg = "white"
)
