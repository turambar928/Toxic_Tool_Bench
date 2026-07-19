# ToxicTool-Bench

ToxicTool-Bench evaluates whether data-analysis agents blindly trust tool outputs that look successful but are silently poisoned. The benchmark focuses on a practical failure mode for tool-augmented agents: the tool call succeeds, the return format is normal, but the returned content is numerically corrupted, semantically misleading, or stale.

The main behavioral metric is blind compliance: whether an agent copies or relies on poisoned tool evidence in its final answer without validation.

## Repository Layout

```text
.
├── main.tex
├── sections/
│   ├── 00_abstract.tex
│   ├── 01_introduction.tex
│   ├── 02_problem_setup.tex
│   ├── 03_toxictool_bench.tex
│   ├── 04_method_ibf.tex
│   ├── 05_experiments.tex
│   ├── 06_qualitative_analysis.tex
│   ├── 06_related_work.tex
│   ├── 07_discussion_limitations.tex
│   └── 08_appendix_guard_details.tex
├── toxictool_bench/
│   ├── tasks/
│   ├── datasets/
│   ├── results/
│   ├── tests/
│   ├── full_adapters.py
│   ├── poisoners.py
│   ├── evaluator.py
│   └── run_full_bench.py
├── EXPERIMENT_RESULTS.md
├── CASE_STUDIES.md
├── GUARDED_CASE_STUDIES.md
├── RUN_COMMANDS.md
└── PAPER_CONSISTENCY_CHECK.md
```

## Current Benchmark

- Numerical suite: 34 tasks over 11 CSV datasets.
- Semantic/schema suite: 24 tasks over 14 CSV datasets.
- ICLR 2027 expanded candidate suites:
  - `toxictool_bench/tasks/numerical_iclr2027.jsonl`: 60 numerical tasks.
  - `toxictool_bench/tasks/semantic_schema_iclr2027.jsonl`: 60 semantic/schema tasks.
  - These add severity labels and additional poison taxonomy coverage such as ratio inversion, denominator swap, unit conversion, and missing-filter poisoning.
- Poisoning families: aggregate scaling, sign flips, rank/label swaps, treatment/control flips, column semantic swaps, stale metadata, and biased retrieval evidence.
- Agent adapters: LangGraph ReAct, smolagents, `data2mcp`, PandasAI, DA-Agent, and AutoGen.
- Models used where practical: `gpt-5.4-mini`, `claude-sonnet-4-6`, and `Qwen3.6-35B-A3B-no-thinking`.

## Metrics

- Clean TSR: task success rate in the clean environment.
- Poisoned TSR: task success rate under silent poisoning.
- Delta TSR: clean-to-poisoned degradation.
- BCR: blind compliance rate.
- ADR: anomaly detection rate.
- VR: validation rate.
- RR: recovery rate.

## Key Results

The completed experiments show that high clean-task success does not imply robustness to silently corrupted tool observations. Several agents solve clean tasks while directly copying poisoned values, labels, or retrieved evidence under poisoning.

The `data2mcp` guarded-verification defense substantially improves robustness:

```text
Semantic/schema, 24 tasks:
Base data2mcp:    Clean TSR 0.92, Poisoned TSR 0.29, BCR 0.62, RR 0.00
Full guard:       Clean TSR 0.83, Poisoned TSR 0.83, BCR 0.00, RR 0.83
Light guard:      Clean TSR 0.83, Poisoned TSR 0.71, BCR 0.00, RR 0.71

Numerical, 34 tasks:
Base data2mcp:    Clean TSR 0.65, Poisoned TSR 0.47, BCR 0.24, RR 0.09
Full guard:       Clean TSR 0.79, Poisoned TSR 0.74, BCR 0.00, RR 0.74
Light guard:      Clean TSR 0.68, Poisoned TSR 0.65, BCR 0.00, RR 0.65
```

For the ICLR 2027 expansion, the data2mcp defense runner now supports a six-way
ablation matrix: base, caution prompt only, expectation only, verification only,
full guard, and light guard.

See `EXPERIMENT_RESULTS.md`, `PROGRESS_REPORT.md`, and `CURRENT_STATUS.md` for fuller summaries.

## Important Artifacts

- Cross-model numerical summary: `toxictool_bench/results/cross_model_summary.csv`
- Cross-model semantic/schema summary: `toxictool_bench/results/semantic_schema_cross_model_summary.csv`
- Guarded semantic ablation: `toxictool_bench/results/data2mcp_guarded_semantic_ablation_summary.csv`
- Guarded numerical ablation: `toxictool_bench/results/data2mcp_guarded_numerical_ablation_summary.csv`
- Guarded overhead: `toxictool_bench/results/data2mcp_guarded_overhead_summary.csv`
- Bootstrap CIs:
  - `toxictool_bench/results/numerical_cross_model_bootstrap_ci.csv`
  - `toxictool_bench/results/semantic_schema_cross_model_bootstrap_ci.csv`
  - `toxictool_bench/results/data2mcp_guarded_bootstrap_ci.csv`

## Paper

The paper entry point is `main.tex`. It includes all section files and an appendix skeleton. The file uses `iclr2026_conference.sty` if present and falls back to a standard `article` layout for local sanity checks.

```bash
pdflatex main.tex
pdflatex main.tex
```

The current environment used to prepare this export did not include `pdflatex` or `latexmk`, so PDF compilation was not run before export.

## Reproduction

See `RUN_COMMANDS.md` for the exact experiment commands. The main scripts are:

```bash
bash toxictool_bench/run_expanded_full_adapters.sh
bash toxictool_bench/run_semantic_schema_full_adapters.sh
bash toxictool_bench/run_data2mcp_guard_ablation.sh
bash toxictool_bench/run_iclr2027_experiments.sh
```

Check local full-adapter dependencies before launching expensive runs:

```bash
python3 toxictool_bench/check_adapter_readiness.py
```

To regenerate the ICLR 2027 expanded candidate task files:

```bash
python3 toxictool_bench/generate_iclr2027_tasks.py
```

## Security Note

API keys and local endpoint configuration should not be committed. This repository ignores the local `api` file and `.env` files.
