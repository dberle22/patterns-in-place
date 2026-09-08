# Source Spec: HUD-USPS ZIP Crosswalk

## Purpose

HUD distributes quarterly USPS ZIP-to-tract, county, and CBSA allocations.
Foundations uses them only for ZIP data, never as Census ZCTA relationships.

## Contract

- Canonical tables are `silver.xwalk_zip_tract`, `silver.xwalk_zip_county`, and
  `silver.xwalk_zip_cbsa`.
- Retain the source release quarter, ZIP, target ID, `RES_RATIO`, `BUS_RATIO`,
  `OTH_RATIO`, and `TOT_RATIO` where available.
- Allocation requires a caller-selected address basis; rounded weights may not
  sum exactly to one.
- CBSA code `99999` represents ZIPs outside a CBSA and must remain visible in
  audit output.
