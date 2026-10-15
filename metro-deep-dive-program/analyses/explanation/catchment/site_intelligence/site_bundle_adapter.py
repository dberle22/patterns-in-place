"""Read-only compatibility adapters for legacy Place Intelligence site bundles.

The adapter is deliberately a boundary, rather than a second implementation of
Catchment or a copy of the legacy Streamlit payload readers.  It only reads
already-materialized files, validates the small contracts needed by the future
workbook, and returns an explicit state when a product cannot be shown.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import json
import os
from pathlib import Path
import sys
from types import MappingProxyType
from typing import Any, Mapping


SECTION_ROOT = Path(__file__).resolve().parent
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from site_section_registry import section_status_payload


class Availability(StrEnum):
    """Truthful display state for one artifact-backed product."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    INVALID = "invalid"
    EMPTY = "empty"


@dataclass(frozen=True)
class BundleMetadata:
    """Manifest-derived provenance attached to every adapter result."""

    bundle_dir: Path
    site_id: str | None
    built_at_utc: str | None
    manifest: Mapping[str, Any]


@dataclass(frozen=True)
class AdapterResult:
    """An immutable product payload with availability and bundle provenance."""

    product: str
    availability: Availability
    data: Mapping[str, Any] | None
    reason: str | None
    metadata: BundleMetadata
    source_years: tuple[str | int, ...]
    provenance: tuple[str, ...]


# These are the page-level JSON contracts observed in the complete Baymeadows
# bundle.  Row-shaped values are validated separately so a missing source
# column is never rendered as a fabricated zero.
PRODUCT_CONTRACTS: Mapping[str, Mapping[str, tuple[str, ...]]] = MappingProxyType({
    "overview": MappingProxyType({
        "required_keys": ("site", "resolved_site", "page_meta", "site_cards", "headline_table", "flags"),
        "required_rows": ("headline_table",),
        "row_columns": MappingProxyType({"headline_table": ("metric", "primary_value", "primary_year", "source_table")}),
    }),
    "people": MappingProxyType({
        "required_keys": ("site", "metric_summary", "catchment_profile", "daytime_population"),
        "required_rows": ("metric_summary", "catchment_profile", "daytime_population"),
        "row_columns": MappingProxyType({
            "metric_summary": ("metric", "primary_value", "primary_year", "source_table"),
            "catchment_profile": ("metric", "value", "year", "source_table"),
            "daytime_population": ("ring_mi", "year", "jobs_total", "workers_total"),
        }),
    }),
    "place": MappingProxyType({
        "required_keys": ("poi_counts", "barrier_summary", "ring_variants", "frontage_segments", "frontage_trend", "ranked_segments_1mi", "d4_meta", "nri_catchment_scores", "nfhl_site_zone", "nfhl_ring_shares", "d5_meta"),
        "required_rows": ("poi_counts",),
        "row_columns": MappingProxyType({"poi_counts": ("ring_mi", "poi_class", "count")}),
    }),
    "market": MappingProxyType({
        "required_keys": ("employment_mix", "gdp_mix", "housing_context", "meta"),
        "required_rows": ("employment_mix",),
        "row_columns": MappingProxyType({"employment_mix": ("year", "sector_id", "share_value", "raw_value", "source")}),
    }),
    "methods": MappingProxyType({
        "required_keys": ("site", "resolved_site", "coverage_diagnostic", "skip_reasons", "source_vintages", "method_notes"),
        "required_rows": ("coverage_diagnostic", "source_vintages"),
        "row_columns": MappingProxyType({
            "coverage_diagnostic": ("ring_mi", "intersecting_tract_count", "total_weight_captured"),
            "source_vintages": ("metric_label", "year", "source_table"),
        }),
    }),
    "map_manifest": MappingProxyType({
        "required_keys": ("site_point", "view_state", "tract_fill_years", "tract_fill_sources", "nfhl_service_status", "nfhl_service_error"),
        "required_rows": (),
        "row_columns": MappingProxyType({}),
    }),
})

PRODUCT_FILES = MappingProxyType({
    "overview": Path("overview.json"),
    "people": Path("people.json"),
    "place": Path("place.json"),
    "market": Path("market_page.json"),
    "methods": Path("methods.json"),
    "map_manifest": Path("map/meta.json"),
})


def discover_bundle(site_id: str, artifact_root: Path | None = None) -> Path | None:
    """Find one complete legacy bundle using the temporary documented rule.

    An explicit root wins.  Otherwise, an environment-configured published root
    wins, then the checked-in cloud bundle, then exactly one local market output.
    Ambiguous local matches are intentionally unavailable rather than guessed.
    """

    if artifact_root is not None:
        candidate = artifact_root / site_id
        return candidate if (candidate / "manifest.json").is_file() else None

    repo_root = Path(__file__).resolve().parents[5]
    candidates: list[Path] = []
    environment_root = os.environ.get("SITE_INTELLIGENCE_ARTIFACT_ROOT", "").strip()
    if environment_root:
        candidates.append(Path(environment_root).expanduser() / site_id)
    legacy_root = repo_root / "metro-deep-dive/metro-area-explorer/place_intelligence"
    candidates.append(legacy_root / "cloud_bundle/site_artifacts" / site_id)
    local_matches = sorted(legacy_root.glob(f"outputs/*/site_artifacts/{site_id}"))
    candidates.extend(local_matches if len(local_matches) == 1 else [])
    for candidate in candidates:
        if (candidate / "manifest.json").is_file():
            return candidate
    return None


