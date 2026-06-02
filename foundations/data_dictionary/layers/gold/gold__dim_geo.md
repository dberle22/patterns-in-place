# Data Dictionary: gold.dim_geo

## Overview
- **Table**: `gold.dim_geo`
- **Purpose**: Canonical serving-layer geography dimension for chatbot joins, dashboard filters, hierarchy lookups, and metro-vs-micro classification.
- **Row grain**: One row per `geo_level + geo_id`.
- **First-release coverage**: `us`, `region`, `division`, `state`, `cbsa`, `county`, and `tract`

## Why This Table Exists

`gold.dim_geo` centralizes geography metadata that was previously scattered across multiple silver crosswalks:

- `silver.xwalk_state_region`
- `silver.xwalk_county_state`
- `silver.xwalk_cbsa_county`

The main immediate use case is clean metro-vs-micro identification. CBSA rows expose:

- `cbsa_type`
- `cbsa_type_short`
- `is_metro`
- `is_micro`

This lets downstream logic answer prompts like “metros” without inferring from raw names or repeating xwalk joins.

## Grain & Keys

- **Declared grain**: One row per `geo_level + geo_id`
- **Primary key candidate**: (`geo_level`, `geo_id`)
- **Time coverage**: none; this is a non-temporal dimension table

## Modeling Notes

- The table is intentionally sparse by design. Level-specific fields are null when they do not apply.
- A `state` row has null `cbsa_*` and `county_*` fields.
- A `cbsa` row may have null `state_*`, `region_*`, or `division_*` fields when it spans multiple parents.
- A `county` row includes `parent_cbsa_code` only when that county belongs to a CBSA.
- A `tract` row rolls up exactly to a county through `silver.xwalk_tract_county`.
- `place` and `zcta` are not included yet because they still need dedicated hierarchy treatment for a gold-grade dimension.

## Key Columns

| Column | Definition |
|---|---|
| `geo_level` | Canonical geography level (`us`, `region`, `division`, `state`, `cbsa`, `county`) |
| `geo_id` | Canonical identifier within the geography level |
| `geo_name` | Canonical geography name |
| `display_name` | User-facing label for dashboards and prompt surfaces |
| `cbsa_type` | OMB CBSA type classification |
| `cbsa_type_short` | Normalized CBSA type label (`metro` or `micro`) |
| `is_metro` | Boolean flag for metropolitan CBSAs |
| `is_micro` | Boolean flag for micropolitan CBSAs |
| `parent_geo_level` | Immediate parent level on the primary hierarchy path when a single parent exists |
| `parent_geo_id` | Immediate parent identifier on the primary hierarchy path when a single parent exists |
| `parent_region_id` | Census region parent identifier where determinable |
| `parent_division_id` | Census division parent identifier where determinable |
| `parent_state_fips` | State parent identifier where determinable |
| `parent_cbsa_code` | CBSA parent identifier for county rows that belong to a CBSA |

## Lineage

1. `etl/gold/gold_dim_geo.sql` builds the table in the gold schema.
2. State, region, and division attributes come from `silver.xwalk_state_region`.
3. County attributes come from `silver.xwalk_county_state`.
4. CBSA identity and metro/micro classification come from `silver.xwalk_cbsa_county`.
5. Exact tract parentage comes from `silver.xwalk_tract_county`.
6. `primary_city_name` is reserved for future enrichment but is null in the first release so the build does not depend on optional CBSA principal-city assets.

## Known Gaps / To-Dos

- Add `place` rows once a canonical place-to-county and place-to-state crosswalk is added to the repo.
- Add `zcta` rows after we decide the canonical weighted hierarchy strategy for zcta-to-county and zcta-to-cbsa relationships.
- Decide whether multi-state CBSAs should also expose a deterministic “primary state” separate from the current single-state-only logic.
- Consider promoting this table into broader semantic-layer support for chatbot planning and dashboard filtering.
