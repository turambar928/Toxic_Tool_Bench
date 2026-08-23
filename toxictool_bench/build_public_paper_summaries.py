"""Build paper tables from public-agent rows only.

The raw result directory contains historical experiments from adapters that are
not part of the current paper. This script makes the exclusion explicit rather
than relying on an undocumented spreadsheet filter.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


METRICS = ("clean_tsr", "poisoned_tsr", "delta_tsr", "toxic_bcr", "poison_delivery_rate")
POISON_METRICS = ("toxic_tsr", "bcr", "adr", "vr", "rr", "poison_delivery_rate")
PAPER_ADAPTERS = {
    "autogen_tool_agent",
    "langgraph_react_full",
    "pandasai_dataframe",
    "smolagents_toolcalling",
}


def read_rows(path: Path, included: set[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [row for row in csv.DictReader(handle) if row["adapter"] in included]


def mean(rows: list[dict[str, str]], key: str) -> float:
    return sum(float(row[key]) for row in rows) / len(rows)


def write_cross_model(rows: list[dict[str, str]], output: Path, suite: str) -> None:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row["model"]].append(row)
    fields = ["suite", "model", "n_adapters", *METRICS]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for model in sorted(groups):
            group = groups[model]
            writer.writerow(
                {
                    "suite": suite,
                    "model": model,
                    "n_adapters": len(group),
                    **{metric: f"{mean(group, metric):.4f}" for metric in METRICS},
                }
            )


def write_poison_type(rows: list[dict[str, str]], output: Path) -> None:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row["poison_type"]].append(row)
    fields = ["poison_type", "n_groups", *POISON_METRICS]
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for poison_type in sorted(groups):
            group = groups[poison_type]
            writer.writerow(
                {
                    "poison_type": poison_type,
                    "n_groups": len(group),
                    **{metric: f"{mean(group, metric):.4f}" for metric in POISON_METRICS},
                }
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=Path("toxictool_bench/results"))
    parser.add_argument("--output-dir", type=Path, default=Path("toxictool_bench/results"))
    parser.add_argument(
        "--include-adapter",
        action="append",
        help="Adapter to include; defaults to the four common cross-model paper adapters.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    included = set(args.include_adapter or PAPER_ADAPTERS)
    write_cross_model(
        read_rows(args.results_dir / "cross_model_summary.csv", included),
        args.output_dir / "public_cross_model_numerical_summary.csv",
        "numerical",
    )
    write_cross_model(
        read_rows(args.results_dir / "semantic_schema_cross_model_summary.csv", included),
        args.output_dir / "public_cross_model_semantic_schema_summary.csv",
        "semantic/schema",
    )
    write_poison_type(
        read_rows(args.results_dir / "poison_type_summary.csv", included),
        args.output_dir / "public_poison_type_summary.csv",
    )


if __name__ == "__main__":
    main()
