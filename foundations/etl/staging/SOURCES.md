# Staging Sources

This file tracks where each staging script gets its data and what is needed to refresh it inside the monorepo ETL.

| Script | Source type | Notes |
|---|---|---|
| `get_acs_*.R` | API (`tidycensus`) | Census API key required for refreshes |
| `get_bea.R` | API (`bea.R`) | BEA API key required |
| `get_bls_laus.R` | API | BLS API key required |
| `get_bls_qcew.R` | CSV download | BLS QCEW annual singlefile ZIP files, with titles backfilled from local metadata; no API key required |
| `get_bps.R` | CSV download | Census Building Permits Survey |
| `get_fhfa.R` | XLSX/CSV download | FHFA House Price Index annual U.S., state, CBSA, county, ZIP5, and tract files; no API key required |
| `get_hud_chas.R` | CSV download | HUD source file |
| `get_hud_fmr.R` | CSV download | HUD source file |
| `get_irs_migration.R` | CSV download | IRS SOI source file |
| `get_tea.R` | CSV download | Texas Education Agency |
| `get_tiger_geos.R` | API (`tigris`) | No key required |
| `get_zillow.R` | CSV download | Zillow Research Data |
| `tx_school_acs_ingest.R` | API (`tidycensus`) | Census API key required |

Detailed source notes live under `notes/patterns_in_place_notes/Data/Sources/`.
