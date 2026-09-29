#!/usr/bin/env python3
"""Compatibility wrapper around the shared benchmarking package."""

from pip_benchmarking import (
    benchmark_metric,
    benchmark_metric_bundle,
    connect,
    get_target_metric_surface,
    list_comparison_sets,
    load_db_path,
)

__all__ = [
    "connect",
    "load_db_path",
    "list_comparison_sets",
    "get_target_metric_surface",
    "benchmark_metric",
    "benchmark_metric_bundle",
]
