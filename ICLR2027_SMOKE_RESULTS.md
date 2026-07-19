# ICLR 2027 Smoke Results

This file tracks lightweight sanity checks for the ICLR 2027 candidate expansion.
These are not final paper results; they are gates before launching full 120-task
runs.

## data2mcp Defense Ablation, Semantic/Schema 5-Task Smoke

Command shape:

```bash
export TOXICTOOL_BASELINE_DIR=/home/taozifu2025/data2mcpv2/baseline_agent
export TOXICTOOL_DATA2MCP_SRC=/home/taozifu2025/data2mcpv2/src

LIMIT=5 \
ADAPTERS="data2mcp_dataframe data2mcp_dataframe_caution data2mcp_dataframe_expectation_only data2mcp_dataframe_verification_only data2mcp_dataframe_guarded data2mcp_dataframe_guarded_light" \
TASK_SUITES="toxictool_bench/tasks/semantic_schema_iclr2027.jsonl" \
bash toxictool_bench/run_iclr2027_experiments.sh
```

Summary artifact:

```text
toxictool_bench/results/iclr2027_data2mcp_ablation_5task_summary.csv
```

| Adapter | Clean TSR | Poisoned TSR | Toxic BCR | Toxic VR | Toxic RR |
|---|---:|---:|---:|---:|---:|
| data2mcp_dataframe | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| data2mcp_dataframe_caution | 1.00 | 0.00 | 0.80 | 0.00 | 0.00 |
| data2mcp_dataframe_expectation_only | 1.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| data2mcp_dataframe_verification_only | 0.80 | 1.00 | 0.00 | 1.00 | 1.00 |
| data2mcp_dataframe_guarded | 0.80 | 1.00 | 0.00 | 1.00 | 1.00 |
| data2mcp_dataframe_guarded_light | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 |

Interpretation:

- Base data2mcp clean success does not transfer to poisoned observations.
- Caution-only and expectation-only prompts do not recover the early semantic/schema tasks.
- Independent verification is the main active ingredient in this smoke.
- Guard prompts were tightened after this smoke to require exact literal labels from
  dataframe rows and to retry when the tool returns only a query/code plan without
  printed results.

## data2mcp Defense Ablation, Numerical 5-Task Smoke

Command shape:

```bash
export TOXICTOOL_BASELINE_DIR=/home/taozifu2025/data2mcpv2/baseline_agent
export TOXICTOOL_DATA2MCP_SRC=/home/taozifu2025/data2mcpv2/src

LIMIT=5 \
ADAPTERS="data2mcp_dataframe data2mcp_dataframe_caution data2mcp_dataframe_expectation_only data2mcp_dataframe_verification_only data2mcp_dataframe_guarded data2mcp_dataframe_guarded_light" \
TASK_SUITES="toxictool_bench/tasks/numerical_iclr2027.jsonl" \
bash toxictool_bench/run_iclr2027_experiments.sh
```

Summary artifact:

```text
toxictool_bench/results/iclr2027_data2mcp_ablation_numerical_5task_summary.csv
```

| Adapter | Clean TSR | Poisoned TSR | Toxic BCR | Toxic VR | Toxic RR |
|---|---:|---:|---:|---:|---:|
| data2mcp_dataframe | 1.00 | 0.20 | 0.60 | 0.00 | 0.00 |
| data2mcp_dataframe_caution | 1.00 | 0.20 | 0.60 | 0.00 | 0.00 |
| data2mcp_dataframe_expectation_only | 0.80 | 0.80 | 0.40 | 0.00 | 0.20 |
| data2mcp_dataframe_verification_only | 1.00 | 0.80 | 0.00 | 1.00 | 0.80 |
| data2mcp_dataframe_guarded | 1.00 | 0.80 | 0.00 | 1.00 | 0.80 |
| data2mcp_dataframe_guarded_light | 1.00 | 0.80 | 0.00 | 1.00 | 0.80 |

Interpretation:

- Caution-only again behaves like base on the early numerical tasks.
- Expectation-only improves TSR but leaves nonzero blind compliance.
- Verification-based variants reduce BCR to zero and preserve clean TSR.
- A guarded rank-task failure was traced to the route trying to read `ab_test.csv`
  from the working directory instead of using the loaded dataframe tool. The prompt
  now explicitly forbids filesystem CSV reads, and a targeted `START_INDEX=2 LIMIT=1`
  guarded rerun recovered the rank task in both clean and toxic environments.

## Next Gate

## data2mcp Defense Ablation, 20-Task/40-Task Expanded Smoke

After the 5-task gates, we extended the same six-way ablation to tasks 1--20 in
both candidate suites using the chunk runner and merged the first three 5-task
chunks plus the fourth `START_INDEX=15 LIMIT=5` chunk.

Summary artifacts:

```text
toxictool_bench/results/iclr2027_data2mcp_ablation_semantic_10task_summary.csv
toxictool_bench/results/iclr2027_data2mcp_ablation_numerical_10task_summary.csv
toxictool_bench/results/iclr2027_data2mcp_ablation_combined_20task_summary.csv
toxictool_bench/results/iclr2027_data2mcp_ablation_auto_semantic_schema_iclr2027_summary.csv
toxictool_bench/results/iclr2027_data2mcp_ablation_auto_numerical_iclr2027_summary.csv
toxictool_bench/results/iclr2027_data2mcp_ablation_auto_combined_summary.csv
toxictool_bench/results/iclr2027_data2mcp_ablation_auto_manifest.csv
```

