suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q005")
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
    question_id = "q005",
    time_window = "2015_2023_level",
    metric_id = "median_hh_income",
    period_min = 2015,
    period_max = 2023
  )
)

line_plot <- render_line(
  line_df,
  config = list(
    output_mode = "presentation",
    title = "How has median household income trended in Sun Belt metros since 2015?",
    subtitle = "Austin, Dallas, Houston, Phoenix, Atlanta, Tampa, Orlando, and Nashville | 2015-2023 annual series",
    y_label = "Median household income ($)",
    label_style = "dollar",
    label_accuracy = 1,
    show_points = TRUE,
    legend_position = "bottom",
    caption_side_note = side_note,
    caption_methodology_note = "Median household income from gold.housing_core_wide for the selected Sun Belt metro set."
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
