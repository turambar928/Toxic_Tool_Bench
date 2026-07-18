# ICLR Project Current Status

Last updated: 2026-07-17

## Current Stage

The project is now at the post-experiment audit and paper-integration stage.

The benchmark, full-agent adapters, numerical expanded experiments, semantic/schema cross-model experiments, rescoring pipeline, and paper result tables are in place. The next work should focus on defense ablations, semantic/retrieval case studies, and paper narrative tightening.

## Built Components

### ToxicTool-Bench

Location:

```text
paper/iclr/toxictool_bench/
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
paper/iclr/toxictool_bench/tasks/numerical.jsonl
```

Expanded task file:

```text
paper/iclr/toxictool_bench/tasks/numerical_expanded.jsonl
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
paper/iclr/toxictool_bench/tasks/semantic_schema.jsonl
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
- `data2mcp_dataframe`
- `data2mcp_dataframe_guarded`
- `data2mcp_dataframe_guarded_light`
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
paper/iclr/toxictool_bench/tests/test_evaluator.py
paper/iclr/toxictool_bench/tests/test_poisoners.py
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
- data2mcp
- PandasAI
- DA-Agent
- AutoGen

Main expanded result table is in:

```text
paper/iclr/EXPERIMENT_RESULTS.md
paper/iclr/sections/05_experiments.tex
```

Semantic/schema 24-task suite is also complete on the five practical-speed adapters.

### claude-sonnet-4-6

Completed on 5 full adapters:

- LangGraph
- smolagents
- data2mcp
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
- data2mcp
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
paper/iclr/toxictool_bench/results/cross_model_summary.csv
```

Poison-type breakdown:

```text
paper/iclr/toxictool_bench/results/poison_type_summary.csv
```

Semantic/schema summary:

```text
paper/iclr/toxictool_bench/results/semantic_schema_summary.csv
paper/iclr/toxictool_bench/results/semantic_schema_poison_summary.csv
paper/iclr/toxictool_bench/results/semantic_schema_cross_model_summary.csv
paper/iclr/toxictool_bench/results/semantic_schema_cross_model_poison_summary.csv
```

Detailed Markdown report:

```text
paper/iclr/EXPERIMENT_RESULTS.md
paper/iclr/PILOT_RESULTS.md
```

LaTeX experiment section:

```text
paper/iclr/sections/05_experiments.tex
```

Benchmark section:

```text
paper/iclr/sections/03_toxictool_bench.tex
```

Case-study extraction:

```text
paper/iclr/toxictool_bench/extract_case_studies.py
paper/iclr/CASE_STUDIES.md
paper/iclr/sections/06_qualitative_analysis.tex
```

Progress report:

```text
paper/iclr/PROGRESS_REPORT.md
paper/iclr/NEXT_EXPERIMENT_PLAN.md
```

## Verification

Latest checks:

```text
python3 -m pytest paper/iclr/toxictool_bench/tests -q
python3 -m compileall -q paper/iclr/toxictool_bench
```

Result:

```text
12 passed
compileall passed
```

## Current Findings

High-level findings from completed runs:

- Poisoned TSR is consistently below clean TSR for high-performing agents.
- The semantic/schema suite shows large drops for `data2mcp_dataframe` and `pandasai_dataframe` under `gpt-5.4-mini`.
- Rank swaps are the most dangerous poison type by average BCR.
- Aggregate scaling is also damaging and often directly copied.
- Sign flips are easier to detect or recover from.
- PandasAI remains highly vulnerable under the current coarse poisoning setup.
- DA-Agent shows higher validation/recovery on `gpt-5.4-mini`, but is too slow for current cross-model batching.
- data2mcp performance depends strongly on model choice; Qwen often hits max-turn behavior in the current router setup.
- The guarded `data2mcp` semantic/schema ablation reduces BCR from 0.62 to 0.00 and raises poisoned TSR from 0.29 to 0.83, with a clean TSR tradeoff from 0.92 to 0.83.
- The light guarded semantic/schema ablation also keeps BCR at 0.00, but poisoned TSR is lower at 0.71.
- The guarded `data2mcp` numerical ablation reduces BCR from 0.24 to 0.00, raises clean TSR from 0.65 to 0.79, and raises poisoned TSR from 0.47 to 0.74.
- The light guarded numerical ablation also keeps BCR at 0.00, but clean/toxic TSR are lower at 0.68/0.65.
- Guarded overhead and case-study artifacts have been generated:
  - `paper/iclr/toxictool_bench/results/data2mcp_guarded_overhead_summary.csv`
  - `paper/iclr/GUARDED_CASE_STUDIES.md`
- Bootstrap CI artifacts have been generated:
  - `paper/iclr/toxictool_bench/results/numerical_gpt_bootstrap_ci.csv`
  - `paper/iclr/toxictool_bench/results/numerical_cross_model_bootstrap_ci.csv`
  - `paper/iclr/toxictool_bench/results/semantic_schema_cross_model_bootstrap_ci.csv`
  - `paper/iclr/toxictool_bench/results/data2mcp_guarded_bootstrap_ci.csv`

Poison-type averages across completed cross-model runs:

```text
rank_swap:       average BCR 0.52
aggregate_scale: average BCR 0.41
sign_flip:      average BCR 0.11
```

## Remaining Work

### Paper analysis

- Case-study extraction is implemented and `CASE_STUDIES.md` has been generated from final rescored expanded results.
- Representative cases have been converted into a first qualitative-analysis draft in `sections/06_qualitative_analysis.tex`.
- `EXPERIMENT_RESULTS.md` now contains only formal expanded/cross-model results; early 4-task pilot results are archived in `PILOT_RESULTS.md`.
- Next paper task is to compress those examples for the final main text and move excess detail to appendix.
- Tighten introduction around the central claim:
  - successful tool execution is not equivalent to trustworthy tool evidence.

### Benchmark expansion

The benchmark now has a 24-task semantic/schema expansion in addition to the numerical suite, and semantic/schema cross-model runs are complete. Remaining missing families:

- instruction/data-content poisoning
- multi-step report tasks

Next experimental step:

- Review final narrative and optional reruns; abstract/introduction/method now frame the paper as benchmark evidence plus guarded-verification defense.

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
