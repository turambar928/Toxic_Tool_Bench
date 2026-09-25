"""Build a narrowly allowlisted anonymous, offline supplementary artifact.

Run from the repository root. Never modifies source data or existing releases.
The builder itself is not distributed (it depends on private local provenance).
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / 'toxictool_bench'
RESOURCES = Path(__file__).resolve().parent
MANIFESTS = [('paper_run_manifest.csv', 'source'),
             ('leakage_free_defense_manifest.csv', 'path'),
             ('verification_stress_manifest.csv', 'path')]
MODULES = ['analyze_revision_v2', 'audit_poison_validity_v3',
           'analyze_evidence_controls_v4', 'submission_revision_v3',
           'rebuild_paper_results', 'run_task_acceptance', 'full_adapters']
TESTS = ['test_answer_selection.py', 'test_evaluator.py', 'test_poisoners.py',
         'test_tools.py', 'test_task_acceptance.py', 'test_evidence_controls_v4.py']
SECRET = re.compile(r'(?:sk-[A-Za-z0-9_-]{20,}|Bearer\s+[A-Za-z0-9._-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)', re.I)
IDENTITY = re.compile(r'taozifu\w*|turambar\w*|Toxic_Tool_Bench', re.I)
HOME = re.compile(r'/(?:home|Users)/[A-Za-z0-9_.-]+')
EMAIL = re.compile(r'[A-Za-z0-9_.+-]{1,80}@[A-Za-z0-9.-]{1,100}\.[A-Za-z]{2,15}')
ENDPOINT = re.compile(r'https?://(?:localhost|127\.[0-9.]+|10\.[0-9.]+|192\.168\.[0-9.]+)(?::\d+)?[^\s"<>]*')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def rows(path):
    with path.open(newline='', encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))


def dumps(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode()


def code_closure():
    seen = set()
    def visit(name):
        path = BENCH / (name + '.py')
        if name in seen or not path.is_file():
            return
        seen.add(name)
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom) and node.module:
                visit(node.module.split('.')[0])
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    visit(alias.name.split('.')[0])
    for name in MODULES:
        visit(name)
    return {BENCH / (n + '.py') for n in seen}


def selected_files():
    paths = code_closure() | {ROOT / 'LICENSE'}
    for sub in ['tasks', 'datasets']:
        paths.update(p for p in (BENCH / sub).rglob('*')
                     if p.is_file() and p.suffix in {'.json', '.jsonl', '.csv', '.md'})
    for name in TESTS:
        paths.add(BENCH / 'tests' / name)
    for name, key in MANIFESTS:
        p = BENCH / 'results' / name
        paths.add(p)
        paths.update(ROOT / r[key] for r in rows(p))
    paths.add(BENCH / 'results/reference_answer_audit.json')
    # Published numerical summaries, not broad historic result-directory copies.
    for pattern in ['cross_model_summary.csv', 'semantic_schema_cross_model_summary.csv',
                    'iclr2027_gpt_expanded_cross_agent_*summary.csv',
                    'langgraph_guarded*summary.csv', 'guard_cost_latency_distribution.csv',
                    'verification_stress_summary.csv']:
        paths.update((BENCH / 'results').glob(pattern))
    for directory in ['output/scorer_revision_v2', 'output/submission_revision_v3',
                      'output/evidence_controls_v4', 'output/task_acceptance_v1']:
        d = ROOT / directory
        paths.update(d.glob('*.csv'))
        for name in ['protocol.json', 'completion_manifest.json', 'summary.json',
                     'tasks.json', 'controlled_tasks.jsonl', 'public_tasks.jsonl',
                     'historical_audit.json', 'analysis_manifest.json']:
            if (d / name).is_file():
                paths.add(d / name)
    # V3 analysis reads completed JSONL trajectories; checkpoints are excluded.
    paths.update((ROOT / 'output/submission_revision_v3/runs').glob('*/*.jsonl'))
    paths.update((ROOT / 'output/evidence_controls_v4/runs').glob('*.json'))
    paths.update((ROOT / 'output/task_acceptance_v1/cases').glob('*.json'))
    for split in ['independent', 'reference_review']:
        paths.update((ROOT / 'output/human_validation_20260920' / split).glob('*.csv'))
    return paths


def human_exports():
    """Export exact binary labels + their linked task/run, excluding personal notes."""
    sys.path.insert(0, str(BENCH))
    from validate_human_returns_v2 import inspect, source_records, BASE
    from analyze_human_holdout import FIELDS, load_cases, METHODS
    out = {}
    for packet, folder, name in [('reviewer_packet', '01_independent_200', 'independent_200'),
                                 ('reference_errata_review', '02_reference_review_40', 'reference_review_40')]:
        ret = BENCH / 'HUMAN_REVIEW_KIT_20260917' / folder
        evidence, a, b, adj, disputed, status = inspect(BASE / packet, ret)
        assert status['human_complete']
        records, _, protocol = source_records(BASE / packet, evidence)
        cases = []
        for e, k, task, run in records:
            sid = e['sample_id']
            label = lambda mapping: {f: mapping[sid][f] for f in FIELDS}
            cases.append(dict(sample_id=sid, pair_id=e['pair_id'], task_id=k['task_id'],
                              suite=task['family'], split=k['split'],
                              method=METHODS[k['adapter']], environment=k['environment'],
                              task=task, run=run, annotator_a=label(a), annotator_b=label(b),
                              adjudication=label(adj) if sid in adj else None,
                              consensus=label(adj if sid in adj else a)))
        out[f'human/{name}.jsonl'] = ''.join(json.dumps(c, ensure_ascii=False)+'\n' for c in cases).encode()
        for role in ['annotator_a', 'annotator_b', 'adjudication']:
            text = io.StringIO(newline='')
            w = csv.DictWriter(text, fieldnames=['sample_id', 'pair_id', *FIELDS], lineterminator='\n')
            w.writeheader()
            for c in cases:
                if c[role] is not None:
                    w.writerow(dict(sample_id=c['sample_id'], pair_id=c['pair_id'], **c[role]))
            out[f'human/{name}/{role}.csv'] = text.getvalue().encode()
        if name == 'independent_200':
            out['human/frozen_protocol.json'] = dumps(protocol)
    # This earlier audit is explicitly development data, not a second test set.
    historical, _ = load_cases()
    exported = []
    cache = {}
    for c in historical:
        p = ROOT / c['source']
        if p not in cache:
            cache[p] = [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
        run, = [r for r in cache[p] if all(r[k] == c[k] for k in ['task_id', 'adapter', 'environment'])]
        exported.append({k:c[k] for k in ['sample_id','pair_id','task_id','split','method','environment','task','ratings']}
                        | {'run':run, 'annotator_a':{f:c['a'][f] for f in FIELDS},
                           'annotator_b':{f:c['b'][f] for f in FIELDS}})
    out['human/historical_development_240.jsonl'] = ''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in exported).encode()
    return out


def sanitize(name, data):
    text = data.decode('utf-8')
    if SECRET.search(text):
        raise ValueError(f'Credential-shaped content in selected file (not displayed): {name}')
    edits = []
    for label, pattern, replacement in [('machine-home', HOME, '/anonymous-home'),
                                        ('local-identity', IDENTITY, 'anonymous-project'),
                                        ('private-endpoint', ENDPOINT, 'https://example.invalid')]:
        text, n = pattern.subn(replacement, text)
        if n:
            edits.append({'kind':label,'occurrences':n})
    # Never silently redact email addresses: require a reviewed allowlist instead.
    if EMAIL.search(text):
        raise ValueError(f'Email-like content requires review (not displayed): {name}')
    if name == 'toxictool_bench/analyze_revision_v2.py':
        old = "source=subprocess.check_output(['git','show',f'{BASE}:toxictool_bench/evaluator.py'],cwd=ROOT,text=True)"
        new = "source=(ROOT/'toxictool_bench/legacy_evaluator.py').read_text()"
        assert old in text
        text = text.replace(old, new)
        edits.append({'kind':'bundled-legacy-scorer-instead-of-git','occurrences':1})
    return text.encode(), edits


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True, help='New destination directory')
    args = p.parse_args()
    base = args.output.resolve()
    if base.exists():
        raise SystemExit('Refusing to overwrite an existing release')
    payload = {}
    for path in sorted(selected_files()):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'Unexpected input: {path.relative_to(ROOT)}')
        payload[path.relative_to(ROOT).as_posix()] = path.read_bytes()
    payload.update(human_exports())
    payload['toxictool_bench/legacy_evaluator.py'] = subprocess.check_output(
        ['git','show','4ae42cdd4de2cc0217f03af3f5caefe305a92249:toxictool_bench/evaluator.py'],cwd=ROOT)
    for name in ['README.md', 'reproduce.py', 'requirements-offline.txt', 'HUMAN_EVALUATION.md']:
        payload[name] = (RESOURCES / name).read_bytes()
    converted, changes = {}, []
    for name, data in sorted(payload.items()):
        clean, edits = sanitize(name, data)
        converted[name] = clean
        if edits:
            changes.append(dict(path=name, changes=edits))
    converted['ANONYMIZATION_REPORT.json'] = dumps({
        'scope':'Allowlisted offline artifact; not a full repository export.',
        'label_policy':'Binary labels preserved. Human free-text notes, names, internal attestations and return archives excluded.',
        'history_policy':'No Git directory. Original per-experiment hash records describe historical inputs; SHA256SUMS describes this anonymized release.',
        'transformations':changes,
        'excluded':'API configuration, credentials, Git metadata, personal correspondence, redundant packets, model caches, checkpoints and manuscript source.',
        'scan':'Credential patterns, home-directory identities, private endpoints, known local identifiers and email-like strings checked; no matched residuals.',
    })
    converted['SHA256SUMS'] = ''.join(f'{digest(v)}  {k}\n' for k,v in sorted(converted.items())).encode()
    base.mkdir(parents=True)
    folder = base / 'ToxicBench_Supplementary'
    for name, data in converted.items():
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    archive = base / 'ToxicBench_Supplementary.zip'
    with zipfile.ZipFile(archive,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(converted.items()):
            entry = zipfile.ZipInfo('ToxicBench_Supplementary/'+name, (2026,9,24,0,0,0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            z.writestr(entry,data,compresslevel=9)
    if archive.stat().st_size >= 100_000_000:
        raise RuntimeError('Archive exceeds 100 MB; do not upload')
    (base / 'ZIP_SHA256.txt').write_text(f'{digest(archive.read_bytes())}  {archive.name}\n')
    print(json.dumps({'archive':str(archive),'files':len(converted),
                      'uncompressed_bytes':sum(map(len,converted.values())),
                      'zip_bytes':archive.stat().st_size,'transformed_files':len(changes)},indent=2))


if __name__ == '__main__':
    main()
