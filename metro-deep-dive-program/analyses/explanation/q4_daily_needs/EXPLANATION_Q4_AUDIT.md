# Explanation Q4 — POI Surface Audit

**Completed:** 2026-09-22

**Decision:** Proceed with a Richmond/Jacksonville POI-first livability
amenities and cluster workbench. Do not build a Q2-derived access score,
network/barrier result, or national product in V1.

## Evidence reviewed

| Topic | Richmond (`40060`) | Jacksonville (`27260`) | Finding |
|---|---:|---:|---|
| Source release | Overture Places `2026-08-19.0` | Overture Places `2026-08-19.0` | Comparable source vintage. |
| Retained points inside governed market boundary | 61,513 | 86,933 | Both markets support a pilot inventory. |
| Mapped points | 59,459 (96.7%) | 83,597 (96.2%) | Governed Category/Subcategory coverage is strong. |
| Unmapped points | 2,054 | 3,336 | These remain visible coverage states; documentation attributes them to absent source category evidence rather than missing rules. |
| Governed categories / subcategories | 22 / 117 | 22 / 117 | A broad basket system can be declared over a shared vocabulary. |
| Tract and county assignment | 100% / 100% | 100% / 100% | Both use governed point-in-polygon assignment. |
| Provider ZIP evidence | 60,120 (97.7%) | 84,880 (97.6%) | Not a Census ZCTA assignment; do not use as a geography identity. |

The observed taxonomy includes substantial grocery/food retail, pharmacies,
primary/general care, hospitals, childcare/education, parks, libraries,
convenience retail, and many broader livability categories in each market.
The audit therefore does not force the analysis into a narrow daily-needs
basket. It supports a basket matrix beginning with broad livability and
errands/essentials.

## Contract findings

- Optional third-level taxonomy Detail is populated for 59.0% of Richmond and
  60.9% of Jacksonville points. That is source structure, not failure of the
  governed Category/Subcategory mapping; V1 should not depend on Detail.
- POI points are the appropriate primary evidence. Their assigned tract can
  provide a transparent demographic/housing context join without defining a
  cluster.
- Infrastructure source runs exist for the two pilots, but the Infrastructure
  Engine does not provide routing, travel time, walkability, or a barrier
  conclusion. Use it as map/profile context only.
- Q2's published Haversine job-center proximity is physical proximity, not an
  access or 15-minute-city method. It can be a comparison layer, not a Q4
  dependency or shared method.
- ACS-derived tract context is documented in the program plan. Its deployed
  serving table, field contract, and vintage must be verified at build time.
- The POI artifacts exist for both markets, but their final reusable
  consumer-serving interface status, especially Jacksonville portability,
  remains a handoff check before other analyses consume them.

## Scope resulting from the audit

V1 will construct direct spatial POI amenity hubs, composition-based amenity
environment typologies, and tract context profiles. It will retain POI
membership and cluster provenance as reusable outputs.

V1 will not claim practical resident access, 15-minute coverage, walkability,
route quality, or effects of physical barriers. Those require a later,
explicitly declared network and barrier method.

## Sources examined

- [POI Engine Contract](../../../engines/poi/CONTRACT.md)
- [POI taxonomy reference](../../../engines/poi/taxonomy/TAXONOMY.md)
- Richmond and Jacksonville source, classification, and geography manifests
  under `metro-deep-dive-program/engines/poi/outputs/`
- [Infrastructure Engine Contract](../../../engines/infrastructure/CONTRACT.md)
- [Q2 Job-Proximity Spec](../q2_job_proximity/EXPLANATION_Q2_JOB_PROXIMITY_SPEC.md)
