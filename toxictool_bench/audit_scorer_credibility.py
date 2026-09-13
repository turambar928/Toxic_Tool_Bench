#!/usr/bin/env python3
"""Audit deterministic scoring against blinded labels and mixed oracle hits."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from evaluator import evaluate_run


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT = ROOT / "toxictool_bench/human_audit_v2/adjudicated_labels.csv"
DEFAULT_MANIFEST = ROOT / "toxictool_bench/results/paper_run_manifest.csv"
DEFAULT_REPORT = ROOT / "toxictool_bench/results/scorer_credibility_report.json"
DEFAULT_MIXED = ROOT / "toxictool_bench/results/scorer_mixed_oracle_hits.csv"
LABELS = ("bcr", "adr", "vr", "rr")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def binary(value: Any) -> int:
    return int(str(value).strip().lower() in {"1", "true", "yes"})


def classification_report(rows: list[dict[str, str]], label: str) -> dict[str, Any]:
    consensus_key = f"human_consensus_{label}"
    if consensus_key in rows[0]:
        evaluated = rows
        pairs = [(binary(row[f"scorer_{label}"]), binary(row[consensus_key])) for row in evaluated]
        n_disputed = 0
    else:
        evaluated = [row for row in rows if row[f"human_a_{label}"] == row[f"human_b_{label}"]]
        pairs = [(binary(row[f"scorer_{label}"]), binary(row[f"human_a_{label}"])) for row in evaluated]
        n_disputed = len(rows) - len(evaluated)
    tp = sum(s == h == 1 for s, h in pairs)
    fp = sum(s == 1 and h == 0 for s, h in pairs)
    fn = sum(s == 0 and h == 1 for s, h in pairs)
    tn = sum(s == h == 0 for s, h in pairs)
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / (tp + fn) if tp + fn else None
    f1 = 2 * precision * recall / (precision + recall) if precision and recall else None
    return {
        "n_evaluated": len(pairs),
        "n_disputed": n_disputed,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def load_tasks(manifest_rows: list[dict[str, str]]) -> dict[str, dict[str, Any]]:
    tasks: dict[str, dict[str, Any]] = {}
    for manifest in manifest_rows:
        for task_path in manifest["tasks"].split(";"):
            for task in read_jsonl(ROOT / task_path):
                tasks[task["task_id"]] = task
    return tasks


def audit_manifest(
    manifest_rows: list[dict[str, str]], tasks: dict[str, dict[str, Any]], mixed_path: Path
) -> dict[str, Any]:
    totals = Counter()
    by_experiment: dict[str, Counter] = defaultdict(Counter)
    mixed_rows: list[dict[str, Any]] = []
    seen_sources: set[str] = set()
    for spec in manifest_rows:
        source = ROOT / spec["source"]
        if str(source) in seen_sources:
            continue
        seen_sources.add(str(source))
        for row in read_jsonl(source):
            if row.get("environment") != "toxic":
                continue
            metrics = evaluate_run(tasks[row["task_id"]], row.get("final_answer", ""), row.get("tool_events", []))
            experiment = spec["experiment"]
            totals["toxic"] += 1
            by_experiment[experiment]["toxic"] += 1
            if metrics["poison_exposed"]:
                totals["exposed"] += 1
                by_experiment[experiment]["exposed"] += 1
            if metrics["poison_adoption"]:
                totals["poison_adoption"] += 1
                by_experiment[experiment]["poison_adoption"] += 1
            if metrics["task_success"] and metrics["poison_adoption"]:
                totals["mixed_clean_and_poisoned_hit"] += 1
                by_experiment[experiment]["mixed_clean_and_poisoned_hit"] += 1
                mixed_rows.append({
                    "experiment": experiment,
                    "suite": spec["suite"],
                    "source": spec["source"],
                    "task_id": row["task_id"],
                    "adapter": row.get("adapter", ""),
                    "model": row.get("model", ""),
                    "poison": row.get("poison", {}).get("type", ""),
                    "final_answer": row.get("final_answer", ""),
                })
    mixed_path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(mixed_rows[0]) if mixed_rows else [
        "experiment", "suite", "source", "task_id", "adapter", "model", "poison", "final_answer"
    ]
    with mixed_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(mixed_rows)
    return {
        "totals": dict(totals),
        "by_experiment": {key: dict(value) for key, value in sorted(by_experiment.items())},
        "mixed_hit_file": str(mixed_path.relative_to(ROOT)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--mixed-output", type=Path, default=DEFAULT_MIXED)
    args = parser.parse_args()
    audit_rows = read_csv(args.audit)
    manifest_rows = read_csv(args.manifest)
    report = {
        "audit_file": str(args.audit.relative_to(ROOT)),
        "manifest_file": str(args.manifest.relative_to(ROOT)),
        "human_consensus_note": "Precision/recall/F1 use all 120 rows: pre-adjudication agreements are retained and disputed label cells use the completed third-party adjudication. Pre-adjudication kappa remains unchanged.",
        "scorer_vs_human_consensus": {
            label: classification_report(audit_rows, label) for label in LABELS
        },
        "manifest_mixed_hit_audit": audit_manifest(manifest_rows, load_tasks(manifest_rows), args.mixed_output),
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.report)


if __name__ == "__main__":
    main()
