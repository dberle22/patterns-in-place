# Shared Engine Assets

`engines/_shared/` holds reusable notebook environments, helpers, and light
infrastructure that sit above engine contracts and below analysis or issue
assembly.

This folder is the right place for:

- generic helper code that multiple engines or notebook layers can reuse
- shared connection and query helpers when they are not issue-specific
- lightweight infrastructure that supports higher-level notebooks elsewhere

This folder is not the place for:

- new mart layers
- issue-specific narrative choices
- shared issue assembly notebooks
- visual-polish work that belongs in `issues/`

The shared Act 1 notebook now lives under
`metro-deep-dive-program/issues/_shared/act_1/` because it is issue-facing
assembly, not engine logic.
