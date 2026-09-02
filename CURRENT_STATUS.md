# ToxicBench Current Status

Last updated: 2026-08-31

## Completed

- Cross-framework benchmark evaluation on LangGraph, smolagents, PandasAI, DA-Agent, and AutoGen where feasible.
- Cross-model numerical (34 tasks) and semantic/schema (24 tasks) evaluations using GPT, Claude, and Qwen families.
- Expanded GPT-only cross-agent evaluation with 60 numerical and 60 semantic/schema tasks.
- Leakage-free LangGraph defense ablation on 120 tasks with Claude Haiku.
- Matched-compute Double-pass baseline, Verification-only baseline, and Generic Guard.
- Task-level bootstrap confidence intervals, poison/severity breakdowns, clean-transition analysis, tool-event counts, and latency distributions.
- Complete repeated-poison matrix: 1,596 toxic trajectories over numerical, semantic/schema, and 13 multi-table tasks at four poisoning probabilities.
- Deterministic strict scorer, regression tests, release audit, licenses, manifests, and checksums.
- Blinded 120-trajectory packet, independent labels, pre-adjudication agreement, and merge utility for a genuine two-person audit.
- Paper updated to use only post-fix defense results and to state that zero BCR is limited to `poison_once`.

## Main Post-Fix Defense Result

| Variant | Clean TSR | Poisoned TSR | BCR | VR | RR |
|---|---:|---:|---:|---:|---:|
| Base | 0.91 | 0.82 | 0.11 | 0.47 | 0.46 |
| Double-pass | 0.91 | 0.92 | 0.01 | 0.98 | 0.95 |
| Verification-only | 0.92 | 0.93 | 0.02 | 0.96 | 0.95 |
| Generic Guard | 0.93 | 0.93 | 0.00 | 0.97 | 0.94 |

Extra evidence and compute explain most of the improvement. Generic Guard removes the residual observed blind compliance under `poison_once`; it is not a guarantee under repeated or shared-source corruption.

## Repeated-Poison Boundary

At poisoning probability 1.00, Generic Guard BCR is 0.24 on numerical tasks, 0.10 on semantic/schema tasks, and 0.00 on the 13 joins. Numerical RR falls to 0.24. The full curves and confidence intervals are in `verification_stress_summary.csv` and `figures/verification_stress_curves.pdf`.

## Audit Result

The two-annotator audit has 0.967 macro percent agreement and 0.913 macro Cohen's kappa over 120 trajectories. Per-label kappa is 0.914 for BCR, 0.826 for ADR, 0.948 for VR, and 0.965 for RR. Twelve trajectories have at least one disagreement and are listed in `human_audit_v2/adjudication.csv` for optional adjudication.

The final PDF must be compiled and visually checked on Overleaf because no local TeX toolchain is installed.
