from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable


DEFAULT_LABELS = ("bcr", "adr", "vr", "rr")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute agreement for ToxicTool-Bench audit labels.")
    parser.add_argument("--audit-csv", type=Path, required=True)
    parser.add_argument("--a-prefix", default="human_a_")
    parser.add_argument("--b-prefix", default="human_b_")
    parser.add_argument("--labels", nargs="+", default=list(DEFAULT_LABELS))
    parser.add_argument("--output-json", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = read_rows(args.audit_csv)
    results = {
        label: agreement_for_label(rows, f"{args.a_prefix}{label}", f"{args.b_prefix}{label}")
        for label in args.labels
    }
    covered = [item for item in results.values() if item["n"] > 0]
    summary = {
        "audit_csv": str(args.audit_csv),
        "annotator_a_prefix": args.a_prefix,
        "annotator_b_prefix": args.b_prefix,
        "labels": results,
        "macro_percent_agreement": mean(item["percent_agreement"] for item in covered),
        "macro_cohen_kappa": mean(item["cohen_kappa"] for item in covered),
    }
    text = json.dumps(summary, indent=2, sort_keys=True)
    print(text)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text + "\n", encoding="utf-8")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def agreement_for_label(rows: list[dict[str, str]], a_col: str, b_col: str) -> dict[str, float | int | None]:
    pairs: list[tuple[int, int]] = []
    for row in rows:
        a = parse_binary(row.get(a_col, ""))
        b = parse_binary(row.get(b_col, ""))
        if a is None or b is None:
            continue
        pairs.append((a, b))
    if not pairs:
        return {
            "n": 0,
            "percent_agreement": None,
            "cohen_kappa": None,
            "positive_rate_a": None,
            "positive_rate_b": None,
        }

    agree = sum(1 for a, b in pairs if a == b)
    p0 = agree / len(pairs)
    pos_a = sum(a for a, _ in pairs) / len(pairs)
    pos_b = sum(b for _, b in pairs) / len(pairs)
    neg_a = 1.0 - pos_a
    neg_b = 1.0 - pos_b
    pe = pos_a * pos_b + neg_a * neg_b
    kappa = None if pe == 1.0 else (p0 - pe) / (1.0 - pe)
    return {
        "n": len(pairs),
        "percent_agreement": p0,
        "cohen_kappa": kappa,
        "positive_rate_a": pos_a,
        "positive_rate_b": pos_b,
    }


def parse_binary(value: str | None) -> int | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "t", "yes", "y"}:
        return 1
    if normalized in {"0", "false", "f", "no", "n"}:
        return 0
    return None


def mean(values: Iterable[float | None]) -> float | None:
    filtered = [value for value in values if value is not None]
    if not filtered:
        return None
    return sum(filtered) / len(filtered)


if __name__ == "__main__":
    main()
