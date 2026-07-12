# CLAUDE.md

See `<monorepo-root>/AGENTS.md` for the shared behavioral guidelines.

## Quick orientation

`publisher/` contains four parts: the chatbot backend, the publisher batch runner, the frontend review app, and the manual content workspace.

**Required env var:** `FOUNDATIONS_PATH` must point to `<monorepo-root>/foundations/`.
`chatbot/query/catalogs.py` and `chatbot/charts/renderer.py` both read it at import time.

| Task | Command |
|---|---|
| Run a question through the chatbot | `PYTHONPATH=. python chatbot/scripts/ask.py "<question>"` |
| Run the Chart-A-Day queue | `PYTHONPATH=. python chart_a_day/runner/run_next.py --next` |
| Boot the frontend | `PYTHONPATH=. streamlit run frontend/streamlit_app.py` |

- `chatbot/` contains orchestration, parsing, SQL generation, validation, execution, and chart rendering.
- `chart_a_day/` contains the Chart-A-Day backlog, runner scaffold, skill prompts, and output artifacts.
- `content/` is a manual topic workspace; do not route it through the chatbot pipeline by default.
- `foundations/semantic_layer/` and `foundations/visual_library/` are the canonical shared assets.
