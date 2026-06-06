acs_standardize_cols <- function(df) {
  df %>%
    dplyr::rename(
      geo_id   = dplyr::any_of("GEOID"),
      geo_name = dplyr::any_of("NAME")
    ) %>%
    dplyr::relocate(dplyr::any_of(c("geo_id","geo_name","year")))
}