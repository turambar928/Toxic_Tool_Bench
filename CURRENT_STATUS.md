# ICLR Project Current Status

Last updated: 2026-07-19

## Current Stage

The project is now at the submission-package and release-cleanup stage.

The benchmark, full-agent adapters, numerical expanded experiments, semantic/schema cross-model experiments, GPT-only 120-task expanded cross-agent pass, rescoring pipeline, guarded DataFrame Router defense ablations, bootstrap confidence intervals, case studies, paper skeleton, and GitHub README are in place. The next work should focus on final PDF compilation, page-budget control, citation polish, and release-package verification.

## Built Components

### ToxicBench

Location:

```text
toxictool_bench/
```

Implemented components:

- Paired clean/toxic task runner.
- Tool-observation poisoning through `DataToolEnv`.
- Poisoning operators:
  - `aggregate_scale`
  - `sign_flip`
  - `rank_swap`
  - `label_swap`
  - `treatment_control_flip`
  - `column_semantic_swap`
  - `stale_metadata`
  - `biased_retrieval`
- Evaluator metrics:
  - Clean/poisoned TSR
  - Delta TSR
  - BCR
  - ADR
  - VR
  - RR
- Rescoring script:
  - `rescore_results.py`
- Summary script:
  - `summarize_results.py`
- Expanded run script:
  - `run_expanded_full_adapters.sh`

### Task Suite

Pilot task file:

```text
toxictool_bench/tasks/numerical.jsonl
```

Expanded task file:

```text
toxictool_bench/tasks/numerical_expanded.jsonl
```

Current expanded suite:

- 34 tasks
- 11 CSV datasets
- Numerical/data-analysis tasks covering:
  - means and totals
  - growth rates
  - group rankings
  - per-unit ratios
  - retention rates
  - defect rates
  - support queue statistics

Semantic/schema expansion:

```text
toxictool_bench/tasks/semantic_schema.jsonl
```

Current semantic/schema suite:

- 24 tasks
- 14 CSV datasets
- `gpt-5.4-mini`, `claude-sonnet-4-6`, and `Qwen3.6-35B-A3B-no-thinking` practical-speed adapter runs completed
- Poisoning operators:
  - `label_swap`
  - `treatment_control_flip`
  - `column_semantic_swap`
  - `stale_metadata`
  - `biased_retrieval`

### Full Framework Adapters

Implemented full adapters:

- `langgraph_react_full`
- `smolagents_toolcalling`
- `dataframe_router`
- `dataframe_router_guarded`
- `dataframe_router_guarded_light`
- `pandasai_dataframe`
- `da_agent_full`
- `autogen_tool_agent`

Important limitation:

- `pandasai_dataframe` runs the full PandasAI agent, but poisoning is applied at the chat-result boundary rather than at an internal code-execution observation boundary.

## Metric Audit Completed

The evaluator was audited after cross-model runs.

Issue found:

- BCR could be nonzero in clean runs if a wrong clean answer happened to match the poisoned answer string.

Fix:

- BCR is now only true when a poisoned observation was actually returned in the run.
- Clean-environment BCR is therefore always zero and is not used as a paper signal.

Regression tests:

```text
toxictool_bench/tests/test_evaluator.py
toxictool_bench/tests/test_poisoners.py
```

Current test result:

```text
12 passed
```

Additional poisoner fix:

- `rank_swap` now uses label-boundary replacement.
- This prevents single-letter labels such as `E` from being replaced inside ordinary words such as `defects`.

## Experiments Completed

### gpt-5.4-mini

Completed on all 6 full adapters:

- LangGraph
- smolagents
- DataFrame Router
- PandasAI
- DA-Agent
- AutoGen

Main expanded result table is in:

```text
EXPERIMENT_RESULTS.md
sections/05_experiments.tex
```

Semantic/schema 24-task suite is also complete on the five practical-speed adapters.

GPT-only expanded cross-agent pass completed on 120 ICLR 2027 candidate tasks:

- 60 numerical tasks
- 60 semantic/schema tasks
- LangGraph
- smolagents
- DataFrame Router
- AutoGen

Combined summary:

```text
toxictool_bench/results/iclr2027_gpt_expanded_cross_agent_combined_summary.csv
```

### claude-sonnet-4-6

Completed on 5 full adapters:

- LangGraph
- smolagents
- DataFrame Router
- PandasAI
- AutoGen

Semantic/schema 24-task suite is also complete on the same five adapters.

Not completed:

- DA-Agent

Reason:

- DA-Agent on Claude was manually stopped after 5/68 environment instances because the run was too slow for the cross-model batch.

### Qwen3.6-35B-A3B-no-thinking

Completed on 5 full adapters:

- LangGraph
- smolagents
- DataFrame Router
- PandasAI
- AutoGen

Semantic/schema 24-task suite is also complete on the same five adapters.

Not completed:

- DA-Agent

Reason:

- DA-Agent was excluded after the Claude run showed impractical throughput.

Notes:

- The first Qwen attempt hit HTTP 429.
- `ChatClient` now retries 429/5xx errors with exponential backoff.
- After this fix, the Qwen non-DA batch completed.
- PandasAI/Qwen hit an internal PandasAI SQL validation exception during semantic/schema; the adapter now records per-task PandasAI exceptions as failed runs instead of aborting the whole batch.

