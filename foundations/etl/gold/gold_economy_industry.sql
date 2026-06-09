-- Gold industry structure mart
-- Grain: one row per geo_level + geo_id + year.
-- Uses ACS as the geography spine so all ACS-supported geographies are present.
-- BEA industry GDP fields are left-joined and sparse outside BEA-supported grains.

create or replace table patterns_in_place.gold.economics_industry_wide as
with acs_base as (
    select
        lower(geo_level) as geo_level,
        geo_id,
        geo_name,
        year,
        pop_total
    from patterns_in_place.silver.age_kpi
    where lower(geo_level) in ('county', 'cbsa', 'state')
),

acs_industry as (
    select
        lower(geo_level) as geo_level,
        geo_id,
        geo_name,
        year,
        ind_total_emp as acs_ind_total_emp,
        ind_ag_mining as acs_ind_ag_mining,
        ind_construction as acs_ind_construction,
        ind_manufacturing as acs_ind_manufacturing,
        ind_wholesale as acs_ind_wholesale,
        ind_retail as acs_ind_retail,
        ind_transport_util as acs_ind_transport_util,
        ind_information as acs_ind_information,
        ind_finance_real as acs_ind_finance_real,
        ind_professional as acs_ind_professional,
        ind_educ_health as acs_ind_educ_health,
        ind_arts_accomm_food as acs_ind_arts_accomm_food,
        ind_other_services as acs_ind_other_services,
        ind_public_admin as acs_ind_public_admin,
        pct_ind_ag_mining as pct_acs_ind_ag_mining,
        pct_ind_construction as pct_acs_ind_construction,
        pct_ind_manufacturing as pct_acs_ind_manufacturing,
        pct_ind_wholesale as pct_acs_ind_wholesale,
        pct_ind_retail as pct_acs_ind_retail,
        pct_ind_transport_util as pct_acs_ind_transport_util,
        pct_ind_information as pct_acs_ind_information,
        pct_ind_finance_real as pct_acs_ind_finance_real,
        pct_ind_professional as pct_acs_ind_professional,
        pct_ind_educ_health as pct_acs_ind_educ_health,
        pct_ind_arts_accomm_food as pct_acs_ind_arts_accomm_food,
        pct_ind_other_services as pct_acs_ind_other_services,
        pct_ind_public_admin as pct_acs_ind_public_admin
    from patterns_in_place.silver.labor_kpi
),

bea_industry as (
    select
        case
            when geo_id = '00000' then 'us'
            else lower(geo_level)
        end as geo_level,
        case
            when geo_id = '00000' then '1'
            when lower(geo_level) = 'state'
                and length(geo_id) = 5
                and substr(geo_id, 3, 3) = '000'
                then substr(geo_id, 1, 2)
            else geo_id
        end as geo_id,
        geo_name,
        period as year,
        real_gdp_total,
        real_gdp_natural_resources_all as real_gdp_natural_resources,
        real_gdp_manufacturing_all as real_gdp_manufacturing,
        real_gdp_construction,
        real_gdp_trade_all as real_gdp_trade,
        real_gdp_transportation,
        real_gdp_information,
        real_gdp_finance_insurance + real_gdp_real_estate as real_gdp_fire,
        real_gdp_professional_scientific
            + real_gdp_professional_management
            + real_gdp_professional_admin_support as real_gdp_professional,
        real_gdp_education_all as real_gdp_edu_health,
        real_gdp_arts_entertainment + real_gdp_accomodation_food as real_gdp_leisure,
        real_gdp_gov_enterprises as real_gdp_gov,
        real_gdp_natural_resources_all / nullif(real_gdp_total, 0) as pct_real_gdp_natural_resources,
        real_gdp_manufacturing_all / nullif(real_gdp_total, 0) as pct_real_gdp_manufacturing,
        real_gdp_construction / nullif(real_gdp_total, 0) as pct_real_gdp_construction,
        real_gdp_trade_all / nullif(real_gdp_total, 0) as pct_real_gdp_trade,
        real_gdp_transportation / nullif(real_gdp_total, 0) as pct_real_gdp_transportation,
        real_gdp_information / nullif(real_gdp_total, 0) as pct_real_gdp_information,
        (real_gdp_finance_insurance + real_gdp_real_estate) / nullif(real_gdp_total, 0) as pct_real_gdp_fire,
        (real_gdp_professional_scientific
            + real_gdp_professional_management
            + real_gdp_professional_admin_support) / nullif(real_gdp_total, 0) as pct_real_gdp_professional,
        real_gdp_education_all / nullif(real_gdp_total, 0) as pct_real_gdp_edu_health,
        (real_gdp_arts_entertainment + real_gdp_accomodation_food) / nullif(real_gdp_total, 0) as pct_real_gdp_leisure,
        real_gdp_gov_enterprises / nullif(real_gdp_total, 0) as pct_real_gdp_gov
    from patterns_in_place.silver.bea_regional_cagdp9_wide
),

