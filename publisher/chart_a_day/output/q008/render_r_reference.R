suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q008")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_line.R")
source("visual_library/shared/render/render_line.R")

result_df <- readr::read_csv(result_path, show_col_types = FALSE)
side_note <- unique(stats::na.omit(result_df$note))[[1]]

line_df <- prep_line(
  result_df,
  config = list(
    question_id = "q008",
    time_window = "2018_2023_indexed",
    metric_id = "pop_total_index_2018eq100"
  )
)

line_plot <- render_line(
  line_df,
  config = list(
    output_mode = "presentation",
    title = "Compare population growth over the last 5 years in the 5 fastest-growing metros.",
    subtitle = "Top 5 CBSAs by 2023 five-year population growth | Indexed to 2018 = 100",
    y_label = "Population index (2018 = 100)",
    label_style = "number",
    label_accuracy = 0.1,
    show_points = TRUE,
    start_at_zero = FALSE,
    caption_side_note = side_note,
    caption_methodology_note = "Metric from gold.population_demographics; geography labels from gold.dim_geo."
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = line_plot,
  width = 12,
  height = 8,
  dpi = 300,
  bg = "white"
)
