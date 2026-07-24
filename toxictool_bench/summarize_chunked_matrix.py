from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from run_bench import load_tasks, select_tasks
from summarize_results import read_jsonl, write_overall, write_poison, write_severity


@dataclass(frozen=True)
class ChunkSelection:
    suite: str
    adapter: str
    start_index: int
    limit: int
    path: Path
    rows: int
    tasks: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize chunked ToxicBench matrix runs.")
    parser.add_argument("--tasks", nargs="+", type=Path, required=True)
    parser.add_argument("--adapters", nargs="+", required=True)
    parser.add_argument("--starts", nargs="+", type=int, required=True)
    parser.add_argument("--limit", type=int, required=True)
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--env", default="both")
    parser.add_argument("--results-dir", type=Path, default=Path("toxictool_bench/results"))
    parser.add_argument("--output-prefix", type=Path, required=True)
    parser.add_argument("--allow-missing", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selections: list[ChunkSelection] = []
    all_rows: list[dict[str, Any]] = []
    missing: list[str] = []

    for task_path in args.tasks:
        suite = task_path.stem
        suite_rows: list[dict[str, Any]] = []
        for adapter in args.adapters:
            for start in args.starts:
                expected_ids = expected_task_ids(task_path, start_index=start, limit=args.limit)
                selection = select_latest_complete_chunk(
                    results_dir=args.results_dir,
                    adapter=adapter,
                    model=args.model,
                    env=args.env,
                    start_index=start,
                    limit=args.limit,
                    expected_task_ids=expected_ids,
                    suite=suite,
                )
                if selection is None:
                    missing.append(f"{suite}:{adapter}:start{start}:limit{args.limit}")
                    continue
                rows = read_jsonl(selection.path)
                selections.append(selection)
                suite_rows.extend(rows)
                all_rows.extend(rows)
        if suite_rows:
            write_outputs(suite_rows, args.output_prefix, suite)

    if all_rows:
        write_outputs(all_rows, args.output_prefix, "combined")
    write_manifest(selections, args.output_prefix.with_name(args.output_prefix.name + "_manifest.csv"))

    if missing and not args.allow_missing:
        raise SystemExit("Missing complete chunks:\n" + "\n".join(missing))
    if missing:
        print("Missing complete chunks:")
        for item in missing:
            print(item)


def expected_task_ids(task_path: Path, *, start_index: int, limit: int) -> set[str]:
    tasks = select_tasks(load_tasks(task_path), start_index=start_index, limit=limit)
    return {str(task["task_id"]) for task in tasks}


def select_latest_complete_chunk(
    *,
    results_dir: Path,
    adapter: str,
    model: str,
    env: str,
    start_index: int,
    limit: int,
    expected_task_ids: set[str],
    suite: str,
) -> ChunkSelection | None:
    patterns = [f"*_{adapter}_{model}_{env}_start{start_index}_limit{limit}.jsonl"]
    if start_index == 0:
        patterns.append(f"*_{adapter}_{model}_{env}.jsonl")
    candidates = sorted(
        {path for pattern in patterns for path in results_dir.glob(pattern)},
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        rows = safe_read_jsonl(path)
        if not rows:
            continue
        row_task_ids = {str(row.get("task_id")) for row in rows}
        row_envs = {str(row.get("environment")) for row in rows}
        if row_task_ids != expected_task_ids:
            continue
        if env == "both" and row_envs != {"clean", "toxic"}:
            continue
        if env != "both" and row_envs != {env}:
            continue
        expected_rows = len(expected_task_ids) * (2 if env == "both" else 1)
        if len(rows) != expected_rows:
            continue
        return ChunkSelection(
            suite=suite,
            adapter=adapter,
            start_index=start_index,
            limit=limit,
            path=path,
            rows=len(rows),
            tasks=len(expected_task_ids),
        )
    return None


def safe_read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        return read_jsonl(path)
    except Exception:
        return []


def write_outputs(rows: list[dict[str, Any]], output_prefix: Path, suite: str) -> None:
    base = output_prefix.with_name(f"{output_prefix.name}_{suite}")
    write_overall(rows, base.with_name(base.name + "_summary.csv"))
    write_poison(rows, base.with_name(base.name + "_poison_summary.csv"))
    write_severity(rows, base.with_name(base.name + "_severity_summary.csv"))


def write_manifest(selections: list[ChunkSelection], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["suite", "adapter", "start_index", "limit", "tasks", "rows", "path"],
        )
        writer.writeheader()
        for selection in selections:
            writer.writerow(
                {
                    "suite": selection.suite,
                    "adapter": selection.adapter,
                    "start_index": selection.start_index,
                    "limit": selection.limit,
                    "tasks": selection.tasks,
                    "rows": selection.rows,
                    "path": selection.path,
                }
            )


if __name__ == "__main__":
    main()
