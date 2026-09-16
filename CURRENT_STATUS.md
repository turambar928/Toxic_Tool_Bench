# ToxicBench Current Status

Last updated: 2026-09-16

## Submission revision

The scoring-only answer selector is frozen at commit `98c2ed8`. A versioned analysis has rescored 5,396 historical trajectories without changing raw trajectories, historical task JSONL, poison targets, or human labels. The manuscript uses corrected scoring references and excludes two denominator-ambiguous tasks from revised comparisons.

The full execution record is [SCORER_REPAIR_EXECUTION_CN.md](SCORER_REPAIR_EXECUTION_CN.md).

## Revised defense result (118 retained tasks)

| Variant | Clean TSR | Poisoned TSR | BCR | VR | RR |
|---|---:|---:|---:|---:|---:|
| Base | 0.99 | 0.89 | 0.09 | 0.46 | 0.44 |
| Double-pass | 0.99 | 1.00 | 0.00 | 0.98 | 0.98 |
| Verification-only | 0.92 | 0.90 | 0.00 | 0.97 | 0.86 |
| Generic Guard | 0.98 | 0.97 | 0.00 | 0.97 | 0.94 |

Double-pass minus Base poisoned TSR is +0.110. Its template-cluster 95% interval is [0.056, 0.171], and its dataset-cluster interval is [0.060, 0.172]. Generic Guard does not improve on Double-pass in this matrix.

## Scorer and reference audit

- Development recheck on the audit-informed 240 cases: TSR agreement 238/240 (99.2%), precision 1.000, recall 0.990. This is not independent validation.
- Reference audit: seven incorrect numerical instances, two tied-answer omissions, and two denominator-ambiguous instances.
- Revised denominators: 118 single-table task instances, 944 defense trajectories, and 1,572 repeated-poison trajectories.
- Forty historical human-audit rows require reference re-review; their original labels remain unchanged.
- PandasAI is excluded from main behavioral comparisons because its historical adapter mutates the final chat return after agent completion.

## Frozen independent validation

The protocol contains 200 trajectories: 90 reused semantic trajectories and 110 new numerical trajectories on task instances excluded from parser development. After bypassing the server's local proxy, all 90 fixed-Haiku core/repeated trajectories completed with zero failed jobs. The original GPT model was unavailable, and the first approved replacement accepted chat but rejected function tools; both events were recorded before any cross-model trajectory completed. A second user-authorized amendment selected tool-compatible Claude Sonnet 4.6, and all 20 AutoGen trajectories completed. The packet is now 200/200, with source hashes and both amendments preserved. Human annotation has not started.

## Paper status

- Main text ends on page 9; references start on page 10.
- The manuscript distinguishes development recheck, reference re-review, and pending independent validation.
- It no longer claims Generic Guard superiority or that every VPA case ignored sufficient correct evidence.
- Test suite: 116 passed.

The paper is materially repaired but not final: two-person validation annotation and the 40-row reference re-review remain required submission work.
