# Semantic Layer

This directory is the canonical semantic-layer home for `patterns-foundations`.
It translates warehouse structure into a reusable contract for planners, AI agents,
question catalogs, chart selection, and future product-specific extensions.

## Source Of Truth

- The YAML catalogs in this directory are authoritative.
- `semantic_layer/artifacts/*` are derived from the YAML catalogs and should be regenerated, not hand-edited.
- `/Users/danberle/Documents/projects/data/duckdb/metro_deep_dive.duckdb` is the primary warehouse source for field, grain, and coverage metadata.
- `/Users/danberle/Documents/projects/metro_deep_dive_chatbot/semantic_layer` is a useful reference implementation, but not the canonical home going forward.

## Catalog Set

Core technical catalogs:

- `table_catalog.yml`
- `metric_catalog.yml`
- `join_catalog.yml`
- `geography_catalog.yml`
- `points_catalog.yml`

Meaning and routing catalogs:

- `theme_catalog.yml`
- `intelligence_catalog.yml`
- `question_catalog.yml`
- `query_templates.yml`
- `chart_rules.yml`

Utilities:

- `graph_builder.py`
- `visualize.py`

## Database Harvest Workflow

Use this sequence whenever the catalogs need to be refreshed from the live warehouse:

1. Inventory Gold tables from `information_schema.tables`.
2. Harvest ordered fields and types from `information_schema.columns`.
3. Validate grain with distinct-count checks against candidate primary keys.
4. Capture geo coverage, year coverage, and null sparsity for major metric families.
5. Pull lineage and descriptions from `silver.metadata_topics`, `silver.metadata_vars`, and `silver.kpi_dictionary`.
6. Reconcile any ambiguous lineage against the `metro_deep_dive` database-design docs and ETL scripts.
7. Update the YAML catalogs.
8. Regenerate graph artifacts.

## Generate Artifacts

```bash
python3 -m semantic_layer.visualize --format artifacts
```

This writes:

- `semantic_layer/artifacts/semantic_graph.mmd`
- `semantic_layer/artifacts/semantic_graph.json`
- `semantic_layer/artifacts/semantic_graph_summary.json`
- `semantic_layer/artifacts/semantic_graph_preview.md`

## Print A Summary

```bash
python3 -m semantic_layer.visualize --format summary
```

## Print Mermaid To Stdout

```bash
python3 -m semantic_layer.visualize --format mermaid
```

## Explore In Python

```python
from semantic_layer.graph_builder import load_catalogs, build_semantic_graph

catalogs = load_catalogs()
graph = build_semantic_graph(catalogs)

theme_nodes = [
    node for node, attrs in graph.nodes(data=True)
    if attrs["kind"] == "theme"
]
```
