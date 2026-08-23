#!/usr/bin/env python3
"""Rebuild paper-facing ToxicBench summaries from immutable raw trajectories."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from evaluator import aggregate, evaluate_run
from bootstrap_ci import METRICS as BOOTSTRAP_METRICS, bootstrap, summarize as bootstrap_summary
from summarize_results import write_overall, write_poison, write_severity


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "toxictool_bench/results/paper_run_manifest.csv"
RESULTS = ROOT / "toxictool_bench/results"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def rescore(spec: dict[str, str]) -> list[dict[str, Any]]:
    tasks: dict[str, dict[str, Any]] = {}
    for task_name in spec["tasks"].split(";"):
        for task in read_jsonl(ROOT / task_name):
            tasks[task["task_id"]] = task
    source = ROOT / spec["source"]
    rows = read_jsonl(source)
    missing = sorted({row["task_id"] for row in rows} - tasks.keys())
    if missing:
        raise ValueError(f"{source}: task definitions missing for {missing[:5]}")
    for row in rows:
        row["metrics"] = evaluate_run(tasks[row["task_id"]], row.get("final_answer", ""), row.get("tool_events", []))
        row["paper_variant"] = spec["variant"]
    return rows


def write_guard_summary(spec_rows: list[tuple[dict[str, str], list[dict[str, Any]]]], output: Path) -> None:
    fields = [
        "suite", "adapter", "clean_tsr", "poisoned_tsr", "delta_tsr", "bcr", "adr", "vr", "rr",
        "poison_delivery_rate", "n_exposed", "n", "source",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for spec, rows in spec_rows:
            suites = [spec["suite"]] if spec["suite"] != "combined" else ["numerical", "semantic_schema"]
            for suite in suites:
                selected = rows if spec["suite"] != "combined" else [row for row in rows if row.get("family") == suite]
                clean = aggregate([row for row in selected if row.get("environment") == "clean"])
                toxic = aggregate([row for row in selected if row.get("environment") == "toxic"])
                writer.writerow(
                    {
                        "suite": suite,
                        "adapter": spec["variant"],
                        "clean_tsr": clean.get("task_success", 0.0),
                        "poisoned_tsr": toxic.get("task_success", 0.0),
                        "delta_tsr": clean.get("task_success", 0.0) - toxic.get("task_success", 0.0),
                        "bcr": toxic.get("blind_compliance", 0.0),
                        "adr": toxic.get("anomaly_detection", 0.0),
                        "vr": toxic.get("validation", 0.0),
                        "rr": toxic.get("recovery", 0.0),
                        "poison_delivery_rate": toxic.get("poison_delivery_rate", 0.0),
                        "n_exposed": toxic.get("n_exposed", 0),
                        "n": toxic.get("n", 0),
                        "source": spec["source"],
                    }
                )


def write_combined_guard(suite_path: Path, output: Path) -> None:
    with suite_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row["adapter"]].append(row)
    fields = ["adapter", "clean_tsr", "poisoned_tsr", "delta_tsr", "bcr", "adr", "vr", "rr", "poison_delivery_rate", "n_exposed", "n"]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for variant, group in groups.items():
            n = sum(int(row["n"]) for row in group)
            n_exposed = sum(int(row["n_exposed"]) for row in group)
            out: dict[str, Any] = {"adapter": variant, "n": n, "n_exposed": n_exposed}
            for key in ("clean_tsr", "poisoned_tsr", "delta_tsr"):
                out[key] = sum(float(row[key]) * int(row["n"]) for row in group) / n
            for key in ("bcr", "adr", "vr", "rr"):
                out[key] = sum(float(row[key]) * int(row["n_exposed"]) for row in group) / n_exposed if n_exposed else 0.0
            out["poison_delivery_rate"] = n_exposed / n if n else 0.0
            writer.writerow(out)


def write_clean_transition_summary(
    spec_rows: list[tuple[dict[str, str], list[dict[str, Any]]]], output: Path
) -> None:
    """Report task-level clean-result changes between base and full guard."""
    grouped: dict[tuple[str, str], dict[str, bool]] = {}
    for spec, rows in spec_rows:
        if spec["variant"] not in {"Base", "Full guard"}:
            continue
        clean = {
            row["task_id"]: bool(row["metrics"]["task_success"])
            for row in rows
            if row.get("environment") == "clean"
        }
        grouped[(spec["suite"], spec["variant"])] = clean

    fields = [
        "suite", "n_paired", "base_correct", "guard_correct", "stable_correct",
        "false_overrides", "clean_repairs", "false_override_task_ids", "clean_repair_task_ids",
    ]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for suite in sorted({key[0] for key in grouped}):
            base = grouped.get((suite, "Base"))
            guard = grouped.get((suite, "Full guard"))
            if base is None or guard is None:
                continue
            task_ids = sorted(base.keys() & guard.keys())
            false_overrides = [task_id for task_id in task_ids if base[task_id] and not guard[task_id]]
            clean_repairs = [task_id for task_id in task_ids if not base[task_id] and guard[task_id]]
            writer.writerow(
                {
                    "suite": suite,
                    "n_paired": len(task_ids),
                    "base_correct": sum(base[task_id] for task_id in task_ids),
                    "guard_correct": sum(guard[task_id] for task_id in task_ids),
                    "stable_correct": sum(base[task_id] and guard[task_id] for task_id in task_ids),
                    "false_overrides": len(false_overrides),
                    "clean_repairs": len(clean_repairs),
                    "false_override_task_ids": ";".join(false_overrides),
                    "clean_repair_task_ids": ";".join(clean_repairs),
                }
            )


def write_bootstrap_table(
    spec_rows: list[tuple[dict[str, str], list[dict[str, Any]]]],
    output: Path,
    iterations: int,
    seed: int,
) -> None:
    fields = ["experiment", "suite", "variant", "model", "adapter", "n_tasks", "n_exposed"]
    for metric in BOOTSTRAP_METRICS:
        fields.extend([metric, f"{metric}_lo", f"{metric}_hi"])
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for index, (spec, rows) in enumerate(spec_rows):
            point = bootstrap_summary(rows)
            intervals = bootstrap(rows, iterations, random.Random(seed + index))
            sample = rows[0]
            toxic = aggregate([row for row in rows if row.get("environment") == "toxic"])
            out: dict[str, Any] = {
                "experiment": spec["experiment"],
                "suite": spec["suite"],
                "variant": spec["variant"],
                "model": sample.get("model", ""),
                "adapter": sample.get("adapter", ""),
                "n_tasks": len({row.get("task_id") for row in rows}),
                "n_exposed": toxic.get("n_exposed", 0),
            }
            for metric in BOOTSTRAP_METRICS:
                lo, hi = intervals[metric]
                out[metric] = point[metric]
                out[f"{metric}_lo"] = lo
                out[f"{metric}_hi"] = hi
            writer.writerow(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--bootstrap-iterations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()
    specs = load_manifest(args.manifest)
    scored = [(spec, rescore(spec)) for spec in specs]

    cross_num = [row for spec, rows in scored if spec["experiment"] == "cross_model" and spec["suite"] == "numerical" for row in rows]
    cross_sem = [row for spec, rows in scored if spec["experiment"] == "cross_model" and spec["suite"] == "semantic_schema" for row in rows]
    write_overall(cross_num, RESULTS / "cross_model_summary.csv")
    write_poison(cross_num, RESULTS / "poison_type_summary.csv")
    write_severity(cross_num, RESULTS / "cross_model_severity_summary.csv")
    write_overall(cross_sem, RESULTS / "semantic_schema_cross_model_summary.csv")
    write_poison(cross_sem, RESULTS / "semantic_schema_cross_model_poison_summary.csv")
    write_severity(cross_sem, RESULTS / "semantic_schema_cross_model_severity_summary.csv")

    expanded_by_suite: dict[str, list[dict[str, Any]]] = {}
    for suite in ("numerical", "semantic_schema"):
        rows = [row for spec, run_rows in scored if spec["experiment"] == "expanded_gpt" and spec["suite"] == suite for row in run_rows]
        expanded_by_suite[suite] = rows
        prefix = f"iclr2027_gpt_expanded_cross_agent_{suite}"
        write_overall(rows, RESULTS / f"{prefix}_summary.csv")
        write_poison(rows, RESULTS / f"{prefix}_poison_summary.csv")
        write_severity(rows, RESULTS / f"{prefix}_severity_summary.csv")
    combined = expanded_by_suite["numerical"] + expanded_by_suite["semantic_schema"]
    write_overall(combined, RESULTS / "iclr2027_gpt_expanded_cross_agent_combined_summary.csv")
    write_poison(combined, RESULTS / "iclr2027_gpt_expanded_cross_agent_combined_poison_summary.csv")
    write_severity(combined, RESULTS / "iclr2027_gpt_expanded_cross_agent_combined_severity_summary.csv")

    langgraph = [(spec, rows) for spec, rows in scored if spec["experiment"] == "langgraph_guard"]
    langgraph_suite = RESULTS / "langgraph_guarded_ablation_suite_summary.csv"
    write_guard_summary(langgraph, langgraph_suite)
    write_combined_guard(langgraph_suite, RESULTS / "langgraph_guarded_ablation_summary.csv")
    autogen = [(spec, rows) for spec, rows in scored if spec["experiment"] == "autogen_guard"]
    autogen_suite = RESULTS / "autogen_guarded_replication_suite_summary.csv"
    write_guard_summary(autogen, autogen_suite)
    write_combined_guard(autogen_suite, RESULTS / "autogen_guarded_replication_summary.csv")
    multitable = [(spec, rows) for spec, rows in scored if spec["experiment"] == "multitable"]
    write_guard_summary(multitable, RESULTS / "langgraph_multitable_extension_summary.csv")
    write_clean_transition_summary(
        langgraph + multitable,
        RESULTS / "langgraph_guard_clean_transition_summary.csv",
    )
    alternatives = [(spec, rows) for spec, rows in scored if spec["experiment"] == "alternative_baseline"]
    write_guard_summary(alternatives, RESULTS / "iclr2027_stronger_baselines_strict_summary.csv")
    stress = [(spec, rows) for spec, rows in scored if spec["experiment"] == "multiroute_stress"]
    write_guard_summary(stress, RESULTS / "iclr2027_semantic_guard_multiroute_stress_strict_summary.csv")
    write_bootstrap_table(
        [(spec, rows) for spec, rows in scored if spec["experiment"] == "cross_model" and spec["suite"] == "numerical"],
        RESULTS / "numerical_cross_model_bootstrap_ci.csv",
        args.bootstrap_iterations,
        args.seed,
    )
    write_bootstrap_table(
        [(spec, rows) for spec, rows in scored if spec["experiment"] == "cross_model" and spec["suite"] == "semantic_schema"],
        RESULTS / "semantic_schema_cross_model_bootstrap_ci.csv",
        args.bootstrap_iterations,
        args.seed + 100,
    )
    write_bootstrap_table(langgraph, RESULTS / "langgraph_guarded_bootstrap_ci.csv", args.bootstrap_iterations, args.seed + 200)
    write_bootstrap_table(autogen, RESULTS / "autogen_guarded_replication_bootstrap_ci.csv", args.bootstrap_iterations, args.seed + 300)
    print(f"Rebuilt paper summaries from {len(specs)} immutable raw runs.")


if __name__ == "__main__":
    main()
