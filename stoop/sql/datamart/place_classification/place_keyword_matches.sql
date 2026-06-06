create or replace table property_classification_mart.place_keyword_matches as

with classification_base as (

    select
        poi_id,
        name as place_name,
        current_category,
        current_subcategory,
        current_detail_level_3,
        source_list_names_clean,
        tags_clean,
        comment_clean,
        editorial_summary_clean
    from property_classification_mart.place_classification_text
    where current_category = 'restaurants'

),

source_texts as (

    select
        poi_id,
        place_name,
        current_category,
        current_subcategory,
        current_detail_level_3,
        'editorial_summary' as source_field,
        editorial_summary_clean as source_text_clean,
        3 as source_weight
    from classification_base
    where editorial_summary_clean is not null
      and trim(editorial_summary_clean) <> ''

    union all

    select
        poi_id,
        place_name,
        current_category,
        current_subcategory,
        current_detail_level_3,
        'comment' as source_field,
        comment_clean as source_text_clean,
        2 as source_weight
    from classification_base
    where comment_clean is not null
      and trim(comment_clean) <> ''

    union all

    select
        poi_id,
        place_name,
        current_category,
        current_subcategory,
        current_detail_level_3,
        'tags' as source_field,
        tags_clean as source_text_clean,
        1 as source_weight
    from classification_base
    where tags_clean is not null
      and trim(tags_clean) <> ''

    union all

    select
        poi_id,
        place_name,
        current_category,
        current_subcategory,
        current_detail_level_3,
        'source_list_names' as source_field,
        source_list_names_clean as source_text_clean,
        0 as source_weight
    from classification_base
    where source_list_names_clean is not null
      and trim(source_list_names_clean) <> ''

),

active_mappings as (

    select
        keyword_id,
        keyword,
        keyword_clean,
        match_type,
        place_domain,
        mapped_category,
        mapped_subcategory,
        coalesce(mapped_detail_level_3, '') as mapped_detail_level_3,
        keyword_role,
        weight,
        priority
    from property_classification_mart.place_keyword_mapping
    where active_flag = true
      and place_domain = 'restaurants'

)

select
    s.poi_id,
    s.place_name,
    m.keyword_id,
    m.keyword,
    m.match_type,
    m.place_domain,
    s.source_field,
    m.mapped_category,
    m.mapped_subcategory,
    m.mapped_detail_level_3,
    m.keyword_role,
    m.weight as base_weight,
    s.source_weight,
    m.weight
        + s.source_weight
        + case
            when m.match_type = 'phrase' or strpos(m.keyword_clean, ' ') > 0 then 1
            else 0
          end as effective_weight,
    m.priority,
    current_timestamp as created_at
from source_texts s
join active_mappings m
    on case
        when m.match_type = 'exact' then s.source_text_clean = m.keyword_clean
        else strpos(' ' || s.source_text_clean || ' ', ' ' || m.keyword_clean || ' ') > 0
       end;
