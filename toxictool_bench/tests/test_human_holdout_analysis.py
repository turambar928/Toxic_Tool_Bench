from __future__ import annotations

import csv
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from analyze_human_holdout import (
    FIELDS, PACKET, ROOT, agreement_tables, bootstrap, confusion, human_metrics,
    keyed, labels_by_id, load_cases, method_rates, paired_comparisons, write_csv,
)
from prepare_holdout_adjudication import make_html, import_completed


class HoldoutUnitTests(unittest.TestCase):
    def test_compound_metrics_follow_paper_definition(self):
        label = dict.fromkeys(FIELDS, 0)
        label.update(final_correct=1, anomaly_detected=1)
        self.assertEqual(human_metrics(label)["RR"], 1)
        self.assertEqual(human_metrics(label)["VR"], 0)
        label.update(final_correct=0, anomaly_detected=0, adopted_poisoned=1)
        self.assertEqual(human_metrics(label)["BCR"], 1)
        label["substantive_validation"] = 1
        self.assertEqual(human_metrics(label)["BCR"], 0)
        self.assertEqual(human_metrics(label)["VPA"], 1)
        label["ambiguous"] = 1
        self.assertTrue(all(v is None for v in human_metrics(label).values()))

    def test_zero_positive_counts_are_not_perfect_recall(self):
        stats = confusion([0, 0], [0, 0])
        self.assertEqual(stats["agreement"], 1)
        for field in ("recall", "precision", "f1", "kappa"):
            self.assertIsNone(stats[field])

    def test_clean_and_toxic_are_distinct_join_keys(self):
        rows = [dict(task_id="t", adapter="a", environment=e) for e in ("clean", "toxic")]
        self.assertEqual(len(keyed(rows, ("task_id", "adapter", "environment"))), 2)
        with self.assertRaises(ValueError):
            keyed(rows + rows[:1], ("task_id", "adapter", "environment"))

    def test_bootstrap_preserves_suite_counts(self):
        point, low, high = bootstrap([[1], [-1, -1]], rounds=100)
        self.assertEqual((point, low, high), (-1 / 3, -1 / 3, -1 / 3))

    def test_returned_sheet_rejects_partial_or_mismatched_labels(self):
        fields = ["sample_id", "pair_id", *FIELDS, "notes"]
        row = {"sample_id": "S", "pair_id": "P", **dict.fromkeys(FIELDS, "0"), "notes": "reviewed"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "labels.csv"
            write_csv(path, [row], fields)
            self.assertIn("S", labels_by_id(path, [row]))
            row["substantive_validation"] = ""
            write_csv(path, [row], fields)
            with self.assertRaises(ValueError):
                labels_by_id(path, [row])
            row["substantive_validation"] = "0"
            row["recovered_clean"] = "1"
            write_csv(path, [row], fields)
            with self.assertRaises(ValueError):
                labels_by_id(path, [row])

    def test_casebook_escapes_untrusted_trajectory_text(self):
        row = dict(sample_id="HOLD-001", user_query="<script>alert(1)</script>",
                   clean_oracle="x", poisoned_oracle="y", final_answer="</pre>",
                   reference_context_json="{}", tool_events_json="[]")
        page = make_html([row])
        self.assertNotIn("<script>", page)
        self.assertIn("&lt;script&gt;", page)

    def test_partial_import_preserves_previous_rows_and_rejects_overwrite(self):
        fields = ["sample_id", "pair_id", *FIELDS, "notes"]
        first = {"sample_id": "S1", "pair_id": "P", **dict.fromkeys(FIELDS, "0"), "notes": "synthetic original"}
        blank = {"sample_id": "S2", "pair_id": "P", **dict.fromkeys(FIELDS, ""), "notes": ""}
        incoming = {**blank, **dict.fromkeys(FIELDS, "0"), "notes": "synthetic supplement"}
        cases = [{"sample_id": r["sample_id"], "requires_adjudication": True, "evidence": r} for r in (first, blank)]
        with tempfile.TemporaryDirectory() as tmp:
            packet = Path(tmp)
            (packet / "analysis").mkdir()
            (packet / "analysis/adjudication_release.json").write_text('{"source_input_sha256": {}}')
            write_csv(packet / "adjudication.csv", [first, blank], fields)
            submitted = packet / "submitted.csv"
            write_csv(submitted, [incoming], fields)
            with patch("prepare_holdout_adjudication.PACKET", packet), patch("prepare_holdout_adjudication.load_cases", return_value=(cases, {})):
                import_completed(submitted, allow_partial=True)
                with (packet / "adjudication.csv").open() as handle:
                    rows = list(csv.DictReader(handle))
                self.assertEqual(rows, [first, incoming])
                incoming["final_correct"] = "1"
                write_csv(submitted, [incoming], fields)
                with self.assertRaises(ValueError):
                    import_completed(submitted, allow_partial=True)


class ReturnedHoldoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases, cls.status = load_cases()

    def test_source_identity_exposure_and_annotation_status(self):
        self.assertEqual(len(self.cases), 240)
        self.assertEqual(self.status["n_exposed"], 94)
        self.assertEqual(self.status["n_task_ids"], 40)
        self.assertEqual(self.status["n_disputed_trajectories"], 60)
        self.assertEqual(self.status["n_adjudication_trajectories"], 70)
        self.assertEqual(self.status["n_development_task_ids_excluded"], 68)
        self.assertTrue(all(not c["exposed"] for c in self.cases if c["environment"] == "clean"))
        if not self.status["consensus_available"]:
            self.assertTrue(all("consensus" not in c["ratings"] for c in self.cases))

    def test_independent_totals_and_scorer_denominators(self):
        agreement, accuracy = agreement_tables(self.cases)
        # Raw field totals independently checked against the returned sheets.
        for rater, correct in (("a", 168), ("b", 181)):
            self.assertEqual(sum(c[rater]["final_correct"] for c in self.cases), correct)
        validation = next(r for r in agreement if r["split"] == "all" and r["field"] == "substantive_validation")
        self.assertEqual(validation["agreement"], 1)
        for r in accuracy:
            if r["split"] == "all":
                self.assertEqual(r["n_eligible"], 240 if r["metric"] == "TSR" else 94)
                self.assertEqual(r["n"] + r["n_pending"] + r["n_ambiguous"], r["n_eligible"])
                if r["metric"] == "VR":
                    self.assertEqual((r["tp"], r["fp"], r["fn"], r["tn"]), (80, 0, 1, 13))
        shared_vpa = [c for c in self.cases if c["split"] == "repeated_p1" and
                      all(c["ratings"][r]["VPA"] for r in ("annotator_a", "annotator_b"))]
        self.assertEqual(len(shared_vpa), 3)

    def test_final_reference_is_complete_and_preserves_label_provenance(self):
        self.assertTrue(self.status["consensus_available"])
        self.assertEqual(self.status["n_received_adjudication"], 70)
        self.assertEqual(self.status["n_reference_available"], 240)
        self.assertEqual(self.status["n_pending_adjudication"], 0)
        self.assertEqual(sum(c["ratings"]["consensus"]["TSR"] for c in self.cases), 193)
        _, accuracy = agreement_tables(self.cases)
        rows = {r["metric"]: r for r in accuracy if r["split"] == "all" and r["rater"] == "consensus"}
        self.assertEqual((rows["TSR"]["tp"], rows["TSR"]["fp"], rows["TSR"]["fn"], rows["TSR"]["tn"]), (129, 3, 64, 44))
        self.assertTrue(all(r["n_pending"] == r["n_ambiguous"] == 0 for r in rows.values()))
        self.assertEqual((rows["VPA"]["n"], rows["VPA"]["tp"], rows["VPA"]["fp"], rows["VPA"]["fn"]), (94, 4, 0, 0))

    def test_sample_comparison_does_not_claim_unchanged_ranking(self):
        comparisons = paired_comparisons(self.cases)
        rows = {r["rater"]: r for r in comparisons if r["split"] == "core" and
                r["treatment"] == "Generic Guard" and r["control"] == "Double-pass" and r["metric"] == "TSR"}
        self.assertEqual(rows["auto"]["difference"], -.1)
        self.assertEqual(rows["annotator_a"]["difference"], .05)
        self.assertEqual(rows["annotator_b"]["difference"], 0)
        for r in (rows[k] for k in ("auto", "annotator_a", "annotator_b")):
            self.assertEqual(r["n_paired_tasks"], 20)
            self.assertLessEqual(r["ci95_lo"], 0)
            self.assertGreaterEqual(r["ci95_hi"], 0)

    def test_paper_holdout_table_matches_derived_method_rates(self):
        paper = (ROOT / "sections/08_appendix_guard_details.tex").read_text()
        rates = method_rates(self.cases)
        for split, method in (("core", "Base"), ("core", "Double-pass"),
                              ("core", "Verification-only"), ("core", "Generic Guard"),
                              ("repeated_p1", "Double-pass"), ("repeated_p1", "Generic Guard")):
            selected = {r["rater"]: r for r in rates if r["split"] == split and r["method"] == method
                        and r["environment"] == "toxic" and r["metric"] == "TSR"}
            cells = " & ".join(f'{selected[r]["rate"]:.2f}' for r in ("auto", "consensus"))
            self.assertIn(f"{method} & 20 & {cells}", paper)

    def test_reviewer_zip_has_only_blinded_evidence_and_empty_labels(self):
        path = ROOT / "output/human_holdout_adjudication_v2.zip"
        with zipfile.ZipFile(path) as z:
            files = {Path(n).name: n for n in z.namelist() if not n.endswith("/")}
            self.assertEqual(set(files), {"README_CN.md", "cases.html", "checksums.json", "evidence.csv", "adjudication_to_fill.csv"})
            evidence = list(csv.DictReader(z.read(files["evidence.csv"]).decode().splitlines()))
            labels = list(csv.DictReader(z.read(files["adjudication_to_fill.csv"]).decode().splitlines()))
            self.assertEqual(len(evidence), 70)
            self.assertEqual(len(labels), 70)
            self.assertEqual({r["sample_id"] for r in evidence}, {c["sample_id"] for c in self.cases if c["requires_adjudication"]})
            self.assertTrue(all(r[f] == "" for r in labels for f in FIELDS))
            self.assertTrue(set(evidence[0]).isdisjoint({"method", "adapter", "model", "source", "run_slot", "split", "disputed_fields"}))

    def test_remaining_packet_contains_only_ten_unexposed_protocol_checks(self):
        path = ROOT / "output/human_holdout_adjudication_remaining_10.zip"
        with zipfile.ZipFile(path) as z:
            names = {Path(n).name: n for n in z.namelist() if not n.endswith("/")}
            rows = list(csv.DictReader(z.read(names["evidence.csv"]).decode().splitlines()))
            labels = list(csv.DictReader(z.read(names["adjudication_to_fill.csv"]).decode().splitlines()))
            selected = set(json.loads((PACKET / "adjudication_selection.json").read_text())["additional_sample_ids"])
            self.assertEqual({r["sample_id"] for r in rows}, selected)
            self.assertEqual(len(rows), 10)
            self.assertTrue(all(not c["exposed"] for c in self.cases if c["sample_id"] in selected))
            self.assertTrue(all(r[f] == "" for r in labels for f in FIELDS))

    def test_adjudicated_paper_precision_recall_and_counts(self):
        _, accuracy = agreement_tables(self.cases)
        paper = (ROOT / "sections/08_appendix_guard_details.tex").read_text()
        final = [r for r in accuracy if r["rater"] == "consensus" and r["split"] == "all"]
        self.assertEqual(len(final), 7)
        for r in final:
            if r["split"] == "all":
                cells = f'{r["metric"]} & {r["n"]} & {r["tp"] + r["fn"]} & {r["precision"]:.3f} & {r["recall"]:.3f} & {r["f1"]:.3f}'
                self.assertIn(cells, paper)


if __name__ == "__main__":
    unittest.main()
