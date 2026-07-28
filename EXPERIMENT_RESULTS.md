# ToxicBench Experiment Results

Last updated: 2026-07-28

This file summarizes the current paper-facing results. The defense mainline now uses LangGraph ReAct rather than an unpublished custom agent.

## Completed Suites

- Cross-model numerical suite: 34 tasks over 11 CSV datasets.
- Cross-model semantic/schema suite: 24 tasks over 14 CSV datasets.
- Expanded GPT-only suite: 120 tasks, split into 60 numerical and 60 semantic/schema tasks.
- Multi-table join extension: 13 tasks over joined table pairs.
- Guarded Verification ablation: six LangGraph ReAct variants on the expanded 120-task suite.

## Main Expanded Cross-Agent Result

GPT-only expanded results on 120 tasks:

| Adapter | Clean TSR | Poisoned TSR | Delta TSR | BCR | ADR | VR | RR |
|---|---:|---:|---:|---:|---:|---:|---:|
| `langgraph_react_full` | 0.93 | 0.60 | 0.33 | 0.33 | 0.07 | 0.43 | 0.44 |
| `smolagents_toolcalling` | 0.91 | 0.55 | 0.36 | 0.38 | 0.00 | 0.10 | 0.10 |
| `autogen_tool_agent` | 0.92 | 0.65 | 0.27 | 0.20 | 0.06 | 0.45 | 0.37 |

Artifact:

```text
toxictool_bench/results/iclr2027_gpt_expanded_cross_agent_combined_summary.csv
```

## LangGraph Guarded Verification Ablation

Combined 120-task ablation:

| Variant | Clean TSR | Poisoned TSR | Delta TSR | BCR | ADR | VR | RR |
|---|---:|---:|---:|---:|---:|---:|---:|
| Base | 0.93 | 0.62 | 0.31 | 0.30 | 0.06 | 0.44 | 0.42 |
| Caution only | 0.94 | 0.68 | 0.26 | 0.21 | 0.06 | 0.44 | 0.41 |
| Expectation only | 0.94 | 0.61 | 0.33 | 0.28 | 0.02 | 0.43 | 0.39 |
| Verification only | 0.91 | 0.89 | 0.02 | 0.00 | 1.00 | 0.91 | 0.89 |
| Full guard | 0.93 | 0.93 | 0.01 | 0.00 | 1.00 | 0.87 | 0.93 |
| Light guard | 0.91 | 0.93 | -0.02 | 0.00 | 1.00 | 0.87 | 0.93 |

Suite breakdown:

| Suite | Variant | Clean TSR | Poisoned TSR | BCR | VR | RR |
|---|---|---:|---:|---:|---:|---:|
| Semantic/schema | Base | 1.00 | 0.82 | 0.13 | 0.85 | 0.80 |
| Semantic/schema | Full guard | 0.98 | 0.98 | 0.00 | 1.00 | 0.98 |
| Semantic/schema | Light guard | 0.98 | 0.98 | 0.00 | 1.00 | 0.98 |
| Numerical | Base | 0.85 | 0.42 | 0.47 | 0.03 | 0.03 |
| Numerical | Full guard | 0.88 | 0.87 | 0.00 | 0.73 | 0.87 |
| Numerical | Light guard | 0.83 | 0.87 | 0.00 | 0.73 | 0.87 |

Artifacts:

```text
toxictool_bench/results/langgraph_guarded_ablation_summary.csv
toxictool_bench/results/langgraph_guarded_ablation_suite_summary.csv
toxictool_bench/results/langgraph_guarded_overhead_summary.csv
toxictool_bench/results/langgraph_guarded_bootstrap_ci.csv
```

## AutoGen Guarded Verification Replication

The defense effect was replicated on AutoGen over the same 120 expanded tasks.

| Variant | Clean TSR | Poisoned TSR | Delta TSR | BCR | ADR | VR | RR |
|---|---:|---:|---:|---:|---:|---:|---:|
| `autogen_verification_only` | 0.93 | 0.93 | 0.00 | 0.00 | 1.00 | 0.86 | 0.93 |
| `autogen_guarded` | 0.92 | 0.93 | -0.01 | 0.00 | 1.00 | 0.87 | 0.93 |

Artifacts:

```text
toxictool_bench/results/autogen_guarded_replication_summary.csv
toxictool_bench/results/autogen_guarded_replication_suite_summary.csv
toxictool_bench/results/autogen_guarded_replication_bootstrap_ci.csv
toxictool_bench/results/autogen_verification_only_gpt-5.4-mini_expanded120_combined.jsonl
toxictool_bench/results/autogen_guarded_gpt-5.4-mini_expanded120_combined.jsonl
```

## Multi-Table Join Extension

LangGraph ReAct on 13 join-style tasks:

| Variant | Clean TSR | Poisoned TSR | BCR | RR | Clean sec. | Toxic sec. |
|---|---:|---:|---:|---:|---:|---:|
| Base | 1.00 | 0.23 | 0.77 | 0.15 | 8.42 | 9.55 |
| Full guard | 1.00 | 1.00 | 0.00 | 1.00 | 18.92 | 23.27 |
| Light guard | 1.00 | 1.00 | 0.00 | 1.00 | 17.92 | 22.96 |

Artifact:

```text
toxictool_bench/results/langgraph_multitable_extension_summary.csv
```

## Cross-Model Results

The cross-model runs use the smaller 34-task numerical and 24-task semantic/schema suites. They show the same main pattern: high clean TSR does not imply low blind compliance. The paper uses compact adapter-mean tables, with full adapter-level artifacts here:

```text
toxictool_bench/results/cross_model_summary.csv
toxictool_bench/results/semantic_schema_cross_model_summary.csv
toxictool_bench/results/numerical_cross_model_bootstrap_ci.csv
toxictool_bench/results/semantic_schema_cross_model_bootstrap_ci.csv
```

## Main Takeaways

1. Silent tool poisoning exposes a gap between tool-use competence and tool-trust calibration.
2. Rank swaps, label swaps, and plausible aggregate scaling induce more blind compliance than obvious sign flips.
3. Prompt-only caution is insufficient; independent verification is the active ingredient.
4. LangGraph Guarded Verification reduces observed BCR to 0.00 on the expanded 120-task ablation and on the 13-task join extension, while improving poisoned-task success.
5. AutoGen replication shows the same BCR reduction on the expanded 120-task suite, strengthening the mitigation claim beyond a single framework.
