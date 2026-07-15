suppressPackageStartupMessages({
  library(ggplot2)
  library(readr)
})

repo_root <- normalizePath(".")
foundations_dir <- file.path(repo_root, "foundations")
output_dir <- file.path(repo_root, "publisher", "chart_a_day", "output", "q028")
result_path <- file.path(output_dir, "result.csv")
chart_path <- file.path(output_dir, "chart_r.png")

old_wd <- getwd()
on.exit(setwd(old_wd), add = TRUE)
setwd(foundations_dir)

source("visual_library/shared/standards.R")
source("visual_library/shared/chart_utils.R")
source("visual_library/shared/data_contracts.R")
source("visual_library/shared/prep/prep_hexbin.R")
source("visual_library/shared/render/render_hexbin.R")

result_df <- readr::read_csv(result_path, show_col_types = FALSE)

plot_df <- prep_hexbin(
  result_df,
  config = list(
    question_id = "q028",
    time_window = "2023_cross_section"
  )
)

plot_obj <- render_hexbin(
  plot_df,
  config = list(
    title = "How does median age cluster against rent burden across all US metros?",
    subtitle = "All CBSAs | 2023 cross-section | Hexbin density view of aging and affordability pressure",
    method = "hex",
    bins = 30,
    label_style_x = "number",
    label_accuracy_x = 1,
    label_style_y = "percent",
    label_accuracy_y = 0.1,
    caption_side_note = "All CBSAs with non-missing 2023 median age and rent-to-income ratio.",
    caption_methodology_note = "Hexbin density summarizes the metro distribution without overplotting individual points."
  )
)

ggplot2::ggsave(
  filename = chart_path,
  plot = plot_obj,
  width = 10.5,
  height = 7.5,
  dpi = 300,
  bg = "white"
)
