from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from evaluator import aggregate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize ToxicBench result JSONL files.")
    parser.add_argument("result_files", nargs="+", type=Path)
    parser.add_argument("--overall-output", type=Path, required=True)
    parser.add_argument("--poison-output", type=Path, required=True)
    parser.add_argument("--severity-output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = []
    for path in args.result_files:
        rows.extend(read_jsonl(path))
    write_overall(rows, args.overall_output)
    write_poison(rows, args.poison_output)
    if args.severity_output:
        write_severity(rows, args.severity_output)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_overall(rows: list[dict[str, Any]], path: Path) -> None:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault((row["model"], adapter_name(row)), []).append(row)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "model",
                "adapter",
                "clean_tsr",
                "poisoned_tsr",
                "delta_tsr",
                "toxic_bcr",
                "toxic_par",
                "toxic_vpa",
                "toxic_adr",
                "toxic_vr",
                "toxic_rr",
                "poison_delivery_rate",
                "n_exposed",
                "avg_elapsed_clean",
                "avg_elapsed_toxic",
                "n",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for (model, adapter), group_rows in sorted(groups.items()):
            by_env = split_by_env(group_rows)
            clean = aggregate(by_env.get("clean", []))
            toxic = aggregate(by_env.get("toxic", []))
            writer.writerow(
                {
                    "model": model,
                    "adapter": adapter,
                    "clean_tsr": fmt(clean.get("task_success", 0.0)),
                    "poisoned_tsr": fmt(toxic.get("task_success", 0.0)),
                    "delta_tsr": fmt(clean.get("task_success", 0.0) - toxic.get("task_success", 0.0)),
                    "toxic_bcr": fmt(toxic.get("blind_compliance", 0.0)),
                    "toxic_par": fmt(toxic.get("poison_adoption", 0.0)),
                    "toxic_vpa": fmt(toxic.get("validated_poison_adoption", 0.0)),
                    "toxic_adr": fmt(toxic.get("anomaly_detection", 0.0)),
                    "toxic_vr": fmt(toxic.get("validation", 0.0)),
                    "toxic_rr": fmt(toxic.get("recovery", 0.0)),
                    "poison_delivery_rate": fmt(toxic.get("poison_delivery_rate", 0.0)),
                    "n_exposed": toxic.get("n_exposed", 0),
                    "avg_elapsed_clean": fmt(avg_elapsed(by_env.get("clean", []))),
                    "avg_elapsed_toxic": fmt(avg_elapsed(by_env.get("toxic", []))),
                    "n": toxic.get("n", 0),
                }
            )


def write_poison(rows: list[dict[str, Any]], path: Path) -> None:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        if row.get("environment") != "toxic":
            continue
        poison_type = row.get("poison", {}).get("type", "unknown")
        groups.setdefault((row["model"], adapter_name(row), poison_type), []).append(row)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "model", "adapter", "poison_type", "toxic_tsr", "bcr", "par", "vpa", "adr", "vr", "rr",
                "poison_delivery_rate", "n_exposed", "n",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for (model, adapter, poison_type), group_rows in sorted(groups.items()):
            metrics = aggregate(group_rows)
            writer.writerow(
                {
                    "model": model,
                    "adapter": adapter,
                    "poison_type": poison_type,
                    "toxic_tsr": fmt(metrics.get("task_success", 0.0)),
                    "bcr": fmt(metrics.get("blind_compliance", 0.0)),
                    "par": fmt(metrics.get("poison_adoption", 0.0)),
                    "vpa": fmt(metrics.get("validated_poison_adoption", 0.0)),
                    "adr": fmt(metrics.get("anomaly_detection", 0.0)),
                    "vr": fmt(metrics.get("validation", 0.0)),
                    "rr": fmt(metrics.get("recovery", 0.0)),
                    "poison_delivery_rate": fmt(metrics.get("poison_delivery_rate", 0.0)),
                    "n_exposed": metrics.get("n_exposed", 0),
                    "n": metrics.get("n", 0),
                }
            )


def write_severity(rows: list[dict[str, Any]], path: Path) -> None:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        if row.get("environment") != "toxic":
            continue
        poison = row.get("poison", {})
        poison_type = poison.get("type", "unknown")
        severity = poison.get("severity", "unspecified")
        groups.setdefault((row["model"], adapter_name(row), poison_type, severity), []).append(row)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "model", "adapter", "poison_type", "severity", "toxic_tsr", "bcr", "par", "vpa", "adr", "vr", "rr",
                "poison_delivery_rate", "n_exposed", "n",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for (model, adapter, poison_type, severity), group_rows in sorted(groups.items()):
            metrics = aggregate(group_rows)
            writer.writerow(
                {
                    "model": model,
                    "adapter": adapter,
                    "poison_type": poison_type,
                    "severity": severity,
                    "toxic_tsr": fmt(metrics.get("task_success", 0.0)),
                    "bcr": fmt(metrics.get("blind_compliance", 0.0)),
                    "par": fmt(metrics.get("poison_adoption", 0.0)),
                    "vpa": fmt(metrics.get("validated_poison_adoption", 0.0)),
                    "adr": fmt(metrics.get("anomaly_detection", 0.0)),
                    "vr": fmt(metrics.get("validation", 0.0)),
                    "rr": fmt(metrics.get("recovery", 0.0)),
                    "poison_delivery_rate": fmt(metrics.get("poison_delivery_rate", 0.0)),
                    "n_exposed": metrics.get("n_exposed", 0),
                    "n": metrics.get("n", 0),
                }
            )


def split_by_env(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_env: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_env.setdefault(row["environment"], []).append(row)
    return by_env


def adapter_name(row: dict[str, Any]) -> str:
    return str(row.get("adapter") or row.get("agent_profile") or "unknown")


def avg_elapsed(rows: list[dict[str, Any]]) -> float:
    values = [float(row.get("elapsed_seconds", 0.0) or 0.0) for row in rows]
    return sum(values) / len(values) if values else 0.0


def fmt(value: float) -> str:
    return f"{value:.2f}"


if __name__ == "__main__":
    main()
