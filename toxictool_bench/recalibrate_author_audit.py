#!/usr/bin/env python3
"""Compare the current deterministic scorer with the released author audit."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from audit_agreement import agreement_for_label
from evaluator import evaluate_run


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "toxictool_bench/results"
TASKS = ROOT / "toxictool_bench/tasks"
LABELS = ("bcr", "adr", "vr", "rr")
METRIC_KEYS = {"bcr": "blind_compliance", "adr": "anomaly_detection", "vr": "validation", "rr": "recovery"}


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=RESULTS / "iclr2027_manual_audit_completed_stratified80.csv")
    parser.add_argument("--output-csv", type=Path, default=RESULTS / "strict_scorer_author_audit_comparison.csv")
    parser.add_argument("--output-json", type=Path, default=RESULTS / "strict_scorer_author_audit_agreement.json")
    args = parser.parse_args()

    tasks: dict[str, dict] = {}
    for path in TASKS.glob("*.jsonl"):
        for task in read_jsonl(path):
            tasks[task["task_id"]] = task
    with args.audit.open(newline="", encoding="utf-8") as handle:
        audit_rows = list(csv.DictReader(handle))

    output_rows: list[dict[str, str]] = []
    source_cache: dict[str, list[dict]] = {}
    for audit in audit_rows:
        source_name = audit["source_file"]
        source_cache.setdefault(source_name, read_jsonl(RESULTS / source_name))
        candidates = [
            row for row in source_cache[source_name]
            if row.get("task_id") == audit["task_id"] and row.get("environment") == "toxic"
        ]
        if len(candidates) != 1:
            raise ValueError(f"Expected one toxic row for {source_name}:{audit['task_id']}, found {len(candidates)}")
        row = candidates[0]
        metrics = evaluate_run(tasks[row["task_id"]], row.get("final_answer", ""), row.get("tool_events", []))
        out = {"source_file": source_name, "task_id": audit["task_id"], "family": audit["family"], "adapter": audit["adapter"]}
        for label, metric_key in METRIC_KEYS.items():
            out[f"current_scorer_{label}"] = str(int(metrics[metric_key]))
            out[f"author_{label}"] = audit[f"adjudicated_{label}"]
        output_rows.append(out)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(output_rows)
    agreement = {
        label: agreement_for_label(output_rows, f"current_scorer_{label}", f"author_{label}")
        for label in LABELS
    }
    args.output_json.write_text(json.dumps({"n": len(output_rows), "agreement": agreement}, indent=2) + "\n", encoding="utf-8")
    print(args.output_json)


if __name__ == "__main__":
    main()
