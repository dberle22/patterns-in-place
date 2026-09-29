"""Build Q3's analysis-owned growth-location mart from governed Geography edges."""

from __future__ import annotations

import os
from pathlib import Path

import duckdb


METHOD_VERSION = "q3_growth_location_v1"
YEARS = (2014, 2019, 2021, 2023, 2024)


def db_path() -> str:
    """Use the configured warehouse, with the repository database as fallback."""
    root = Path(__file__).resolve().parents[4]
    return os.environ.get("DB_PATH", "") or str(
        root / "foundations/etl/data/duckdb/patterns_in_place.duckdb"
    )


def build(con: duckdb.DuckDBPyConnection) -> None:
    """Materialize Q3 outputs without adding ACS measures to mart_geography."""
    con.execute("create schema if not exists mart_explanation_q3")

    # Edge rows retain every historical crosswalk input. The target panel below
    # is convenient for analysis, but this surface is the audit record.
    con.execute("""
        create or replace table mart_explanation_q3.tract_harmonization_edges as
        with historical as (
          select h.year as data_year, 'population' as metric, h.geo_id as source_tract_geoid,
                 e.to_geo_id as target_tract_geoid, 2010 as source_boundary_vintage,
                 e.to_boundary_vintage as target_boundary_vintage, e.weight_basis, e.weight,
                 e.change_type, e.quality_flag, e.source_denominator, e.target_numerator,
                 e.allocated_weight_sum, h.pop_total as source_value, h.pop_total * e.weight as allocated_value,
                 e.source as crosswalk_source
          from gold.housing_core_wide h join mart_geography.temporal_edges e
            on h.geo_id = e.from_geo_id and e.weight_basis = 'population'
          where lower(h.geo_level) = 'tract' and h.year in (2014, 2019) and h.pop_total is not null
          union all
          select h.year, 'housing_units', h.geo_id, e.to_geo_id, 2010, e.to_boundary_vintage,
                 e.weight_basis, e.weight, e.change_type, e.quality_flag, e.source_denominator,
                 e.target_numerator, e.allocated_weight_sum, h.hu_total, h.hu_total * e.weight, e.source
          from gold.housing_core_wide h join mart_geography.temporal_edges e
            on h.geo_id = e.from_geo_id and e.weight_basis = 'housing_units'
          where lower(h.geo_level) = 'tract' and h.year in (2014, 2019) and h.hu_total is not null
        ), direct as (
          select year, 'population', geo_id, geo_id, 2020, 2020, 'population', 1.0,
                 'unchanged', 'complete', pop_total, pop_total, 1.0, pop_total, pop_total,
                 'ACS_5_YEAR_2020_TRACT_IDENTITY'
          from gold.housing_core_wide where lower(geo_level) = 'tract' and year in (2021, 2023, 2024) and pop_total is not null
          union all
          select year, 'housing_units', geo_id, geo_id, 2020, 2020, 'housing_units', 1.0,
                 'unchanged', 'complete', hu_total, hu_total, 1.0, hu_total, hu_total,
                 'ACS_5_YEAR_2020_TRACT_IDENTITY'
          from gold.housing_core_wide where lower(geo_level) = 'tract' and year in (2021, 2023, 2024) and hu_total is not null
        ) select * from historical union all select * from direct
    """)

    con.execute("""
        create or replace table mart_explanation_q3.tract_panel_2020 as
        with endpoint as (
          select distinct geo_id as tract_geoid from gold.housing_core_wide
          where lower(geo_level) = 'tract' and year = 2024
        ), years as (select unnest([2014, 2019, 2021, 2023, 2024]) as data_year),
        metric as (
          select data_year, target_tract_geoid as tract_geoid, metric, sum(allocated_value) as value,
                 max(case when quality_flag in ('partial', 'undefined') then 1 else 0 end) as incomplete,
                 max(case when change_type in ('split', 'redrawn') then 1 else 0 end) as boundary_change
          from mart_explanation_q3.tract_harmonization_edges group by 1,2,3
        )
        select years.data_year, endpoint.tract_geoid,
               max(case when metric.metric = 'population' then metric.value end) as population,
               max(case when metric.metric = 'housing_units' then metric.value end) as housing_units,
               coalesce(max(metric.incomplete), 1) = 1 as low_confidence_flag,
               coalesce(max(metric.boundary_change), 0) = 1 as boundary_change_flag,
               case when count(metric.metric) = 0 then 'insufficient_coverage'
                    when max(metric.incomplete) = 1 then 'partial_allocation' else 'complete' end as harmonization_status,
               'q3_growth_location_v1' as method_version
        from endpoint cross join years left join metric using (data_year, tract_geoid)
        group by 1,2
    """)

    con.execute("""
        create or replace table mart_explanation_q3.tract_harmonization_qa as
        with source as (
          select data_year, metric, source_tract_geoid, max(source_value) as source_value,
                 sum(allocated_value) as allocated_value,
                 max(allocated_weight_sum) as allocated_weight_sum,
                 max(case when quality_flag in ('partial', 'undefined') then 1 else 0 end) as low_confidence,
                 max(case when change_type in ('split', 'redrawn') then 1 else 0 end) as boundary_change
          from mart_explanation_q3.tract_harmonization_edges group by 1,2,3
        )
        select data_year, metric, count(*) as source_tract_count, sum(source_value) as source_total,
               sum(allocated_value) as allocated_total, sum(source_value) - sum(allocated_value) as allocation_error,
               (sum(source_value) - sum(allocated_value)) / nullif(sum(source_value), 0) as allocation_error_share,
               count(case when low_confidence = 1 then 1 end) as low_confidence_source_tract_count,
               count(case when boundary_change = 1 then 1 end) as boundary_changed_source_tract_count,
               'q3_growth_location_v1' as method_version
        from source group by 1,2
    """)

    con.execute("""
        create or replace table mart_explanation_q3.tract_growth_horizons as
        with horizons as (
          select * from (values (1, 2023, 'watchlist_signal'), (3, 2021, 'watchlist_signal'),
                                (5, 2019, 'interpretive_core'), (10, 2014, 'interpretive_core'))
          as t(horizon_years, start_year, evidence_role)
        )
        select h.horizon_years, h.start_year, 2024 as end_year, h.evidence_role, s.tract_geoid,
               s.population as population_start, e.population as population_end,
               e.population - s.population as population_change,
               (e.population - s.population) / nullif(s.population, 0) as population_pct_change,
               s.housing_units as housing_units_start, e.housing_units as housing_units_end,
               e.housing_units - s.housing_units as housing_units_change,
               (e.housing_units - s.housing_units) / nullif(s.housing_units, 0) as housing_units_pct_change,
               s.low_confidence_flag or e.low_confidence_flag as low_confidence_flag,
               case when s.low_confidence_flag or e.low_confidence_flag then 'insufficient_confidence_or_coverage'
                    else 'usable_with_declared_horizon_posture' end as comparison_status,
               'ACS_5_YEAR_RELEASES_OVERLAP;_1_AND_3_YEAR_ARE_DESCRIPTIVE_NOT_INDEPENDENT_ANNUAL_GROWTH' as release_overlap_note,
               'q3_growth_location_v1' as method_version
        from horizons h join mart_explanation_q3.tract_panel_2020 s on s.data_year = h.start_year
        join mart_explanation_q3.tract_panel_2020 e on e.data_year = 2024 and e.tract_geoid = s.tract_geoid
    """)

    # The ledger uses exact tract-to-CBSA membership and includes unusable rows
    # separately, so metros never silently gain coverage by exclusion.
    con.execute("""
        create or replace table mart_explanation_q3.metro_growth_ledger as
        select r.cbsa_code, h.horizon_years, h.start_year, h.end_year, h.evidence_role,
               count(*) as tract_count, count(case when h.comparison_status like 'usable%' then 1 end) as usable_tract_count,
               sum(case when h.comparison_status like 'usable%' then h.population_change end) as usable_population_change,
               sum(case when h.comparison_status like 'usable%' then h.housing_units_change end) as usable_housing_units_change,
               count(case when h.comparison_status not like 'usable%' then 1 end) as insufficient_confidence_tract_count,
               'q3_growth_location_v1' as method_version
        from mart_explanation_q3.tract_growth_horizons h join mart_geography.rollup_tract_to_cbsa r using (tract_geoid)
        group by 1,2,3,4,5
    """)

    con.execute("""
        create or replace table mart_explanation_q3.tract_growth_status as
        select h.*, r.cbsa_code,
               case when h.comparison_status not like 'usable%' then 'insufficient_confidence_or_coverage'
                    when h.population_change > 0 then 'gain' when h.population_change < 0 then 'loss'
                    else 'no_material_change' end as population_status,
               case when h.comparison_status not like 'usable%' then 'insufficient_confidence_or_coverage'
                    when h.housing_units_change > 0 then 'gain' when h.housing_units_change < 0 then 'loss'
                    else 'no_material_change' end as housing_units_status,
               'zero_change_only_pending_epic_5_sensitivity' as materiality_rule
        from mart_explanation_q3.tract_growth_horizons h join mart_geography.rollup_tract_to_cbsa r using (tract_geoid)
    """)

    con.execute("""
        create or replace table mart_explanation_q3.growth_concentration as
        with long as (
          select cbsa_code, horizon_years, 'population' as measure, tract_geoid, population_change as change_value
          from mart_explanation_q3.tract_growth_status where comparison_status like 'usable%'
          union all select cbsa_code, horizon_years, 'housing_units', tract_geoid, housing_units_change
          from mart_explanation_q3.tract_growth_status where comparison_status like 'usable%'
        ), positive as (
          select *, row_number() over w as tract_rank, sum(change_value) over w as cumulative_change,
                 sum(change_value) over (partition by cbsa_code, horizon_years, measure) as positive_change_total,
                 count(*) over (partition by cbsa_code, horizon_years, measure) as positive_tract_count
          from long where change_value > 0
          window w as (partition by cbsa_code, horizon_years, measure order by change_value desc, tract_geoid rows unbounded preceding)
        )
        select *, cumulative_change / nullif(positive_change_total, 0) as cumulative_positive_change_share,
               tract_rank::double / positive_tract_count as cumulative_positive_tract_share
        from positive
    """)

    # County and Place lenses remain direct native-grain ACS values. Place rows
    # gain membership labels but are never summed into the metro ledger.
    con.execute("""
        create or replace table mart_explanation_q3.county_growth_horizons as
        with h as (select * from (values (1,2023,'watchlist_signal'),(3,2021,'watchlist_signal'),(5,2019,'interpretive_core'),(10,2014,'interpretive_core')) t(horizon_years,start_year,evidence_role))
        select r.cbsa_code, h.horizon_years, h.start_year, 2024 as end_year, h.evidence_role, e.geo_id as county_geoid, e.geo_name as county_name,
               e.pop_total-s.pop_total as population_change, (e.pop_total-s.pop_total)/nullif(s.pop_total,0) as population_pct_change,
               e.hu_total-s.hu_total as housing_units_change, (e.hu_total-s.hu_total)/nullif(s.hu_total,0) as housing_units_pct_change,
               e.permits_total_units as permits_total_units_2024,
               'direct_county_acs' as observation_type, 'q3_growth_location_v1' as method_version
        from h join gold.housing_core_wide e on lower(e.geo_level)='county' and e.year=2024
        join gold.housing_core_wide s on lower(s.geo_level)='county' and s.geo_id=e.geo_id and s.year=h.start_year
        join mart_geography.rollup_county_to_cbsa r on r.county_geoid=e.geo_id
    """)

    con.execute("""
        create or replace table mart_explanation_q3.place_growth_horizons as
        with h as (select * from (values (1,2023,'watchlist_signal'),(3,2021,'watchlist_signal'),(5,2019,'interpretive_core'),(10,2014,'interpretive_core')) t(horizon_years,start_year,evidence_role)),
        membership as (select * from mart_geography.place_to_cbsa_membership where weight_basis='population')
        select membership.target_geo_id as cbsa_code, h.horizon_years, h.start_year, 2024 as end_year, h.evidence_role,
               e.geo_id as place_geoid, e.geo_name as place_name, e.pop_total-s.pop_total as population_change,
               e.hu_total-s.hu_total as housing_units_change, e.permits_total_units as permits_total_units_2024, membership.membership_status,
               primary_association.association_status, membership.is_primary_cbsa,
               case when primary_association.association_status='whole_cbsa_membership' then 'whole_place_direct_value_allowed'
                    else 'split_or_partial_place_requires_allocation_or_caveat' end as direct_measure_use,
               'direct_place_acs_not_metro_additive' as observation_type, 'q3_growth_location_v1' as method_version
        from h join gold.housing_core_wide e on lower(e.geo_level)='place' and e.year=2024
        join gold.housing_core_wide s on lower(s.geo_level)='place' and s.geo_id=e.geo_id and s.year=h.start_year
        join membership on membership.place_geoid=e.geo_id
        join mart_geography.place_primary_cbsa_association primary_association using (place_geoid)
    """)

    con.execute("""
        create or replace table mart_explanation_q3.national_growth_coverage as
        select horizon_years, evidence_role, measure, count(*) as cbsa_count,
               avg(usable_tract_count::double/nullif(tract_count,0)) as mean_usable_tract_share
        from (select horizon_years,evidence_role,cbsa_code,'population' as measure,tract_count,usable_tract_count from mart_explanation_q3.metro_growth_ledger
              union all select horizon_years,evidence_role,cbsa_code,'housing_units',tract_count,usable_tract_count from mart_explanation_q3.metro_growth_ledger)
        group by 1,2,3
    """)


if __name__ == "__main__":
    with duckdb.connect(db_path()) as connection:
        build(connection)
    print("Built mart_explanation_q3 growth-location surfaces.")
