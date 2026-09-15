from __future__ import annotations

import csv
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from analyze_human_holdout import (
    FIELDS, PACKET, ROOT, agreement_tables, bootstrap, confusion, human_metrics,
    keyed, labels_by_id, load_cases, method_rates, paired_comparisons, write_csv,
)
from prepare_holdout_adjudication import make_html


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
                self.assertEqual(r["n"], 240 if r["metric"] == "TSR" else 94)
                if r["metric"] == "VR":
                    self.assertEqual((r["tp"], r["fp"], r["fn"], r["tn"]), (80, 0, 1, 13))
        shared_vpa = [c for c in self.cases if c["split"] == "repeated_p1" and
                      all(c["ratings"][r]["VPA"] for r in ("annotator_a", "annotator_b"))]
        self.assertEqual(len(shared_vpa), 3)

    def test_sample_comparison_does_not_claim_unchanged_ranking(self):
        comparisons = paired_comparisons(self.cases)
        rows = {r["rater"]: r for r in comparisons if r["split"] == "core" and
                r["treatment"] == "Generic Guard" and r["control"] == "Double-pass" and r["metric"] == "TSR"}
        self.assertEqual(rows["auto"]["difference"], -.1)
        self.assertEqual(rows["annotator_a"]["difference"], .05)
        self.assertEqual(rows["annotator_b"]["difference"], 0)
        for r in rows.values():
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
            cells = " & ".join(f'{selected[r]["rate"]:.2f}' for r in ("auto", "annotator_a", "annotator_b"))
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


if __name__ == "__main__":
    unittest.main()
