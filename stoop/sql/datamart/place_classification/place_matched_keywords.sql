create or replace table property_classification_mart.place_matched_keywords as

select
    poi_id,
    place_name,
    string_agg(distinct keyword, ', ' order by keyword) as matched_keywords,
    count(distinct keyword_id) as matched_keyword_count,
    string_agg(distinct case when keyword_role = 'type' then keyword end, ', ' order by case when keyword_role = 'type' then keyword end) as matched_type_keywords,
    string_agg(distinct case when keyword_role = 'cuisine' then keyword end, ', ' order by case when keyword_role = 'cuisine' then keyword end) as matched_cuisine_keywords,
    string_agg(distinct case when keyword_role = 'experience' then keyword end, ', ' order by case when keyword_role = 'experience' then keyword end) as matched_vibe_keywords,
    string_agg(distinct case when keyword_role = 'format' then keyword end, ', ' order by case when keyword_role = 'format' then keyword end) as matched_format_keywords,
    string_agg(distinct case when keyword_role = 'occasion' then keyword end, ', ' order by case when keyword_role = 'occasion' then keyword end) as matched_occasion_keywords,
    string_agg(distinct case when keyword_role = 'quality_signal' then keyword end, ', ' order by case when keyword_role = 'quality_signal' then keyword end) as matched_quality_signal_keywords,
    sum(effective_weight) as total_keyword_weight,
    current_timestamp as created_at
from property_classification_mart.place_keyword_matches
group by
    poi_id,
    place_name;
