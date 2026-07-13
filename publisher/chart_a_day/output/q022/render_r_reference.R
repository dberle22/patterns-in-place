suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q022")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_correlation_heatmap.R")
source("visual_library/shared/render/render_correlation_heatmap.R")

result_df <- readr::read_csv(result_path, show_col_types = FALSE)

plot_df <- prep_correlation_heatmap(
  result_df,
  config = list(
    question_id = "q022",
    method = "spearman",
    order_method = "clustered",
    weak_threshold = NULL
  )
)

plot_obj <- render_correlation_heatmap(
  plot_df,
  config = list(
    title = "How correlated are rent burden, vacancy rate, income growth, and population growth across US metros?",
    subtitle = "CBSAs with population above 250k | Spearman correlation | 2023 cross-section with 5-year growth metrics",
    legend_title = "Correlation",
    caption_side_note = "All CBSAs with population above 250k and non-missing values for the four selected metrics.",
    caption_methodology_note = "Spearman correlation on rent-to-income ratio, vacancy rate, per capita income growth (5y), and population growth (5y)."
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = plot_obj,
  width = 9.5,
  height = 8.5,
  dpi = 300,
  bg = "white"
)
