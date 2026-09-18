import csv
import hashlib
import io
import json
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_human_review_kit import build, SOURCES, PACKETS, FIELDS, cases_page


@pytest.fixture(scope="module")
def kit(tmp_path_factory):
    folder = tmp_path_factory.mktemp("human-kit-test")/"kit"
    build(folder)
    return folder


def test_canonical_evidence_templates_and_data_are_unchanged(kit):
    for source,folder,_,count in PACKETS:
        with zipfile.ZipFile(SOURCES/(source+".zip")) as z:
            for name in ["evidence.csv","annotator_a.csv","annotator_b.csv","adjudication.csv"]:
                assert (kit/folder/name).read_bytes()==z.read(name)
        with (kit/folder/"evidence.csv").open() as f:
            rows=list(csv.DictReader(f))
        assert len(rows)==count
        for row in rows:
            expected=json.loads(row["reference_context_json"])["data_csv"].encode()
            assert (kit/folder/"data"/(row["sample_id"]+".csv")).read_bytes()==expected
        for name in ["annotator_a.csv","annotator_b.csv","adjudication.csv"]:
            with (kit/folder/name).open() as f:
                labels=list(csv.DictReader(f))
            assert not any(r[field] for r in labels for field in (*FIELDS,"notes"))


def test_role_neutral_offline_html_and_all_links_exist(kit):
    class Links(HTMLParser):
        def __init__(self):super().__init__();self.links=[]
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if tag in {"a","script","link"}:
                for key in ["href","src"]:
                    if key in attrs:self.links.append(attrs[key])
    for path in kit.rglob("*.html"):
        text=path.read_text()
        parser=Links();parser.feed(text)
        for link in parser.links:
            u=urlsplit(link)
            assert not u.scheme,link
            if u.path:assert (path.parent/unquote(u.path)).is_file(),(path,link)
        if path.name=="cases.html":
            # Historical tool observations may mention old filenames. Preserve
            # those evidence bytes; only the new UI instructions must be fixed.
            header=text.split('<article id=',1)[0]
            assert "ToxicBench · 第三位人工裁决" not in header
            assert "adjudication_to_fill.csv" not in header
            assert "本页只供阅读，不保存标签" in text


def test_manifests_zip_and_unsigned_provenance(kit):
    checks=json.loads((kit/"immutable_checksums.json").read_text())
    for name,digest in checks.items():
        assert hashlib.sha256((kit/name).read_bytes()).hexdigest()==digest
        assert not name.endswith(("annotator_a.csv","annotator_b.csv","adjudication.csv"))
    files={p.relative_to(kit).as_posix() for p in kit.rglob("*") if p.is_file()}
    assert not any("admin" in f or f.endswith(".py") for f in files)
    for _,folder,_,_ in PACKETS:
        p=json.loads((kit/folder/"provenance_TEMPLATE.json").read_text())
        assert p["independent_human_annotation"] is None
        assert all(p[r]["completed_at"]=="" for r in ["annotator_a","annotator_b","adjudicator"])
    with zipfile.ZipFile(kit.with_suffix(".zip")) as z:
        assert z.testzip() is None
        assert {n.split("/",1)[1] for n in z.namelist()}==files


def test_existing_materials_are_never_overwritten(kit):
    with pytest.raises(ValueError,match="overwrite"):
        build(kit)


def test_case_content_is_html_escaped():
    row={"sample_id":"VAL2-999","pair_id":"TEST","user_query":"<script>bad()</script>",
         "final_answer":"<img src=x onerror=bad()>","clean_oracle":"A","poisoned_oracle":"B",
         "reference_context_json":json.dumps({"data_csv":"a\n<script>\n","oracle":{}}),
         "tool_events_json":json.dumps([{"tool_name":"<svg>","returned_observation":"<script>bad()</script>"}])}
    text=cases_page([row],"TEST")
    assert "<script>bad()" not in text and "<img src=x" not in text
    assert "&lt;script&gt;bad()&lt;/script&gt;" in text
