# `cbsa_county_crosswalk`

Static current-vintage county-to-CBSA membership lookup.

| Property | Value |
| --- | --- |
| Grain | One row per current county-to-CBSA membership |
| Primary key | `county_geoid`, `cbsa_code` |
| Vintage | OMB 2023 |
| Coverage | 1,915 memberships, 1,915 counties, 935 CBSAs |
| Time | No year field; not a historical delineation series |

| Column | Type | Definition and upstream field | Null behavior |
| --- | --- | --- | --- |
| `county_geoid` | text | Five-digit state-and-county FIPS from OMB state and county codes. | Never null. |
| `county_name` | text | OMB county or county-equivalent name. | Never null. |
| `state_fips` | text | Two-digit OMB state FIPS. | Never null. |
| `state_abbr` | text | Census state-reference abbreviation joined to the member county. | Never null. |
| `state_name` | text | OMB state name. | Never null. |
| `cbsa_code` | text | Five-digit OMB CBSA code. | Never null. |
| `cbsa_name` | text | Official OMB CBSA title. | Never null. |
| `cbsa_type` | text | Official metropolitan or micropolitan statistical-area type. | Never null. |
| `cbsa_type_short` | text | Convenience mapping of `cbsa_type` to `metro` or `micro`. | Never null. |
| `county_role` | text | OMB central/core or outlying county designation. | Never null. |
| `primary_state_abbr` | text | First state suffix in the official CBSA title, resolved to a member-state abbreviation. | Never null. |
| `primary_state_fips` | text | FIPS for `primary_state_abbr`. | Never null. |
| `crosswalk_vintage` | integer | Static delineation vintage: `2023`. | Never null. |

The primary state is a deterministic display and grouping convenience. Use county rows when
you need all states represented by a multistate CBSA.

```sql
SELECT cbsa_code, cbsa_name, count(*) AS member_counties
FROM cbsa_county_crosswalk
GROUP BY 1, 2
ORDER BY member_counties DESC
LIMIT 10;
```