qcew_industry as (
    select
        lower(geo_level) as geo_level,
        geo_id,
        geo_name,
        period as year,
        max(case when industry_code = '10' and own_code = '0' then annual_avg_emplvl end) as qcew_total_covered_emp,
        max(case when industry_code = '10' and own_code = '0' then annual_avg_estabs end) as qcew_total_covered_estabs,
        max(case when industry_code = '10' and own_code = '0' then total_annual_wages end) as qcew_total_covered_wages,
        max(case when industry_code = '10' and own_code = '0' then annual_avg_wkly_wage end) as qcew_total_covered_avg_wkly_wage,
        sum(case when own_code = '5' then annual_avg_emplvl else 0 end) as qcew_private_emp_total,
        sum(case when own_code = '5' then annual_avg_estabs else 0 end) as qcew_private_estabs_total,
        sum(case when own_code = '5' then total_annual_wages else 0 end) as qcew_private_wages_total,
        case
            when sum(case when own_code = '5' then annual_avg_emplvl else 0 end) > 0
                then sum(case when own_code = '5' then total_annual_wages else 0 end)
                    / sum(case when own_code = '5' then annual_avg_emplvl else 0 end)
                    / 52.0
            else null
        end as qcew_private_avg_wkly_wage,

        sum(case when own_code = '5' and industry_code in ('11', '21') then annual_avg_emplvl else 0 end) as qcew_private_emp_ag_mining,
        sum(case when own_code = '5' and industry_code = '23' then annual_avg_emplvl else 0 end) as qcew_private_emp_construction,
        sum(case when own_code = '5' and industry_code = '31-33' then annual_avg_emplvl else 0 end) as qcew_private_emp_manufacturing,
        sum(case when own_code = '5' and industry_code = '42' then annual_avg_emplvl else 0 end) as qcew_private_emp_wholesale,
        sum(case when own_code = '5' and industry_code = '44-45' then annual_avg_emplvl else 0 end) as qcew_private_emp_retail,
        sum(case when own_code = '5' and industry_code in ('22', '48-49') then annual_avg_emplvl else 0 end) as qcew_private_emp_transport_util,
        sum(case when own_code = '5' and industry_code = '51' then annual_avg_emplvl else 0 end) as qcew_private_emp_information,
        sum(case when own_code = '5' and industry_code in ('52', '53') then annual_avg_emplvl else 0 end) as qcew_private_emp_finance_real,
        sum(case when own_code = '5' and industry_code in ('54', '55', '56') then annual_avg_emplvl else 0 end) as qcew_private_emp_professional,
        sum(case when own_code = '5' and industry_code in ('61', '62') then annual_avg_emplvl else 0 end) as qcew_private_emp_educ_health,
        sum(case when own_code = '5' and industry_code in ('71', '72') then annual_avg_emplvl else 0 end) as qcew_private_emp_arts_accomm_food,
        sum(case when own_code = '5' and industry_code = '81' then annual_avg_emplvl else 0 end) as qcew_private_emp_other_services,
        sum(case when industry_code = '92' then annual_avg_emplvl else 0 end) as qcew_public_admin_emp,

        case when sum(case when own_code = '5' and industry_code in ('11', '21') then annual_avg_emplvl else 0 end) > 0
            then sum(case when own_code = '5' and industry_code in ('11', '21') then total_annual_wages else 0 end)
                / sum(case when own_code = '5' and industry_code in ('11', '21') then annual_avg_emplvl else 0 end) / 52.0
            else null end as qcew_private_avg_wkly_wage_ag_mining,
        case when sum(case when own_code = '5' and industry_code = '23' then annual_avg_emplvl else 0 end) > 0
            then sum(case when own_code = '5' and industry_code = '23' then total_annual_wages else 0 end)
                / sum(case when own_code = '5' and industry_code = '23' then annual_avg_emplvl else 0 end) / 52.0
            else null end as qcew_private_avg_wkly_wage_construction,
        case when sum(case when own_code = '5' and industry_code = '31-33' then annual_avg_emplvl else 0 end) > 0
            then sum(case when own_code = '5' and industry_code = '31-33' then total_annual_wages else 0 end)
                / sum(case when own_code = '5' and industry_code = '31-33' then annual_avg_emplvl else 0 end) / 52.0
            else null end as qcew_private_avg_wkly_wage_manufacturing,
        case when sum(case when own_code = '5' and industry_code = '42' then annual_avg_emplvl else 0 end) > 0
            then sum(case when own_code = '5' and industry_code = '42' then total_annual_wages else 0 end)
                / sum(case when own_code = '5' and industry_code = '42' then annual_avg_emplvl else 0 end) / 52.0
            else null end as qcew_private_avg_wkly_wage_wholesale,
        case when sum(case when own_code = '5' and industry_code = '44-45' then annual_avg_emplvl else 0 end) > 0
            then sum(case when own_code = '5' and industry_code = '44-45' then total_annual_wages else 0 end)
                / sum(case when own_code = '5' and industry_code = '44-45' then annual_avg_emplvl else 0 end) / 52.0
            else null end as qcew_private_avg_wkly_wage_retail,
        case when sum(case when own_code = '5' and industry_code in ('22', '48-49') then annual_avg_emplvl else 0 end) > 0
            then sum(case when own_code = '5' and industry_code in ('22', '48-49') then total_annual_wages else 0 end)
                / sum(case when own_code = '5' and industry_code in ('22', '48-49') then annual_avg_emplvl else 0 end) / 52.0
            else null end as qcew_private_avg_wkly_wage_transport_util,
        case when sum(case when own_code = '5' and industry_code = '51' then annual_avg_emplvl else 0 end) > 0
            then sum(case when own_code = '5' and industry_code = '51' then total_annual_wages else 0 end)
                / sum(case when own_code = '5' and industry_code = '51' then annual_avg_emplvl else 0 end) / 52.0
            else null end as qcew_private_avg_wkly_wage_information,
        case when sum(case when own_code = '5' and industry_code in ('52', '53') then annual_avg_emplvl else 0 end) > 0
            then sum(case when own_code = '5' and industry_code in ('52', '53') then total_annual_wages else 0 end)
                / sum(case when own_code = '5' and industry_code in ('52', '53') then annual_avg_emplvl else 0 end) / 52.0
            else null end as qcew_private_avg_wkly_wage_finance_real,
        case when sum(case when own_code = '5' and industry_code in ('54', '55', '56') then annual_avg_emplvl else 0 end) > 0
            then sum(case when own_code = '5' and industry_code in ('54', '55', '56') then total_annual_wages else 0 end)
                / sum(case when own_code = '5' and industry_code in ('54', '55', '56') then annual_avg_emplvl else 0 end) / 52.0
            else null end as qcew_private_avg_wkly_wage_professional,
        case when sum(case when own_code = '5' and industry_code in ('61', '62') then annual_avg_emplvl else 0 end) > 0
            then sum(case when own_code = '5' and industry_code in ('61', '62') then total_annual_wages else 0 end)
                / sum(case when own_code = '5' and industry_code in ('61', '62') then annual_avg_emplvl else 0 end) / 52.0
            else null end as qcew_private_avg_wkly_wage_educ_health,
        case when sum(case when own_code = '5' and industry_code in ('71', '72') then annual_avg_emplvl else 0 end) > 0
            then sum(case when own_code = '5' and industry_code in ('71', '72') then total_annual_wages else 0 end)
                / sum(case when own_code = '5' and industry_code in ('71', '72') then annual_avg_emplvl else 0 end) / 52.0
            else null end as qcew_private_avg_wkly_wage_arts_accomm_food,
        case when sum(case when own_code = '5' and industry_code = '81' then annual_avg_emplvl else 0 end) > 0
            then sum(case when own_code = '5' and industry_code = '81' then total_annual_wages else 0 end)
                / sum(case when own_code = '5' and industry_code = '81' then annual_avg_emplvl else 0 end) / 52.0
            else null end as qcew_private_avg_wkly_wage_other_services,
        case when sum(case when industry_code = '92' then annual_avg_emplvl else 0 end) > 0
            then sum(case when industry_code = '92' then total_annual_wages else 0 end)
                / sum(case when industry_code = '92' then annual_avg_emplvl else 0 end) / 52.0
            else null end as qcew_public_admin_avg_wkly_wage
    from patterns_in_place.silver.bls_qcew
    group by 1, 2, 3, 4
),

