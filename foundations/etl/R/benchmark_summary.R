# Create our benchmark data frames
bench_summary <- function(df, method = c("metro_mean","pop_weighted")) {
  method <- match.arg(method)
  if (method == "metro_mean") {
    df %>%
      summarise(
        pop_chg_5y  = mean(pop_chg_5y,  na.rm=TRUE),
        gdp_chg_5y  = mean(gdp_chg_5y,  na.rm=TRUE),
        gdp_pc_chg_5y = mean(gdp_pc_chg_5y,  na.rm=TRUE),
        inc_chg_5y  = mean(inc_chg_5y,  na.rm=TRUE),
        inc_pc_chg_5y = mean(inc_pc_chg_5y,  na.rm=TRUE),
        pop_cagr_5y = mean(pop_cagr_5y, na.rm=TRUE),
        gdp_cagr_5y = mean(gdp_cagr_5y, na.rm=TRUE),
        gdp_pc_cagr_5y = mean(gdp_pc_cagr_5y,  na.rm=TRUE),
        inc_cagr_5y = mean(inc_cagr_5y, na.rm=TRUE),
        inc_pc_cagr_5y = mean(inc_pc_cagr_5y,  na.rm=TRUE)
      )
  } else {
    w <- df$population
    w[is.na(w)] <- 0
    if (sum(w) == 0) w <- rep(1, nrow(df))
    df %>%
      summarise(
        pop_chg_5y  = weighted.mean(pop_chg_5y,  w, na.rm=TRUE),
        gdp_chg_5y  = weighted.mean(gdp_chg_5y,  w, na.rm=TRUE),
        gdp_pc_chg_5y  = weighted.mean(gdp_pc_chg_5y,  w, na.rm=TRUE),
        inc_chg_5y  = weighted.mean(inc_chg_5y, w, na.rm=TRUE),
        inc_pc_chg_5y  = weighted.mean(inc_pc_chg_5y,  w, na.rm=TRUE),
        pop_cagr_5y = weighted.mean(pop_cagr_5y, w, na.rm=TRUE),
        gdp_cagr_5y = weighted.mean(gdp_cagr_5y, w, na.rm=TRUE),
        gdp_pc_cagr_5y  = weighted.mean(gdp_pc_cagr_5y,  w, na.rm=TRUE),
        inc_cagr_5y = weighted.mean(inc_cagr_5y, w, na.rm=TRUE),
        inc_pc_cagr_5y  = weighted.mean(inc_pc_cagr_5y,  w, na.rm=TRUE)
      )
  }
}