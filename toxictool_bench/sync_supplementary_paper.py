#!/usr/bin/env python3
"""Synchronize the AutoGen and repeated-poison evidence with the frozen scorer."""
import json
from pathlib import Path

from build_defense_paired_analysis import read_csv, read_jsonl
from rebuild_paper_results import rescore, write_guard_summary, write_combined_guard
from summarize_verification_stress import rescore_rows
from bootstrap_ci import summarize
from sync_defense_paper import ROOT, RESULTS, SECTIONS, NAMES, table_rows, line, f, sha


def main():
    specs = read_csv(RESULTS / 'paper_run_manifest.csv')
    auto = [(s, rescore(s)) for s in specs if s['experiment'] == 'autogen_guard']
    suite_path = RESULTS / 'autogen_guarded_replication_suite_summary.csv'
    write_guard_summary(auto, suite_path)
    write_combined_guard(suite_path, RESULTS / 'autogen_guarded_replication_summary.csv')
    alternatives = [(s, rescore(s)) for s in specs if s['experiment'] == 'alternative_baseline']
    alternative_path = RESULTS / 'iclr2027_stronger_baselines_strict_summary.csv'
    write_guard_summary(alternatives, alternative_path)
    table_rows(SECTIONS / '08_appendix_guard_details.tex', 'tab:appendix-stronger-baselines', [
        line('Numerical-20' if r['suite']=='numerical' else 'Semantic-10', r['adapter'],
             *[f(r[k]) for k in ('clean_tsr','poisoned_tsr','bcr','vr','rr','poison_delivery_rate')])
        for r in read_csv(alternative_path)])
    manifest = RESULTS / 'verification_stress_manifest.csv'
    summary_path = RESULTS / 'verification_stress_summary.csv'
    groups = {}
    for spec in read_csv(manifest):
        key = (spec['suite'], float(spec['poison_probability']), spec['adapter'])
        groups.setdefault(key, []).extend(read_jsonl(ROOT / spec['path']))
    summaries = read_csv(summary_path)
    for spec in summaries:
        key = (spec['suite'], float(spec['poison_probability']), spec['adapter'])
        point = summarize(rescore_rows(spec['suite'], groups[key]))
        for col, metric in {'toxic_tsr':'toxic_tsr','bcr':'toxic_bcr','par':'toxic_par','vpa':'toxic_vpa','vr':'toxic_vr','rr':'toxic_rr'}.items():
            if f(point[metric],4) != spec[col]:
                raise ValueError('Stale stress summary; run summarize_verification_stress.py first')
    titles = {'numerical_iclr2027':'Numerical','semantic_schema_iclr2027':'Semantic/schema','realistic_extension_iclr2027':'Multi-table'}
    table_rows(SECTIONS / '08_appendix_guard_details.tex','tab:appendix-multiroute-stress',[
        line(titles[s],NAMES[a],*[f(r[k]) for k in ('toxic_tsr','bcr','par','vpa','vr','rr','poison_delivery_rate')])
        for s in titles for a in NAMES if a != 'langgraph_react_full'
        for r in summaries if r['suite']==s and r['adapter']==a and float(r['poison_probability'])==1])
    sources = {manifest,summary_path,Path(__file__),ROOT/'toxictool_bench/evaluator.py',ROOT/'toxictool_bench/summarize_verification_stress.py'}
    sources.update(ROOT / 'toxictool_bench' / name for name in (
        'answer_selection.py', 'audit_reference_answers.py', 'results/reference_answer_audit.json'))
    sources.update(ROOT/s['path'] for s in read_csv(manifest))
    sources.update(ROOT/s['source'] for s,_ in auto)
    sources.update(ROOT/s['source'] for s,_ in alternatives)
    sources.update(ROOT/p for s,_ in auto+alternatives for p in s['tasks'].split(';'))
    sources.update(ROOT/f'toxictool_bench/tasks/{s}.jsonl' for s in titles)
    (RESULTS/'supplementary_analysis_provenance.json').write_text(json.dumps({
        'n_stress_trajectories':sum(len(g) for g in groups.values()),
        'sha256':{str(p.relative_to(ROOT)):sha(p) for p in sorted(sources)}},indent=2)+'\n')
    print('Synchronized repeated-poison and AutoGen summaries with explicit reference exclusions.')


if __name__ == '__main__':
    main()
