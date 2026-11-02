--- IRS migration direction check
--- Run after irs_migration_silver.R and gold_migration_wide.sql.
--- Returns one row of results when every check passes; raises an error (and so
--- stops a scripted build) if the IRS flows have been stored backwards.
---
--- Why this exists: until 2026-10 the staging script read origin from the IRS
--- y2_ columns and destination from y1_, which swapped every inflow and outflow
--- and flipped the sign of every net value. Each check below is a fact about
--- direction that a reversal would break. See
--- foundations/etl/IRS_MIGRATION_DIRECTION_FIX_SPEC.md.

with ny_state as (
    -- New York State has lost people to other states in every recent year.
    -- A reversed table shows it gaining them instead.
    select
        count(*) as years_checked,
        count(*) filter (where net_exemptions >= 0) as years_not_negative
    from patterns_in_place.silver.irs_migration_summary
    where geo_level = 'state'
      and geo_id = '36'
      and year between 2020 and 2022
),

manhattan_miami as (
    -- Manhattan -> Miami-Dade is the larger of the two flows (2,676 vs 1,100
    -- people in 2022, read the same way from the IRS inflow and outflow files).
    select
        max(n_exemptions) filter (where origin_geo_id = '36061' and dest_geo_id = '12086') as ny_to_miami,
        max(n_exemptions) filter (where origin_geo_id = '12086' and dest_geo_id = '36061') as miami_to_ny
    from patterns_in_place.silver.irs_migration_flows
    where geo_level = 'county'
      and year = 2022
),

gold_ny as (
    -- Gold must carry the same sign as Silver, since the Intelligence
    -- Framework and the marts read irs_net_migration_rate from here.
    select
        max(irs_net_migration) as irs_net_migration_2022
    from patterns_in_place.gold.migration_wide
    where geo_level = 'state'
      and geo_id = '36'
      and year = 2022
)

select
    n.years_checked,
    n.years_not_negative,
    m.ny_to_miami,
    m.miami_to_ny,
    g.irs_net_migration_2022,
    -- error() aborts the query, so any failure stops the build loudly.
    case
        when n.years_checked <> 3
            then error('IRS direction check: expected 3 NY State years (2020-22) in silver.irs_migration_summary')
        when n.years_not_negative > 0
            then error('IRS direction check: NY State net interstate migration is not negative; flows look reversed')
        when m.ny_to_miami is null or m.miami_to_ny is null
            then error('IRS direction check: Manhattan / Miami-Dade 2022 flows missing from silver.irs_migration_flows')
        when m.ny_to_miami <= m.miami_to_ny
            then error('IRS direction check: Miami-Dade -> Manhattan exceeds Manhattan -> Miami-Dade; flows look reversed')
        when g.irs_net_migration_2022 is null or g.irs_net_migration_2022 >= 0
            then error('IRS direction check: gold.migration_wide NY State irs_net_migration is not negative')
        else 'pass'
    end as check_status
from ny_state n
cross join manhattan_miami m
cross join gold_ny g
;
