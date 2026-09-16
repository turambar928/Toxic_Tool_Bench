"""Run the frozen 110-trajectory matrix, recording first-complete sources.

The default is preflight only; --run executes the prepared matrix. Transport
failures are recorded, never treated as agent failures or silently substituted
with another model. Re-run with --run resumes completed jobs by source hash.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

from llm_client import ChatClient, load_api_config

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/scorer_revision_v2/final_validation'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-file',type=Path,default=ROOT/'api')
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--scope',choices=['all','core','cross_model'],default='all',
                        help='Run all jobs, the Haiku core/repeated jobs, or the GPT cross-model jobs.')
    args=parser.parse_args()
    protocol=json.loads((OUT/'protocol.json').read_text())
    for name,digest in protocol['parser_sha256'].items():
        if sha(ROOT/'toxictool_bench'/name)!=digest:raise SystemExit('Parser freeze mismatch')
    config=load_api_config(args.api_file)
    results=[]
    models=[]
    if args.scope in {'all','core'}:models.append(protocol['core_model'])
    if args.scope in {'all','cross_model'}:models.append(protocol['cross_model'])
    for model in models:
        try:
            answer=ChatClient(args.api_file,model,max_tokens=8,max_retries=0).complete([{'role':'user','content':'Reply OK.'}])
            result={'model':model,'ok':bool(answer),'status':'response_received'}
        except Exception as exc:
            detail=str(exc).replace(config['api_key'],'[REDACTED]')
            result={'model':model,'ok':False,'status':detail[:500]}
        results.append(result)
    stamp=time.strftime('%Y%m%d-%H%M%S')
    (OUT/f'api_preflight_{stamp}.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2),flush=True)
    if not all(r['ok'] for r in results):raise SystemExit('API preflight failed; matrix not started')
    if not args.run:return
    receipt=OUT/'new_run_manifest.json'
    manifest=json.loads(receipt.read_text()) if receipt.exists() else {'protocol_sha256':sha(OUT/'protocol.json'),'completed':[],'failures':[]}
    if manifest['protocol_sha256']!=sha(OUT/'protocol.json'):raise SystemExit('Protocol changed')
    for spec in manifest['completed']:
        if sha(ROOT/spec['source'])!=spec['sha256']:raise SystemExit('Completed source hash changed')
    jobs=[]
    if args.scope in {'all','core'}:
        for adapter in ['langgraph_react_full','langgraph_react_double_pass','langgraph_react_verification_only','langgraph_react_guarded']:
            for index in range(10):jobs.append(('core',adapter,protocol['core_model'],index,'both',False))
        for adapter in ['langgraph_react_double_pass','langgraph_react_guarded']:
            for index in range(5):jobs.append(('repeated_p1',adapter,protocol['core_model'],index,'toxic',True))
    if args.scope in {'all','cross_model'}:
        for index in range(10):jobs.append(('cross_model','autogen_tool_agent',protocol['cross_model'],index,'both',False))
    done={r['job'] for r in manifest['completed']}
    for split,adapter,model,index,environment,repeated in jobs:
        job=f'{split}-{adapter}-{index:02d}'
        if job in done:continue
        run_dir=OUT/'runs'/job/time.strftime('%Y%m%d-%H%M%S')
        budget=protocol['repeated_budget' if repeated else 'core_budget']
        tasks=ROOT/'toxictool_bench/tasks'/('scorer_validation_numerical_repeat_v2.jsonl' if repeated else 'scorer_validation_numerical_v2.jsonl')
        cmd=[sys.executable,str(ROOT/'toxictool_bench/run_full_bench.py'),'--api-file',str(args.api_file.resolve()),
             '--tasks',str(tasks),'--adapter',adapter,'--model',model,'--env',environment,'--start-index',str(index),'--limit','1',
             '--max-steps',str(budget['max_steps']),'--max-tokens',str(budget['max_tokens']),'--temperature','0','--output-dir',str(run_dir)]
        if repeated:cmd+=['--poison-repeat','--poison-probability','1.0']
        result=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True)
        run_dir.mkdir(parents=True,exist_ok=True)
        (run_dir/'run.log').write_text((result.stdout+result.stderr).replace(config['api_key'],'[REDACTED]'))
        paths=list(run_dir.glob('*.jsonl'))
        expected=1 if repeated else 2
        if result.returncode or len(paths)!=1 or len(paths[0].read_text().splitlines())!=expected:
            manifest['failures'].append({'job':job,'returncode':result.returncode,'log':str((run_dir/'run.log').relative_to(ROOT))})
            receipt.write_text(json.dumps(manifest,indent=2)+'\n')
            raise SystemExit(f'Job {job} failed; partial source preserved and excluded from packet')
        manifest['completed'].append({'job':job,'split':split,'source':str(paths[0].relative_to(ROOT)),'sha256':sha(paths[0]),'n':expected})
        receipt.write_text(json.dumps(manifest,indent=2)+'\n')
        print('Completed',job,flush=True)
    print('Completed new trajectories:',sum(s['n'] for s in manifest['completed']))


if __name__=='__main__':main()
