# Richmond POI Data Shape

Snapshot: Overture Places `2026-08-19.0`, 61,513 source-faithful records
retained inside the governed Richmond boundary.

| Field / surface | Coverage | Meaning |
|---|---:|---|
| Source ID | 61,513 (100%) | Unique Overture record identity in this release. |
| Name | 61,513 (100%) | Provider primary place name. |
| Geometry and representative point | 61,513 (100%) | Valid and assigned to tract and county. |
| Freeform street address | 59,826 (97.3%) | Street text; it commonly omits a postal code. |
| Structured provider postcode | 60,066 (97.6%) | `addresses[1].postcode`, preserved separately from street text. |
| Postal ZIP after structured field + street fallback | 60,120 (97.7%) | Source address evidence, not a Census ZCTA assignment. |
| Primary / taxonomy category | 58,758 (95.5%) | Raw provider labels retained for mapping and review. |
| First governed mapping | 1,053 (1.7%) | Narrow Q4 starter mappings only; all other valid records remain unmapped for review. |

The source record is richer than the normalized fields: it also retains source
categories, confidence, websites, phones, brand, operating status, full
address structure, source lineage, version, geometry, and bbox metadata in the
source-faithful acquisition cache.

The intended sequence is: source-faithful cache → normalized source-place
record → governed taxonomy mapping → tract/county assignment → Q4 analysis
basket and access method. See [the taxonomy guide](taxonomy/TAXONOMY_GUIDE.md)
for the classification layer and [the contract](CONTRACT.md) for field-level
rules.
