# Data Dictionary: silver.place_primary_cbsa_association

One declared population-share primary-CBSA association for every 2020 Census
Place in the block registry. It is a selection label, not exact containment.

- `primary_cbsa_code` is the CBSA receiving the largest 2020 population share
  of the Place.
- `association_status` distinguishes `whole_cbsa_membership`,
  `split_cbsa_membership`, `partial_cbsa_membership`, `no_cbsa_membership`,
  and `undefined_population_basis`.
- `cbsa_coverage_share` reports the amount of Place population represented by
  current CBSA membership rows.

Consumers using direct Place measures must retain the status and, for split or
partial Places, either allocate with `silver.xwalk_place_membership` or state a
whole-Place caveat.
