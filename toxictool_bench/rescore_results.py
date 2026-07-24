from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from evaluator import aggregate, evaluate_run
from run_bench import load_tasks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rescore ToxicBench JSONL result files.")
    parser.add_argument("result_files", nargs="+", type=Path)
    parser.add_argument("--tasks", type=Path, default=Path("toxictool_bench/tasks/numerical.jsonl"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tasks = {task["task_id"]: task for task in load_tasks(args.tasks)}
    for path in args.result_files:
        rows = read_jsonl(path)
        for row in rows:
            task = tasks[row["task_id"]]
            row["metrics"] = evaluate_run(task, row.get("final_answer", ""), row.get("tool_events", []))
        scored_path = path.with_name(path.stem + ".rescored.jsonl")
        with scored_path.open("w", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        summary = summarize(rows)
        summary_path = scored_path.with_suffix(".summary.json")
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{path.name} -> {scored_path.name}")
        print(json.dumps(summary, indent=2, ensure_ascii=False))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


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