cbp_industry as (
    select
        lower(geo_level) as geo_level,
        geo_id,
        geo_name,
        period as year,
        max(case when is_total_row then establishments end) as cbp_total_estabs,
        max(case when is_total_row then employment_march12 end) as cbp_total_emp_march12,
        max(case when is_total_row then annual_payroll_k end) as cbp_total_annual_payroll_k,
        max(case when is_total_row then first_quarter_payroll_k end) as cbp_total_first_quarter_payroll_k,
        sum(case when silver_rollup_family = 'ag_mining' then establishments else 0 end) as cbp_estabs_ag_mining,
        sum(case when silver_rollup_family = 'construction' then establishments else 0 end) as cbp_estabs_construction,
        sum(case when silver_rollup_family = 'manufacturing' then establishments else 0 end) as cbp_estabs_manufacturing,
        sum(case when silver_rollup_family = 'wholesale' then establishments else 0 end) as cbp_estabs_wholesale,
        sum(case when silver_rollup_family = 'retail' then establishments else 0 end) as cbp_estabs_retail,
        sum(case when silver_rollup_family = 'transport_util' then establishments else 0 end) as cbp_estabs_transport_util,
        sum(case when silver_rollup_family = 'information' then establishments else 0 end) as cbp_estabs_information,
        sum(case when silver_rollup_family = 'finance_real' then establishments else 0 end) as cbp_estabs_finance_real,
        sum(case when silver_rollup_family = 'professional' then establishments else 0 end) as cbp_estabs_professional,
        sum(case when silver_rollup_family = 'educ_health' then establishments else 0 end) as cbp_estabs_educ_health,
        sum(case when silver_rollup_family = 'arts_accomm_food' then establishments else 0 end) as cbp_estabs_arts_accomm_food,
        sum(case when silver_rollup_family = 'other_services' then establishments else 0 end) as cbp_estabs_other_services
    from patterns_in_place.silver.cbp
    group by 1, 2, 3, 4
),

