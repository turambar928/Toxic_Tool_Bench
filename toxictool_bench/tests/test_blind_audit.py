from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys


BENCH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH_DIR))

from build_blind_audit_packet import stratified_sample  # noqa: E402


def audit_row(family: str, adapter: str, probability: str, task_id: str) -> dict:
    return {
        "family": family,
        "adapter": adapter,
        "_probability": probability,
        "task_id": task_id,
    }


def test_stratified_sample_balances_suites_and_is_deterministic():
    rows = []
    for family in ("numerical", "semantic_schema", "realistic_extension"):
        for adapter in ("a", "b", "c"):
            for probability in ("0.25", "0.50"):
                for index in range(4):
                    rows.append(audit_row(family, adapter, probability, f"{family}-{adapter}-{probability}-{index}"))

    first = stratified_sample(rows, per_suite=12, seed=17)
    second = stratified_sample(rows, per_suite=12, seed=17)

    assert [row["task_id"] for row in first] == [row["task_id"] for row in second]
    assert Counter(row["family"] for row in first) == {
        "numerical": 12,
        "semantic_schema": 12,
        "realistic_extension": 12,
    }
    assert len({row["task_id"] for row in first}) == 36
