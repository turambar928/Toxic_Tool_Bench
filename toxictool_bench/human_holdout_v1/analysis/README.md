# Returned holdout analysis

Status: two completed annotator sheets; third-rater adjudication of 70 trajectories
is pending. Do not interpret either rater as an adjudicated ground truth.

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
- `analysis_status.json`: eligibility counts, pending status, definitions and hashes.
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

Give the third reviewer only `output/human_holdout_adjudication_v2.zip` from the
repository root. Do not send this analysis directory. See the parent README for
import commands. Final consensus columns appear only after all 70 rows return.
The original A/B analysis remains available after adjudication.
