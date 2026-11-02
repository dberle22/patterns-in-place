# Time-Series / Trajectory Engine Notes

## Pilot-vintage decision

The initial Phase 6 inventory was useful for source discovery but cannot be
used as a scoring contract. The pilot uses a common 2023 end vintage because
the IRS net-migration rate is not currently populated at the 2023/2024 end
point, while the other selected metrics have usable 2023 histories. The
Character pilot therefore uses `pct_ba_plus` in place of the initially proposed
IRS metric.

The population universe continues to use the 2024 100,000-person threshold.
That keeps CBSA membership stable while avoiding a mixed-vintage frame score.
Health, environment, and QCEW coverage are not complete for every metro; the
engine preserves that limitation through coverage fields rather than imputing.

## Legacy Phase 6 disposition

The legacy `exploration/intelligence_framework/phase_6_trajectory/` material
is evidence and a candidate inventory. Its endpoint/z-score classification,
field exclusions, and publication outputs are not reused as this engine's
method. Future KPI expansion must add a registry entry, pass source and
coverage validation, and update this note if it changes the common panel or
vintage.

## IRS direction fix (2026-10-26)

The IRS series were stored with the sign reversed until 2026-10-26
(`foundations/etl/IRS_MIGRATION_DIRECTION_FIX_SPEC.md`). All five IRS registry
entries are `insufficient_history` at the 2023 end vintage, so no momentum,
label, tier or turn signal changed; only the IRS raw values in
`intelligence_trajectory_series` (and start values in the metric table) flipped.

The mart was promoted from `irs_fix_rerun_engine.py promote`, not from
`build_time_series_engine.py`, because gold now carries the BEA GDP refresh
(county GDP through 2024) and Dan held that for a separate GDP and clustering
refresh. The two GDP series (`industry_concentration_hhi`,
`pct_real_gdp_information`) in the mart are therefore the June values. **The
next `build_time_series_engine.py` run will publish the GDP refresh**; do it as
part of that refresh (see `foundations/ROADMAP.md`).

