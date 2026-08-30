from __future__ import annotations

import json
from pathlib import Path
import sys


BENCH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH_DIR))

from summarize_chunked_matrix import normalize_chunks, parse_suite_chunks, select_latest_complete_chunk  # noqa: E402


def write_jsonl(path: Path, rows: list[dict]):
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def row(task_id: str, env: str) -> dict:
    return {
        "task_id": task_id,
        "environment": env,
        "adapter": "data2mcp_dataframe",
        "model": "m",
        "poison": {"type": "x", "severity": "plausible"},
        "metrics": {
            "task_success": True,
            "blind_compliance": False,
            "anomaly_detection": False,
            "validation": False,
            "recovery": False,
        },
    }


def test_select_latest_complete_chunk_skips_partial_files(tmp_path):
    partial = tmp_path / "20260719-000001_data2mcp_dataframe_m_both_start0_limit2.jsonl"
    complete = tmp_path / "20260719-000002_data2mcp_dataframe_m_both_start0_limit2.jsonl"
    write_jsonl(partial, [row("t0", "clean"), row("t0", "toxic"), row("t1", "clean")])
    write_jsonl(complete, [row("t0", "clean"), row("t0", "toxic"), row("t1", "clean"), row("t1", "toxic")])

    selection = select_latest_complete_chunk(
        results_dir=tmp_path,
        adapter="data2mcp_dataframe",
        model="m",
        env="both",
        start_index=0,
        limit=2,
        expected_task_ids={"t0", "t1"},
        suite="suite",
    )

    assert selection is not None
    assert selection.path == complete
    assert selection.rows == 4


def test_select_latest_complete_chunk_rejects_wrong_task_ids(tmp_path):
    path = tmp_path / "20260719-000002_data2mcp_dataframe_m_both_start0_limit2.jsonl"
    write_jsonl(path, [row("other", "clean"), row("other", "toxic")])

    selection = select_latest_complete_chunk(
        results_dir=tmp_path,
        adapter="data2mcp_dataframe",
        model="m",
        env="both",
        start_index=0,
        limit=2,
        expected_task_ids={"t0", "t1"},
        suite="suite",
    )

    assert selection is None


def test_select_latest_complete_chunk_accepts_legacy_start_zero_name(tmp_path):
    legacy = tmp_path / "20260719-000002_data2mcp_dataframe_m_both.jsonl"
    write_jsonl(legacy, [row("t0", "clean"), row("t0", "toxic"), row("t1", "clean"), row("t1", "toxic")])

    selection = select_latest_complete_chunk(
        results_dir=tmp_path,
        adapter="data2mcp_dataframe",
        model="m",
        env="both",
        start_index=0,
        limit=2,
        expected_task_ids={"t0", "t1"},
        suite="suite",
    )

    assert selection is not None
    assert selection.path == legacy


def test_normalize_chunks_supports_mixed_sizes():
    assert normalize_chunks(None, None, ["0:5", "5:5", "20:20"]) == [
        (0, 5),
        (5, 5),
        (20, 20),
    ]


def test_normalize_chunks_preserves_legacy_starts_and_limit():
    assert normalize_chunks([0, 20, 40], 20, None) == [(0, 20), (20, 20), (40, 20)]


def test_parse_suite_chunks_supports_distinct_suite_layouts():
    assert parse_suite_chunks(["numerical=0:20,20:20", "semantic=0:5,5:5"]) == {
        "numerical": [(0, 20), (20, 20)],
        "semantic": [(0, 5), (5, 5)],
    }
