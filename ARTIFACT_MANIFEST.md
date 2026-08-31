# ToxicBench Artifact Manifest

Last updated: 2026-08-31

This manifest lists the paper-facing artifacts needed to inspect and reproduce the ToxicBench experiments. It intentionally emphasizes public-framework results: LangGraph ReAct, smolagents, PandasAI, DA-Agent where practical, and AutoGen. Legacy development artifacts may remain in `toxictool_bench/results/`, but they are not part of the current paper mainline.

## Paper Entry Points

| Artifact | Purpose |
|---|---|
| `main.tex` | Main paper entry point. |
| `REPRODUCIBILITY.md` | Environment, seeds, stress matrix, and release checks. |
| `LICENSE` / `DATA_LICENSE.md` | Code and synthetic benchmark-data licensing. |
| `sections/*.tex` | Paper sections and appendix. |
| `references.bib` | Bibliography database. |
| `SUBMISSION_CHECKLIST.md` | Reviewer-issue coverage and final PDF checklist. |
| `PAPER_CONSISTENCY_CHECK.md` | Earlier consistency audit notes. |

## Task Suites

| File | Scope |
|---|---|
| `toxictool_bench/tasks/numerical_expanded.jsonl` | 34-task numerical cross-model suite. |
| `toxictool_bench/tasks/semantic_schema.jsonl` | 24-task semantic/schema cross-model suite. |
| `toxictool_bench/tasks/numerical_iclr2027.jsonl` | 60-task expanded numerical release suite. |
| `toxictool_bench/tasks/semantic_schema_iclr2027.jsonl` | 60-task expanded semantic/schema release suite. |
| `toxictool_bench/tasks/realistic_extension_iclr2027.jsonl` | 13-task multi-table join extension. |
| `toxictool_bench/tasks/*_stratified10.jsonl` | Small fixed subsets for smoke and stress tests. |
| `toxictool_bench/tasks/*_stratified20.jsonl` | Fixed subsets for stronger verification baselines. |

## Datasets

All CSV datasets are stored under `toxictool_bench/datasets/`.

| Dataset group | Files |
|---|---|
| Original numerical and semantic/schema suites | `ab_test.csv`, `campaign_roi.csv`, `customer_segments.csv`, `data_dictionary.csv`, `employee_productivity.csv`, `experiment_outcomes.csv`, `feature_flags.csv`, `loan_evidence.csv`, `medical_trial.csv`, `monthly_revenue.csv`, `policy_eval.csv`, `pricing_evidence.csv`, `product_margin.csv`, `quality_batches.csv`, `regional_sales.csv`, `retention_evidence.csv`, `risk_dictionary.csv`, `safety_evidence.csv`, `shipping_evidence.csv`, `store_efficiency.csv`, `subscription_cohorts.csv`, `support_queue.csv`, `toy_sales.csv`, `vendor_evidence.csv`, `warehouse_dictionary.csv`. |
| Expanded and multi-table suites | `iclr2027_*.csv`, including ad operations, clinic, customer/order, product, retrieval, schema dictionary, and support-team tables. |

## Main Result Tables

| File | Used for |
|---|---|
| `toxictool_bench/results/cross_model_summary.csv` | Numerical cross-model summary. |
| `toxictool_bench/results/semantic_schema_cross_model_summary.csv` | Semantic/schema cross-model summary. |
| `toxictool_bench/results/iclr2027_gpt_expanded_cross_agent_combined_summary.csv` | GPT-only 120-task public cross-agent summary. |
| `toxictool_bench/results/iclr2027_gpt_expanded_cross_agent_combined_poison_summary.csv` | Expanded GPT poison-type breakdown. |
| `toxictool_bench/results/iclr2027_gpt_expanded_cross_agent_combined_severity_summary.csv` | Expanded GPT severity breakdown. |
| `toxictool_bench/results/leakage_free_defense_combined_summary.csv` | Post-fix 120-task LangGraph defense ablation. |
| `toxictool_bench/results/leakage_free_defense_{numerical_iclr2027,semantic_schema_iclr2027}_summary.csv` | Suite-level post-fix defense results. |
| `toxictool_bench/results/leakage_free_defense_overhead.csv` | Mean, p50, and p90 latency plus tool-event overhead. |
| `toxictool_bench/results/leakage_free_defense_{combined,numerical_iclr2027,semantic_schema_iclr2027}_{poison,severity}_summary.csv` | Poison-type and severity breakdowns. |
| `toxictool_bench/results/leakage_free_defense_manifest.csv` | Immutable mapping from post-fix result groups to raw logs. |
| `toxictool_bench/results/verification_stress_summary.csv` | Full repeated-poison probability matrix with bootstrap intervals. |
| `toxictool_bench/results/verification_stress_manifest.csv` | Complete repeated-poison chunk manifest. |
| `toxictool_bench/results/paper_run_manifest.csv` | Immutable mapping from each paper result group to its raw run log. |
| `toxictool_bench/results/artifact_sha256.csv` | SHA-256 checksums for task files, manifest-listed raw logs, scorer, poisoner, and paper-facing summaries. |
| `toxictool_bench/results/iclr2027_stronger_baselines_strict_summary.csv` | LangGraph abstain, randomized, and selective-policy results on fixed subsets. |

