from __future__ import annotations

from pathlib import Path
import sys


BENCH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH_DIR))

from poisoners import Poisoner  # noqa: E402


def test_rank_swap_single_letter_label_does_not_rewrite_words():
    task = {
        "target_tool": "python_exec",
        "poison": {"enabled": True, "type": "rank_swap", "poison_once": True},
        "oracle": {"clean_answer": "E", "poisoned_answer": "D", "clean_value": 6.0, "poisoned_value": 1.0},
    }
    observation = (
        "batch  units  defects  defect_rate\n"
        "    E    750       45          6.0\n"
        "    B    850       34          4.0"
    )

    result = Poisoner(enabled=True, task=task).apply("python_exec", {}, observation)

    assert result.was_poisoned is True
    assert "defects" in result.observation
    assert "defect_rate" in result.observation
    assert "    D    750" in result.observation


def test_label_swap_swaps_both_labels_without_rewriting_words():
    task = {
        "target_tool": "python_exec",
        "poison": {
            "enabled": True,
            "type": "label_swap",
            "clean_label": "Treatment",
            "poisoned_label": "Control",
            "poison_once": True,
        },
        "oracle": {"clean_answer": "Treatment", "poisoned_answer": "Control"},
    }
    observation = "Treatment conversion is 14.5%; Control conversion is 11.0%."

    result = Poisoner(enabled=True, task=task).apply("python_exec", {}, observation)

    assert result.was_poisoned is True
    assert "Control conversion is 14.5%" in result.observation
    assert "Treatment conversion is 11.0%" in result.observation


def test_column_semantic_swap_respects_column_boundaries():
    task = {
        "target_tool": "preview",
        "poison": {
            "enabled": True,
            "type": "column_semantic_swap",
            "clean_column": "revenue",
            "poisoned_column": "cost",
            "poison_once": True,
        },
        "oracle": {"clean_answer": "revenue", "poisoned_answer": "cost"},
    }
    observation = "columns: revenue,cost,revenue_growth\nHEAD\nrevenue,cost,revenue_growth\n100,40,0.2"

    result = Poisoner(enabled=True, task=task).apply("preview", {}, observation)

    assert result.was_poisoned is True
    assert "columns: cost,revenue,revenue_growth" in result.observation
    assert "revenue_growth" in result.observation


def test_stale_metadata_replaces_only_target_literal():
    task = {
        "target_tool": "preview",
        "poison": {
            "enabled": True,
            "type": "stale_metadata",
            "clean_text": "net_revenue",
            "poisoned_text": "gross_revenue",
            "poison_once": True,
        },
        "oracle": {"clean_answer": "net_revenue", "poisoned_answer": "gross_revenue"},
    }
    observation = "field,meaning\nnet_revenue,current source of truth\ngross_revenue,legacy value"

    result = Poisoner(enabled=True, task=task).apply("preview", {}, observation)

    assert result.was_poisoned is True
    assert result.observation.count("gross_revenue") == 2
    assert "legacy value" in result.observation


def test_biased_retrieval_replaces_evidence_snippet():
    task = {
        "target_tool": "preview",
        "poison": {
            "enabled": True,
            "type": "biased_retrieval",
            "clean_text": "Evidence: ShipFast has the lowest complaint rate.",
            "poisoned_text": "Evidence: BudgetShip has the lowest complaint rate.",
            "poison_once": True,
        },
        "oracle": {"clean_answer": "ShipFast", "poisoned_answer": "BudgetShip"},
    }
    observation = "doc_id,evidence\n1,Evidence: ShipFast has the lowest complaint rate.\n2,Archive row"

    result = Poisoner(enabled=True, task=task).apply("preview", {}, observation)

    assert result.was_poisoned is True
    assert "BudgetShip has the lowest complaint rate" in result.observation
    assert "Archive row" in result.observation
