"""Offline reviewer entry point. No API calls, no generated human labels."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'toxictool_bench'))


def no_network(*args, **kwargs):
    raise RuntimeError('Network access is disabled for supplementary reproduction')


def verify():
    count = 0
    for line in (ROOT / 'SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError('Release checksum mismatch: '+name)
        count += 1
    print(f'Verified {count} release file checksums.', flush=True)


def csvrows(p):
    with p.open(newline='') as f:
        return list(csv.DictReader(f))


def assert_csv(actual, expected):
    a, b = csvrows(actual), csvrows(expected)
    if len(a) != len(b):
        raise AssertionError(f'Row count differs: {actual.name}: {len(a)} != {len(b)}')
    for i, (x, y) in enumerate(zip(a, b)):
        if x.keys() != y.keys():
            raise AssertionError(f'Columns differ: {actual.name}')
        for k in x:
            if x[k] == y[k]:
                continue
            try:
                if math.isclose(float(x[k]), float(y[k]), rel_tol=1e-10, abs_tol=1e-12):
                    continue
            except (ValueError, TypeError):
                pass
            raise AssertionError(f'Golden-result mismatch: {actual.name}, row {i}, field {k}')


def human(out):
    from analyze_human_holdout import (FIELDS, METRICS, human_metrics, agreement_tables,
                                      method_rates, paired_comparisons, write_csv)
    from evaluator import evaluate_run
    for name, expected_dir in [('independent_200','independent'), ('reference_review_40','reference_review')]:
        records = [json.loads(x) for x in (ROOT/'human'/f'{name}.jsonl').read_text().splitlines()]
        cases = []
        for r in records:
            m = evaluate_run(r['task'],r['run']['final_answer'],r['run']['tool_events'])
            case = {k:r[k] for k in ['sample_id','pair_id','task_id','suite','split','method','environment']}
            case.update(exposed=bool(m['poison_exposed']), a=r['annotator_a'], b=r['annotator_b'],
                        adjudication_pending=False,
                        ratings={'auto':{k:int(bool(m[v])) for k,v in METRICS.items()},
                                 'annotator_a':human_metrics(r['annotator_a']),
                                 'annotator_b':human_metrics(r['annotator_b']),
                                 'consensus':human_metrics(r['consensus'])})
            cases.append(case)
        agreement, comparison = agreement_tables(cases)
        tables = {'annotator_agreement':agreement,'scorer_comparison':comparison,
                  'method_rates':method_rates(cases)}
        if name == 'independent_200':
            tables['paired_comparisons'] = paired_comparisons(cases)
            tsr = next(r for r in comparison if r['split']=='all' and r['rater']=='consensus' and r['metric']=='TSR')
            assert (tsr['tp'],tsr['tn'],tsr['fp'],tsr['fn']) == (176,16,0,8)
            assert len(cases)==200 and sum(c['exposed'] for c in cases)==77
        for title, table in tables.items():
            path = out/name/(title+'.csv')
            write_csv(path,table)
            assert_csv(path,ROOT/'output/human_validation_20260920'/expected_dir/(title+'.csv'))
        print(f'Human comparison reproduced: {name}; binary labels unchanged.', flush=True)


def full(out):
    import analyze_revision_v2 as revision
    import audit_poison_validity_v3 as delivery
    revision.OUT = out/'scorer_revision'
    revision.OUT.mkdir()
    records = revision.revision_rows()
    revision.cluster_analysis()
    revision.vpa_inventory(records)
    assert len(records)==5396
    # Compare every recorded score, not only whether aggregate scores improved.
    before = csvrows(ROOT/'output/scorer_revision_v2/trajectory_changes.csv')
    now = csvrows(revision.OUT/'trajectory_changes.csv')
    assert len(before)==len(now)
    score_fields = [k for k in before[0] if k.startswith(('old_','parser_','corrected_'))]
    for i,(a,b) in enumerate(zip(before,now)):
        for k in ['source','line','task_id','model','adapter','environment','reference_eligible',*score_fields]:
            assert a[k]==b[k], f'Row-level score changed: row {i}, field {k}'
    for name in ['version_summary.csv','cluster_sensitivity.csv','vpa_inventory.csv']:
        assert_csv(revision.OUT/name,ROOT/'output/scorer_revision_v2'/name)
    print('All 5,396 versioned trajectory scores and clustered comparisons match.',flush=True)
    delivery.OUT = out/'delivery_audit'
    delivery.main()
    for name in ['historical_exposure_sensitivity.csv','historical_operator_exclusion.csv']:
        assert_csv(delivery.OUT/name,ROOT/'output/submission_revision_v3'/name)
    audit = json.loads((delivery.OUT/'historical_audit.json').read_text())
    assert (audit['poisoned_events'],audit['flagged_events'],audit['flagged_trajectories'])==(3319,204,157)

    # Analysis functions expect their input/output directories together. Work on
    # copies so archived evidence and hashes in the submitted artifact stay intact.
    import analyze_evidence_controls_v4 as evidence
    import evidence_controls_v4 as protocol
    evidence.OUT = out/'evidence_controls'
    shutil.copytree(ROOT/'output/evidence_controls_v4',evidence.OUT)
    protocol.OUT = evidence.OUT
    evidence.main()
    for name in ['summary.csv','paired_effects.csv','delivery_audit.csv','trajectory_metrics.csv']:
        assert_csv(evidence.OUT/name,ROOT/'output/evidence_controls_v4'/name)
    print('All 264 structured-evidence trajectories reproduce archived results.',flush=True)

    import submission_revision_v3 as repaired
    repaired.OUT = out/'repaired_injector'
    shutil.copytree(ROOT/'output/submission_revision_v3',repaired.OUT)
    repaired.analyze()
    for name in ['fresh_summary.csv','route_condition_intervals.csv']:
        assert_csv(repaired.OUT/name,ROOT/'output/submission_revision_v3'/name)

    import run_task_acceptance
    saved = sys.argv
    try:
        sys.argv = ['run_task_acceptance.py','--output',str(out/'task_acceptance')]
        run_task_acceptance.main()
    finally:
        sys.argv = saved
    assert_csv(out/'task_acceptance/summary.csv',ROOT/'output/task_acceptance_v1/summary.csv')
    print('Model-free acceptance for all 131 retained tasks reproduced.',flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['verify','quick','full'])
    p.add_argument('--output',type=Path,default=ROOT/'reproduced')
    args=p.parse_args()
    verify()
    if args.mode=='verify':
        return
    socket.socket.connect=no_network
    socket.create_connection=no_network
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    human(out/'human')
    if args.mode=='full':
        full(out)
    (out/'SUCCESS.json').write_text(json.dumps({'mode':args.mode,'passed':True,'model_calls':0},indent=2)+'\n')
    print(f'SUCCESS: {args.mode}; outputs in {out}',flush=True)


if __name__=='__main__':
    main()
