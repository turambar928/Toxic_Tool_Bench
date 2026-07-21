# Paper Consistency Check

Date: 2026-07-19

## Entry Point

- Added `main.tex` as the paper entry point.
- Section order:
  - `sections/00_abstract.tex`
  - `sections/01_introduction.tex`
  - `sections/02_problem_setup.tex`
  - `sections/03_toxictool_bench.tex`
  - `sections/04_method_ibf.tex`
  - `sections/05_experiments.tex`
  - `sections/06_qualitative_analysis.tex`
  - `sections/06_related_work.tex`
  - `sections/07_discussion_limitations.tex`
  - appendix: `sections/08_appendix_guard_details.tex`
- `main.tex` defines:
  - `\benchmarkname`: `ToxicTool-Bench`
  - `\methodname`: `Guarded Verification`
- `main.tex` uses `iclr2026_conference.sty` if present and falls back to `article` layout otherwise, so the paper can be sanity-compiled before the official style file is added.

## Checked

- All section files referenced by `main.tex` exist.
- All current `\ref{...}` targets have matching `\label{...}` definitions.
- Related-work citations are present and `main.tex` includes `references.bib`.
- Main numerical cross-model table matches `toxictool_bench/results/cross_model_summary.csv`.
- Main semantic/schema table matches `toxictool_bench/results/semantic_schema_cross_model_summary.csv`.
- Guarded ablation table matches:
  - `toxictool_bench/results/data2mcp_guarded_semantic_ablation_summary.csv`
  - `toxictool_bench/results/data2mcp_guarded_numerical_ablation_summary.csv`
- Appendix light-guard and CI values match the guarded result artifacts as written.

## Fixed

- Normalized the defense naming around `Guarded Verification` in the method section and paper macro.
- Updated RQ2 to match the completed numerical and semantic/schema experiments instead of implying a completed instruction-poisoning suite.
- Reworded the benchmark discussion of data-embedded instructions as framework support rather than a reported main experiment.
- Reworded the experiment failure-pattern list to avoid implying instruction-poisoning results in the main tables.
- Reorganized Section 5 after the GPT-only 120-task expanded cross-agent run:
  - main text keeps the 120-task cross-agent table and the 120-task `data2mcp` defense table as the primary results;
  - cross-model evidence is compressed into one adapter-mean table;
  - detailed adapter-level cross-model and suite-breakdown tables are released as artifact CSVs and listed in the appendix.

## Remaining Before Submission

- Add the official ICLR style file for the target year or replace the fallback with the final conference package.
- Run a full LaTeX build after TeX is installed in the environment.
- Check page budget after the official style is applied; the current skeleton is content-complete but not page-budget validated.
- Decide whether to include compact bootstrap CI tables beyond the guarded CI table already in the appendix.
- After applying the official ICLR style, verify whether the compact cross-model table and defense tables fit without overflow.

## Build Status

- `pdflatex` is not installed in the current environment.
- `latexmk` is not installed in the current environment.
- Static LaTeX checks passed for includes and labels.
- Attempted to download the official ICLR 2026 template from the ICLR Master-Template GitHub repository, but the network transfer stalled and the direct raw path returned an invalid 14-byte file. The invalid partial file was removed. `main.tex` still supports the official style if `iclr2026_conference.sty` and `iclr2026_conference.bst` are added later.
