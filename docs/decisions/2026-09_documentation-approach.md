# Documentation approach

**Date:** 2026-09-29
**Source:** Repo documentation overhaul review

## Decision

- The repo docs are written for Dan and AI agents. There are no technical collaborators yet; revisit if that changes.
- The repo is the single source of truth. The `notes/` Obsidian vault is reviewed, useful content is merged in, and the rest is deleted. Done 2026-09-29; a backup zip is kept outside the repo.
- Area statuses: Metro Deep Dive program, public panel, foundations and exploration are Active. Area Explorer, Publisher and Stoop are Paused. Legacy `metro-deep-dive/` retires into the program once nothing depends on it.
- Old docs get the new conventions only as they're touched, never in a sweep.

## Why

The docs had no front door, overlapping roadmaps, and context split between the repo and an unversioned vault that agents were told to read.

## What it means

- Start from the root `README.md`. Doc rules are in [CONVENTIONS.md](../CONVENTIONS.md).
- Public-facing docs are built for each release.
