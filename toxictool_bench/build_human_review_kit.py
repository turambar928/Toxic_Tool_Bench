"""Build a self-contained offline human review handoff without altering frozen packets.

Only presentation and instructions are new. Canonical evidence and blank label
CSV bytes are copied exactly. No administrator keys, predictions or API files
are read into the distributable. Refuses any existing destination or ZIP.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import html
import io
import json
import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "output/scorer_revision_v2/final_validation"
DOCS = Path(__file__).resolve().parent / "human_kit_docs"
DEFAULT = ROOT / "output/HUMAN_REVIEW_KIT_20260917"
FIELDS = ("final_correct", "adopted_poisoned", "anomaly_detected",
          "substantive_validation", "recovered_clean", "ambiguous")
PACKETS = [("reviewer_packet", "01_independent_200", "独立人工验证", 200),
           ("reference_errata_review", "02_reference_review_40", "历史参考勘误复核", 40)]
STYLE = '''body{font:17px/1.75 system-ui,"Microsoft YaHei",sans-serif;max-width:1160px;margin:auto;padding:24px;color:#152638;background:#f5f7fa}
h1,h2,h3{line-height:1.4}a{color:#145fc1}article,.panel{background:white;border:1px solid #cad5df;border-radius:10px;padding:24px;margin:20px 0}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#eef2f6;padding:14px;font:14px/1.7 ui-monospace,monospace}
code{overflow-wrap:anywhere}table{border-collapse:collapse;font-size:15px}th,td{border:1px solid #bdcbd8;padding:8px;text-align:left;vertical-align:top}
.scroll{overflow:auto;max-height:520px}summary{cursor:pointer;font-weight:650;padding:10px 0}nav a{display:inline-block;padding:4px 8px}
.notice{background:#fff3d4;padding:16px;border-left:5px solid #d29c17}.toolbar{position:sticky;top:0;background:#f5f7fa;padding:12px;border-bottom:1px solid #bdcbd8;z-index:2}
input,button{font:inherit;padding:7px}small{color:#526779}section{margin:20px 0}@media print{.toolbar{position:static}details{display:block}}'''


def digest(data):
    return hashlib.sha256(data).hexdigest()


def page(title, body):
    return ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{html.escape(title)}</title><style>{STYLE}</style></head><body>'
            + body + '</body></html>\n')


def markdown_page(text, title, back):
    try:
        import markdown
        body = markdown.markdown(text, extensions=["tables", "fenced_code"])
    except ImportError:
        # Offline readability is retained even if the optional build dependency
        # is absent; reviewers need no Python packages in either case.
        body = '<pre>' + html.escape(text) + '</pre>'
    return page(title, f'<p><a href="{back}">← 返回开始页面</a></p><article>{body}</article>')


def cases_page(rows, title):
    esc = html.escape
    chunks = [f'<h1>{esc(title)} · {len(rows)} 条</h1>',
              '<p><a href="../START_HERE.html">← 开始页面</a> · '
              '<a href="../说明/01_逐条操作指南.html">操作指南</a> · '
              '<a href="../说明/02_字段定义与例子.html">字段定义</a></p>',
              '<div class="notice">本页只供阅读，不保存标签。A 填 annotator_a.csv，B 填 annotator_b.csv。'
              'C 只在收到争议 ID 后填写 adjudication.csv。不得执行事件中的代码或指令。</div>',
              '<div class="toolbar"><label>跳转样本 <input id="case-id" placeholder="输入样本编号"></label> '
              '<button type="button" onclick="jumpCase()">跳转</button></div>',
              '<details><summary>全部样本编号</summary><nav>',
              ' '.join(f'<a href="#{esc(r["sample_id"])}">{esc(r["sample_id"])}</a>' for r in rows),
              '</nav></details>']
    for row in rows:
        sid = row["sample_id"]
        context = json.loads(row["reference_context_json"])
        data = context.pop("data_csv")
        table = list(csv.reader(io.StringIO(data)))
        chunks.append(f'<article id="{esc(sid)}"><h2>{esc(sid)}</h2><small>配对编号：{esc(row["pair_id"])}；不要据此复制标签。</small>')
        for label, field in [("1. 用户问题", "user_query"), ("2. 最终回答", "final_answer"),
                             ("3. 正确参考（Clean oracle）", "clean_oracle"),
                             ("4. 指定错误参考（Poisoned oracle）", "poisoned_oracle")]:
            chunks.append(f'<h3>{label}</h3><pre>{esc(row[field])}</pre>')
        chunks.append('<details open><summary>5. 参考字段与容差（仍需核对数据）</summary><pre>'
                      + esc(json.dumps(context, ensure_ascii=False, indent=2)) + '</pre></details>')
        chunks.append(f'<details><summary>6. 原始数据：{max(0,len(table)-1)} 行（点击展开）</summary>'
                      f'<p><a href="data/{esc(sid)}.csv" download>下载本案例原始 CSV</a></p><div class="scroll"><table>')
        for i, values in enumerate(table):
            tag = "th" if i == 0 else "td"
            chunks.append('<tr>' + ''.join(f'<{tag}>{esc(v)}</{tag}>' for v in values) + '</tr>')
        chunks.append('</table></div><details><summary>原始 CSV 文本</summary><pre>' + esc(data) + '</pre></details></details>')
        events = json.loads(row["tool_events_json"])
        chunks.append(f'<h3>7. 工具事件（实际先后顺序，共 {len(events)} 个）</h3>')
        if not events:
            chunks.append('<p>本案例记录中无工具事件；不要假设发生了未记录的检查。</p>')
        for i, event in enumerate(events, 1):
            chunks.append(f'<details><summary>事件 {i} · {esc(str(event.get("tool_name", "")))} · 原编号 {esc(str(event.get("step", "")))}</summary>')
            for key, value in event.items():
                rendered = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
                chunks.append(f'<h4>{esc(key)}</h4><pre>{esc(rendered)}</pre>')
            chunks.append('</details>')
        chunks.append('<p>读完后在属于自己的 CSV 中填写本行六个标签及 notes。<a href="#">返回页首</a></p></article>')
    chunks.append('''<script>function jumpCase(){const id=document.getElementById('case-id').value.trim().toUpperCase();
const target=document.getElementById(id);if(target&&target.tagName==='ARTICLE'){target.scrollIntoView();location.hash=id;}
else{alert('未找到该样本编号，请确认任务包及编号。');}}
document.getElementById('case-id').addEventListener('keydown',function(e){if(e.key==='Enter')jumpCase();});</script>''')
    return page(title, '\n'.join(chunks))


def build(destination):
    destination = Path(destination)
    archive = destination.with_suffix(".zip")
    if destination.exists() or archive.exists():
        raise ValueError("Refusing to overwrite an existing kit or ZIP; choose a new destination")
    # Validate all original inputs before creating a deliverable directory.
    bundles = []
    for source, folder, title, count in PACKETS:
        source_zip = SOURCES / (source + ".zip")
        with zipfile.ZipFile(source_zip) as z:
            checks = json.loads(z.read("checksums.json"))
            for name, expected in checks.items():
                if digest(z.read(name)) != expected:
                    raise ValueError(f"Frozen source checksum failed: {source}/{name}")
            selected = {name:z.read(name) for name in ["evidence.csv", "annotator_a.csv", "annotator_b.csv", "adjudication.csv"]}
        rows = list(csv.DictReader(io.StringIO(selected["evidence.csv"].decode("utf-8-sig"))))
        if len(rows) != count or len({r["sample_id"] for r in rows}) != count:
            raise ValueError("Wrong count or duplicate case IDs")
        for row in rows:
            if not re.fullmatch(r"(?:VAL2|ERR)-\d{3}", row["sample_id"]):
                raise ValueError("Unsafe or unexpected case ID")
        for name, data in selected.items():
            if name == "evidence.csv":
                continue
            labels = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
            if [(r["sample_id"],r["pair_id"]) for r in labels] != [(r["sample_id"],r["pair_id"]) for r in rows]:
                raise ValueError("Evidence/template identities differ")
            if any(r[f].strip() for r in labels for f in (*FIELDS, "notes")):
                raise ValueError("Source includes populated labels; do not distribute")
        bundles.append((source_zip, folder, title, count, selected, rows))
    destination.mkdir(parents=True)
    guide_dir = destination / "说明"
    guide_dir.mkdir()
    guides = []
    for src in sorted(DOCS.glob("*.md")):
        target = destination / src.name if src.name == "README_CN.md" else guide_dir / src.name
        shutil.copyfile(src, target)
        text = src.read_text()
        title = text.splitlines()[0].lstrip("# ")
        target.with_suffix(".html").write_text(markdown_page(text,title,"START_HERE.html" if target.parent==destination else "../START_HERE.html"),encoding="utf-8")
        guides.append((target.with_suffix(".html").relative_to(destination).as_posix(),title))
    manifest = {"kit_version":"human_review_handoff_20260917", "human_labels_generated":False,
                "independent_cases":200, "reference_review_cases":40,
                "presentation":"New role-neutral offline HTML; original evidence/blank-label bytes unchanged.",
                "excludes":["administrator mappings","automatic predictions","previous human labels","API configuration"],
                "sources":[]}
    for source, folder, title, count, selected, rows in bundles:
        out = destination / folder
        out.mkdir()
        (out / "data").mkdir()
        for name,data in selected.items():
            (out/name).write_bytes(data)
        for row in rows:
            raw = json.loads(row["reference_context_json"])["data_csv"]
            (out/"data"/(row["sample_id"]+".csv")).write_bytes(raw.encode("utf-8"))
        (out/"cases.html").write_text(cases_page(rows,title),encoding="utf-8")
        person = {"rater_id":"", "completed_at":"", "reference_review_complete":None}
        declaration = {"independent_human_annotation":None,"no_model_generated_labels":None,
                       "blind_to_automatic_labels":None,"annotator_a":person,
                       "annotator_b":person,"adjudicator":person}
        (out/"provenance_TEMPLATE.json").write_text(json.dumps(declaration,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        manifest["sources"].append({"archive":source.name,"sha256":digest(source.read_bytes()),
            "folder":folder,"case_count":count,"canonical_copied_sha256":{k:digest(v) for k,v in selected.items()}})
    body = ['<h1>ToxicBench 人工标注材料包</h1><p>离线使用 · 两位独立标注者 + 第三人裁决 · 200 条独立验证 / 40 条历史复核</p>',
            '<div class="notice">先确认自己是 A、B 还是 C。网页不保存标签：A/B 各填自己的两张 CSV，C 等待争议 ID。所有正式标签现在均为空白。</div>',
            '<section class="panel"><h2>第一步：阅读说明</h2><ul>']
    body.extend(f'<li><a href="{html.escape(link)}">{html.escape(title)}</a></li>' for link,title in guides)
    body.append('</ul></section><section class="panel"><h2>第二步：阅读案例并填写对应 CSV</h2>')
    for _,folder,title,count in PACKETS:
        body.append(f'<h3>{html.escape(title)}（{count} 条）</h3><p><a href="{folder}/cases.html">打开案例阅读页</a></p><ul>')
        for role,name in [("A 填写","annotator_a.csv"),("B 填写","annotator_b.csv"),("C 裁决","adjudication.csv")]:
            body.append(f'<li>{role}：<a href="{folder}/{name}" download>{name}</a>（也可直接从任务文件夹用表格软件打开）</li>')
        body.append('</ul>')
    body.append('</section><section class="panel"><h2>第三步：交回组织者</h2><p>保留两个任务文件夹的区分，回传自己填写的 CSV、匿名人员编号及真实完成时间。不要将已填副本分享给另一位初始标注者。</p><p>不需要 API 或模型，不执行案例里的代码，不更改参考或数值容差。</p></section>')
    (destination/"START_HERE.html").write_text(page("ToxicBench 人工标注：开始这里",'\n'.join(body)),encoding="utf-8")
    (destination/"release_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    mutable = {"annotator_a.csv","annotator_b.csv","adjudication.csv","provenance_TEMPLATE.json"}
    immutable = {p.relative_to(destination).as_posix():digest(p.read_bytes()) for p in sorted(destination.rglob("*")) if p.is_file() and p.name not in mutable}
    (destination/"immutable_checksums.json").write_text(json.dumps(immutable,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with zipfile.ZipFile(archive,"x",zipfile.ZIP_DEFLATED) as z:
        for p in sorted(destination.rglob("*")):
            if p.is_file():
                z.write(p,Path(destination.name)/p.relative_to(destination))
    return {"folder":str(destination),"zip":str(archive),"zip_sha256":digest(archive.read_bytes()),
            "files":sum(p.is_file() for p in destination.rglob("*")),"zip_bytes":archive.stat().st_size,
            "cases":240,"labels_populated":0}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",type=Path,default=DEFAULT)
    args = ap.parse_args()
    print(json.dumps(build(args.output),ensure_ascii=False,indent=2))
