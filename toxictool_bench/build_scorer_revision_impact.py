#!/usr/bin/env python3
"""Compare current paper summaries with the committed pre-revision summaries."""

from __future__ import annotations

import csv
import io
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "toxictool_bench/results"
FILES = (
    "cross_model_summary.csv",
    "semantic_schema_cross_model_summary.csv",
    "iclr2027_gpt_expanded_cross_agent_combined_summary.csv",
    "leakage_free_defense_combined_summary.csv",
)
KEYS = ("clean_tsr", "poisoned_tsr", "delta_tsr", "toxic_bcr", "toxic_par", "toxic_vpa", "toxic_adr", "toxic_vr", "toxic_rr")


def rows_from_text(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(text)))


def old_rows(path: str) -> list[dict[str, str]]:
    try:
        text = subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT, text=True)
    except subprocess.CalledProcessError:
        return []
    return rows_from_text(text)


def main() -> None:
    output: list[dict[str, str]] = []
    for filename in FILES:
        current = rows_from_text((RESULTS / filename).read_text(encoding="utf-8"))
        previous = old_rows(f"toxictool_bench/results/{filename}")
        identity = [key for key in ("model", "adapter") if key in current[0]]
        old_by_key = {tuple(row.get(key, "") for key in identity): row for row in previous}
        for row in current:
            key = tuple(row.get(name, "") for name in identity)
            before = old_by_key.get(key, {})
            for metric in KEYS:
                if metric not in row or metric not in before:
                    continue
                new_value = float(row[metric])
                old_value = float(before[metric])
                output.append({
                    "summary": filename,
                    **{name: row.get(name, "") for name in identity},
                    "metric": metric,
                    "old_value": f"{old_value:.6f}",
                    "revised_value": f"{new_value:.6f}",
                    "delta": f"{new_value - old_value:+.6f}",
                })
    destination = RESULTS / "scorer_revision_impact.csv"
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    print(destination)


if __name__ == "__main__":
    main()
