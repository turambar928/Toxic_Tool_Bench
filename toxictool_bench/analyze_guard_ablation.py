#!/usr/bin/env python3
"""Summarize data2mcp guard ablations and extract representative cases."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def one_line(value: Any, limit: int = 700) -> str:
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def metric_rate(rows: list[dict[str, Any]], key: str) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if row.get("metrics", {}).get(key)) / len(rows)


def avg(rows: list[dict[str, Any]], fn) -> float:
    if not rows:
        return 0.0
    return mean(fn(row) for row in rows)


def summarize_file(suite: str, path: Path) -> dict[str, Any]:
    rows = load_jsonl(path)
    clean = [row for row in rows if row.get("environment") == "clean"]
    toxic = [row for row in rows if row.get("environment") == "toxic"]
    sample = rows[0] if rows else {}
    return {
        "suite": suite,
        "model": sample.get("model", ""),
        "adapter": sample.get("adapter", ""),
        "n_clean": len(clean),
        "n_toxic": len(toxic),
        "clean_tsr": metric_rate(clean, "task_success"),
        "toxic_tsr": metric_rate(toxic, "task_success"),
        "delta_tsr": metric_rate(clean, "task_success") - metric_rate(toxic, "task_success"),
        "toxic_bcr": metric_rate(toxic, "blind_compliance"),
        "toxic_adr": metric_rate(toxic, "anomaly_detection"),
        "toxic_vr": metric_rate(toxic, "validation"),
        "toxic_rr": metric_rate(toxic, "recovery"),
        "avg_tool_events_clean": avg(clean, lambda row: len(row.get("tool_events", []))),
        "avg_tool_events_toxic": avg(toxic, lambda row: len(row.get("tool_events", []))),
        "avg_messages_clean": avg(clean, lambda row: len(row.get("messages", []))),
        "avg_messages_toxic": avg(toxic, lambda row: len(row.get("messages", []))),
        "avg_final_chars_clean": avg(clean, lambda row: len(str(row.get("final_answer", "")))),
        "avg_final_chars_toxic": avg(toxic, lambda row: len(str(row.get("final_answer", "")))),
    }


def by_task(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row.get("task_id", ""): row for row in rows if row.get("environment") == "toxic"}


def first_poisoned(row: dict[str, Any]) -> dict[str, Any]:
    for event in row.get("tool_events", []):
        if event.get("was_poisoned"):
            return event
    return {}


def render_case(title: str, base: dict[str, Any], guarded: dict[str, Any], light: dict[str, Any] | None = None) -> str:
    event = first_poisoned(base) or first_poisoned(guarded)
    lines = [
        f"## {title}",
        "",
        f"- Task: `{base.get('task_id')}`",
        f"- Dataset: `{base.get('dataset')}`",
        f"- Poison type: `{event.get('poison_type') or base.get('poison', {}).get('type', '')}`",
        f"- Base metrics: {base.get('metrics', {})}",
        f"- Full guard metrics: {guarded.get('metrics', {})}",
    ]
    if light is not None:
        lines.append(f"- Light guard metrics: {light.get('metrics', {})}")
    lines.extend(
        [
            "",
            "**Poisoned observation seen by base**",
            "",
            "```text",
            one_line(event.get("returned_observation", "")),
            "```",
            "",
            "**Base final answer**",
            "",
            "```text",
            one_line(base.get("final_answer", "")),
            "```",
            "",
            "**Full guarded final answer**",
            "",
            "```text",
            one_line(guarded.get("final_answer", "")),
            "```",
            "",
        ]
    )
    if light is not None:
        lines.extend(
            [
                "**Light guarded final answer**",
                "",
                "```text",
                one_line(light.get("final_answer", "")),
                "```",
                "",
            ]
        )
    return "\n".join(lines)


def select_cases(suite: str, base_path: Path, full_path: Path, light_path: Path) -> list[str]:
    base = by_task(load_jsonl(base_path))
    full = by_task(load_jsonl(full_path))
    light = by_task(load_jsonl(light_path))
    sections: list[str] = []

    for task_id, base_row in base.items():
        full_row = full.get(task_id)
        if not full_row:
            continue
        if base_row.get("metrics", {}).get("blind_compliance") and full_row.get("metrics", {}).get("recovery"):
            sections.append(render_case(f"{suite}: base blind compliance, full guard recovery", base_row, full_row, light.get(task_id)))
            break

    for task_id, full_row in full.items():
        light_row = light.get(task_id)
        base_row = base.get(task_id)
        if not light_row or not base_row:
            continue
        if full_row.get("metrics", {}).get("task_success") and not light_row.get("metrics", {}).get("task_success"):
            sections.append(render_case(f"{suite}: light guard failure under tight budget", base_row, full_row, light_row))
            break

    return sections


def write_csv(rows: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) if rows else []
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--semantic-base", type=Path, required=True)
    parser.add_argument("--semantic-full", type=Path, required=True)
    parser.add_argument("--semantic-light", type=Path, required=True)
    parser.add_argument("--numerical-base", type=Path, required=True)
    parser.add_argument("--numerical-full", type=Path, required=True)
    parser.add_argument("--numerical-light", type=Path, required=True)
    args = parser.parse_args()

    specs = [
        ("semantic_schema", args.semantic_base),
        ("semantic_schema", args.semantic_full),
        ("semantic_schema", args.semantic_light),
        ("numerical", args.numerical_base),
        ("numerical", args.numerical_full),
        ("numerical", args.numerical_light),
    ]
    summary = [summarize_file(suite, path) for suite, path in specs]
    write_csv(summary, args.output_csv)

    cases = [
        "# Guarded data2mcp Case Studies",
        "",
        "Generated from rescored base/full/light ablation files. Cases are selected mechanically: base blind-compliance cases that full guard recovers, and full-guard successes that light guard loses under the tighter budget.",
        "",
    ]
    cases.extend(select_cases("Semantic/schema", args.semantic_base, args.semantic_full, args.semantic_light))
    cases.extend(select_cases("Numerical", args.numerical_base, args.numerical_full, args.numerical_light))
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text("\n".join(cases), encoding="utf-8")
    print(args.output_csv)
    print(args.output_md)


if __name__ == "__main__":
    main()
