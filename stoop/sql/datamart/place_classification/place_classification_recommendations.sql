create or replace table property_classification_mart.place_classification_recommendations as

with subcategory_scores as (

    select
        poi_id,
        place_name,
        mapped_category as candidate_category,
        mapped_subcategory as candidate_subcategory,
        sum(effective_weight)
            + case
                when count(distinct source_field) > 1 then count(distinct source_field) - 1
                else 0
              end
            + case
                when count(distinct keyword_id) > 1 then 1
                else 0
              end as classification_score,
        count(distinct keyword_id) as matched_keyword_count,
        min(priority) as highest_priority
    from property_classification_mart.place_keyword_matches
    where mapped_subcategory <> '__any__'
    group by
        poi_id,
        place_name,
        mapped_category,
        mapped_subcategory

),

ranked_subcategories as (

    select
        s.*,
        row_number() over (
            partition by poi_id
            order by classification_score desc, matched_keyword_count desc, highest_priority asc, candidate_subcategory asc
        ) as recommendation_rank,
        lead(classification_score) over (
            partition by poi_id
            order by classification_score desc, matched_keyword_count desc, highest_priority asc, candidate_subcategory asc
        ) as runner_up_score
    from subcategory_scores s

),

winning_subcategories as (

    select *
    from ranked_subcategories
    where recommendation_rank = 1

),

detail_scores as (

    select
        poi_id,
        mapped_subcategory,
        mapped_detail_level_3,
        sum(effective_weight) as detail_score,
        min(priority) as highest_priority
    from property_classification_mart.place_keyword_matches
    where mapped_detail_level_3 is not null
      and trim(mapped_detail_level_3) <> ''
    group by
        poi_id,
        mapped_subcategory,
        mapped_detail_level_3

),

ranked_details as (

    select
        w.poi_id,
        d.mapped_detail_level_3,
        row_number() over (
            partition by w.poi_id
            order by
                case when d.mapped_subcategory = w.candidate_subcategory then 0 else 1 end,
                d.detail_score desc,
                d.highest_priority asc,
                d.mapped_detail_level_3 asc
        ) as detail_rank
    from winning_subcategories w
    join detail_scores d
        on w.poi_id = d.poi_id
       and d.mapped_subcategory in (w.candidate_subcategory, '__any__')

),

matched_keyword_rollup as (

    select
        w.poi_id,
        string_agg(distinct m.keyword, ', ' order by m.keyword) as matched_keywords
    from winning_subcategories w
    join property_classification_mart.place_keyword_matches m
        on w.poi_id = m.poi_id
       and m.mapped_subcategory in (w.candidate_subcategory, '__any__')
    group by w.poi_id

)

select
    w.poi_id,
    w.place_name,
    t.current_category,
    t.current_subcategory,
    t.current_detail_level_3,
    w.candidate_category as recommended_category,
    w.candidate_subcategory as recommended_subcategory,
    rd.mapped_detail_level_3 as recommended_detail_level_3,
    w.classification_score,
    w.runner_up_score,
    w.classification_score - coalesce(w.runner_up_score, 0) as score_margin,
    w.matched_keyword_count,
    mr.matched_keywords,
    case
        when w.classification_score >= 16 and w.matched_keyword_count >= 2 and coalesce(w.runner_up_score, 0) <= w.classification_score - 4 then 'high'
        when w.classification_score >= 10 and coalesce(w.runner_up_score, 0) <= w.classification_score - 2 then 'medium'
        when w.classification_score > 0 then 'low'
        else 'needs_review'
    end as classification_confidence,
    w.recommendation_rank,
    current_timestamp as created_at
from winning_subcategories w
join property_classification_mart.place_classification_text t
    on w.poi_id = t.poi_id
left join ranked_details rd
    on w.poi_id = rd.poi_id
   and rd.detail_rank = 1
left join matched_keyword_rollup mr
    on w.poi_id = mr.poi_id;
