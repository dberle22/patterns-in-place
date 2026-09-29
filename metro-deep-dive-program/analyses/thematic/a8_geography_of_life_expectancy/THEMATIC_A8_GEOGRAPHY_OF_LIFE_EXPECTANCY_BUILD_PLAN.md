# Thematic A8 — Geography of Life Expectancy Build Plan

**Status:** Provisional; Epic 1 is the only authorized starting work

## Epic 1 — Audit health vintages, geography, and inference

- [ ] Profile `health_wide` coverage and trace life-expectancy values to their
  source periods, reliability notes, and rollup behavior.
- [ ] Profile income, housing, social-fabric, food-access, and environment
  context by county/CBSA and vintage.
- [ ] Decide whether county or CBSA is the primary national unit and document
  the role of the other.
- [ ] Test candidate income baselines, weighting, minimum-population rules, and
  region/urbanicity controls.
- [ ] Review correlated context measures and propose a deliberately narrow
  staged model or descriptive design.
- [ ] Replace unsupported “place effect” language with an explicit residual or
  association interpretation unless a stronger design is found.
- [ ] Propose standard market deep-dive paths and geography limits.
- [ ] Revise the spec and this plan before writing code.

**Done when:** every outcome/context field has a period and grain, the primary
unit is chosen, and the residual interpretation is defensible.

## Epic 2 — Establish the health-context surface

- [ ] Build the reviewed county/CBSA components from governed inputs.
- [ ] Preserve source periods, reliability, rollup method, and coverage flags.
- [ ] Validate joins, weights, and any expected/residual fields.

## Epic 3 — Build the national notebook

- [ ] Present health and income baselines before contextual models.
- [ ] Add context families in transparent stages.
- [ ] Run region, weighting, reliability, and variable-set sensitivities.
- [ ] Produce the finding ledger and counterexample markets.

## Epic 4 — Build the parameterized market notebook

- [ ] Add the standard CBSA selector and comparison contexts.
- [ ] Show member-county outcome and component variation.
- [ ] Label finer-grain context separately from observed health outcomes.
- [ ] Test Richmond plus single-county and multi-county contrast markets.

## Epic 5 — Review and hand off

- [ ] Confirm national and market residual language is consistent.
- [ ] Document any reusable health-context comparison surface.
- [ ] Hand issue candidates downstream with ecological, period, and reliability
  caveats intact.

