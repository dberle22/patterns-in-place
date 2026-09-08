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
