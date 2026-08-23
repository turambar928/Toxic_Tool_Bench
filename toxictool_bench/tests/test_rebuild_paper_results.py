from __future__ import annotations

import csv
from pathlib import Path
import sys


BENCH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH_DIR))

from rebuild_paper_results import write_clean_transition_summary  # noqa: E402


def _rows(outcomes: dict[str, bool]) -> list[dict]:
    return [
        {
            "task_id": task_id,
            "environment": "clean",
            "metrics": {"task_success": success},
        }
        for task_id, success in outcomes.items()
    ]


def test_clean_transition_summary_counts_overrides_and_repairs(tmp_path):
    spec_rows = [
        ({"suite": "numerical", "variant": "Base"}, _rows({"a": True, "b": True, "c": False})),
        ({"suite": "numerical", "variant": "Full guard"}, _rows({"a": True, "b": False, "c": True})),
    ]
    output = tmp_path / "transitions.csv"

    write_clean_transition_summary(spec_rows, output)

    with output.open(newline="", encoding="utf-8") as handle:
        row = next(csv.DictReader(handle))
    assert row["n_paired"] == "3"
    assert row["stable_correct"] == "1"
    assert row["false_overrides"] == "1"
    assert row["clean_repairs"] == "1"
    assert row["false_override_task_ids"] == "b"
    assert row["clean_repair_task_ids"] == "c"
