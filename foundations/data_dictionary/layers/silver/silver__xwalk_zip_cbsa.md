# Data Dictionary: silver.xwalk_zip_cbsa

HUD-USPS quarterly ZIP-to-CBSA allocation. One row per ZIP/CBSA/release.

- `zip_geoid`: five-digit USPS ZIP code, not a Census ZCTA.
- `cbsa_geoid`: OMB CBSA code; `99999` remains an explicit non-CBSA case.
- Address-ratio columns are basis-specific allocation weights and may not sum
  exactly to one because HUD publishes rounded ratios.

`silver.xwalk_zcta_cbsa` remains a temporary compatibility view only.
