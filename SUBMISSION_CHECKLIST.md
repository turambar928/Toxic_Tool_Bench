# ToxicBench Submission Checklist

Last updated: 2026-08-23

## Reviewer-Issue Coverage

| Reviewer concern | Current response in paper/package |
|---|---|
| Benchmark/method names missing or inconsistent | Main text consistently uses ToxicBench and Guarded Verification. Static scan finds no `data2mcp`, `DataFrame Router`, or placeholder benchmark macros in paper-facing files. |
| Defense depends on unpublished custom agent | Paper-facing defense mainline is LangGraph ReAct. AutoGen provides a second-framework replication. |
| Defense generality beyond one framework | Main text reports LangGraph full ablation and AutoGen replication. Appendix reports AutoGen suite breakdown and runtime. |
| `poison_once` assumption may favor the guard | Main text distinguishes operational from source independence and states that source-independent coverage is 0/133. Appendix reports a small repeated/probabilistic poisoning stress test. Full-suite adaptive/source-corruption evaluation remains open. |
| Need scorer definitions for BCR/ADR/VR/RR | Section 3 gives compact metric rules. Appendix A gives deterministic scoring rules, borderline cases, and manual-audit rubric. |
| Need human audit / IAA | Appendix transparently reports an 80-run strict-scorer versus earlier single-author diagnostic. It is not IAA; independent multi-annotator adjudication remains open. |
| Need cost/latency overhead | Main experiments include overhead discussion. Appendix reports tool-event overhead and wall-clock latency for expanded and multi-table runs. |
| Need stronger baselines than caution prompting | Main text includes caution, expectation-only, verification-only, full guard, and light guard. Appendix adds abstain, randomized, and selective verification policies. |
| Need multi-route/adaptive poisoning stress | Appendix reports repeated-probabilistic poisoning over a 10-task semantic subset and explicitly labels the result small and non-monotonic. Numerical, join, and shared-source stress remain open. |
| Need multi-table / more realistic data workflows | Main experiments include 13-task multi-table extension. Appendix lists task families and latency. |
| Cross-framework poisoning boundaries differ | Experiments and limitations explicitly distinguish tool-observation poisoning from PandasAI's coarser chat-result boundary. |
| Need artifact release clarity | Appendix lists machine-readable summaries, raw logs, fixed seeds, task files, scripts, and SHA-256 checksums. Explicit code/data licenses still need an author decision. |
| False overrides on clean tasks | Appendix reports two base-correct to guard-wrong transitions, three clean repairs, and zero false overrides on the 13 joins; task IDs are released. |
| Adjacent verification methods | Related work now directly contrasts Guarded Verification with PoU contracts, RAGShield claim checks, and ToolCritic feedback. Head-to-head adapted baselines remain open. |
| References / unresolved labels | `python3 toxictool_bench/check_paper_static.py --main main.tex` passes with 38/38 cite keys and 21 refs. |

## Final PDF Checks Still Needed

The current server does not have a working LaTeX toolchain (`latexmk`, `pdflatex`, `xelatex`, and `tectonic` are unavailable; `tlmgr` is a Debian stub without user-mode initialization). Compile on Overleaf or a machine with a full TeX Live installation, then inspect:

- No unresolved `??` references or missing bibliography entries.
- Title line breaks render as intended.
- Appendix sections render as A, B, C, ... rather than all under A.
- Tables fit within margins and do not stack awkwardly.
- Page budget matches the target ICLR format.
- Extracted PDF text does not garble key result tables.

## Local Verification Completed

```text
python3 toxictool_bench/check_paper_static.py --main main.tex
python3 -m pytest toxictool_bench/tests -q
python3 -m compileall -q toxictool_bench
```
