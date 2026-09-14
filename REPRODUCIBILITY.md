# Reproducibility

## Environment

The validated public-adapter dependencies are pinned in `requirements.txt`:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Scoring and tests do not require the ignored `api` file. Model runs require local endpoint configuration, which is deliberately excluded from the repository.

## Determinism

Bootstrap commands use seed `13` unless overridden. Repeated poisoning derives each gate from a SHA-256 digest of task ID, tool name, call index, and arguments. The independent audit packet uses seed `20260831`. Task files, selected logs, summaries, and checksums are listed in the result manifests and `artifact_sha256.csv`.

## Leakage-Free Defense Results

Refresh the complete primary cross-model and expanded-GPT suites with
`python3 toxictool_bench/sync_primary_paper.py`. This scores all 1,460 and 720
trajectories respectively, updates the main tables and headline ranges, and
records input hashes in `primary_analysis_provenance.json`. It does not depend
on the three unavailable historical multi-table logs. Regenerate all paper
figures after the result pipelines with `python3 toxictool_bench/plot_paper_figures.py`
and `python3 toxictool_bench/plot_verification_stress.py`.

The paper-facing defense ablation uses `claude-haiku-4-5-20251001` and four LangGraph variants: Base, matched Double-pass, Verification-only, and Generic Guard. Rebuild its summaries, task-level bootstrap intervals, poison/severity tables, and overhead table with:

```bash
bash toxictool_bench/rebuild_leakage_free_defense_results.sh
```

The matched Double-pass adapter executes two ordinary routes with the same per-route cap, without expectations or primary-answer handoff.

The rebuild now reads the committed `leakage_free_defense_manifest.csv` directly;
it does not choose logs by filesystem modification time. It rescales no answers
and makes no model calls. It re-evaluates the fixed 960 trajectories and writes
the defense tables directly into `sections/05_experiments.tex` and
`sections/08_appendix_guard_details.tex`, together with paired CSVs, marginal
intervals, exact BCR counts, answer-selection counts, and the existing 120-row
consensus audit. The wrapper also refreshes the repeated-poison, AutoGen, and
alternative-policy appendix tables with the same evaluator. Human labels are unchanged. The evaluator now removes known adapter display prefixes uniformly before scoring the underlying answer.

Paired success inference uses seed 13 and 5,000 draws. Each draw retains the
four method/environment outcomes for a task; the combined analysis keeps 60
tasks in each suite. Behavior differences use tasks exposed in both methods.
Marginal intervals use seed 13 plus the adapter index. The scorer sensitivity
comparison uses evaluator commit `f0aa054dccc9437dcf89f0b22a01825e2772be66` on
the same trajectories, rather than a moving HEAD or rounded CSV differences.
See `leakage_free_defense_analysis_provenance.json` for input hashes and
`scorer_consensus_validation.json` for the re-evaluated development audit.

Three older sources in the broader `paper_run_manifest.csv` are not included
in this checkout; their paths are recorded in the analysis provenance. The
complete defense analysis and consensus audit do not depend on those files.
The all-experiment audit/rebuild still requires them; do not silently skip
them or describe this rebuild as validation of every benchmark experiment.
An independent held-out human audit has not been performed by this script.


## Repeated-Poison Matrix

The complete matrix covers three suites, three two-route variants, and probabilities 0.25, 0.50, 0.75, and 1.00:

```bash
MODEL=claude-haiku-4-5-20251001 \
  bash toxictool_bench/run_full_verification_stress.sh
python3 toxictool_bench/summarize_verification_stress.py
python3 toxictool_bench/plot_verification_stress.py
```

The matrix corrupts matching returned observations repeatedly. Primary and verification routes still share source tables and a backend, so this is not source-independent or Byzantine corruption. The summary command defaults to the committed manifest, rescoring each trajectory with the current evaluator; use `--discover` only to intentionally select a new run set. The current plot shows VPA, while the CSV retains both BCR and VPA. At p=1 all nine BCR cells are zero, but VPA is nonzero; lower probabilities can still yield BCR events.

## Independent Audit

Build the fixed blinded packet and, after two annotators independently complete and lock their sheets, compute agreement:

```bash
python3 toxictool_bench/build_blind_audit_packet.py
python3 toxictool_bench/merge_blind_audit.py
```

The completed packet is stored in `toxictool_bench/human_audit_v2/`. The
pre-adjudication macro Cohen's kappa is 0.913 over 120 trajectories. The merge
script lists 12 rows with at least one disagreement in `adjudication.csv`.

To audit scorer agreement and identify answers that mention both clean and poisoned
oracle values, run:

```bash
python3 toxictool_bench/audit_scorer_credibility.py
```

The report computes precision, recall, and F1 against all 120 final-consensus
rows. Cells on which the original annotators agreed retain that label; the 16
disputed label cells across 12 trajectories use the completed third-party
adjudication.

Do not expose `key.csv`, raw scorer outputs, or one annotator's labels to the other. Report Cohen's kappa on pre-adjudication labels.

### Third-party follow-up review

The repository also contains a sanitized handoff packet in
`toxictool_bench/human_review_v3/`. It has 12 disputed trajectories for final
adjudication and 18 non-disputed trajectories for auditing whether scorer-marked
VR actions checked the task-relevant target. The packet deliberately omits oracle
answers, poison markers, scorer labels, keys, raw JSONL, and prior annotator
labels. It is therefore suitable for an external reviewer to work independently.

Regenerate it with:

```bash
python3 toxictool_bench/build_human_review_packet.py
```

The completed, versioned label sheets are stored beside the templates. Validate
and merge them with:

```bash
python3 toxictool_bench/finalize_human_review.py
python3 toxictool_bench/audit_scorer_credibility.py
```

The first command writes `human_audit_v2/adjudicated_labels.csv` and
`human_review_v3/vr_audit_summary.json`. The second recomputes scorer
precision/recall/F1 against the final consensus. The original pre-adjudication
agreement report remains unchanged. The 18-case VR review is conditioned on
non-disputed scorer-positive VR cases and must not be reported as an overall
trajectory-level accuracy estimate.

## Release Checks

```bash
python3 toxictool_bench/build_artifact_checksums.py
python3 toxictool_bench/release_audit.py
python3 toxictool_bench/check_paper_static.py --main main.tex
python3 -m pytest toxictool_bench/tests -q
```

Adapters using external source checkouts accept `TOXICTOOL_BASELINE_DIR`; expected imports are documented in `RUN_COMMANDS.md`. Code and synthetic benchmark data are covered by `LICENSE` and `DATA_LICENSE.md`.

## Updated defense figures

After rebuilding the tables, regenerate the corresponding PDF figures in an
environment with NumPy and Matplotlib installed:

```bash
python3 toxictool_bench/plot_verification_stress.py
python3 toxictool_bench/plot_paper_figures.py --defense-only
```

The cost plot now uses the four leakage-free Claude Haiku variants, not the older
GPT six-variant ablation. Original Figure 1 and Figure 2 PNG assets, absent from
the fetched tree, were recovered without redrawing from the user-supplied
`toxic_bench (3).pdf` (page 4).
