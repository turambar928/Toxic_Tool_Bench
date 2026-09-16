"""Recover infrastructure failures without rerunning completed trajectories.

Use only after previous schedulers and their children have stopped. Initial
attempt logs stay in place. Each additional attempt has a separate log and
status; only missing clean/toxic environments are requested. No score is used.
"""
import json
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from submission_revision_v3 import ROOT, OUT, read_jsonl, sha


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--attempt",type=int,default=1)
    parser.add_argument("--workers",type=int,default=4)
    args=parser.parse_args()
    if args.attempt < 1 or args.workers < 1: raise ValueError("Positive attempt and worker count required")
    protocol=json.loads((OUT / "protocol.json").read_text())
    for file,digest in protocol["input_sha256"].items():
        assert sha(ROOT / file)==digest,file
    pending=[]; original=[]
    for j in protocol["jobs"]:
        folder=OUT / "runs" / j["id"]
        folder.mkdir(parents=True,exist_ok=True)
        status=folder / "status.json"
        if status.exists(): original.append(json.loads(status.read_text()))
        rows=[r for p in folder.glob("*.jsonl") for r in read_jsonl(p)]
        seen=[r["environment"] for r in rows]
        assert len(seen)==len(set(seen)),j["id"]
        expected=["clean","toxic"] if j["environment"]=="both" else [j["environment"]]
        missing=[e for e in expected if e not in seen]
        if missing: pending.append((j,missing))
        else: status.write_text(json.dumps({"job_id":j["id"],"exit_code":0,"complete_from_saved_rows":True})+"\n")
    note=OUT / ("rate_limit_recovery.json" if args.attempt==1 else f"rate_limit_recovery_{args.attempt}.json")
    if note.exists(): raise RuntimeError("Recovery amendment already exists; review before further retries")
    note.write_text(json.dumps({"reason":"HTTP 429 after automatic transport retries; retain every completed trajectory and retry only missing environments",
        "selection":"Infrastructure/completion status only; no answer or metric selection",
        "workers":args.workers,"attempt":args.attempt,"original_status":original,"missing":[{"job_id":j["id"],"environments":missing} for j,missing in pending]},indent=2)+"\n")
    environment={k:v for k,v in os.environ.items() if k.lower() not in {"http_proxy","https_proxy","all_proxy"}}
    environment.update(NO_PROXY="*",no_proxy="*")
    def run(item):
        j,missing=item
        folder=OUT / "runs" / j["id"]
        env="both" if len(missing)==2 else missing[0]
        cmd=[sys.executable,"toxictool_bench/run_full_bench.py","--tasks",j["task_file"],"--api-file","api",
             "--output-dir",str(folder),"--adapter",j["adapter"],"--model",protocol["model"],
             "--env",env,"--start-index",str(j["index"]),"--limit","1",
             "--route-poison-policy",j["policy"],"--max-steps","10","--max-tokens","3072"]
        with (folder / f"recovery_{args.attempt}.log").open("x") as log:
            result=subprocess.run(cmd,cwd=ROOT,env=environment,stdout=log,stderr=log)
        status={"job_id":j["id"],"exit_code":result.returncode,"recovery_attempt":args.attempt}
        (folder / f"recovery_{args.attempt}_status.json").write_text(json.dumps(status)+"\n")
        (folder / "status.json").write_text(json.dumps(status)+"\n")
        print(status,flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(run,pending))


if __name__ == "__main__":main()
