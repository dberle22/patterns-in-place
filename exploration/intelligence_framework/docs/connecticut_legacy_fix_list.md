# Connecticut Legacy GEOID Fix List

Tables below still carry the legacy Connecticut county GEOIDs (`09001`-`09015`) and have CBSA rows in the contract, but currently produce `0` Connecticut CBSA rows.

Reference files:

- full audit: [connecticut_crosswalk_audit.csv](outputs/connecticut_crosswalk_audit.csv)
- filtered fix list: [connecticut_legacy_fix_tables.csv](outputs/connecticut_legacy_fix_tables.csv)

## Highest Priority For Intelligence Layer

- `silver.epa_sld`
- `silver.usda_food_atlas`
- `gold.transport_built_form_sld`
- `gold.food_access_wide`
- `gold.housing_market_wide`

## Silver Tables Needing The CT Legacy Fix

- `silver.bea_regional_cagdp2_long`
- `silver.bea_regional_cagdp2_wide`
- `silver.bea_regional_cagdp9_long`
- `silver.bea_regional_cagdp9_wide`
- `silver.bea_regional_cainc1_long`
- `silver.bea_regional_cainc1_wide`
- `silver.bea_regional_cainc4_long`
- `silver.bea_regional_cainc4_wide`
- `silver.epa_sld`
- `silver.hud_chas_burden`
- `silver.opportunity_insights_social_capital`
- `silver.usda_food_atlas`
- `silver.zillow_zhvi`
- `silver.zillow_zori`

## Gold Tables Needing The CT Legacy Fix

- `gold.food_access_wide`
- `gold.housing_market_wide`
- `gold.social_fabric_wide`
- `gold.transport_built_form_sld`

## Read

- The pattern is consistent: these tables are `legacy_only` for Connecticut county keys, while the current `silver.xwalk_cbsa_county` uses planning-region GEOIDs.
- The practical fix path is to standardize CT county-equivalent IDs before the county-to-CBSA rollup, or introduce a dedicated legacy-CT to planning-region bridge and join through that bridge during CBSA derivation.
