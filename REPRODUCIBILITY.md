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

The paper-facing defense ablation uses `claude-haiku-4-5-20251001` and four LangGraph variants: Base, matched Double-pass, Verification-only, and Generic Guard. Rebuild its summaries, task-level bootstrap intervals, poison/severity tables, and overhead table with:

```bash
bash toxictool_bench/rebuild_leakage_free_defense_results.sh
```

The matched Double-pass adapter executes two ordinary routes with the same per-route cap, without expectations or primary-answer handoff.

## Repeated-Poison Matrix

The complete matrix covers three suites, three two-route variants, and probabilities 0.25, 0.50, 0.75, and 1.00:

```bash
MODEL=claude-haiku-4-5-20251001 \
  bash toxictool_bench/run_full_verification_stress.sh
python3 toxictool_bench/summarize_verification_stress.py
python3 toxictool_bench/plot_verification_stress.py
```

The matrix corrupts matching returned observations repeatedly. Primary and verification routes still share source tables and a backend, so this is not source-independent or Byzantine corruption.

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
