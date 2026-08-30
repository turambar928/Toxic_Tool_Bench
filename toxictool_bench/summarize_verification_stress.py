#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any

from bootstrap_ci import bootstrap, summarize, was_exposed


SUITES = {
    "numerical_iclr2027": 60,
    "semantic_schema_iclr2027": 60,
    "realistic_extension_iclr2027": 13,
}
ADAPTERS = [
    "langgraph_react_verification_only",
    "langgraph_react_double_pass",
    "langgraph_react_guarded",
]
PROBABILITIES = [("p025", 0.25), ("p050", 0.50), ("p075", 0.75), ("p100", 1.00)]


def read_rows(path: Path) -> list[dict[str, Any]]:
    try:
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError):
        return []


def select_chunk(directory: Path, adapter: str, model: str, start: int, limit: int) -> Path | None:
    pattern = f"*_{adapter}_{model}_toxic_start{start}_limit{limit}.jsonl"
    for path in sorted(directory.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True):
        rows = read_rows(path)
        if len(rows) == limit and len({row.get("task_id") for row in rows}) == limit:
            return path
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize the full repeated-poison stress matrix.")
    parser.add_argument("--root", type=Path, default=Path("toxictool_bench/results/verification_stress"))
    parser.add_argument("--model", default="claude-haiku-4-5-20251001")
    parser.add_argument("--output", type=Path, default=Path("toxictool_bench/results/verification_stress_summary.csv"))
    parser.add_argument("--manifest", type=Path, default=Path("toxictool_bench/results/verification_stress_manifest.csv"))
    parser.add_argument("--iterations", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260830)
    args = parser.parse_args()

    groups: list[tuple[str, float, str, list[dict[str, Any]]]] = []
    selected: list[tuple[str, float, str, int, int, Path]] = []
    missing: list[str] = []
    for suite, total in SUITES.items():
        for tag, probability in PROBABILITIES:
            directory = args.root / suite / tag
            for adapter in ADAPTERS:
                rows: list[dict[str, Any]] = []
                for start in range(0, total, 5):
                    limit = min(5, total - start)
                    path = select_chunk(directory, adapter, args.model, start, limit)
                    if path is None:
                        missing.append(f"{suite}:{tag}:{adapter}:start{start}:limit{limit}")
                        continue
                    chunk_rows = read_rows(path)
                    rows.extend(chunk_rows)
                    selected.append((suite, probability, adapter, start, limit, path))
                if len(rows) == total:
                    groups.append((suite, probability, adapter, rows))
    if missing:
        raise SystemExit("Missing complete stress chunks:\n" + "\n".join(missing))

    write_summary(groups, args.output, args.iterations, args.seed)
    write_manifest(selected, args.manifest)


def write_summary(groups, path: Path, iterations: int, seed: int) -> None:
    fields = [
        "suite", "poison_probability", "adapter", "n", "n_exposed", "poison_delivery_rate",
        "toxic_tsr", "toxic_tsr_lo", "toxic_tsr_hi", "bcr", "bcr_lo", "bcr_hi",
        "vr", "rr", "rr_lo", "rr_hi", "mean_elapsed_seconds",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for index, (suite, probability, adapter, rows) in enumerate(groups):
            point = summarize(rows)
            intervals = bootstrap(rows, iterations, random.Random(seed + index))
            exposed = sum(was_exposed(row) for row in rows)
            writer.writerow({
                "suite": suite,
                "poison_probability": f"{probability:.2f}",
                "adapter": adapter,
                "n": len(rows),
                "n_exposed": exposed,
                "poison_delivery_rate": f"{point['poison_delivery_rate']:.4f}",
                "toxic_tsr": f"{point['toxic_tsr']:.4f}",
                "toxic_tsr_lo": f"{intervals['toxic_tsr'][0]:.4f}",
                "toxic_tsr_hi": f"{intervals['toxic_tsr'][1]:.4f}",
                "bcr": f"{point['toxic_bcr']:.4f}",
                "bcr_lo": f"{intervals['toxic_bcr'][0]:.4f}",
                "bcr_hi": f"{intervals['toxic_bcr'][1]:.4f}",
                "vr": f"{point['toxic_vr']:.4f}",
                "rr": f"{point['toxic_rr']:.4f}",
                "rr_lo": f"{intervals['toxic_rr'][0]:.4f}",
                "rr_hi": f"{intervals['toxic_rr'][1]:.4f}",
                "mean_elapsed_seconds": f"{sum(float(row.get('elapsed_seconds', 0)) for row in rows) / len(rows):.2f}",
            })


def write_manifest(selected, path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["suite", "poison_probability", "adapter", "start_index", "limit", "path"])
        for row in selected:
            writer.writerow(row)


if __name__ == "__main__":
    main()
