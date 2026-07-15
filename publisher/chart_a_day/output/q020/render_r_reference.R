suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q020")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_waterfall.R")
source("visual_library/shared/render/render_waterfall.R")

result_df <- as.data.frame(readr::read_csv(result_path, show_col_types = FALSE))
side_note <- unique(stats::na.omit(result_df$note))[[1]]

waterfall_df <- prep_waterfall(
  result_df,
  config = list(
    value_mode = "level",
    include_total = TRUE
  )
)

waterfall_plot <- render_waterfall(
  waterfall_df,
  config = list(
    title = "What share of US metros fall into each vacancy rate tier in 2023?",
    subtitle = "CBSAs with population 250k+ | Tier shares sum to 100% of the 196-metro universe",
    label_style = "percent",
    label_accuracy = 0.1,
    show_value_labels = TRUE,
    side_note = side_note
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = waterfall_plot,
  width = 12,
  height = 7,
  dpi = 300,
  bg = "white"
)