## Confidence Intervals

| File | Scope |
|---|---|
| `toxictool_bench/results/numerical_cross_model_bootstrap_ci.csv` | Numerical cross-model bootstrap CIs. |
| `toxictool_bench/results/semantic_schema_cross_model_bootstrap_ci.csv` | Semantic/schema cross-model bootstrap CIs. |
| `toxictool_bench/results/numerical_gpt_bootstrap_ci.csv` | GPT numerical bootstrap CIs. |
| `toxictool_bench/results/leakage_free_defense_combined_bootstrap_ci.csv` | Combined post-fix defense bootstrap CIs. |
| `toxictool_bench/results/leakage_free_defense_{numerical_iclr2027,semantic_schema_iclr2027}_bootstrap_ci.csv` | Suite-level post-fix defense bootstrap CIs. |

## Raw Logs and Case Studies

| Artifact | Scope |
|---|---|
| `toxictool_bench/results/20260829-*_langgraph_react_*_claude-haiku-4-5-20251001_*.jsonl` | Selected raw logs for the leakage-free defense ablation. |
| `toxictool_bench/results/20260819-*_langgraph_react_{abstain,randomized,selective}_gpt-5.4-mini_both.jsonl` | LangGraph alternative-policy logs on fixed numerical and semantic subsets. |
| `toxictool_bench/results/verification_stress/**/*.jsonl` | Complete chunked repeated-poison logs selected by the stress manifest. |
| `CASE_STUDIES.md` | Qualitative blind-compliance cases. |
| `GUARDED_CASE_STUDIES.md` | Guarded-verification recovery cases. |

## Audit and Scoring

| Artifact | Purpose |
|---|---|
| `toxictool_bench/evaluator.py` | Task-success and behavior-metric scoring. |
| `toxictool_bench/poisoners.py` | Silent-poisoning operators. |
| `toxictool_bench/bootstrap_ci.py` | Nonparametric task-level bootstrap CIs. |
| `toxictool_bench/check_paper_static.py` | Static citation/reference/placeholder check for the paper. |
| `toxictool_bench/audit_agreement.py` | Human-audit agreement utility. |
| `toxictool_bench/rebuild_paper_results.py` | Rebuild paper-facing summaries and CIs from the immutable run manifest. |
| `toxictool_bench/recalibrate_author_audit.py` | Compare the strict scorer with the earlier single-author labels. |
| `toxictool_bench/results/iclr2027_manual_audit_completed_stratified80.csv` | Historical 80-run single-author audit sheet; repeated passes are not independent IAA. |
| `toxictool_bench/results/strict_scorer_author_audit_comparison.csv` | Run-level strict-scorer versus single-author diagnostic comparison. |
| `toxictool_bench/results/strict_scorer_author_audit_agreement.json` | Agreement summary for that diagnostic comparison; not inter-annotator agreement. |
| `toxictool_bench/results/human_audit_v2/evidence.csv` | Blinded evidence for 120 exposed trajectories. |
| `toxictool_bench/results/human_audit_v2/annotator_{a,b}.csv` | Empty independent label sheets; completion is pending. |
| `toxictool_bench/build_blind_audit_packet.py` / `merge_blind_audit.py` | Fixed-seed packet builder and strict pre-adjudication IAA merger. |

## Reproduction Commands

The canonical command list is `RUN_COMMANDS.md`. The most important entry points are:

```bash
python3 toxictool_bench/check_adapter_readiness.py
python3 toxictool_bench/rebuild_paper_results.py
bash toxictool_bench/rebuild_leakage_free_defense_results.sh
python3 toxictool_bench/summarize_verification_stress.py
python3 toxictool_bench/plot_verification_stress.py
python3 toxictool_bench/build_public_paper_summaries.py
python3 toxictool_bench/recalibrate_author_audit.py
python3 toxictool_bench/plot_paper_figures.py --preview-dir /tmp/toxicbench-figures
python3 toxictool_bench/run_full_bench.py --tasks toxictool_bench/tasks/semantic_schema_iclr2027.jsonl --adapter langgraph_react_full --model gpt-5.4-mini --env both --limit 1
MODEL=claude-haiku-4-5-20251001 bash toxictool_bench/run_full_verification_stress.sh
python3 toxictool_bench/bootstrap_ci.py toxictool_bench/results/RESULT_1.jsonl --output toxictool_bench/results/bootstrap_ci.csv
python3 toxictool_bench/check_paper_static.py --main main.tex
python3 -m pytest toxictool_bench/tests -q
```

Framework adapters that depend on local third-party checkouts use `TOXICTOOL_BASELINE_DIR=/path/to/baseline_agent`. API keys and endpoint configuration must be supplied through local ignored files or environment variables.

## Security and Anonymization Notes

The repository ignores local secrets:

```text
api
.env
.env.*
```

Before preparing an anonymous submission package, verify that the public archive does not contain local paths, API keys, or private endpoint configuration. The current paper text uses anonymous authors and does not require the ignored `api` file.

Bootstrap scripts use fixed command-line seeds (default `13`), and probabilistic poisoning derives deterministic decisions from task/call identifiers. `artifact_sha256.csv` records release-file checksums. Code and synthetic benchmark data are covered by `LICENSE` and `DATA_LICENSE.md`.
