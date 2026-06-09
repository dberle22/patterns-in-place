-- Gold environment mart
-- Grain: one row per geo_level + geo_id + year
-- Notes:
--   * AQI remains the source-faithful county + CBSA backbone for the table.
--   * EJScreen is rolled up from tract to county / CBSA with population-weighted
--     averages so we can preserve the shared Gold geography contract while still
--     carrying the tract-first archive into the environment mart.
--   * FEMA NRI is joined from the county + CBSA Silver table at the shared
--     `geo_level + geo_id + year` grain and promoted as a compact risk slice.

create or replace table patterns_in_place.gold.environment_wide as
with aqi as (
    select
        geo_level,
        geo_id,
        geo_name,
        year,
        days_with_aqi,
        good_days,
        moderate_days,
        usg_days,
        unhealthy_days,
        very_unhealthy_days,
        hazardous_days,
        max_aqi,
        aqi_p90,
        aqi_median,
        days_ozone,
        days_pm25
    from patterns_in_place.silver.epa_aqi
),
ejscreen_tract_bridge as (
    select
        e.year,
        e.geo_id as tract_geoid,
        d.county_geoid,
        d.parent_cbsa_code as cbsa_code,
        e.total_population,
        e.pm25,
        e.ozone,
        e.diesel_pm,
        e.traffic_proximity,
        e.superfund_proximity,
        e.rmp_proximity,
        e.wastewater_discharge,
        e.drinking_water_noncompliance,
        e.pctile_pm25_us,
        e.pctile_ozone_us,
        e.pctile_diesel_pm_us,
        e.pctile_traffic_us,
        e.pctile_superfund_us,
        e.pctile_rmp_us,
        e.pctile_wastewater_us,
        e.pctile_drinking_water_us,
        e.count_high_exposure_indicators,
        e.count_high_exposure_supplemental
    from patterns_in_place.silver.ejscreen e
    inner join patterns_in_place.gold.dim_geo d
        on e.geo_level = 'tract'
       and d.geo_level = 'tract'
       and e.geo_id = d.geo_id
),
ejscreen_county as (
    select
        'county' as geo_level,
        county_geoid as geo_id,
        year,
        sum(total_population) as ejs_population_covered,
        sum(pm25 * total_population) / nullif(sum(total_population), 0) as ejs_pm25,
        sum(ozone * total_population) / nullif(sum(total_population), 0) as ejs_ozone,
        sum(diesel_pm * total_population) / nullif(sum(total_population), 0) as ejs_diesel_pm,
        sum(traffic_proximity * total_population) / nullif(sum(total_population), 0) as ejs_traffic_proximity,
        sum(superfund_proximity * total_population) / nullif(sum(total_population), 0) as ejs_superfund_proximity,
        sum(rmp_proximity * total_population) / nullif(sum(total_population), 0) as ejs_rmp_proximity,
        sum(wastewater_discharge * total_population) / nullif(sum(total_population), 0) as ejs_wastewater_discharge,
        sum(drinking_water_noncompliance * total_population) / nullif(sum(total_population), 0) as ejs_drinking_water_noncompliance,
        sum(pctile_pm25_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_pm25_us,
        sum(pctile_ozone_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_ozone_us,
        sum(pctile_diesel_pm_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_diesel_pm_us,
        sum(pctile_traffic_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_traffic_us,
        sum(pctile_superfund_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_superfund_us,
        sum(pctile_rmp_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_rmp_us,
        sum(pctile_wastewater_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_wastewater_us,
        sum(pctile_drinking_water_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_drinking_water_us,
        sum(count_high_exposure_indicators * total_population) / nullif(sum(total_population), 0) as ejs_avg_high_exposure_indicators,
        sum(count_high_exposure_supplemental * total_population) / nullif(sum(total_population), 0) as ejs_avg_high_exposure_supplemental
    from ejscreen_tract_bridge
    group by 1, 2, 3
),
ejscreen_cbsa as (
    select
        'cbsa' as geo_level,
        cbsa_code as geo_id,
        year,
        sum(total_population) as ejs_population_covered,
        sum(pm25 * total_population) / nullif(sum(total_population), 0) as ejs_pm25,
        sum(ozone * total_population) / nullif(sum(total_population), 0) as ejs_ozone,
        sum(diesel_pm * total_population) / nullif(sum(total_population), 0) as ejs_diesel_pm,
        sum(traffic_proximity * total_population) / nullif(sum(total_population), 0) as ejs_traffic_proximity,
        sum(superfund_proximity * total_population) / nullif(sum(total_population), 0) as ejs_superfund_proximity,
        sum(rmp_proximity * total_population) / nullif(sum(total_population), 0) as ejs_rmp_proximity,
        sum(wastewater_discharge * total_population) / nullif(sum(total_population), 0) as ejs_wastewater_discharge,
        sum(drinking_water_noncompliance * total_population) / nullif(sum(total_population), 0) as ejs_drinking_water_noncompliance,
        sum(pctile_pm25_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_pm25_us,
        sum(pctile_ozone_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_ozone_us,
        sum(pctile_diesel_pm_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_diesel_pm_us,
        sum(pctile_traffic_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_traffic_us,
        sum(pctile_superfund_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_superfund_us,
        sum(pctile_rmp_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_rmp_us,
        sum(pctile_wastewater_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_wastewater_us,
        sum(pctile_drinking_water_us * total_population) / nullif(sum(total_population), 0) as ejs_pctile_drinking_water_us,
        sum(count_high_exposure_indicators * total_population) / nullif(sum(total_population), 0) as ejs_avg_high_exposure_indicators,
        sum(count_high_exposure_supplemental * total_population) / nullif(sum(total_population), 0) as ejs_avg_high_exposure_supplemental
    from ejscreen_tract_bridge
    where cbsa_code is not null
    group by 1, 2, 3
),
ejscreen_rollup as (
    select * from ejscreen_county
    union all
    select * from ejscreen_cbsa
),
fema as (
    select
        geo_level,
        geo_id,
        year,
        risk_score as fema_risk_score,
        eal_score as fema_eal_score,
        alr_national_pctile as fema_alr_national_pctile,
        alr_vra_national_pctile as fema_alr_vra_national_pctile,
        social_vulnerability_score as fema_social_vulnerability_score,
        community_resilience_score as fema_community_resilience_score,
        avalanche_risk_score as fema_avalanche_risk_score,
        coastal_flooding_risk_score as fema_coastal_flooding_risk_score,
        cold_wave_risk_score as fema_cold_wave_risk_score,
        drought_risk_score as fema_drought_risk_score,
        earthquake_risk_score as fema_earthquake_risk_score,
        hail_risk_score as fema_hail_risk_score,
        heat_wave_risk_score as fema_heat_wave_risk_score,
        hurricane_risk_score as fema_hurricane_risk_score,
        ice_storm_risk_score as fema_ice_storm_risk_score,
        inland_flooding_risk_score as fema_inland_flooding_risk_score,
        landslide_risk_score as fema_landslide_risk_score,
        lightning_risk_score as fema_lightning_risk_score,
        strong_wind_risk_score as fema_strong_wind_risk_score,
        tornado_risk_score as fema_tornado_risk_score,
        tsunami_risk_score as fema_tsunami_risk_score,
        volcanic_activity_risk_score as fema_volcanic_activity_risk_score,
        wildfire_risk_score as fema_wildfire_risk_score,
        winter_weather_risk_score as fema_winter_weather_risk_score
    from patterns_in_place.silver.fema_nri
)
select
    aqi.geo_level,
    aqi.geo_id,
    aqi.geo_name,
    aqi.year,
    aqi.days_with_aqi,
    aqi.good_days,
    aqi.moderate_days,
    aqi.usg_days,
    aqi.unhealthy_days,
    aqi.very_unhealthy_days,
    aqi.hazardous_days,
    aqi.max_aqi,
    aqi.aqi_p90,
    aqi.aqi_median,
    aqi.days_ozone,
    aqi.days_pm25,
    ejs.ejs_population_covered,
    ejs.ejs_pm25,
    ejs.ejs_ozone,
    ejs.ejs_diesel_pm,
    ejs.ejs_traffic_proximity,
    ejs.ejs_superfund_proximity,
    ejs.ejs_rmp_proximity,
    ejs.ejs_wastewater_discharge,
    ejs.ejs_drinking_water_noncompliance,
    ejs.ejs_pctile_pm25_us,
    ejs.ejs_pctile_ozone_us,
    ejs.ejs_pctile_diesel_pm_us,
    ejs.ejs_pctile_traffic_us,
    ejs.ejs_pctile_superfund_us,
    ejs.ejs_pctile_rmp_us,
    ejs.ejs_pctile_wastewater_us,
    ejs.ejs_pctile_drinking_water_us,
    ejs.ejs_avg_high_exposure_indicators,
    ejs.ejs_avg_high_exposure_supplemental,
    fema.fema_risk_score,
    fema.fema_eal_score,
    fema.fema_alr_national_pctile,
    fema.fema_alr_vra_national_pctile,
    fema.fema_social_vulnerability_score,
    fema.fema_community_resilience_score,
    fema.fema_avalanche_risk_score,
    fema.fema_coastal_flooding_risk_score,
    fema.fema_cold_wave_risk_score,
    fema.fema_drought_risk_score,
    fema.fema_earthquake_risk_score,
    fema.fema_hail_risk_score,
    fema.fema_heat_wave_risk_score,
    fema.fema_hurricane_risk_score,
    fema.fema_ice_storm_risk_score,
    fema.fema_inland_flooding_risk_score,
    fema.fema_landslide_risk_score,
    fema.fema_lightning_risk_score,
    fema.fema_strong_wind_risk_score,
    fema.fema_tornado_risk_score,
    fema.fema_tsunami_risk_score,
    fema.fema_volcanic_activity_risk_score,
    fema.fema_wildfire_risk_score,
    fema.fema_winter_weather_risk_score
from aqi
left join ejscreen_rollup ejs
    on aqi.geo_level = ejs.geo_level
   and aqi.geo_id = ejs.geo_id
   and aqi.year = ejs.year
left join fema
    on aqi.geo_level = fema.geo_level
   and aqi.geo_id = fema.geo_id
   and aqi.year = fema.year
;
