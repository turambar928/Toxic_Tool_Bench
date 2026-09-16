from __future__ import annotations

from pathlib import Path
import sys


BENCH_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH_DIR))

from poisoners import Poisoner  # noqa: E402
import pytest


def numeric_poison(old=70.0, new=-70.0, kind="sign_flip", **extra):
    return Poisoner(True, {"target_tool": "python_exec",
        "poison": {"enabled": True, "type": kind, "poison_once": True, **extra},
        "oracle": {"clean_value": old, "poisoned_value": new}})


def test_sign_flip_waits_for_scalar_and_does_not_consume_once_on_index():
    p = numeric_poison()
    table = "  month revenue\n0 2025-01 100\n1 2025-02 170"
    assert not p.apply("python_exec", {}, table).was_poisoned
    assert not p.used
    r = p.apply("python_exec", {}, table + "\nGrowth rate: 70.00%")
    assert r.was_poisoned
    assert r.observation == table + "\nGrowth rate: -70.0%"


@pytest.mark.parametrize("text", ["ERROR: ValueError 70", "Traceback (70)",
    "0 70", "70 row_label", "70 2025-01", "a=70 b=80", "a=70\nb=70", "value=170", "date=2070-01-01"])
def test_no_unsafe_numeric_replacement(text):
    p = numeric_poison()
    assert not p.apply("python_exec", {}, text).was_poisoned
    assert not p.used


def test_numeric_tokens_and_explicit_field_binding():
    p = numeric_poison(6300, 21900, "value_replace", target_field="Profit")
    assert not p.apply("python_exec", {}, "Cost: $6,300").was_poisoned
    assert p.apply("python_exec", {}, "Profit: $6,300").observation == "Profit: $21900.0"
    assert not numeric_poison(6, 12, "value_replace").apply("python_exec", {}, "$6,300").was_poisoned
    assert numeric_poison(6300, 21900, "value_replace").apply("python_exec", {}, "6.3e3").was_poisoned


def test_zero_flip_and_missing_rank_target_are_not_exposures():
    assert not numeric_poison(0, 0).apply("python_exec", {}, "0").was_poisoned
    p = Poisoner(True, {"poison": {"enabled": True, "type": "rank_swap"},
                        "oracle": {"clean_answer": "Email", "poisoned_answer": "Display"}})
    assert p.apply("python_exec", {}, "Search leads the comparison").observation == "Search leads the comparison"


@pytest.mark.parametrize("policy, expected", [("shared", False), ("per_route", True)])
def test_route_reset_keeps_event_history(policy, expected):
    from tools import DataToolEnv
    p = numeric_poison()
    task = {**p.task, "dataset": "monthly_revenue.csv"}
    env = DataToolEnv(task, BENCH_DIR, True)
    env.route_poison_policy = policy
    env.begin_route()
    env.call("python_exec", {"code": "print(70)"})
    env.begin_route()
    env.call("python_exec", {"code": "print(70)"})
    assert [e["route_id"] for e in env.events] == [1, 2]
    assert env.events[1]["was_poisoned"] is expected


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


def test_value_replace_uses_oracle_values_for_new_numeric_taxonomy():
    task = {
        "target_tool": "python_exec",
        "poison": {"enabled": True, "type": "unit_conversion", "poison_once": True},
        "oracle": {"clean_value": 2.5, "poisoned_value": 2500.0},
    }
    observation = "The average shipment weight is 2.5 kg."

    result = Poisoner(enabled=True, task=task).apply("python_exec", {}, observation)

    assert result.was_poisoned is True
    assert "2500.0 kg" in result.observation


def test_poison_probability_zero_disables_eligible_poison():
    task = {
        "task_id": "probability_gate",
        "target_tool": "python_exec",
        "poison": {"enabled": True, "type": "aggregate_scale", "scale": 2.0, "poison_probability": 0.0},
        "oracle": {"clean_value": 10.0, "poisoned_value": 20.0},
    }

    result = Poisoner(enabled=True, task=task).apply("python_exec", {}, "mean = 10.0")

    assert result.was_poisoned is False
    assert result.observation == "mean = 10.0"
