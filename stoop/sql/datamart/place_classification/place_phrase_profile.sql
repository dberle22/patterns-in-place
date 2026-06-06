create or replace table property_classification_mart.place_phrase_profile as

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
        row_number() over (
            partition by analysis_domain, analysis_segment, poi_id
            order by ordinality
        ) as token_position,
        token
    from analysis_base,
    unnest(string_split(classification_text_clean, ' ')) with ordinality as t(token, ordinality)
    where token is not null
      and trim(token) <> ''
      and length(token) >= 2

),

filtered_tokens as (

    select *
    from tokens
    where token not in (
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
        'all', '100', 'out', 'appetit', 'bon', 'setting', 'chef', 'open',
        'time', 'love', 'hours', 'brooklyn', 'tip'
    )

),

bigrams as (

    select
        t1.analysis_domain,
        t1.analysis_segment,
        t1.poi_id,
        t1.name,
        t1.current_category,
        t1.current_subcategory,
        2 as phrase_length,
        t1.token || ' ' || t2.token as phrase
    from filtered_tokens t1
    join filtered_tokens t2
        on t1.analysis_domain = t2.analysis_domain
       and t1.analysis_segment = t2.analysis_segment
       and t1.poi_id = t2.poi_id
       and t2.token_position = t1.token_position + 1

),

trigrams as (

    select
        t1.analysis_domain,
        t1.analysis_segment,
        t1.poi_id,
        t1.name,
        t1.current_category,
        t1.current_subcategory,
        3 as phrase_length,
        t1.token || ' ' || t2.token || ' ' || t3.token as phrase
    from filtered_tokens t1
    join filtered_tokens t2
        on t1.analysis_domain = t2.analysis_domain
       and t1.analysis_segment = t2.analysis_segment
       and t1.poi_id = t2.poi_id
       and t2.token_position = t1.token_position + 1
    join filtered_tokens t3
        on t1.analysis_domain = t3.analysis_domain
       and t1.analysis_segment = t3.analysis_segment
       and t1.poi_id = t3.poi_id
       and t3.token_position = t1.token_position + 2

),

phrases as (

    select * from bigrams
    union all
    select * from trigrams

)

select
    analysis_domain,
    analysis_segment,
    phrase,
    phrase_length,
    count(*) as phrase_count,
    count(distinct poi_id) as place_count,
    count(distinct poi_id) * 1.0 / (
        select count(distinct denominator.poi_id)
        from analysis_base denominator
        where denominator.analysis_domain = phrases.analysis_domain
          and denominator.analysis_segment = phrases.analysis_segment
    ) as place_share,
    string_agg(distinct name, ', ') as example_places,
    current_timestamp as created_at
from phrases
where phrase is not null
  and trim(phrase) <> ''
group by
    analysis_domain,
    analysis_segment,
    phrase,
    phrase_length
order by analysis_segment, place_count desc, phrase_count desc;
