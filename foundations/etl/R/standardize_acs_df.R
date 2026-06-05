standardize_acs_df <- function(df, geo_level, drop_e = FALSE) {
  df <- df %>%
    rename(
      geo_id   = any_of("GEOID"),
      geo_name = any_of("NAME")
    ) %>%
    mutate(geo_level = geo_level) %>%
    relocate(geo_level, geo_id, geo_name, year, .before = 1) %>%
    select(-ends_with("M"))
  
  if (isTRUE(drop_e)) {
    df <- df %>%
      rename_with(
        ~ sub("E$", "", .x),
        ends_with("E")
      )
  }
  
  df
}