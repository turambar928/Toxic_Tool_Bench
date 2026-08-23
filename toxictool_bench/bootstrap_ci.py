#!/usr/bin/env python3
"""Bootstrap confidence intervals for ToxicBench result JSONL files."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any


METRICS = [
    "clean_tsr", "toxic_tsr", "delta_tsr", "toxic_bcr", "toxic_adr", "toxic_vr", "toxic_rr",
    "poison_delivery_rate",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def mean_bool(rows: list[dict[str, Any]], metric: str) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if row.get("metrics", {}).get(metric)) / len(rows)


def was_exposed(row: dict[str, Any]) -> bool:
    metrics = row.get("metrics", {})
    if "poison_exposed" in metrics:
        return bool(metrics["poison_exposed"])
    return any(event.get("was_poisoned") for event in row.get("tool_events", []))


def summarize(rows: list[dict[str, Any]]) -> dict[str, float]:
    clean = [row for row in rows if row.get("environment") == "clean"]
    toxic = [row for row in rows if row.get("environment") == "toxic"]
    exposed = [row for row in toxic if was_exposed(row)]
    clean_tsr = mean_bool(clean, "task_success")
    toxic_tsr = mean_bool(toxic, "task_success")
    return {
        "clean_tsr": clean_tsr,
        "toxic_tsr": toxic_tsr,
        "delta_tsr": clean_tsr - toxic_tsr,
        "toxic_bcr": mean_bool(exposed, "blind_compliance"),
        "toxic_adr": mean_bool(exposed, "anomaly_detection"),
        "toxic_vr": mean_bool(exposed, "validation"),
        "toxic_rr": mean_bool(exposed, "recovery"),
        "poison_delivery_rate": len(exposed) / len(toxic) if toxic else 0.0,
    }


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    frac = pos - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac


def bootstrap(rows: list[dict[str, Any]], iterations: int, rng: random.Random) -> dict[str, tuple[float, float]]:
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_task[str(row.get("task_id", ""))].append(row)
    task_ids = sorted(by_task)
    samples: dict[str, list[float]] = {metric: [] for metric in METRICS}
    for _ in range(iterations):
        sampled_rows: list[dict[str, Any]] = []
        for task_id in (rng.choice(task_ids) for _ in task_ids):
            sampled_rows.extend(by_task[task_id])
        summary = summarize(sampled_rows)
        for metric in METRICS:
            samples[metric].append(summary[metric])
    return {metric: (percentile(values, 0.025), percentile(values, 0.975)) for metric, values in samples.items()}


def analyze_file(path: Path, iterations: int, rng: random.Random) -> dict[str, Any]:
    rows = load_jsonl(path)
    if not rows:
        raise ValueError(f"No rows in {path}")
    point = summarize(rows)
    ci = bootstrap(rows, iterations, rng)
    sample = rows[0]
    out: dict[str, Any] = {
        "file": str(path),
        "model": sample.get("model", ""),
        "adapter": sample.get("adapter", ""),
        "family": sample.get("family", ""),
        "n_tasks": len({row.get("task_id") for row in rows}),
        "n_rows": len(rows),
    }
    for metric in METRICS:
        lo, hi = ci[metric]
        out[metric] = point[metric]
        out[f"{metric}_lo"] = lo
        out[f"{metric}_hi"] = hi
    return out


def write_csv(rows: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else []
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("results", nargs="+", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    rows = [analyze_file(path, args.iterations, rng) for path in args.results]
    write_csv(rows, args.output)
    print(args.output)


if __name__ == "__main__":
    main()
