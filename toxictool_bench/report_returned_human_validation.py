"""Archive supplied labels and report frozen-scorer comparisons, without relabelling.

This is an author-reported annotation analysis, not a replacement for the strict
provenance gate in validate_human_returns_v2.analyze. Unconfirmed source details
stay explicit. No model calls, scorer changes, or generated human labels.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import zipfile

from analyze_human_holdout import (
    FIELDS, METRICS, METHODS, agreement_tables, human_metrics,
    method_rates, paired_comparisons, write_csv,
)
from evaluator import evaluate_run
from validate_human_returns_v2 import ROOT, BASE, inspect, source_records, sha

DEFAULT_RETURNS = ROOT / 'toxictool_bench/HUMAN_REVIEW_KIT_20260917'
DEFAULT_NOTES = ROOT / 'docs/HUMAN_ANNOTATION_SOURCE_20260920.json'
DEFAULT_OUTPUT = ROOT / 'output/human_validation_20260920'
PACKETS = {'independent': ('reviewer_packet', '01_independent_200'),
           'reference_review': ('reference_errata_review', '02_reference_review_40')}


def validate_source_notes(path):
    notes = json.loads(path.read_text())
    for field in ('independent_annotation_author_confirmed', 'no_llm_author_confirmed',
                  'binary_labels_unchanged_after_notes_edit'):
        if notes.get(field) is not True:
            raise ValueError(f'Missing author confirmation: {field}')
    ids = []
    for role in ('annotator_a', 'annotator_b'):
        person = notes[role]
        if not person.get('rater_id', '').strip():
            raise ValueError('Missing anonymous rater identifier')
        date.fromisoformat(person['completed_on'])
        ids.append(person['rater_id'])
    if len(set(ids)) != 2:
        raise ValueError('Expected two distinct rater identifiers')
    return notes


def inspect_returned_materials(returns):
    original = ROOT / 'output/HUMAN_REVIEW_KIT_20260917'
    manifest = original / 'immutable_checksums.json'
    checks = json.loads(manifest.read_text())
    changed = []
    for name, digest in checks.items():
        path = returns / name
        if not path.is_file():
            raise ValueError(f'Missing returned evidence: {name}')
        if sha(path) != digest:
            changed.append(name)
    # Preserve/document edited instructions, but never allow changed case evidence.
    if set(changed) - {'README_CN.md', 'README_CN.html'}:
        raise ValueError(f'Returned immutable evidence differs: {changed}')
    return {'n_files_checked': len(checks), 'changed_instruction_files': changed,
            'original_checksum_manifest_sha256': sha(manifest),
            'case_evidence_and_data_unchanged': True}


def analyze_packet(packet, returns):
    evidence, a, b, adj, disputed, status = inspect(packet, returns)
    if not status['human_complete']:
        raise ValueError('Incomplete labels or unresolved rater disagreements')
    records, sources, protocol = source_records(packet, evidence)
    cases, inventory, differences = [], [], []
    for e, k, task, run in records:
        sid = e['sample_id']
        label = adj.get(sid, a[sid])
        if task.get('reference_ineligible') and not label['ambiguous']:
            raise ValueError(f'Ineligible reference must be excluded: {sid}')
        auto = evaluate_run(task, run['final_answer'], run['tool_events'])
        exposed = bool(auto['poison_exposed'])
        human = human_metrics(label)
        predictions = {m: int(bool(auto[key])) for m, key in METRICS.items()}
        case = {'sample_id': sid, 'pair_id': e['pair_id'], 'task_id': k['task_id'],
                'suite': task['family'], 'split': k['split'], 'method': METHODS[k['adapter']],
                'environment': k['environment'], 'exposed': exposed, 'a': a[sid], 'b': b[sid],
                'adjudication_pending': False,
                'ratings': {'auto': predictions, 'annotator_a': human_metrics(a[sid]),
                            'annotator_b': human_metrics(b[sid]), 'consensus': human}}
        cases.append(case)
        row = {key: case[key] for key in ('sample_id', 'pair_id', 'task_id', 'suite', 'split',
                                          'method', 'environment', 'exposed')}
        row.update(ambiguous=label['ambiguous'], reference_ineligible=bool(task.get('reference_ineligible')),
                   source=k['source'], answer_selection=auto.get('answer_selection', ''),
                   **{f'human_{m}': human[m] for m in METRICS},
                   **{f'auto_{m}': predictions[m] for m in METRICS})
        inventory.append(row)
        for metric in METRICS:
            if (metric == 'TSR' or exposed) and human[metric] is not None and predictions[metric] != human[metric]:
                differences.append({**row, 'metric': metric, 'human': human[metric],
                                    'automatic': predictions[metric], 'query': task['user_query'],
                                    'clean_oracle': e['clean_oracle'], 'poisoned_oracle': e['poisoned_oracle'],
                                    'final_answer': run['final_answer']})
    agreement, accuracy = agreement_tables(cases)
    families = []
    for family in sorted({c['suite'] for c in cases}):
        _, rows = agreement_tables([c for c in cases if c['suite'] == family])
        families.extend({'suite': family, **r} for r in rows)
    status.update(n_task_ids=len({c['task_id'] for c in cases}), n_exposed=sum(c['exposed'] for c in cases),
                  n_ambiguous=sum(c['a']['ambiguous'] for c in cases),
                  split_counts=dict(Counter(c['split'] for c in cases)),
                  disputed_label_cells=sum(c['a'][f] != c['b'][f] for c in cases for f in FIELDS),
                  n_scorer_disagreement_trajectories=len({r['sample_id'] for r in differences}),
                  rater_files_byte_identical=(returns / 'annotator_a.csv').read_bytes() == (returns / 'annotator_b.csv').read_bytes(),
                  parser_sha256=protocol['parser_sha256'])
    files = [packet / 'evidence.csv', BASE / 'protocol.json', *sources,
             *[returns / name for name in ('annotator_a.csv', 'annotator_b.csv', 'adjudication.csv')]]
    status['input_sha256'] = {str(p.relative_to(ROOT)): sha(p) for p in files}
    tables = {'annotator_agreement': agreement, 'scorer_comparison': accuracy,
              'scorer_comparison_by_family': families, 'method_rates': method_rates(cases),
              'trajectory_inventory': inventory, 'scorer_disagreements': differences}
    if packet.name == 'reviewer_packet':
        tables['paired_comparisons'] = paired_comparisons(cases)
    return tables, status


def latex_tables(tables):
    accuracy = [r for r in tables['scorer_comparison'] if r['split'] == 'all' and r['rater'] == 'consensus']
    fmt = lambda value: '--' if value is None else f'{value:.3f}'
    lines = [r'% Generated by report_returned_human_validation.py; frozen scorer.',
             r'\begin{tabular}{@{}lrrrrrr@{}}', r'\toprule',
             r'Metric & $n$ & Human $+$ & Precision & Recall & F1 & Agreement \\', r'\midrule']
    for row in accuracy:
        lines.append(' & '.join([row['metric'], str(row['n']), str(row['tp'] + row['fn']),
                                *[fmt(row[k]) for k in ('precision', 'recall', 'f1', 'agreement')]]) + r' \\')
    lines.extend([r'\bottomrule', r'\end{tabular}'])
    metrics = '\n'.join(lines) + '\n'
    rates = {(r['split'], r['method'], r['environment'], r['rater']): r for r in tables['method_rates'] if r['metric'] == 'TSR'}
    lines = [r'% Generated by report_returned_human_validation.py; counts, not rounded ranks.',
             r'\begin{tabular}{@{}llrrrr@{}}', r'\toprule',
             r'& & \multicolumn{2}{c}{Clean} & \multicolumn{2}{c}{Poisoned} \\',
             r'Setting & Method & Auto & Human & Auto & Human \\', r'\midrule']
    for split, method in [('core', m) for m in ['Base', 'Double-pass', 'Verification-only', 'Generic Guard']] + [('repeated_p1', 'Double-pass'), ('repeated_p1', 'Generic Guard'), ('cross_model', 'AutoGen')]:
        cells = []
        for env in ['clean', 'toxic']:
            for rater in ['auto', 'consensus']:
                row = rates.get((split, method, env, rater))
                cells.append('--' if row is None else f"{row['positives']}/{row['n']}")
        setting = {'core': 'Core', 'repeated_p1': r'Repeated, $p=1$', 'cross_model': 'Cross-model'}[split]
        lines.append(' & '.join([setting, method, *cells]) + r' \\')
    lines.extend([r'\bottomrule', r'\end{tabular}'])
    return metrics, '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--returns', type=Path, default=DEFAULT_RETURNS)
    parser.add_argument('--source-notes', type=Path, default=DEFAULT_NOTES)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    returns, output = args.returns.resolve(), args.output.resolve()
    if output.exists():
        raise ValueError('Choose a new output directory; never overwrite archived results')
    notes = validate_source_notes(args.source_notes)
    evidence_audit = inspect_returned_materials(returns)
    results = {kind: analyze_packet(BASE / canonical, returns / folder)
               for kind, (canonical, folder) in PACKETS.items()}
    # Validate both packets before creating the report. No files in either
    # returned or original packet are written by this program.
    output.mkdir(parents=True)
    for kind, (tables, status) in results.items():
        directory = output / kind
        directory.mkdir()
        for name, rows in tables.items():
            write_csv(directory / (name + '.csv'), rows,
                      fields=None if rows else ['sample_id', 'metric', 'human', 'automatic'])
        (directory / 'status.json').write_text(json.dumps(status, indent=2) + '\n')
    metrics, comparisons = latex_tables(results['independent'][0])
    (output / 'scorer_metrics.tex').write_text(metrics)
    (output / 'method_comparison.tex').write_text(comparisons)
    archived = [returns / name for name in ('README_CN.md', 'README_CN.html', 'release_manifest.json', 'immutable_checksums.json')]
    for _, folder in PACKETS.values():
        archived.extend(returns / folder / name for name in ('annotator_a.csv', 'annotator_b.csv', 'adjudication.csv', 'provenance_TEMPLATE.json'))
    with zipfile.ZipFile(output / 'returned_materials.zip', 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in archived:
            archive.write(path, str(path.relative_to(returns)))
        archive.write(args.source_notes, 'author_source_notes.json')
    manifest = {'report_type': 'frozen_scorer_author_reported_human_annotation',
                'source_notes': notes, 'source_notes_sha256': sha(args.source_notes),
                'source_independence_evidence': 'author confirmation; not independently established by identical files',
                'blinding_attested': notes.get('blind_to_automatic_labels') is True,
                'strict_blinded_validation_provenance_complete': False,
                'packet_masking': 'Distributed kit excludes automatic predictions and administrator mappings.',
                'evidence_integrity': evidence_audit,
                'no_labels_generated_or_changed': True,
                'scorer_frozen': True,
                'comparison_bootstrap': {'draws': 5000, 'seed': 20260915, 'unit': 'paired task within suite'},
                'script_sha256': {str(p.relative_to(ROOT)): sha(p) for p in
                    [Path(__file__).resolve(), ROOT / 'toxictool_bench/analyze_human_holdout.py',
                     ROOT / 'toxictool_bench/validate_human_returns_v2.py']},
                'returned_files_sha256': {str(p.relative_to(returns)): sha(p) for p in archived},
                'output_sha256': {str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*')) if p.is_file()}}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({kind: {k: status[k] for k in ('expected', 'annotator_a', 'annotator_b', 'disputed', 'n_exposed', 'n_ambiguous')}
                      for kind, (_, status) in results.items()}, indent=2))


if __name__ == '__main__':
    main()
