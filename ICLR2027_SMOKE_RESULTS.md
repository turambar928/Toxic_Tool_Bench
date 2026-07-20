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

## data2mcp Defense Ablation, 110-Task Expanded Smoke

After the 5-task gates, we extended the same six-way ablation to tasks 1--30 in
both candidate suites, then added five more 5-task chunks from each suite. The
current merged smoke covers eleven 5-task chunks:
`START_INDEX=0,5,10,15,20,25,30,35,40,45,50`.

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
  --starts 0 5 10 15 20 25 30 35 40 45 50 \
  --limit 5 \
  --output-prefix toxictool_bench/results/iclr2027_data2mcp_ablation_auto
```

The current manifest contains 132 complete chunks:

```text
2 suites x 6 adapters x 11 starts = 132 chunks
```

Semantic/schema 55-task summary:

| Adapter | Clean TSR | Poisoned TSR | Toxic BCR | Toxic VR | Toxic RR |
|---|---:|---:|---:|---:|---:|
| data2mcp_dataframe | 0.96 | 0.53 | 0.60 | 0.15 | 0.25 |
| data2mcp_dataframe_caution | 0.87 | 0.58 | 0.51 | 0.33 | 0.35 |
| data2mcp_dataframe_expectation_only | 0.93 | 0.55 | 0.71 | 0.02 | 0.11 |
| data2mcp_dataframe_verification_only | 0.96 | 0.98 | 0.00 | 0.96 | 0.98 |
| data2mcp_dataframe_guarded | 0.93 | 0.93 | 0.00 | 1.00 | 0.93 |
| data2mcp_dataframe_guarded_light | 0.87 | 0.89 | 0.00 | 1.00 | 0.89 |

Numerical 55-task summary:

| Adapter | Clean TSR | Poisoned TSR | Toxic BCR | Toxic VR | Toxic RR |
|---|---:|---:|---:|---:|---:|
| data2mcp_dataframe | 0.71 | 0.42 | 0.25 | 0.00 | 0.11 |
| data2mcp_dataframe_caution | 0.75 | 0.44 | 0.22 | 0.22 | 0.18 |
| data2mcp_dataframe_expectation_only | 0.65 | 0.42 | 0.38 | 0.02 | 0.04 |
| data2mcp_dataframe_verification_only | 0.80 | 0.67 | 0.00 | 0.73 | 0.67 |
| data2mcp_dataframe_guarded | 0.75 | 0.76 | 0.00 | 1.00 | 0.76 |
| data2mcp_dataframe_guarded_light | 0.80 | 0.78 | 0.00 | 1.00 | 0.78 |

Combined 110-task summary:

| Adapter | Clean TSR | Poisoned TSR | Toxic BCR | Toxic VR | Toxic RR |
|---|---:|---:|---:|---:|---:|
| data2mcp_dataframe | 0.84 | 0.47 | 0.43 | 0.07 | 0.18 |
| data2mcp_dataframe_caution | 0.81 | 0.51 | 0.36 | 0.27 | 0.26 |
| data2mcp_dataframe_expectation_only | 0.79 | 0.48 | 0.55 | 0.02 | 0.07 |
| data2mcp_dataframe_verification_only | 0.88 | 0.83 | 0.00 | 0.85 | 0.83 |
| data2mcp_dataframe_guarded | 0.84 | 0.85 | 0.00 | 1.00 | 0.85 |
| data2mcp_dataframe_guarded_light | 0.84 | 0.84 | 0.00 | 1.00 | 0.84 |

Interpretation:

- The semantic/schema suite shows a clean mechanism split: prompt-only variants
  remain vulnerable, while verification-based variants recover nearly all
  poisoned cases in the first 50 tasks.
- The numerical suite is harder: verification removes blind compliance, but some
  ordinary calculation and answer-extraction failures remain.
- The combined 110-task smoke is strong enough to justify completing the remaining
  candidate tasks and using the verification ablation as a main defense result.

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
