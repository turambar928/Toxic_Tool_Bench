# ToxicTool-Bench Formal Experiment Results

Last updated: 2026-07-17

This file reports the formal expanded results used by the current paper draft. Early 4-task pilot runs have been moved to `PILOT_RESULTS.md` to avoid mixing development checks with the main experimental evidence.

## Experimental Scope

Task suite:

```text
paper/iclr/toxictool_bench/tasks/numerical_expanded.jsonl
```

The expanded suite contains 34 numerical/data-analysis tasks over 11 CSV datasets. It covers aggregate statistics, growth/sign calculations, rankings, ratios, retention rates, defect rates, and support-queue statistics.

Environments:

- `clean`: normal tool observations.
- `toxic`: selected tool observations silently poisoned while keeping the same interface and return format.

Full framework adapters:

- `langgraph_react_full`
- `smolagents_toolcalling`
- `data2mcp_dataframe`
- `pandasai_dataframe`
- `da_agent_full`
- `autogen_tool_agent`

Models:

- `gpt-5.4-mini`
- `claude-sonnet-4-6`
- `Qwen3.6-35B-A3B-no-thinking`

Important scope note:

- `da_agent_full` completed the expanded suite on `gpt-5.4-mini`.
- `da_agent_full` is excluded from the cross-model table because its Claude run was manually stopped after 5/68 environment instances due to slow throughput.
- `pandasai_dataframe` runs the full PandasAI agent, but poisoning is currently applied at the chat-result boundary rather than at an internal code-execution observation boundary.

## Scoring Notes

Current metrics:

- Clean TSR: task success rate in the clean environment.
- Poisoned TSR: task success rate in the toxic environment.
- Delta TSR: Clean TSR minus Poisoned TSR.
- BCR: blind compliance rate, counted only when a poisoned observation was actually returned.
- ADR: anomaly detection rate.
- VR: validation rate.
- RR: recovery rate.

Metric audit:

- BCR was fixed after cross-model runs so clean-environment BCR cannot be nonzero merely because a wrong clean answer matches a poisoned answer string.
- `rank_swap` was fixed to use label-boundary replacement, so single-letter labels such as `E` are not rewritten inside words such as `defects`.
- The original cross-model tables below use the final `.rescored.jsonl` files.

## GPT-Only Expanded Cross-Agent Results: 120 Tasks

This pass was added to strengthen the scale of the cross-agent evidence beyond the initial 34-task numerical and 24-task semantic/schema suites. It runs four practical-speed full adapters on the ICLR 2027 candidate suites:

- 60 numerical tasks
- 60 semantic/schema tasks
- `gpt-5.4-mini`
- clean/toxic paired environments

Combined 120-task summary:

| Full adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR | Toxic ADR | Toxic VR | Toxic RR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `langgraph_react_full` | 0.93 | 0.60 | 0.33 | 0.33 | 0.07 | 0.43 | 0.44 |
| `smolagents_toolcalling` | 0.91 | 0.55 | 0.36 | 0.38 | 0.00 | 0.10 | 0.10 |
| `data2mcp_dataframe` | 0.77 | 0.48 | 0.28 | 0.37 | 0.16 | 0.22 | 0.23 |
| `autogen_tool_agent` | 0.92 | 0.65 | 0.27 | 0.20 | 0.06 | 0.45 | 0.37 |

Suite-level summaries:

```text
toxictool_bench/results/iclr2027_gpt_expanded_cross_agent_numerical_summary.csv
toxictool_bench/results/iclr2027_gpt_expanded_cross_agent_semantic_schema_summary.csv
toxictool_bench/results/iclr2027_gpt_expanded_cross_agent_combined_summary.csv
```

Raw result files:

