"""Build a blinded packet from the frozen validation selection, without labels.

Incomplete packets are explicitly marked incomplete. An administrator key and
source hashes stay outside the distributable zip. Existing human sheets are
never overwritten by this builder.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import random
import zipfile
from pathlib import Path

from build_independent_holdout_packet import load_manifest_runs, blinded_events, scrub
from prepare_holdout_adjudication import make_html
from analyze_human_holdout import FIELDS, write_csv, load_cases
from audit_reference_answers import corrected_task
from evaluator import normalize_answer

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/scorer_revision_v2/final_validation'


def read_jsonl(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def evidence_row(task,row,sid,pair):
    context={'oracle':task['oracle'],'reference_status':'human_review_required',
             'data_csv':(ROOT/'toxictool_bench/datasets'/task['dataset']).read_text()}
    return {'sample_id':sid,'pair_id':pair,'user_query':task['user_query'],
        'clean_oracle':str(task['oracle']['clean_answer']),'poisoned_oracle':str(task['oracle']['poisoned_answer']),
        'reference_context_json':json.dumps(context,ensure_ascii=False),
        'final_answer':scrub(normalize_answer(row['final_answer'])),
        'tool_events_json':blinded_events(row['tool_events'])}


def write_packet(directory,evidence,admin,status):
    directory.mkdir(parents=True,exist_ok=True)
    for name in ['annotator_a.csv','annotator_b.csv','adjudication.csv']:
        if (directory/name).exists():
            with (directory/name).open() as f:
                if any(r.get(k,'').strip() for r in csv.DictReader(f) for k in FIELDS):
                    raise ValueError('Refusing to overwrite returned labels')
    write_csv(directory/'evidence.csv',evidence)
    empty=[{k:r[k] for k in ['sample_id','pair_id']}|dict.fromkeys(FIELDS,'')|{'notes':''} for r in evidence]
    for name in ['annotator_a.csv','annotator_b.csv','adjudication.csv']:write_csv(directory/name,empty)
    (directory/'cases.html').write_text(make_html(evidence))
    (directory/'README_CN.md').write_text(
        '# 独立标注包\n\n'+status+'\n\n独立填写 A/B 表；不得使用自动评分辅助标注。'
        '按 reference_context_json 中的容差和原始 CSV 判断。'
        '遇到标准答案与原始数据冲突，标记 ambiguous 并说明，不强行服从参考。'
        '第三人裁决分歧，保留原始 A/B。自动代理不得冒充独立人工标注者。\n')
    files=['evidence.csv','cases.html','annotator_a.csv','annotator_b.csv','adjudication.csv','README_CN.md']
    (directory/'checksums.json').write_text(json.dumps({n:sha(directory/n) for n in files},indent=2)+'\n')
    write_csv(directory.parent/(directory.name+'_admin.csv'),admin)
    with zipfile.ZipFile(directory.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
        for name in files+['checksums.json']:z.write(directory/name,name)


def main():
    protocol=json.loads((OUT/'protocol.json').read_text())
    for name,digest in protocol['parser_sha256'].items():
        if sha(ROOT/'toxictool_bench'/name)!=digest:raise ValueError('Scorer differs from freeze')
    tasks={t['task_id']:t for name in ['numerical','semantic'] for t in read_jsonl(ROOT/f'toxictool_bench/tasks/scorer_validation_{name}_v2.jsonl')}
    rows=[]
    for manifest,split in [('leakage_free_defense_manifest.csv','core'),('verification_stress_manifest.csv','repeated_p1')]:
        ids=set(protocol['semantic_task_ids' if split=='core' else 'repeated_semantic_ids'])
        for row in load_manifest_runs(ROOT/'toxictool_bench/results'/manifest,p1_only=split=='repeated_p1'):
            if row['task_id'] in ids and (split=='core' or row['adapter'] in {'langgraph_react_double_pass','langgraph_react_guarded'}):
                rows.append((split,row,row['_source']))
    if len(rows)!=90:raise ValueError(f'Expected exactly 90 reused trajectories, got {len(rows)}')
    # New logs are accepted only from an explicit successful-run receipt.
    receipt=OUT/'new_run_manifest.json'
    if receipt.exists():
        for spec in json.loads(receipt.read_text())['completed']:
            path=ROOT/spec['source']
            if sha(path)!=spec['sha256']:raise ValueError('New source hash changed')
            for row in read_jsonl(path):rows.append((spec['split'],row,spec['source']))
    identities=[(s,r['task_id'],r['adapter'],r['environment']) for s,r,_ in rows]
    if len(identities)!=len(set(identities)):raise ValueError('Duplicate validation trajectory')
    rng=random.Random(protocol['seed']);rng.shuffle(rows)
    pair_keys=list(dict.fromkeys((s,r['task_id'],r['adapter'] if s!='repeated_p1' else 'methods') for s,r,_ in rows));rng.shuffle(pair_keys)
    pairs={key:f'PAIR-{i+1:03d}' for i,key in enumerate(pair_keys)}
    evidence=[];admin=[]
    for i,(split,row,source) in enumerate(rows):
        key=(split,row['task_id'],row['adapter'] if split!='repeated_p1' else 'methods')
        sid=f'VAL2-{i+1:03d}';pair=pairs[key]
        evidence.append(evidence_row(tasks[row['task_id']],row,sid,pair))
        admin.append({'sample_id':sid,'pair_id':pair,'split':split,'task_id':row['task_id'],
                      'adapter':row['adapter'],'environment':row['environment'],'source':source,'sha256':sha(ROOT/source)})
    complete=len(rows)==200
    status=f'当前 {len(rows)}/200 条轨迹；'+('完整，等待人工参考审查和双人标注。' if complete else '不完整：缺少新数值模型轨迹，不可作为完整独立验证结果。')
    write_packet(OUT/'reviewer_packet',evidence,admin,status)
    (OUT/'packet_status.json').write_text(json.dumps({'n':len(rows),'expected':200,'complete':complete,'human_annotation':'pending',
        'source_hashes':{s:sha(ROOT/s) for _,_,s in rows},'blinding':'Independent shuffled case and pair IDs; no method slots. Trace style may identify methods.'},indent=2)+'\n')
    # Separate errata review: do not mix this with independent validation.
    cases,_=load_cases();evidence=[];admin=[]
    for c in cases:
        task=corrected_task(c['task'])
        if task==c['task']:continue
        row=next(r for r in read_jsonl(ROOT/c['source']) if r['task_id']==c['task_id'] and r['adapter']==c['adapter'] and r['environment']==c['environment'])
        sid=f'ERR-{len(evidence)+1:03d}'
        er=evidence_row(task,row,sid,c['pair_id'])
        ctx=json.loads(er['reference_context_json']);ctx['reference_ineligible']=bool(task.get('reference_ineligible'));er['reference_context_json']=json.dumps(ctx)
        evidence.append(er);admin.append({'sample_id':sid,'original_sample_id':c['sample_id'],'task_id':c['task_id'],'source':c['source']})
    rng.shuffle(evidence)
    write_packet(OUT/'reference_errata_review',evidence,admin,'40 条历史参考勘误复核；这是开发审计，不是独立验证。分母含糊的题请保留歧义。')
    print(status,'Reference errata review:',len(evidence))


if __name__=='__main__':main()
