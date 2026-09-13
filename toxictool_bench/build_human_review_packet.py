#!/usr/bin/env python3
"""Build a third-party human-review packet without scorer or oracle labels."""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "toxictool_bench/human_audit_v2"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty packet: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def blinded_events(raw: str) -> str:
    """Keep visible evidence while removing poison/scorer metadata."""
    events = json.loads(raw)
    clean: list[dict[str, Any]] = []
    for event in events:
        clean.append({
            "step": event.get("step"),
            "tool_name": event.get("tool_name"),
            "args": event.get("args", {}),
            "clean_observation": event.get("clean_observation", ""),
            "returned_observation": event.get("returned_observation", ""),
        })
    return json.dumps(clean, ensure_ascii=True)


def make_case(evidence: dict[str, str], case_id: str) -> dict[str, str]:
    return {
        "case_id": case_id,
        "blind_id": evidence["blind_id"],
        "family": evidence["family"],
        "user_query": evidence["user_query"],
        "final_answer": evidence["final_answer"],
        "tool_events_json": blinded_events(evidence["tool_events_json"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the external human-review packet.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "toxictool_bench/human_review_v3")
    parser.add_argument("--vr-cases", type=int, default=18)
    parser.add_argument("--seed", type=int, default=20260913)
    args = parser.parse_args()

    evidence = {row["blind_id"]: row for row in read_csv(AUDIT / "evidence.csv")}
    disputed = [row["blind_id"] for row in read_csv(AUDIT / "adjudication.csv")]
    adjudication = [make_case(evidence[blind_id], f"ADJ-{i:03d}") for i, blind_id in enumerate(disputed, 1)]

    merged = read_csv(AUDIT / "merged_labels.csv")
    candidates = [row for row in merged if row["scorer_vr"] == "1" and row["blind_id"] not in disputed]
    by_family: dict[str, list[dict[str, str]]] = {}
    for row in candidates:
        by_family.setdefault(evidence[row["blind_id"]]["family"], []).append(row)
    rng = random.Random(args.seed)
    for rows in by_family.values():
        rng.shuffle(rows)
    selected: list[dict[str, str]] = []
    families = sorted(by_family)
    while len(selected) < min(args.vr_cases, len(candidates)) and families:
        next_families = []
        for family in families:
            rows = by_family[family]
            if rows and len(selected) < args.vr_cases:
                selected.append(rows.pop())
            if rows:
                next_families.append(family)
        families = next_families
    vr_cases = [make_case(evidence[row["blind_id"]], f"VR-{i:03d}") for i, row in enumerate(selected, 1)]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "adjudication_cases.csv", adjudication)
    write_csv(args.output_dir / "adjudication_labels_template.csv", [
        {"case_id": row["case_id"], "blind_id": row["blind_id"], "bcr": "", "adr": "", "vr": "", "rr": "", "notes": ""}
        for row in adjudication
    ])
    write_csv(args.output_dir / "vr_audit_cases.csv", vr_cases)
    write_csv(args.output_dir / "vr_audit_labels_template.csv", [
        {"case_id": row["case_id"], "blind_id": row["blind_id"], "relevant_vr": "", "checked_target": "", "independent_evidence": "", "notes": ""}
        for row in vr_cases
    ])
    print(f"Wrote {len(adjudication)} adjudication cases and {len(vr_cases)} VR-audit cases to {args.output_dir}")


if __name__ == "__main__":
    main()
