# Staging Layer Coverage Checklist

Coverage unit: source/theme family contract.
Replica tables listed in a family doc's coverage matrix are considered documented there and should not be tracked as missing standalone dictionaries.

Contract family count: 22

| Status | Source | Theme | Contract dictionary | Materialized coverage |
| --- | --- | --- | --- | --- |
| [x] | ACS | Age | [staging__acs_age.md](./staging__acs_age.md) | `acs_age_us, acs_age_region, acs_age_division, acs_age_state, acs_age_county, acs_age_place, acs_age_zcta, acs_age_tract, acs_age_tract_fl, acs_age_tract_ga, acs_age_tract_nc, acs_age_tract_sc` |
| [x] | ACS | Education | [staging__acs_education.md](./staging__acs_education.md) | `acs_edu_us, acs_edu_region, acs_edu_division, acs_edu_state, acs_edu_county, acs_edu_place, acs_edu_zcta, acs_edu_tract, acs_edu_tract_fl, acs_edu_tract_ga, acs_edu_tract_nc, acs_edu_tract_sc` |
| [x] | ACS | Housing | [staging__acs_housing.md](./staging__acs_housing.md) | `acs_housing_us, acs_housing_region, acs_housing_division, acs_housing_state, acs_housing_county, acs_housing_place, acs_housing_zcta, acs_housing_tract, acs_housing_tract_fl, acs_housing_tract_ga, acs_housing_tract_nc, acs_housing_tract_sc` |
| [x] | ACS | Income | [staging__acs_income.md](./staging__acs_income.md) | `acs_income_us, acs_income_region, acs_income_division, acs_income_state, acs_income_county, acs_income_place, acs_income_zcta, acs_income_tract, acs_income_tract_fl, acs_income_tract_ga, acs_income_tract_nc, acs_income_tract_sc` |
| [x] | ACS | Labor | [staging__acs_labor.md](./staging__acs_labor.md) | `acs_labor_us, acs_labor_region, acs_labor_division, acs_labor_state, acs_labor_county, acs_labor_place, acs_labor_zcta, acs_labor_tract, acs_labor_tract_fl, acs_labor_tract_ga, acs_labor_tract_nc, acs_labor_tract_sc` |
| [x] | ACS | Migration | [staging__acs_migration.md](./staging__acs_migration.md) | `acs_migration_us, acs_migration_region, acs_migration_division, acs_migration_state, acs_migration_county, acs_migration_place, acs_migration_zcta, acs_migration_tract, acs_migration_tract_fl, acs_migration_tract_ga, acs_migration_tract_nc, acs_migration_tract_sc` |
| [x] | ACS | Race | [staging__acs_race.md](./staging__acs_race.md) | `acs_race_us, acs_race_region, acs_race_division, acs_race_state, acs_race_county, acs_race_place, acs_race_zcta, acs_race_tract, acs_race_tract_fl, acs_race_tract_ga, acs_race_tract_nc, acs_race_tract_sc` |
| [x] | ACS | Social Infrastructure | [staging__acs_social_infrastructure.md](./staging__acs_social_infrastructure.md) | `acs_social_infra_us, acs_social_infra_region, acs_social_infra_division, acs_social_infra_state, acs_social_infra_county, acs_social_infra_place, acs_social_infra_zcta, acs_social_infra_tract, acs_social_infra_tract_fl, acs_social_infra_tract_ga, acs_social_infra_tract_nc, acs_social_infra_tract_sc` |
| [x] | ACS | Transportation | [staging__acs_transportation.md](./staging__acs_transportation.md) | `acs_transport_us, acs_transport_region, acs_transport_division, acs_transport_state, acs_transport_county, acs_transport_place, acs_transport_zcta, acs_transport_tract, acs_transport_tract_fl, acs_transport_tract_ga, acs_transport_tract_nc, acs_transport_tract_sc` |
| [x] | BEA | CAGDP2 | [staging__bea_cagdp2.md](./staging__bea_cagdp2.md) | `bea_regional_cbsa_cagdp2, bea_regional_county_cagdp2, bea_regional_state_cagdp2` |
| [x] | BEA | CAGDP9 | [staging__bea_cagdp9.md](./staging__bea_cagdp9.md) | `bea_regional_cbsa_cagdp9, bea_regional_county_cagdp9, bea_regional_state_cagdp9` |
| [x] | BEA | CAINC1 | [staging__bea_cainc1.md](./staging__bea_cainc1.md) | `bea_regional_cbsa_cainc1, bea_regional_county_cainc1, bea_regional_state_cainc1` |
| [x] | BEA | CAINC4 | [staging__bea_cainc4.md](./staging__bea_cainc4.md) | `bea_regional_cbsa_cainc4, bea_regional_county_cainc4, bea_regional_state_cainc4` |
| [x] | BEA | MARPP | [staging__bea_marpp.md](./staging__bea_marpp.md) | `bea_regional_cbsa_marpp, bea_regional_state_marpp` |
| [x] | BEA | Metadata | [staging__bea_metadata.md](./staging__bea_metadata.md) | `bea_regional_tables, bea_regional_line_codes` |
| [x] | BLS | LAUS | [staging__bls_laus.md](./staging__bls_laus.md) | `bls_laus_county` |
| [x] | BPS | Building Permits Survey | [staging__bps.md](./staging__bps.md) | `bps_region, bps_division, bps_state, bps_county, bps_place` |
| [x] | HUD | CHAS | [staging__hud_chas.md](./staging__hud_chas.md) | `hud_chas_state, hud_chas_county, hud_chas_place` |
| [x] | HUD | FMR | [staging__hud_fmr.md](./staging__hud_fmr.md) | `hud_fmr_county, hud_fmr_zip, hud_rent50_county` |
| [x] | IRS | Migration | [staging__irs_migration.md](./staging__irs_migration.md) | `irs_inflow_migration_county, irs_inflow_migration_state` |
| [x] | Zillow | ZHVI | [staging__zillow_zhvi.md](./staging__zillow_zhvi.md) | `zillow_zhvi_state, zillow_zhvi_county, zillow_zhvi_city, zillow_zhvi_zip_code` |
| [x] | Zillow | ZORI | [staging__zillow_zori.md](./staging__zillow_zori.md) | `zillow_zori_county, zillow_zori_city, zillow_zori_zip_code` |
