"""Checks independent of model outcomes; the frozen answer parser is untouched."""
import csv
import hashlib
import json
import statistics
import sys
from pathlib import Path

import pytest

BENCH = Path(__file__).resolve().parents[1]
ROOT = BENCH.parent
sys.path.insert(0, str(BENCH))
from audit_poison_validity_v3 import flags


def test_audit_flags_zero_index_and_does_not_certify_other_events():
    task = {"oracle": {"clean_value":70}}
    event = {"was_poisoned":True,"poison_type":"sign_flip",
             "clean_observation":"0 100\n1 170", "returned_observation":"-0.0 100\n1 170"}
    assert set(flags(event,task)) == {"off_target_sign_flip", "no_value_or_text_change"}
    event.update(clean_observation="Growth:70",returned_observation="Growth:-70.0")
    assert flags(event,task) == []


def test_audit_flags_error_output():
    event={"was_poisoned":True,"poison_type":"sign_flip",
           "clean_observation":"ERROR: row 4 missing", "returned_observation":"ERROR: row -4.0 missing"}
    assert "error_observation" in flags(event,{"oracle":{"clean_value":70}})


def test_protocol_hashes_and_fixed_membership():
    p=json.loads((ROOT / "output/submission_revision_v3/protocol.json").read_text())
    for file,digest in p["input_sha256"].items():
        assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest() == digest, file
    assert len(p["jobs"]) == 130
    assert len({j["id"] for j in p["jobs"]}) == 130
    assert sum(2 if j["environment"]=="both" else 1 for j in p["jobs"]) == 152


def test_public_references_with_standard_library():
    with (BENCH / "datasets/public_penguins_v3.csv").open() as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==344
    def mean(column, keep=lambda r:True):
        return statistics.mean(float(r[column]) for r in rows if keep(r) and r[column] != "NA")
    expected={
        "mass": mean("body_mass_g"),
        "adelie_mass": mean("body_mass_g",lambda r:r["species"]=="Adelie"),
        "gentoo_count":sum(r["species"]=="Gentoo" for r in rows),
        "male_bill":mean("bill_length_mm",lambda r:r["sex"]=="male"),
        "biscoe_flipper":mean("flipper_length_mm",lambda r:r["island"]=="Biscoe"),
        "mass_kg":mean("body_mass_g")/1000,
    }
    tasks=[json.loads(l) for l in (ROOT / "output/submission_revision_v3/public_tasks.jsonl").read_text().splitlines()]
    for t in tasks:
        key=t["task_id"].removeprefix("public_penguins_").removesuffix("_v3")
        assert t["oracle"]["clean_value"] == pytest.approx(expected[key],abs=1e-10)
