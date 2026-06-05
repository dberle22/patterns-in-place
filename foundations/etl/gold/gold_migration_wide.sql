-- Gold migration mart
-- Grain: one row per geo_level + geo_id + year
-- Combines ACS mobility / nativity metrics with IRS migration summary metrics
-- where the IRS summary contract exists (county, cbsa, state).

create or replace table patterns_in_place.gold.migration_wide as
with migration as (
    -- ACS remains the backbone of the table because it covers the full
    -- geography ladder used elsewhere in the Gold layer.
    select
        lower(geo_level) as geo_level,
        geo_id,
        geo_name,
        year,
        mig_total,
        mig_same_house,
        mig_moved_same_cnty,
        mig_moved_same_st,
        mig_moved_diff_st,
        mig_moved_abroad,
        pct_same_house,
        pct_moved_same_cnty,
        pct_moved_same_st,
        pct_moved_diff_st,
        pct_moved_abroad,
        pop_nativity_total,
        pop_native,
        pop_foreign_born,
        pop_foreign_born_citizen,
        pop_foreign_born_noncitizen,
        pct_native,
        pct_foreign_born,
        pct_non_citizen
    from patterns_in_place.silver.migration_kpi
),

irs_summary as (
    -- IRS summary exists only for county, cbsa, and state rows.
    -- Keep it at the same lowercase geo_level + geo_id + year contract
    -- so it can be joined cleanly into the ACS-backed mart.
    select
        lower(geo_level) as geo_level,
        geo_id,
        year,
        inflow_returns,
        outflow_returns,
        net_returns,
        inflow_agi,
        outflow_agi,
        net_agi
    from patterns_in_place.silver.irs_migration_summary
)

select
    m.geo_level,
    m.geo_id,
    m.geo_name,
    m.year,
    m.mig_total,
    m.mig_same_house,
    m.mig_moved_same_cnty,
    m.mig_moved_same_st,
    m.mig_moved_diff_st,
    m.mig_moved_abroad,
    m.pct_same_house,
    m.pct_moved_same_cnty,
    m.pct_moved_same_st,
    m.pct_moved_diff_st,
    m.pct_moved_abroad,
    case
        when m.pct_same_house is not null then 1.0 - m.pct_same_house
        else null
    end as mobility_rate,
    coalesce(m.pct_moved_same_cnty, 0)
        + coalesce(m.pct_moved_same_st, 0)
        + coalesce(m.pct_moved_diff_st, 0) as pct_moved_domestic,
    coalesce(m.pct_moved_same_cnty, 0)
        + coalesce(m.pct_moved_same_st, 0)
        + coalesce(m.pct_moved_diff_st, 0)
        + coalesce(m.pct_moved_abroad, 0) as migration_churn,
    coalesce(m.mig_moved_same_cnty, 0)
        + coalesce(m.mig_moved_same_st, 0)
        + coalesce(m.mig_moved_diff_st, 0)
        + coalesce(m.mig_moved_abroad, 0) as migration_churn_count,
    m.pop_nativity_total,
    m.pop_native,
    m.pop_foreign_born,
    m.pop_foreign_born_citizen,
    m.pop_foreign_born_noncitizen,
    m.pct_native,
    m.pct_foreign_born,
    m.pct_non_citizen,
    case
        when m.pop_nativity_total > 0
            then m.pop_foreign_born_citizen / m.pop_nativity_total
        else null
    end as pct_foreign_born_citizen,
    case
        when m.pop_nativity_total > 0
            then m.pop_foreign_born_noncitizen / m.pop_nativity_total
        else null
    end as pct_foreign_born_noncitizen,
    -- IRS "total" fields are household-return counts from the IRS summary table.
    i.inflow_returns as irs_inflow_total,
    i.outflow_returns as irs_outflow_total,
    i.net_returns as irs_net_migration,
    -- Use ACS nativity total as the common population denominator so the rate
    -- is comparable across the geographies where IRS summary exists.
    case
        when m.pop_nativity_total > 0 and i.net_returns is not null
            then i.net_returns / m.pop_nativity_total
        else null
    end as irs_net_migration_rate,
    case
        when m.pop_nativity_total > 0
             and i.inflow_returns is not null
             and i.outflow_returns is not null
            then (i.inflow_returns + i.outflow_returns) / m.pop_nativity_total
        else null
    end as irs_migration_churn,
    -- AGI columns add the income profile of movers, which ACS does not provide.
    i.inflow_agi as irs_inflow_agi,
    i.outflow_agi as irs_outflow_agi,
    i.net_agi as irs_net_agi
from migration m
left join irs_summary i
    on m.geo_level = i.geo_level
   and m.geo_id = i.geo_id
   and m.year = i.year
;
