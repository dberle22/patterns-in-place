-- Exact tract-to-CBSA relationship. SUM is valid only when the metric is additive.
select rollup.cbsa_code, sum(metric.value) as total_value
from some_tract_metric as metric
inner join mart_geography.rollup_tract_to_cbsa as rollup
    on metric.tract_geoid = rollup.tract_geoid
group by 1;

-- A rate needs numerator/denominator aggregation; the mart does not average rates.
select rollup.cbsa_code,
       sum(metric.numerator) / nullif(sum(metric.denominator), 0) as rate
from some_tract_rate as metric
inner join mart_geography.rollup_tract_to_cbsa as rollup
    on metric.tract_geoid = rollup.tract_geoid
group by 1;
