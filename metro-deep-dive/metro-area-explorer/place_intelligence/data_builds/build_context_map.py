"""Compatibility wrapper for the current context-map build bundle."""

from __future__ import annotations

from pathlib import Path
import sys

SECTION_ROOT = Path(__file__).resolve().parents[1]
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from data_builds.maps.build_context_map_assets import build_context_map_for_site, main


if __name__ == "__main__":
    raise SystemExit(main())
