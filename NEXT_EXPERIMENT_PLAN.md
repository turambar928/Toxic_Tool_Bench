# Next Experiment Plan

Last updated: 2026-07-17

## Goal

Move from the current first-round benchmark evidence to a stronger ICLR-ready experiment package.

Current completed evidence:

- 34-task numerical suite.
- 24-task semantic/schema suite.
- Full-adapter results for numerical tasks on `gpt-5.4-mini`.
- Cross-model numerical results on `gpt-5.4-mini`, `claude-sonnet-4-6`, and `Qwen3.6-35B-A3B-no-thinking` for practical-speed adapters.
- Cross-model semantic/schema results on `gpt-5.4-mini`, `claude-sonnet-4-6`, and `Qwen3.6-35B-A3B-no-thinking` for practical-speed adapters.

## Phase 1: Expand Semantic/Schema Tasks

Target size:

```text
20-30 semantic/schema tasks
```

Current size:

```text
24 tasks
```

Status: complete for the current round.

Implemented coverage:

- biased retrieval evidence
- conflicting metadata vs raw data
- stale documentation
- treatment/control inversion
- column meaning swap
- entity-label swap with plausible numeric evidence

Expected files:

```text
toxictool_bench/tasks/semantic_schema.jsonl
toxictool_bench/datasets/*.csv
toxictool_bench/poisoners.py
toxictool_bench/tests/test_poisoners.py
```

Acceptance checks:

```bash
python3 -m pytest toxictool_bench/tests -q
python3 -m compileall -q toxictool_bench
```

## Phase 2: Run Expanded Semantic/Schema Experiments

First model:

```text
gpt-5.4-mini
```

Adapters:

```text
langgraph_react_full
smolagents_toolcalling
data2mcp_dataframe
pandasai_dataframe
autogen_tool_agent
```

Command:

```bash
bash toxictool_bench/run_semantic_schema_full_adapters.sh gpt-5.4-mini
```

Status: complete for `gpt-5.4-mini`.

Current summary files:

```text
toxictool_bench/results/semantic_schema_summary.csv
toxictool_bench/results/semantic_schema_poison_summary.csv
```

For reruns, rescore and summarize the exact result files:

```bash
python3 toxictool_bench/rescore_results.py \
  --tasks toxictool_bench/tasks/semantic_schema.jsonl \
  RESULT_1.jsonl RESULT_2.jsonl RESULT_3.jsonl RESULT_4.jsonl RESULT_5.jsonl

python3 toxictool_bench/summarize_results.py \
  RESULT_1.rescored.jsonl RESULT_2.rescored.jsonl RESULT_3.rescored.jsonl RESULT_4.rescored.jsonl RESULT_5.rescored.jsonl \
  --overall-output toxictool_bench/results/semantic_schema_summary.csv \
  --poison-output toxictool_bench/results/semantic_schema_poison_summary.csv
```

Do not use wildcard result selection because failed or old runs may exist in the results directory.

## Phase 3: Cross-Model Semantic/Schema

Status: complete for the current round.

Models:

```text
gpt-5.4-mini
claude-sonnet-4-6
Qwen3.6-35B-A3B-no-thinking
```

Adapters:

```text
langgraph_react_full
smolagents_toolcalling
data2mcp_dataframe
pandasai_dataframe
autogen_tool_agent
```

DA-Agent remains GPT-only unless a timeout/resume mechanism is added.

Output files:

```text
toxictool_bench/results/semantic_schema_cross_model_summary.csv
toxictool_bench/results/semantic_schema_cross_model_poison_summary.csv
```

## Phase 4: Defense Ablation

Evaluate Guarded Verification as a structured wrapper, not only as a caution prompt.

Status: semantic/schema and numerical full/light guarded ablations complete for `data2mcp_dataframe`.

Core comparisons:

- base adapter
- adapter + expectation generation
- adapter + expectation generation + observation gating
- adapter + full validation/recovery policy

Metrics:

- clean TSR
- poisoned TSR
- delta TSR
- BCR
- ADR
- VR
- RR
- latency / token cost

Acceptance criterion:

```text
BCR decreases substantially without a large clean TSR drop.
```

Current result on the 24-task semantic/schema suite with `gpt-5.4-mini`:

| Adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR | Toxic VR | Toxic RR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `data2mcp_dataframe` | 0.92 | 0.29 | 0.62 | 0.62 | 0.00 | 0.00 |
| `data2mcp_dataframe_guarded` | 0.83 | 0.83 | 0.00 | 0.00 | 1.00 | 0.83 |
| `data2mcp_dataframe_guarded_light` | 0.83 | 0.71 | 0.12 | 0.00 | 1.00 | 0.71 |

Current result on the 34-task numerical suite with `gpt-5.4-mini`:

| Adapter | Clean TSR | Poisoned TSR | Delta TSR | Toxic BCR | Toxic VR | Toxic RR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `data2mcp_dataframe` | 0.65 | 0.47 | 0.18 | 0.24 | 0.03 | 0.09 |
| `data2mcp_dataframe_guarded` | 0.79 | 0.74 | 0.06 | 0.00 | 1.00 | 0.74 |
| `data2mcp_dataframe_guarded_light` | 0.68 | 0.65 | 0.03 | 0.00 | 1.00 | 0.65 |

Output files:

```text
toxictool_bench/results/data2mcp_guarded_semantic_ablation_summary.csv
toxictool_bench/results/data2mcp_guarded_semantic_ablation_poison_summary.csv
toxictool_bench/results/data2mcp_guarded_numerical_ablation_summary.csv
toxictool_bench/results/data2mcp_guarded_numerical_ablation_poison_summary.csv
```

## Phase 5: Paper Integration

Update:

```text
EXPERIMENT_RESULTS.md
sections/03_toxictool_bench.tex
sections/05_experiments.tex
sections/06_qualitative_analysis.tex
sections/07_discussion_limitations.tex
```

Add:

- semantic/schema cross-model table
- retrieval-poisoning breakdown
- 3-5 qualitative cases from semantic/retrieval tasks
- limitation paragraph for poisoning boundaries

## Immediate Next Step

Status: qualitative evidence and overhead summary generated for the current guard ablations.

Generated files:

```text
toxictool_bench/results/data2mcp_guarded_overhead_summary.csv
GUARDED_CASE_STUDIES.md
toxictool_bench/results/numerical_gpt_bootstrap_ci.csv
toxictool_bench/results/numerical_cross_model_bootstrap_ci.csv
toxictool_bench/results/semantic_schema_cross_model_bootstrap_ci.csv
toxictool_bench/results/data2mcp_guarded_bootstrap_ci.csv
```

## ICLR 2027 Expansion Track

If targeting ICLR 2027, the next experiments should use the expanded candidate suites:

```text
toxictool_bench/tasks/numerical_iclr2027.jsonl
toxictool_bench/tasks/semantic_schema_iclr2027.jsonl
```

Recommended order:

1. Run partial smoke tests for `data2mcp_dataframe`, `langgraph_react_full`, and `pandasai_dataframe`.
2. Generate severity summaries with `--severity-output` and check obvious/plausible/subtle trends.
3. Run full guard and light guard on the expanded candidate suites.
4. Only then expand to all adapters and cross-model runs.

Next actions:

1. Do a full paper consistency pass: symbols, section order, table references, appendix inclusion.
2. Run optional reruns only if final variance looks too wide for a key claim.
3. Prepare final ICLR submission package.
