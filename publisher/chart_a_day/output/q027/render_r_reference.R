suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q027")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_bivariate_choropleth.R")
source("visual_library/shared/render/render_bivariate_choropleth.R")

result_df <- readr::read_csv(result_path, show_col_types = FALSE)

plot_df <- prep_bivariate_choropleth(
  result_df,
  config = list(
    question_id = "q027",
    time_window = "2023_snapshot",
    bin_method = "quantile",
    n_bins = 3,
    drop_missing_values = TRUE
  )
)

plot_obj <- render_bivariate_choropleth(
  plot_df,
  config = list(
    title = "Which states combine high rent burden with low vacancy?",
    subtitle = "Contiguous 48 states plus DC | 2023 snapshot | Quantile bins on rent burden and inverted vacancy",
    composition_preset = "national_compact",
    caption_side_note = "Higher values on the vertical bivariate axis indicate lower vacancy after sign inversion.",
    caption_methodology_note = "Both metrics are binned into 3 quantiles across states. The darkest high-high cells indicate the strongest combined housing stress."
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = plot_obj,
  width = 12,
  height = 7.5,
  dpi = 300,
  bg = "white"
)
