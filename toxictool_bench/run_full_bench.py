from __future__ import annotations

import argparse
import copy
import json
import time
from pathlib import Path
from typing import Any

from evaluator import aggregate, evaluate_run
from full_adapters import DATAFRAME_ROUTER_ALIASES, run_full_adapter
from run_bench import chunk_suffix, load_tasks, select_tasks
from tools import DataToolEnv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ToxicBench with full framework adapters.")
    parser.add_argument("--tasks", type=Path, default=Path("toxictool_bench/tasks/numerical.jsonl"))
    parser.add_argument("--api-file", type=Path, default=Path("api"))
    parser.add_argument("--output-dir", type=Path, default=Path("toxictool_bench/results"))
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument(
        "--adapter",
        required=True,
        choices=[
            "smolagents_toolcalling",
            "langgraph_react_full",
            "langgraph_react_caution",
            "langgraph_react_expectation_only",
            "langgraph_react_verification_only",
            "langgraph_react_guarded",
            "langgraph_react_guarded_light",
            "langgraph_react_abstain",
            "langgraph_react_randomized",
            "langgraph_react_selective",
            "autogen_tool_agent",
            "autogen_verification_only",
            "autogen_guarded",
            *DATAFRAME_ROUTER_ALIASES.keys(),
            "pandasai_dataframe",
            "da_agent_full",
        ],
    )
    parser.add_argument("--env", choices=["clean", "toxic", "both"], default="both")
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--poison-probability",
        type=float,
        default=None,
        help="Override poison probability for eligible tool observations; useful for multi-route stress tests.",
    )
    parser.add_argument(
        "--poison-repeat",
        action="store_true",
        help="Allow every eligible poisoned observation to be corrupted instead of only the first one.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bench_dir = Path(__file__).resolve().parent
    tasks = load_tasks(args.tasks)
    tasks = select_tasks(tasks, start_index=args.start_index, limit=args.limit)
    tasks = apply_poison_overrides(tasks, probability=args.poison_probability, repeat=args.poison_repeat)
    envs = ["clean", "toxic"] if args.env == "both" else [args.env]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    chunk = chunk_suffix(args.start_index, args.limit)
    result_path = args.output_dir / f"{stamp}_{args.adapter}_{args.model}_{args.env}{chunk}.jsonl"
    rows: list[dict[str, Any]] = []
    with result_path.open("w", encoding="utf-8") as f:
        for task in tasks:
            for env_name in envs:
                env = DataToolEnv(task=task, bench_dir=bench_dir, toxic=(env_name == "toxic"))
                run_started = time.perf_counter()
                run = run_full_adapter(
                    adapter=args.adapter,
                    api_file=args.api_file,
                    model=args.model,
                    env=env,
                    task=task,
                    max_steps=args.max_steps,
                    temperature=args.temperature,
                    max_tokens=args.max_tokens,
                )
                elapsed_seconds = time.perf_counter() - run_started
                metrics = evaluate_run(task, run.final_answer, env.events)
                row = {
                    "task_id": task["task_id"],
                    "family": task["family"],
                    "dataset": task["dataset"],
                    "adapter": args.adapter,
                    "model": args.model,
                    "environment": env_name,
                    "poison": task.get("poison", {}),
                    "tool_events": env.events,
                    "final_answer": run.final_answer,
                    "raw_actions": run.raw_actions,
                    "parse_errors": run.parse_errors,
                    "elapsed_seconds": elapsed_seconds,
                    "metrics": metrics,
                }
                rows.append(row)
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                f.flush()
                print(
                    f"{task['task_id']} {env_name}: "
                    f"success={metrics['task_success']} "
                    f"bcr={metrics['blind_compliance']} "
                    f"adr={metrics['anomaly_detection']} "
                    f"vr={metrics['validation']}"
                )

    summary = summarize(rows)
    summary_path = result_path.with_suffix(".summary.json")
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote results: {result_path}")
    print(f"Wrote summary: {summary_path}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_env: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_env.setdefault(row["environment"], []).append(row)
    out = {env: aggregate(env_rows) for env, env_rows in sorted(by_env.items())}
    clean = out.get("clean", {})
    toxic = out.get("toxic", {})
    if clean and toxic:
        out["delta_tsr"] = clean.get("task_success", 0.0) - toxic.get("task_success", 0.0)
    return out


def apply_poison_overrides(
    tasks: list[dict[str, Any]],
    *,
    probability: float | None,
    repeat: bool,
) -> list[dict[str, Any]]:
    if probability is None and not repeat:
        return tasks
    if probability is not None and not (0.0 <= probability <= 1.0):
        raise ValueError("--poison-probability must be between 0 and 1")
    out: list[dict[str, Any]] = []
    for task in tasks:
        patched = copy.deepcopy(task)
        poison = patched.setdefault("poison", {})
        if probability is not None:
            poison["poison_probability"] = probability
        if repeat:
            poison["poison_once"] = False
        out.append(patched)
    return out


if __name__ == "__main__":
    main()
