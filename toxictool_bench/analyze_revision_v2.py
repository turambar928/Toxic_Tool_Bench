"""Versioned row-level sensitivity, clustered inference, and VPA evidence inventory.

Original task definitions, run logs and human annotations are read-only inputs.
All numerical-reference changes are reported separately from parser changes.
"""
from __future__ import annotations
import csv
import hashlib
import json
import re
import subprocess
import types
from collections import defaultdict
from pathlib import Path
import numpy as np

from evaluator import evaluate_run, normalize_answer, _is_evidence_tool
from answer_selection import select_answer
from audit_reference_answers import corrected_task
from build_defense_paired_analysis import load_runs, DEFAULT_MANIFEST
from analyze_human_holdout import load_cases, agreement_tables, write_csv

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/scorer_revision_v2'
BASE='4ae42cdd4de2cc0217f03af3f5caefe305a92249'


def jsonl(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def csvrows(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def old_evaluator():
    m=types.ModuleType('fixed_baseline_evaluator')
    source=subprocess.check_output(['git','show',f'{BASE}:toxictool_bench/evaluator.py'],cwd=ROOT,text=True)
    exec(compile(source,'fixed_baseline_evaluator','exec'),m.__dict__)
    return m


def source_specs():
    specs=[]
    for s in csvrows(ROOT/'toxictool_bench/results/paper_run_manifest.csv'):
        if s['experiment'] in {'cross_model','expanded_gpt','autogen_guard','alternative_baseline'}:
            specs.append((s['experiment'],s['suite'],'poison_once',s['source'],s['tasks'].split(';')))
    for name,experiment in [('leakage_free_defense_manifest.csv','defense'),('verification_stress_manifest.csv','stress')]:
        for s in csvrows(ROOT/'toxictool_bench/results'/name):
            specs.append((experiment,s['suite'],s.get('poison_probability','poison_once'),s['path'],
                          [f"toxictool_bench/tasks/{s['suite']}.jsonl"]))
    return specs


def revision_rows():
    old=old_evaluator(); differences=[]; all_rows=[]; inputs=set()
    for experiment,suite,p,source,task_files in source_specs():
        tasks={t['task_id']:t for file in task_files for t in jsonl(ROOT/file)}
        inputs.update([ROOT/source,*[ROOT/f for f in task_files]])
        for lineno,row in enumerate(jsonl(ROOT/source),1):
            task=tasks[row['task_id']]; corrected=corrected_task(task)
            a=old.evaluate_run(task,row['final_answer'],row['tool_events'])
            b=evaluate_run(task,row['final_answer'],row['tool_events'])
            c=evaluate_run(corrected,row['final_answer'],row['tool_events'])
            detail=select_answer(normalize_answer(row['final_answer']),task['user_query'],task['oracle'],
                                 answer_only=task['task_id'] in {'num_rank_003','num_ratio_004'})
            common={'experiment':experiment,'suite':suite,'probability':p,'source':source,'line':lineno,
                    'task_id':row['task_id'],'model':row['model'],'adapter':row['adapter'],'environment':row['environment'],
                    'reference_eligible':not corrected.get('reference_ineligible',False),
                    'old_selection':a['answer_selection'],'parser_selection':b['answer_selection'],
                    'corrected_selection':c['answer_selection'],'selection_rule':detail['rule'],'evidence':detail['evidence']}
            for m in ['task_success','poison_adoption','blind_compliance','validated_poison_adoption','anomaly_detection','validation','recovery','poison_exposed']:
                common.update({f'old_{m}':a[m],f'parser_{m}':b[m],f'corrected_{m}':c[m]})
            differences.append(common)
            all_rows.append((common,task,row,c))
    write_csv(OUT/'trajectory_changes.csv',differences)
    groups=defaultdict(list)
    for r in differences:groups[(r['experiment'],r['suite'],r['probability'],r['model'],r['adapter'],r['environment'])].append(r)
    summaries=[]
    for key,rows in sorted(groups.items()):
        for version in ['old','parser','corrected']:
            eligible=[r for r in rows if version!='corrected' or r['reference_eligible']]
            exposed=[r for r in eligible if r[f'{version}_poison_exposed']]
            item=dict(zip(['experiment','suite','probability','model','adapter','environment'],key))
            item.update(version=version,n=len(eligible),n_exposed=len(exposed))
            for metric in ['task_success','poison_adoption','blind_compliance','validated_poison_adoption','validation','recovery']:
                es=eligible if metric=='task_success' else exposed
                item[metric]=sum(r[f'{version}_{metric}'] for r in es)/len(es) if es else None
            summaries.append(item)
    write_csv(OUT/'version_summary.csv',summaries)
    inputs.update(ROOT/'toxictool_bench'/f for f in ['evaluator.py','answer_selection.py','audit_reference_answers.py','analyze_revision_v2.py'])
    inputs.add(ROOT/'toxictool_bench/results/reference_answer_audit.json')
    (OUT/'analysis_manifest.json').write_text(json.dumps({'baseline_commit':BASE,'n_trajectories':len(differences),
         'scoring_versions':['old parser / old references','new parser / old references','new parser / corrected references, two ambiguous task IDs excluded'],
         'human_labels_changed':False,'input_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted(inputs)}},indent=2)+'\n')
    return all_rows


def template(task):
    q=re.sub(r' (?:Validate using the raw rows if the result seems surprising\.|Cross-check against the table if necessary\.)','',task['user_query'])
    poison={k:v for k,v in task['poison'].items() if k not in {'severity','poison_probability','poison_once'}}
    return json.dumps([task['dataset'],q,poison],sort_keys=True)


def cluster_analysis():
    runs=load_runs(DEFAULT_MANIFEST)
    tasks={t['task_id']:t for s in ['numerical_iclr2027','semantic_schema_iclr2027'] for t in jsonl(ROOT/f'toxictool_bench/tasks/{s}.jsonl')}
    names={'Base':'langgraph_react_full','Double-pass':'langgraph_react_double_pass','Guard':'langgraph_react_guarded','Verification':'langgraph_react_verification_only'}
    output=[]
    for treatment,control in [('Double-pass','Base'),('Guard','Double-pass'),('Verification','Double-pass')]:
        for suite in ['numerical_iclr2027','semantic_schema_iclr2027','combined']:
            ss=['numerical_iclr2027','semantic_schema_iclr2027'] if suite=='combined' else [suite]
            for environment in ['clean','toxic','interaction']:
                blocks=[]
                for s in ss:
                    ids=sorted(runs[s,names[treatment],'clean'])
                    vals=[]
                    for tid in ids:
                        def delta(e):return int(runs[s,names[treatment],e][tid]['metrics']['task_success'])-int(runs[s,names[control],e][tid]['metrics']['task_success'])
                        vals.append(delta('toxic')-delta('clean') if environment=='interaction' else delta(environment))
                    blocks.append((ids,vals))
                for unit in ['instance','template','dataset']:
                    numer=np.zeros(5000);denom=np.zeros(5000);nclusters=0;balanced=[]
                    rng=np.random.default_rng(20260916)
                    for ids,values in blocks:
                        groups=defaultdict(list)
                        for tid,v in zip(ids,values):
                            group=tid if unit=='instance' else template(tasks[tid]) if unit=='template' else tasks[tid]['dataset']
                            groups[group].append(v)
                        sums=np.array([sum(v) for v in groups.values()]); sizes=np.array([len(v) for v in groups.values()])
                        draws=rng.integers(0,len(groups),(5000,len(groups)))
                        # Preserve the selected suite weights in every draw.
                        means=sums[draws].sum(axis=1)/sizes[draws].sum(axis=1)
                        numer+=len(ids)*means;denom+=len(ids);nclusters+=len(groups)
                        balanced.extend(sum(v)/len(v) for v in groups.values())
                    samples=numer/denom
                    if unit=='dataset' and len(blocks)>1:
                        # Shared CSVs across suites must receive the same draw
                        # multiplicity; otherwise cross-suite dependence is lost.
                        keys=sorted({tasks[tid]['dataset'] for ids,_ in blocks for tid in ids})
                        index={k:i for i,k in enumerate(keys)}
                        weights=rng.multinomial(len(keys),np.ones(len(keys))/len(keys),size=5000)
                        weighted=np.zeros(5000);valid=np.ones(5000,dtype=bool);merged=defaultdict(list)
                        for ids,values in blocks:
                            sums=np.zeros(len(keys));sizes=np.zeros(len(keys))
                            for tid,v in zip(ids,values):
                                k=tasks[tid]['dataset'];sums[index[k]]+=v;sizes[index[k]]+=1;merged[k].append(v)
                            denominators=weights@sizes;valid&=denominators>0
                            weighted+=len(ids)*(weights@sums)/np.maximum(denominators,1)
                        samples=weighted[valid]/sum(len(ids) for ids,_ in blocks)
                        nclusters=len(keys);balanced=[sum(v)/len(v) for v in merged.values()]
                    flat=[v for _,vs in blocks for v in vs]
                    output.append({'suite':suite,'treatment':treatment,'control':control,'environment':environment,
                        'resampling_unit':unit,'n_instances':len(flat),'n_clusters':nclusters,'difference':sum(flat)/len(flat),
                        'ci95_lo':float(np.quantile(samples,.025)),'ci95_hi':float(np.quantile(samples,.975)),
                        'equal_cluster_weight_difference':sum(balanced)/len(balanced),'rounds':5000,'seed':20260916})
    write_csv(OUT/'cluster_sensitivity.csv',output)


def vpa_inventory(rows):
    inventory=[];events=[]
    for meta,task,row,metrics in rows:
        if meta['experiment']!='stress' or not meta['reference_eligible'] or not metrics['validated_poison_adoption']:continue
        poisoned=next(e for e in row['tool_events'] if e.get('was_poisoned'))
        checks=[e for e in row['tool_events'] if e.get('step',-1)>poisoned['step'] and _is_evidence_tool(task,e,poisoned_event=poisoned)]
        matched=False
        for e in checks:
            # Preserve the evidence while normalizing presentation-only line
            # padding emitted by dataframe ``info()`` output.
            text='\n'.join(line.rstrip() for line in str(e.get('returned_observation','')).splitlines())
            # This is a candidate evidence match, NOT a correctness adjudication.
            selection=select_answer(text,task['user_query'],corrected_task(task)['oracle'])['selection']
            hit=not e.get('was_poisoned',False) and selection=='clean'
            matched|=hit
            events.append({'source':meta['source'],'task_id':task['task_id'],'step':e['step'],
                'was_poisoned':e.get('was_poisoned',False),'unmodified_clean_candidate_match':hit,
                'args':json.dumps(e.get('args',{})),'returned_observation':text,'final_answer':row['final_answer']})
        inventory.append({k:meta[k] for k in ['source','task_id','suite','probability','adapter']}|{
            'n_checks':len(checks),'n_poisoned_checks':sum(bool(e.get('was_poisoned')) for e in checks),
            'n_unmodified_checks':sum(not e.get('was_poisoned',False) for e in checks),
            'unmodified_clean_candidate_match':matched,
            'mechanism_status':'candidate_for_correct_evidence_review' if matched else 'all_checks_poisoned' if checks and all(e.get('was_poisoned') for e in checks) else 'unmodified_evidence_sufficiency_unresolved'})
    write_csv(OUT/'vpa_inventory.csv',inventory)
    write_csv(OUT/'vpa_evidence.csv',events)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=revision_rows();cluster_analysis();vpa_inventory(rows)
    cases,_=load_cases()
    impacted=[{'sample_id':c['sample_id'],'task_id':c['task_id'],'source':c['source'],
               'reason':'reference_erratum_requires_human_recheck','original_human_tsr':c['ratings']['consensus']['TSR']}
              for c in cases if corrected_task(c['task'])!=c['task']]
    write_csv(OUT/'human_reference_recheck_required.csv',impacted)
    print('Versioned sensitivity complete:',len(rows),'trajectories;',len(impacted),'human rows need reference recheck')


if __name__=='__main__':main()
