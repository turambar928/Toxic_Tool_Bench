# ToxicBench Current Status

Last updated: 2026-09-21

## Model-free task acceptance

The executable acceptance run is complete on 131 retained synthetic tasks,
262 task--condition cases, and 786 tool events, with zero model API calls.
All reference/specification checks agree and input hashes are unchanged.
Under fixed calls/rendering, 119 tasks receive valid target-changing returns;
raw-data recovery is 119/119 for one-shot and 110/119 for repeated poisoning.
Ten numeric targets are not exposed and two table-discovery previews have
duplicate table-name keys; neither is counted as a valid target intervention.
The 21 declared schema-role checks are not independent semantic annotation.
See [the report](output/task_acceptance_v1/README_CN.md), §3.1 and Appendix A.
The regression suite now has 201 passing tests. Historical tasks, model outcomes,
injector, frozen scorer, and human labels are unchanged.

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
or the separate human evaluation of the free-text scorer. The V4 checkpoint had 156 passing tests.

Two annotators have returned all 200 post-freeze evaluation labels and all 40
reference-review labels, with no binary-label disagreements. The author confirms
independent completion without LLM use on September 17, followed by note
standardization without changing labels. TSR agreement is 192/200 (96.0%).
Human core poisoned TSR is Base 0.80, Double-pass 1.00, Verification-only 1.00,
and Guard 0.95; the Double-pass--Base contrast is +0.20 [0.05, 0.35].
The 40-case review excludes 12 ambiguous references and agrees on 28/28 eligible
cases. See the [full report](output/human_validation_20260920/README_CN.md)
for all metric counts, source attestations, and the unchanged frozen scorer.

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
answer parser were untouched at the V3 checkpoint, which had 134 passing tests.

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
- Forty historical audit rows have now been reviewed separately: 12 reference-ineligible, 28 eligible and scorer-concordant. Original historical labels remain unchanged.
- PandasAI is excluded from main behavioral comparisons because its historical adapter mutates the final chat return after agent completion.

## Post-freeze human evaluation

The protocol contains 200 trajectories: 90 reused semantic trajectories and 110 new numerical trajectories on task instances excluded from parser development. After bypassing the server's local proxy, all 90 fixed-Haiku core/repeated trajectories completed with zero failed jobs. The original GPT model was unavailable, and the first approved replacement accepted chat but rejected function tools; both events were recorded before any cross-model trajectory completed. A second user-authorized amendment selected tool-compatible Claude Sonnet 4.6, and all 20 AutoGen trajectories completed. Execution and human-label collection are complete; source hashes, amendments, received-label bytes, and author-reported provenance are preserved. The distributed kit omitted automatic labels; additional blinding attestations were not supplied and are not fabricated.

## Paper status

- Main text ends on page 9; references start on page 10.
- The current build is 27 pages, with five appendix sections; new evidence
  controls are in Appendix E and the human evaluation is in Appendix B.
- The manuscript distinguishes historical development recheck, completed reference review, and post-freeze human evaluation.
- It no longer claims Generic Guard superiority or that every VPA case ignored sufficient correct evidence.
- V2 checkpoint test suite: 116 passed; current test count is reported above.
- September 21 regression suite: 201 passed; static references and both official-template PDF builds checked. The acceptance table is Table 5, on page 15. Main text remains nine pages.

The annotation collection is no longer the blocking task. The manuscript now leads
with the supported phenomena and reports the full human/automatic comparison in
the appendix, including Verification-only's tie with Double-pass on the audited
core subset. Final submission still requires the usual author and format review.
