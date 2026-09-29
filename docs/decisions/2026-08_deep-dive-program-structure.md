# Metro Deep Dive program: engines, analyses, issues

**Date:** 2026-08-22
**Source:** `metro-deep-dive-program/metro_deep_dive_program.md` §1–2

## Decision

Metro Deep Dive work is organized in three layers: engines (reusable computation), analyses (reusable question notebooks) and issues (published pieces). The Intelligence Framework is the router: it decides which analyses a market gets and which act to lead with. `metro-deep-dive-program/` replaces the legacy `metro-deep-dive/` tree.

## Why

Seven overlapping efforts had each partly answered "show me a metro" and were being treated as peers. The three layers sort them, and working backward from the issue keeps effort pointed at output.

## What it means

- An engine is built only when an analysis needs it, and is promoted to `foundations/` when two consumers use it unchanged.
- Issues own every lock-once decision. Analyses stay exploratory.
- Acts are output lenses, not the folder structure.
