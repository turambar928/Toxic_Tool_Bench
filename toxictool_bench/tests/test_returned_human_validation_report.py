"""Frozen report regression checks; never writes or repairs human labels."""
import csv
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from report_returned_human_validation import ROOT, DEFAULT_OUTPUT, DEFAULT_NOTES, latex_tables, validate_source_notes
from validate_human_returns_v2 import validate_provenance


def rows(name, kind='independent'):
    with (DEFAULT_OUTPUT / kind / (name + '.csv')).open(newline='') as f:
        return list(csv.DictReader(f))


def test_frozen_scorer_confusion_counts_and_denominators():
    expected = {'TSR': (200, 176, 0, 8, 16), 'PAR': (77, 12, 0, 2, 63),
                'BCR': (77, 8, 0, 2, 67), 'ADR': (77, 0, 0, 1, 76),
                'VR': (77, 61, 0, 3, 13), 'VPA': (77, 4, 0, 0, 73),
                'RR': (77, 52, 0, 8, 17)}
    actual = {r['metric']: r for r in rows('scorer_comparison')
              if r['split'] == 'all' and r['rater'] == 'consensus'}
    for metric, counts in expected.items():
        assert tuple(int(actual[metric][k]) for k in ('n', 'tp', 'fp', 'fn', 'tn')) == counts
    assert actual['ADR']['precision'] == ''
    assert float(actual['TSR']['agreement']) == .96


def test_human_method_comparison_keeps_verification_tie():
    rates = {(r['method'], r['rater']): r for r in rows('method_rates')
             if r['split'] == 'core' and r['environment'] == 'toxic' and r['metric'] == 'TSR'}
    assert int(rates['Verification-only', 'auto']['positives']) == 16
    assert int(rates['Verification-only', 'consensus']['positives']) == 20
    assert int(rates['Double-pass', 'consensus']['positives']) == 20
    paired = [r for r in rows('paired_comparisons') if r['split'] == 'core'
              and r['metric'] == 'TSR' and r['rater'] == 'consensus']
    dp = next(r for r in paired if r['control'] == 'Base')
    assert tuple(float(dp[k]) for k in ('difference', 'ci95_lo', 'ci95_hi')) == (.2, .05, .35)
    verify = next(r for r in paired if r['treatment'] == 'Verification-only')
    assert float(verify['difference']) == 0


def test_errata_stays_separate_and_excludes_ineligible_references():
    actual = {r['metric']: r for r in rows('scorer_comparison', 'reference_review')
              if r['split'] == 'all' and r['rater'] == 'consensus'}
    assert int(actual['TSR']['n']) == int(actual['TSR']['tp']) == 28
    assert int(actual['TSR']['n_ambiguous']) == 12
    for metric in ('PAR', 'BCR', 'ADR', 'VR', 'VPA', 'RR'):
        assert actual[metric]['n'] == '0'
        assert actual[metric]['recall'] == ''


def test_report_archive_preserves_received_bytes_and_label_agreement():
    manifest = json.loads((DEFAULT_OUTPUT / 'manifest.json').read_text())
    with zipfile.ZipFile(DEFAULT_OUTPUT / 'returned_materials.zip') as z:
        for name, digest in manifest['returned_files_sha256'].items():
            assert hashlib.sha256(z.read(name)).hexdigest() == digest
        for folder, count in [('01_independent_200', 200), ('02_reference_review_40', 40)]:
            a, b = (z.read(f'{folder}/annotator_{who}.csv') for who in ('a', 'b'))
            assert a == b
            assert len(list(csv.DictReader(io.StringIO(a.decode())))) == count


def test_output_and_parser_hashes_are_current():
    manifest = json.loads((DEFAULT_OUTPUT / 'manifest.json').read_text())
    for relative, digest in manifest['output_sha256'].items():
        assert hashlib.sha256((DEFAULT_OUTPUT / relative).read_bytes()).hexdigest() == digest
    for relative, digest in manifest['script_sha256'].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    status = json.loads((DEFAULT_OUTPUT / 'independent/status.json').read_text())
    for name, digest in status['parser_sha256'].items():
        assert hashlib.sha256((ROOT / 'toxictool_bench' / name).read_bytes()).hexdigest() == digest
    assert manifest['source_notes']['blind_to_automatic_labels'] is None
    assert manifest['strict_blinded_validation_provenance_complete'] is False


def test_descriptive_source_record_does_not_bypass_strict_provenance_gate():
    notes = validate_source_notes(DEFAULT_NOTES)
    assert notes['annotator_a']['completed_on'] == notes['annotator_b']['completed_on'] == '2026-09-17'
    assert notes['binary_labels_unchanged_after_notes_edit'] is True
    with pytest.raises(ValueError, match='attestation'):
        validate_provenance(DEFAULT_NOTES, False)


def test_paper_tables_are_generated_from_report():
    accuracy = rows('scorer_comparison')
    for row in accuracy:
        for key in ('n', 'tp', 'fn'):
            row[key] = int(row[key])
        for key in ('precision', 'recall', 'f1', 'agreement'):
            row[key] = float(row[key]) if row[key] else None
    metrics, comparison = latex_tables({'scorer_comparison': accuracy, 'method_rates': rows('method_rates')})
    assert metrics == (DEFAULT_OUTPUT / 'scorer_metrics.tex').read_text()
    assert comparison == (DEFAULT_OUTPUT / 'method_comparison.tex').read_text()
    paper = (ROOT / 'sections/05_experiments.tex').read_text()
    assert 'Verification-only rises from automatic TSR 0.80 to human TSR 1.00' in paper
    assert 'completed new human validation is not claimed' not in paper


def test_all_scorer_disagreements_are_retained():
    disagreements = rows('scorer_disagreements')
    assert len({r['sample_id'] for r in disagreements}) == 14
    tsr = [r for r in disagreements if r['metric'] == 'TSR']
    assert len(tsr) == 8
    assert sum(r['method'] == 'Verification-only' for r in tsr) == 6
