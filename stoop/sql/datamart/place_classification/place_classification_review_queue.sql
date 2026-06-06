create or replace table property_classification_mart.place_classification_review_queue as

with review_candidates as (

    select
        t.poi_id,
        t.name as place_name,
        t.current_category,
        t.current_subcategory,
        t.current_detail_level_3,
        r.recommended_category,
        r.recommended_subcategory,
        r.recommended_detail_level_3,
        coalesce(r.classification_confidence, 'needs_review') as classification_confidence,
        coalesce(r.classification_score, 0) as classification_score,
        coalesce(r.score_margin, 0) as score_margin,
        r.matched_keywords,
        t.classification_text_raw,
        concat_ws(
            '; ',
            case when t.current_subcategory = 'mixed_restaurants' then 'mixed_restaurants' end,
            case when r.poi_id is null then 'no_recommendation' end,
            case when coalesce(r.classification_confidence, 'needs_review') in ('low', 'needs_review') then 'low_confidence' end,
            case
                when r.poi_id is not null
                 and (
                    coalesce(r.recommended_category, '') <> coalesce(t.current_category, '')
                    or coalesce(r.recommended_subcategory, '') <> coalesce(t.current_subcategory, '')
                    or coalesce(r.recommended_detail_level_3, '') <> coalesce(t.current_detail_level_3, '')
                 ) then 'classification_change'
            end,
            case when r.poi_id is not null and coalesce(r.score_margin, 0) <= 2 then 'ambiguous_top_match' end
        ) as review_reason,
        'needs_review' as review_status,
        cast(null as varchar) as reviewed_category,
        cast(null as varchar) as reviewed_subcategory,
        cast(null as varchar) as reviewed_detail_level_3,
        cast(null as varchar) as review_notes,
        current_timestamp as created_at,
        cast(null as timestamp) as reviewed_at
    from property_classification_mart.place_classification_text t
    left join property_classification_mart.place_classification_recommendations r
        on t.poi_id = r.poi_id
    left join property_classification_mart.place_classification_overrides o
        on t.poi_id = o.poi_id
       and o.active_flag = true
    where t.current_category = 'restaurants'
      and o.poi_id is null

)

select *
from review_candidates
where review_reason is not null
  and trim(review_reason) <> '';
