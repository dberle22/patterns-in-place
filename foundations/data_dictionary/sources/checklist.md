# Source Spec Coverage Checklist

Coverage unit: upstream source spec.

Source spec count: 16

| Status | Source | Spec | Scope |
| --- | --- | --- | --- |
| [x] | ACS | [source__acs.md](./source__acs.md) | Canonical ACS source spec with topic sections for shared ingestion and downstream modeling patterns |
| [x] | BEA | [source__bea.md](./source__bea.md) | Canonical BEA source spec with topic sections for regional ingestion, metadata, and downstream modeling patterns |
| [x] | BFS | [source__bfs.md](./source__bfs.md) | Provider-level spec for annual county business applications, with a deliberately narrow first-pass architecture and explicit notes on what the county file does not contain |
| [x] | BLS | [source__bls.md](./source__bls.md) | Provider-level spec for LAUS labor-market coverage plus QCEW staging, curated Silver modeling, and Gold industry placement |
| [x] | BLS OEWS | [source__bls_oews.md](./source__bls_oews.md) | Child topic spec for metro-first OEWS occupation and wage-distribution staging, suppression handling, and SOC-based analytical rollups |
| [x] | BPS | [source__bps.md](./source__bps.md) | Provider-level spec for annual building-permit staging and wide Silver modeling |
| [x] | CBP | [source__cbp.md](./source__cbp.md) | Provider-level spec for county-first business structure staging, with ZIP products documented but deferred from the first-pass ingest |
| [x] | HUD | [source__hud.md](./source__hud.md) | Provider-level spec for HUD CHAS plus FMR / SAFMR rent families |
| [x] | EPA | [source__epa.md](./source__epa.md) | Provider-level spec for AQI-first environmental coverage plus an archival EJScreen follow-on path |
| [x] | IRS | [source__irs.md](./source__irs.md) | Provider-level spec for IRS migration inflow staging and partial downstream modeling |
| [x] | IRS EO BMF | [source__irs_bmf.md](./source__irs_bmf.md) | Child topic spec for EO Business Master File nonprofit headquarters-density modeling via ZIP5-to-county allocation |
| [x] | LEHD LODES | [source__lehd_lodes.md](./source__lehd_lodes.md) | Child topic spec for block-native LODES WAC/RAC staging, tract-first aggregation strategy, and deferred OD flow modeling |
| [x] | LEHD J2J | [source__lehd_j2j.md](./source__lehd_j2j.md) | Child topic spec for J2J counts, J2JR rates, J2JOD origin-destination flow structure, and first-pass public bulk ingest scoping |
| [x] | LEHD QWI | [source__lehd_qwi.md](./source__lehd_qwi.md) | Child topic spec for county-first annualized QWI labor-dynamics staging, canonical Silver rollups, and Gold labor placement |
| [x] | USDA ERS County Typology | [source__usda_ers_typology.md](./source__usda_ers_typology.md) | Provider/topic spec for Rural-Urban Continuum Codes and County Typology classifications, including the Connecticut backbone mismatch and county-first Silver modeling decision |
| [x] | Zillow | [source__zillow.md](./source__zillow.md) | Provider-level spec for ZHVI and ZORI staged monthly series |

## Authoring Rule

- Use one source spec per upstream provider when shared ingestion mechanics, credentials, and operating assumptions dominate and topic differences can be captured cleanly as sections.
- Add child topic specs only when the source contains multiple dataset families with meaningfully different request strategies, transformations, or downstream ownership.
- Keep staging family contracts and Silver table contracts in their current folders; source specs should link to them rather than replace them.
