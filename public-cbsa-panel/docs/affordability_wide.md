# `affordability_wide`

Annual CBSA housing and income measures from ACS, plus county-derived HUD two-bedroom FMR.

| Property | Value |
| --- | --- |
| Grain | One row per CBSA-year |
| Primary key | `geo_level`, `geo_id`, `year` |
| Years | 2012–2024 |
| Table coverage | 928 CBSAs in 2012–2021; 935 in 2022–2024 |

ACS monetary fields are current-dollar estimates from their respective five-year windows. HUD
FMR is a fiscal-year measure and is population-weighted across CBSA member counties.

| Column | Type | Definition and upstream variable | Null behavior |
| --- | --- | --- | --- |
| `geo_level` | text | Geography level; always `cbsa`. | Never null. |
| `geo_id` | text | Five-digit CBSA code. | Never null. |
| `geo_name` | text | CBSA name. | Never null. |
| `year` | integer | ACS five-year end year; HUD fiscal-year label for FMR fields. | Never null. |
| `median_gross_rent` | number | ACS 5-year B25064 `B25064_001`; monthly dollars. | Never null. |
| `annualized_median_rent` | number | `12 × median_gross_rent`; annual dollars. | Never null. |
| `median_home_value` | number | ACS 5-year B25077 `B25077_001`; dollars. | Never null. |
| `median_hh_income` | number | ACS 5-year B19013 `B19013_001`; dollars. | Never null. |
| `rent_to_income` | number | `(12 × median_gross_rent) / median_hh_income`. | Never null. |
| `value_to_income` | number | `median_home_value / median_hh_income`. Uses ACS value, not Zillow. | Never null. |
| `hud_fmr_2br` | number | HUD two-bedroom Fair Market Rent; population-weighted across member counties; monthly dollars. | Null for seven CBSAs annually. |
| `hud_fmr_2br_gap_vs_acs_median_rent` | number | `hud_fmr_2br − median_gross_rent`; monthly dollars. | Null when FMR is null; 928 CBSAs annually. |

FMR is a policy rent benchmark, not a local median rent estimate. The gap compares it with the
ACS median gross rent, which has a different source period and meaning.

```sql
SELECT geo_name, annualized_median_rent, rent_to_income
FROM affordability_wide
WHERE year = 2024
ORDER BY rent_to_income DESC
LIMIT 10;
```
