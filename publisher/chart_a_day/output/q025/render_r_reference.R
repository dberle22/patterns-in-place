suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q025")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_highlight_context_map.R")
source("visual_library/shared/render/render_highlight_context_map.R")

result_df <- readr::read_csv(result_path, show_col_types = FALSE)
side_note <- unique(stats::na.omit(result_df$note))[[1]]

map_df <- prep_highlight_context_map(
  result_df,
  config = list(
    question_id = "q025",
    time_window = "2024_snapshot",
    variant = "binned",
    require_single_time_window = TRUE
  )
)

map_plot <- render_highlight_context_map(
  map_df,
  config = list(
    title = "Where is Phoenix in the national vacancy landscape?",
    subtitle = "CBSAs with population >= 250k | 2024 snapshot | Context colored by vacancy-rate tier",
    variant = "binned",
    fill_field = "bin",
    legend_title = "Vacancy rate tier",
    composition_preset = "national_compact",
    caption_side_note = side_note,
    caption_methodology_note = "Metric from gold.housing_core_wide; geography labels from gold.dim_geo; geometry from geo.cbsas."
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = map_plot,
  width = 12,
  height = 8,
  dpi = 300,
  bg = "white"
)
