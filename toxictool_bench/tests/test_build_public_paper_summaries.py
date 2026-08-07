from __future__ import annotations

import csv
from pathlib import Path
import sys


BENCH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH_DIR))

from build_public_paper_summaries import read_rows, write_cross_model  # noqa: E402


def test_public_summary_uses_explicit_adapter_allowlist(tmp_path):
    source = tmp_path / "source.csv"
    fields = ["model", "adapter", "clean_tsr", "poisoned_tsr", "delta_tsr", "toxic_bcr"]
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(
            {
                "model": "m",
                "adapter": "public_agent",
                "clean_tsr": "1.0",
                "poisoned_tsr": "0.5",
                "delta_tsr": "0.5",
                "toxic_bcr": "0.4",
            }
        )
        writer.writerow(
            {
                "model": "m",
                "adapter": "dataframe_router",
                "clean_tsr": "0.0",
                "poisoned_tsr": "0.0",
                "delta_tsr": "0.0",
                "toxic_bcr": "0.0",
            }
        )

    output = tmp_path / "public.csv"
    write_cross_model(read_rows(source, {"public_agent"}), output, "numerical")
    with output.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert rows == [
        {
            "suite": "numerical",
            "model": "m",
            "n_adapters": "1",
            "clean_tsr": "1.0000",
            "poisoned_tsr": "0.5000",
            "delta_tsr": "0.5000",
            "toxic_bcr": "0.4000",
        }
    ]
