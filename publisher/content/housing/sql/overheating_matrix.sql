-- Housing overheating feature mart.
-- This table keeps the raw signals, the directional standardization fields, and
-- a provisional composite so we can QA rankings without locking the section
-- into one irreversible heuristic too early.
--
-- Design choices:
-- - Multi-year surface where the housing-market inputs exist.
-- - `2024` remains the main editorial snapshot year.
-- - Scoring universes are separated by `geo_level + year` so CBSAs and counties
--   are never ranked against each other.
-- - Missing ZORI is allowed; component and composite scores average only over
--   the metrics that are actually present for a row.
-- - Higher component and composite scores mean "more overheating pressure."

create schema if not exists mart_housing;

create or replace table mart_housing.overheating_matrix as
with base as (
    select
        c.geo_level,
        c.geo_id,
        c.geo_name,
        c.display_name,
        c.year,
        c.region_id,
        c.region_name,
        c.division_id,
        c.division_name,
        c.state_fips,
        c.state_name,
        c.state_abbr,
        c.cbsa_code,
        c.cbsa_name,
        c.parent_geo_level,
        c.parent_geo_id,
        c.pop_total,
        c.major_cbsa_100k_flag,
        c.major_cbsa_250k_flag,
        case
            when c.vacancy_rate is not null and not isnan(c.vacancy_rate) and not isinf(c.vacancy_rate) then c.vacancy_rate
            else null
        end as vacancy_rate,
        case
            when c.pct_rent_burden_30plus is not null and not isnan(c.pct_rent_burden_30plus) and not isinf(c.pct_rent_burden_30plus) then c.pct_rent_burden_30plus
            else null
        end as pct_rent_burden_30plus,
        c.pct_rent_burden_50plus,
        case
            when c.permits_per_1000_housing_units is not null and not isnan(c.permits_per_1000_housing_units) and not isinf(c.permits_per_1000_housing_units) then c.permits_per_1000_housing_units
            else null
        end as permits_per_1000_housing_units,
        c.permits_per_1000_population,
        case
            when c.permits_share_multifam_units is not null and not isnan(c.permits_share_multifam_units) and not isinf(c.permits_share_multifam_units) then c.permits_share_multifam_units
            else null
        end as permits_share_multifam_units,
        c.permits_share_units_5_plus,
        c.permits_avg_units_per_bldg,
        c.pct_struct_multifam,
        c.median_gross_rent,
        c.annualized_median_rent,
        c.median_home_value,
        case
            when c.rent_to_income is not null and not isnan(c.rent_to_income) and not isinf(c.rent_to_income) then c.rent_to_income
            else null
        end as rent_to_income,
        case
            when c.value_to_income is not null and not isnan(c.value_to_income) and not isinf(c.value_to_income) then c.value_to_income
            else null
        end as value_to_income,
        c.median_hh_income,
        c.acs_income_pc,
        case
            when c.acs_income_pc_growth_1yr is not null and not isnan(c.acs_income_pc_growth_1yr) and not isinf(c.acs_income_pc_growth_1yr) then c.acs_income_pc_growth_1yr
            else null
        end as acs_income_pc_growth_1yr,
        case
            when c.acs_income_pc_growth_5yr is not null and not isnan(c.acs_income_pc_growth_5yr) and not isinf(c.acs_income_pc_growth_5yr) then c.acs_income_pc_growth_5yr
            else null
        end as acs_income_pc_growth_5yr,
        case
            when c.income_pc_growth_1yr is not null and not isnan(c.income_pc_growth_1yr) and not isinf(c.income_pc_growth_1yr) then c.income_pc_growth_1yr
            else null
        end as income_pc_growth_1yr,
        case
            when c.income_pc_growth_5yr is not null and not isnan(c.income_pc_growth_5yr) and not isinf(c.income_pc_growth_5yr) then c.income_pc_growth_5yr
            else null
        end as income_pc_growth_5yr,
        case
            when c.pop_growth_1yr is not null and not isnan(c.pop_growth_1yr) and not isinf(c.pop_growth_1yr) then c.pop_growth_1yr
            else null
        end as pop_growth_1yr,
        case
            when c.pop_growth_5yr is not null and not isnan(c.pop_growth_5yr) and not isinf(c.pop_growth_5yr) then c.pop_growth_5yr
            else null
        end as pop_growth_5yr,
        m.hpi_level,
        case
            when m.hpi_yoy_pct is not null and not isnan(m.hpi_yoy_pct) and not isinf(m.hpi_yoy_pct) then m.hpi_yoy_pct
            else null
        end as hpi_yoy_pct,
        case
            when m.hpi_5yr_pct is not null and not isnan(m.hpi_5yr_pct) and not isinf(m.hpi_5yr_pct) then m.hpi_5yr_pct
            else null
        end as hpi_5yr_pct,
        m.hpi_10yr_pct,
        m.zhvi_annual_avg,
        m.zhvi_december,
        m.zhvi_annual_avg_yoy_pct,
        m.zhvi_december_yoy_pct,
        m.zori_annual_avg,
        m.zori_december,
        case
            when m.zori_annual_avg_yoy_pct is not null and not isnan(m.zori_annual_avg_yoy_pct) and not isinf(m.zori_annual_avg_yoy_pct) then m.zori_annual_avg_yoy_pct
            else null
        end as zori_annual_avg_yoy_pct,
        m.zori_december_yoy_pct
    from mart_housing.core_metrics c
    inner join gold.housing_market_wide m
        on c.geo_level = m.geo_level
       and c.geo_id = m.geo_id
       and c.year = m.year
    where c.geo_level in ('cbsa', 'county')
),

