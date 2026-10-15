"""Authoritative Site Intelligence section readiness and deferred-work cards."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping


class SectionReadiness(StrEnum):
    """Whether a section can appear in the client brief at this stage."""

    CLIENT_READY = "client_ready"
    PROVISIONAL = "provisional"
    WITHHELD = "withheld"
    METHOD_CANDIDATE = "method_candidate"


@dataclass(frozen=True)
class SectionDefinition:
    """One product section and the evidence gate controlling its use."""

    section_id: str
    workbook_label: str
    status: SectionReadiness
    client_eligible: bool
    source_contract: str
    known_issue: str
    promotion_gate: str
    owner: str


# Entries are finer-grained than the five legacy pages. Page contracts make
# legacy navigation traceable without making a page client-ready by itself.
SECTION_REGISTRY = (
    SectionDefinition("catchment_profile", "Catchment profile and compatible benchmarks", SectionReadiness.CLIENT_READY, True, "people.metric_summary and people.catchment_profile; only declared compatible benchmark rows", "Adapter reconciliation is required before display.", "Reconcile displayed values and source/vintage labels to the selected bundle.", "Catchment"),
    SectionDefinition("daytime_context", "Daytime jobs and workers", SectionReadiness.CLIENT_READY, True, "people.daytime_population", "Adapter reconciliation is required before display.", "Reconcile jobs/workers, year, and LEHD provenance to the selected bundle.", "Catchment"),
    SectionDefinition("poi_aadt", "POI mix and current AADT", SectionReadiness.PROVISIONAL, False, "place.poi_counts and place.frontage_segments", "POI category labels and current-traffic wording need source review.", "Review source labels and reader-facing descriptions.", "POI and Infrastructure"),
    SectionDefinition("environmental_screening", "Environmental screening", SectionReadiness.PROVISIONAL, False, "place.nri_catchment_scores, place.nfhl_site_zone, and place.nfhl_ring_shares", "Screening is not an access, insurance, or site-suitability conclusion.", "Approve method framing and client wording.", "Infrastructure"),
    SectionDefinition("market_employment_mix", "Market employment mix", SectionReadiness.PROVISIONAL, False, "market.employment_mix", "Unit and scale QA remains open.", "Verify units, scale, and presentation against the source contract.", "Market context"),
    SectionDefinition("housing_rent_trend", "Housing and rent trend", SectionReadiness.WITHHELD, False, "market.housing_context", "A non-empty validated series is not yet established.", "Provide a non-empty series with an approved source and validation.", "Market context"),
    SectionDefinition("gdp_mix", "GDP mix", SectionReadiness.WITHHELD, False, "market.gdp_mix", "Source, units, and share contract are not approved.", "Approve the GDP source and share contract.", "Market context"),
    SectionDefinition("frontage_traffic_trend", "Frontage traffic trend", SectionReadiness.WITHHELD, False, "place.frontage_trend", "Trend output has not rendered and reconciled as a reader-facing series.", "Render and reconcile the trend contract.", "Infrastructure"),
    SectionDefinition("barrier_water_adjustment", "Barrier and water adjustment", SectionReadiness.WITHHELD, False, "place.barrier_summary and place.ring_variants", "No routing or access claim is supported.", "Make a method decision on a companion view and its limitations.", "Catchment and Infrastructure"),
    SectionDefinition("dasymetric_weighting", "Dasymetric weighting", SectionReadiness.METHOD_CANDIDATE, False, "No default artifact; future method comparison only", "It is not an approved alternative to areal weighting.", "Test against areal weighting and approve a separate method contract.", "Catchment"),
    SectionDefinition("routed_reach", "Routed reach", SectionReadiness.METHOD_CANDIDATE, False, "No default artifact; future method comparison only", "Straight-line reach is not travel time, access, or commuting.", "Specify and validate a routed reach method before any access claim.", "Catchment"),
)

LEGACY_PAGE_CONTRACTS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "overview": ("site_identity", "overview", "map_manifest"),
    "people": ("people",),
    "place": ("place", "map_manifest"),
    "market": ("market",),
    "methods": ("methods", "section_status"),
})


def section_status_payload() -> Mapping[str, tuple[Mapping[str, object], ...] | Mapping[str, tuple[str, ...]]]:
    """Return immutable registry data for adapters and later Marimo consumers."""

    return MappingProxyType({
        "sections": tuple(MappingProxyType(asdict(section)) for section in SECTION_REGISTRY),
        "legacy_page_contracts": LEGACY_PAGE_CONTRACTS,
    })


def render_work_card(section: SectionDefinition) -> str | None:
    """Render a compact internal-only card for withheld method work."""

    if section.status not in {SectionReadiness.WITHHELD, SectionReadiness.METHOD_CANDIDATE}:
        return None
    return (
        f"### {section.workbook_label}\n\n"
        f"**Status:** {section.status.value}\n\n{section.known_issue}\n\n"
        f"**Source contract:** {section.source_contract}\n\n"
        f"**Promotion gate:** {section.promotion_gate}\n\n**Owner:** {section.owner}"
    )
