# Metro Deep Dive Program Sandbox

This folder is the clean sandbox for the new Metro Deep Dive build structure.

It intentionally sits alongside the legacy `metro-deep-dive/` tree so we can:

- define the new program structure clearly
- scaffold the new build layers without premature migration
- prove which reusable components, analyses, and issue builders actually work

Top-level structure:

- `docs/` for supporting planning notes as needed
- `engines/` for reusable systems, methods, marts, and supporting infrastructure
- `analyses/` for reusable question notebooks, theme notebooks, and reusable act-level builders
- `issues/` for market-specific assembly, lock-once decisions, and output planning

Acts are output lenses, not the top-level scaffold.
