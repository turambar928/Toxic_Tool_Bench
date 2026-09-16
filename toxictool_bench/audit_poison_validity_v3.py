"""Read-only historical exposure audit; not a counterfactual repaired-agent run.

Flags are sufficient reasons for sensitivity exclusion, not an exhaustive
semantic validity classifier. Unflagged means unchecked, not certified valid.
"""
from __future__ import annotations
import copy
import json
import re
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path

from analyze_revision_v2 import ROOT, source_specs, jsonl, sha
from analyze_human_holdout import write_csv
from audit_reference_answers import corrected_task
from evaluator import evaluate_run
from poisoners import NUMBER_RE

OUT = ROOT / "output/submission_revision_v3"
ADAPTERS = {"langgraph_react_full", "smolagents_toolcalling", "autogen_tool_agent",
            "langgraph_react_double_pass", "langgraph_react_guarded",
            "langgraph_react_verification_only", "autogen_guarded", "autogen_verification_only"}
LEGACY_NUMBER = re.compile(r"[-+]?\d+(?:\.\d+)?")


def numeric_signature(text):
    return (NUMBER_RE.sub("<number>", text),
            [float(m.group().replace(",", "")) for m in NUMBER_RE.finditer(text)])


def flags(event, task):
    if not event.get("was_poisoned"):
        return []
    clean, returned = event["clean_observation"], event["returned_observation"]
    out = []
    if clean.lstrip().startswith(("ERROR:", "Traceback (")):
        out.append("error_observation")
    if numeric_signature(clean) == numeric_signature(returned):
        out.append("no_value_or_text_change")
    if event.get("poison_type") == "sign_flip":
        m = LEGACY_NUMBER.search(clean)
        target = task.get("oracle", {}).get("clean_value")
        if m and target is not None and abs(float(m.group()) - float(target)) > 1e-6:
            out.append("off_target_sign_flip")
        if m and not any(n.span() == m.span() for n in NUMBER_RE.finditer(clean)):
            out.append("partial_numeric_token")
    if event.get("poison_type") == "rank_swap":
        oracle = task.get("oracle", {})
        if returned == str(oracle.get("poisoned_answer")) and len(clean) > len(returned):
            if str(oracle.get("clean_answer", "")).lower() not in clean.lower():
                out.append("whole_observation_fallback")
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    events, rows, inputs = [], [], set()
    for experiment, suite, probability, source, task_files in source_specs():
        tasks = {t["task_id"]: t for p in task_files for t in jsonl(ROOT / p)}
        inputs.update([ROOT / source, *(ROOT / p for p in task_files)])
        for line, row in enumerate(jsonl(ROOT / source), 1):
            if row["adapter"] not in ADAPTERS:
                continue
            task = tasks[row["task_id"]]
            revised = corrected_task(task)
            common = dict(experiment=experiment, suite=suite, probability=probability,
                          source=source, line=line, task_id=row["task_id"],
                          model=row["model"], adapter=row["adapter"], environment=row["environment"])
            filtered = copy.deepcopy(row["tool_events"])
            for i, e in enumerate(row["tool_events"]):
                if not e.get("was_poisoned"):
                    continue
                reasons = flags(e, task)
                events.append({**common, "event_index": i, "poison_type": e.get("poison_type"),
                               "flags": ";".join(reasons), "flagged": bool(reasons)})
                if reasons:
                    filtered[i]["was_poisoned"] = False
            if revised.get("reference_ineligible"):
                continue
            for version, ev in [("recorded_exposure", row["tool_events"]), ("flag_excluded_sensitivity", filtered)]:
                metrics = evaluate_run(revised, row["final_answer"], ev)
                rows.append({**common, "version": version, **metrics})
    write_csv(OUT / "historical_poison_events.csv", events)
    groups = defaultdict(list)
    for r in rows:
        groups[tuple(r[k] for k in ("experiment", "suite", "probability", "model", "adapter", "environment", "version"))].append(r)
    summary = []
    for key, rs in sorted(groups.items()):
        exposed = [r for r in rs if r["poison_exposed"]]
        item = dict(zip(("experiment", "suite", "probability", "model", "adapter", "environment", "version"), key))
        item.update(n=len(rs), n_exposed=len(exposed))
        for metric in ["task_success", "blind_compliance", "poison_adoption", "validation", "recovery", "validated_poison_adoption"]:
            denominator = rs if metric == "task_success" else exposed
            item[metric] = sum(r[metric] for r in denominator) / len(denominator) if denominator else None
        summary.append(item)
    write_csv(OUT / "historical_exposure_sensitivity.csv", summary)
    # Common-task exclusion sensitivity removes the entire affected operator,
    # including unflagged events, rather than selecting only successful delivery.
    sign_ids = {t["task_id"] for t in jsonl(ROOT / "toxictool_bench/tasks/numerical_iclr2027.jsonl")
                if t["poison"]["type"] == "sign_flip"}
    defense = [r for r in rows if r["experiment"] == "defense" and
               r["version"] == "recorded_exposure" and r["environment"] == "toxic"]
    intervals = []
    for excluded in [False, True]:
        selected = [r for r in defense if not excluded or r["task_id"] not in sign_ids]
        by_adapter = defaultdict(dict)
        for r in selected: by_adapter[r["adapter"]][r["task_id"]] = r
        for a,b in [("langgraph_react_double_pass", "langgraph_react_full"),
                    ("langgraph_react_guarded", "langgraph_react_double_pass"),
                    ("langgraph_react_verification_only", "langgraph_react_double_pass")]:
            ids = sorted(by_adapter[a].keys() & by_adapter[b].keys())
            d = np.array([int(by_adapter[a][i]["task_success"])-int(by_adapter[b][i]["task_success"]) for i in ids])
            rng = np.random.default_rng(20260916)
            samples = d[rng.integers(0,len(d),(5000,len(d)))].mean(axis=1)
            intervals.append(dict(exclude_sign_tasks=excluded, treatment=a, control=b, n=len(ids),
                delta=float(d.mean()), ci_low=float(np.quantile(samples,.025)), ci_high=float(np.quantile(samples,.975))))
    write_csv(OUT / "historical_operator_exclusion.csv", intervals)
    flagged = [e for e in events if e["flagged"]]
    inputs.update(ROOT / "toxictool_bench" / f for f in
                  ["audit_poison_validity_v3.py", "analyze_revision_v2.py", "poisoners.py",
                   "evaluator.py", "answer_selection.py", "audit_reference_answers.py"])
    inputs.add(ROOT / "toxictool_bench/results/reference_answer_audit.json")
    report = {"scope": "Eight observation-level adapter identifiers; all operators in existing analysis manifests",
              "interpretation": "Conservative flag audit, NOT certification of unflagged events. Sensitivity keeps answers fixed; it cannot restore a consumed opportunity or simulate repaired behavior.",
              "poisoned_events": len(events), "flagged_events": len(flagged),
              "flagged_trajectories": len({(e["source"], e["line"]) for e in flagged}),
              "flags": dict(Counter(f for e in flagged for f in e["flags"].split(";"))),
              "by_experiment": dict(Counter(e["experiment"] for e in flagged)),
              "input_sha256": {str(p.relative_to(ROOT)): sha(p) for p in sorted(inputs)}}
    (OUT / "historical_audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k:v for k,v in report.items() if k != "input_sha256"}, indent=2))


if __name__ == "__main__":
    main()
