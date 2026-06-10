# Phase 1 Mapping Audit

This audit checks the Phase 1 variable-selection scope across four layers:

1. `INTELLIGENCE_LAYER_ROADMAP.md`
2. `exploration/intelligence_framework/docs/metric_map.md`
3. Gold ETL contracts and Gold data dictionaries
4. Existing Phase 1 notebooks in `exploration/intelligence_framework/phase_variable_selection/`

Status key:

- `green`: roadmap / metric map / Gold contract / notebook are aligned
- `yellow`: the metric exists, but the canonical table, column name, or notebook usage needs cleanup
- `red`: the current notebook or docs point to the wrong table / missing field and should be fixed before Phase 1 runs

## Source-of-Truth Decisions

These are the decisions that make Phase 1 runnable without carrying naming ambiguity into later phases.

| Decision | Outcome |
|---|---|
| Affordability burden metric for Phase 1 | Use `pct_rent_burden_30plus` as the recurring CBSA affordability-burden field. Keep CHAS fields (`pct_cost_burdened`, `pct_severely_cost_burdened`, `pct_renter_severely_cost_burdened`) as separate contextual metrics rather than treating `pct_cost_burden_30plus` as a live Gold column. |
| Foreign-born source for Character | Use `gold.migration_wide.pct_foreign_born`, not `gold.population_demographics`. |
| Homeownership and permit supply source | Use `gold.housing_core_wide` as the primary source for `owner_occ_rate`, `permits_per_1000_housing_units`, `permits_share_multifam_units`, and `permits_avg_units_per_bldg`. `gold.affordability_wide` is acceptable only when the same field is intentionally reused as a convenience copy. |
| Character social capital coverage | Include both `economic_connectedness` and `civic_engagement_volunteering_rate` in Character Phase 1. |
| Opportunity cross-frame overlap | Include `economic_connectedness` in Opportunity Phase 1 as the explicit cross-frame overlap variable. |
| Opportunity market rent momentum | Include `zori_annual_avg_yoy_pct` in the Opportunity candidate set; it is in the Gold contract and in the metric map and should not be omitted from the roadmap candidate list. |

## Character

| Metric | Metric map source | Gold contract check | Notebook check | Status | Note |
|---|---|---|---|---|---|
| `median_age` | `gold.population_demographics` | present | present | `green` | Aligned. |
| `pct_foreign_born` | `gold.migration_wide` | present | present | `green` | Fixed in this pass to use the correct Gold table. |
| `pct_ba_plus` | `gold.population_demographics` | present | present | `green` | Aligned. |
| `diversity_index` | `gold.population_demographics` | present | present | `green` | Aligned. |
| `pct_white_nh` | `gold.population_demographics` | present | present | `green` | Aligned. |
| `pct_black_nh` | `gold.population_demographics` | present | present | `green` | Aligned. |
| `pct_hispanic` | `gold.population_demographics` | present | present | `green` | Aligned. |
| `pct_asian_nh` | `gold.population_demographics` | present | present | `green` | Aligned. |
| `pct_same_house` | `gold.migration_wide` | present | present | `green` | Aligned. |
| `mobility_rate` | `gold.migration_wide` | present | present | `green` | Aligned. |
| `pct_moved_diff_st` | `gold.migration_wide` | present | present | `green` | Aligned. |
| `irs_net_migration_rate` | `gold.migration_wide` | present | present | `green` | Aligned. |
| `economic_connectedness` | `gold.social_fabric_wide` | present | present | `green` | Aligned. |
| `civic_engagement_volunteering_rate` | `gold.social_fabric_wide` | present | present | `green` | Fixed in this pass. |
| `owner_occ_rate` | `gold.housing_core_wide` / `gold.affordability_wide` | present | present | `green` | Fixed in this pass to use the housing table. |
| `pct_struct_multifam` | `gold.housing_core_wide` | present | present | `green` | Aligned. |
| `pop_weighted_density_sqmi` | `gold.transport_built_form_wide` | present | present | `green` | Aligned. |

## Livability

| Metric | Metric map source | Gold contract check | Notebook check | Status | Note |
|---|---|---|---|---|---|
| `pct_rent_burden_30plus` | `gold.affordability_wide` / `gold.housing_core_wide` | present | present | `green` | Fixed in this pass to use the real Gold column name. |
| `rent_to_income` | `gold.affordability_wide` | present | present | `green` | Aligned. |
| `value_to_income` | `gold.affordability_wide` | present | present | `green` | Aligned. |
| `rpp_real_pc_income` | `gold.affordability_wide` | present | present | `green` | Aligned. |
| `pct_commute_transit` | `gold.transport_built_form_wide` | present | present | `green` | Aligned. |
| `mean_travel_time` | `gold.transport_built_form_wide` | present | present | `green` | Aligned. |
| `pct_hh_0_vehicles` | `gold.transport_built_form_wide` | present | present | `green` | Aligned. |
| `life_expectancy` | `gold.health_wide` | present | present | `green` | Aligned. |
| `premature_death_rate` | `gold.health_wide` | present | present | `green` | Aligned. |
| `physical_inactivity` | `gold.health_wide` | present | present | `green` | Aligned. |
| `adult_obesity` | `gold.health_wide` | present | present | `green` | Aligned. |
| `poor_mental_health_days` | `gold.health_wide` | present | present | `green` | Aligned. |
| `drug_overdose_death_rate` | `gold.health_wide` | present | present | `green` | Aligned. |
| `homicide_rate` | `gold.health_wide` | present | present | `green` | Aligned. |
| `firearm_fatality_rate` | `gold.health_wide` | present | present | `green` | Aligned. |
| `motor_vehicle_crash_rate` | `gold.health_wide` | present | present | `green` | Aligned. |
| `aqi_median` | `gold.environment_wide` | present | present | `green` | Aligned. |
| `aqi_unhealthy_days` | `gold.environment_wide` | present | present | `green` | Aligned. |
| `fema_risk_score` | `gold.environment_wide` | present | present | `green` | Aligned. |
| `ej_pm25` | `gold.environment_wide` | present | present | `green` | Aligned. |
| `permits_per_1000_housing_units` | `gold.housing_core_wide` primary | present | present via `gold.housing_core_wide` | `green` | Aligned. |
| `permits_share_multifam_units` | `gold.housing_core_wide` | present | present | `green` | Aligned. |
| `permits_avg_units_per_bldg` | `gold.housing_core_wide` | present | present | `green` | Aligned. |
| `vacancy_rate` | `gold.housing_core_wide` / `gold.affordability_wide` | present | present | `green` | Aligned. |
| `hs_graduation_rate` | `gold.health_wide` | present | present | `green` | Present as an education companion metric in the current notebook. |
| `math_score_index` | `gold.health_wide` | present | present | `green` | Present as an education companion metric in the current notebook. |
| `reading_score_index` | `gold.health_wide` | present | present | `green` | Present as an education companion metric in the current notebook. |

