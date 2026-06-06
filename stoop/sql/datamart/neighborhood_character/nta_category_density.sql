create or replace table neighborhood_character_mart.nta_category_density as

with curated_counts as (
    select
        c.nta_id,
        c.nta_name,
        c.borough,
        b.area_sqkm,
        'curated' as source,
        c.category,
        sum(c.poi_count) as poi_count,
        count(distinct case when c.subcategory <> '__unknown__' then c.subcategory end) as subcategory_diversity,
        max(c.nyc_category_total) as nyc_category_total,
        coalesce(ctrl.min_nyc_category_total, 5) as min_nyc_category_total
    from neighborhood_character_mart.nta_curated_poi_counts c
    inner join neighborhood_character_mart.nta_boundaries b
        on c.nta_id = b.nta_id
    left join neighborhood_character_mart.nta_category_controls ctrl
        on c.category = ctrl.category
    group by
        c.nta_id,
        c.nta_name,
        c.borough,
        b.area_sqkm,
        c.category,
        coalesce(ctrl.min_nyc_category_total, 5)
),
public_counts as (
    select
        p.nta_id,
        p.nta_name,
        p.borough,
        b.area_sqkm,
        'public' as source,
        p.category,
        p.poi_count,
        cast(null as integer) as subcategory_diversity,
        sum(p.poi_count) over (partition by p.category) as nyc_category_total,
        1 as min_nyc_category_total
    from neighborhood_character_mart.nta_public_poi_counts p
    inner join neighborhood_character_mart.nta_boundaries b
        on p.nta_id = b.nta_id
),
combined as (
    select * from curated_counts
    union all
    select * from public_counts
),
ranked as (
    select
        *,
        percent_rank() over (
            partition by source, category
            order by poi_count, coalesce(subcategory_diversity, 0), nta_name
        ) as nyc_percentile
    from combined
)
select
    nta_id,
    nta_name,
    borough,
    area_sqkm,
    source,
    category,
    poi_count,
    case
        when area_sqkm is null or area_sqkm = 0 then null
        else poi_count / area_sqkm
    end as poi_density_per_sqkm,
    subcategory_diversity,
    nyc_category_total,
    nyc_percentile,
    case
        when nyc_category_total < min_nyc_category_total then null
        when nyc_percentile >= 0.90 then 'destination'
        when nyc_percentile >= 0.75 then 'strong'
        when nyc_percentile >= 0.50 then 'present'
        else 'limited'
    end as concentration_tier,
    nyc_category_total >= min_nyc_category_total as meets_evidence_threshold
from ranked;
