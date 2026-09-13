-- The national baseline is a tract-share comparison. It deliberately does not
-- turn tract counts into a population-weighted national claim.
WITH market_zone_counts AS (
    SELECT zone_type, COUNT(*) AS market_tract_count
    FROM mart_intelligence.intelligence_zones
    WHERE cbsa_code = '__CBSA_CODE__'
    GROUP BY zone_type
),
national_zone_counts AS (
    SELECT zone_type, COUNT(*) AS national_tract_count
    FROM mart_intelligence.intelligence_zones
    GROUP BY zone_type
),
market_total AS (SELECT SUM(market_tract_count) AS tract_count FROM market_zone_counts),
national_total AS (SELECT SUM(national_tract_count) AS tract_count FROM national_zone_counts)
SELECT m.zone_type, m.market_tract_count,
       m.market_tract_count / mt.tract_count AS market_tract_share,
       n.national_tract_count,
       n.national_tract_count / nt.tract_count AS national_tract_share,
       (m.market_tract_count / mt.tract_count) - (n.national_tract_count / nt.tract_count) AS share_difference
FROM market_zone_counts AS m
JOIN national_zone_counts AS n USING (zone_type)
CROSS JOIN market_total AS mt
CROSS JOIN national_total AS nt
ORDER BY market_tract_share DESC, zone_type;
