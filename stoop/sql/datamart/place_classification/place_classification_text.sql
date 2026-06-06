create or replace table property_classification_mart.place_classification_text as

with source_places as (

    select
        poi_id,
        name,
        category as current_category,
        subcategory as current_subcategory,
        detail_level_3 as current_detail_level_3,
        source_system,
        source_list_names as source_list_names_raw,
        tags as tags_raw,
        comment as comment_raw,
        editorial_summary as editorial_summary_raw
    from property_explorer_gold.dim_user_poi_v2

),

classification_base as (

    select
        *,
        concat_ws(
            ' ',
            comment_raw,
            editorial_summary_raw,
            source_list_names_raw,
            tags_raw
        ) as classification_text_raw
    from source_places

),

classification_clean as (

    select
        *,
        trim(
            regexp_replace(
                lower(regexp_replace(coalesce(classification_text_raw, ''), '[^a-zA-Z0-9 ]', ' ', 'g')),
                '\\s+',
                ' ',
                'g'
            )
        ) as classification_text_clean,
        trim(
            regexp_replace(
                lower(regexp_replace(coalesce(source_list_names_raw, ''), '[^a-zA-Z0-9 ]', ' ', 'g')),
                '\\s+',
                ' ',
                'g'
            )
        ) as source_list_names_clean,
        trim(
            regexp_replace(
                lower(regexp_replace(coalesce(tags_raw, ''), '[^a-zA-Z0-9 ]', ' ', 'g')),
                '\\s+',
                ' ',
                'g'
            )
        ) as tags_clean,
        trim(
            regexp_replace(
                lower(regexp_replace(coalesce(comment_raw, ''), '[^a-zA-Z0-9 ]', ' ', 'g')),
                '\\s+',
                ' ',
                'g'
            )
        ) as comment_clean,
        trim(
            regexp_replace(
                lower(regexp_replace(coalesce(editorial_summary_raw, ''), '[^a-zA-Z0-9 ]', ' ', 'g')),
                '\\s+',
                ' ',
                'g'
            )
        ) as editorial_summary_clean,
        comment_raw is not null and trim(comment_raw) <> '' as has_comment,
        editorial_summary_raw is not null and trim(editorial_summary_raw) <> '' as has_editorial_summary,
        source_list_names_raw is not null and trim(source_list_names_raw) <> '' as has_source_list_names,
        tags_raw is not null and trim(tags_raw) <> '' as has_tags,
        current_timestamp as created_at
    from classification_base

)

select
    poi_id,
    name,
    current_category,
    current_subcategory,
    current_detail_level_3,
    source_system,
    source_list_names_raw,
    tags_raw,
    comment_raw,
    editorial_summary_raw,
    classification_text_raw,
    classification_text_clean,
    source_list_names_clean,
    tags_clean,
    comment_clean,
    editorial_summary_clean,
    has_comment,
    has_editorial_summary,
    has_source_list_names,
    has_tags,
    created_at
from classification_clean;