```text
toxictool_bench/results/20260721-145704_langgraph_react_full_gpt-5.4-mini_both.jsonl
toxictool_bench/results/20260721-152956_smolagents_toolcalling_gpt-5.4-mini_both.jsonl
toxictool_bench/results/20260721-155522_data2mcp_dataframe_gpt-5.4-mini_both.jsonl
toxictool_bench/results/20260721-172417_autogen_tool_agent_gpt-5.4-mini_both.jsonl
toxictool_bench/results/20260721-182010_langgraph_react_full_gpt-5.4-mini_both.jsonl
toxictool_bench/results/20260721-184737_smolagents_toolcalling_gpt-5.4-mini_both.jsonl
toxictool_bench/results/20260721-191227_data2mcp_dataframe_gpt-5.4-mini_both.jsonl
toxictool_bench/results/20260721-203945_autogen_tool_agent_gpt-5.4-mini_both.jsonl
```

## Main Expanded Results: gpt-5.4-mini

| Full adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR | Toxic ADR | Toxic VR | Toxic RR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `langgraph_react_full` | 1.00 | 0.41 | 0.59 | 0.68 | 0.00 | 0.00 | 0.00 |
| `smolagents_toolcalling` | 0.97 | 0.62 | 0.35 | 0.32 | 0.00 | 0.15 | 0.15 |
| `data2mcp_dataframe` | 0.65 | 0.47 | 0.18 | 0.24 | 0.12 | 0.03 | 0.09 |
| `pandasai_dataframe` | 1.00 | 0.47 | 0.53 | 0.65 | 0.00 | 0.00 | 0.00 |
| `da_agent_full` | 0.85 | 0.53 | 0.32 | 0.32 | 0.06 | 0.38 | 0.38 |
| `autogen_tool_agent` | 0.97 | 0.56 | 0.41 | 0.47 | 0.03 | 0.00 | 0.00 |

Result files:

```text
paper/iclr/toxictool_bench/results/20260707-133726_langgraph_react_full_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-134758_smolagents_toolcalling_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-122940_data2mcp_dataframe_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-130327_pandasai_dataframe_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-130859_da_agent_full_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-124859_autogen_tool_agent_gpt-5.4-mini_both.rescored.jsonl
```

## Cross-Model Expanded Results

Cross-model runs use the same 34-task expanded set. `da_agent_full` is omitted from these two tables for throughput reasons, as noted above.

### claude-sonnet-4-6

| Full adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR | Toxic ADR | Toxic VR | Toxic RR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `langgraph_react_full` | 0.88 | 0.76 | 0.12 | 0.18 | 0.06 | 0.18 | 0.18 |
| `smolagents_toolcalling` | 1.00 | 0.82 | 0.18 | 0.12 | 0.03 | 0.50 | 0.50 |
| `data2mcp_dataframe` | 0.85 | 0.62 | 0.24 | 0.24 | 0.26 | 0.50 | 0.53 |
| `pandasai_dataframe` | 0.97 | 0.32 | 0.65 | 0.76 | 0.00 | 0.00 | 0.00 |
| `autogen_tool_agent` | 0.91 | 0.82 | 0.09 | 0.24 | 0.09 | 0.15 | 0.15 |

Result files:

```text
paper/iclr/toxictool_bench/results/20260707-160205_langgraph_react_full_claude-sonnet-4-6_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-161144_smolagents_toolcalling_claude-sonnet-4-6_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-162340_data2mcp_dataframe_claude-sonnet-4-6_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-170254_pandasai_dataframe_claude-sonnet-4-6_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-171009_autogen_tool_agent_claude-sonnet-4-6_both.rescored.jsonl
```

### Qwen3.6-35B-A3B-no-thinking

The first Qwen attempt hit `HTTP 429`; after adding retry/backoff to `ChatClient`, the non-DA adapters completed.

| Full adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR | Toxic ADR | Toxic VR | Toxic RR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `langgraph_react_full` | 1.00 | 0.44 | 0.56 | 0.59 | 0.00 | 0.06 | 0.06 |
| `smolagents_toolcalling` | 0.82 | 0.65 | 0.18 | 0.18 | 0.03 | 0.18 | 0.18 |
| `data2mcp_dataframe` | 0.32 | 0.24 | 0.09 | 0.06 | 0.03 | 0.35 | 0.09 |
| `pandasai_dataframe` | 1.00 | 0.26 | 0.74 | 0.76 | 0.00 | 0.00 | 0.00 |
| `autogen_tool_agent` | 0.94 | 0.76 | 0.18 | 0.29 | 0.03 | 0.32 | 0.29 |

