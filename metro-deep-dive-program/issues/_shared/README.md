# Shared Issue Conventions

Use this folder for issue-facing materials that are shared across markets, such as:

- shared output conventions
- reusable issue checklists
- fixed visual or table specs once they lock
- shared wording notes and caveats
- shared issue notebooks or helpers when they assemble issue-facing assets

## Marimo Conventions

When building shared issue notebooks in this folder:

- keep notebooks as `.py` files and open them in VS Code with
  `marimo: Open as marimo notebook`
- use `.venv-marimo/bin/python` as the notebook interpreter unless the notebook
  explicitly needs a different environment
- assume the notebook will also be reviewed in the browser via `marimo edit`,
  so path logic should be portable and not depend on ad hoc local cwd state
- keep reusable analytical logic in `analyses/`; shared notebooks here should
  assemble and inspect issue-facing surfaces rather than redefine them

Common marimo gotchas we already hit:

- Marimo treats assigned variable names as notebook-graph definitions, so do
  not reuse generic names like `con` across cells
- UI dropdown defaults must use the option key shown in the UI, not the mapped
  underlying value
- if a dependency cell fails, downstream UI cells often error second; fix the
  earliest cell error first
