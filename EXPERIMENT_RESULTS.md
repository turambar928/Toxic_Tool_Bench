# ToxicBench Experiment Results

Last updated: 2026-08-31

## Benchmark Evidence

The paper reports a 34-task numerical and 24-task semantic/schema cross-model evaluation, a 120-task GPT-only cross-agent evaluation, and a 13-task multi-table extension. Across LangGraph, smolagents, PandasAI, DA-Agent, and AutoGen where feasible, clean competence coexists with poisoned-task degradation and nonzero exposure-conditioned BCR. Detailed adapter/model tables remain in the released cross-model and expanded summary CSVs.

## Leakage-Free Defense Ablation

The current defense mainline uses LangGraph ReAct with `claude-haiku-4-5-20251001`. Generic expectations have no access to poison type, expected behavior, or the clean oracle.

| Variant | Clean TSR | Poisoned TSR | Delta TSR | BCR | ADR | VR | RR |
|---|---:|---:|---:|---:|---:|---:|---:|
| Base | 0.91 | 0.82 | 0.09 | 0.11 | 0.01 | 0.47 | 0.46 |
| Double-pass | 0.91 | 0.92 | -0.01 | 0.01 | 0.00 | 0.98 | 0.95 |
| Verification-only | 0.92 | 0.93 | -0.01 | 0.02 | 0.02 | 0.96 | 0.95 |
| Generic Guard | 0.93 | 0.93 | 0.00 | 0.00 | 0.02 | 0.97 | 0.94 |

Artifacts use the `toxictool_bench/results/leakage_free_defense_*` prefix. The matched Double-pass result shows that a second evidence route accounts for most of the gain.

## Repeated-Poison Stress

The complete stress matrix contains 1,596 toxic trajectories: 60 numerical, 60 semantic/schema, and 13 multi-table tasks; three two-route variants; and poisoning probabilities 0.25, 0.50, 0.75, and 1.00.

At probability 1.00:

| Suite | Variant | Poisoned TSR | BCR | RR |
|---|---|---:|---:|---:|
| Numerical | Verification-only | 0.68 | 0.44 | 0.09 |
| Numerical | Double-pass | 0.63 | 0.24 | 0.02 |
| Numerical | Generic Guard | 0.73 | 0.24 | 0.24 |
| Semantic/schema | Verification-only | 0.97 | 0.13 | 0.82 |
| Semantic/schema | Double-pass | 0.95 | 0.08 | 0.75 |
| Semantic/schema | Generic Guard | 0.87 | 0.10 | 0.87 |
| Multi-table | Verification-only | 0.69 | 0.38 | 0.38 |
| Multi-table | Double-pass | 0.54 | 0.38 | 0.46 |
| Multi-table | Generic Guard | 0.54 | 0.00 | 0.46 |

The result narrows the claim: zero BCR is observed under `poison_once`, while repeated corruption can restore blind compliance and reduce recovery. Artifacts are `verification_stress_summary.csv`, `verification_stress_manifest.csv`, and `figures/verification_stress_curves.pdf`.

## Cost

Across the two 60-task suites, Base averages 16.98 seconds and 2.36 tool events per toxic run. Generic Guard averages 39.90 seconds and 4.86 events; Double-pass averages 36.16 seconds. The gateway does not provide consistent token usage, so the paper does not infer dollar costs.

## Audit Status

The historical 80-run repeated-author comparison is diagnostic, not IAA. A separate blinded 120-trajectory packet is ready for two independent annotators. No IAA claim is made until both sheets are locked and merged.