ranked as (
    select
        b.*,

        -- Momentum: higher price and rent acceleration means more overheating.
        cume_dist() over (
            partition by b.geo_level, b.year
            order by b.hpi_yoy_pct
        ) as hpi_yoy_pct_pctile,
        cume_dist() over (
            partition by b.geo_level, b.year
            order by b.hpi_5yr_pct
        ) as hpi_5yr_pct_pctile,
        cume_dist() over (
            partition by b.geo_level, b.year
            order by b.zori_annual_avg_yoy_pct
        ) as zori_annual_avg_yoy_pct_pctile,

        -- Growth pressure: higher population and ACS income growth raise demand pressure.
        cume_dist() over (
            partition by b.geo_level, b.year
            order by b.acs_income_pc_growth_1yr
        ) as acs_income_pc_growth_1yr_pctile,
        cume_dist() over (
            partition by b.geo_level, b.year
            order by b.acs_income_pc_growth_5yr
        ) as acs_income_pc_growth_5yr_pctile,
        cume_dist() over (
            partition by b.geo_level, b.year
            order by b.pop_growth_1yr
        ) as pop_growth_1yr_pctile,
        cume_dist() over (
            partition by b.geo_level, b.year
            order by b.pop_growth_5yr
        ) as pop_growth_5yr_pctile,

        -- Affordability strain: higher burden and higher price-to-income ratios mean more overheating.
        cume_dist() over (
            partition by b.geo_level, b.year
            order by b.rent_to_income
        ) as rent_to_income_pctile,
        cume_dist() over (
            partition by b.geo_level, b.year
            order by b.value_to_income
        ) as value_to_income_pctile,
        cume_dist() over (
            partition by b.geo_level, b.year
            order by b.pct_rent_burden_30plus
        ) as pct_rent_burden_30plus_pctile,

        -- Tightness and supply: lower vacancy and lower permit response mean more overheating.
        cume_dist() over (
            partition by b.geo_level, b.year
            order by b.vacancy_rate desc
        ) as vacancy_rate_inverse_pctile,
        cume_dist() over (
            partition by b.geo_level, b.year
            order by b.permits_per_1000_housing_units desc
        ) as permits_per_1000_housing_units_inverse_pctile,
        cume_dist() over (
            partition by b.geo_level, b.year
            order by b.permits_share_multifam_units desc
        ) as permits_share_multifam_units_inverse_pctile,

        -- Direction-aware z-scores keep a second normalization surface for QA.
        case
            when stddev_pop(b.hpi_yoy_pct) over (partition by b.geo_level, b.year) > 0 then
                (b.hpi_yoy_pct - avg(b.hpi_yoy_pct) over (partition by b.geo_level, b.year))
                / stddev_pop(b.hpi_yoy_pct) over (partition by b.geo_level, b.year)
            else null
        end as hpi_yoy_pct_zscore,
        case
            when stddev_pop(b.hpi_5yr_pct) over (partition by b.geo_level, b.year) > 0 then
                (b.hpi_5yr_pct - avg(b.hpi_5yr_pct) over (partition by b.geo_level, b.year))
                / stddev_pop(b.hpi_5yr_pct) over (partition by b.geo_level, b.year)
            else null
        end as hpi_5yr_pct_zscore,
        case
            when stddev_pop(b.zori_annual_avg_yoy_pct) over (partition by b.geo_level, b.year) > 0 then
                (b.zori_annual_avg_yoy_pct - avg(b.zori_annual_avg_yoy_pct) over (partition by b.geo_level, b.year))
                / stddev_pop(b.zori_annual_avg_yoy_pct) over (partition by b.geo_level, b.year)
            else null
        end as zori_annual_avg_yoy_pct_zscore,
        case
            when stddev_pop(b.acs_income_pc_growth_1yr) over (partition by b.geo_level, b.year) > 0 then
                (b.acs_income_pc_growth_1yr - avg(b.acs_income_pc_growth_1yr) over (partition by b.geo_level, b.year))
                / stddev_pop(b.acs_income_pc_growth_1yr) over (partition by b.geo_level, b.year)
            else null
        end as acs_income_pc_growth_1yr_zscore,
        case
            when stddev_pop(b.acs_income_pc_growth_5yr) over (partition by b.geo_level, b.year) > 0 then
                (b.acs_income_pc_growth_5yr - avg(b.acs_income_pc_growth_5yr) over (partition by b.geo_level, b.year))
                / stddev_pop(b.acs_income_pc_growth_5yr) over (partition by b.geo_level, b.year)
            else null
        end as acs_income_pc_growth_5yr_zscore,
        case
            when stddev_pop(b.pop_growth_1yr) over (partition by b.geo_level, b.year) > 0 then
                (b.pop_growth_1yr - avg(b.pop_growth_1yr) over (partition by b.geo_level, b.year))
                / stddev_pop(b.pop_growth_1yr) over (partition by b.geo_level, b.year)
            else null
        end as pop_growth_1yr_zscore,
        case
            when stddev_pop(b.pop_growth_5yr) over (partition by b.geo_level, b.year) > 0 then
                (b.pop_growth_5yr - avg(b.pop_growth_5yr) over (partition by b.geo_level, b.year))
                / stddev_pop(b.pop_growth_5yr) over (partition by b.geo_level, b.year)
            else null
        end as pop_growth_5yr_zscore,
        case
            when stddev_pop(b.rent_to_income) over (partition by b.geo_level, b.year) > 0 then
                (b.rent_to_income - avg(b.rent_to_income) over (partition by b.geo_level, b.year))
                / stddev_pop(b.rent_to_income) over (partition by b.geo_level, b.year)
            else null
        end as rent_to_income_zscore,
        case
            when stddev_pop(b.value_to_income) over (partition by b.geo_level, b.year) > 0 then
                (b.value_to_income - avg(b.value_to_income) over (partition by b.geo_level, b.year))
                / stddev_pop(b.value_to_income) over (partition by b.geo_level, b.year)
            else null
        end as value_to_income_zscore,
        case
            when stddev_pop(b.pct_rent_burden_30plus) over (partition by b.geo_level, b.year) > 0 then
                (b.pct_rent_burden_30plus - avg(b.pct_rent_burden_30plus) over (partition by b.geo_level, b.year))
                / stddev_pop(b.pct_rent_burden_30plus) over (partition by b.geo_level, b.year)
            else null
        end as pct_rent_burden_30plus_zscore,
        case
            when stddev_pop(b.vacancy_rate) over (partition by b.geo_level, b.year) > 0 then
                -1.0 * (b.vacancy_rate - avg(b.vacancy_rate) over (partition by b.geo_level, b.year))
                / stddev_pop(b.vacancy_rate) over (partition by b.geo_level, b.year)
            else null
        end as vacancy_rate_inverse_zscore,
        case
            when stddev_pop(b.permits_per_1000_housing_units) over (partition by b.geo_level, b.year) > 0 then
                -1.0 * (b.permits_per_1000_housing_units - avg(b.permits_per_1000_housing_units) over (partition by b.geo_level, b.year))
                / stddev_pop(b.permits_per_1000_housing_units) over (partition by b.geo_level, b.year)
            else null
        end as permits_per_1000_housing_units_inverse_zscore,
        case
            when stddev_pop(b.permits_share_multifam_units) over (partition by b.geo_level, b.year) > 0 then
                -1.0 * (b.permits_share_multifam_units - avg(b.permits_share_multifam_units) over (partition by b.geo_level, b.year))
                / stddev_pop(b.permits_share_multifam_units) over (partition by b.geo_level, b.year)
            else null
        end as permits_share_multifam_units_inverse_zscore
    from base b
),

