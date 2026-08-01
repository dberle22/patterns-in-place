"""Small profiling harness for standalone Place Intelligence page payloads."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
import sys


SECTION_ROOT = Path(__file__).resolve().parent
if str(SECTION_ROOT) not in sys.path:
    sys.path.insert(0, str(SECTION_ROOT))

from site_prep import (
    build_context_map_payload,
    build_market_context_payload,
    build_site_base_payload,
    build_d2_profile_payload,
    get_default_site_config_path,
    get_d3_context_payload,
    get_d4_traffic_payload,
    get_d5_flood_payload,
    load_site,
)


@dataclass
class TimedStep:
    label: str
    seconds: float


def _time_step(label: str, fn):
    start = perf_counter()
    value = fn()
    step = TimedStep(label=label, seconds=perf_counter() - start)
    print(f"{label}: {_format_seconds(step.seconds)}", flush=True)
    return value, step


def _format_seconds(seconds: float) -> str:
    return f"{seconds:.2f}s"


def main() -> int:
    site_config_path = get_default_site_config_path()
    site = load_site(str(site_config_path))
    steps: list[TimedStep] = []

    base, step = _time_step("build_site_base_payload", lambda: build_site_base_payload(site))
    steps.append(step)
    d2_payload, step = _time_step("build_d2_profile_payload", lambda: build_d2_profile_payload(site, base["weight_table"]))
    steps.append(step)
    d3_payload, step = _time_step("get_d3_context_payload", lambda: get_d3_context_payload(site, base["weight_table"]))
    steps.append(step)
    d4_payload, step = _time_step("get_d4_traffic_payload", lambda: get_d4_traffic_payload(site, cumulative_rings=base["cumulative_rings"]))
    steps.append(step)
    d5_payload, step = _time_step("get_d5_flood_payload", lambda: get_d5_flood_payload(site, base["weight_table"], cumulative_rings=base["cumulative_rings"]))
    steps.append(step)
    market_payload, step = _time_step("build_market_context_payload", lambda: build_market_context_payload(site))
    steps.append(step)

    _, step = _time_step(
        "build_context_map_payload[pop_total][no_flood]",
        lambda: build_context_map_payload(
            site,
            base["weight_table"],
            fill_metric="pop_total",
            include_flood_context=False,
        ),
    )
    steps.append(step)
    _, step = _time_step(
        "build_context_map_payload[pop_total][with_flood]",
        lambda: build_context_map_payload(
            site,
            base["weight_table"],
            fill_metric="pop_total",
            include_flood_context=True,
        ),
    )
    steps.append(step)

    page_totals = {
        "overview": step_lookup(steps, "build_site_base_payload") + step_lookup(steps, "build_d2_profile_payload") + step_lookup(steps, "get_d3_context_payload") + step_lookup(steps, "get_d5_flood_payload") + step_lookup(steps, "build_context_map_payload[pop_total][no_flood]"),
        "people": step_lookup(steps, "build_site_base_payload") + step_lookup(steps, "build_d2_profile_payload") + step_lookup(steps, "get_d3_context_payload"),
        "place": step_lookup(steps, "get_d3_context_payload") + step_lookup(steps, "get_d4_traffic_payload") + step_lookup(steps, "get_d5_flood_payload") + step_lookup(steps, "build_context_map_payload[pop_total][with_flood]"),
        "market": step_lookup(steps, "build_market_context_payload"),
        "methods": step_lookup(steps, "build_site_base_payload") + step_lookup(steps, "build_d2_profile_payload"),
    }

    print(f"Profile date: 2026-08-01")
    print(f"Site config: {site_config_path}")
    print("")
    print("Timed prep steps")
    for step in steps:
        print(f"- {step.label}: {_format_seconds(step.seconds)}")
    print("")
    print("Estimated page payload totals")
    for label, seconds in page_totals.items():
        print(f"- {label}: {_format_seconds(seconds)}")
    print("")
    print("Payload shapes")
    print(f"- D2 catchment rows: {len(d2_payload['catchment_profile'])}")
    print(f"- D3 barrier rows: {len(d3_payload['barrier_summary'])}")
    print(f"- D4 frontage rows: {len(d4_payload['frontage_segments'])}")
    print(f"- D5 flood share rows: {len(d5_payload['nfhl_ring_shares'])}")
    print(f"- Market housing rows: {len(market_payload['housing_context'])}")
    return 0


def step_lookup(steps: list[TimedStep], label: str) -> float:
    """Read one timed step by label."""

    for step in steps:
        if step.label == label:
            return step.seconds
    raise KeyError(label)


if __name__ == "__main__":
    raise SystemExit(main())
