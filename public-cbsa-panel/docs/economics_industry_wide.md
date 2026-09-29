# `economics_industry_wide`

Annual CBSA employment composition from ACS and county-derived real GDP measures from BEA.

| Property | Value |
| --- | --- |
| Grain | One row per CBSA-year |
| Primary key | `geo_level`, `geo_id`, `year` |
| Years | 2012–2024 |
| Table coverage | 928 CBSAs in 2012–2021; 935 in 2022–2024 |
| Required values | All ACS fields are complete within table rows |

All share fields are proportions. BEA fields are optional: use their non-null coverage, not the
table row count, as the denominator for analysis.

| Column | Type | Definition and upstream variable | Null behavior |
| --- | --- | --- | --- |
| `geo_level` | text | Geography level; always `cbsa`. | Never null. |
| `geo_id` | text | Five-digit CBSA code. | Never null. |
| `geo_name` | text | CBSA name. | Never null. |
| `year` | integer | ACS five-year end year and BEA annual year. | Never null. |
| `acs_ind_total_emp` | number | ACS 5-year C24030 `C24030_001`: civilian employed population age 16+. | Never null. |
| `pct_acs_ind_manufacturing` | number | `(C24030_007 + C24030_034) / C24030_001`. | Never null. |
| `pct_acs_ind_professional` | number | `(C24030_017 + C24030_044) / C24030_001`. | Never null. |
| `pct_acs_ind_educ_health` | number | `(C24030_021 + C24030_048) / C24030_001`. | Never null. |
| `pct_acs_ind_arts_accomm_food` | number | `(C24030_024 + C24030_051) / C24030_001`. | Never null. |
| `acs_industry_concentration_hhi` | number | Sum of squared shares over the full ACS industry family listed in [Methodology](../METHODOLOGY.md). | Never null. |
| `bea_real_gdp_total` | number | BEA CAGDP9 line 1, real GDP in chained dollars, summed across member counties. | Null for 15 CBSAs annually. |
| `pct_bea_real_gdp_manufacturing` | number | BEA CAGDP9 line 12 divided by line 1 after county aggregation. | Null where either required component is unavailable; 788–840 CBSAs annually. |
| `pct_bea_real_gdp_professional` | number | BEA CAGDP9 lines 60, 64, and 65 summed, then divided by line 1 after county aggregation. | Null where any required component is unavailable; 334–471 CBSAs annually. |
| `pct_bea_real_gdp_edu_health` | number | BEA CAGDP9 line 68 divided by line 1 after county aggregation. | Null where either required component is unavailable; 671–801 CBSAs annually. |

`pct_bea_real_gdp_professional` and `pct_bea_real_gdp_edu_health` are released for transparent
reuse, but are not appropriate headline fields until their sparse coverage receives the planned
review. BEA GDP industry HHI is not in v2026.1.

```sql
SELECT year,
       count(*) FILTER (WHERE pct_bea_real_gdp_professional IS NOT NULL) AS professional_coverage
FROM economics_industry_wide
GROUP BY year
ORDER BY year;
```
