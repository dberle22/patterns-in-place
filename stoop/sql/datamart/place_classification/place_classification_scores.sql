create or replace table property_classification_mart.place_classification_scores as

select
    poi_id,
    place_name,
    mapped_category as candidate_category,
    mapped_subcategory as candidate_subcategory,
    coalesce(mapped_detail_level_3, '') as candidate_detail_level_3,
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
    count(distinct source_field) as source_field_count,
    string_agg(distinct keyword, ', ' order by keyword) as matched_keywords,
    min(priority) as highest_priority,
    current_timestamp as created_at
from property_classification_mart.place_keyword_matches
where mapped_subcategory <> '__any__'
group by
    poi_id,
    place_name,
    mapped_category,
    mapped_subcategory,
    coalesce(mapped_detail_level_3, '');
