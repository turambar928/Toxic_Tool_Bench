#!/usr/bin/env python3
"""Fail fast on algebraic and denominator inconsistencies in paper result CSVs."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "toxictool_bench/results"


def number(row: dict[str, str], key: str) -> float | None:
    value = row.get(key, "")
    return float(value) if value not in {"", "NA", "--"} else None


def main() -> None:
    failures: list[str] = []
    checked = 0
    for path in sorted(RESULTS.glob("*.csv")):
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if not rows or not {"bcr", "par", "vpa"}.issubset(rows[0]):
            continue
        for index, row in enumerate(rows, 2):
            bcr, par, vpa = (number(row, key) for key in ("bcr", "par", "vpa"))
            if None in {bcr, par, vpa}:
                continue
            checked += 1
            # Some paper-facing summaries are rounded to two decimals; allow the
            # largest possible combined rounding error, but still catch real gaps.
            if bcr > par + 0.011 or vpa > par + 0.011 or bcr + vpa > par + 0.011:
                failures.append(
                    f"{path.name}:{index} BCR={bcr:.6f}, PAR={par:.6f}, VPA={vpa:.6f}"
                )
            exposed = number(row, "n_exposed")
            total = number(row, "n") or number(row, "n_toxic")
            if exposed is not None and total is not None and exposed > total:
                failures.append(f"{path.name}:{index} n_exposed={exposed} > n={total}")
    if failures:
        raise SystemExit("Result consistency failures:\n" + "\n".join(failures))
    print(f"Checked {checked} rows; no BCR/PAR/VPA or denominator violations.")


if __name__ == "__main__":
    main()
