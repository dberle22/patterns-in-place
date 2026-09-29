# Source References for v2026.1

This file records the authoritative public references used to turn the lineage ledger into release documentation. `manifest.json` will additionally record the exact source retrieval/vintage used for each released version.

| Source family | Release citation/reference | v2026.1 use |
| --- | --- | --- |
| CBSA delineation | [OMB Bulletin No. 23-01](https://www.whitehouse.gov/wp-content/uploads/2023/07/OMB-Bulletin-23-01.pdf) | Current static county-to-CBSA memberships, CBSA type, and central/outlying designation. |
| ACS 5-year | [American Community Survey 5-Year Data](https://www.census.gov/data/developers/data-sets/acs-5year.html) | `B25064`, `B25077`, `B19013`, and `C24030` estimates. The release year is the end year of each five-year window. |
| BEA Regional GDP | [BEA API table reference](https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf) | `CAGDP9`: real GDP by county and metropolitan area. |
| BEA Regional Price Parities | [BEA Regional Price Parities](https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area) | `MARPP`: real per-capita income, all-items RPP, and price deflator. |
| HUD Fair Market Rents | [HUD Fair Market Rents documentation](https://www.huduser.gov/portal/datasets/fmr.html) | FY2012–FY2024 county FMR inputs, used to calculate population-weighted CBSA two-bedroom FMR. |

## Versioning rule

The links above identify source families, not a substitute for a release-specific vintage. Before v2026.1 is published, record the retrieved-file URL or API request, provider release date, and retrieval date in the release `manifest.json` for every source family. A newer upstream release does not silently replace values in a published version.
