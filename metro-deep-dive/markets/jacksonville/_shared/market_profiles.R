# Shared market profile registry for Retail Opportunity Finder

MARKET_PROFILES <- list(
  jacksonville_fl = list(
    market_key = "jacksonville_fl",
    cbsa_code = "27260",
    state_scope = c("FL"),
    benchmark_region_type = "census_division",
    benchmark_region_value = "South Atlantic",
    benchmark_region_label = "South Atlantic",
    peers = c("27260", "48900", "42340", "39580", "24860"),
    labels = list(
      cbsa_name = "Jacksonville",
      cbsa_name_full = "Jacksonville, FL",
      market_name = "Jacksonville market",
      peer_group = "Southeast peers",
      target_flag = "Jacksonville",
      us_label = "United States (CBSAs)"
    )
  ),
  orlando_fl = list(
    market_key = "orlando_fl",
    cbsa_code = "36740",
    state_scope = c("FL"),
    benchmark_region_type = "census_division",
    benchmark_region_value = "South Atlantic",
    benchmark_region_label = "South Atlantic",
    peers = c("36740", "45300", "33100", "27260", "29460"),
    labels = list(
      cbsa_name = "Orlando",
      cbsa_name_full = "Orlando-Kissimmee-Sanford, FL",
      market_name = "Orlando market",
      peer_group = "Florida peers",
      target_flag = "Orlando",
      us_label = "United States (CBSAs)"
    )
  ),
  gainesville_fl = list(
    market_key = "gainesville_fl",
    cbsa_code = "23540",
    state_scope = c("FL"),
    benchmark_region_type = "census_division",
    benchmark_region_value = "South Atlantic",
    benchmark_region_label = "South Atlantic",
    peers = c("23540", "27260", "36740", "29460", "36100"),
    labels = list(
      cbsa_name = "Gainesville",
      cbsa_name_full = "Gainesville, FL",
      market_name = "Gainesville market",
      peer_group = "Florida peers",
      target_flag = "Gainesville",
      us_label = "United States (CBSAs)"
    )
  ),
  wilmington_nc = list(
    market_key = "wilmington_nc",
    cbsa_code = "48900",
    state_scope = c("NC"),
    benchmark_region_type = "census_division",
    benchmark_region_value = "South Atlantic",
    benchmark_region_label = "South Atlantic",
    peers = c("48900", "42340", "24860", "39580", "27260"),
    labels = list(
      cbsa_name = "Wilmington",
      cbsa_name_full = "Wilmington, NC",
      market_name = "Wilmington market",
      peer_group = "Southeast peers",
      target_flag = "Wilmington",
      us_label = "United States (CBSAs)"
    )
  ),
  savannah_ga = list(
    market_key = "savannah_ga",
    cbsa_code = "42340",
    state_scope = c("GA"),
    benchmark_region_type = "census_division",
    benchmark_region_value = "South Atlantic",
    benchmark_region_label = "South Atlantic",
    peers = c("42340", "48900", "24860", "39580", "27260"),
    labels = list(
      cbsa_name = "Savannah",
      cbsa_name_full = "Savannah, GA",
      market_name = "Savannah market",
      peer_group = "Southeast peers",
      target_flag = "Savannah",
      us_label = "United States (CBSAs)"
    )
  ),
  raleigh_nc = list(
    market_key = "raleigh_nc",
    cbsa_code = "39580",
    state_scope = c("NC"),
    benchmark_region_type = "census_division",
    benchmark_region_value = "South Atlantic",
    benchmark_region_label = "South Atlantic",
    peers = c("39580", "48900", "42340", "24860", "27260"),
    labels = list(
      cbsa_name = "Raleigh",
      cbsa_name_full = "Raleigh-Cary, NC",
      market_name = "Raleigh market",
      peer_group = "Southeast peers",
      target_flag = "Raleigh",
      us_label = "United States (CBSAs)"
    )
  ),
  greenville_sc = list(
    market_key = "greenville_sc",
    cbsa_code = "24860",
    state_scope = c("SC"),
    benchmark_region_type = "census_division",
    benchmark_region_value = "South Atlantic",
    benchmark_region_label = "South Atlantic",
    peers = c("24860", "48900", "42340", "39580", "27260"),
    labels = list(
      cbsa_name = "Greenville",
      cbsa_name_full = "Greenville-Anderson, SC",
      market_name = "Greenville market",
      peer_group = "Southeast peers",
      target_flag = "Greenville",
      us_label = "United States (CBSAs)"
    )
  )
)
