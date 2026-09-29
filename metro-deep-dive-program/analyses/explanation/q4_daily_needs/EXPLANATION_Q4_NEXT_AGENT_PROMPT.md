# Explanation Q4 — Next-Agent Handoff Prompt

You are taking over Explanation Q4, **Livability Amenities and POI Clusters**.
Read these documents first, in order:

1. `EXPLANATION_Q4_DAILY_NEEDS_SPEC.md`
2. `EXPLANATION_Q4_DAILY_NEEDS_BUILD_PLAN.md`
3. `EXPLANATION_Q4_AUDIT.md`
4. `EXPLANATION_Q4_AMENITY_HUB_REVIEW.md`
5. `README.md`

## Mission and boundary

Q4 is a POI-first livability workbench for Richmond (`40060`) and Jacksonville
(`27260`). It starts with governed POI points, makes amenity composition and
spatial concentration visible, and creates reusable evidence for later work.

It is **not** a tract-ranking exercise, a resident-access score, a 15-minute
access claim, a walkability model, a routing product, or a barrier analysis.
Do not infer any of those outcomes from POI counts, straight-line proximity, or
Infrastructure context.

Tracts are contextual overlays. POI points determine basket membership and hub
membership; tract demographics/housing must not select a hub.

## What exists

- Epic 1 audit is complete.
- Epic 2 is complete:
  - `q4_amenity_baskets.yml` declares `broad_livability` and
    `errands_essentials` baskets.
  - `build_q4_poi_workbench.py` builds the POI workbench, basket membership,
    coverage, category composition, and manifest in `outputs/q4_poi_workbench_v1/`.
  - `EXPLANATION_Q4_NOTEBOOK.py` is the read-only Marimo workbench.
- Epic 3 is complete only as a **pre-basket baseline**:
  - `build_q4_amenity_hubs.py` produced all-mapped-POI density candidates in
    `outputs/q4_amenity_hub_grid_v1/`.
  - `grid_250m_min_20` is selected for workbench review; `grid_500m_min_60` is
    retained as sensitivity.
  - The baseline is not the final basket-specific hub construction.

The POI artifacts are direct pilot artifacts, not a promoted shared mart. Keep
that status visible.

## Intended notebook flow

The notebook should be an analyst workbench, not a static report. The flow is:

1. **Orientation:** purpose, source vintage, scope, and explicit non-claims.
2. **Controls:** market and basket selection; controls must affect display or a
   declared exploratory candidate only, never silently alter source taxonomy.
3. **Coverage:** mapped versus unclassified POIs, tract-assignment coverage,
   and the difference between a true zero and incomplete coverage.
4. **Basket contract:** show the exact governed categories/subcategories that
   enter the selected basket and why.
5. **POI map:** interactive, filterable point inventory for the selected basket.
6. **Composition:** category/subcategory counts and mix, shown before any hub
   interpretation.
7. **Hub review:** after the basket-specific rerun, show hub geometry, POI
   membership, candidate/sensitivity choice, and a hub-detail table.
8. **Later pages, not yet built:** composition typologies, tract-context
   profiles, and Q2 employment comparison.

The current notebook covers steps 1–6. Its flow and usability must be reviewed
with the user before adding steps 7–8 or starting Epics 4–5.

## Deliverables to preserve

The durable Q4 interface should consist of:

| Product | Grain | Role |
|---|---|---|
| POI workbench | retained POI point | Governed classification, assignment, basket flags, and coverage state. |
| Basket catalog | basket × governed taxonomy member | Analysis-owned definitions; never changes source taxonomy. |
| Amenity-hub inventory | market × method version × hub | Geometry, construction rule, size, category mix, and review status. |
| POI-to-hub membership | method version × POI | Transparent, reproducible hub evidence. |
| Hub composition profile | hub × category/subcategory | Basis for later typologies and review. |
| Tract context matrix | tract × snapshot | Later descriptive interpretation only. |

## Next work and stop condition

1. Confirm the existing notebook runs against its generated artifacts and give
   the user a concise walkthrough of its flow.
2. Ask for the user's usability review of that notebook before extending it.
3. If the user approves basket-specific hub work, rerun the direct point-pattern
   candidate method using `broad_livability` as the primary hub universe. Keep
   the all-mapped baseline and the 500 m method as declared sensitivities.
4. Do not begin Epic 4 (typologies/context) or Epic 5 (Q2 comparison/reuse)
   until that review occurs.

## Guardrails

- Do not silently treat all mapped POIs as the broad-livability basket.
- Do not use taxonomy Detail as a required field.
- Do not drop unclassified POIs from coverage reporting.
- Do not use Infrastructure to split or rank hubs until a separate named method
  defines that role.
- Do not turn the notebook into a final editorial chart or a tract scorecard.
- Do not promote direct pilot artifacts to a shared mart without the required
  consumer-interface review.
