"""Build graph representations of the semantic layer catalogs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised by runtime guard
    yaml = None

try:
    import networkx as nx
    from networkx.readwrite import json_graph
except ImportError:  # pragma: no cover - exercised by runtime guard
    nx = None
    json_graph = None


CATALOG_FILES = {
    "table_catalog": "table_catalog.yml",
    "metric_catalog": "metric_catalog.yml",
    "geography_catalog": "geography_catalog.yml",
    "join_catalog": "join_catalog.yml",
    "query_templates": "query_templates.yml",
    "chart_rules": "chart_rules.yml",
    "theme_catalog": "theme_catalog.yml",
    "intelligence_catalog": "intelligence_catalog.yml",
    "question_catalog": "question_catalog.yml",
    "points_catalog": "points_catalog.yml",
}


def _require_dependencies() -> None:
    missing = []
    if yaml is None:
        missing.append("PyYAML")
    if nx is None:
        missing.append("networkx")
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            f"Missing required dependencies: {joined}. "
            "Install them with `python3 -m pip install --user PyYAML networkx`."
        )


def semantic_layer_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is None:
        return Path(__file__).resolve().parent
    return Path(base_dir)


def load_catalogs(base_dir: str | Path | None = None) -> dict[str, dict[str, Any]]:
    """Load all semantic YAML catalogs from disk."""
    _require_dependencies()
    root = semantic_layer_dir(base_dir)
    catalogs: dict[str, dict[str, Any]] = {}
    for catalog_name, filename in CATALOG_FILES.items():
        path = root / filename
        with path.open("r", encoding="utf-8") as handle:
            catalogs[catalog_name] = yaml.safe_load(handle)
    return catalogs


def _node_id(kind: str, value: str) -> str:
    return f"{kind}:{value}"


def _add_node(graph: Any, kind: str, value: str, label: str | None = None, **attrs: Any) -> str:
    node_id = _node_id(kind, value)
    graph.add_node(node_id, kind=kind, value=value, label=label or value, **attrs)
    return node_id


def _build_table_nodes(graph: Any, catalogs: dict[str, dict[str, Any]]) -> None:
    for table in catalogs["table_catalog"]["tables"]:
        table_id = table["table_id"]
        table_node = _add_node(
            graph,
            "table",
            table_id,
            label=table_id,
            status=table.get("status"),
        )
        for subject_area in table.get("subject_areas", []):
            subject_node = _add_node(graph, "subject_area", subject_area, label=subject_area)
            graph.add_edge(table_node, subject_node, relation="in_subject_area")
        for geo_level in table.get("supported_geo_levels", []):
            geo_node = _add_node(graph, "geo_level", geo_level, label=geo_level)
            graph.add_edge(table_node, geo_node, relation="supports_geo_level")


def _build_metric_nodes(graph: Any, catalogs: dict[str, dict[str, Any]]) -> None:
    for metric in catalogs["metric_catalog"]["metrics"]:
        metric_id = metric["metric_id"]
        metric_node = _add_node(
            graph,
            "metric",
            metric_id,
            label=metric_id,
            status=metric.get("status"),
            growth_eligible=metric.get("growth_eligible"),
        )
        table_node = _add_node(graph, "table", metric["source_table"], label=metric["source_table"])
        graph.add_edge(metric_node, table_node, relation="from_table", column=metric.get("source_column"))
        for subject_area in metric.get("subject_areas", []):
            subject_node = _add_node(graph, "subject_area", subject_area, label=subject_area)
            graph.add_edge(metric_node, subject_node, relation="in_subject_area")
        for theme_id in metric.get("themes", []):
            theme_node = _add_node(graph, "theme", theme_id, label=theme_id)
            graph.add_edge(metric_node, theme_node, relation="tagged_to_theme")
        for geo_level in metric.get("valid_geo_levels", []):
            geo_node = _add_node(graph, "geo_level", geo_level, label=geo_level)
            graph.add_edge(metric_node, geo_node, relation="valid_for_geo_level")


def _build_geography_nodes(graph: Any, catalogs: dict[str, dict[str, Any]]) -> None:
    for geo in catalogs["geography_catalog"]["geo_levels"]:
        _add_node(
            graph,
            "geo_level",
            geo["geo_level"],
            label=geo.get("display_name", geo["geo_level"]),
            supported_in_mvp=geo.get("supported_in_mvp"),
            hierarchy_rank=geo.get("hierarchy_rank"),
        )

    for edge in catalogs["geography_catalog"]["hierarchy_edges"]:
        child = _add_node(graph, "geo_level", edge["child_geo_level"], label=edge["child_geo_level"])
        parent = _add_node(graph, "geo_level", edge["parent_geo_level"], label=edge["parent_geo_level"])
        graph.add_edge(
            child,
            parent,
            relation="rolls_up_to",
            relationship_type=edge.get("relationship_type"),
            valid_for_rollup=edge.get("valid_for_rollup"),
            source_table=edge.get("source_table"),
        )


def _build_join_nodes(graph: Any, catalogs: dict[str, dict[str, Any]]) -> None:
    join_rules = catalogs["join_catalog"].get("non_standard_joins", catalogs["join_catalog"].get("join_rules", []))
    for join_rule in join_rules:
        left = _add_node(graph, "table", join_rule["left_table"], label=join_rule["left_table"])
        right = _add_node(graph, "table", join_rule["right_table"], label=join_rule["right_table"])
        graph.add_edge(
            left,
            right,
            relation="joins_to",
            join_id=join_rule["join_id"],
            join_category=join_rule.get("join_category"),
            join_type=join_rule.get("join_type"),
            status=join_rule.get("status"),
        )


def _build_template_and_chart_nodes(graph: Any, catalogs: dict[str, dict[str, Any]]) -> None:
    for template in catalogs["query_templates"]["templates"]:
        template_id = template["template_id"]
        template_node = _add_node(graph, "template", template_id, label=template_id)
        for question_type in template.get("question_types", []):
            question_type_node = _add_node(graph, "question_type", question_type, label=question_type)
            graph.add_edge(question_type_node, template_node, relation="uses_template")

    for rule in catalogs["chart_rules"]["rules"]:
        rule_node = _add_node(graph, "chart_rule", rule["rule_id"], label=rule["rule_id"])
        question_type_node = _add_node(graph, "question_type", rule["question_type"], label=rule["question_type"])
        graph.add_edge(question_type_node, rule_node, relation="mapped_to_chart_rule")
        for chart_type in rule.get("approved_chart_types", []):
            chart_node = _add_node(graph, "chart_type", chart_type, label=chart_type)
            graph.add_edge(rule_node, chart_node, relation="approved_chart")
        for chart_type in rule.get("fallback_chart_types", []):
            chart_node = _add_node(graph, "chart_type", chart_type, label=chart_type)
            graph.add_edge(rule_node, chart_node, relation="fallback_chart")


def _build_theme_and_intelligence_nodes(graph: Any, catalogs: dict[str, dict[str, Any]]) -> None:
    for theme in catalogs["theme_catalog"]["themes"]:
        theme_node = _add_node(graph, "theme", theme["theme_id"], label=theme.get("display_name", theme["theme_id"]))
        for topic in theme.get("topics", []):
            topic_node = _add_node(graph, "topic", topic["topic_id"], label=topic.get("display_name", topic["topic_id"]))
            graph.add_edge(theme_node, topic_node, relation="has_topic")
            for metric_id in topic.get("metrics", []):
                metric_node = _add_node(graph, "metric", metric_id, label=metric_id)
                graph.add_edge(topic_node, metric_node, relation="uses_metric")

    for score in catalogs["intelligence_catalog"]["scores"]:
        score_node = _add_node(graph, "score", score["score_id"], label=score.get("display_name", score["score_id"]))
        theme_node = _add_node(graph, "theme", score["theme"], label=score["theme"])
        graph.add_edge(theme_node, score_node, relation="has_score")
        for metric in score.get("inputs", []):
            metric_node = _add_node(graph, "metric", metric["metric_id"], label=metric["metric_id"])
            graph.add_edge(score_node, metric_node, relation="score_input")
        for geo_level in score.get("valid_geo_levels", []):
            geo_node = _add_node(graph, "geo_level", geo_level, label=geo_level)
            graph.add_edge(score_node, geo_node, relation="score_valid_for_geo_level")


def _build_question_nodes(graph: Any, catalogs: dict[str, dict[str, Any]]) -> None:
    for question in catalogs["question_catalog"]["questions"]:
        question_id = question["question_id"]
        question_node = _add_node(graph, "question_pattern", question_id, label=question_id)
        question_type_node = _add_node(graph, "question_type", question["intent_type"], label=question["intent_type"])
        graph.add_edge(question_type_node, question_node, relation="has_question_pattern")
        for theme_id in question.get("themes", []):
            theme_node = _add_node(graph, "theme", theme_id, label=theme_id)
            graph.add_edge(question_node, theme_node, relation="question_for_theme")
        for metric_id in question.get("required_metrics", []):
            metric_node = _add_node(graph, "metric", metric_id, label=metric_id)
            graph.add_edge(question_node, metric_node, relation="requires_metric")
        for table_id in question.get("required_tables", []):
            table_node = _add_node(graph, "table", table_id, label=table_id)
            graph.add_edge(question_node, table_node, relation="requires_table")
        for geo_level in question.get("valid_geo_levels", []):
            geo_node = _add_node(graph, "geo_level", geo_level, label=geo_level)
            graph.add_edge(question_node, geo_node, relation="question_valid_for_geo_level")
        if question.get("default_template"):
            template_node = _add_node(graph, "template", question["default_template"], label=question["default_template"])
            graph.add_edge(question_node, template_node, relation="defaults_to_template")
        if question.get("default_chart"):
            chart_rule_node = _add_node(graph, "chart_rule", question["default_chart"], label=question["default_chart"])
            graph.add_edge(question_node, chart_rule_node, relation="defaults_to_chart_rule")


def _build_points_nodes(graph: Any, catalogs: dict[str, dict[str, Any]]) -> None:
    for point_set in catalogs["points_catalog"]["point_sets"]:
        point_node = _add_node(
            graph,
            "point_set",
            point_set["catalog_id"],
            label=point_set.get("display_name", point_set["catalog_id"]),
            status=point_set.get("status"),
        )
        for spatial_join in point_set.get("spatial_joins", []):
            geo_node = _add_node(graph, "geo_level", spatial_join["target_geo_level"], label=spatial_join["target_geo_level"])
            graph.add_edge(point_node, geo_node, relation="spatially_joins_to", method=spatial_join.get("method"))
        for source in point_set.get("sources", []):
            source_node = _add_node(graph, "source", source["source_id"], label=source["source_id"])
            graph.add_edge(point_node, source_node, relation="point_source")


def build_semantic_graph(catalogs: dict[str, dict[str, Any]]) -> Any:
    """Build a directed multigraph from semantic catalogs."""
    _require_dependencies()
    graph = nx.MultiDiGraph(name="semantic_layer")

    _build_table_nodes(graph, catalogs)
    _build_metric_nodes(graph, catalogs)
    _build_geography_nodes(graph, catalogs)
    _build_join_nodes(graph, catalogs)
    _build_template_and_chart_nodes(graph, catalogs)
    _build_theme_and_intelligence_nodes(graph, catalogs)
    _build_question_nodes(graph, catalogs)
    _build_points_nodes(graph, catalogs)

    return graph


def graph_summary(graph: Any) -> dict[str, Any]:
    _require_dependencies()
    counts: dict[str, int] = {}
    for _, attrs in graph.nodes(data=True):
        kind = attrs["kind"]
        counts[kind] = counts.get(kind, 0) + 1

    edge_counts: dict[str, int] = {}
    for _, _, attrs in graph.edges(data=True):
        relation = attrs["relation"]
        edge_counts[relation] = edge_counts.get(relation, 0) + 1

    return {
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "node_kinds": counts,
        "edge_relations": edge_counts,
    }


def graph_to_node_link_json(graph: Any) -> str:
    _require_dependencies()
    return json.dumps(json_graph.node_link_data(graph), indent=2)


def mermaid_from_graph(graph: Any) -> str:
    _require_dependencies()

    kind_order = [
        "table",
        "metric",
        "theme",
        "topic",
        "score",
        "question_pattern",
        "template",
        "chart_rule",
        "chart_type",
        "geo_level",
        "point_set",
        "source",
        "subject_area",
        "question_type",
    ]
    kind_labels = {
        "table": "Tables",
        "metric": "Metrics",
        "theme": "Themes",
        "topic": "Topics",
        "score": "Scores",
        "question_pattern": "Question Patterns",
        "template": "Templates",
        "chart_rule": "Chart Rules",
        "chart_type": "Chart Types",
        "geo_level": "Geographies",
        "point_set": "Point Sets",
        "source": "Sources",
        "subject_area": "Subject Areas",
        "question_type": "Question Types",
    }
    relation_labels = {
        "from_table": "from table",
        "in_subject_area": "subject area",
        "supports_geo_level": "supports",
        "valid_for_geo_level": "valid for",
        "rolls_up_to": "rolls up to",
        "joins_to": "joins to",
        "uses_template": "uses",
        "mapped_to_chart_rule": "maps to",
        "approved_chart": "approved",
        "fallback_chart": "fallback",
        "tagged_to_theme": "tagged to",
        "has_topic": "has topic",
        "uses_metric": "uses metric",
        "has_score": "has score",
        "score_input": "score input",
        "score_valid_for_geo_level": "score valid for",
        "has_question_pattern": "has question",
        "question_for_theme": "question for",
        "requires_metric": "requires metric",
        "requires_table": "requires table",
        "question_valid_for_geo_level": "question valid for",
        "defaults_to_template": "defaults to template",
        "defaults_to_chart_rule": "defaults to chart rule",
        "spatially_joins_to": "spatial join",
        "point_source": "source",
    }

    lines = ["flowchart LR"]
    by_kind: dict[str, list[tuple[str, dict[str, Any]]]] = {kind: [] for kind in kind_order}
    for node_id, attrs in sorted(graph.nodes(data=True), key=lambda item: (item[1]["kind"], item[1]["value"])):
        by_kind.setdefault(attrs["kind"], []).append((node_id, attrs))

    for kind in kind_order:
        nodes = by_kind.get(kind, [])
        if not nodes:
            continue
        lines.append(f"  subgraph {kind_labels.get(kind, kind)}")
        for node_id, attrs in nodes:
            safe_id = _mermaid_id(node_id)
            label = attrs.get("label", attrs["value"]).replace('"', "'")
            lines.append(f'    {safe_id}["{label}"]')
        lines.append("  end")

    for source, target, attrs in sorted(
        graph.edges(data=True),
        key=lambda item: (
            graph.nodes[item[0]]["kind"],
            graph.nodes[item[0]]["value"],
            attrs_sort_key(item[2]),
            graph.nodes[item[1]]["kind"],
            graph.nodes[item[1]]["value"],
        ),
    ):
        label = relation_labels.get(attrs["relation"], attrs["relation"]).replace('"', "'")
        lines.append(f"  {_mermaid_id(source)} -->|{label}| {_mermaid_id(target)}")

    return "\n".join(lines) + "\n"


def attrs_sort_key(attrs: dict[str, Any]) -> str:
    return str(attrs.get("relation", ""))


def _mermaid_id(node_id: str) -> str:
    return node_id.replace(":", "_").replace("-", "_")


def write_default_artifacts(base_dir: str | Path | None = None) -> dict[str, Path]:
    root = semantic_layer_dir(base_dir)
    artifacts_dir = root / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    catalogs = load_catalogs(root)
    graph = build_semantic_graph(catalogs)
    summary = graph_summary(graph)
    mermaid = mermaid_from_graph(graph)

    mermaid_path = artifacts_dir / "semantic_graph.mmd"
    mermaid_path.write_text(mermaid, encoding="utf-8")

    json_path = artifacts_dir / "semantic_graph.json"
    json_path.write_text(graph_to_node_link_json(graph), encoding="utf-8")

    summary_path = artifacts_dir / "semantic_graph_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    preview_path = artifacts_dir / "semantic_graph_preview.md"
    preview = (
        "# Semantic Graph Preview\n\n"
        "## Summary\n\n"
        f"```json\n{json.dumps(summary, indent=2)}\n```\n\n"
        "## Mermaid\n\n"
        f"```mermaid\n{mermaid}```\n"
    )
    preview_path.write_text(preview, encoding="utf-8")

    return {
        "mermaid": mermaid_path,
        "json": json_path,
        "summary": summary_path,
        "preview": preview_path,
    }
