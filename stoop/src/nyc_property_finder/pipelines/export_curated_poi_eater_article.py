"""Compatibility alias for the generic curated article export CLI."""

from __future__ import annotations

import sys

from nyc_property_finder.pipelines.export_curated_poi_article import main as generic_main


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--list-articles" in argv and "--publisher-filter" not in argv:
        argv.extend(["--publisher-filter", "Eater"])
    if "--publisher" not in argv:
        argv.extend(["--publisher", "Eater"])
    return generic_main(argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
