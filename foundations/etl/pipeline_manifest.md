# Pipeline Manifest

`pipeline_manifest.yml` is a lightweight source of truth for ETL order, outputs, and dependencies.

For now it is documentation only. The next builder should stay small:

- Read the manifest.
- Select `enabled: true` steps.
- Topologically sort by `depends_on`.
- Run each `script` from the repo root with `Rscript`.
- Before each step, optionally skip work if all declared `outputs` already exist.
- Stop on the first failure and print the blocked downstream steps.

That gives us a simple, inspectable builder without introducing a larger orchestration framework. If we later need retries, partial rebuilds, or layer-specific runs, those can be added on top of this manifest instead of hardcoding order in multiple R files.
