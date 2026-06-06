create or replace table property_classification_mart.curated_places_classified as

select
    t.poi_id,
    t.name as place_name,
    t.current_category as original_category,
    t.current_subcategory as original_subcategory,
    t.current_detail_level_3 as original_detail_level_3,
    mk.matched_keywords,
    r.recommended_category,
    r.recommended_subcategory,
    r.recommended_detail_level_3,
    coalesce(
        o.override_category,
        case when t.current_subcategory = 'mixed_restaurants' then r.recommended_category end,
        t.current_category
    ) as final_category,
    coalesce(
        o.override_subcategory,
        case when t.current_subcategory = 'mixed_restaurants' then r.recommended_subcategory end,
        t.current_subcategory
    ) as final_subcategory,
    coalesce(
        o.override_detail_level_3,
        case when t.current_subcategory = 'mixed_restaurants' then r.recommended_detail_level_3 end,
        t.current_detail_level_3
    ) as final_detail_level_3,
    case
        when o.poi_id is not null and o.active_flag = true then 'override'
        when t.current_subcategory = 'mixed_restaurants' and r.poi_id is not null then 'rule_based'
        else 'original'
    end as classification_method,
    coalesce(
        case when o.poi_id is not null and o.active_flag = true then 'reviewed_override' end,
        case when t.current_subcategory = 'mixed_restaurants' then r.classification_confidence end,
        'not_classified'
    ) as classification_confidence,
    coalesce(case when t.current_subcategory = 'mixed_restaurants' then r.classification_score end, 0) as classification_score,
    current_timestamp as classification_run_at
from property_classification_mart.place_classification_text t
left join property_classification_mart.place_matched_keywords mk
    on t.poi_id = mk.poi_id
left join property_classification_mart.place_classification_recommendations r
    on t.poi_id = r.poi_id
left join property_classification_mart.place_classification_overrides o
    on t.poi_id = o.poi_id
   and o.active_flag = true;