def load_bundle(bundle_dir: Path) -> Mapping[str, AdapterResult]:
    """Load every Epic 1 product from one explicitly selected artifact directory."""

    metadata = _bundle_metadata(bundle_dir)
    return MappingProxyType({
        "site_identity": _load_identity(bundle_dir, metadata),
        **{product: _load_json_product(product, bundle_dir, metadata) for product in PRODUCT_FILES},
        "section_status": _section_status(metadata),
    })


def _load_identity(bundle_dir: Path, metadata: BundleMetadata) -> AdapterResult:
    """Combine authored and resolved site identity without inventing coordinates."""

    product = "site_identity"
    site = _read_json(bundle_dir / "site.json")
    resolved = _read_json(bundle_dir / "resolved_site.json")
    if site is None or resolved is None:
        return _unavailable(product, metadata, "site.json or resolved_site.json is missing or unreadable")
    required_site = {"site_id", "address", "rings_mi", "primary_ring_mi", "lat", "lon", "geocode_source"}
    required_resolved = {"lat", "lon", "matched_address", "match_type", "geocode_source"}
    missing = sorted(required_site - site.keys()) + sorted(required_resolved - resolved.keys())
    if missing:
        return _invalid(product, metadata, f"identity contract is missing: {', '.join(missing)}", {"site": site, "resolved_site": resolved})
    return _available(product, metadata, {"site": site, "resolved_site": resolved})


def _load_json_product(product: str, bundle_dir: Path, metadata: BundleMetadata) -> AdapterResult:
    """Validate one legacy JSON product while preserving its original payload."""

    payload = _read_json(bundle_dir / PRODUCT_FILES[product])
    if payload is None:
        return _unavailable(product, metadata, f"{PRODUCT_FILES[product]} is missing or unreadable")
    contract = PRODUCT_CONTRACTS[product]
    missing = sorted(set(contract["required_keys"]) - payload.keys())
    if missing:
        return _invalid(product, metadata, f"contract keys are missing: {', '.join(missing)}", payload)
    empty = [key for key in contract["required_rows"] if not isinstance(payload[key], list) or not payload[key]]
    if empty:
        return _empty(product, metadata, f"required product rows are empty: {', '.join(empty)}", payload)
    missing_columns = []
    for row_name, columns in contract["row_columns"].items():
        rows = payload[row_name]
        if rows and isinstance(rows, list) and isinstance(rows[0], dict):
            absent = sorted(set(columns) - rows[0].keys())
            if absent:
                missing_columns.append(f"{row_name}.{', '.join(absent)}")
    if missing_columns:
        return _invalid(product, metadata, f"row columns are missing: {'; '.join(missing_columns)}", payload)
    return _available(product, metadata, payload)


def _section_status(metadata: BundleMetadata) -> AdapterResult:
    """Expose the program-owned readiness registry alongside bundle provenance."""

    return _available("section_status", metadata, section_status_payload())


def _bundle_metadata(bundle_dir: Path) -> BundleMetadata:
    """Read manifest once so even unavailable products retain build provenance."""

    manifest = _read_json(bundle_dir / "manifest.json") or {}
    return BundleMetadata(
        bundle_dir=bundle_dir,
        site_id=manifest.get("site_id"),
        built_at_utc=manifest.get("built_at_utc"),
        manifest=_freeze(manifest),
    )


def _available(product: str, metadata: BundleMetadata, payload: Mapping[str, Any]) -> AdapterResult:
    """Attach source years and provenance found in the unmodified payload."""

    years, provenance = _source_metadata(payload)
    return AdapterResult(product, Availability.AVAILABLE, _freeze(payload), None, metadata, years, provenance)


def _unavailable(product: str, metadata: BundleMetadata, reason: str) -> AdapterResult:
    return AdapterResult(product, Availability.UNAVAILABLE, None, reason, metadata, (), ())


def _invalid(product: str, metadata: BundleMetadata, reason: str, payload: Mapping[str, Any]) -> AdapterResult:
    years, provenance = _source_metadata(payload)
    return AdapterResult(product, Availability.INVALID, _freeze(payload), reason, metadata, years, provenance)


def _empty(product: str, metadata: BundleMetadata, reason: str, payload: Mapping[str, Any]) -> AdapterResult:
    years, provenance = _source_metadata(payload)
    return AdapterResult(product, Availability.EMPTY, _freeze(payload), reason, metadata, years, provenance)


def _read_json(path: Path) -> Mapping[str, Any] | None:
    """Return only object-shaped JSON; malformed or array payloads are unavailable."""

    try:
        with path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _source_metadata(payload: Mapping[str, Any]) -> tuple[tuple[str | int, ...], tuple[str, ...]]:
    """Collect declared years and source labels without assigning a substitute vintage."""

    years: set[str | int] = set()
    provenance: set[str] = set()

    def visit(value: Any, key: str | None = None) -> None:
        if isinstance(value, Mapping):
            for child_key, child_value in value.items():
                visit(child_value, child_key)
        elif isinstance(value, (list, tuple)):
            for child_value in value:
                visit(child_value, key)
        elif value not in (None, "") and key:
            if key == "year" or key.endswith("_year"):
                if isinstance(value, (str, int)) and not isinstance(value, bool):
                    years.add(value)
            if key in {"source", "source_table", "source_system", "source_citation", "geocode_source"}:
                if isinstance(value, str):
                    provenance.add(value)

    visit(payload)
    return tuple(sorted(years, key=str)), tuple(sorted(provenance))


def _freeze(value: Any) -> Any:
    """Make returned JSON structurally immutable to reinforce the read-only boundary."""

    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(child) for key, child in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(child) for child in value)
    return value
