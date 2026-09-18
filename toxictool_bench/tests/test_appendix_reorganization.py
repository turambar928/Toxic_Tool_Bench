"""The compact appendix preserves data and remains regenerable offline."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from check_paper_static import collect_tex_files
from sync_defense_paper import (
    ROOT, RESULTS, SUITES, read_csv, suite_table_lines, audit_table_lines,
    table_rows,
)


def test_appendix_has_five_sections_and_no_paragraph_headings():
    active = collect_tex_files(ROOT / 'main.tex', ROOT)
    sources = [p for p in active if p.parent.name == 'sections'
               and p.name[:2] in {'08', '09', '10', '11'}]
    assert len(sources) == 4
    text = '\n'.join(p.read_text() for p in sources)
    assert len(re.findall(r'\\section\{', text)) == 5
    assert len(re.findall(r'\\subsection\{', text)) == 6
    assert r'\paragraph{' not in text
    assert not any('appendix_archive' in str(p) for p in active)


def test_combined_suite_table_matches_frozen_results():
    summaries = {s: {r['adapter']: r for r in read_csv(
        RESULTS / f'leakage_free_defense_{s}_summary.csv')} for s in SUITES}
    exposure = read_csv(RESULTS / 'leakage_free_defense_exposure_denominators.csv')
    lines = suite_table_lines(summaries, exposure)
    assert len(lines) == 8
    paper = (ROOT / 'sections/08_appendix_guard_details.tex').read_text()
    assert all(row in paper for row in lines)
    assert all(len(row.split(' & ')) == 9 for row in lines)


def test_combined_development_audit_matches_independent_sources():
    consensus = json.loads((RESULTS / 'scorer_consensus_validation.json').read_text())['metrics']
    agreement = json.loads((ROOT / 'toxictool_bench/human_audit_v2/agreement.json').read_text())['labels']
    lines = audit_table_lines(consensus, agreement)
    assert len(lines) == 4
    paper = (ROOT / 'sections/09_revision_validation.tex').read_text()
    assert all(row in paper for row in lines)
    assert all(len(row.split(' & ')) == 7 for row in lines)


def test_table_sync_preserves_merged_label_aliases(tmp_path):
    source = ROOT / 'sections/08_appendix_guard_details.tex'
    copy = tmp_path / source.name
    original = source.read_text()
    copy.write_text(original)
    label = 'tab:appendix-guard-suite-breakdown'
    table_rows(copy, label, [r'Sentinel & values \\'])
    modified = copy.read_text()
    assert modified.count(r'\label{' + label + '}') == 1
    assert modified.count(r'\label{tab:appendix-defense-exposure}') == 1
    assert r'Sentinel & values \\' in modified
    assert source.read_text() == original


def test_moved_numeric_tables_preserve_archived_rows():
    archive = ROOT / 'docs/appendix_archive_20260918'
    old = (archive / '08_appendix_guard_details.tex').read_text()
    active = '\n'.join((ROOT / 'sections' / name).read_text() for name in
                       ('08_appendix_guard_details.tex', '09_revision_validation.tex'))
    for label in ('tab:appendix-scorer-revision-impact', 'tab:appendix-paired-defense-ci',
                  'tab:appendix-latency-distribution', 'tab:appendix-multiroute-stress'):
        pos = old.index(r'\label{' + label + '}')
        start = old.rindex(r'\begin{table}', 0, pos)
        body = old[old.index(r'\midrule', start):old.index(r'\bottomrule', start)]
        assert body in active