Result files:

```text
paper/iclr/toxictool_bench/results/20260707-180904_langgraph_react_full_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-181347_smolagents_toolcalling_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-185704_data2mcp_dataframe_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-191325_pandasai_dataframe_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260707-191533_autogen_tool_agent_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl
```

## Poison-Type Breakdown

Machine-readable summary:

```text
paper/iclr/toxictool_bench/results/poison_type_summary.csv
```

Across completed cross-model runs:

| Poison type | Average BCR | Interpretation |
| --- | ---: | --- |
| `rank_swap` | 0.52 | Most likely to induce blind compliance because values remain plausible while entity labels change. |
| `aggregate_scale` | 0.41 | Often copied directly when the poisoned aggregate is returned as a clean-looking scalar. |
| `sign_flip` | 0.11 | Easier to detect or recover from; average recovery is 0.28. |

## Semantic/Schema Expansion Results

The semantic/schema expansion now contains 24 tasks over 14 CSV datasets. It covers treatment/control label flips, schema column swaps, stale data-dictionary metadata, and biased retrieval evidence. It has now completed on the five practical-speed adapters across `gpt-5.4-mini`, `claude-sonnet-4-6`, and `Qwen3.6-35B-A3B-no-thinking`.

### gpt-5.4-mini

| Full adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR | Toxic ADR | Toxic VR | Toxic RR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `langgraph_react_full` | 1.00 | 0.79 | 0.21 | 0.21 | 0.00 | 0.75 | 0.75 |
| `smolagents_toolcalling` | 1.00 | 0.46 | 0.54 | 0.50 | 0.00 | 0.04 | 0.00 |
| `data2mcp_dataframe` | 0.92 | 0.29 | 0.62 | 0.62 | 0.00 | 0.00 | 0.00 |
| `pandasai_dataframe` | 1.00 | 0.25 | 0.75 | 0.75 | 0.00 | 0.00 | 0.00 |
| `autogen_tool_agent` | 1.00 | 0.71 | 0.29 | 0.21 | 0.04 | 0.75 | 0.67 |

### claude-sonnet-4-6

| Full adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR | Toxic ADR | Toxic VR | Toxic RR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `langgraph_react_full` | 1.00 | 0.96 | 0.04 | 0.00 | 0.00 | 0.79 | 0.75 |
| `smolagents_toolcalling` | 1.00 | 0.71 | 0.29 | 0.25 | 0.00 | 0.46 | 0.42 |
| `data2mcp_dataframe` | 1.00 | 0.46 | 0.54 | 0.54 | 0.08 | 0.25 | 0.25 |
| `pandasai_dataframe` | 1.00 | 0.29 | 0.71 | 0.75 | 0.00 | 0.00 | 0.00 |
| `autogen_tool_agent` | 1.00 | 0.96 | 0.04 | 0.38 | 0.12 | 0.54 | 0.58 |

### Qwen3.6-35B-A3B-no-thinking

| Full adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR | Toxic ADR | Toxic VR | Toxic RR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `langgraph_react_full` | 1.00 | 0.79 | 0.21 | 0.21 | 0.00 | 0.75 | 0.75 |
| `smolagents_toolcalling` | 1.00 | 0.46 | 0.54 | 0.38 | 0.00 | 0.21 | 0.04 |
| `data2mcp_dataframe` | 0.54 | 0.33 | 0.21 | 0.04 | 0.12 | 0.62 | 0.33 |
| `pandasai_dataframe` | 0.83 | 0.21 | 0.62 | 0.67 | 0.00 | 0.00 | 0.00 |
| `autogen_tool_agent` | 1.00 | 0.75 | 0.25 | 0.25 | 0.12 | 0.54 | 0.58 |

Result files:

