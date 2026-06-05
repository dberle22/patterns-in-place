# Definition Audit

## Track 2 shared-field pass (2026-06-02)

- Silver YAML files scanned: 50
- Total Silver column records scanned: 941
- Shared fields in scope: `geo_id`, `geo_level`, `geo_name`, `period`, `table`, `line_desc_clean`, `source`, `metric_key`, `code`
- Unresolved shared-field records before the final fixes: 2
- Unresolved shared-field records after the final fixes: 0

## Shared-field status

| Field | Silver occurrences checked | Unresolved after pass | Notes |
| --- | ---: | ---: | --- |
| `geo_id` | 33 | 0 | Already documented across current Silver YAMLs; verified in this pass. |
| `geo_level` | 33 | 0 | Already documented across current Silver YAMLs; verified in this pass. |
| `geo_name` | 33 | 0 | Already documented across current Silver YAMLs; verified in this pass. |
| `period` | 14 | 0 | Already documented across current Silver YAMLs; verified in this pass. |
| `table` | 12 | 0 | Already documented across current Silver YAMLs; verified in this pass. |
| `line_desc_clean` | 8 | 0 | Already documented across current Silver YAMLs; verified in this pass. |
| `source` | 9 | 0 | Final unresolved placeholder removed from `silver__kpi_dictionary.yml`. |
| `metric_key` | 7 | 0 | Already documented across current Silver YAMLs; verified in this pass. |
| `code` | 5 | 0 | Final unresolved placeholder removed from `silver__bea_regional_marpp_long.yml`. |

## Remaining non-Track-2 work

- This pass closes the targeted shared-field gaps only.
- Other unresolved field definitions still exist elsewhere in Silver YAMLs and should be handled in a separate follow-up pass rather than expanding Track 2 scope silently.
