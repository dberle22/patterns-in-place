# Data Dictionary: silver.xwalk_allocation

Census 2020 tract-to-Place and tract-to-ZCTA weighted allocations. One row per
source tract, target, and explicitly selected basis.

- `weight_basis` is `population`, `housing_units`, or `land_area`; callers must
  choose it and may not treat a weight from one basis as another.
- `weight` is the target share of the source tract for that basis.
- `source_denominator`, `target_numerator`, and `allocated_weight_sum` retain
  the arithmetic needed to audit partial or zero-denominator cases.
- `quality_flag` is `exact`, `clean`, `split`, `partial`, or `undefined`.
- These are allocations, not exact containment relationships.
