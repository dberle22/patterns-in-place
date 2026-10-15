"""Render one fixed Site Intelligence client brief and its delivery manifest."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True, help="Empty or existing delivery directory.")
    parser.add_argument("--marimo", default=".venv-marimo/bin/marimo", help="Marimo executable used for deterministic exports.")
    parser.add_argument("--site-id", default="jacksonville_fl_baymeadows_v0", help="Built site identifier for this fixed render.")
    parser.add_argument("--title", default="Site Intelligence Brief", help="Brief title.")
    parser.add_argument("--audience", default="Client review", help="Brief audience label.")
    args = parser.parse_args()

    brief = Path(__file__).with_name("SITE_INTELLIGENCE_CLIENT_BRIEF.py")
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "site_intelligence_client_brief.html"
    pdf_path = output_dir / "site_intelligence_client_brief.pdf"
    config = {"site_id": args.site_id, "title": args.title, "audience": args.audience, "client_section_ids": ("catchment_profile", "daytime_context")}
    export_environment = {**os.environ, "SITE_INTELLIGENCE_BRIEF_SITE_ID": args.site_id, "SITE_INTELLIGENCE_BRIEF_TITLE": args.title, "SITE_INTELLIGENCE_BRIEF_AUDIENCE": args.audience}
    commands = [
        [args.marimo, "export", "html", str(brief), "--no-include-code", "--force", "--output", str(html_path)],
        [args.marimo, "export", "pdf", str(brief), "--no-include-inputs", "--force", "--output", str(pdf_path)],
    ]
    for command in commands:
        subprocess.run(command, check=True, env=export_environment)

    manifest = {
        "site_id": config["site_id"],
        "title": config["title"],
        "audience": config["audience"],
        "client_section_ids": config["client_section_ids"],
        "outputs": [{"filename": path.name, "bytes": path.stat().st_size, "sha256": _sha256(path)} for path in (html_path, pdf_path)],
    }
    (output_dir / "delivery_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    main()
