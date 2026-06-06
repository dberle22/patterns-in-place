create or replace table neighborhood_character_mart.nta_character_profile as

with curated_totals as (
    select
        nta_id,
        sum(poi_count) as total_curated_poi_count
    from neighborhood_character_mart.nta_category_density
    where source = 'curated'
    group by nta_id
),
top_category as (
    select
        nta_id,
        category as top_category
    from (
        select
            nta_id,
            category,
            poi_count,
            subcategory_diversity,
            row_number() over (
                partition by nta_id
                order by poi_count desc, coalesce(subcategory_diversity, 0) desc, category asc
            ) as row_num
        from neighborhood_character_mart.nta_category_density
        where source = 'curated'
    )
    where row_num = 1
),
top_subcategory as (
    select
        ranked.nta_id,
        subcategory as top_subcategory
    from (
        select
            c.nta_id,
            c.subcategory,
            c.poi_count,
            row_number() over (
                partition by c.nta_id
                order by c.poi_count desc, c.subcategory asc
            ) as row_num
        from neighborhood_character_mart.nta_curated_poi_counts c
        inner join top_category tc
            on c.nta_id = tc.nta_id
           and c.category = tc.top_category
        where c.subcategory <> '__unknown__'
    ) ranked
    where row_num = 1
),
category_lists as (
    select
        d.nta_id,
        string_agg(
            case
                when d.concentration_tier = 'destination' and coalesce(c.known_for_enabled, false) then d.category
                else null
            end,
            '|' order by d.poi_count desc, d.category asc
        ) as destination_categories,
        string_agg(
            case
                when d.concentration_tier = 'strong' and coalesce(c.include_in_explore_v1, false) then d.category
                else null
            end,
            '|' order by d.poi_count desc, d.category asc
        ) as strong_categories
    from neighborhood_character_mart.nta_category_density d
    left join neighborhood_character_mart.nta_category_controls c
        on d.category = c.category
    where d.source = 'curated'
      and d.meets_evidence_threshold = true
    group by d.nta_id
),
public_rollup as (
    select
        nta_id,
        sum(case when category = 'subway_station' then poi_count else 0 end) as subway_station_count,
        sum(case when category = 'bus_stop' then poi_count else 0 end) as bus_stop_count,
        sum(case when category = 'grocery_store' then poi_count else 0 end) as grocery_store_count,
        sum(case when category = 'pharmacy' then poi_count else 0 end) as pharmacy_count,
        sum(case when category = 'park' then poi_count else 0 end) as park_count,
        sum(case when category = 'public_library' then poi_count else 0 end) as public_library_count,
        sum(case when category = 'public_school' then poi_count else 0 end) as public_school_count
    from neighborhood_character_mart.nta_public_poi_counts
    group by nta_id
)
select
    b.nta_id,
    b.nta_name,
    b.borough,
    b.area_sqkm,
    coalesce(ct.total_curated_poi_count, 0) as total_curated_poi_count,
    cl.destination_categories,
    cl.strong_categories,
    tc.top_category,
    ts.top_subcategory,
    coalesce(p.subway_station_count, 0) as subway_station_count,
    coalesce(p.bus_stop_count, 0) as bus_stop_count,
    coalesce(p.grocery_store_count, 0) as grocery_store_count,
    coalesce(p.pharmacy_count, 0) as pharmacy_count,
    coalesce(p.park_count, 0) as park_count,
    coalesce(p.public_library_count, 0) as public_library_count,
    coalesce(p.public_school_count, 0) as public_school_count,
    current_timestamp as built_at
from neighborhood_character_mart.nta_boundaries b
left join curated_totals ct
    on b.nta_id = ct.nta_id
left join category_lists cl
    on b.nta_id = cl.nta_id
left join top_category tc
    on b.nta_id = tc.nta_id
left join top_subcategory ts
    on b.nta_id = ts.nta_id
left join public_rollup p
    on b.nta_id = p.nta_id;
