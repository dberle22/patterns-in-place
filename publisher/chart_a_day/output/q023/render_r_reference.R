suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q023")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_age_pyramid.R")
source("visual_library/shared/render/render_age_pyramid.R")

result_df <- readr::read_csv(result_path, show_col_types = FALSE)

plot_df <- prep_age_pyramid(
  result_df,
  config = list(
    question_id = "q023",
    period = 2023,
    measure = "share",
    require_single_period = TRUE
  )
)

plot_obj <- render_age_pyramid(
  plot_df,
  config = list(
    title = "How does the age distribution in Miami compare to the US overall in 2023?",
    subtitle = "Miami-Fort Lauderdale-West Palm Beach, FL vs United States | Percent of total population | Male left, female right",
    caption_side_note = "Gray benchmark outlines show the United States using the same 2023 age-sex bins.",
    caption_methodology_note = "Population shares are computed within each geography across both sexes and all displayed age bins."
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = plot_obj,
  width = 10.5,
  height = 8.0,
  dpi = 300,
  bg = "white"
)
