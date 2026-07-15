suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q026")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_proportional_symbol_map.R")
source("visual_library/shared/render/render_proportional_symbol_map.R")

result_df <- readr::read_csv(result_path, show_col_types = FALSE)

plot_df <- prep_proportional_symbol_map(
  result_df,
  config = list(
    question_id = "q026",
    time_window = "2018_2023_growth",
    require_single_time_window = TRUE,
    label_strategy = "provided_or_top_n"
  )
)

plot_obj <- render_proportional_symbol_map(
  plot_df,
  config = list(
    title = "Where is population growth concentrated across US metros?",
    subtitle = "CBSAs with population above 100k | Bubble size = 2018-2023 growth rate | Color = Census region",
    color_mode = "color_group",
    label_include_value = FALSE,
    value_style = "percent",
    value_accuracy = 0.1,
    composition_preset = "national_compact",
    caption_side_note = "Bubble size reflects 2018-2023 population growth for CBSAs above 100k population.",
    caption_methodology_note = "Point locations come from CBSA polygon point-on-surface coordinates; colors show Census region."
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = plot_obj,
  width = 11,
  height = 7.8,
  dpi = 300,
  bg = "white"
)
