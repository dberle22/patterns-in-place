-- Gold housing market mart
-- Grain: one row per geo_level + geo_id + year
-- Notes:
--   * Uses Zillow Silver monthly series as the full contract surface.
--   * Annual averages are computed over observed monthly values only; missing months
--     are not backfilled after the Silver null-row trim.
--   * December values provide a point-in-time year-end reference alongside the
--     annual average series.

create or replace table patterns_in_place.gold.housing_market_wide as
with zhvi_yearly as (
    select
        lower(geo_level) as geo_level,
        geo_id,
        max(geo_name) as geo_name,
        year,
        avg(zhvi) as zhvi_annual_avg,
        max(case when month = 12 then zhvi end) as zhvi_december
    from patterns_in_place.silver.zillow_zhvi
    group by 1, 2, 4
),

zori_yearly as (
    select
        lower(geo_level) as geo_level,
        geo_id,
        max(geo_name) as geo_name,
        year,
        avg(zori) as zori_annual_avg,
        max(case when month = 12 then zori end) as zori_december
    from patterns_in_place.silver.zillow_zori
    group by 1, 2, 4
),

base as (
    select geo_level, geo_id, geo_name, year
    from zhvi_yearly

    union

    select geo_level, geo_id, geo_name, year
    from zori_yearly
),

metrics as (
    select
        b.geo_level,
        b.geo_id,
        coalesce(b.geo_name, zh.geo_name, zr.geo_name, fhfa.geo_name) as geo_name,
        b.year,
        zh.zhvi_annual_avg,
        zh.zhvi_december,
        zr.zori_annual_avg,
        zr.zori_december,
        fhfa.hpi_level,
        fhfa.hpi_yoy_pct,
        fhfa.hpi_5yr_pct,
        fhfa.hpi_10yr_pct,
        lag(zh.zhvi_annual_avg, 1) over (
            partition by b.geo_level, b.geo_id
            order by b.year
        ) as zhvi_annual_avg_lag1,
        lag(zh.zhvi_december, 1) over (
            partition by b.geo_level, b.geo_id
            order by b.year
        ) as zhvi_december_lag1,
        lag(zr.zori_annual_avg, 1) over (
            partition by b.geo_level, b.geo_id
            order by b.year
        ) as zori_annual_avg_lag1,
        lag(zr.zori_december, 1) over (
            partition by b.geo_level, b.geo_id
            order by b.year
        ) as zori_december_lag1
    from base b
    left join zhvi_yearly zh
        on b.geo_level = zh.geo_level
       and b.geo_id = zh.geo_id
       and b.year = zh.year
    left join zori_yearly zr
        on b.geo_level = zr.geo_level
       and b.geo_id = zr.geo_id
       and b.year = zr.year
    left join patterns_in_place.silver.fhfa_hpi fhfa
        on b.geo_level = fhfa.geo_level
       and b.geo_id = fhfa.geo_id
       and b.year = fhfa.year
)

select
    geo_level,
    geo_id,
    geo_name,
    year,
    hpi_level,
    hpi_yoy_pct,
    hpi_5yr_pct,
    hpi_10yr_pct,
    zhvi_annual_avg,
    zhvi_december,
    case
        when zhvi_annual_avg_lag1 > 0 then (zhvi_annual_avg - zhvi_annual_avg_lag1) / zhvi_annual_avg_lag1
        else null
    end as zhvi_annual_avg_yoy_pct,
    case
        when zhvi_december_lag1 > 0 then (zhvi_december - zhvi_december_lag1) / zhvi_december_lag1
        else null
    end as zhvi_december_yoy_pct,
    zori_annual_avg,
    zori_december,
    case
        when zori_annual_avg_lag1 > 0 then (zori_annual_avg - zori_annual_avg_lag1) / zori_annual_avg_lag1
        else null
    end as zori_annual_avg_yoy_pct,
    case
        when zori_december_lag1 > 0 then (zori_december - zori_december_lag1) / zori_december_lag1
        else null
    end as zori_december_yoy_pct
from metrics
