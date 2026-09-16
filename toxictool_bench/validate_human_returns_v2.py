"""Check real human returns against immutable V2 packets; never generate labels.

`check` works on blank packets and emits readiness only. `analyze` requires two
complete independent human sheets, resolved disagreements and a signed-off
provenance declaration. Declarations document, but cannot prove, independence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import zipfile
from datetime import datetime
from pathlib import Path

from analyze_human_holdout import (FIELDS, METRICS, METHODS, read_csv, write_csv,
    labels_by_id, human_metrics, agreement_tables, method_rates, paired_comparisons, load_cases)
from build_validation_v2_packet import evidence_row
from audit_reference_answers import corrected_task
from evaluator import evaluate_run

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "output/scorer_revision_v2/final_validation"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def inspect(packet, returns):
    # Archive is the distributed frozen artifact; never regenerate it on import.
    with zipfile.ZipFile(packet.with_suffix(".zip")) as z:
        for name in ["evidence.csv", "cases.html", "README_CN.md", "checksums.json"]:
            if (packet / name).read_bytes() != z.read(name):
                raise ValueError(f"Frozen evidence changed: {name}")
    evidence = read_csv(packet / "evidence.csv")
    a = labels_by_id(returns / "annotator_a.csv", evidence, allow_blank=True)
    b = labels_by_id(returns / "annotator_b.csv", evidence, allow_blank=True)
    adj = labels_by_id(returns / "adjudication.csv", evidence, allow_blank=True)
    disputes = {s for s in a.keys() & b.keys() if any(a[s][f] != b[s][f] for f in FIELDS)}
    # Non-disputed extra reviews are accepted only with an explanation, and used.
    for s in adj.keys() - disputes:
        if not adj[s]["notes"].strip():
            raise ValueError(f"Additional adjudication needs a note: {s}")
    status = dict(packet=packet.name, expected=len(evidence), annotator_a=len(a), annotator_b=len(b),
                  disputed=len(disputes), adjudicated=len(adj), pending_disputes=sorted(disputes - adj.keys()),
                  human_complete=len(a) == len(b) == len(evidence) and disputes <= adj.keys(),
                  labels_created_by_this_tool=False, archive_sha256=sha(packet.with_suffix(".zip")))
    return evidence, a, b, adj, disputes, status


def validate_provenance(path, require_third):
    p = json.loads(path.read_text())
    if p.get("independent_human_annotation") is not True or p.get("no_model_generated_labels") is not True:
        raise ValueError("Human/no-model-label attestation required")
    roles = ["annotator_a", "annotator_b"] + (["adjudicator"] if require_third else [])
    ids = []
    for role in roles:
        person = p.get(role, {})
        if not person.get("rater_id", "").strip() or person.get("reference_review_complete") is not True:
            raise ValueError(f"Missing rater identity or reference review: {role}")
        datetime.fromisoformat(person["completed_at"].replace("Z", "+00:00"))
        ids.append(person["rater_id"])
    if len(set(ids)) != len(ids):
        raise ValueError("Raters and adjudicator must be distinct people")
    if p.get("blind_to_automatic_labels") is not True:
        raise ValueError("Blinding declaration required")
    return p


def source_records(packet, evidence):
    """Read-only source integrity audit, also usable before any human return."""
    protocol = json.loads((BASE / "protocol.json").read_text())
    for name, digest in protocol["parser_sha256"].items():
        if sha(ROOT / "toxictool_bench" / name) != digest:
            raise ValueError("Frozen scorer changed")
    admin_path = packet.parent / (packet.name + "_admin.csv")
    admin = {r["sample_id"]:r for r in read_csv(admin_path)}
    if set(admin) != {r["sample_id"] for r in evidence}:
        raise ValueError("Evidence/admin mismatch")
    independent = packet.name == "reviewer_packet"
    if independent:
        tasks = {t["task_id"]: t for family in ["numerical", "semantic"]
                 for t in map(json.loads, (ROOT / f"toxictool_bench/tasks/scorer_validation_{family}_v2.jsonl").read_text().splitlines())}
    else:
        old, _ = load_cases()
        old = {c["sample_id"]:c for c in old}
    records, cache = [], {}
    for e in evidence:
        sid = e["sample_id"]
        k = admin[sid]
        if independent:
            task = tasks[k["task_id"]]
            if sha(ROOT / k["source"]) != k["sha256"]:
                raise ValueError("Source changed")
        else:
            original = old[k["original_sample_id"]]
            task = corrected_task(original["task"])
            k = {**original, **k}
        path = ROOT / k["source"]
        if path not in cache:
            cache[path] = [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
        found = [r for r in cache[path] if all(r[key] == k[key] for key in ["task_id", "adapter", "environment"])]
        if len(found) != 1:
            raise ValueError("Nonunique source trajectory")
        run = found[0]
        expected = evidence_row(task, run, sid, e["pair_id"])
        for field in ["user_query", "clean_oracle", "poisoned_oracle", "final_answer", "tool_events_json"]:
            if e[field] != expected[field]:
                raise ValueError(f"Evidence differs from source: {sid}/{field}")
        expected_context = json.loads(expected["reference_context_json"])
        if not independent:
            expected_context["reference_ineligible"] = bool(task.get("reference_ineligible"))
        if json.loads(e["reference_context_json"]) != expected_context:
            raise ValueError(f"Reference context changed: {sid}")
        records.append((e,k,task,run))
    return records, [admin_path, *cache], protocol


def analyze(packet, returns, output):
    evidence, a, b, adj, disputed, status = inspect(packet, returns)
    if not status["human_complete"]:
        raise ValueError("Human labels/adjudication pending; no completed-validation report generated")
    provenance = validate_provenance(returns / "provenance.json", bool(adj))
    records, sources, protocol = source_records(packet, evidence)
    independent = packet.name == "reviewer_packet"
    cases = []
    for e,k,task,run in records:
        sid = e["sample_id"]
        auto = evaluate_run(task, run["final_answer"], run["tool_events"])
        label = adj.get(sid, a[sid])
        if task.get("reference_ineligible") and not label["ambiguous"]:
            raise ValueError("Ineligible ambiguous reference must not enter accuracy denominator")
        cases.append({"sample_id":sid, "pair_id":e["pair_id"], "task_id":k["task_id"],
                      "suite":task["family"], "split":k["split"], "method":METHODS[k["adapter"]],
                      "environment":k["environment"], "exposed":bool(auto["poison_exposed"]),
                      "a":a[sid], "b":b[sid], "adjudication_pending":False,
                      "ratings":{"auto":{m:int(bool(auto[key])) for m,key in METRICS.items()},
                                 "annotator_a":human_metrics(a[sid]), "annotator_b":human_metrics(b[sid]),
                                 "consensus":human_metrics(label)}})
    if output.exists():
        raise ValueError("Choose a new report directory; preserve prior reports")
    output.mkdir(parents=True)
    agreement, accuracy = agreement_tables(cases)
    for name, rows in [("annotator_agreement", agreement), ("scorer_comparison", accuracy),
                       ("method_rates", method_rates(cases))]:
        write_csv(output / (name + ".csv"), rows)
    if independent:
        write_csv(output / "paired_comparisons.csv", paired_comparisons(cases))
    status.update(independent_validation=independent, provenance=provenance,
                  scope="Frozen pre-V4 trajectories; validates scoring, not V4 delivery or data-transfer outcomes.",
                  input_sha256={str(p):sha(p) for p in [*sources, returns / "provenance.json",
                    *[returns / f for f in ["annotator_a.csv", "annotator_b.csv", "adjudication.csv"]]]},
                  parser_sha256=protocol["parser_sha256"])
    (output / "status.json").write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["check", "sources", "analyze"])
    p.add_argument("--kind", choices=["independent", "errata"], default="independent")
    p.add_argument("--returns", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    packet = BASE / ("reviewer_packet" if args.kind == "independent" else "reference_errata_review")
    returns = args.returns or packet
    if args.action == "check":
        print(json.dumps(inspect(packet, returns)[-1], ensure_ascii=False, indent=2))
    elif args.action == "sources":
        evidence = inspect(packet, returns)[0]
        records, sources, protocol = source_records(packet, evidence)
        print(json.dumps({"source_verified":len(records),"human_validation_claimed":False,
                          "sources":len(sources),"parser_sha256":protocol["parser_sha256"]},indent=2))
    elif args.output is None:
        p.error("--output must name a new report directory")
    else:
        analyze(packet, returns, args.output)
