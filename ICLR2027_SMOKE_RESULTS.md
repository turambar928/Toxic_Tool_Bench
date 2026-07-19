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

## Next Gate

Run the full six-way data2mcp ablation on both ICLR 2027 candidate suites:

```bash
ADAPTERS="data2mcp_dataframe data2mcp_dataframe_caution data2mcp_dataframe_expectation_only data2mcp_dataframe_verification_only data2mcp_dataframe_guarded data2mcp_dataframe_guarded_light" \
TASK_SUITES="toxictool_bench/tasks/semantic_schema_iclr2027.jsonl toxictool_bench/tasks/numerical_iclr2027.jsonl" \
bash toxictool_bench/run_iclr2027_experiments.sh
```
