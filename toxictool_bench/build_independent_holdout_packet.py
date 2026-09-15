#!/usr/bin/env python3
"""Build a frozen, method-blinded human holdout packet from existing logs.

The packet is deliberately separate from human_audit_v2 and human_review_v3.
It must be built once, before any annotator sees labels or scorer output. The
script uses existing trajectories only; it never calls a model.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CORE_MANIFEST = ROOT / "toxictool_bench/results/leakage_free_defense_manifest.csv"
STRESS_MANIFEST = ROOT / "toxictool_bench/results/verification_stress_manifest.csv"
CROSS_MANIFEST = ROOT / "toxictool_bench/results/iclr2027_claude-sonnet-4-6_expanded_cross_agent_manifest.csv"
TASK_FILES = {
    "numerical_iclr2027": ROOT / "toxictool_bench/tasks/numerical_iclr2027.jsonl",
    "semantic_schema_iclr2027": ROOT / "toxictool_bench/tasks/semantic_schema_iclr2027.jsonl",
}
ADAPTERS = (
    "langgraph_react_full",
    "langgraph_react_double_pass",
    "langgraph_react_verification_only",
    "langgraph_react_guarded",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_manifest_runs(manifest: Path, *, p1_only: bool = False) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in read_csv(manifest):
        if p1_only and spec.get("poison_probability") != "1.0":
            continue
        path = ROOT / spec["path"]
        for row in read_jsonl(path):
            row = dict(row)
            row["_manifest"] = str(manifest.relative_to(ROOT))
            row["_source"] = spec["path"]
            row["_suite"] = spec["suite"]
            row["_probability"] = spec.get("poison_probability", "poison_once")
            rows.append(row)
    return rows


def task_defs() -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for path in TASK_FILES.values():
        for task in read_jsonl(path):
            output[task["task_id"]] = task
    return output


def prior_task_ids() -> set[str]:
    path = ROOT / "toxictool_bench/human_audit_v2/key.csv"
    return {row["task_id"] for row in read_csv(path)}


def index(rows: list[dict[str, Any]], keys: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, Any]]:
    result: dict[tuple[str, ...], dict[str, Any]] = {}
    for row in rows:
        key = tuple(str(row.get(k, "")) for k in keys)
        if key in result:
            raise ValueError(f"duplicate trajectory for {key}")
        result[key] = row
    return result


REDACTIONS = (
    "langgraph_react_full", "langgraph_react_double_pass",
    "langgraph_react_verification_only", "langgraph_react_guarded",
    "LangGraph ReAct", "LangGraph", "Guarded verification", "Guarded Verification",
    "Verification-only", "Double-pass", "PandasAI", "AutoGen", "smolagents",
)


def scrub(text: str) -> str:
    for token in sorted(REDACTIONS, key=len, reverse=True):
        text = re.sub(re.escape(token), "[REDACTED_METHOD]", text, flags=re.IGNORECASE)
    return text


def blinded_events(events: list[dict[str, Any]]) -> str:
    visible = []
    for event in events:
        visible.append({
            "step": event.get("step"),
            "tool_name": scrub(str(event.get("tool_name", ""))),
            "args": scrub(json.dumps(event.get("args", {}), ensure_ascii=True)),
            "clean_observation": scrub(str(event.get("clean_observation", ""))),
            "returned_observation": scrub(str(event.get("returned_observation", ""))),
        })
    return json.dumps(visible, ensure_ascii=True)


def stable_id(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def choose_tasks(core: dict[tuple[str, str, str, str], dict[str, Any]], excluded: set[str], n_each: int) -> list[str]:
    candidates = []
    for suite in TASK_FILES:
        task_ids = sorted({key[3] for key in core if key[0] == suite and key[3] not in excluded})
        complete = [task_id for task_id in task_ids if all((suite, adapter, env, task_id) in core for adapter in ADAPTERS for env in ("clean", "toxic"))]
        if len(complete) < n_each:
            raise ValueError(f"Only {len(complete)} eligible {suite} tasks; need {n_each}")
        candidates.extend(complete[:n_each])
    return candidates


def oracle_fields(task: dict[str, Any]) -> tuple[str, str]:
    oracle = task.get("oracle", {})
    return str(oracle.get("clean_answer", "")), str(oracle.get("poisoned_answer", ""))


def make_case(row: dict[str, Any], task: dict[str, Any], pair_id: str, source_pair_id: str, slot: str, sample_id: str, split: str) -> tuple[dict[str, str], dict[str, str]]:
    clean_answer, poisoned_answer = oracle_fields(task)
    case = {
        "sample_id": sample_id,
        "pair_id": pair_id,
        "run_slot": slot,
        "split": split,
        "family": task.get("family", row.get("family", "")),
        "user_query": scrub(str(task.get("user_query", ""))),
        "clean_oracle": scrub(clean_answer),
        "poisoned_oracle": scrub(poisoned_answer),
        "final_answer": scrub(str(row.get("final_answer", ""))),
        "tool_events_json": blinded_events(row.get("tool_events", [])),
    }
    admin = {
        "sample_id": sample_id,
        "pair_id": pair_id,
        "source_pair_id": source_pair_id,
        "run_slot": slot,
        "split": split,
        "suite": row.get("_suite", ""),
        "task_id": row.get("task_id", ""),
        "adapter": row.get("adapter", ""),
        "model": row.get("model", ""),
        "environment": row.get("environment", ""),
        "poison_probability": row.get("_probability", ""),
        "source": row.get("_source", ""),
    }
    return case, admin


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "toxictool_bench/human_holdout_v1")
    parser.add_argument("--seed", type=int, default=20260915)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    tasks = task_defs()
    excluded = prior_task_ids()

    core_rows = load_manifest_runs(CORE_MANIFEST)
    core = index(core_rows, ("_suite", "adapter", "environment", "task_id"))
    selected_tasks = choose_tasks(core, excluded, 10)

    stress_rows = load_manifest_runs(STRESS_MANIFEST, p1_only=True)
    stress = index(stress_rows, ("_suite", "adapter", "task_id"))
    cross_rows = load_manifest_runs(CROSS_MANIFEST)
    cross = index(cross_rows, ("_suite", "adapter", "environment", "task_id"))

    cases: list[dict[str, str]] = []
    admin: list[dict[str, str]] = []
    used_pairs: set[str] = set()

    def add_pair(pair_id: str, left: dict[str, Any], right: dict[str, Any], split: str) -> None:
        if pair_id in used_pairs:
            raise ValueError(f"duplicate pair {pair_id}")
        used_pairs.add(pair_id)
        public_pair_id = f"PAIR-{len(used_pairs):03d}"
        entries = [("A", left), ("B", right)]
        rng.shuffle(entries)
        for slot, row in entries:
            sample_id = f"HOLD-{len(cases) + 1:03d}"
            case, hidden = make_case(row, tasks[str(row["task_id"])], public_pair_id, pair_id, slot, sample_id, split)
            cases.append(case)
            admin.append(hidden)

    # 160 core cases: 20 tasks x 4 methods x clean/toxic, paired by task/method.
    for task_id in selected_tasks:
        suite = next(s for s in TASK_FILES if (s, ADAPTERS[0], "clean", task_id) in core)
        for adapter in ADAPTERS:
            add_pair(f"CORE-{task_id}-{adapter}", core[(suite, adapter, "clean", task_id)], core[(suite, adapter, "toxic", task_id)], "core")

    # 40 repeated-poison cases on the same 20 tasks, Double-pass vs Guard.
    for task_id in selected_tasks:
        suite = next(s for s in TASK_FILES if (s, "langgraph_react_double_pass", "toxic", task_id) in core)
        add_pair(f"REPEAT-{task_id}", stress[(suite, "langgraph_react_double_pass", task_id)], stress[(suite, "langgraph_react_guarded", task_id)], "repeated_p1")

    # 40 cross-framework/model cases from a separate Claude manifest. Avoid all
    # task IDs already used in the core packet or prior development audit.
    taken_tasks = set(selected_tasks) | excluded
    cross_candidates = []
    for (suite, adapter, environment, task_id), row in cross.items():
        if environment != "clean" or task_id in taken_tasks:
            continue
        if (suite, adapter, "toxic", task_id) in cross:
            cross_candidates.append((suite, adapter, task_id))
    selected_cross = [x for x in sorted(cross_candidates) if x[0] in TASK_FILES][:20]
    if len(selected_cross) < 20:
        raise ValueError(f"Only {len(selected_cross)} eligible cross-model pairs; need 20")
    for suite, adapter, task_id in selected_cross:
        add_pair(f"CROSS-{suite}-{adapter}-{task_id}", cross[(suite, adapter, "clean", task_id)], cross[(suite, adapter, "toxic", task_id)], "cross_model")

    if len(cases) != 240 or len(used_pairs) != 120:
        raise AssertionError((len(cases), len(used_pairs)))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fields = list(cases[0])
    with (args.output_dir / "evidence.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(cases)
    admin_fields = list(admin[0])
    with (args.output_dir / "admin_key.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=admin_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(admin)
    labels = [{"sample_id": c["sample_id"], "pair_id": c["pair_id"], "final_correct": "", "adopted_poisoned": "", "anomaly_detected": "", "substantive_validation": "", "recovered_clean": "", "ambiguous": "", "notes": ""} for c in cases]
    for name in ("annotator_a.csv", "annotator_b.csv"):
        with (args.output_dir / name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(labels[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(labels)
    with (args.output_dir / "adjudication.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(labels[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(labels)
    metadata = {
        "packet": "human_holdout_v1",
        "seed": args.seed,
        "n_trajectories": len(cases),
        "n_pairs": len(used_pairs),
        "composition": {"core": 160, "repeated_p1": 40, "cross_model": 40},
        "excluded_prior_task_ids": len(excluded),
        "independent_holdout": True,
        "scorer_labels_in_evidence": False,
        "method_and_model_labels_in_evidence": False,
        "source_manifests": [str(CORE_MANIFEST.relative_to(ROOT)), str(STRESS_MANIFEST.relative_to(ROOT)), str(CROSS_MANIFEST.relative_to(ROOT))],
    }
    (args.output_dir / "PACKET_METADATA.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(cases)} cases in {len(used_pairs)} paired comparisons to {args.output_dir}")


if __name__ == "__main__":
    main()