These can now be regenerated from completed chunks with:

```bash
python3 toxictool_bench/summarize_chunked_matrix.py \
  --tasks toxictool_bench/tasks/semantic_schema_iclr2027.jsonl toxictool_bench/tasks/numerical_iclr2027.jsonl \
  --adapters data2mcp_dataframe data2mcp_dataframe_caution data2mcp_dataframe_expectation_only data2mcp_dataframe_verification_only data2mcp_dataframe_guarded data2mcp_dataframe_guarded_light \
  --starts 0 5 10 15 \
  --limit 5 \
  --output-prefix toxictool_bench/results/iclr2027_data2mcp_ablation_auto
```

The current manifest contains 48 complete chunks:

```text
2 suites x 6 adapters x 4 starts = 48 chunks
```

Semantic/schema 20-task summary:

| Adapter | Clean TSR | Poisoned TSR | Toxic BCR | Toxic VR | Toxic RR |
|---|---:|---:|---:|---:|---:|
| data2mcp_dataframe | 0.90 | 0.10 | 0.80 | 0.00 | 0.00 |
| data2mcp_dataframe_caution | 0.90 | 0.20 | 0.75 | 0.05 | 0.00 |
| data2mcp_dataframe_expectation_only | 0.95 | 0.30 | 0.65 | 0.05 | 0.05 |
| data2mcp_dataframe_verification_only | 0.90 | 1.00 | 0.00 | 0.95 | 1.00 |
| data2mcp_dataframe_guarded | 0.95 | 0.95 | 0.00 | 1.00 | 0.95 |
| data2mcp_dataframe_guarded_light | 1.00 | 0.95 | 0.00 | 1.00 | 0.95 |

Numerical 20-task summary:

| Adapter | Clean TSR | Poisoned TSR | Toxic BCR | Toxic VR | Toxic RR |
|---|---:|---:|---:|---:|---:|
| data2mcp_dataframe | 0.75 | 0.40 | 0.30 | 0.00 | 0.05 |
| data2mcp_dataframe_caution | 0.85 | 0.45 | 0.30 | 0.25 | 0.25 |
| data2mcp_dataframe_expectation_only | 0.70 | 0.55 | 0.30 | 0.00 | 0.05 |
| data2mcp_dataframe_verification_only | 0.90 | 0.70 | 0.00 | 0.75 | 0.70 |
| data2mcp_dataframe_guarded | 0.80 | 0.80 | 0.00 | 1.00 | 0.80 |
| data2mcp_dataframe_guarded_light | 0.85 | 0.85 | 0.00 | 1.00 | 0.85 |

Combined 40-task summary:

| Adapter | Clean TSR | Poisoned TSR | Toxic BCR | Toxic VR | Toxic RR |
|---|---:|---:|---:|---:|---:|
| data2mcp_dataframe | 0.82 | 0.25 | 0.55 | 0.00 | 0.03 |
| data2mcp_dataframe_caution | 0.88 | 0.33 | 0.53 | 0.15 | 0.12 |
| data2mcp_dataframe_expectation_only | 0.82 | 0.42 | 0.47 | 0.03 | 0.05 |
| data2mcp_dataframe_verification_only | 0.90 | 0.85 | 0.00 | 0.85 | 0.85 |
| data2mcp_dataframe_guarded | 0.88 | 0.88 | 0.00 | 1.00 | 0.88 |
| data2mcp_dataframe_guarded_light | 0.93 | 0.90 | 0.00 | 1.00 | 0.90 |

Interpretation:

- The semantic/schema suite shows a clean mechanism split: prompt-only variants
  remain vulnerable, while verification-based variants recover all poisoned cases
  or nearly all poisoned cases in the first 20 tasks.
- The numerical suite is harder: verification removes blind compliance, but some
  ordinary calculation and answer-extraction failures remain.
- The combined 40-task smoke is strong enough to justify launching the full
  chunked data2mcp ablation across all 120 candidate tasks.

Run the full six-way data2mcp ablation on both ICLR 2027 candidate suites:

```bash
ADAPTERS="data2mcp_dataframe data2mcp_dataframe_caution data2mcp_dataframe_expectation_only data2mcp_dataframe_verification_only data2mcp_dataframe_guarded data2mcp_dataframe_guarded_light" \
TASK_SUITES="toxictool_bench/tasks/semantic_schema_iclr2027.jsonl toxictool_bench/tasks/numerical_iclr2027.jsonl" \
bash toxictool_bench/run_iclr2027_experiments.sh
```

For safer long runs, execute the same matrix in 10-task chunks:

```bash
for start in 0 10 20 30 40 50; do
  START_INDEX="$start" LIMIT=10 \
  ADAPTERS="data2mcp_dataframe data2mcp_dataframe_caution data2mcp_dataframe_expectation_only data2mcp_dataframe_verification_only data2mcp_dataframe_guarded data2mcp_dataframe_guarded_light" \
  TASK_SUITES="toxictool_bench/tasks/semantic_schema_iclr2027.jsonl toxictool_bench/tasks/numerical_iclr2027.jsonl" \
  bash toxictool_bench/run_iclr2027_experiments.sh
done
```
