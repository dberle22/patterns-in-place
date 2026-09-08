# Data Dictionary: silver.xwalk_zip_county

HUD-USPS quarterly ZIP-to-county allocation. One row per ZIP/county/release.

- `zip_geoid`: five-digit USPS ZIP code, not a Census ZCTA.
- `county_geoid`: five-digit county GEOID.
- `residential_address_ratio`, `business_address_ratio`,
  `other_address_ratio`, `total_address_ratio`: source-published ZIP address
  shares; choose the basis explicitly.
- `source_release_year`, `source_release`, `source`: acquisition provenance.

`silver.xwalk_zcta_county` remains a temporary compatibility view only.
