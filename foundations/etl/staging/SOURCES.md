# Staging Sources

This file tracks where each staging script gets its data and what is needed to refresh it inside the monorepo ETL.

| Script | Source type | Notes |
|---|---|---|
| `get_acs_*.R` | API (`tidycensus`) | Census API key required for refreshes |
| `get_bea.R` | API (`bea.R`) | BEA API key required |
| `get_bls_laus.R` | API | BLS API key required |
| `get_bls_qcew.R` | CSV download | BLS QCEW annual singlefile ZIP files, with titles backfilled from local metadata; no API key required |
| `get_bfs.R` | XLSX download | Census BFS annual county workbook (`bfs_county_apps_annual.xlsx`); county business applications only in the verified first-pass source |
| `get_bps.R` | CSV download | Census Building Permits Survey |
| `get_cbp.R` | ZIP download with delimited text file | Census CBP county annual ZIP (`cbp23co.zip` in the current release) containing a quoted comma-delimited `.txt` file; county is the first-pass ingest path |
| `get_epa_aqi.R` | CSV download | EPA AirData annual AQI ZIP files by county and CBSA; no API key required |
| `get_epa_sld.R` | ZIP / geodatabase or tabular download | EPA Smart Location Database bulk download plus ArcGIS REST fallback; no API key required |
| `get_ejscreen.R` | Archived CSV download | Archived EJScreen block-group snapshot; public EPA delivery discontinued on 2025-02-05, so pin exact archive source when implemented |
| `get_fema_nri.R` | CSV download | FEMA National Risk Index county and tract ZIP bundles (`NRI_Table_Counties.zip`, `NRI_Table_CensusTracts.zip`) with packaged data dictionary and hazard metadata; no API key required |
| `get_fhfa.R` | XLSX/CSV download | FHFA House Price Index annual U.S., state, CBSA, county, ZIP5, and tract files; no API key required |
| `get_hud_chas.R` | CSV download | HUD source file |
| `get_hud_fmr.R` | CSV download | HUD source file |
| `get_irs_migration.R` | CSV download | IRS SOI source file |
| `get_tea.R` | CSV download | Texas Education Agency |
| `get_tiger_geos.R` | API (`tigris`) | No key required |
| `get_usda_food_atlas.R` | XLSX / ZIP download | USDA ERS Food Access Research Atlas current public release is 2019; ArcGIS REST service available for schema / QA |
| `get_zillow.R` | CSV download | Zillow Research Data |
| `tx_school_acs_ingest.R` | API (`tidycensus`) | Census API key required |

Detailed source notes live under `notes/patterns_in_place_notes/Data/Sources/`.
