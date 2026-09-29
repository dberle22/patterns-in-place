# Three Intelligence frames, one shared method

**Date:** 2026-06
**Source:** `docs/archive/2026-09_intelligence_layer_roadmap/INTELLIGENCE_LAYER_ROADMAP.md`; [intelligence_framework_overview.md](../methodology/intelligence_framework/intelligence_framework_overview.md) §1; the locked architecture is in [ARCHITECTURE.md](../methodology/intelligence_framework/ARCHITECTURE.md)

## Decision

Places are assessed through three separate frames (Character, Livability, Opportunity) plus a combined Cross-Frame view, not one composite score. Every frame uses the same pipeline: imputation, standardization, clustering sequence, scoring and similarity method. The architecture is locked; phase work doesn't re-argue it.

## Why

A single "best place" score averages away real tensions, such as a metro that's good for building wealth but hard to live in day to day. One shared method means it's learned once, and outputs from different frames are comparable in how they were made.

## What it means

- Character is descriptive; it has no good or bad direction.
- The CBSA universe is never trimmed for missing data. Missingness is handled per KPI.
- Changes to the method need a new decision record, not an edit inside a phase notebook.
