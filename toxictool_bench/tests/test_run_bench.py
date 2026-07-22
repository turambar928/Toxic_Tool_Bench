from __future__ import annotations

from pathlib import Path
import sys


BENCH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH_DIR))

from run_bench import chunk_suffix, select_tasks  # noqa: E402
from run_full_bench import apply_poison_overrides  # noqa: E402


def test_select_tasks_supports_start_index_and_limit():
    tasks = [{"task_id": f"t{i}"} for i in range(6)]

    selected = select_tasks(tasks, start_index=2, limit=3)

    assert [task["task_id"] for task in selected] == ["t2", "t3", "t4"]


def test_select_tasks_limit_zero_returns_all_after_start():
    tasks = [{"task_id": f"t{i}"} for i in range(4)]

    selected = select_tasks(tasks, start_index=1, limit=0)

    assert [task["task_id"] for task in selected] == ["t1", "t2", "t3"]


def test_chunk_suffix_names_chunked_runs():
    assert chunk_suffix(0, 0) == ""
    assert chunk_suffix(0, 5) == "_start0_limit5"
    assert chunk_suffix(10, 5) == "_start10_limit5"
    assert chunk_suffix(10, 0) == "_start10"


def test_apply_poison_overrides_does_not_mutate_input_tasks():
    tasks = [
        {
            "task_id": "t0",
            "poison": {"enabled": True, "poison_once": True},
        }
    ]

    patched = apply_poison_overrides(tasks, probability=0.5, repeat=True)

    assert patched[0]["poison"]["poison_probability"] == 0.5
    assert patched[0]["poison"]["poison_once"] is False
    assert "poison_probability" not in tasks[0]["poison"]
    assert tasks[0]["poison"]["poison_once"] is True
