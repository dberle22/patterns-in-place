# Data Dictionary: silver.disability_base

## Overview
- **Table**: `silver.disability_base`
- **Purpose**: Silver disability base table (`base` type).
- **Row count**: 1,891,571
- **KPI applicability**: Base/source-aligned Silver table.

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + geo_name + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `geo_name`, `year`)
  - `geo_level + geo_id + geo_name + year` => rows=1891571, distinct=1891571, duplicates=0
  - `geo_level + geo_id + year` => rows=1891571, distinct=1891571, duplicates=0
  - `geo_id + year` => rows=1891571, distinct=1869428, duplicates=22143
  - `geo_level` => rows=1891571, distinct=9, duplicates=1891562
- **Time coverage**: `year` min=2012, max=2024
- **Geo coverage**: distinct_geo_levels=9; distinct_geo_id=198456

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 9 | len 2-8 | tract (1006492); zcta (433172); place (397094); county (41870); cbsa (12085) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 198,456 | len 1-11 | 1 (39); 2 (26); 3 (26); 4 (26); 01001 (25) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 251,188 | len 4-81 | Alexandria city, Virginia (26); Baltimore city, Maryland (26); Bristol city, Virginia (26); Buena Vista city, Virginia (26); Carson City, Nevada (26) | Geographic name (from ACS NAME) |
| `year` | `INTEGER` | 0.0000 | 13 | min 2012, max 2024 | 2024 (154726); 2023 (154720); 2022 (154598); 2021 (154311); 2020 (153657) | Observation year or period year for the row. |
| `disability_totalE` | `DOUBLE` | 0.0000 | 80,081 | min 0, max 329980753 | 0.0 (21493); 61.0 (627); 74.0 (623); 64.0 (614); 69.0 (609) | Total civilian noninstitutionalized population in the disability-status universe. |
| `disability_male_totalE` | `DOUBLE` | 0.0000 | 52,594 | min 0, max 162271028 | 0.0 (23807); 42.0 (1180); 32.0 (1174); 44.0 (1171); 41.0 (1170) | Male civilian noninstitutionalized population in the disability-status universe. |
| `disability_male_under_5_totalE` | `DOUBLE` | 0.0000 | 13,303 | min 0, max 10289512 | 0.0 (173223); 8.0 (12026); 6.0 (12000); 5.0 (11827); 4.0 (11762) | Male under 5 in the disability-status universe. |
| `disability_male_under_5_with_disabilityE` | `DOUBLE` | 0.0000 | 1,503 | min 0, max 88162 | 0.0 (1733511); 3.0 (6091); 9.0 (6079); 10.0 (6037); 8.0 (5986) | Male under 5 with a disability. |
| `disability_male_under_5_no_disabilityE` | `DOUBLE` | 0.0000 | 13,274 | min 0, max 10201864 | 0.0 (174187); 6.0 (12144); 8.0 (12105); 5.0 (11873); 4.0 (11797) | Male under 5 without a disability. |
| `disability_male_5_17_totalE` | `DOUBLE` | 0.0000 | 21,424 | min 0, max 27972329 | 0.0 (87798); 9.0 (6096); 12.0 (5840); 8.0 (5829); 6.0 (5810) | Male 5 to 17 in the disability-status universe. |
| `disability_male_5_17_with_disabilityE` | `DOUBLE` | 0.0000 | 6,243 | min 0, max 2107800 | 0.0 (620963); 9.0 (31902); 8.0 (31724); 10.0 (31608); 7.0 (30275) | Male 5 to 17 with a disability. |
| `disability_male_5_17_no_disabilityE` | `DOUBLE` | 0.0000 | 20,657 | min 0, max 26003111 | 0.0 (92074); 9.0 (6507); 12.0 (6280); 8.0 (6237); 6.0 (6209) | Male 5 to 17 without a disability. |
| `disability_male_18_34_totalE` | `DOUBLE` | 0.0000 | 25,258 | min 0, max 37601126 | 0.0 (68088); 10.0 (5212); 8.0 (5183); 9.0 (5170); 12.0 (5099) | Male 18 to 34 in the disability-status universe. |
| `disability_male_18_34_with_disabilityE` | `DOUBLE` | 0.0000 | 7,189 | min 0, max 3092051 | 0.0 (476076); 2.0 (30792); 10.0 (29290); 9.0 (29063); 8.0 (28974) | Male 18 to 34 with a disability. |
| `disability_male_18_34_no_disabilityE` | `DOUBLE` | 0.0000 | 24,375 | min 0, max 34750905 | 0.0 (72483); 10.0 (5679); 8.0 (5583); 9.0 (5544); 11.0 (5480) | Male 18 to 34 without a disability. |
| `disability_male_35_64_totalE` | `DOUBLE` | 0.0000 | 31,059 | min 0, max 61906135 | 0.0 (36598); 12.0 (2911); 16.0 (2897); 20.0 (2856); 21.0 (2854) | Male 35 to 64 in the disability-status universe. |
| `disability_male_35_64_with_disabilityE` | `DOUBLE` | 0.0000 | 11,836 | min 0, max 7715423 | 0.0 (130415); 9.0 (14864); 8.0 (14638); 10.0 (14445); 7.0 (14204) | Male 35 to 64 with a disability. |
| `disability_male_35_64_no_disabilityE` | `DOUBLE` | 0.0000 | 28,979 | min 0, max 54266253 | 0.0 (41925); 10.0 (3625); 12.0 (3496); 14.0 (3495); 9.0 (3489) | Male 35 to 64 without a disability. |
| `disability_male_65_74_totalE` | `DOUBLE` | 0.0000 | 14,832 | min 0, max 15826728 | 0.0 (78814); 8.0 (9838); 9.0 (9609); 10.0 (9518); 6.0 (9195) | Male 65 to 74 in the disability-status universe. |
| `disability_male_65_74_with_disabilityE` | `DOUBLE` | 0.0000 | 7,941 | min 0, max 3954473 | 0.0 (238261); 9.0 (28411); 8.0 (27855); 10.0 (27516); 7.0 (26270) | Male 65 to 74 with a disability. |
| `disability_male_65_74_no_disabilityE` | `DOUBLE` | 0.0000 | 12,840 | min 0, max 11872255 | 0.0 (107970); 8.0 (13346); 6.0 (13183); 9.0 (12958); 5.0 (12850) | Male 65 to 74 without a disability. |
| `disability_male_75_plus_totalE` | `DOUBLE` | 0.0000 | 11,886 | min 0, max 9638669 | 0.0 (125156); 9.0 (14639); 8.0 (14421); 10.0 (14350); 6.0 (14224) | Male 75 and older in the disability-status universe. |
| `disability_male_75_plus_with_disabilityE` | `DOUBLE` | 0.0000 | 8,376 | min 0, max 4375884 | 0.0 (232788); 9.0 (26158); 8.0 (25492); 10.0 (25179); 6.0 (24186) | Male 75 and older with a disability. |
| `disability_male_75_plus_no_disabilityE` | `DOUBLE` | 0.0000 | 8,893 | min 0, max 5262785 | 0.0 (235935); 9.0 (24398); 8.0 (24283); 10.0 (23687); 6.0 (23360) | Male 75 and older without a disability. |
| `disability_female_totalE` | `DOUBLE` | 0.0000 | 53,981 | min 0, max 167709725 | 0.0 (24132); 49.0 (1240); 43.0 (1227); 56.0 (1215); 31.0 (1198) | Female civilian noninstitutionalized population in the disability-status universe. |
| `disability_female_under_5_totalE` | `DOUBLE` | 0.0000 | 13,054 | min 0, max 9845628 | 0.0 (178949); 4.0 (12507); 6.0 (12412); 8.0 (12384); 10.0 (12183) | Female under 5 in the disability-status universe. |
| `disability_female_under_5_with_disabilityE` | `DOUBLE` | 0.0000 | 1,384 | min 0, max 73179 | 0.0 (1755197); 9.0 (5433); 3.0 (5376); 4.0 (5357); 8.0 (5343) | Female under 5 with a disability. |
| `disability_female_under_5_no_disabilityE` | `DOUBLE` | 0.0000 | 13,008 | min 0, max 9775911 | 0.0 (179761); 4.0 (12644); 6.0 (12475); 8.0 (12455); 10.0 (12303) | Female under 5 without a disability. |
| `disability_female_5_17_totalE` | `DOUBLE` | 0.0000 | 21,022 | min 0, max 26728050 | 0.0 (89328); 8.0 (6239); 9.0 (6077); 10.0 (6041); 7.0 (5843) | Female 5 to 17 in the disability-status universe. |
| `disability_female_5_17_with_disabilityE` | `DOUBLE` | 0.0000 | 4,938 | min 0, max 1341347 | 0.0 (852085); 8.0 (33143); 9.0 (32459); 10.0 (31552); 7.0 (31132) | Female 5 to 17 with a disability. |
| `disability_female_5_17_no_disabilityE` | `DOUBLE` | 0.0000 | 20,585 | min 0, max 25543083 | 0.0 (92090); 8.0 (6521); 9.0 (6285); 10.0 (6262); 7.0 (6125) | Female 5 to 17 without a disability. |
| `disability_female_18_34_totalE` | `DOUBLE` | 0.0000 | 25,398 | min 0, max 37339354 | 0.0 (69889); 9.0 (5547); 10.0 (5433); 12.0 (5408); 8.0 (5402) | Female 18 to 34 in the disability-status universe. |
| `disability_female_18_34_with_disabilityE` | `DOUBLE` | 0.0000 | 6,811 | min 0, max 2966420 | 0.0 (545191); 2.0 (31645); 9.0 (30933); 8.0 (30696); 10.0 (30470) | Female 18 to 34 with a disability. |
| `disability_female_18_34_no_disabilityE` | `DOUBLE` | 0.0000 | 24,628 | min 0, max 34768701 | 0.0 (73764); 9.0 (5869); 10.0 (5827); 8.0 (5705); 11.0 (5645) | Female 18 to 34 without a disability. |
| `disability_female_35_64_totalE` | `DOUBLE` | 0.0000 | 31,915 | min 0, max 63731772 | 0.0 (36442); 16.0 (2998); 15.0 (2991); 12.0 (2980); 18.0 (2954) | Female 35 to 64 in the disability-status universe. |
| `disability_female_35_64_with_disabilityE` | `DOUBLE` | 0.0000 | 12,149 | min 0, max 8122515 | 0.0 (134705); 8.0 (14714); 6.0 (14603); 9.0 (14589); 10.0 (14473) | Female 35 to 64 with a disability. |
| `disability_female_35_64_no_disabilityE` | `DOUBLE` | 0.0000 | 29,704 | min 0, max 55711491 | 0.0 (40920); 10.0 (3586); 13.0 (3575); 11.0 (3555); 12.0 (3536) | Female 35 to 64 without a disability. |
| `disability_female_65_74_totalE` | `DOUBLE` | 0.0000 | 15,801 | min 0, max 17851030 | 0.0 (77318); 8.0 (9417); 9.0 (9126); 7.0 (8812); 10.0 (8758) | Female 65 to 74 in the disability-status universe. |
| `disability_female_65_74_with_disabilityE` | `DOUBLE` | 0.0000 | 8,152 | min 0, max 4116578 | 0.0 (248323); 9.0 (27996); 8.0 (27439); 10.0 (26796); 2.0 (25935) | Female 65 to 74 with a disability. |
| `disability_female_65_74_no_disabilityE` | `DOUBLE` | 0.0000 | 13,816 | min 0, max 13734452 | 0.0 (98370); 8.0 (11961); 9.0 (11628); 6.0 (11554); 7.0 (11425) | Female 65 to 74 without a disability. |
| `disability_female_75_plus_totalE` | `DOUBLE` | 0.0000 | 14,058 | min 0, max 12923272 | 0.0 (104594); 9.0 (11598); 8.0 (11475); 10.0 (11234); 6.0 (11069) | Female 75 and older in the disability-status universe. |
| `disability_female_75_plus_with_disabilityE` | `DOUBLE` | 0.0000 | 10,202 | min 0, max 6040839 | 0.0 (180639); 9.0 (19147); 8.0 (19090); 2.0 (18694); 6.0 (18448) | Female 75 and older with a disability. |
| `disability_female_75_plus_no_disabilityE` | `DOUBLE` | 0.0000 | 10,211 | min 0, max 6882433 | 0.0 (186390); 9.0 (19963); 6.0 (19398); 8.0 (19368); 10.0 (19041) | Female 75 and older without a disability. |
## Data Quality Notes
- No columns with non-zero null rates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `foundations/etl/silver/acs_disability_silver.R writes silver.disability_base from staging.acs_disability_* with CBSA rebasing from county data via silver.xwalk_cbsa_county.`

## Known Gaps / To-Dos
- Validate and harden grain/PK contracts with automated DQ checks.
- Re-run the landed profile after major ACS topic changes and sync both this `.md` file and the companion `.yml` artifact.
