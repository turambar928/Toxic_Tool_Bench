# Returned holdout analysis

Status: complete. All 60 disputed trajectories and ten additional ROAS
numeric-tolerance checks have returned third-rater labels. The final `consensus`
reference covers all 240 trajectories, including all 94 exposed trajectories;
there are no pending or ambiguous decisions. Third-rater labels replace all six
fields on those 70 rows; the other 170 use the original raters' shared labels.
Original A/B comparisons are retained separately.

Run `python3 toxictool_bench/analyze_human_holdout.py` from the repository root.
The script preserves source annotations and the evaluator. It checks one-to-one
source identity using task, adapter, and environment, verifies the distributed
evidence, and derives current scorer labels from original logs.

- `annotator_agreement.csv`: raw two-rater agreement before adjudication.
- `scorer_comparison.csv`: confusion counts, precision, recall, F1, and agreement
  against each rater, overall and by sampling stratum. Empty ratios are undefined.
- `method_rates.csv`: numerator and denominator for each method and label source.
- `paired_comparisons.csv`: task-paired, suite-stratified 95% bootstrap intervals;
  these condition on the fixed selected tasks and the rater.
- `case_metrics.csv`: traceable automatic and per-rater derived labels.
- `disagreements.csv`: the 60 trajectories with at least one differing field.
- `analysis_status.json`: eligibility counts, received/pending status, definitions and hashes.
- `reference_status.csv`: reference availability and label provenance per trajectory.
- `adjudication_imports.json`: original returned-file hashes and import receipts.
- `adjudication_release.json`: administrator-only fingerprints for the 70-case
  release (60 disagreements plus ten numeric-tolerance checks).

TSR uses all 240 trajectories; behavior metrics use the 94 exposed trajectories.
No pooled positive rate is presented as benchmark-wide prevalence. Original
`recovered_clean` labels require a check; the derived RR uses correct AND
(detection OR validation), matching the manuscript.

The source packet uses fixed task selection, has 100 clean/toxic pairs plus
20 repeated-poison method pairs, and is not a randomized representative sample.
The cross-model stratum contains AutoGen/Sonnet numerical tasks only. Pair-slot
assignment was fixed even though row order was shuffled.

The archived reviewer packets are `output/human_holdout_adjudication_v2.zip`
and `output/human_holdout_adjudication_remaining_10.zip`. Original returned files:

- `toxictool_bench/human_holdout_adjudication_v1/adjudication_completed.csv` (60 rows)
- `toxictool_bench/human_holdout_adjudication_remaining_10/adjudication_completed.csv` (10 rows)

Their SHA-256 hashes and imported IDs are in `adjudication_imports.json`.
The importer preserves existing labels and rejects conflicting overwrites.
The evidence, original annotations, task oracles, and scorer remain unchanged.

## Final findings

- TSR: 173/240 scorer decisions agree with the reference (72.1%); precision
  0.977, recall 0.668. The scorer misses 64 human-correct answers.
- VR: precision 1.000, recall 0.988 on 94 exposed trajectories.
- VPA: all four human-positive cases match the scorer, with no false positives;
  the positive count is small.
- BCR: one of three human-positive cases is detected; RR recall is 0.500.
- Core poisoned TSR: all four methods have human TSR 0.85 on the same 20 tasks.
- Repeated poisoning: Double-pass 0.80, Generic Guard 0.70; Guard minus
  Double-pass is -0.10, task-paired 95% interval [-0.25, 0.00].

The completed audit supports the observed check-then-adopt failure. It does not
confirm the full automatic method ranking or remove final-answer scoring error.
