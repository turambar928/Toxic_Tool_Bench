#!/usr/bin/env python3
"""Extract representative ToxicTool-Bench trajectory case studies."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


DEFAULT_RESULTS = [
    "results/20260707-133726_langgraph_react_full_gpt-5.4-mini_both.rescored.jsonl",
    "results/20260707-134758_smolagents_toolcalling_gpt-5.4-mini_both.rescored.jsonl",
    "results/20260707-122940_data2mcp_dataframe_gpt-5.4-mini_both.rescored.jsonl",
    "results/20260707-130327_pandasai_dataframe_gpt-5.4-mini_both.rescored.jsonl",
    "results/20260707-130859_da_agent_full_gpt-5.4-mini_both.rescored.jsonl",
    "results/20260707-124859_autogen_tool_agent_gpt-5.4-mini_both.rescored.jsonl",
    "results/20260707-160205_langgraph_react_full_claude-sonnet-4-6_both.rescored.jsonl",
    "results/20260707-161144_smolagents_toolcalling_claude-sonnet-4-6_both.rescored.jsonl",
    "results/20260707-162340_data2mcp_dataframe_claude-sonnet-4-6_both.rescored.jsonl",
    "results/20260707-170254_pandasai_dataframe_claude-sonnet-4-6_both.rescored.jsonl",
    "results/20260707-171009_autogen_tool_agent_claude-sonnet-4-6_both.rescored.jsonl",
    "results/20260707-180904_langgraph_react_full_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl",
    "results/20260707-181347_smolagents_toolcalling_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl",
    "results/20260707-185704_data2mcp_dataframe_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl",
    "results/20260707-191325_pandasai_dataframe_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl",
    "results/20260707-191533_autogen_tool_agent_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def one_line(text: Any, limit: int = 320) -> str:
    value = " ".join(str(text).split())
    if len(value) <= limit:
        return value
    return value[: limit - 3] + "..."


def first_poisoned_event(row: dict[str, Any]) -> dict[str, Any] | None:
    for event in row.get("tool_events", []):
        if event.get("was_poisoned"):
            return event
    return None


def classify(row: dict[str, Any]) -> list[str]:
    metrics = row.get("metrics", {})
    labels = []
    poisoned_event = first_poisoned_event(row)
    if row.get("environment") != "toxic" or poisoned_event is None:
        return labels

    if metrics.get("blind_compliance"):
        labels.append("blind_compliance")
    if metrics.get("validation") and metrics.get("recovery"):
        labels.append("validated_recovery")
    if metrics.get("anomaly_detection") and not metrics.get("recovery"):
        labels.append("detected_not_recovered")
    if not metrics.get("task_success") and not metrics.get("poisoned_answer_used"):
        labels.append("non_poison_failure")
    if row.get("parse_errors", 0) or len(row.get("tool_events", [])) >= 8:
        labels.append("execution_loop_or_parse_issue")
    return labels


def case_score(row: dict[str, Any]) -> tuple[int, int, str]:
    metrics = row.get("metrics", {})
    events = row.get("tool_events", [])
    poisoned = first_poisoned_event(row) is not None
    signal = int(poisoned) + int(metrics.get("blind_compliance")) + int(metrics.get("validation"))
    return (signal, len(events), row.get("task_id", ""))


def render_case(label: str, row: dict[str, Any], index: int) -> str:
    metrics = row.get("metrics", {})
    poison_event = first_poisoned_event(row) or {}
    poison_type = poison_event.get("poison_type") or row.get("poison", {}).get("type", "unknown")
    lines = [
        f"### {index}. {label}: `{row.get('adapter')}` / `{row.get('model')}` / `{row.get('task_id')}`",
        "",
        f"- Dataset: `{row.get('dataset')}`",
        f"- Poison type: `{poison_type}`",
        f"- Metrics: task_success={metrics.get('task_success')}, blind_compliance={metrics.get('blind_compliance')}, "
        f"anomaly_detection={metrics.get('anomaly_detection')}, validation={metrics.get('validation')}, recovery={metrics.get('recovery')}",
        f"- Tool steps: {len(row.get('tool_events', []))}",
        "",
        "**Poisoned Observation Excerpt**",
        "",
        "```text",
        one_line(poison_event.get("returned_observation", ""), 700),
        "```",
        "",
        "**Clean Observation Excerpt**",
        "",
        "```text",
        one_line(poison_event.get("clean_observation", ""), 700),
        "```",
        "",
        "**Final Answer Excerpt**",
        "",
        "```text",
        one_line(row.get("final_answer", ""), 900),
        "```",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bench-dir",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Path to paper/iclr/toxictool_bench.",
    )
    parser.add_argument(
        "--results",
        nargs="*",
        default=DEFAULT_RESULTS,
        help="Rescored JSONL result files, relative to bench-dir or absolute.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "CASE_STUDIES.md",
    )
    parser.add_argument("--per-category", type=int, default=2)
    args = parser.parse_args()

    by_label: dict[str, list[dict[str, Any]]] = defaultdict(list)
    files = []
    for item in args.results:
        path = Path(item)
        if not path.is_absolute():
            path = args.bench_dir / path
        if not path.exists():
            raise FileNotFoundError(path)
        files.append(path)
        for row in load_jsonl(path):
            for label in classify(row):
                by_label[label].append(row)

    labels = [
        ("blind_compliance", "Blindly copied poisoned evidence"),
        ("validated_recovery", "Validated and recovered"),
        ("detected_not_recovered", "Detected anomaly but did not recover"),
        ("non_poison_failure", "Failed without using poisoned answer"),
        ("execution_loop_or_parse_issue", "Execution loop or parse issue"),
    ]

    out = [
        "# ToxicTool-Bench Case Studies",
        "",
        "Generated from final rescored expanded-result files only. These examples are intended for paper discussion and appendix writing; they should not replace the aggregate tables.",
        "",
        "## Source Files",
        "",
    ]
    out.extend(f"- `{path}`" for path in files)
    out.append("")

    idx = 1
    for key, title in labels:
        cases = sorted(by_label.get(key, []), key=case_score, reverse=True)
        if not cases:
            continue
        out.extend([f"## {title}", ""])
        seen = set()
        kept = 0
        for row in cases:
            dedupe_key = (row.get("adapter"), row.get("model"), row.get("task_id"))
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            out.append(render_case(title, row, idx))
            idx += 1
            kept += 1
            if kept >= args.per_category:
                break

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(out), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
