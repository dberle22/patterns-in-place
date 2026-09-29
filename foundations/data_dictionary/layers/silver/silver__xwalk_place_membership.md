# Data Dictionary: silver.xwalk_place_membership

2020 Census Place membership in current counties and 2023 OMB CBSAs. This is a
weighted relationship derived from 2020 Census block assignments; it is never
an exact containment hierarchy.

One row represents a Place, target County or CBSA, and explicit weight basis.

- `target_share_in_place` is the share of the Place's selected-basis total in
  the target. For a CBSA row, this is the CBSA share in the Place.
- `place_share_in_target` is the share of the target's selected-basis total in
  the Place. For a CBSA row, this is the Place share in the CBSA.
- `target_numerator`, `place_denominator`, and `target_denominator` make both
  shares inspectable instead of treating either as a universal weight.
- `membership_status` is `whole`, `split`, `partial`, or `undefined`.
  `partial` means that some Place mass falls outside the declared target
  universe, such as a Place partly outside all current CBSAs.
- `quality_flag` retains the allocation-quality classification. It is not a
  claim of administrative containment.
- `primary_cbsa_code` and `is_primary_cbsa` occur only on population-basis
  CBSA rows. They select the largest 2020 population share while preserving
  all other memberships.

Use `silver.place_primary_cbsa_association` or its mart view for a complete
one-row-per-Place primary-association label, including no-CBSA and undefined
population-basis cases.
