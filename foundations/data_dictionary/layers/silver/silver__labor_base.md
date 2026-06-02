# Data Dictionary: silver.labor_base

## Overview
- **Table**: `silver.labor_base`
- **Purpose**: Silver labor table (`base` type).
- **Row count**: 1,020,930
- **KPI applicability**: KPI table (or has KPI dictionary entries).

## Grain & Keys
- **Declared grain (inferred)**: One row per `geo_level + geo_id + geo_name + year`.
- **Primary key candidate (recommended)**: (`geo_level`, `geo_id`, `geo_name`, `year`)
  - `geo_level + geo_id + geo_name + year` => rows=1020930, distinct=1020930, duplicates=0
  - `geo_level + geo_id + year` => rows=1020930, distinct=1020930, duplicates=0
  - `geo_id + year` => rows=1020930, distinct=998787, duplicates=22143
  - `geo_level` => rows=1020930, distinct=9, duplicates=1020921
- **Time coverage**: `year` min=2012, max=2024
- **Geo coverage**: distinct_geo_levels=9; distinct_geo_id=115976

## Columns

| Column | DuckDB type | Null % | Distinct | Range / Length | Top values (count) | Definition |
|---|---|---:|---:|---|---|---|
| `geo_level` | `VARCHAR` | 0.0000 | 9 | len 2-8 | zcta (433172); place (397094); tract (135851); county (41870); cbsa (12085) | Geographic level (US, region, division, state, county, place, zcta, tract, cbsa) |
| `geo_id` | `VARCHAR` | 0.0000 | 115976 | len 1-11 | 1 (39); 2 (26); 3 (26); 4 (26); 01001 (25) | Geographic identifier for the row |
| `geo_name` | `VARCHAR` | 0.0000 | 97125 | len 4-66 | Alexandria city, Virginia (26); Baltimore city, Maryland (26); Bristol city, Virginia (26); Buena Vista city, Virginia (26); Carson City, Nevada (26) | Geographic name (from ACS NAME) |
| `year` | `INTEGER` | 0.0000 | 13 | min 2012, max 2024 | 2024 (82276); 2023 (82271); 2022 (82134); 2021 (81848); 2020 (81194) | Observation year or period year for the row. |
| `pop_16plusE` | `DOUBLE` | 0.0069 | 70459 | min 0, max 270181640 | 0.0 (11027); 65.0 (746); 80.0 (741); 77.0 (739); 47.0 (734) | ACS 2024 Employment Status for the Population 16 Years and Over [B23025_001]: Total: (estimate). |
| `in_labor_forceE` | `DOUBLE` | 0.0069 | 54423 | min 0, max 171493280 | 0.0 (17145); 53.0 (1241); 49.0 (1240); 38.0 (1237); 46.0 (1234) | ACS 2024 Employment Status for the Population 16 Years and Over [B23025_002]: Total:, In labor force: (estimate). |
| `in_lf_civilianE` | `DOUBLE` | 0.0069 | 54223 | min 0, max 170199520 | 0.0 (17517); 53.0 (1253); 38.0 (1241); 49.0 (1239); 30.0 (1235) | ACS 2024 Employment Status for the Population 16 Years and Over [B23025_003]: Total:, In labor force:, Civilian labor force: (estimate). |
| `in_lf_armed_forcesE` | `DOUBLE` | 0.0069 | 52125 | min 0, max 161297160 | 0.0 (18242); 46.0 (1392); 27.0 (1364); 28.0 (1363); 41.0 (1337) | ACS 2024 Employment Status for the Population 16 Years and Over [B23025_004]: Total:, In labor force:, Civilian labor force:, Employed (estimate). |
| `not_in_labor_forceE` | `DOUBLE` | 0.0069 | 13916 | min 0, max 15249189 | 0.0 (128203); 2.0 (13467); 3.0 (12219); 4.0 (11942); 5.0 (11384) | ACS 2024 Employment Status for the Population 16 Years and Over [B23025_005]: Total:, In labor force:, Civilian labor force:, Unemployed (estimate). |
| `employedE` | `DOUBLE` | 0.0069 | 39939 | min 0, max 98688351 | 0.0 (17315); 35.0 (1752); 39.0 (1740); 28.0 (1731); 34.0 (1718) | ACS 2024 Employment Status for the Population 16 Years and Over [B23025_007]: Total:, Not in labor force (estimate). |
| `occ_totalE` | `DOUBLE` | 0.0069 | 52125 | min 0, max 161297160 | 0.0 (18242); 46.0 (1392); 27.0 (1364); 28.0 (1363); 41.0 (1337) | ACS 2024 Sex by Occupation for the Civilian Employed Population 16 Years and Over [C24010_001]: Total: (estimate). |
| `occ_male_mgmt_business_sci_artsE` | `DOUBLE` | 0.0069 | 21637 | min 0, max 32610799 | 0.0 (75799); 2.0 (8496); 5.0 (8379); 7.0 (8317); 6.0 (8293) | ACS 2024 Sex by Occupation for the Civilian Employed Population 16 Years and Over [C24010_003]: Total:, Male:, Management, business, science, and arts occupations: (estimate). |
| `occ_male_serviceE` | `DOUBLE` | 0.0069 | 14353 | min 0, max 11935283 | 0.0 (115341); 2.0 (13466); 4.0 (12112); 3.0 (11783); 6.0 (11601) | ACS 2024 Sex by Occupation for the Civilian Employed Population 16 Years and Over [C24010_019]: Total:, Male:, Service occupations: (estimate). |
| `occ_male_sales_officeE` | `DOUBLE` | 0.0069 | 14789 | min 0, max 13522354 | 0.0 (122933); 2.0 (13578); 3.0 (12256); 4.0 (12026); 5.0 (11945) | ACS 2024 Sex by Occupation for the Civilian Employed Population 16 Years and Over [C24010_027]: Total:, Male:, Sales and office occupations: (estimate). |
| `occ_male_nat_resources_const_maintE` | `DOUBLE` | 0.0069 | 14853 | min 0, max 13084961 | 0.0 (76266); 8.0 (8458); 9.0 (8354); 10.0 (8223); 6.0 (7950) | ACS 2024 Sex by Occupation for the Civilian Employed Population 16 Years and Over [C24010_030]: Total:, Male:, Natural resources, construction, and maintenance occupations: (estimate). |
| `occ_male_prod_transp_materialE` | `DOUBLE` | 0.0069 | 16183 | min 0, max 15860730 | 0.0 (80666); 9.0 (7955); 8.0 (7908); 6.0 (7708); 10.0 (7697) | ACS 2024 Sex by Occupation for the Civilian Employed Population 16 Years and Over [C24010_034]: Total:, Male:, Production, transportation, and material moving occupations: (estimate). |
| `occ_female_mgmt_business_sci_artsE` | `DOUBLE` | 0.0069 | 22480 | min 0, max 36177870 | 0.0 (58473); 9.0 (6939); 8.0 (6893); 6.0 (6809); 5.0 (6728) | ACS 2024 Sex by Occupation for the Civilian Employed Population 16 Years and Over [C24010_039]: Total:, Female:, Management, business, science, and arts occupations: (estimate). |
| `occ_female_serviceE` | `DOUBLE` | 0.0069 | 16246 | min 0, max 15554218 | 0.0 (83230); 8.0 (8681); 6.0 (8563); 9.0 (8543); 7.0 (8504) | ACS 2024 Sex by Occupation for the Civilian Employed Population 16 Years and Over [C24010_055]: Total:, Female:, Service occupations: (estimate). |
| `occ_female_sales_officeE` | `DOUBLE` | 0.0069 | 18838 | min 0, max 22225028 | 0.0 (66497); 8.0 (7530); 9.0 (7407); 6.0 (7325); 10.0 (7314) | ACS 2024 Sex by Occupation for the Civilian Employed Population 16 Years and Over [C24010_063]: Total:, Female:, Sales and office occupations: (estimate). |
| `occ_female_nat_resources_const_maintE` | `DOUBLE` | 0.0069 | 3707 | min 0, max 713167 | 0.0 (565565); 2.0 (20380); 3.0 (19248); 4.0 (16251); 5.0 (14904) | ACS 2024 Sex by Occupation for the Civilian Employed Population 16 Years and Over [C24010_066]: Total:, Female:, Natural resources, construction, and maintenance occupations: (estimate). |
| `occ_female_prod_transp_materialE` | `DOUBLE` | 0.0069 | 9212 | min 0, max 5109590 | 0.0 (204849); 2.0 (18699); 3.0 (16903); 4.0 (16601); 5.0 (15412) | ACS 2024 Sex by Occupation for the Civilian Employed Population 16 Years and Over [C24010_070]: Total:, Female:, Production, transportation, and material moving occupations: (estimate). |
| `ind_totalE` | `DOUBLE` | 0.0069 | 52125 | min 0, max 161297160 | 0.0 (18242); 46.0 (1392); 27.0 (1364); 28.0 (1363); 41.0 (1337) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_001]: Total: (estimate). |
| `ind_male_ag_miningE` | `DOUBLE` | 0.0069 | 5798 | min 0, max 2319970 | 0.0 (326842); 2.0 (18562); 3.0 (16389); 4.0 (16259); 6.0 (15802) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_003]: Total:, Male:, Agriculture, forestry, fishing and hunting, and mining: (estimate). |
| `ind_male_constructionE` | `DOUBLE` | 0.0069 | 12496 | min 0, max 9914382 | 0.0 (116058); 4.0 (11584); 2.0 (11412); 6.0 (11412); 5.0 (11323) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_006]: Total:, Male:, Construction (estimate). |
| `ind_male_manufacturingE` | `DOUBLE` | 0.0069 | 13984 | min 0, max 11277067 | 0.0 (130060); 2.0 (10078); 6.0 (9915); 4.0 (9811); 5.0 (9740) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_007]: Total:, Male:, Manufacturing (estimate). |
| `ind_male_wholesaleE` | `DOUBLE` | 0.0069 | 7412 | min 0, max 2838306 | 0.0 (300931); 2.0 (23874); 3.0 (20258); 4.0 (18337); 5.0 (17173) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_008]: Total:, Male:, Wholesale trade (estimate). |
| `ind_male_retailE` | `DOUBLE` | 0.0069 | 12648 | min 0, max 9117233 | 0.0 (140642); 2.0 (14745); 4.0 (13290); 3.0 (13160); 5.0 (12951) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_009]: Total:, Male:, Retail trade (estimate). |
| `ind_male_transport_utilE` | `DOUBLE` | 0.0069 | 10369 | min 0, max 7115521 | 0.0 (157949); 2.0 (16475); 3.0 (15074); 4.0 (15066); 5.0 (14747) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_010]: Total:, Male:, Transportation and warehousing, and utilities: (estimate). |
| `ind_male_informationE` | `DOUBLE` | 0.0069 | 6184 | min 0, max 1879235 | 0.0 (463221); 2.0 (21461); 3.0 (19433); 4.0 (16328); 5.0 (14475) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_013]: Total:, Male:, Information (estimate). |
| `ind_male_finance_realE` | `DOUBLE` | 0.0069 | 9205 | min 0, max 5059484 | 0.0 (314338); 2.0 (22842); 3.0 (19831); 4.0 (17144); 5.0 (15675) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_014]: Total:, Male:, Finance and insurance, and real estate, and rental and leasing: (estimate). |
| `ind_male_professionalE` | `DOUBLE` | 0.0069 | 13135 | min 0, max 11554698 | 0.0 (182233); 2.0 (20450); 3.0 (16833); 4.0 (15785); 5.0 (14559) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_017]: Total:, Male:, Professional, scientific, and management, and administrative, and waste management services: (estimate). |
| `ind_male_educ_healthE` | `DOUBLE` | 0.0069 | 13040 | min 0, max 9957612 | 0.0 (153898); 2.0 (17994); 3.0 (14802); 4.0 (14597); 5.0 (13682) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_021]: Total:, Male:, Educational services, and health care and social assistance: (estimate). |
| `ind_male_arts_accomm_foodE` | `DOUBLE` | 0.0069 | 11426 | min 0, max 7269634 | 0.0 (213452); 2.0 (20473); 3.0 (17524); 4.0 (16087); 5.0 (14785) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_024]: Total:, Male:, Arts, entertainment, and recreation, and accommodation and food services: (estimate). |
| `ind_male_otherE` | `DOUBLE` | 0.0069 | 8104 | min 0, max 3548671 | 0.0 (228256); 2.0 (23933); 3.0 (20067); 4.0 (18851); 5.0 (17442) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_027]: Total:, Male:, Other services, except public administration (estimate). |
| `ind_male_public_adminE` | `DOUBLE` | 0.0069 | 8922 | min 0, max 4151356 | 0.0 (227090); 2.0 (22862); 3.0 (19618); 4.0 (17598); 5.0 (16792) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_028]: Total:, Male:, Public administration (estimate). |
| `ind_female_ag_miningE` | `DOUBLE` | 0.0069 | 3227 | min 0, max 557221 | 0.0 (610820); 2.0 (19539); 3.0 (18120); 4.0 (15577); 5.0 (14971) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_030]: Total:, Female:, Agriculture, forestry, fishing and hunting, and mining: (estimate). |
| `ind_female_constructionE` | `DOUBLE` | 0.0069 | 4661 | min 0, max 1252658 | 0.0 (489633); 2.0 (21979); 3.0 (20004); 4.0 (16766); 5.0 (15360) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_033]: Total:, Female:, Construction (estimate). |
| `ind_female_manufacturingE` | `DOUBLE` | 0.0069 | 9040 | min 0, max 4687740 | 0.0 (232467); 2.0 (19062); 3.0 (16548); 4.0 (15860); 5.0 (15359) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_034]: Total:, Female:, Manufacturing (estimate). |
| `ind_female_wholesaleE` | `DOUBLE` | 0.0069 | 5008 | min 0, max 1206753 | 0.0 (486366); 2.0 (22885); 3.0 (20622); 4.0 (16773); 5.0 (15656) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_035]: Total:, Female:, Wholesale trade (estimate). |
| `ind_female_retailE` | `DOUBLE` | 0.0069 | 12396 | min 0, max 8455763 | 0.0 (127976); 2.0 (13466); 4.0 (12618); 3.0 (12589); 5.0 (12317) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_036]: Total:, Female:, Retail trade (estimate). |
| `ind_female_transport_utilE` | `DOUBLE` | 0.0069 | 6389 | min 0, max 2453246 | 0.0 (338656); 2.0 (28476); 3.0 (24707); 4.0 (21595); 5.0 (19751) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_037]: Total:, Female:, Transportation and warehousing, and utilities: (estimate). |
| `ind_female_informationE` | `DOUBLE` | 0.0069 | 5239 | min 0, max 1349388 | 0.0 (483559); 2.0 (23598); 3.0 (21178); 4.0 (17765); 5.0 (16023) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_040]: Total:, Female:, Information (estimate). |
| `ind_female_finance_realE` | `DOUBLE` | 0.0069 | 10039 | min 0, max 5723675 | 0.0 (214686); 2.0 (21398); 3.0 (18124); 4.0 (17080); 5.0 (15802) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_041]: Total:, Female:, Finance and insurance, and real estate, and rental and leasing: (estimate). |
| `ind_female_professionalE` | `DOUBLE` | 0.0069 | 11334 | min 0, max 8727752 | 0.0 (200335); 2.0 (22310); 3.0 (18709); 4.0 (17021); 5.0 (15581) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_044]: Total:, Female:, Professional, scientific, and management, and administrative, and waste management services: (estimate). |
| `ind_female_educ_healthE` | `DOUBLE` | 0.0069 | 20957 | min 0, max 27956051 | 0.0 (58465); 8.0 (6532); 9.0 (6433); 6.0 (6279); 10.0 (6244) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_048]: Total:, Female:, Educational services, and health care and social assistance: (estimate). |
| `ind_female_arts_accomm_foodE` | `DOUBLE` | 0.0069 | 11730 | min 0, max 7692665 | 0.0 (162200); 2.0 (17352); 3.0 (15505); 4.0 (14665); 5.0 (14053) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_051]: Total:, Female:, Arts, entertainment, and recreation, and accommodation and food services: (estimate). |
| `ind_female_otherE` | `DOUBLE` | 0.0069 | 8647 | min 0, max 4042521 | 0.0 (233826); 2.0 (24911); 3.0 (20238); 4.0 (18633); 5.0 (17170) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_054]: Total:, Female:, Other services, except public administration (estimate). |
| `ind_female_public_adminE` | `DOUBLE` | 0.0069 | 8022 | min 0, max 3472887 | 0.0 (242209); 2.0 (25029); 3.0 (21238); 4.0 (19986); 5.0 (18382) | ACS 2024 Sex by Industry for the Civilian Employed Population 16 Years and Over [C24030_055]: Total:, Female:, Public administration (estimate). |
## Data Quality Notes
- Columns with non-zero null rates: pop_16plusE=0.0069%, in_labor_forceE=0.0069%, in_lf_civilianE=0.0069%, in_lf_armed_forcesE=0.0069%, not_in_labor_forceE=0.0069%, employedE=0.0069%, occ_totalE=0.0069%, occ_male_mgmt_business_sci_artsE=0.0069%, occ_male_serviceE=0.0069%, occ_male_sales_officeE=0.0069% ...
- Key uniqueness check for recommended PK (`geo_level + geo_id + geo_name + year`) returns zero duplicates in current snapshot.
- Primary/foreign keys are not enforced as DB constraints in current pipeline.

## Lineage
1. **Creation/write references**:
   - `scripts/etl/silver/acs_labor_silver.R:267:DBI::dbWriteTable(con, DBI::Id(schema="silver", table="labor_base"),`

## Known Gaps / To-Dos
- Validate and harden grain/PK contracts with automated DQ checks.
- Add explicit business definitions for columns flagged as needs confirmation.
- Add enforced lineage metadata entries in `silver.metadata_topics` / `silver.metadata_vars` where missing.

## How To Extend (Next Table)
1. Run table-existence and row-count checks from DuckDB.
2. Pull schema from `information_schema.columns` and compute per-column profile metrics.
3. Run uniqueness checks for plausible key combinations.
4. Locate ETL lineage with `rg -n "<table_name>|dbWriteTable|CREATE TABLE" scripts notebooks documents`.
5. Write `data_dictionary/layers/<layer>/<schema>__<table>.md` and `.yml` artifacts.
6. Mark inferred statements explicitly and set `needs_confirmation` where definitions are unclear.
