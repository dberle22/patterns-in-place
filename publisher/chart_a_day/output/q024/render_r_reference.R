# Render the q024 state cost-burden choropleth through the R visual library so
# the manual run compares the Python geo path to the current reference path.

suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q024")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_choropleth.R")
source("visual_library/shared/render/render_choropleth.R")

result_df <- readr::read_csv(result_path, show_col_types = FALSE)

map_df <- prep_choropleth(
  result_df,
  config = list(
    question_id = "q024",
    time_window = "2023_snapshot",
    metric_id = "pct_rent_burden_30plus",
    variant = "continuous",
    require_single_time_window = TRUE
  )
)

map_plot <- render_choropleth(
  map_df,
  config = list(
    output_mode = "presentation",
    title = "Which states have the highest share of cost-burdened renters in 2023?",
    subtitle = "Contiguous 48 states plus DC | 2023 snapshot | Darker states = higher renter cost burden",
    variant = "continuous",
    composition_preset = "national_compact",
    fill_label = "Renter cost-burden share (%)",
    legend_title = "2023 renter cost-burden share",
    show_us_outline = FALSE,
    show_state_outlines = FALSE,
    border_color = "white",
    border_linewidth = 0.2,
    caption_side_note = "Contiguous 48 states plus DC only. Darker states indicate higher renter cost burden.",
    caption_methodology_note = "Metric from gold.housing_core_wide, joined to geo.states for state geometry."
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = map_plot,
  width = 11,
  height = 7,
  dpi = 300,
  bg = "white"
)
