# Source Spec Coverage Checklist

Coverage unit: upstream source spec.

Source spec count: 7

| Status | Source | Spec | Scope |
| --- | --- | --- | --- |
| [x] | ACS | [source__acs.md](./source__acs.md) | Canonical ACS source spec with topic sections for shared ingestion and downstream modeling patterns |
| [x] | BEA | [source__bea.md](./source__bea.md) | Canonical BEA source spec with topic sections for regional ingestion, metadata, and downstream modeling patterns |
| [x] | BLS | [source__bls.md](./source__bls.md) | Provider-level spec for LAUS labor-market coverage plus QCEW staging, curated Silver modeling, and Gold industry placement |
| [x] | BPS | [source__bps.md](./source__bps.md) | Provider-level spec for annual building-permit staging and wide Silver modeling |
| [x] | HUD | [source__hud.md](./source__hud.md) | Provider-level spec for HUD CHAS plus FMR / SAFMR rent families |
| [x] | IRS | [source__irs.md](./source__irs.md) | Provider-level spec for IRS migration inflow staging and partial downstream modeling |
| [x] | Zillow | [source__zillow.md](./source__zillow.md) | Provider-level spec for ZHVI and ZORI staged monthly series |

## Authoring Rule

- Use one source spec per upstream provider when shared ingestion mechanics, credentials, and operating assumptions dominate and topic differences can be captured cleanly as sections.
- Add child topic specs only when the source contains multiple dataset families with meaningfully different request strategies, transformations, or downstream ownership.
- Keep staging family contracts and Silver table contracts in their current folders; source specs should link to them rather than replace them.
