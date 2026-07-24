# ICLR section draft map

These files are written as modular LaTeX sections included by the project-level `main.tex`:

- `00_abstract.tex`: abstract draft.
- `01_introduction.tex`: motivation, threat model intuition, and contributions.
- `02_problem_setup.tex`: formal setup for silent tool poisoning and trust calibration.
- `03_toxictool_bench.tex`: benchmark design, poisoning operators, paired protocol, and metrics.
- `04_method_ibf.tex`: guarded verification mitigation.
- `05_experiments.tex`: main experiments, cross-model results, and guarded ablations.
- `06_qualitative_analysis.tex`: trajectory-level failure and recovery analysis.
- `06_related_work.tex`: related work.
- `07_discussion_limitations.tex`: limitations and positioning.
- `08_appendix_guard_details.tex`: appendix material for light guard, overhead, and framework-boundary details.

The paper uses literal names in the section files: `ToxicBench` for the benchmark and `Guarded Verification` for the defense.
