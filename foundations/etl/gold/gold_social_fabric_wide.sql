create or replace table patterns_in_place.gold.social_fabric_wide as
select
    sc.geo_level,
    sc.geo_id,
    sc.geo_name,
    sc.population_total,
    sc.children_below_p50,
    sc.economic_connectedness,
    sc.childhood_economic_connectedness,
    sc.neighborhood_economic_connectedness,
    sc.economic_exposure,
    sc.childhood_economic_exposure,
    sc.neighborhood_economic_exposure,
    sc.friending_bias,
    sc.childhood_friending_bias,
    sc.neighborhood_friending_bias,
    sc.cohesion_clustering,
    sc.cohesion_support_ratio,
    sc.civic_engagement_volunteering_rate,
    sc.civic_organizations_per_1000,
    bmf.snapshot_date as irs_bmf_snapshot_date,
    bmf.population_year as irs_bmf_population_year,
    bmf.nonprofit_org_count_est,
    bmf.nonprofit_org_count_nonreligious_est,
    bmf.nonprofits_per_100k,
    bmf.nonprofits_total_per_100k,
    bmf.source_zip5_count as nonprofit_source_zip5_count,
    bmf.weight_method as nonprofit_weight_method
from silver.opportunity_insights_social_capital sc
left join silver.irs_bmf bmf
    on sc.geo_level = bmf.geo_level
   and sc.geo_id = bmf.geo_id
;
