#!/usr/bin/env python3
"""Build paired defense deltas and exposure-denominator tables from the fixed manifest."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from evaluator import evaluate_run


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "toxictool_bench/results/leakage_free_defense_manifest.csv"
ADAPTERS = ("langgraph_react_full", "langgraph_react_double_pass", "langgraph_react_guarded", "langgraph_react_verification_only")
METRICS = ("task_success", "blind_compliance", "validation", "recovery")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def bootstrap(values: list[float], seed: int, rounds: int = 5000) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    rng = random.Random(seed)
    n = len(values)
    samples = sorted(mean([values[rng.randrange(n)] for _ in range(n)]) for _ in range(rounds))
    return samples[int(0.025 * rounds)], samples[int(0.975 * rounds) - 1]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_toxic(manifest: Path) -> dict[tuple[str, str], dict[str, dict[str, Any]]]:
    grouped: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    task_defs: dict[str, dict[str, Any]] = {}
    for spec in read_csv(manifest):
        task_paths = {
            "numerical_iclr2027": "toxictool_bench/tasks/numerical_iclr2027.jsonl",
            "semantic_schema_iclr2027": "toxictool_bench/tasks/semantic_schema_iclr2027.jsonl",
            "realistic_extension_iclr2027": "toxictool_bench/tasks/realistic_extension_iclr2027.jsonl",
        }.get(spec["suite"])
        if task_paths is None:
            raise ValueError(f"No task definition mapping for suite {spec['suite']}")
        for task_path in task_paths.split(";"):
            with (ROOT / task_path).open(encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        task = json.loads(line)
                        task_defs[task["task_id"]] = task
        suite, adapter = spec["suite"], spec["adapter"]
        for row in read_jsonl(ROOT / spec["path"]):
            if row.get("environment") != "toxic":
                continue
            task_id = str(row["task_id"])
            if task_id in grouped[(suite, adapter)]:
                raise ValueError(f"duplicate toxic task {suite}/{adapter}/{task_id}")
            row["metrics"] = evaluate_run(
                task_defs[task_id], row.get("final_answer", ""), row.get("tool_events", [])
            )
            grouped[(suite, adapter)][task_id] = row
    return grouped


def metric(row: dict[str, Any], name: str) -> float:
    metrics = row.get("metrics", {})
    if name == "poison_adoption":
        return float(bool(metrics.get("poison_exposed") and metrics.get("poison_adoption")))
    if name == "validated_poison_adoption":
        return float(bool(
            metrics.get("poison_exposed") and metrics.get("validated_poison_adoption")
        ))
    return float(bool(metrics.get(name)))


def build_exposure(rows: dict[tuple[str, str], dict[str, dict[str, Any]]]) -> list[dict[str, Any]]:
    output = []
    for (suite, adapter), tasks in sorted(rows.items()):
        exposed = [row for row in tasks.values() if row.get("metrics", {}).get("poison_exposed")]
        output.append({
            "suite": suite,
            "adapter": adapter,
            "model": next(iter(tasks.values())).get("model", "") if tasks else "",
            "n_toxic": len(tasks),
            "n_exposed": len(exposed),
            "pdr": f"{len(exposed) / len(tasks):.4f}" if tasks else "0.0000",
            "bcr": f"{mean([metric(row, 'blind_compliance') for row in exposed]):.4f}",
            "par": f"{mean([metric(row, 'poison_adoption') for row in exposed]):.4f}",
            "vpa": f"{mean([metric(row, 'validated_poison_adoption') for row in exposed]):.4f}",
            "adr": f"{mean([metric(row, 'anomaly_detection') for row in exposed]):.4f}",
            "vr": f"{mean([metric(row, 'validation') for row in exposed]):.4f}",
            "rr": f"{mean([metric(row, 'recovery') for row in exposed]):.4f}",
        })
    return output


def build_paired(rows: dict[tuple[str, str], dict[str, dict[str, Any]]], seed: int) -> list[dict[str, Any]]:
    output = []
    comparisons = (("langgraph_react_guarded", "langgraph_react_double_pass"), ("langgraph_react_verification_only", "langgraph_react_double_pass"))
    for suite in sorted({suite for suite, _ in rows}):
        for treatment, control in comparisons:
            left, right = rows.get((suite, treatment), {}), rows.get((suite, control), {})
            common = sorted(set(left) & set(right))
            for name in METRICS:
                ids = common
                if name == "blind_compliance":
                    ids = [task_id for task_id in common if left[task_id].get("metrics", {}).get("poison_exposed") and right[task_id].get("metrics", {}).get("poison_exposed")]
                deltas = [metric(left[task_id], name) - metric(right[task_id], name) for task_id in ids]
                lo, hi = bootstrap(deltas, seed + len(output))
                output.append({
                    "suite": suite,
                    "treatment": treatment,
                    "control": control,
                    "metric": "BCR" if name == "blind_compliance" else name,
                    "estimand": "treatment-minus-control",
                    "n_paired": len(ids),
                    "mean_delta": f"{mean(deltas):.4f}",
                    "ci95_lo": f"{lo:.4f}",
                    "ci95_hi": f"{hi:.4f}",
                })
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-exposure", type=Path, default=ROOT / "toxictool_bench/results/leakage_free_defense_exposure_denominators.csv")
    parser.add_argument("--output-paired", type=Path, default=ROOT / "toxictool_bench/results/leakage_free_defense_paired_ci.csv")
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()
    rows = load_toxic(args.manifest)
    write_csv(args.output_exposure, build_exposure(rows))
    write_csv(args.output_paired, build_paired(rows, args.seed))
    print(args.output_exposure)
    print(args.output_paired)


if __name__ == "__main__":
    main()
