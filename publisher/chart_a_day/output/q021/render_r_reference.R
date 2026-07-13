suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q021")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_strength_strip.R")
source("visual_library/shared/render/render_strength_strip.R")

result_df <- as.data.frame(readr::read_csv(result_path, show_col_types = FALSE))
side_note <- unique(stats::na.omit(result_df$note))[[1]]

strip_df <- prep_strength_strip(
  result_df,
  config = list(
    normalize = FALSE,
    metric_order = c("rent_to_income", "vacancy_rate", "pop_growth_5yr", "cost_burden_share")
  )
)

strip_plot <- render_strength_strip(
  strip_df,
  config = list(
    title = "How does Austin rank across housing stress indicators in 2023?",
    subtitle = "Austin vs large-metro median benchmark | Rightward percentile means more housing stress or demand pressure",
    x_label = "Housing-stress percentile within large-metro universe",
    side_note = side_note
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = strip_plot,
  width = 12,
  height = 6.5,
  dpi = 300,
  bg = "white"
)
