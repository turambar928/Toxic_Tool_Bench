"""Analyze all frozen V4 conditions; no outcome-based filtering or replacement."""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from analyze_human_holdout import write_csv
from evidence_controls_v4 import OUT, ROOT, SEED, sha, verify_protocol
from structured_evidence_v4 import render


def paired_interval(values, rounds=5000):
    """values: dataset -> one within-task contrast per task (replicates averaged)."""
    rng = np.random.default_rng(SEED)
    blocks = [np.asarray(v, dtype=float) for _, v in sorted(values.items())]
    n = sum(len(b) for b in blocks)
    draws = sum(rng.choice(b, size=(rounds, len(b)), replace=True).sum(axis=1) for b in blocks) / n
    return float(sum(b.sum() for b in blocks)/n), *map(float, np.quantile(draws, [.025,.975]))


def main():
    protocol = verify_protocol()
    ts = {t["task_id"]:t for t in json.loads((OUT / "tasks.json").read_text())}
    rows, events, runs = [], [], {}
    for job in protocol["jobs"]:
        path = OUT / "runs" / (job["id"] + ".json")
        if not path.exists():
            raise RuntimeError(f"Incomplete experiment: {job['id']}")
        r = json.loads(path.read_text())
        runs[job["id"]] = r
        assert all(r[k] == v for k,v in job.items())
        t = ts[r["task_id"]]
        if r.get("parent"):
            parent_path = OUT / "runs" / (r["parent"] + ".json")
            assert sha(parent_path) == r["parent_sha256"]
            if r["policy"] == "verify":
                parent = json.loads(parent_path.read_text())
                assert r["messages"][:len(parent["messages"])] == parent["messages"]
        row = {k:r[k] for k in ["id","task_id","dataset","stage","policy","mode","replicate",
                                    "task_success","poison_adoption","status","llm_requests","elapsed_seconds"]}
        row.update(n_exposed=0, n_unmodified_alternative_calls=0, n_tool_errors=0,
                   n_model_requested_calls=sum(not e["seeded"] for e in r["tool_events"]))
        for i,e in enumerate(r["tool_events"]):
            original, returned = e["clean_observation"], e["returned_observation"]
            target = original.get("query") == t["query"] and original.get("status") == "ok"
            changed = [k for k in ["value","decimal","display"]
                       if target and original["result"][k] != returned["result"][k]]
            residual = [k for k in ["value","decimal","display"]
                        if target and original["result"][k] == returned["result"][k]]
            if e["was_poisoned"]:
                assert target and r["mode"] != "clean"
                assert returned["result"]["value"] == t["poisoned_value"]
                assert changed == (["value","decimal","display"] if r["mode"] == "full" else ["value"])
                row["n_exposed"] += 1
            else:
                assert returned == original
            assert e["was_poisoned"] == (target and r["mode"] != "clean")
            if not e["seeded"] and not target and original.get("status") == "ok":
                row["n_unmodified_alternative_calls"] += 1
            row["n_tool_errors"] += original.get("status") == "error"
            events.append(dict(job_id=r["id"], event_index=i, mode=r["mode"], seeded=e["seeded"],
                               target_field=target, exposed=e["was_poisoned"],
                               changed_aliases=len(changed), residual_clean_aliases=len(residual)))
        # Every condition starts with a correctly bound seeded target call.
        assert r["tool_events"][0]["seeded"] and (row["n_exposed"] > 0) == (r["mode"] != "clean")
        rows.append(row)
    expected = {j["id"] for j in protocol["jobs"]}
    assert {p.stem for p in (OUT / "runs").glob("*.json")} == expected
    assert len(rows) == 264
    groups = defaultdict(list)
    for row in rows:
        for scope in ["all", row["dataset"]]:
            groups[(scope,row["stage"],row["policy"],row["mode"])].append(row)
    summary = []
    for (scope,stage,policy,mode), rs in sorted(groups.items()):
        summary.append(dict(dataset=scope,stage=stage,policy=policy,mode=mode,n=len(rs),
            correct=sum(r["task_success"] for r in rs), TSR=np.mean([r["task_success"] for r in rs]),
            adopted=sum(r["poison_adoption"] for r in rs), PAR=np.mean([r["poison_adoption"] for r in rs]),
            exposed=sum(r["n_exposed"]>0 for r in rs),
            alternative_query_runs=sum(r["n_unmodified_alternative_calls"]>0 for r in rs),
            logical_requests=sum(r["llm_requests"] for r in rs)))
    index = {(r["task_id"],r["stage"],r["policy"],r["mode"],r["replicate"]):r for r in rows}
    comparisons = []
    for stage,policy,left,right in [("primary","base","full","clean"), ("primary","base","full","partial"),
                                    ("branch","retry","clean","full"), ("branch","verify","clean","full")]:
        reps = [0] if stage == "primary" else [1,2]
        for metric in ["task_success","poison_adoption"]:
            values = defaultdict(list)
            for tid,t in ts.items():
                delta = np.mean([index[(tid,stage,policy,left,rep)][metric] - index[(tid,stage,policy,right,rep)][metric] for rep in reps])
                values[t["dataset"]].append(float(delta))
            point,lo,hi = paired_interval(values)
            comparisons.append(dict(stage=stage,policy=policy,metric=metric,contrast=left+"-minus-"+right,
                                    n_tasks=24,difference=point,ci95_lo=lo,ci95_hi=hi,
                                    **{f"effect_{k}":float(np.mean(v)) for k,v in values.items()}))
    for name,data in [("trajectory_metrics",rows),("delivery_audit",events),("summary",summary),("paired_effects",comparisons)]:
        write_csv(OUT / (name + ".csv"), data)
    manifest = dict(n_completed=len(rows),expected=264,logical_requests=sum(r["llm_requests"] for r in rows),
                    full_target_events=sum(e["exposed"] and e["mode"]=="full" for e in events),
                    partial_target_events=sum(e["exposed"] and e["mode"]=="partial" for e in events),
                    residual_clean_aliases_in_full=sum(e["residual_clean_aliases"] for e in events if e["exposed"] and e["mode"]=="full"),
                    exhausted=sum(r["status"]!="final" for r in rows),
                    failed_attempts=len(list((OUT/"failures").glob("**/*.json"))),
                    protocol_sha256=sha(OUT / "protocol.json"),
                    analysis_script_sha256=sha(Path(__file__)),
                    run_sha256={name:sha(OUT / "runs" / (name+".json")) for name in sorted(runs)},
                    human_validation="pending; V4 uses a separate structured-numeric endpoint, not a validation of free-text scoring")
    (OUT/"completion_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    latex=[r"\begin{table}[t]",r"\centering\small",r"\begin{tabular}{@{}llrrr@{}}",r"\toprule",
           r"Stage/policy & Evidence & Penguins & Auto MPG & Bike \\",r"\midrule"]
    for stage,policy,mode in [("primary","base","clean"),("primary","base","partial"),("primary","base","full"),
                              ("branch","retry","clean"),("branch","retry","full"),("branch","verify","clean"),("branch","verify","full")]:
        counts=[]
        for dataset in ["penguins","auto_mpg","bike"]:
            s=next(s for s in summary if (s["dataset"],s["stage"],s["policy"],s["mode"])==(dataset,stage,policy,mode))
            counts.append(f"{s['correct']}/{s['n']}")
        label="Primary" if stage=="primary" else policy.capitalize()
        latex.append(label+" & "+mode+" & "+" & ".join(counts)+r" \\")
    latex += [r"\bottomrule",r"\end{tabular}",
              r"\caption{Structured-evidence V4 correctness counts on eight tasks per source. Second-stage cells contain two completions per task sharing a fixed full-poison primary. These are not 16 independent task instances. Full corruption replaces all three target-field aliases; alternative queries and raw rows remain unmodified.}",
              r"\label{tab:evidence-v4}",r"\end{table}"]
    (OUT/"results.tex").write_text("\n".join(latex)+"\n")
    print(json.dumps({k:v for k,v in manifest.items() if k!="run_sha256"},indent=2))
    print(json.dumps(comparisons,indent=2))


if __name__ == "__main__":
    main()
