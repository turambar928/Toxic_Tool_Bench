#!/usr/bin/env python3
"""Validate completed follow-up review and build adjudicated audit artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "toxictool_bench/human_audit_v2"
REVIEW_DIR = ROOT / "toxictool_bench/human_review_v3"
LABELS = ("bcr", "adr", "vr", "rr")
VR_LABELS = ("relevant_vr", "checked_target", "independent_evidence")


def read_by_id(path: Path, id_field: str = "blind_id") -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or len(rows) != len({row[id_field] for row in rows}):
        raise ValueError(f"{path} is empty or has duplicate {id_field} values")
    return {row[id_field]: row for row in rows}


def require_binary(rows: dict[str, dict[str, str]], fields: tuple[str, ...], path: Path) -> None:
    for row_id, row in rows.items():
        for field in fields:
            if row.get(field, "").strip() not in {"0", "1"}:
                raise ValueError(f"{path}: {row_id} {field} must be 0 or 1")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--adjudication",
        type=Path,
        default=REVIEW_DIR / "adjudication_labels_completed_2026-09-13.csv",
    )
    parser.add_argument(
        "--vr-audit",
        type=Path,
        default=REVIEW_DIR / "vr_audit_labels_completed_2026-09-13.csv",
    )
    args = parser.parse_args()

    merged = read_by_id(AUDIT_DIR / "merged_labels.csv")
    disputed = read_by_id(AUDIT_DIR / "adjudication.csv")
    adjudication = read_by_id(args.adjudication)
    vr_cases = read_by_id(REVIEW_DIR / "vr_audit_cases.csv")
    vr_audit = read_by_id(args.vr_audit)
    if set(adjudication) != set(disputed):
        raise ValueError("completed adjudication IDs do not match the 12 disputed IDs")
    if set(vr_audit) != set(vr_cases):
        raise ValueError("completed VR-audit IDs do not match the released VR cases")
    require_binary(adjudication, LABELS, args.adjudication)
    require_binary(vr_audit, VR_LABELS, args.vr_audit)

    adjudicated_rows: list[dict[str, Any]] = []
    resolved_cells = 0
    for blind_id in sorted(merged):
        source = merged[blind_id]
        output: dict[str, Any] = dict(source)
        output["has_any_pre_adjudication_disagreement"] = int(blind_id in disputed)
        for label in LABELS:
            a = source[f"human_a_{label}"]
            b = source[f"human_b_{label}"]
            if a == b:
                consensus = a
                method = "pre_adjudication_agreement"
            else:
                consensus = adjudication[blind_id][label]
                method = "third_party_adjudication"
                resolved_cells += 1
            output[f"human_consensus_{label}"] = consensus
            output[f"consensus_method_{label}"] = method
        output["adjudication_notes"] = adjudication.get(blind_id, {}).get("notes", "")
        adjudicated_rows.append(output)
    write_csv(AUDIT_DIR / "adjudicated_labels.csv", adjudicated_rows)

    vr_summary: dict[str, Any] = {
        "audit_file": str(args.vr_audit.relative_to(ROOT)),
        "n": len(vr_audit),
        "selection": "Deterministic suite-rotating sample of non-disputed scorer-positive VR cases.",
        "labels": {},
    }
    for label in VR_LABELS:
        positives = sum(row[label] == "1" for row in vr_audit.values())
        vr_summary["labels"][label] = {
            "positive": positives,
            "negative": len(vr_audit) - positives,
            "rate": positives / len(vr_audit),
        }
    (REVIEW_DIR / "vr_audit_summary.json").write_text(
        json.dumps(vr_summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Wrote 120 adjudicated rows; resolved {resolved_cells} disputed label cells")
    print(json.dumps(vr_summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
