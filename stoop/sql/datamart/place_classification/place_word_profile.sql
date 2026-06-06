create or replace table property_classification_mart.place_word_profile as

with base as (

    select
        poi_id,
        name,
        current_category,
        current_subcategory,
        classification_text_clean
    from property_classification_mart.place_classification_text
    where current_category = 'restaurants'
      and classification_text_clean is not null
      and trim(classification_text_clean) <> ''

),

analysis_base as (

    select
        'restaurant' as analysis_domain,
        'all_restaurants' as analysis_segment,
        poi_id,
        name,
        current_category,
        current_subcategory,
        classification_text_clean
    from base

    union all

    select
        'restaurant' as analysis_domain,
        'mixed_restaurants' as analysis_segment,
        poi_id,
        name,
        current_category,
        current_subcategory,
        classification_text_clean
    from base
    where current_subcategory = 'mixed_restaurants'

    union all

    select
        'restaurant' as analysis_domain,
        'subcategory:' || current_subcategory as analysis_segment,
        poi_id,
        name,
        current_category,
        current_subcategory,
        classification_text_clean
    from base
    where current_subcategory is not null
      and trim(current_subcategory) <> ''

),

tokens as (

    select
        analysis_domain,
        analysis_segment,
        poi_id,
        name,
        current_category,
        current_subcategory,
        unnest(string_split(classification_text_clean, ' ')) as token
    from analysis_base

),

filtered_tokens as (

    select
        analysis_domain,
        analysis_segment,
        poi_id,
        name,
        current_category,
        current_subcategory,
        token
    from tokens
    where token is not null
      and trim(token) <> ''
      and length(token) >= 3
      and token not in (
          'the', 'and', 'for', 'with', 'from', 'that', 'this',
          'are', 'you', 'your', 'its', 'into', 'has', 'have',
          'had', 'was', 'were', 'been', 'being', 'one', 'two',
          'new', 'york', 'nyc', 'best', 'top', 'food', 'foods',
          'menu', 'menus', 'place', 'places', 'spot', 'spots',
          'restaurant', 'restaurants', 'eat', 'eats', 'eating',
          'serves', 'serving', 'served', 'known', 'including',
          'like', 'also', 'where', 'what', 'when', 'which',
          'their', 'there', 'they', 'them', 'these', 'those',
          'more', 'most', 'some', 'very', 'much', 'many',
          'good', 'great', 'favorite', 'popular', 'classic',
          'price', 'mag', '1000', 'cuisines', 'plus', 'fare', 'but',
          'all', '100', 'out', 'appetit', 'bon', 'setting', 'chef',
          'time', 'love', 'hours', 'brooklyn', 'tip'
      )

)

select
    analysis_domain,
    analysis_segment,
    token,
    count(*) as token_count,
    count(distinct poi_id) as place_count,
    count(distinct poi_id) * 1.0 / (
        select count(distinct denominator.poi_id)
        from analysis_base denominator
        where denominator.analysis_domain = filtered_tokens.analysis_domain
          and denominator.analysis_segment = filtered_tokens.analysis_segment
    ) as place_share,
    string_agg(distinct name, ', ') as example_places,
    current_timestamp as created_at
from filtered_tokens
group by
    analysis_domain,
    analysis_segment,
    token
order by analysis_segment, place_count desc, token_count desc;
