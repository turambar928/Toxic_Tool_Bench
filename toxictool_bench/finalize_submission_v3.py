"""Completion gate and paper tables generated only from the frozen full set."""
from __future__ import annotations
import csv
import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path

from submission_revision_v3 import ROOT, OUT, read_jsonl, sha, analyze
from evaluator import evaluate_run
from poisoners import NUMBER_RE
from analyze_human_holdout import write_csv


def main():
    protocol=json.loads((OUT / "protocol.json").read_text())
    paths=[]; rows=[]; residual=[]
    for file,digest in protocol["input_sha256"].items():
        assert sha(ROOT / file)==digest,file
    for j in protocol["jobs"]:
        files=sorted((OUT / "runs" / j["id"]).glob("*.jsonl"))
        found=[r for p in files for r in read_jsonl(p)]
        expected=["clean","toxic"] if j["environment"]=="both" else [j["environment"]]
        assert sorted(r["environment"] for r in found)==sorted(expected),j["id"]
        task=read_jsonl(ROOT / j["task_file"])[j["index"]]
        for r in found:
            assert r["task_id"]==j["task_id"]
            assert r["adapter"]==j["adapter"] and r["model"]==protocol["model"]
            assert r["route_poison_policy"]==j["policy"]
            assert r["poisoner_version"]=="target_scalar_v3"
            assert r["route_count"]==(1 if j["method"]=="Base" else 2)
            assert r["budget"]=={"max_steps_per_route":10,"max_output_tokens_per_request":3072}
            assert r["llm_requests"]<=10*r["route_count"]
            assert r["metrics"]==evaluate_run(task,r["final_answer"],r["tool_events"])
            for route in range(1,r["route_count"]+1):
                assert sum(e["was_poisoned"] for e in r["tool_events"] if e["route_id"]==route)<=1
            if j["policy"]=="shared": assert sum(e["was_poisoned"] for e in r["tool_events"])<=1
            if r["environment"]=="clean": assert not any(e["was_poisoned"] for e in r["tool_events"])
            assert all(e["clean_observation"]!=e["returned_observation"] and
                       not e["clean_observation"].startswith("ERROR:") for e in r["tool_events"] if e["was_poisoned"])
            if task["family"] == "numerical":
                target=float(task["oracle"]["clean_value"])
                tolerance=float(task["oracle"].get("tolerance",1e-6))
                for e in r["tool_events"]:
                    if not e["was_poisoned"]: continue
                    untouched=set(e["clean_observation"].splitlines()) & set(e["returned_observation"].splitlines())
                    matches=[line for line in sorted(untouched) if any(abs(float(m.group().replace(",",""))-target)<=tolerance for m in NUMBER_RE.finditer(line))]
                    residual.append(dict(suite=j["suite"],method=j["method"],policy=j["policy"],task_id=r["task_id"],
                        route=e["route_id"],step=e["step"],clean_value=target,tolerance=tolerance,
                        candidate_clean_reference_remains=bool(matches),unchanged_lines="\n".join(matches)))
        rows.extend(found); paths.extend(files)
    assert len(rows)==152
    analyze()
    write_csv(OUT / "fresh_residual_reference_inventory.csv",residual)
    with (OUT / "fresh_summary.csv").open() as f: summary=list(csv.DictReader(f))
    tables=[]
    for suite,title in [("control","Preselected 16-task control"),("public","Six-task public-data transfer check")]:
        lines=[r"\begin{table}[t]",r"\centering\small",r"\begin{tabular}{@{}llrrrr@{}}",r"\toprule",
               r"Method & Condition & $n$ & TSR & Exposed & Route 2 exposed \\",r"\midrule"]
        ordered=sorted(summary,key=lambda r:({"Base":0,"Double-pass":1,"Verification":2,"Guard":3}[r["method"]],
                                             r["environment"]!="clean",r["policy"]!="shared"))
        for r in ordered:
            if r["suite"]!=suite: continue
            condition="Clean" if r["environment"]=="clean" else ("Shared" if r["policy"]=="shared" else "Per-route")
            route2="--" if r["method"]=="Base" else str(round(float(r["route2_exposed"])*int(r["n"])))
            lines.append(f"{r['method']} & {condition} & {r['n']} & {float(r['task_success']):.3f} & {r['n_exposed']} & {route2} \\\\")
        lines += [r"\bottomrule",r"\end{tabular}",
                  f"\\caption{{{title}, using the repaired injector and frozen scorer. Exposed counts are trajectories with actual corruption, not opportunities. TSR uses all tasks.}}",
                  f"\\label{{tab:fresh-{suite}-v3}}",r"\end{table}"]
        tables.extend(lines)
    (OUT / "fresh_results.tex").write_text("\n".join(tables)+"\n")
    versions={}
    for name in ["numpy","pandas","langgraph","requests"]:
        try: versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: versions[name]="not installed as distribution; adapter may use local source path"
    inputs=paths+[OUT/"protocol.json",OUT/"fresh_summary.csv",OUT/"route_condition_intervals.csv",OUT/"fresh_results.tex",OUT/"fresh_residual_reference_inventory.csv"]
    inputs += [ROOT/"toxictool_bench"/name for name in ["llm_client.py","run_bench.py","finalize_submission_v3.py","resume_submission_v3.py"]]
    manifest=dict(complete=True,trajectories=len(rows),jobs=len(protocol["jobs"]),python=sys.version,packages=versions,
                  logical_requests=sum(r["llm_requests"] for r in rows),tool_calls=sum(len(r["tool_events"]) for r in rows),
                  note="Transport retries and failed attempts are not included in logical request totals or completed-trajectory latency",
                  sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(inputs))})
    (OUT / "completion_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("Completion gate passed: 152 unique expected trajectories; fresh paper tables generated")


if __name__=="__main__":main()
