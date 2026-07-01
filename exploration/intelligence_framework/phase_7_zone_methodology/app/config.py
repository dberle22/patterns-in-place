"""Phase 7 tract EDA app configuration."""

from __future__ import annotations

APP_TITLE = "Phase 7 — Tract KPI Explorer"

# The Sprint 1.2 locked Phase 7 KPI contract drawn from
# zone_methodology_notes.md. Grouped by theme. is_opportunity_zone is carried
# as context, not in the clustering vector.
TRACT_KPIS: list[dict] = [
    # --- Theme A: Character ---
    {"kpi_id": "pct_hispanic",              "display_name": "% Hispanic",                   "theme": "Character", "polarity": 0},
    {"kpi_id": "pct_black_nh",              "display_name": "% Black (non-Hispanic)",        "theme": "Character", "polarity": 0},
    {"kpi_id": "pct_asian_nh",              "display_name": "% Asian (non-Hispanic)",        "theme": "Character", "polarity": 0},
    {"kpi_id": "pct_age_over_64",           "display_name": "% Age 65+",                    "theme": "Character", "polarity": 0},
    {"kpi_id": "pct_ba_plus",              "display_name": "% BA+",                         "theme": "Character", "polarity": 1},
    {"kpi_id": "pct_same_house",            "display_name": "% Same House (Stability)",     "theme": "Character", "polarity": 1},
    {"kpi_id": "owner_occ_rate",            "display_name": "Owner Occupancy Rate",         "theme": "Character", "polarity": 1},
    {"kpi_id": "pop_weighted_density_sqmi", "display_name": "Pop-Weighted Density (sq mi)", "theme": "Character", "polarity": 1},

    # --- Theme B: Livability ---
    {"kpi_id": "pct_rent_burden_30plus",    "display_name": "% Rent Burdened (30%+)",       "theme": "Livability", "polarity": -1},
    {"kpi_id": "vacancy_rate",              "display_name": "Vacancy Rate",                 "theme": "Livability", "polarity": -1},
    {"kpi_id": "pct_commute_walk",          "display_name": "% Commute by Walk",            "theme": "Livability", "polarity": 1},
    {"kpi_id": "walkability_index",         "display_name": "Walkability Index",            "theme": "Livability", "polarity": 1},
    {"kpi_id": "pct_no_internet_access",    "display_name": "% No Internet Access",         "theme": "Livability", "polarity": -1},
    {"kpi_id": "ejs_pm25",                  "display_name": "EJScreen PM2.5",               "theme": "Livability", "polarity": -1},
    {"kpi_id": "fema_risk_score",           "display_name": "FEMA Risk Score",              "theme": "Livability", "polarity": -1},

    # --- Theme C: Opportunity ---
    {"kpi_id": "pov_rate",                      "display_name": "Poverty Rate",                     "theme": "Opportunity", "polarity": -1},
    {"kpi_id": "pov_rate_change_3yr",           "display_name": "Poverty Rate Change (3yr)",        "theme": "Opportunity", "polarity": -1},
    {"kpi_id": "pct_unemployment_rate",         "display_name": "Unemployment Rate",                "theme": "Opportunity", "polarity": -1},
    {"kpi_id": "pct_ba_plus_change_3yr",        "display_name": "% BA+ Change (3yr)",               "theme": "Opportunity", "polarity": 1},
    # LODES-derived KPIs (economics_lodes_wide, geo_level = 'tract')
    {"kpi_id": "jobs_per_resident",             "display_name": "Jobs-to-Workers Ratio",            "theme": "Opportunity", "polarity": 1},
    {"kpi_id": "pct_jobs_high_wage",            "display_name": "% Jobs High Wage",                 "theme": "Opportunity", "polarity": 1},
    {"kpi_id": "pct_jobs_professional_services","display_name": "% Jobs Professional Services",     "theme": "Opportunity", "polarity": 1},
]

KPI_IDS = [kpi["kpi_id"] for kpi in TRACT_KPIS]

THEME_COLORS = {
    "Character":    "#2b8cbe",
    "Livability":   "#31a354",
    "Opportunity":  "#d94801",
}

# Source table map: kpi_id -> (schema, table, column).
# All from the Gold layer at geo_level = 'tract'.
KPI_SOURCE_MAP: dict[str, tuple[str, str, str]] = {
    "pct_hispanic":              ("gold", "population_demographics",    "pct_hispanic"),
    "pct_black_nh":              ("gold", "population_demographics",    "pct_black_nh"),
    "pct_asian_nh":              ("gold", "population_demographics",    "pct_asian_nh"),
    "pct_age_over_64":           ("gold", "population_demographics",    "pct_age_over_64"),
    "pct_ba_plus":               ("gold", "population_demographics",    "pct_ba_plus"),
    "pct_ba_plus_change_3yr":    ("gold", "population_demographics",    "pct_ba_plus_change_3yr"),
    "pct_same_house":            ("gold", "migration_wide",             "pct_same_house"),
    "owner_occ_rate":            ("gold", "housing_core_wide",          "owner_occ_rate"),
    "pct_rent_burden_30plus":    ("gold", "housing_core_wide",          "pct_rent_burden_30plus"),
    "vacancy_rate":              ("gold", "housing_core_wide",          "vacancy_rate"),
    "pct_no_internet_access":    ("gold", "social_infra_wide",          "pct_no_internet_access"),
    "pop_weighted_density_sqmi": ("gold", "transport_built_form_wide",  "pop_weighted_density_sqmi"),
    "pct_commute_walk":          ("gold", "transport_built_form_wide",  "pct_commute_walk"),
    "walkability_index":         ("gold", "transport_built_form_sld",   "walkability_index"),
    "ejs_pm25":                  ("gold", "environment_wide",           "ejs_pm25"),
    "fema_risk_score":           ("gold", "environment_wide",           "fema_risk_score"),
    "pov_rate":                      ("gold", "economics_income_wide",   "pov_rate"),
    "pov_rate_change_3yr":           ("gold", "economics_income_wide",   "pov_rate_change_3yr"),
    "pct_unemployment_rate":         ("gold", "economics_labor_wide",    "pct_unemployment_rate"),
    # LODES — mapped to exact column names in economics_lodes_wide
    "jobs_per_resident":             ("gold", "economics_lodes_wide",    "jobs_to_workers_ratio"),
    "pct_jobs_high_wage":            ("gold", "economics_lodes_wide",    "pct_jobs_earnings_high"),
    "pct_jobs_professional_services":("gold", "economics_lodes_wide",    "pct_jobs_ind_professional_scientific_technical"),
}
