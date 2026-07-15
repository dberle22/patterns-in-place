with base as (
  select
    geo_level,
    geo_id,
    geo_name,
    year as period,
    pop_totalE as pop_total,
    case when geo_id = '33100' then true else false end as highlight_flag,
    case when geo_id = '1' then 'United States' else null end as benchmark_label,
    'Miami vs United States' as facet_label,
    pop_age_male_under5E,
    pop_age_male_5_9E,
    pop_age_male_10_14E,
    pop_age_male_15_17E,
    pop_age_male_18_19E,
    pop_age_male_20E,
    pop_age_male_21E,
    pop_age_male_22_24E,
    pop_age_male_25_29E,
    pop_age_male_30_34E,
    pop_age_male_35_39E,
    pop_age_male_40_44E,
    pop_age_male_45_49E,
    pop_age_male_50_54E,
    pop_age_male_55_59E,
    pop_age_male_60_61E,
    pop_age_male_62_64E,
    pop_age_male_65_66E,
    pop_age_male_67_69E,
    pop_age_male_70_74E,
    pop_age_male_75_79E,
    pop_age_male_80_84E,
    pop_age_male_85_plusE,
    pop_age_female_under5E,
    pop_age_female_5_9E,
    pop_age_female_10_14E,
    pop_age_female_15_17E,
    pop_age_female_18_19E,
    pop_age_female_20E,
    pop_age_female_21E,
    pop_age_female_22_24E,
    pop_age_female_25_29E,
    pop_age_female_30_34E,
    pop_age_female_35_39E,
    pop_age_female_40_44E,
    pop_age_female_45_49E,
    pop_age_female_50_54E,
    pop_age_female_55_59E,
    pop_age_female_60_61E,
    pop_age_female_62_64E,
    pop_age_female_65_66E,
    pop_age_female_67_69E,
    pop_age_female_70_74E,
    pop_age_female_75_79E,
    pop_age_female_80_84E,
    pop_age_female_85_plusE
  from silver.age_base
  where year = 2023
    and (
      (geo_level = 'cbsa' and geo_id = '33100')
      or (geo_level = 'US' and geo_id = '1')
    )
),
long_rows as (
  select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, 'Under 5' as age_bin, 'Male' as sex, pop_age_male_under5E as pop_value from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '5-9', 'Male', pop_age_male_5_9E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '10-14', 'Male', pop_age_male_10_14E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '15-17', 'Male', pop_age_male_15_17E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '18-19', 'Male', pop_age_male_18_19E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '20', 'Male', pop_age_male_20E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '21', 'Male', pop_age_male_21E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '22-24', 'Male', pop_age_male_22_24E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '25-29', 'Male', pop_age_male_25_29E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '30-34', 'Male', pop_age_male_30_34E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '35-39', 'Male', pop_age_male_35_39E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '40-44', 'Male', pop_age_male_40_44E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '45-49', 'Male', pop_age_male_45_49E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '50-54', 'Male', pop_age_male_50_54E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '55-59', 'Male', pop_age_male_55_59E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '60-61', 'Male', pop_age_male_60_61E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '62-64', 'Male', pop_age_male_62_64E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '65-66', 'Male', pop_age_male_65_66E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '67-69', 'Male', pop_age_male_67_69E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '70-74', 'Male', pop_age_male_70_74E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '75-79', 'Male', pop_age_male_75_79E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '80-84', 'Male', pop_age_male_80_84E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '85+', 'Male', pop_age_male_85_plusE from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, 'Under 5', 'Female', pop_age_female_under5E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '5-9', 'Female', pop_age_female_5_9E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '10-14', 'Female', pop_age_female_10_14E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '15-17', 'Female', pop_age_female_15_17E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '18-19', 'Female', pop_age_female_18_19E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '20', 'Female', pop_age_female_20E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '21', 'Female', pop_age_female_21E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '22-24', 'Female', pop_age_female_22_24E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '25-29', 'Female', pop_age_female_25_29E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '30-34', 'Female', pop_age_female_30_34E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '35-39', 'Female', pop_age_female_35_39E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '40-44', 'Female', pop_age_female_40_44E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '45-49', 'Female', pop_age_female_45_49E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '50-54', 'Female', pop_age_female_50_54E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '55-59', 'Female', pop_age_female_55_59E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '60-61', 'Female', pop_age_female_60_61E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '62-64', 'Female', pop_age_female_62_64E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '65-66', 'Female', pop_age_female_65_66E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '67-69', 'Female', pop_age_female_67_69E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '70-74', 'Female', pop_age_female_70_74E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '75-79', 'Female', pop_age_female_75_79E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '80-84', 'Female', pop_age_female_80_84E from base
  union all select geo_level, geo_id, geo_name, period, pop_total, benchmark_label, highlight_flag, facet_label, '85+', 'Female', pop_age_female_85_plusE from base
)
select
  'q023' as question_id,
  geo_level,
  geo_id,
  geo_name,
  period,
  age_bin,
  sex,
  pop_value,
  pop_total,
  case when pop_total > 0 then pop_value / pop_total else null end as pop_share,
  benchmark_label,
  highlight_flag,
  facet_label,
  'ACS age-sex population profile via silver.age_base' as source,
  '2023' as vintage,
  'Miami-Fort Lauderdale-West Palm Beach, FL compared with the United States using consistent age-sex bins.' as note
from long_rows
where pop_value is not null
order by highlight_flag desc, sex, age_bin;
