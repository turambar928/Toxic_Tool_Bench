#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


TASK_FILES = [
    Path("toxictool_bench/tasks/numerical_iclr2027.jsonl"),
    Path("toxictool_bench/tasks/semantic_schema_iclr2027.jsonl"),
    Path("toxictool_bench/tasks/realistic_extension_iclr2027.jsonl"),
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def clean_multiline(value: Any) -> str:
    return "\n".join(line.rstrip() for line in str(value).splitlines())


def load_manifest_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for item in csv.DictReader(handle):
            for row in read_jsonl(Path(item["path"])):
                if any(event.get("was_poisoned") for event in row.get("tool_events", [])):
                    row["_source_file"] = item["path"]
                    row["_probability"] = item["poison_probability"]
                    rows.append(row)
    return rows


def stratified_sample(rows: list[dict[str, Any]], per_suite: int, seed: int) -> list[dict[str, Any]]:
    by_suite: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_suite[str(row["family"])].append(row)
    rng = random.Random(seed)
    selected: list[dict[str, Any]] = []
    for suite in sorted(by_suite):
        strata: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for row in by_suite[suite]:
            strata[(str(row["adapter"]), str(row["_probability"]))].append(row)
        queues: list[deque[dict[str, Any]]] = []
        for key in sorted(strata):
            candidates = strata[key]
            rng.shuffle(candidates)
            queues.append(deque(candidates))
        rng.shuffle(queues)
        suite_selected: list[dict[str, Any]] = []
        while queues and len(suite_selected) < per_suite:
            next_round: list[deque[dict[str, Any]]] = []
            for queue in queues:
                if queue and len(suite_selected) < per_suite:
                    suite_selected.append(queue.popleft())
                if queue:
                    next_round.append(queue)
            queues = next_round
        if len(suite_selected) != per_suite:
            raise ValueError(f"Suite {suite!r} has only {len(suite_selected)} exposed rows; need {per_suite}.")
        selected.extend(suite_selected)
    rng.shuffle(selected)
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a blinded two-annotator ToxicBench audit packet.")
    parser.add_argument("--manifest", type=Path, default=Path("toxictool_bench/results/verification_stress_manifest.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("toxictool_bench/human_audit_v2"))
    parser.add_argument("--per-suite", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260831)
    args = parser.parse_args()

    tasks = {task["task_id"]: task for path in TASK_FILES for task in read_jsonl(path)}
    sample = stratified_sample(load_manifest_rows(args.manifest), args.per_suite, args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    evidence_rows, key_rows = [], []
    for index, row in enumerate(sample, 1):
        blind_id = f"TB-AUD-{index:03d}"
        task = tasks[str(row["task_id"])]
        evidence_rows.append({
            "blind_id": blind_id,
            "family": row["family"],
            "user_query": clean_multiline(task["user_query"]),
            "oracle_json": json.dumps(task.get("oracle", {}), ensure_ascii=True, sort_keys=True),
            "poison_type": row.get("poison", {}).get("type", ""),
            "severity": row.get("poison", {}).get("severity", ""),
            "final_answer": clean_multiline(row.get("final_answer", "")),
            "tool_events_json": json.dumps(row.get("tool_events", []), ensure_ascii=True),
        })
        metrics = row.get("metrics", {})
        key_rows.append({
            "blind_id": blind_id,
            "source_file": row["_source_file"],
            "task_id": row["task_id"],
            "adapter": row["adapter"],
            "model": row["model"],
            "poison_probability": row["_probability"],
            **{f"scorer_{label}": int(bool(metrics.get(name))) for label, name in {
                "bcr": "blind_compliance", "adr": "anomaly_detection", "vr": "validation", "rr": "recovery"
            }.items()},
        })
    write_csv(args.output_dir / "evidence.csv", evidence_rows)
    write_csv(args.output_dir / "key.csv", key_rows)
    label_rows = [{"blind_id": row["blind_id"], "bcr": "", "adr": "", "vr": "", "rr": "", "notes": ""} for row in evidence_rows]
    write_csv(args.output_dir / "annotator_a.csv", label_rows)
    write_csv(args.output_dir / "annotator_b.csv", label_rows)
    print(f"Wrote {len(sample)} blinded trajectories to {args.output_dir}")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
