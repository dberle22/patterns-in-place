# Source Specs

## Purpose

This folder holds provider-level source specs for the Foundations data dictionary.

These docs sit above the layer contracts and answer the higher-level questions that staging and Silver table docs do not answer cleanly on their own:
- what the upstream source is
- how we ingest it
- which staging families it creates
- which Silver outputs it feeds
- what important transformation patterns or exceptions exist

## How To Use This Folder

- Start here when the question is about upstream provenance, ingestion strategy, or how a provider fans out into multiple downstream tables.
- Use the staging family contracts for landed schema details and geography coverage.
- Use the Silver table contracts for field-level analytical definitions and profiling.

## Current Source Specs

- [source__acs.md](./source__acs.md)
- [source__bea.md](./source__bea.md)
- [source__bfs.md](./source__bfs.md)
- [source__bls.md](./source__bls.md)
- [source__bls_oews.md](./source__bls_oews.md)
- [source__bps.md](./source__bps.md)
- [source__cbp.md](./source__cbp.md)
- [source__social_capital_atlas.md](./source__social_capital_atlas.md)
- [source__hud.md](./source__hud.md)
- [source__epa.md](./source__epa.md)
- [source__irs.md](./source__irs.md)
- [source__opportunity_atlas.md](./source__opportunity_atlas.md)
- [source__usda_ers_typology.md](./source__usda_ers_typology.md)
- [source__lehd_lodes.md](./source__lehd_lodes.md)
- [source__lehd_j2j.md](./source__lehd_j2j.md)
- [source__lehd_qwi.md](./source__lehd_qwi.md)
- [source__zillow.md](./source__zillow.md)

Coverage tracking:
- [checklist.md](./checklist.md)
- [source_topic_checklist.md](./source_topic_checklist.md)

## Standard Structure

Each source spec should follow the same 9-section pattern:

1. `Overview`
2. `Coverage Matrix`
3. `Source Contract`
4. `Staging Shape`
5. `Staging To Silver`
6. `Transformation Notes`
7. `Data Quality Expectations`
8. `Operational Notes`
9. `Known Gaps`

Some newer specs also add a short `Source References` section when the live upstream URLs are important to preserve explicitly.

For large providers like ACS or BEA, topic groups should be handled inside one provider file rather than split into many repetitive child docs unless the operating rules diverge materially.

## Relationship To Layer Docs

- `sources/` explains the provider and the pipeline strategy.
- `layers/staging/` explains source-family landing contracts.
- `layers/silver/` explains modeled analytical tables.
- `layers/gold/` explains decision-ready downstream outputs.
