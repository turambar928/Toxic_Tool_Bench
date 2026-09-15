#!/usr/bin/env python3
"""Describe post-poison evidence states in the fixed defense trajectories.

This is a descriptive re-analysis of existing logs. It does not estimate a
causal contribution of clean evidence because route selection is endogenous.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from build_defense_paired_analysis import DEFAULT_MANIFEST, load_runs, write_csv


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "toxictool_bench/results/leakage_free_defense_route_mechanism.csv"


def state(row: dict) -> str:
    events = row.get("tool_events", [])
    poisoned = [i for i, event in enumerate(events) if event.get("was_poisoned")]
    if not poisoned:
        return "no_poison_observed"
    first = poisoned[0]
    later = events[first + 1 :]
    if not later:
        return "no_post_poison_event"
    if any(event.get("was_poisoned") is False for event in later):
        return "post_poison_clean_observation"
    return "post_poison_observations_poisoned"


def metric(row: dict, name: str) -> float:
    return float(bool(row.get("metrics", {}).get(name)))


def main() -> None:
    runs = load_runs(DEFAULT_MANIFEST)
    grouped = defaultdict(list)
    for (suite, adapter, environment), rows in runs.items():
        if environment != "toxic":
            continue
        for row in rows.values():
            if row.get("metrics", {}).get("poison_exposed"):
                grouped[(suite, adapter, state(row))].append(row)
    output = []
    for (suite, adapter, evidence_state), rows in sorted(grouped.items()):
        n = len(rows)
        output.append({
            "suite": suite,
            "adapter": adapter,
            "post_poison_evidence_state": evidence_state,
            "n_exposed": n,
            "poisoned_tsr": f"{sum(metric(r, 'task_success') for r in rows) / n:.4f}",
            "poison_adoption": f"{sum(metric(r, 'poison_adoption') for r in rows) / n:.4f}",
            "validated_poison_adoption": f"{sum(metric(r, 'validated_poison_adoption') for r in rows) / n:.4f}",
            "recovery": f"{sum(metric(r, 'recovery') for r in rows) / n:.4f}",
            "validation": f"{sum(metric(r, 'validation') for r in rows) / n:.4f}",
        })
    write_csv(OUTPUT, output)
    print(OUTPUT)


if __name__ == "__main__":
    main()
