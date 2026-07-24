from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize latency and tool-event overhead coverage.")
    parser.add_argument("--manifest", action="append", type=Path, default=[], help="CSV manifest with a path column.")
    parser.add_argument("--result-file", action="append", type=Path, default=[], help="Additional JSONL result file.")
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = collect_paths(args.manifest, args.result_file)
    rows: list[dict[str, Any]] = []
    for path in paths:
        if path.exists():
            rows.extend(read_jsonl(path))
    write_summary(rows, args.output)
    print(f"wrote {args.output} from {len(paths)} files and {len(rows)} rows")


def collect_paths(manifests: list[Path], explicit: list[Path]) -> list[Path]:
    out: list[Path] = []
    seen: set[Path] = set()
    for manifest in manifests:
        with manifest.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                raw = row.get("path")
                if not raw:
                    continue
                path = Path(raw)
                if path not in seen:
                    seen.add(path)
                    out.append(path)
    for path in explicit:
        if path not in seen:
            seen.add(path)
            out.append(path)
    return out


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_summary(rows: list[dict[str, Any]], path: Path) -> None:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (
            str(row.get("family", "unknown")),
            str(row.get("model", "unknown")),
            str(row.get("adapter") or row.get("agent_profile") or "unknown"),
            str(row.get("environment", "unknown")),
        )
        groups.setdefault(key, []).append(row)

    fieldnames = [
        "suite",
        "model",
        "adapter",
        "environment",
        "n",
        "elapsed_n",
        "elapsed_coverage",
        "mean_elapsed_seconds",
        "p50_elapsed_seconds",
        "p90_elapsed_seconds",
        "avg_tool_events",
        "avg_raw_actions",
        "avg_final_chars",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for key, group in sorted(groups.items()):
            suite, model, adapter, environment = key
            elapsed = [float(row["elapsed_seconds"]) for row in group if row.get("elapsed_seconds") not in (None, "")]
            writer.writerow(
                {
                    "suite": suite,
                    "model": model,
                    "adapter": adapter,
                    "environment": environment,
                    "n": len(group),
                    "elapsed_n": len(elapsed),
                    "elapsed_coverage": fmt(len(elapsed) / len(group) if group else 0.0),
                    "mean_elapsed_seconds": fmt(mean(elapsed)),
                    "p50_elapsed_seconds": fmt(percentile(elapsed, 50)),
                    "p90_elapsed_seconds": fmt(percentile(elapsed, 90)),
                    "avg_tool_events": fmt(mean([len(row.get("tool_events", [])) for row in group])),
                    "avg_raw_actions": fmt(mean([len(row.get("raw_actions", [])) for row in group])),
                    "avg_final_chars": fmt(mean([len(str(row.get("final_answer", ""))) for row in group])),
                }
            )


def mean(values: list[float] | list[int]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * (pct / 100.0)
    lower = int(rank)
    upper = min(lower + 1, len(ordered) - 1)
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def fmt(value: float) -> str:
    return f"{value:.2f}"


if __name__ == "__main__":
    main()
