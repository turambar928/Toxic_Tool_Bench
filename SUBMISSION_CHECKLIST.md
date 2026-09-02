# ToxicBench Submission Checklist

Last updated: 2026-08-31

## Reviewer-Issue Coverage

| Reviewer concern | Current response in paper/package |
|---|---|
| Benchmark/method naming | Paper-facing files consistently use ToxicBench and Guarded Verification. Static checks find no benchmark placeholders or `data2mcp`. |
| Defense prompt leakage | Fixed. Generic expectations cannot read poison type, expected behavior, or the clean oracle. The paper uses only the post-fix 120-task Claude ablation for defense claims. |
| Extra compute as a confound | A budget-matched Double-pass control runs two ordinary isolated routes. It explains most of the Base-to-Guard improvement; the paper states this directly. |
| `poison_once` assumption | A full 1,596-run matrix covers 60 numerical, 60 semantic/schema, and 13 multi-table tasks at route-poison probabilities 0.25, 0.50, 0.75, and 1.00. BCR returns and RR falls under repeated poisoning. |
| Route independence | The paper distinguishes observation, execution-route, and source independence. Source-independent coverage is 0/133; no Byzantine-source guarantee is claimed. |
| Deterministic scoring | Main text gives compact BCR/ADR/VR/RR rules. The appendix gives temporal requirements, borderline cases, and the conservative lexical ADR limitation. |
| Human audit / IAA | A blinded 120-trajectory audit is complete. Pre-adjudication macro agreement is 0.967 and macro Cohen's kappa is 0.913; 12 trajectories are released for separate adjudication. |
| Cost and latency | Main text and appendix report mean, p50, and p90 latency plus tool-event counts. Dollar cost is omitted because the gateway does not provide consistent token accounting. |
| Stronger baselines | Results include Base, matched Double-pass, Verification-only, Generic Guard, plus fixed-subset abstain, randomized, and keyword-selective policies. |
| Stronger adversary | Complete repeated-observation poisoning results and confidence intervals are released. Shared-source, parser, and cache corruption remain outside the measured threat model. |
| Cross-framework boundaries | Paper distinguishes tool-observation adapters from PandasAI's coarser chat-result boundary and avoids strict framework rankings. |
| Task breadth | Numerical, semantic/schema, retrieval, and a 13-task multi-table join extension are included. Large databases, live APIs, and notebooks remain future work. |
| Artifact reproducibility | Requirements, code/data licenses, fixed seeds, raw logs, manifests, checksums, scorer, and rebuild scripts are present. |
| References and labels | `check_paper_static.py` passes with all cited keys resolved and no missing labels. |

## Remaining External Step

The two independent annotators completed `toxictool_bench/human_audit_v2/annotator_a.csv` and `annotator_b.csv`. The merge output is in the same directory. Remaining work is optional adjudication of the 12 disagreement rows; Cohen's kappa must remain based on the pre-adjudication labels.

## Final PDF Checks

The local machine has no full LaTeX toolchain. Compile on Overleaf and inspect page count, float placement, table width, title wrapping, appendix lettering, and extracted-text readability. Confirm that the PDF shows no unresolved `??` references.

## Local Verification

```bash
python3 toxictool_bench/check_paper_static.py --main main.tex
python3 -m pytest toxictool_bench/tests -q
python3 toxictool_bench/release_audit.py
git diff --check
```
