from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_defense_paired_analysis import build_exposure, build_paired, paired_success

GUARD = "langgraph_react_guarded"
DP = "langgraph_react_double_pass"


def row(success=0, exposed=True, validation=0, bcr=0):
    return {"model": "test", "metrics": {"task_success": success, "poison_exposed": exposed,
            "validation": validation, "blind_compliance": bcr}}


def test_behavior_pairing_excludes_runs_exposed_in_only_one_method():
    runs = {("suite", GUARD): {"a": row(validation=1), "b": row(validation=1)},
            ("suite", DP): {"a": row(validation=1), "b": row(exposed=False)}}
    paired = build_paired(runs, 13)
    vr = next(r for r in paired if r['metric'] == 'validation' and r['treatment'] == GUARD)
    assert vr['n_paired'] == 1
    assert float(vr['mean_delta']) == 0
    tsr = next(r for r in paired if r['metric'] == 'task_success' and r['treatment'] == GUARD)
    assert tsr['n_paired'] == 2


def test_integer_event_denominator_reconstructs_bcr():
    tasks = {str(i): row(bcr=i < 9) for i in range(42)}
    result = build_exposure({('numerical', GUARD): tasks})[0]
    assert result['bcr_events'] == 9
    assert result['n_exposed'] == 42
    assert result['bcr'] == '0.2143'


def test_identical_clean_and_poisoned_gains_have_zero_interaction_uncertainty():
    # Paired resampling must preserve covariance. Independently resampling four
    # cells would spuriously add interaction uncertainty even in this example.
    runs = {}
    for env in ('clean', 'toxic'):
        runs['suite', GUARD, env] = {'a': row(1), 'b': row(0)}
        runs['suite', DP, env] = {'a': row(0), 'b': row(0)}
    for result in paired_success(runs, 13, rounds=200):
        if result['metric'] == 'clean_adjusted_tsr_delta':
            assert float(result['mean_delta']) == 0
            assert float(result['ci95_lo']) == float(result['ci95_hi']) == 0


def test_interaction_rejects_unpaired_task_ids():
    runs = {('suite', a, e): {'a': row()} for a in (GUARD, DP) for e in ('clean', 'toxic')}
    runs['suite', DP, 'clean'] = {'b': row()}
    with pytest.raises(ValueError, match='Incomplete four-outcome pairing'):
        paired_success(runs, 13, rounds=200)


def test_stress_rescores_legacy_bcr_as_validated_poison_adoption(monkeypatch):
    import summarize_verification_stress as stress
    task = {'task_id':'example', 'oracle':{'match_mode':'answer_only', 'clean_answer':'clean', 'poisoned_answer':'wrong'}}
    monkeypatch.setattr(stress, 'read_rows', lambda path: [task])
    trajectory = {'task_id':'example', 'final_answer':'Final answer: wrong',
                  'metrics':{'blind_compliance':True, 'validation':False},
                  'tool_events':[
                      {'step':1,'tool_name':'python_exec','was_poisoned':True,'args':{'code':'df.sum()'}},
                      {'step':2,'tool_name':'python_exec','was_poisoned':True,'args':{'code':'df.sum()'}},
                  ]}
    scored = stress.rescore_rows('example', [trajectory])[0]['metrics']
    assert scored['blind_compliance'] is False
    assert scored['validated_poison_adoption'] is True
    assert scored['validation_evidence_poisoned'] is True