```text
paper/iclr/toxictool_bench/results/20260717-151320_langgraph_react_full_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-152215_smolagents_toolcalling_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-152700_data2mcp_dataframe_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-154035_pandasai_dataframe_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-154417_autogen_tool_agent_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-174634_langgraph_react_full_claude-sonnet-4-6_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-175313_smolagents_toolcalling_claude-sonnet-4-6_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-175813_data2mcp_dataframe_claude-sonnet-4-6_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-181538_pandasai_dataframe_claude-sonnet-4-6_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-181929_autogen_tool_agent_claude-sonnet-4-6_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-183020_langgraph_react_full_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-183447_smolagents_toolcalling_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-184710_data2mcp_dataframe_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-193637_pandasai_dataframe_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-193925_autogen_tool_agent_Qwen3.6-35B-A3B-no-thinking_both.rescored.jsonl
```

Machine-readable summaries:

```text
paper/iclr/toxictool_bench/results/semantic_schema_summary.csv
paper/iclr/toxictool_bench/results/semantic_schema_poison_summary.csv
paper/iclr/toxictool_bench/results/semantic_schema_cross_model_summary.csv
paper/iclr/toxictool_bench/results/semantic_schema_cross_model_poison_summary.csv
```

Semantic/schema takeaways:

1. Semantic poisoning is at least as damaging as numerical poisoning for some adapters. `data2mcp_dataframe` and `pandasai_dataframe` have large poisoned TSR drops and high BCR.
2. Cross-model behavior is not monotonic. Claude makes LangGraph more robust on semantic/schema tasks, but AutoGen still shows nontrivial blind compliance despite high poisoned TSR.
3. Biased retrieval is represented explicitly. LangGraph tends to recover via validation, while weaker tool-use integrations often either copy biased evidence or fail to validate.
4. Stale metadata and label flips remain damaging for smolagents, data2mcp, and PandasAI; LangGraph and AutoGen recover more often through validation.

## Guarded data2mcp Ablation

We implemented a guarded `data2mcp` adapter that runs a two-pass expectation/check/recovery policy:

1. Generate task-specific expectations about columns, labels, entity bindings, and evidence rows.
2. Run the normal `data2mcp_dataframe` route.
3. Run an independent verification route that recomputes or re-inspects the dataframe before finalizing.
4. Use the verified answer as final output and mark the trajectory as validated/recomputed.

Completed semantic/schema ablation:

```text
paper/iclr/toxictool_bench/tasks/semantic_schema.jsonl
model: gpt-5.4-mini
```

| Adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR | Toxic ADR | Toxic VR | Toxic RR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `data2mcp_dataframe` | 0.92 | 0.29 | 0.62 | 0.62 | 0.00 | 0.00 | 0.00 |
| `data2mcp_dataframe_guarded` | 0.83 | 0.83 | 0.00 | 0.00 | 1.00 | 1.00 | 0.83 |
| `data2mcp_dataframe_guarded_light` | 0.83 | 0.71 | 0.12 | 0.00 | 1.00 | 1.00 | 0.71 |

Result files:

```text
paper/iclr/toxictool_bench/results/20260717-152700_data2mcp_dataframe_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260717-214348_data2mcp_dataframe_guarded_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260718-153208_data2mcp_dataframe_guarded_light_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/data2mcp_guarded_semantic_ablation_summary.csv
paper/iclr/toxictool_bench/results/data2mcp_guarded_semantic_ablation_poison_summary.csv
```

Interpretation:

1. Guarding eliminates blind compliance on this semantic/schema run: BCR drops from 0.62 to 0.00.
2. Poisoned TSR improves from 0.29 to 0.83 and recovery rises from 0.00 to 0.83.
3. The tradeoff is a clean TSR drop from 0.92 to 0.83, caused by several validation-pass max-turn or over-analysis failures.
4. This is the first positive defense result and should be followed by numerical-suite ablations and lighter-weight guard variants.

Completed numerical ablation:

```text
paper/iclr/toxictool_bench/tasks/numerical_expanded.jsonl
model: gpt-5.4-mini
```

| Adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR | Toxic ADR | Toxic VR | Toxic RR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `data2mcp_dataframe` | 0.65 | 0.47 | 0.18 | 0.24 | 0.12 | 0.03 | 0.09 |
| `data2mcp_dataframe_guarded` | 0.79 | 0.74 | 0.06 | 0.00 | 1.00 | 1.00 | 0.74 |
| `data2mcp_dataframe_guarded_light` | 0.68 | 0.65 | 0.03 | 0.00 | 1.00 | 1.00 | 0.65 |

Numerical result files:

```text
paper/iclr/toxictool_bench/results/20260707-122940_data2mcp_dataframe_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260718-003358_data2mcp_dataframe_guarded_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/20260718-160351_data2mcp_dataframe_guarded_light_gpt-5.4-mini_both.rescored.jsonl
paper/iclr/toxictool_bench/results/data2mcp_guarded_numerical_ablation_summary.csv
paper/iclr/toxictool_bench/results/data2mcp_guarded_numerical_ablation_poison_summary.csv
```

Numerical interpretation:

1. The guarded route eliminates observed blind compliance on the 34-task numerical suite: BCR drops from 0.24 to 0.00.
2. Unlike the semantic/schema run, numerical clean TSR improves from 0.65 to 0.79 because the verification pass also corrects some ordinary data2mcp tool-use failures.
3. Poisoned TSR improves from 0.47 to 0.74 and RR rises from 0.09 to 0.74.
4. The main remaining cost is latency: full guarded mode roughly doubles data2mcp routing work because it always performs an independent verification pass.

Light-guard interpretation:

1. The 5-turn light guard also drives observed BCR to 0.00 on both suites.
2. It loses task success relative to full guard: semantic poisoned TSR drops from 0.83 to 0.71, and numerical poisoned TSR drops from 0.74 to 0.65.
3. The current light budget is therefore too aggressive for the main defense result, but useful as an overhead/robustness tradeoff ablation.

Overhead and case-study artifacts:

```text
paper/iclr/toxictool_bench/results/data2mcp_guarded_overhead_summary.csv
paper/iclr/GUARDED_CASE_STUDIES.md
```

## Main Takeaways

1. High clean TSR does not imply poisoned robustness. LangGraph, PandasAI, and AutoGen all have high clean TSR under `gpt-5.4-mini`, but their poisoned TSR drops sharply.
2. Rank swaps are particularly damaging because they preserve plausible numbers while corrupting the binding between an entity and its statistic.
3. PandasAI is highly vulnerable in the current coarse poisoning setup, especially when the poisoned chat result is directly used as the final analytical answer.
4. DA-Agent shows more validation and recovery on `gpt-5.4-mini`, but current throughput makes cross-model DA-Agent runs impractical without a dedicated resume/timeout mechanism.
5. `data2mcp` is sensitive to model/tool-use behavior; under Qwen, many runs hit max-turn behavior and clean TSR is low.
6. A guarded `data2mcp` verification policy substantially reduces blind compliance on both semantic/schema and numerical suites; the main remaining tradeoff is validation-pass overhead and occasional over-analysis.

## Additional Artifacts

Cross-model summary:

```text
paper/iclr/toxictool_bench/results/cross_model_summary.csv
paper/iclr/toxictool_bench/results/numerical_cross_model_bootstrap_ci.csv
```

Qualitative cases:

```text
paper/iclr/CASE_STUDIES.md
paper/iclr/GUARDED_CASE_STUDIES.md
paper/iclr/sections/06_qualitative_analysis.tex
```

Bootstrap confidence intervals:

```text
paper/iclr/toxictool_bench/results/numerical_gpt_bootstrap_ci.csv
paper/iclr/toxictool_bench/results/numerical_cross_model_bootstrap_ci.csv
paper/iclr/toxictool_bench/results/semantic_schema_cross_model_bootstrap_ci.csv
paper/iclr/toxictool_bench/results/data2mcp_guarded_bootstrap_ci.csv
```

Pilot archive:

```text
paper/iclr/PILOT_RESULTS.md
```