scored as (
    select
        r.*,

        -- Count how much evidence each component is using so downstream work
        -- can decide whether a row is robust enough for ranking or labeling.
        (
            case when r.hpi_yoy_pct_pctile is not null then 1 else 0 end
            + case when r.hpi_5yr_pct_pctile is not null then 1 else 0 end
            + case when r.zori_annual_avg_yoy_pct_pctile is not null then 1 else 0 end
        ) as momentum_metric_count,
        (
            case when r.acs_income_pc_growth_1yr_pctile is not null then 1 else 0 end
            + case when r.acs_income_pc_growth_5yr_pctile is not null then 1 else 0 end
            + case when r.pop_growth_1yr_pctile is not null then 1 else 0 end
            + case when r.pop_growth_5yr_pctile is not null then 1 else 0 end
        ) as pressure_metric_count,
        (
            case when r.rent_to_income_pctile is not null then 1 else 0 end
            + case when r.value_to_income_pctile is not null then 1 else 0 end
            + case when r.pct_rent_burden_30plus_pctile is not null then 1 else 0 end
        ) as strain_metric_count,
        (
            case when r.vacancy_rate_inverse_pctile is not null then 1 else 0 end
            + case when r.permits_per_1000_housing_units_inverse_pctile is not null then 1 else 0 end
            + case when r.permits_share_multifam_units_inverse_pctile is not null then 1 else 0 end
        ) as tightness_metric_count,

        (
            coalesce(r.hpi_yoy_pct_pctile, 0.0)
            + coalesce(r.hpi_5yr_pct_pctile, 0.0)
            + coalesce(r.zori_annual_avg_yoy_pct_pctile, 0.0)
        )
        / nullif(
            (case when r.hpi_yoy_pct_pctile is not null then 1 else 0 end)
            + (case when r.hpi_5yr_pct_pctile is not null then 1 else 0 end)
            + (case when r.zori_annual_avg_yoy_pct_pctile is not null then 1 else 0 end),
            0
        ) as momentum_component_score,

        (
            coalesce(r.acs_income_pc_growth_1yr_pctile, 0.0)
            + coalesce(r.acs_income_pc_growth_5yr_pctile, 0.0)
            + coalesce(r.pop_growth_1yr_pctile, 0.0)
            + coalesce(r.pop_growth_5yr_pctile, 0.0)
        )
        / nullif(
            (case when r.acs_income_pc_growth_1yr_pctile is not null then 1 else 0 end)
            + (case when r.acs_income_pc_growth_5yr_pctile is not null then 1 else 0 end)
            + (case when r.pop_growth_1yr_pctile is not null then 1 else 0 end)
            + (case when r.pop_growth_5yr_pctile is not null then 1 else 0 end),
            0
        ) as pressure_component_score,

        (
            coalesce(r.rent_to_income_pctile, 0.0)
            + coalesce(r.value_to_income_pctile, 0.0)
            + coalesce(r.pct_rent_burden_30plus_pctile, 0.0)
        )
        / nullif(
            (case when r.rent_to_income_pctile is not null then 1 else 0 end)
            + (case when r.value_to_income_pctile is not null then 1 else 0 end)
            + (case when r.pct_rent_burden_30plus_pctile is not null then 1 else 0 end),
            0
        ) as strain_component_score,

        (
            coalesce(r.vacancy_rate_inverse_pctile, 0.0)
            + coalesce(r.permits_per_1000_housing_units_inverse_pctile, 0.0)
            + coalesce(r.permits_share_multifam_units_inverse_pctile, 0.0)
        )
        / nullif(
            (case when r.vacancy_rate_inverse_pctile is not null then 1 else 0 end)
            + (case when r.permits_per_1000_housing_units_inverse_pctile is not null then 1 else 0 end)
            + (case when r.permits_share_multifam_units_inverse_pctile is not null then 1 else 0 end),
            0
        ) as tightness_component_score
    from ranked r
),

final as (
    select
        s.*,
        (
            case when s.momentum_component_score is not null then 1 else 0 end
            + case when s.pressure_component_score is not null then 1 else 0 end
            + case when s.strain_component_score is not null then 1 else 0 end
            + case when s.tightness_component_score is not null then 1 else 0 end
        ) as component_count,
        (
            coalesce(s.momentum_component_score, 0.0)
            + coalesce(s.pressure_component_score, 0.0)
            + coalesce(s.strain_component_score, 0.0)
            + coalesce(s.tightness_component_score, 0.0)
        )
        / nullif(
            (case when s.momentum_component_score is not null then 1 else 0 end)
            + (case when s.pressure_component_score is not null then 1 else 0 end)
            + (case when s.strain_component_score is not null then 1 else 0 end)
            + (case when s.tightness_component_score is not null then 1 else 0 end),
            0
        ) as provisional_overheating_score
    from scored s
)

select
    *,
    cume_dist() over (
        partition by geo_level, year
        order by provisional_overheating_score
    ) as provisional_overheating_score_pctile,
    row_number() over (
        partition by geo_level, year
        order by provisional_overheating_score desc, pop_total desc, geo_name
    ) as provisional_overheating_rank,
    year = 2024 as reference_year_flag
from final;