## Opportunity

| Metric | Metric map source | Gold contract check | Notebook check | Status | Note |
|---|---|---|---|---|---|
| `income_pc_growth_5yr` | `gold.economics_income_wide` | present | present | `green` | Aligned. |
| `income_pc_growth_1yr` | `gold.economics_income_wide` | present | present | `green` | Aligned. |
| `lfpr` | `gold.economics_labor_wide` | present | present | `green` | Aligned. |
| `pct_unemployment_rate` | `gold.economics_labor_wide` | present | present | `green` | Aligned. |
| `gini_index` | `gold.economics_income_wide` | present | present | `green` | Aligned. |
| `pov_rate_change_5yr` | `gold.economics_income_wide` | present | present | `green` | Included in notebook even though the roadmap summary line omitted it. |
| `hpi_5yr_pct` | `gold.housing_market_wide` | present | present | `green` | Aligned. |
| `hpi_yoy_pct` | `gold.housing_market_wide` | present | present | `green` | Aligned. |
| `zori_annual_avg_yoy_pct` | `gold.housing_market_wide` | present | present | `green` | Added to the roadmap candidate list in this pass. |
| `pop_growth_5yr` | `gold.population_demographics` | present | present | `green` | Aligned. |
| `irs_net_migration_rate` | `gold.migration_wide` | present | present | `green` | Aligned. |
| `irs_net_agi` | `gold.migration_wide` | present | present in notebook | `green` | Useful for the divergence diagnostic already mentioned in the roadmap narrative. |
| `permits_per_1000_housing_units` | `gold.housing_core_wide` primary | present | present | `green` | Fixed in this pass to use the primary housing-core source. |
| `real_gdp_growth_5yr` | `gold.economics_gdp_wide` | present | present | `green` | Aligned. |
| `productivity_growth_5yr` | `gold.economics_gdp_wide` | present | present | `green` | Aligned. |
| `industry_concentration_hhi` | `gold.economics_industry_wide` | present | present | `green` | Aligned. |
| `bfs_business_application_rate_per_1000_establishments` | `gold.economics_industry_wide` | present | present | `green` | Aligned. |
| `pct_qcew_private_emp_*` sector shares | `gold.economics_industry_wide` | present | present | `green` | Added representative sector-share candidates in this pass. |
| `pct_real_gdp_*` sector shares | `gold.economics_industry_wide` | present | present | `green` | Added representative BEA GDP-share candidates in this pass. |
| `lq_*` specialization metrics | `gold.economics_industry_wide` | present | present | `green` | Now explicitly positioned as complements to sector-share candidates. |
| `economic_connectedness` | `gold.social_fabric_wide` | present | present | `green` | Fixed in this pass as the explicit cross-frame overlap variable. |

## Notebook-Level Findings

| Notebook | Finding | Status |
|---|---|---|
| `character_variable_selection.qmd` | Pulls `pct_foreign_born` from the wrong table | fixed in this pass |
| `character_variable_selection.qmd` | Omits `civic_engagement_volunteering_rate` | fixed in this pass |
| `character_variable_selection.qmd` | Pulls `owner_occ_rate` from `gold.transport_built_form_wide` instead of a housing table | fixed in this pass |
| `character_variable_selection.qmd` | Refers to Character clustering as Phase 3 instead of Phase 2 | fixed in this pass |
| `livability_variable_selection.qmd` | Uses notebook-local alias `pct_cost_burden_30plus` for a non-canonical column name | fixed in this pass |
| `opportunity_variable_selection.qmd` | Omits `economic_connectedness` despite the roadmap calling it out as a cross-frame overlap | fixed in this pass |
| `opportunity_variable_selection.qmd` | Uses permit supply from `gold.affordability_wide` convenience copy instead of the primary housing-core source | fixed in this pass |
| `opportunity_variable_selection.qmd` | Uses LQ specialization metrics without also exposing the sector-share family named in the metric map | fixed in this pass with a mixed candidate set |

## Ready-State Summary

After the notebook and doc fixes in this pass:

- Phase 1 now has a clean canonical source for every Character, Livability, and Opportunity candidate metric.
- The blocking mapping errors are resolved in the current docs and Phase 1 notebooks.
- The main remaining analytical choice is how aggressively to use sector-share metrics versus LQ specialization metrics in the final Opportunity reduction pass. The notebook is now set up to evaluate both rather than forcing the choice up front.
