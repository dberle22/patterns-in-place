"""Manifest-first, layer-specific readers and display assets for Site Intelligence."""

from __future__ import annotations

from dataclasses import dataclass
import csv
import json
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from site_bundle_adapter import AdapterResult, Availability, BundleMetadata


@dataclass(frozen=True)
class MapLayerDefinition:
    """Reader-facing contract for one optional site map layer."""

    layer_id: str
    relative_path: Path | None
    reader_label: str
    source: str
    vintage: str
    measurement: str
    geometry_limitation: str


@dataclass(frozen=True)
class MapLayerManifest:
    """Small manifest that describes files without reading their contents."""

    metadata: BundleMetadata
    site_point: Mapping[str, Any]
    view_state: Mapping[str, Any]
    layers: tuple[MapLayerDefinition, ...]


@dataclass(frozen=True)
class MapLayerResult:
    """One selected layer, never a preloaded collection of map products."""

    definition: MapLayerDefinition
    availability: Availability
    data: Mapping[str, Any] | tuple[Mapping[str, str], ...] | None
    reason: str | None
    bytes_on_disk: int | None


def load_map_manifest(result: AdapterResult) -> MapLayerManifest | None:
    """Build file descriptors from small map metadata only, never map contents."""

    if result.product != "map_manifest" or result.availability is not Availability.AVAILABLE or result.data is None:
        return None
    data = result.data
    map_dir = result.metadata.bundle_dir / "map"
    years, sources = data["tract_fill_years"], data["tract_fill_sources"]
    layers = [
        MapLayerDefinition("rings", Path("rings.geojson"), "Site rings", "legacy Place Intelligence catchment geometry", "bundle build", "apportioned reach geometry", "Straight-line Euclidean rings; not a travel-time or access area."),
        _tract_layer("pop_total", "Population context", "tract context, not a catchment total", "Tract display geometry; do not compare this distribution to a multi-tract catchment total.", years, sources),
        _tract_layer("median_hh_income", "Household income context", "tract context, not a catchment median", "Tract display geometry; contributing tract medians are not a catchment median.", years, sources),
        _tract_layer("median_home_value", "Home value context", "tract context, not a catchment median", "Tract display geometry; contributing tract medians are not a catchment median.", years, sources),
        _tract_layer("pct_ba_plus", "Education context", "tract context, not a catchment total", "Tract display geometry; do not compare this distribution to a multi-tract catchment total.", years, sources),
        MapLayerDefinition("pois", Path("poi_rows.csv"), "Points of interest", "legacy Place Intelligence POI extract", "bundle build", "direct point observations", "Point coverage and classification are limited to the legacy extract."),
        MapLayerDefinition("roads", Path("roads.geojson"), "Road context", "FDOT AADT segments", "bundle build", "direct roadway observations", "Road segments are context, not travel routing."),
        MapLayerDefinition("severed_area", Path("severed_area.geojson"), "Water-adjustment context", "legacy Place Intelligence geometry", "bundle build", "illustrative geometry", "No barrier or access adjustment is applied to the baseline catchment."),
        MapLayerDefinition("flood", Path("flood.geojson"), "Flood screening context", "NFHL service output", str(data["nfhl_service_status"]), "screening context", "Not an insurance, engineering, or site-suitability determination."),
    ]
    return MapLayerManifest(result.metadata, data["site_point"][0], data["view_state"], tuple(_with_availability(layer, map_dir) for layer in layers))


def load_map_layer(manifest: MapLayerManifest, layer_id: str) -> MapLayerResult:
    """Open exactly one requested layer after the lightweight manifest is loaded."""

    definition = next((layer for layer in manifest.layers if layer.layer_id == layer_id), None)
    if definition is None:
        definition = MapLayerDefinition(layer_id, None, layer_id, "unavailable", "unavailable", "unavailable", "unknown layer")
        return MapLayerResult(definition, Availability.UNAVAILABLE, None, "The requested layer is not in this bundle manifest.", None)
    if definition.relative_path is None:
        return MapLayerResult(definition, Availability.UNAVAILABLE, None, "The layer file is not available.", None)
    path = manifest.metadata.bundle_dir / "map" / definition.relative_path
    try:
        if path.suffix == ".csv":
            with path.open(newline="", encoding="utf-8") as handle:
                data = tuple(MappingProxyType(row) for row in csv.DictReader(handle))
        else:
            with path.open(encoding="utf-8") as handle:
                payload = json.load(handle)
            if not isinstance(payload, dict):
                raise ValueError("map JSON must be an object")
            data = MappingProxyType(payload)
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as error:
        return MapLayerResult(definition, Availability.UNAVAILABLE, None, str(error), None)
    return MapLayerResult(definition, Availability.AVAILABLE, data, None, path.stat().st_size)


def write_display_geojson(layer: MapLayerResult, destination: Path, *, max_features: int, max_bytes: int) -> MapLayerResult:
    """Write a bounded display-only derivative without editing analysis geometry."""

    if layer.availability is not Availability.AVAILABLE or not isinstance(layer.data, Mapping):
        return MapLayerResult(layer.definition, Availability.UNAVAILABLE, None, "Only an available GeoJSON layer can produce a display asset.", None)
    features = layer.data.get("features")
    if not isinstance(features, (list, tuple)):
        return MapLayerResult(layer.definition, Availability.UNAVAILABLE, None, "The selected layer is not a GeoJSON feature collection.", None)
    selected = []
    for feature in features[:max_features]:
        candidate = {"type": "FeatureCollection", "features": selected + [feature]}
        if len(json.dumps(candidate, separators=(",", ":")).encode("utf-8")) > max_bytes:
            break
        selected.append(feature)
    output = {
        "type": "FeatureCollection",
        "features": selected,
        "display_metadata": {
            "source_layer": layer.definition.layer_id,
            "source_bytes": layer.bytes_on_disk,
            "source_feature_count": len(features),
            "display_feature_count": len(selected),
            "max_features": max_features,
            "max_bytes": max_bytes,
            "geometry_limitation": "Display-only feature cap; analytical source geometry is unchanged.",
        },
    }
    encoded = json.dumps(output, separators=(",", ":"))
    if len(encoded.encode("utf-8")) > max_bytes:
        return MapLayerResult(layer.definition, Availability.UNAVAILABLE, None, "Display metadata exceeds the requested byte limit.", None)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(encoded, encoding="utf-8")
    return MapLayerResult(layer.definition, Availability.AVAILABLE, MappingProxyType(output), None, len(encoded.encode("utf-8")))


def _tract_layer(metric: str, label: str, measurement: str, limitation: str, years: Mapping[str, Any], sources: Mapping[str, Any]) -> MapLayerDefinition:
    return MapLayerDefinition(f"tract_fill_{metric}", Path(f"tract_fill_{metric}.geojson"), label, str(sources.get(metric, "unavailable")), str(years.get(metric, "unavailable")), measurement, limitation)


def _with_availability(layer: MapLayerDefinition, map_dir: Path) -> MapLayerDefinition:
    """Check existence only; `Path.is_file` does not open heavy map contents."""

    if layer.relative_path and (map_dir / layer.relative_path).is_file():
        return layer
    return MapLayerDefinition(layer.layer_id, None, layer.reader_label, layer.source, layer.vintage, layer.measurement, layer.geometry_limitation)
