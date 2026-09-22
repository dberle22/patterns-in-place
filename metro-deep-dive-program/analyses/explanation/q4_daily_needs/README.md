# Q4 — Livability Amenities and POI Clusters

**Build order:** E5 — POI-first workbench for the Richmond and Jacksonville
pilot markets.

**Status:** Epic 1 audit complete. The workbench, basket catalog, and cluster
method remain to be built.

**Question:** How are livability amenities organized across a metro, what
spatial amenity hubs and comparable amenity environments emerge, and what is
the demographic and housing context around them?

Q4 starts with governed POI points, not tract scores. It will retain POI
membership in reviewed spatial amenity hubs, group similar but noncontiguous
hubs into amenity-environment typologies, and use tract measures as descriptive
context. Those reusable outputs can support later corridor, catchment, housing,
employment, and access analyses.

## Scope boundary

Q4 is the program's introductory 15-minute-city workbench. V1 can describe
amenity concentration, diversity, and surrounding conditions. It cannot claim
15-minute access, walkability, travel time, route quality, or barrier effects
without a later declared network and barrier method.

**Owns:** analysis basket definitions, POI-cluster construction, typologies,
tract-context profiles, and Q2 employment comparison.

**Borrows from the POI Engine:** source identity, provenance, governed taxonomy,
coordinates, and point assignment. It does not rewrite them locally.

**Borrows from Infrastructure:** roads, rail, and water as mapped context only.

**Borrows from Q2:** reviewed job-center and physical-proximity evidence only as
a comparison layer. Q2 does not supply an access or 15-minute-city definition
for Q4 to reuse.

## Pilot outputs

- POI workbench and versioned basket catalog, starting with broad livability and
  errands/essentials;
- spatial amenity-hub inventory, geometry, and POI membership;
- composition-based amenity-environment typologies;
- cluster profiles and tract demographic/housing context; and
- a method record, coverage flags, sensitivities, and a Q2 employment-context
  comparison.

See [EXPLANATION_Q4_DAILY_NEEDS_SPEC.md](EXPLANATION_Q4_DAILY_NEEDS_SPEC.md) for the
analysis contract, [EXPLANATION_Q4_DAILY_NEEDS_BUILD_PLAN.md](EXPLANATION_Q4_DAILY_NEEDS_BUILD_PLAN.md)
for the build sequence, and [EXPLANATION_Q4_AUDIT.md](EXPLANATION_Q4_AUDIT.md) for
the completed audit.
