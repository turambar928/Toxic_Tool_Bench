import copy
import json
import socket
import sys
from pathlib import Path

import pandas as pd
import pytest

BENCH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH))
from audit_reference_answers import corrected_task
from task_acceptance_specs import recipe
from run_task_acceptance import (SUITES, load_tables, std_answer, pandas_answer, reference_match,
                                 run_case, observed_answer, strict_json, sha)


def tasks():
    rows = [json.loads(l) for s in SUITES for l in (BENCH / 'tasks' / (s+'.jsonl')).read_text().splitlines()]
    return [t for t in rows if not corrected_task(t).get('reference_ineligible')]


def test_scope_and_no_oracle_access():
    ts = tasks()
    assert len(ts) == len({t['task_id'] for t in ts}) == 131
    for t in ts:
        allowed = {k: t[k] for k in ['dataset', 'user_query', 'family', 'aux_datasets'] if k in t}
        spec = recipe(allowed)
        changed = copy.deepcopy(t)
        changed['oracle'] = {'clean_answer':'WRONG', 'clean_value':-999999}
        changed['poison'] = {'type':'nonexistent'}
        assert recipe(changed) == spec


def test_two_implementations_for_all_retained_tasks():
    for t in tasks():
        spec, data = recipe(t), load_tables(t)
        std = std_answer(spec, t['dataset'], data)
        other = pandas_answer(spec, t['dataset'], {n: pd.read_csv(BENCH/'datasets'/n) for n in data})
        assert std['labels'] == other['labels'], t['task_id']
        if std['value'] is not None:
            assert std['value'] == pytest.approx(other['value'], abs=1e-9), t['task_id']


def test_reference_check_rejects_wrong_answer_and_missing_tie():
    assert not reference_match(dict(labels=[], value=4), dict(clean_value=5, tolerance=.1))
    assert not reference_match(dict(labels=['A','B'], value=2), dict(clean_answer='A', match_mode='answer_only'))
    assert reference_match(dict(labels=['A','B'], value=2), dict(clean_answer='A', clean_aliases=['B'], match_mode='answer_only'))


def test_source_perturbation_changes_computation():
    spec = dict(op='mean', a='a', b=None, scale=1)
    data = {'table.csv':dict(columns=['a'], rows=[dict(a=1),dict(a=3)])}
    assert std_answer(spec, 'table.csv', data)['value'] == 2
    data['table.csv']['rows'][0]['a'] = 9
    assert std_answer(spec, 'table.csv', data)['value'] == 6


def test_duplicate_keys_are_rejected_not_silently_certified():
    with pytest.raises(ValueError, match='duplicate JSON key'):
        strict_json('{"table":1,"table":2}')


def test_schema_check_is_positional_binding_not_global_candidate_matching():
    task = {'dataset':'table.csv', 'target_tool':'preview'}
    source = {'table.csv':dict(columns=['revenue','cost'], rows=[])}
    text = 'DATASET SUMMARY\n{"columns":["cost","revenue"]}\n\nHEAD\ncost,revenue\n10,8\n'
    actual = observed_answer(text, dict(op='schema',field='revenue'), task, source)
    assert actual['labels'] == ['cost']


@pytest.mark.parametrize('mode', ['one_shot','repeated_p1'])
def test_actual_routes_without_network_and_with_unchanged_sources(monkeypatch, mode):
    def denied(*a, **kw): raise AssertionError('Network is forbidden in acceptance tests')
    monkeypatch.setattr(socket, 'create_connection', denied)
    monkeypatch.setattr(socket.socket, 'connect', denied)
    for tid in ['num_mean_001', 'sem_stale_inventory_011', 'real_join_top_customer_004']:
        t = next(t for t in tasks() if t['task_id'] == tid)
        data, spec = load_tables(t), recipe(t)
        expected = std_answer(spec, t['dataset'], data)
        result = run_case(t, spec, expected, data, mode)
        assert result['clean_execution_matches'], result
        assert result['primary_exposed'], result
        assert result['source_unchanged'], result
        assert len(result['events']) == 3
        if mode == 'one_shot':
            assert result['scripted_retry_correct']
            assert not result['events'][1]['was_poisoned']


def test_non_delivery_is_not_recovery():
    t = copy.deepcopy(next(t for t in tasks() if t['task_id'] == 'num_mean_001'))
    t['oracle']['clean_value'] = -99999  # deliberately missing injector target
    spec, data = recipe(t), load_tables(t)
    result = run_case(t, spec, std_answer(spec, t['dataset'], data), data, 'one_shot')
    assert not result['primary_exposed']
    assert result['raw_route_correct']
    assert result['raw_recovery_after_exposure'] is None
    assert not result['pair_pass']


def test_real_preview_collision_is_unresolved_not_passed():
    t = next(t for t in tasks() if t['task_id'] == 'real_multi_preview_customers_001')
    spec, data = recipe(t), load_tables(t)
    result = run_case(t, spec, std_answer(spec, t['dataset'], data), data, 'one_shot')
    assert result['primary_exposed']
    assert not result['primary_interface_valid']
    assert result['target_changed'] is None
    assert result['raw_recovery_after_valid_target'] is None
    assert not result['pair_pass']


def test_formal_results_integrity_and_complete_denominators():
    output = BENCH.parent / 'output/task_acceptance_v1'
    manifest = json.loads((output/'completion_manifest.json').read_text())
    assert manifest['model_calls'] == 0
    assert manifest['n_tasks'] == 131 and manifest['inputs_unchanged']
    for name, digest in manifest['output_sha256'].items():
        assert sha(output/name) == digest
    protocol = json.loads((output/'protocol.json').read_text())
    for name, digest in protocol['input_sha256'].items():
        assert sha(BENCH.parent/name) == digest
    assert len(protocol['excluded_task_ids']) == 2 and not protocol['unsupported']
    records = [json.loads(p.read_text()) for p in (output/'cases').glob('*.json')]
    assert {r['task_id'] for r in records} == {t['task_id'] for t in tasks()}
    assert all(len(r['scenarios']) == 2 for r in records)
    groups = json.loads((output/'summary.json').read_text())['groups']
    for group in groups:
        cases = [s for r in records if r['family'] == group['family'] for s in r['scenarios'] if s['mode'] == group['mode']]
        assert len(cases) == group['n_executed'] == group['n_tasks']
        for key in ['primary_exposed','target_changed','raw_route_correct','raw_recovery_after_valid_target','pair_pass']:
            assert sum(s[key] is True for s in cases) == group[key]
