# ToxicBench: anonymous supplementary artifact

This self-contained artifact accompanies **When Tools Silently Lie: Evaluating
and Mitigating Blind Compliance in Tool-Augmented Data Agents**. It provides
data, saved trajectories, frozen scoring, human labels, and executable offline
checks. No credentials, paid model API, external repository, or Git history is
needed for the reproduction commands below. Dependency installation requires
internet access unless the packages are already installed.

## Quick start

Use Python 3.10 (the tested environment). Run commands from the extracted
`ToxicBench_Supplementary` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-offline.txt
python reproduce.py verify
python reproduce.py quick --output reproduced_quick
python reproduce.py full --output reproduced_full
python -m pytest toxictool_bench/tests -q
```

`verify` uses only the Python standard library. `quick` recomputes the 200-case
post-freeze human comparison and separate 40-case reference review. `full` also
rescans 5,396 historical trajectories with old/new scoring, reproduces clustered
comparisons and exposure audits, analyzes 264 structured-evidence trajectories
and 152 repaired-injector trajectories, and reruns executable acceptance for all
131 retained synthetic tasks. Allow several minutes for the full check.
Use a new output directory each time; existing outputs are not overwritten.
The entry point disables network connections during all analysis stages.

A successful run writes `SUCCESS.json`. It compares recomputed results against
the archived results and fails on mismatches. Scores stored in historical logs
can predate scorer repair; the primary historical comparisons are **rescored
from final answers and tool events**, not accepted from those stored scores.
The separate V3 repaired-injector analysis aggregates its archived run metrics.
No new model trajectories or human labels are generated.

## Paper-to-artifact map

| Paper result | Evidence and archived results | Reproduction output under `reproduced_full/` |
|---|---|---|
| Expanded GPT and cross-model comparisons (§4.2) | `toxictool_bench/results/paper_run_manifest.csv`; linked JSONL trajectories; `output/scorer_revision_v2/version_summary.csv` | `scorer_revision/version_summary.csv` |
| Four-method comparison and clustered intervals (§4.3) | `leakage_free_defense_manifest.csv` in the same results directory; `output/scorer_revision_v2/cluster_sensitivity.csv` | `scorer_revision/cluster_sensitivity.csv` and version summary |
| Repeated poisoning / 101 VPA cases (§4.3) | `verification_stress_manifest.csv`; `output/scorer_revision_v2/vpa_inventory.csv` and `vpa_evidence.csv` | `scorer_revision/vpa_inventory.csv`, `vpa_evidence.csv` |
| Post-freeze human evaluation (§4.4) | `human/independent_200.jsonl`; binary CSVs; `output/human_validation_20260920/independent/` | `human/independent_200/` |
| Separate 40-case reference review | `human/reference_review_40.jsonl`; binary CSVs | `human/reference_review_40/` |
| Historical development audit | `human/historical_development_240.jsonl` | Archived evidence; not an independent test of the revised scorer |
| Task construction / executable acceptance (Appendix A) | `tasks/` and `datasets/` under `toxictool_bench/`; `output/task_acceptance_v1/` | `task_acceptance/` |
| Historical delivery audit (Appendix E) | `output/submission_revision_v3/historical_*` | `delivery_audit/` |
| Fresh repaired-injector checks (Appendix E) | `output/submission_revision_v3/protocol.json` and `runs/` | `repaired_injector/` |
| Public-table matched-evidence controls (Appendix E) | `output/evidence_controls_v4/` and three public CSVs | `evidence_controls/` |

The full manuscript and its figures are in the separately submitted paper PDF;
this ZIP is the executable evidence supplement, not an alternative paper version.

## How to interpret the results

- The single-table retained set has 58 numerical and 60 semantic/schema tasks.
  The original task files retain all 120 instances. `corrected_task()` applies
  audited reference corrections and marks two ambiguous numerical instances for
  exclusion without editing historical queries, poison targets, or trajectories.
- The 34+24 cross-model tasks overlap the expanded suites. The 13 multi-table
  tasks yield 131 retained synthetic tasks, not 131 additional tasks.
- TSR includes all retained runs. BCR, PAR, VR, VPA and RR condition on recorded
  poison exposure. Historical exposure is not certified valid intervention;
  the separate audit flags 204 events among 3,319 across eight adapter identifiers.
- Version summaries also retain archived PandasAI rows for transparency. Exclude
  PandasAI from observation-level main-paper comparisons: that historical adapter
  edited the final answer after execution. Cross-model means use only the three
  common observation-level adapters; DA-Agent is a separate numerical-only row.
- The four-method 118-task comparison uses Claude Haiku 4.5. Do not combine it
  with the separate expanded GPT results merely because task counts match.
- Repeated-poison counts retain 1,572 eligible trajectories and 101 detected VPA
  cases. VPA means adoption after checking, not necessarily ignoring sufficient
  correct evidence. The evidence inventory distinguishes corrupted checks from
  unmodified checks and candidate clean-reference matches.
- The 200 post-freeze cases use task IDs disjoint from scorer-development packets,
  not disjoint task templates. TSR agreement is 192/200; the behavior denominator
  is 77. See `HUMAN_EVALUATION.md` for labels, sampling and limitations.
- Executable acceptance finds 119 valid target interventions among 131 fixed
  tasks, with scripted raw-data recovery for 119/119 under one-shot and 110/119
  under repeated poisoning. This is feasibility of specified calls, not an
  autonomous-agent success rate.
- Public-table V4 uses a separate structured numeric endpoint and seeded calls;
  it tests a local evidence effect, not unconstrained real-world robustness.

## Integrity, anonymity, and provenance

`SHA256SUMS` covers the distributed files. `ANONYMIZATION_REPORT.json` lists
files with local-path/identity substitutions. Task answers, binary human labels,
numeric data, and metric definitions are not intentionally altered. The full
reproduction checks every old/new/corrected trajectory score against the
archived analysis to test that these substitutions preserve the measurements.

Original per-experiment hash records are retained as historical provenance;
they describe the original inputs and may not match anonymized copies. Use the
release-level `SHA256SUMS` for this ZIP. The only portability edit to an existing
analysis module loads the bundled `legacy_evaluator.py` instead of querying a
Git commit. Current scorer files are otherwise unchanged. The independent human
protocol records their freeze hashes.

For reviewer inspection, human exports restore method/task/source evidence
relationships that were masked in the annotation packet. These exports were
created after annotation; they are not a new blinded annotation packet. Personal
notes and internal provenance declarations are excluded. Binary labels remain
exactly the received labels. Archived historical statements about pending
validation describe their original experiment stage, not the status of the
completed post-freeze evaluation supplied here.

No online rerun is needed to evaluate this artifact. Some archived experiment
modules retain their original API-capable functions for methodological context;
the documented commands invoke only offline analysis. External model providers,
third-party adapter checkouts, and model weights are not bundled.

## Licensing

Project code is covered by the included MIT `LICENSE`. Public datasets retain
their own licenses and attribution: Palmer Penguins is CC0; Auto MPG and Bike
Sharing are CC BY 4.0. See the license and provenance Markdown files under
`toxictool_bench/datasets/`. Source authors and dataset citations are retained;
they are not identities of this submission's authors. No endorsement is implied.