final as (
    select
        b.geo_level,
        b.geo_id,
        coalesce(b.geo_name, a.geo_name, bea.geo_name) as geo_name,
        b.year,
        b.pop_total,
        a.acs_ind_total_emp,
        a.acs_ind_ag_mining,
        a.acs_ind_construction,
        a.acs_ind_manufacturing,
        a.acs_ind_wholesale,
        a.acs_ind_retail,
        a.acs_ind_transport_util,
        a.acs_ind_information,
        a.acs_ind_finance_real,
        a.acs_ind_professional,
        a.acs_ind_educ_health,
        a.acs_ind_arts_accomm_food,
        a.acs_ind_other_services,
        a.acs_ind_public_admin,
        a.pct_acs_ind_ag_mining,
        a.pct_acs_ind_construction,
        a.pct_acs_ind_manufacturing,
        a.pct_acs_ind_wholesale,
        a.pct_acs_ind_retail,
        a.pct_acs_ind_transport_util,
        a.pct_acs_ind_information,
        a.pct_acs_ind_finance_real,
        a.pct_acs_ind_professional,
        a.pct_acs_ind_educ_health,
        a.pct_acs_ind_arts_accomm_food,
        a.pct_acs_ind_other_services,
        a.pct_acs_ind_public_admin,
        q.qcew_total_covered_emp,
        q.qcew_total_covered_estabs,
        q.qcew_total_covered_wages,
        q.qcew_total_covered_avg_wkly_wage,
        q.qcew_private_emp_total,
        q.qcew_private_estabs_total,
        q.qcew_private_wages_total,
        q.qcew_private_avg_wkly_wage,
        q.qcew_private_emp_ag_mining,
        q.qcew_private_emp_construction,
        q.qcew_private_emp_manufacturing,
        q.qcew_private_emp_wholesale,
        q.qcew_private_emp_retail,
        q.qcew_private_emp_transport_util,
        q.qcew_private_emp_information,
        q.qcew_private_emp_finance_real,
        q.qcew_private_emp_professional,
        q.qcew_private_emp_educ_health,
        q.qcew_private_emp_arts_accomm_food,
        q.qcew_private_emp_other_services,
        q.qcew_public_admin_emp,
        q.qcew_private_avg_wkly_wage_ag_mining,
        q.qcew_private_avg_wkly_wage_construction,
        q.qcew_private_avg_wkly_wage_manufacturing,
        q.qcew_private_avg_wkly_wage_wholesale,
        q.qcew_private_avg_wkly_wage_retail,
        q.qcew_private_avg_wkly_wage_transport_util,
        q.qcew_private_avg_wkly_wage_information,
        q.qcew_private_avg_wkly_wage_finance_real,
        q.qcew_private_avg_wkly_wage_professional,
        q.qcew_private_avg_wkly_wage_educ_health,
        q.qcew_private_avg_wkly_wage_arts_accomm_food,
        q.qcew_private_avg_wkly_wage_other_services,
        q.qcew_public_admin_avg_wkly_wage,
        c.cbp_total_estabs,
        c.cbp_total_emp_march12,
        c.cbp_total_annual_payroll_k,
        c.cbp_total_first_quarter_payroll_k,
        c.cbp_estabs_ag_mining,
        c.cbp_estabs_construction,
        c.cbp_estabs_manufacturing,
        c.cbp_estabs_wholesale,
        c.cbp_estabs_retail,
        c.cbp_estabs_transport_util,
        c.cbp_estabs_information,
        c.cbp_estabs_finance_real,
        c.cbp_estabs_professional,
        c.cbp_estabs_educ_health,
        c.cbp_estabs_arts_accomm_food,
        c.cbp_estabs_other_services,
        bea.real_gdp_total,
        bea.real_gdp_natural_resources,
        bea.real_gdp_manufacturing,
        bea.real_gdp_construction,
        bea.real_gdp_trade,
        bea.real_gdp_transportation,
        bea.real_gdp_information,
        bea.real_gdp_fire,
        bea.real_gdp_professional,
        bea.real_gdp_edu_health,
        bea.real_gdp_leisure,
        bea.real_gdp_gov,
        bea.pct_real_gdp_natural_resources,
        bea.pct_real_gdp_manufacturing,
        bea.pct_real_gdp_construction,
        bea.pct_real_gdp_trade,
        bea.pct_real_gdp_transportation,
        bea.pct_real_gdp_information,
        bea.pct_real_gdp_fire,
        bea.pct_real_gdp_professional,
        bea.pct_real_gdp_edu_health,
        bea.pct_real_gdp_leisure,
        bea.pct_real_gdp_gov
    from acs_base b
    left join acs_industry a
        on b.geo_level = a.geo_level
       and b.geo_id = a.geo_id
       and b.year = a.year
    left join bea_industry bea
        on b.geo_level = bea.geo_level
       and b.geo_id = bea.geo_id
       and b.year = bea.year
    left join qcew_industry q
        on b.geo_level = q.geo_level
       and b.geo_id = q.geo_id
       and b.year = q.year
    left join cbp_industry c
        on b.geo_level = c.geo_level
       and b.geo_id = c.geo_id
       and b.year = c.year
)

