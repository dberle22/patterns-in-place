"""CLI for generating semantic-layer graph artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from semantic_layer.graph_builder import (
    build_semantic_graph,
    graph_summary,
    load_catalogs,
    mermaid_from_graph,
    semantic_layer_dir,
    write_default_artifacts,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Visualize the semantic layer catalogs.")
    parser.add_argument(
        "--base-dir",
        default=None,
        help="Optional semantic_layer directory override.",
    )
    parser.add_argument(
        "--format",
        choices=["summary", "mermaid", "artifacts"],
        default="summary",
        help="Output mode.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    root = semantic_layer_dir(args.base_dir)
    if args.format == "artifacts":
        artifacts = write_default_artifacts(root)
        for name, path in artifacts.items():
            print(f"{name}: {path}")
        return

    catalogs = load_catalogs(root)
    graph = build_semantic_graph(catalogs)

    if args.format == "summary":
        print(json.dumps(graph_summary(graph), indent=2))
        return

    if args.format == "mermaid":
        print(mermaid_from_graph(graph))
        return

    raise ValueError(f"Unsupported format: {args.format}")


if __name__ == "__main__":
    main()
