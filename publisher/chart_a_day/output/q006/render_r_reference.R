# Render the q006 national vacancy trend through the R visual library so the
# manual run compares the Python line chart to the current reference path.

suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q006")
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

line_df <- prep_line(
  result_df,
  config = list(
    question_id = "q006",
    time_window = "2015_2024_level",
    metric_id = "vacancy_rate",
    period_min = 2015,
    period_max = 2024
  )
)

line_plot <- render_line(
  line_df,
  config = list(
    output_mode = "presentation",
    title = "How has the vacancy rate trended nationally since 2015?",
    subtitle = "United States | 2015-2024 annual series",
    y_label = "Vacancy rate (%)",
    label_style = "number",
    label_accuracy = 0.1,
    start_at_zero = TRUE,
    y_limits = c(0, 20),
    show_points = TRUE,
    legend_position = "none",
    caption_side_note = "This uses the true national row in gold.housing_core_wide rather than a rolled-up metro average.",
    caption_methodology_note = "Annual vacancy rate from gold.housing_core_wide, filtered to the United States row."
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = line_plot,
  width = 11,
  height = 7,
  dpi = 300,
  bg = "white"
)
