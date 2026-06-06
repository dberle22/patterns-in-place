"""Artifact checks for publisher output folders."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


EXPECTED_ARTIFACTS_BY_STEP = {
    "parse": ("query_plan.json",),
    "sql": ("query_plan.json", "result.sql", "result.csv", "answer.txt"),
    "chart": ("query_plan.json", "result.sql", "result.csv", "answer.txt", "chart.png"),
    "summarize": (
        "query_plan.json",
        "result.sql",
        "result.csv",
        "answer.txt",
        "chart.png",
        "post_draft.md",
    ),
}


@dataclass
class PackageCheck:
    """Simple completeness report for a question output folder."""

    output_dir: Path
    expected_files: list[str]
    present_files: list[str]
    missing_files: list[str]

    @property
    def is_complete(self) -> bool:
        return not self.missing_files


def verify_output_folder(output_dir: Path, step: str) -> PackageCheck:
    """Report which expected artifacts exist for the requested step."""

    if step not in EXPECTED_ARTIFACTS_BY_STEP:
        raise ValueError(f"Unsupported step for packaging check: {step}")
    expected = list(EXPECTED_ARTIFACTS_BY_STEP[step])
    present = sorted(path.name for path in output_dir.iterdir()) if output_dir.exists() else []
    missing = [name for name in expected if not (output_dir / name).exists()]
    return PackageCheck(
        output_dir=output_dir,
        expected_files=expected,
        present_files=present,
        missing_files=missing,
    )
