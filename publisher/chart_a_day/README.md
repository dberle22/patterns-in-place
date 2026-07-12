# Chart Engine

`chart_a_day/` is the agent-driven chart-a-day pipeline for the Publisher product area. It bypasses the chatbot NL-to-SQL parser entirely: each backlog entry is a pre-defined question, the agent writes SQL directly against the Gold warehouse, renders a chart through `chart_engine_py`, and drafts social copy for human review before posting.

Use the queue CLI from `publisher/` with `PYTHONPATH=.`. `python chart_a_day/runner/run_next.py --status` shows backlog counts, `python chart_a_day/runner/run_next.py --next` shows the next ready question, and `python chart_a_day/runner/run_next.py --id q003 --note "..."` appends a review note to that question's output folder. The skill prompts live in `skills/sql_agent.md` (question to SQL and CSV), `skills/chart_request.md` (result CSV to `ChartRequest` and chart artifact), and `skills/social_copy.md` (finding plus chart to X and Bluesky drafts).
