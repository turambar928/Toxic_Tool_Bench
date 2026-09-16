# ToxicBench Current Status

Last updated: 2026-09-16

## Submission revision

The V4 field-bound, matched-parent experiment is complete: 264/264 trajectories
on 24 tasks across three public datasets. Primary correctness is 24/24 clean,
20/24 partial corruption, and 0/24 full-target corruption. With clean second-stage
evidence, retry is 48/48 and review 47/48; both are 0/48 under full corruption.
All 120 full-target events change every result alias, leaving no clean target
alias. One budget-exhausted model outcome is retained as a failure; one API
failure was recovered without replacing completed answers. See
[EVIDENCE_CONTROLS_V4_CN.md](EVIDENCE_CONTROLS_V4_CN.md). It is a separate
structured-tool interface, not a replacement for historical framework results
or independent validation of the free-text scorer. The current 156 tests pass.

Real human annotations remain pending (0/200 independent, 0/40 errata).
[HUMAN_VALIDATION_HANDOFF_CN.md](HUMAN_VALIDATION_HANDOFF_CN.md) provides
distribution instructions and a source/return validator. All 240 packet entries
have passed read-only source verification; no human labels were generated.

Previous non-human submission revision V3 is documented in
[SUBMISSION_REVISION_V3_CN.md](SUBMISSION_REVISION_V3_CN.md). The injector now
targets complete, unambiguous scalar values and does not consume one-shot
eligibility on no-ops or tool errors. The historical delivery audit flags 204
off-target sign-flip events (157 trajectories) among 3,319 recorded corruptions.
Historical matrices below retain the old injector; they are not repaired-injector
results. The separately frozen follow-up is complete: 152/152 trajectories,
including 128 controlled and 24 public-data runs, with no missing or duplicate
conditions. Eight failed attempts caused by HTTP 429 are retained; only missing
environments were recovered, finishing at one worker. Human validation and the
answer parser remain untouched. All 134 tests pass.

The 16-task control increases second-route exposure but gives small, uncertain
TSR differences: per-route minus shared is -0.0625 for Double-pass and
Verification-only and -0.1875 for Guard; every paired interval includes zero.
Base already achieves 16/16 on this repair-focused subset. All public-data
conditions achieve 6/6, with residual clean answers still present in exposed
returns, so this is an execution check, not a demonstration of robust transfer.
See `output/submission_revision_v3/completion_manifest.json` and the new appendix.

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
- The V4 build is 32 pages including references and appendices; new evidence
  controls are in Appendix I and do not expand the main-text limit.
- The manuscript distinguishes development recheck, reference re-review, and pending independent validation.
- It no longer claims Generic Guard superiority or that every VPA case ignored sufficient correct evidence.
- V2 checkpoint test suite: 116 passed; current test count is reported above.

The paper is materially repaired but not final: two-person validation annotation and the 40-row reference re-review remain required submission work.
