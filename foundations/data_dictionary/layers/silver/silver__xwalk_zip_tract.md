# Data Dictionary: silver.xwalk_zip_tract

HUD-USPS quarterly ZIP-to-tract allocation. One row per ZIP/tract/release.

- `zip_geoid`: five-digit USPS ZIP code, not a Census ZCTA.
- `tract_geoid`: eleven-digit Census tract GEOID.
- Use the explicit source address-ratio basis that matches the metric.

`silver.xwalk_zcta_tract` remains a temporary compatibility view only.
