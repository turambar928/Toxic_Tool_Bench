"""Synthetic temporary fixtures only; never writes labels into real packets."""
import json
import csv
import io
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze_human_holdout import FIELDS, write_csv
from validate_human_returns_v2 import inspect, validate_provenance, BASE


def toy_packet(tmp_path):
    p = tmp_path / "toy"
    p.mkdir()
    evidence = [{"sample_id":"TEST-ONLY", "pair_id":"TOY"}]
    write_csv(p/"evidence.csv", evidence)
    for name in ["cases.html","README_CN.md","checksums.json"]:
        (p/name).write_text("synthetic fixture")
    with zipfile.ZipFile(p.with_suffix(".zip"),"w") as z:
        for f in p.iterdir(): z.write(f,f.name)
    row = {**evidence[0], **dict.fromkeys(FIELDS,""), "notes":""}
    for name in ["annotator_a.csv","annotator_b.csv","adjudication.csv"]:
        write_csv(p/name,[row])
    return p, row


def test_blank_is_pending_and_real_packets_are_intact(tmp_path):
    p, row = toy_packet(tmp_path)
    assert inspect(p,p)[-1]["human_complete"] is False
    for name,expected in [("reviewer_packet",200),("reference_errata_review",40)]:
        with zipfile.ZipFile((BASE/name).with_suffix(".zip")) as z:
            rows = list(csv.DictReader(io.StringIO(z.read("evidence.csv").decode())))
            assert len(rows) == expected


def test_disagreement_needs_complete_adjudication(tmp_path):
    p, row = toy_packet(tmp_path)
    a = {**row, **dict.fromkeys(FIELDS,"0")}
    b = {**a, "final_correct":"1"}
    write_csv(p/"annotator_a.csv",[a]); write_csv(p/"annotator_b.csv",[b])
    assert inspect(p,p)[-1]["pending_disputes"] == ["TEST-ONLY"]
    write_csv(p/"adjudication.csv",[{**b,"notes":"synthetic test decision"}])
    assert inspect(p,p)[-1]["human_complete"]


def test_changed_evidence_and_partial_labels_fail(tmp_path):
    p,row = toy_packet(tmp_path)
    write_csv(p/"annotator_a.csv",[{**row,"final_correct":"1"}])
    with pytest.raises(ValueError,match="Incomplete"):
        inspect(p,p)
    (p/"evidence.csv").write_text("changed")
    with pytest.raises(ValueError,match="Frozen evidence"):
        inspect(p,p)


def test_provenance_requires_distinct_raters_and_attestation(tmp_path):
    path = tmp_path/"declaration.json"
    person = dict(rater_id="SYNTHETIC-A",completed_at="2026-09-16T12:00:00Z",reference_review_complete=True)
    data = dict(independent_human_annotation=True,no_model_generated_labels=True,
                blind_to_automatic_labels=True,annotator_a=person,annotator_b=person)
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError,match="distinct"):
        validate_provenance(path,False)
    data["annotator_b"] = {**person,"rater_id":"SYNTHETIC-B"}
    path.write_text(json.dumps(data))
    assert validate_provenance(path,False)
    data["no_model_generated_labels"] = False
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError,match="attestation"):
        validate_provenance(path,False)