select
    *,
    cbp_total_estabs / nullif(pop_total, 0) * 1000.0 as cbp_estabs_per_1000_residents,
    cbp_estabs_ag_mining / nullif(cbp_total_estabs, 0) as pct_cbp_estabs_ag_mining,
    cbp_estabs_construction / nullif(cbp_total_estabs, 0) as pct_cbp_estabs_construction,
    cbp_estabs_manufacturing / nullif(cbp_total_estabs, 0) as pct_cbp_estabs_manufacturing,
    cbp_estabs_wholesale / nullif(cbp_total_estabs, 0) as pct_cbp_estabs_wholesale,
    cbp_estabs_retail / nullif(cbp_total_estabs, 0) as pct_cbp_estabs_retail,
    cbp_estabs_transport_util / nullif(cbp_total_estabs, 0) as pct_cbp_estabs_transport_util,
    cbp_estabs_information / nullif(cbp_total_estabs, 0) as pct_cbp_estabs_information,
    cbp_estabs_finance_real / nullif(cbp_total_estabs, 0) as pct_cbp_estabs_finance_real,
    cbp_estabs_professional / nullif(cbp_total_estabs, 0) as pct_cbp_estabs_professional,
    cbp_estabs_educ_health / nullif(cbp_total_estabs, 0) as pct_cbp_estabs_educ_health,
    cbp_estabs_arts_accomm_food / nullif(cbp_total_estabs, 0) as pct_cbp_estabs_arts_accomm_food,
    cbp_estabs_other_services / nullif(cbp_total_estabs, 0) as pct_cbp_estabs_other_services,
    qcew_private_emp_ag_mining / nullif(qcew_private_emp_total, 0) as pct_qcew_private_emp_ag_mining,
    qcew_private_emp_construction / nullif(qcew_private_emp_total, 0) as pct_qcew_private_emp_construction,
    qcew_private_emp_manufacturing / nullif(qcew_private_emp_total, 0) as pct_qcew_private_emp_manufacturing,
    qcew_private_emp_wholesale / nullif(qcew_private_emp_total, 0) as pct_qcew_private_emp_wholesale,
    qcew_private_emp_retail / nullif(qcew_private_emp_total, 0) as pct_qcew_private_emp_retail,
    qcew_private_emp_transport_util / nullif(qcew_private_emp_total, 0) as pct_qcew_private_emp_transport_util,
    qcew_private_emp_information / nullif(qcew_private_emp_total, 0) as pct_qcew_private_emp_information,
    qcew_private_emp_finance_real / nullif(qcew_private_emp_total, 0) as pct_qcew_private_emp_finance_real,
    qcew_private_emp_professional / nullif(qcew_private_emp_total, 0) as pct_qcew_private_emp_professional,
    qcew_private_emp_educ_health / nullif(qcew_private_emp_total, 0) as pct_qcew_private_emp_educ_health,
    qcew_private_emp_arts_accomm_food / nullif(qcew_private_emp_total, 0) as pct_qcew_private_emp_arts_accomm_food,
    qcew_private_emp_other_services / nullif(qcew_private_emp_total, 0) as pct_qcew_private_emp_other_services,
    qcew_private_emp_total / nullif(qcew_total_covered_emp, 0) as pct_qcew_private_emp_of_total_covered,
    qcew_public_admin_emp / nullif(qcew_total_covered_emp, 0) as pct_qcew_public_admin_emp_of_total_covered,
    real_gdp_natural_resources
        + real_gdp_manufacturing
        + real_gdp_construction
        + real_gdp_trade
        + real_gdp_transportation
        + real_gdp_information
        + real_gdp_fire
        + real_gdp_professional
        + real_gdp_edu_health
        + real_gdp_leisure
        + real_gdp_gov as sector_sum,
    real_gdp_total - sector_sum as calc_real_gdp_other,
    calc_real_gdp_other / nullif(real_gdp_total, 0) as pct_calc_real_gdp_other,
    (
        power(pct_real_gdp_natural_resources, 2)
        + power(pct_real_gdp_manufacturing, 2)
        + power(pct_real_gdp_construction, 2)
        + power(pct_real_gdp_trade, 2)
        + power(pct_real_gdp_transportation, 2)
        + power(pct_real_gdp_information, 2)
        + power(pct_real_gdp_fire, 2)
        + power(pct_real_gdp_professional, 2)
        + power(pct_real_gdp_edu_health, 2)
        + power(pct_real_gdp_leisure, 2)
        + power(pct_real_gdp_gov, 2)
        + power(pct_calc_real_gdp_other, 2)
    ) as industry_concentration_hhi,
    (
        power(pct_acs_ind_ag_mining, 2)
        + power(pct_acs_ind_construction, 2)
        + power(pct_acs_ind_manufacturing, 2)
        + power(pct_acs_ind_wholesale, 2)
        + power(pct_acs_ind_retail, 2)
        + power(pct_acs_ind_transport_util, 2)
        + power(pct_acs_ind_information, 2)
        + power(pct_acs_ind_finance_real, 2)
        + power(pct_acs_ind_professional, 2)
        + power(pct_acs_ind_educ_health, 2)
        + power(pct_acs_ind_arts_accomm_food, 2)
        + power(pct_acs_ind_other_services, 2)
        + power(pct_acs_ind_public_admin, 2)
    ) as acs_industry_concentration_hhi,
    sector_sum / nullif(real_gdp_total, 0) as sector_sum_ratio,
    case
        when sector_sum_ratio > 1.05 then 'Sector Bug'
        when sector_sum_ratio is null then null
        else 'Non Bug'
    end as sector_sum_ratio_quality_flag
from final;