## Current Result Artifacts

Overall cross-model summary:

```text
toxictool_bench/results/cross_model_summary.csv
```

Poison-type breakdown:

```text
toxictool_bench/results/poison_type_summary.csv
```

Semantic/schema summary:

```text
toxictool_bench/results/semantic_schema_summary.csv
toxictool_bench/results/semantic_schema_poison_summary.csv
toxictool_bench/results/semantic_schema_cross_model_summary.csv
toxictool_bench/results/semantic_schema_cross_model_poison_summary.csv
```

Detailed Markdown report:

```text
EXPERIMENT_RESULTS.md
PILOT_RESULTS.md
```

LaTeX experiment section:

```text
sections/05_experiments.tex
```

Benchmark section:

```text
sections/03_toxictool_bench.tex
```

Case-study extraction:

```text
toxictool_bench/extract_case_studies.py
CASE_STUDIES.md
sections/06_qualitative_analysis.tex
```

Progress report:

```text
PROGRESS_REPORT.md
NEXT_EXPERIMENT_PLAN.md
```

## Verification

Latest checks:

```text
python3 -m pytest toxictool_bench/tests -q
python3 -m compileall -q toxictool_bench
```

Result:

```text
12 passed
compileall passed
```

## Current Findings

High-level findings from completed runs:

- Poisoned TSR is consistently below clean TSR for high-performing agents.
- The semantic/schema suite shows large drops for `dataframe_router` and `pandasai_dataframe` under `gpt-5.4-mini`.
- Rank swaps are the most dangerous poison type by average BCR.
- Aggregate scaling is also damaging and often directly copied.
- Sign flips are easier to detect or recover from.
- PandasAI remains highly vulnerable under the current coarse poisoning setup.
- DA-Agent shows higher validation/recovery on `gpt-5.4-mini`, but is too slow for current cross-model batching.
- DataFrame Router performance depends strongly on model choice; Qwen often hits max-turn behavior in the current router setup.
- The guarded `DataFrame Router` semantic/schema ablation reduces BCR from 0.62 to 0.00 and raises poisoned TSR from 0.29 to 0.83, with a clean TSR tradeoff from 0.92 to 0.83.
- The light guarded semantic/schema ablation also keeps BCR at 0.00, but poisoned TSR is lower at 0.71.
- The guarded `DataFrame Router` numerical ablation reduces BCR from 0.24 to 0.00, raises clean TSR from 0.65 to 0.79, and raises poisoned TSR from 0.47 to 0.74.
- The light guarded numerical ablation also keeps BCR at 0.00, but clean/toxic TSR are lower at 0.68/0.65.
- Guarded overhead and case-study artifacts have been generated:
  - `toxictool_bench/results/dataframe_router_guarded_overhead_summary.csv`
  - `GUARDED_CASE_STUDIES.md`
- Bootstrap CI artifacts have been generated:
  - `toxictool_bench/results/numerical_gpt_bootstrap_ci.csv`
  - `toxictool_bench/results/numerical_cross_model_bootstrap_ci.csv`
  - `toxictool_bench/results/semantic_schema_cross_model_bootstrap_ci.csv`
  - `toxictool_bench/results/dataframe_router_guarded_bootstrap_ci.csv`

Poison-type averages across completed cross-model runs:

```text
rank_swap:       average BCR 0.52
aggregate_scale: average BCR 0.41
sign_flip:      average BCR 0.11
```

## Remaining Work

### Paper analysis

- Case-study extraction is implemented and `CASE_STUDIES.md` / `GUARDED_CASE_STUDIES.md` have been generated.
- Representative cases have been compressed into `sections/06_qualitative_analysis.tex`.
- Light-guard, overhead, bootstrap CI, and framework-boundary details are in `sections/08_appendix_guard_details.tex`.
- `main.tex` now provides the paper entry point and includes all sections.
- Related-work citations and `references.bib` are present.
- Remaining paper task: run the final LaTeX build with TeX installed and check ICLR page budget.

### Benchmark expansion

The benchmark now has a 24-task semantic/schema expansion in addition to the numerical suite, and semantic/schema cross-model runs are complete. Remaining missing families:

- instruction/data-content poisoning
- multi-step report tasks

Next experimental step:

- Do not run more large experiments by default. Only rerun if final CI/page-review exposes a specific weak claim.

### DA-Agent cross-model

Current recommendation:

- Do not block the main paper table on DA-Agent cross-model runs.
- Report DA-Agent on `gpt-5.4-mini`.
- Mention cross-model DA-Agent omission as a runtime limitation.

If needed later:

- Run DA-Agent cross-model separately with fewer tasks or a dedicated timeout/resume mechanism.

### Engineering cleanup

- Add a resume mode to `run_full_bench.py`.
- Add per-adapter timeout control.
- Add automatic rescore and summary generation after each full run.
- Optionally suppress AutoGen model-mismatch warnings in batch logs.
- Update external adapter setup instructions if publishing a fully reproducible release with third-party framework checkouts.
