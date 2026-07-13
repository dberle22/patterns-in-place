suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q016")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_scatter.R")
source("visual_library/shared/render/render_scatter.R")

result_df <- readr::read_csv(result_path, show_col_types = FALSE)
side_note <- unique(stats::na.omit(result_df$note))[[1]]

scatter_df <- prep_scatter(result_df, time_window = "2018_2023_growth_vs_2023_affordability")

scatter_plot <- render_scatter(
  scatter_df,
  title = "How does rent-to-income ratio correlate with 5-year population growth across major metros?",
  subtitle = "Major CBSAs with population 500k+ | X = 2018-2023 population growth | Y = 2023 rent-to-income ratio",
  highlight_mode = "labels",
  add_trend_line = TRUE,
  add_reference_line = FALSE,
  add_quadrants = TRUE,
  side_note = side_note,
  footer_note = NULL
)

ggplot2::ggsave(
  filename = chart_path,
  plot = scatter_plot,
  width = 12,
  height = 8,
  dpi = 300,
  bg = "white"
)
