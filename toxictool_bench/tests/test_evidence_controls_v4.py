import copy
import csv
import json
import sys
from pathlib import Path

import pytest

BENCH = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH))
from structured_evidence_v4 import canonical, intervene, render, EvidenceEnv
from evidence_controls_v4 import tasks, parse


def sample():
    query = canonical({"op":"mean", "column":"a"})
    return query, {"status":"ok", "query":query, "result":render(6300.)}


def test_full_alias_binding_and_partial_distinction():
    q, original = sample()
    before = copy.deepcopy(original)
    full, yes = intervene(original, q, 7000., "full")
    assert yes and full["result"] == render(7000.)
    assert original == before
    partial, yes = intervene(original, q, 7000., "partial")
    assert yes and partial["result"] == {**render(6300.), "value":7000.}
    assert original["query"] == full["query"]


def test_noop_error_wrong_field_and_rounded_noop_are_not_exposure():
    q, obs = sample()
    for target, value, original in [(dict(q, column="b"),7000,obs), (q,6300,obs),
                                   (q,6300.000001,obs), (q,7000,{"status":"error"})]:
        out, exposed = intervene(original, target, value, "full")
        assert not exposed and out == original


def test_query_identity_not_value_identity():
    q, obs = sample()
    for change in [{"op":"sum"}, {"scale":2}, {"filters":{"a":"3"}}]:
        out, exposed = intervene(obs, {**q, **change}, 7000, "full")
        assert not exposed
    assert canonical({"op":"mean", "column":"a", "filters":{"y":2,"x":1}}) == canonical(
        {"op":"mean", "column":"a", "filters":{"x":"1","y":"2"},"scale":1})


def test_source_invariance_and_alternative_computation(tmp_path):
    path = tmp_path / "table.csv"
    path.write_text("a,b\n1,1\n3,3\n")
    original = path.read_bytes()
    task = {"query":{"op":"mean", "column":"a"},"poisoned_value":10}
    env = EvidenceEnv(path, task, "full")
    assert json.loads(env.call("aggregate",task["query"]))["result"]["value"] == 10
    assert json.loads(env.call("aggregate",{"op":"mean","column":"b"}))["result"]["value"] == 2
    assert json.loads(env.call("aggregate",{"op":"sum","column":"a"}))["result"]["value"] == 4
    assert json.loads(env.call("raw_values",{"column":"a"}))["values"] == ["1","3"]
    assert path.read_bytes() == original and sum(e["was_poisoned"] for e in env.events) == 1


def test_real_references_agree_across_independent_implementations():
    ts = tasks()  # standard-library reference checked against pandas
    assert len(ts) == 24 and len({t["task_id"] for t in ts}) == 24
    assert {t["row_count"] for t in ts} == {344,398,17379}
    for t in ts:
        assert abs(t["clean_value"] - t["poisoned_value"]) > t["tolerance"] * 2


@pytest.mark.parametrize("text", ['{"final":true}', '{"final":"2"}', '{"final":NaN}',
                                  '{"final":2,"tool":"aggregate"}', 'Answer 2', '[]'])
def test_structured_endpoint_rejects_ambiguous_formats(text):
    with pytest.raises((ValueError, TypeError)):
        parse(text)


def test_structured_endpoint_not_explanation_number_search():
    result = parse('{"final":7.76,"explanation":"Denominator 8,000; old estimate 8.0"}')
    assert result["final"] == 7.76


def test_frozen_v4_inputs_and_balanced_jobs():
    from evidence_controls_v4 import verify_protocol
    p = verify_protocol()
    assert len(p["jobs"]) == len({j["id"] for j in p["jobs"]}) == 264
    assert sum(j["stage"] == "primary" for j in p["jobs"]) == 72
    assert sum(j["stage"] == "branch" for j in p["jobs"]) == 192


def test_checkpoint_resume_and_matched_parent(monkeypatch, tmp_path):
    import evidence_controls_v4 as runner
    monkeypatch.setattr(runner, "OUT", tmp_path)
    task = tasks()[0]
    responses = ['{"tool":"aggregate","args":{"op":"count","column":null}}', RuntimeError("transport")]
    received = []
    class FakeClient:
        def __init__(self, *a, **kw): pass
        def complete(self, messages):
            received.append(copy.deepcopy(messages))
            value = responses.pop(0)
            if isinstance(value, Exception): raise value
            return value
    monkeypatch.setattr(runner, "ChatClient", FakeClient)
    job = dict(id="parent",task_id=task["task_id"],stage="primary",policy="base",mode="full",replicate=0)
    assert runner.run_job(job, task).startswith("transport_failed")
    responses.append(json.dumps({"final":task["poisoned_value"]}))
    assert runner.run_job(job, task).startswith("completed")
    assert received[1] == received[2]  # exact completed prefix, not a resampled route
    parent = json.loads((tmp_path / "runs/parent.json").read_text())
    assert parent["llm_requests"] == 2 and parent["poison_adoption"] == 1
    for mode in ["clean", "full"]:
        branch = dict(id="child_"+mode,task_id=task["task_id"],stage="branch",policy="verify",mode=mode,replicate=1,parent="parent")
        responses.append(json.dumps({"final":task["clean_value"]}))
        runner.run_job(branch, task)
        child = json.loads((tmp_path / ("runs/child_"+mode+".json")).read_text())
        assert child["messages"][:len(parent["messages"])] == parent["messages"]
        assert child["parent_sha256"] == runner.sha(tmp_path / "runs/parent.json")
        assert child["tool_events"][0]["was_poisoned"] == (mode == "full")
    assert runner.run_job(job, task).startswith("retained")


def test_bootstrap_averaged_task_unit():
    from analyze_evidence_controls_v4 import paired_interval
    point, low, high = paired_interval({"a":[1,1],"b":[1,1],"c":[1,1]})
    assert (point, low, high) == (1,1,1)
    assert paired_interval({"a":[.5,-.5],"b":[.5,-.5]})[0] == 0


def test_completed_artifact_hashes_and_delivery():
    from evidence_controls_v4 import OUT, sha
    manifest = json.loads((OUT / "completion_manifest.json").read_text())
    assert manifest["n_completed"] == manifest["expected"] == 264
    assert manifest["residual_clean_aliases_in_full"] == 0
    assert manifest["protocol_sha256"] == sha(OUT / "protocol.json")
    assert manifest["analysis_script_sha256"] == sha(BENCH / "analyze_evidence_controls_v4.py")
    for name,digest in manifest["run_sha256"].items():
        assert sha(OUT / "runs" / (name + ".json")) == digest
