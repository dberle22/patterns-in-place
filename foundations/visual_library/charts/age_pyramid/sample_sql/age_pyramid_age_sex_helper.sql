-- Age Pyramid SQL helper.
--
-- Usage:
--   1. Define a `selected_rows` CTE with the age_base columns needed below.
--   2. Include the `{{AGE_PYRAMID_HELPER}}` marker after `selected_rows`.
--   3. Select from the `standardized` CTE and aggregate to the chart contract.
--
-- Required selected_rows fields:
--   question_id, geo_level, geo_id, geo_name, period, pop_total, facet_label,
--   benchmark_label, highlight_flag, note, and the wide ACS age-by-sex columns
--   matching ^pop_age_(male|female)_.*E$.
--
-- This helper deliberately keeps the simplified age-bin scheme local to the
-- age pyramid chart samples rather than creating a new DuckDB table.
, long_age AS (
  SELECT
    question_id, geo_level, geo_id, geo_name, period, pop_total, facet_label,
    benchmark_label, highlight_flag, note, sex_age_col, pop_value
  FROM selected_rows
  UNPIVOT (pop_value FOR sex_age_col IN (COLUMNS('^pop_age_(male|female)_.*E$')))
),
standardized AS (
  SELECT
    question_id, geo_level, geo_id, geo_name, period, pop_total, facet_label,
    benchmark_label, highlight_flag,
    CASE WHEN sex_age_col LIKE 'pop_age_male_%' THEN 'Male' ELSE 'Female' END AS sex,
    CASE
      WHEN sex_age_col LIKE '%under5E' THEN '0-4'
      WHEN sex_age_col LIKE '%_5_9E' OR sex_age_col LIKE '%_10_14E' THEN '5-14'
      WHEN sex_age_col LIKE '%_15_17E' THEN '15-17'
      WHEN sex_age_col LIKE '%_18_19E' OR sex_age_col LIKE '%_20E' OR sex_age_col LIKE '%_21E' OR sex_age_col LIKE '%_22_24E' THEN '18-24'
      WHEN sex_age_col LIKE '%_25_29E' OR sex_age_col LIKE '%_30_34E' THEN '25-34'
      WHEN sex_age_col LIKE '%_35_39E' OR sex_age_col LIKE '%_40_44E' THEN '35-44'
      WHEN sex_age_col LIKE '%_45_49E' OR sex_age_col LIKE '%_50_54E' THEN '45-54'
      WHEN sex_age_col LIKE '%_55_59E' OR sex_age_col LIKE '%_60_61E' OR sex_age_col LIKE '%_62_64E' THEN '55-64'
      WHEN sex_age_col LIKE '%_65_66E' OR sex_age_col LIKE '%_67_69E' OR sex_age_col LIKE '%_70_74E' THEN '65-74'
      WHEN sex_age_col LIKE '%_75_79E' OR sex_age_col LIKE '%_80_84E' THEN '75-84'
      ELSE '85+'
    END AS age_bin,
    pop_value,
    note
  FROM long_age
)
