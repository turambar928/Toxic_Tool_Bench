"""Execute an untouched tail of the frozen queue with additional workers.

The primary runner skips existing status records. Reserve tail jobs *before*
it reaches them; never reserve a directory that it has already created. This
changes scheduling only, not protocol, task membership, or retries.
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from submission_revision_v3 import ROOT, OUT, sha


def main():
    protocol = json.loads((OUT / "protocol.json").read_text())
    for path,digest in protocol["input_sha256"].items():
        assert sha(ROOT / path) == digest, path
    reserved=[]
    for j in protocol["jobs"]:
        if j["suite"] == "control" and j["index"] < 8: continue
        folder=OUT / "runs" / j["id"]
        try: folder.mkdir()
        except FileExistsError: continue
        (folder / "status.json").write_text(json.dumps({"job_id":j["id"],"exit_code":None,"reserved":True})+"\n")
        reserved.append(j)
    amendment=OUT / "scheduling_note.json"
    if amendment.exists(): raise RuntimeError("Do not reserve twice")
    amendment.write_text(json.dumps({"reason":"Additional six workers for untouched tail; no outcome-based changes or retries",
        "reserved_jobs":[j["id"] for j in reserved], "peak_workers":12},indent=2)+"\n")
    environment={k:v for k,v in os.environ.items() if k.lower() not in {"http_proxy","https_proxy","all_proxy"}}
    environment.update(NO_PROXY="*", no_proxy="*")
    def run(j):
        folder=OUT / "runs" / j["id"]
        cmd=[sys.executable,"toxictool_bench/run_full_bench.py","--tasks",j["task_file"],"--api-file","api",
             "--output-dir",str(folder),"--adapter",j["adapter"],"--model",protocol["model"],
             "--env",j["environment"],"--start-index",str(j["index"]),"--limit","1",
             "--route-poison-policy",j["policy"],"--max-steps","10","--max-tokens","3072"]
        with (folder / "run.log").open("w") as log:
            result=subprocess.run(cmd,cwd=ROOT,env=environment,stdout=log,stderr=log)
        status={"job_id":j["id"],"exit_code":result.returncode,"reserved":False}
        (folder / "status.json").write_text(json.dumps(status)+"\n")
        print(status,flush=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        list(pool.map(run,reserved))


if __name__ == "__main__": main()
