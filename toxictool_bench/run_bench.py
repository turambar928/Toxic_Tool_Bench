from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from toxictool_bench.agents import AGENT_PROFILES, run_heuristic_agent, run_llm_agent
from toxictool_bench.evaluator import aggregate, evaluate_run
from toxictool_bench.llm_client import ChatClient, load_api_config
from toxictool_bench.tools import DataToolEnv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ToxicBench pilot experiments.")
    parser.add_argument("--tasks", type=Path, default=Path("toxictool_bench/tasks/numerical.jsonl"))
    parser.add_argument("--api-file", type=Path, default=Path("api"))
    parser.add_argument("--output-dir", type=Path, default=Path("toxictool_bench/results"))
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument(
        "--agent-profile",
        default="react",
        choices=sorted(AGENT_PROFILES) + ["heuristic_naive", "heuristic_ibf"],
    )
    parser.add_argument("--env", choices=["clean", "toxic", "both"], default="both")
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--list-models", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.list_models:
        config = load_api_config(args.api_file)
        print("\n".join(config["models"]))
        return

    bench_dir = Path(__file__).resolve().parent
    tasks = load_tasks(args.tasks)
    tasks = select_tasks(tasks, start_index=args.start_index, limit=args.limit)

    envs = ["clean", "toxic"] if args.env == "both" else [args.env]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    chunk = chunk_suffix(args.start_index, args.limit)
    result_path = args.output_dir / f"{stamp}_{args.agent_profile}_{args.model}_{args.env}{chunk}.jsonl"
    summary_path = result_path.with_suffix(".summary.json")

    client = None
    if not args.agent_profile.startswith("heuristic"):
        client = ChatClient(
            api_file=args.api_file,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )

    rows: list[dict[str, Any]] = []
    with result_path.open("w", encoding="utf-8") as f:
        for task in tasks:
            for env_name in envs:
                env = DataToolEnv(task=task, bench_dir=bench_dir, toxic=(env_name == "toxic"))
                if args.agent_profile.startswith("heuristic"):
                    run = run_heuristic_agent(env, task, args.agent_profile)
                else:
                    assert client is not None
                    run = run_llm_agent(
                        client=client,
                        env=env,
                        task=task,
                        profile=args.agent_profile,
                        max_steps=args.max_steps,
                    )
                metrics = evaluate_run(task, run.final_answer, env.events)
                row = {
                    "task_id": task["task_id"],
                    "family": task["family"],
                    "dataset": task["dataset"],
                    "agent_profile": args.agent_profile,
                    "model": args.model,
                    "environment": env_name,
                    "poison": task.get("poison", {}),
                    "tool_events": env.events,
                    "final_answer": run.final_answer,
                    "raw_actions": run.raw_actions,
                    "parse_errors": run.parse_errors,
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
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote results: {result_path}")
    print(f"Wrote summary: {summary_path}")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def load_tasks(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def select_tasks(tasks: list[dict[str, Any]], *, start_index: int = 0, limit: int = 0) -> list[dict[str, Any]]:
    if start_index < 0:
        raise ValueError("--start-index must be non-negative")
    if limit < 0:
        raise ValueError("--limit must be non-negative")
    selected = tasks[start_index:]
    if limit:
        selected = selected[:limit]
    return selected


def chunk_suffix(start_index: int, limit: int) -> str:
    if start_index == 0 and limit == 0:
        return ""
    if limit:
        return f"_start{start_index}_limit{limit}"
    return f"_start{start_index}"


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


if __name__ == "__main__":
    main()
