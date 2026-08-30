from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from bootstrap_ci import METRICS as BOOTSTRAP_METRICS, bootstrap, summarize as bootstrap_summary, was_exposed
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
    parser.add_argument("--starts", nargs="+", type=int)
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--chunks",
        nargs="+",
        metavar="START:LIMIT",
        help="Explicit mixed-size chunks, for example: --chunks 0:5 5:5 20:20.",
    )
    parser.add_argument(
        "--suite-chunks",
        action="append",
        metavar="SUITE=START:LIMIT,...",
        help="Suite-specific chunks; may be repeated for task suites with different chunking.",
    )
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--env", default="both")
    parser.add_argument("--results-dir", type=Path, default=Path("toxictool_bench/results"))
    parser.add_argument("--output-prefix", type=Path, required=True)
    parser.add_argument("--allow-missing", action="store_true")
    parser.add_argument("--bootstrap-iterations", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=13)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selections: list[ChunkSelection] = []
    all_rows: list[dict[str, Any]] = []
    missing: list[str] = []
    suite_chunks = parse_suite_chunks(args.suite_chunks)
    has_default_chunks = bool(args.chunks or args.starts or args.limit is not None)
    default_chunks = normalize_chunks(args.starts, args.limit, args.chunks) if has_default_chunks else None

    for suite_index, task_path in enumerate(args.tasks):
        suite = task_path.stem
        chunks = suite_chunks.get(suite, default_chunks)
        if chunks is None:
            raise SystemExit(f"No chunks specified for suite {suite!r}.")
        suite_rows: list[dict[str, Any]] = []
        for adapter in args.adapters:
            for start, limit in chunks:
                expected_ids = expected_task_ids(task_path, start_index=start, limit=limit)
                selection = select_latest_complete_chunk(
                    results_dir=args.results_dir,
                    adapter=adapter,
                    model=args.model,
                    env=args.env,
                    start_index=start,
                    limit=limit,
                    expected_task_ids=expected_ids,
                    suite=suite,
                )
                if selection is None:
                    missing.append(f"{suite}:{adapter}:start{start}:limit{limit}")
                    continue
                rows = read_jsonl(selection.path)
                selections.append(selection)
                suite_rows.extend(rows)
                all_rows.extend(rows)
        if suite_rows:
            write_outputs(
                suite_rows,
                args.output_prefix,
                suite,
                bootstrap_iterations=args.bootstrap_iterations,
                seed=args.seed + suite_index * 1000,
            )

    if all_rows:
        write_outputs(
            all_rows,
            args.output_prefix,
            "combined",
            bootstrap_iterations=args.bootstrap_iterations,
            seed=args.seed + 10_000,
        )
    write_manifest(selections, args.output_prefix.with_name(args.output_prefix.name + "_manifest.csv"))

    if missing and not args.allow_missing:
        raise SystemExit("Missing complete chunks:\n" + "\n".join(missing))
    if missing:
        print("Missing complete chunks:")
        for item in missing:
            print(item)


def normalize_chunks(
    starts: list[int] | None,
    limit: int | None,
    chunks: list[str] | None,
) -> list[tuple[int, int]]:
    if chunks and (starts or limit is not None):
        raise SystemExit("Use either --chunks or --starts with --limit, not both.")
    if chunks:
        parsed: list[tuple[int, int]] = []
        for spec in chunks:
            try:
                start_text, limit_text = spec.split(":", 1)
                start, chunk_limit = int(start_text), int(limit_text)
            except ValueError as exc:
                raise SystemExit(f"Invalid chunk {spec!r}; expected START:LIMIT.") from exc
            if start < 0 or chunk_limit <= 0:
                raise SystemExit(f"Invalid chunk {spec!r}; START >= 0 and LIMIT > 0 are required.")
            parsed.append((start, chunk_limit))
        if len(set(parsed)) != len(parsed):
            raise SystemExit("Duplicate --chunks entries are not allowed.")
        return parsed
    if not starts or limit is None:
        raise SystemExit("Provide --chunks or both --starts and --limit.")
    if limit <= 0:
        raise SystemExit("--limit must be greater than zero.")
    return [(start, limit) for start in starts]


def parse_suite_chunks(specs: list[str] | None) -> dict[str, list[tuple[int, int]]]:
    parsed: dict[str, list[tuple[int, int]]] = {}
    for spec in specs or []:
        try:
            suite, raw_chunks = spec.split("=", 1)
        except ValueError as exc:
            raise SystemExit(f"Invalid suite chunk spec {spec!r}; expected SUITE=START:LIMIT,...") from exc
        suite = suite.strip()
        if not suite or suite in parsed:
            raise SystemExit(f"Suite names must be non-empty and unique in --suite-chunks: {suite!r}")
        chunk_specs = [chunk.strip() for chunk in raw_chunks.split(",") if chunk.strip()]
        parsed[suite] = normalize_chunks(None, None, chunk_specs)
    return parsed


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


def write_outputs(
    rows: list[dict[str, Any]],
    output_prefix: Path,
    suite: str,
    *,
    bootstrap_iterations: int,
    seed: int,
) -> None:
    base = output_prefix.with_name(f"{output_prefix.name}_{suite}")
    write_overall(rows, base.with_name(base.name + "_summary.csv"))
    write_poison(rows, base.with_name(base.name + "_poison_summary.csv"))
    write_severity(rows, base.with_name(base.name + "_severity_summary.csv"))
    write_bootstrap_ci(
        rows,
        base.with_name(base.name + "_bootstrap_ci.csv"),
        iterations=bootstrap_iterations,
        seed=seed,
    )


def write_bootstrap_ci(rows: list[dict[str, Any]], path: Path, *, iterations: int, seed: int) -> None:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (str(row.get("model", "")), str(row.get("adapter", "")))
        groups.setdefault(key, []).append(row)

    fields = ["model", "adapter", "n_tasks", "n_exposed"]
    for metric in BOOTSTRAP_METRICS:
        fields.extend([metric, f"{metric}_lo", f"{metric}_hi"])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for index, ((model, adapter), group_rows) in enumerate(sorted(groups.items())):
            point = bootstrap_summary(group_rows)
            intervals = bootstrap(group_rows, iterations, random.Random(seed + index))
            toxic = [row for row in group_rows if row.get("environment") == "toxic"]
            out: dict[str, Any] = {
                "model": model,
                "adapter": adapter,
                "n_tasks": len({str(row.get("task_id", "")) for row in group_rows}),
                "n_exposed": sum(was_exposed(row) for row in toxic),
            }
            for metric in BOOTSTRAP_METRICS:
                lo, hi = intervals[metric]
                out[metric] = f"{point[metric]:.4f}"
                out[f"{metric}_lo"] = f"{lo:.4f}"
                out[f"{metric}_hi"] = f"{hi:.4f}"
            writer.writerow(out)


def write_manifest(selections: list[ChunkSelection], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["suite", "adapter", "start_index", "limit", "tasks", "rows", "path"],
            lineterminator="\n",
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
