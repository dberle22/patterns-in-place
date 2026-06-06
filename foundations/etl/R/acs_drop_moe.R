acs_drop_moe <- function(df) {
  if ("moe" %in% names(df)) {
    # tidy output
    df %>% dplyr::select(-moe)
  } else {
    # wide output: remove *_M columns, keep everything else
    df %>% dplyr::select(-tidyselect::ends_with("_M"))
  }
}