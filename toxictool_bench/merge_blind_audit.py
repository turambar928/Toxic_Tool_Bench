#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from audit_agreement import DEFAULT_LABELS, agreement_for_label, mean


def read_by_id(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != len({row["blind_id"] for row in rows}):
        raise ValueError(f"Duplicate blind_id in {path}")
    return {row["blind_id"]: row for row in rows}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and merge independent ToxicBench audit labels.")
    parser.add_argument("--audit-dir", type=Path, default=Path("toxictool_bench/human_audit_v2"))
    args = parser.parse_args()
    evidence = read_by_id(args.audit_dir / "evidence.csv")
    key = read_by_id(args.audit_dir / "key.csv")
    annotator_a = read_by_id(args.audit_dir / "annotator_a.csv")
    annotator_b = read_by_id(args.audit_dir / "annotator_b.csv")
    ids = set(evidence)
    if any(set(table) != ids for table in (key, annotator_a, annotator_b)):
        raise ValueError("Evidence, key, and annotation sheets must contain identical blind_id sets.")

    merged = []
    for blind_id in sorted(ids):
        row = {"blind_id": blind_id, **key[blind_id]}
        for prefix, labels in (("human_a_", annotator_a[blind_id]), ("human_b_", annotator_b[blind_id])):
            for label in DEFAULT_LABELS:
                value = labels.get(label, "").strip()
                if value not in {"0", "1"}:
                    raise ValueError(f"{blind_id} {prefix}{label} must be 0 or 1, got {value!r}")
                row[prefix + label] = value
            row[prefix + "notes"] = labels.get("notes", "")
        merged.append(row)
    write_csv(args.audit_dir / "merged_labels.csv", merged)

    agreement = {label: agreement_for_label(merged, f"human_a_{label}", f"human_b_{label}") for label in DEFAULT_LABELS}
    summary = {
        "n": len(merged),
        "labels": agreement,
        "macro_percent_agreement": mean(item["percent_agreement"] for item in agreement.values()),
        "macro_cohen_kappa": mean(item["cohen_kappa"] for item in agreement.values()),
    }
    (args.audit_dir / "agreement.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    disagreements = [row for row in merged if any(row[f"human_a_{label}"] != row[f"human_b_{label}"] for label in DEFAULT_LABELS)]
    write_csv(args.audit_dir / "adjudication.csv", disagreements or [{"blind_id": "", "status": "no_disagreements"}])
    print(json.dumps(summary, indent=2, sort_keys=True))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
