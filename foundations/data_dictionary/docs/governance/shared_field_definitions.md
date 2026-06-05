# Shared Field Definitions

Canonical definitions for shared Silver-layer fields that recur across multiple table contracts.

Use these definitions verbatim when the field meaning matches the standard contract below. If a table uses one of these names in a materially different way, document the exception in that table's YAML and Markdown pair.

| Field | Canonical definition |
| --- | --- |
| `geo_id` | Canonical geographic identifier for the row. Format depends on `geo_level` and is zero-padded where applicable. |
| `geo_level` | Canonical geography grain label for the row (for example, state, county, place, tract, zcta, or cbsa). |
| `geo_name` | Display name for the geography identified by `geo_id`. |
| `period` | Standardized observation period for the row, usually a calendar year. |
| `table` | Upstream source table or program identifier carried through the Silver layer. |
| `line_desc_clean` | Cleaned human-readable description of the source line, code, or metric represented by the row. |
| `source` | Upstream source or ETL-assigned provenance label for the row. |
| `metric_key` | Stable machine-friendly metric identifier used across long-format and metadata tables. |
| `code` | Upstream source code or line identifier used to link rows back to source metadata. |

## Track 2 completion notes

- `geo_id`, `geo_level`, `geo_name`, and `period` were already documented across current Silver YAML files during the 2026-06-02 pass.
- The remaining unresolved shared-field gaps found in this pass were `code` in `silver__bea_regional_marpp_long.yml` and `source` in `silver__kpi_dictionary.yml`; both were aligned to the canonical definitions.
