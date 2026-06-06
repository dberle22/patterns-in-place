create or replace table neighborhood_character_mart.nta_category_controls as

select *
from (
    values
        ('restaurants', true, true, 5, 'Restaurants', 'First-class Explore input.'),
        ('museums', true, true, 5, 'Museums', 'Strong cultural anchor.'),
        ('bookstores', true, true, 5, 'Bookstores', 'High-character editorial signal.'),
        ('shopping', true, true, 5, 'Shopping', 'Broad destination signal.'),
        ('hotels', true, true, 5, 'Hotels', 'Visitor-oriented anchor and control category.'),
        ('bakeries', true, true, 5, 'Bakeries', 'Food-adjacent editorial signal.'),
        ('food_markets', true, true, 5, 'Food markets', 'Browse-and-eat signal.'),
        ('specialty_grocery', true, true, 5, 'Specialty grocery', 'Useful in food stories.'),
        ('record_stores', true, true, 5, 'Record stores', 'Niche but high-character when present.'),
        ('bars', true, true, 3, 'Bars', 'Included even if under-covered so validation shows gaps.'),
        ('music_venues', false, false, 5, 'Music venues', 'Hold until coverage is more trustworthy.'),
        ('movie_theaters', false, false, 5, 'Movie theaters', 'Hold for now.'),
        ('coffee', false, false, 5, 'Coffee', 'Hide until evidence improves.')
) as controls (
    category,
    include_in_explore_v1,
    known_for_enabled,
    min_nyc_category_total,
    display_label,
    notes
);
