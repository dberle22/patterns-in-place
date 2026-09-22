# mart_geography Regional Lens Surfaces

**Build:** `foundations/etl/geo/build_regional_lens_geography.R`

**Source:** 2023 Census TIGER/Line state and CBSA geometry via `tigris`.

These tables provide reusable regional-boundary inputs. They do not create a
Regional Role score, commute shed, travel-time estimate, or notebook-specific
comparison table.

## `mart_geography.state_adjacency`

One row per directed state-to-adjacent-state relationship. The table is
symmetric: every edge has its reverse edge. A relationship requires a shared
boundary line with nonzero length, so point-only contact, ocean, and Great Lake
contact are excluded; a river boundary counts.

Key fields: `state_fips`, `adjacent_state_fips`, `shared_boundary_meters`,
`boundary_vintage`, `source`, and `method_version`.

## `mart_geography.cbsa_centroids`

One equal-area geometric centroid per CBSA and boundary vintage. Coordinates
are stored as WGS84 longitude and latitude after calculating the centroid in
EPSG:5070.

Key fields: `cbsa_code`, `boundary_vintage`, `centroid_method`,
`longitude`, `latitude`, `source`, and `method_version`.

The centroid is a declared geographic-proximity reference point. It is not a
travel-time, access, or commuting measure.

## `mart_geography.region_lens_membership`

One target metropolitan CBSA × lens × parameter × member metropolitan CBSA
relationship. The surface contains:

- `census_division`
- `primary_state`
- `primary_state_adjacent`
- `cbsa_centroid_250mi` with 200-, 250-, and 300-mile parameter rows

Key fields: `target_cbsa_code`, `lens_id`, `lens_version`,
`parameter_name`, `parameter_value`, `member_cbsa_code`,
`member_role`, `distance_miles`, `membership_source`,
`boundary_vintage`, and `method_version`.

Primary state is `gold.dim_geo.state_fips`: the first state named in the
official CBSA label. It is not based on county count or population.
