from __future__ import annotations

from pathlib import Path
import csv
import sys


BENCH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH_DIR))

from summarize_results import write_severity  # noqa: E402


def test_write_severity_groups_by_poison_type_and_severity(tmp_path):
    rows = [
        {
            "environment": "toxic",
            "model": "m",
            "adapter": "a",
            "poison": {"type": "aggregate_scale", "severity": "plausible"},
            "metrics": {
                "task_success": False,
                "blind_compliance": True,
                "anomaly_detection": False,
                "validation": False,
                "recovery": False,
            },
        },
        {
            "environment": "toxic",
            "model": "m",
            "adapter": "a",
            "poison": {"type": "aggregate_scale", "severity": "plausible"},
            "metrics": {
                "task_success": True,
                "blind_compliance": False,
                "anomaly_detection": True,
                "validation": True,
                "recovery": True,
            },
        },
    ]
    path = tmp_path / "severity.csv"

    write_severity(rows, path)

    with path.open(newline="", encoding="utf-8") as f:
        out = list(csv.DictReader(f))
    assert len(out) == 1
    assert out[0]["poison_type"] == "aggregate_scale"
    assert out[0]["severity"] == "plausible"
    assert out[0]["bcr"] == "0.50"
    assert out[0]["n"] == "2"
