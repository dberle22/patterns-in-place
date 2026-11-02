-- Read the verified Infrastructure consumer artifact, supplied by its handoff.
-- This is a drawing selection over source-faithful features, not a new engine
-- mapping, legal road inventory or routable network. No operator tag is needed.
WITH tags AS (
    SELECT source_record_key, source_name, feature_type, geometry AS geom_wkb,
        json_extract_string(source_tags, '$.other_tags') AS other_tags
    FROM read_parquet('__INFRASTRUCTURE_PATH__')
    WHERE market_id = '36' AND market_boundary_geo_level = 'state'
      AND record_status = 'retained'
      AND feature_type IN ('motorway', 'rail')
), parsed AS (
    SELECT *,
        NULLIF(regexp_extract(other_tags, '"ref"=>"([^"]*)"', 1), '') AS route_ref,
        NULLIF(regexp_extract(other_tags, '"usage"=>"([^"]*)"', 1), '') AS rail_usage
    FROM tags
), selected AS (
    SELECT *, CASE
        -- Names distinguish the mainline from the Adirondack Northway and
        -- Albany's free I-90. Include the other named system sections and the
        -- Grand Island bridges, which use bridge names instead of road names.
        -- Checked against the Authority's six-section description:
        -- https://www.thruway.ny.gov/business/real-property
        WHEN feature_type = 'motorway' AND (
            source_name IN (
                'New York State Thruway', 'New York State Thruway Berkshire Connector',
                'New England Thruway', 'Niagara Thruway',
                'Cross Westchester Expressway', 'Garden State Parkway Connector'
            )
            OR (source_name IN ('North Grand Island Bridge', 'South Grand Island Bridge')
                AND regexp_matches(route_ref, '(^|;)I 190(;|$)'))
            OR (source_name = 'AMVETS Memorial Highway'
                AND regexp_matches(route_ref, '(^|;)I 90(;|$)'))
        ) THEN 'thruway'
        -- Exact route tokens avoid counting the I-81 business route as an
        -- interstate. Semicolon-separated concurrent routes remain eligible.
        WHEN feature_type = 'motorway'
            AND regexp_matches(route_ref, '(^|;)I [0-9]+(;|$)') THEN 'interstate'
        -- A missing usage tag is unavailable classification, never evidence
        -- that a line is a main line. Subways/light rail are outside this map.
        WHEN feature_type = 'rail' AND rail_usage = 'main' THEN 'mainline_rail'
        ELSE NULL
    END AS map_layer
    FROM parsed
)
SELECT source_record_key, source_name, route_ref, rail_usage, map_layer, geom_wkb
FROM selected
WHERE map_layer IS NOT NULL
ORDER BY map_layer, source_record_key;
