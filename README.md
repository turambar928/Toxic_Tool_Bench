# ToxicBench

ToxicBench evaluates whether data-analysis agents blindly trust tool outputs that look successful but are silently poisoned. The benchmark focuses on a practical failure mode for tool-augmented agents: the tool call succeeds, the return format is normal, but the returned content is numerically corrupted, semantically misleading, or stale.

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
├── ARTIFACT_MANIFEST.md
├── CASE_STUDIES.md
├── GUARDED_CASE_STUDIES.md
├── RUN_COMMANDS.md
└── PAPER_CONSISTENCY_CHECK.md
```

## Current Benchmark

- Numerical suite: 34 tasks over 11 CSV datasets.
- Semantic/schema suite: 24 tasks over 14 CSV datasets.
- Expanded release suites:
  - `toxictool_bench/tasks/numerical_iclr2027.jsonl`: 60 numerical tasks.
  - `toxictool_bench/tasks/semantic_schema_iclr2027.jsonl`: 60 semantic/schema tasks.
  - These add severity labels and additional poison taxonomy coverage such as ratio inversion, denominator swap, unit conversion, and missing-filter poisoning.
- Poisoning families: aggregate scaling, sign flips, rank/label swaps, treatment/control flips, column semantic swaps, stale metadata, and biased retrieval evidence.
- Agent adapters: LangGraph ReAct, smolagents, PandasAI, DA-Agent, and AutoGen.
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

The LangGraph ReAct guarded-verification defense substantially improves robustness on the 120-task expanded ablation:

```text
Combined 120 tasks:
Base LangGraph:   Clean TSR 0.93, Poisoned TSR 0.62, BCR 0.30, RR 0.42
Full guard:       Clean TSR 0.93, Poisoned TSR 0.93, BCR 0.00, RR 0.93
Light guard:      Clean TSR 0.91, Poisoned TSR 0.93, BCR 0.00, RR 0.93

Multi-table join extension, 13 tasks:
Base LangGraph:   Clean TSR 1.00, Poisoned TSR 0.23, BCR 0.77, RR 0.15
Full guard:       Clean TSR 1.00, Poisoned TSR 1.00, BCR 0.00, RR 1.00
Light guard:      Clean TSR 1.00, Poisoned TSR 1.00, BCR 0.00, RR 1.00

AutoGen replication, 120 tasks:
Base AutoGen:     Clean TSR 0.92, Poisoned TSR 0.65, BCR 0.20, RR 0.37
Verification:     Clean TSR 0.93, Poisoned TSR 0.93, BCR 0.00, RR 0.93
Guarded:          Clean TSR 0.92, Poisoned TSR 0.93, BCR 0.00, RR 0.93
```

For the expanded release, the LangGraph defense runner supports a six-way
ablation matrix: base, caution prompt only, expectation only, verification only,
full guard, and light guard.

See `EXPERIMENT_RESULTS.md`, `ARTIFACT_MANIFEST.md`, `SUBMISSION_CHECKLIST.md`, and `CURRENT_STATUS.md` for fuller summaries and release-package status.

## Important Artifacts

For a complete artifact map, see `ARTIFACT_MANIFEST.md`. The core paper-facing result files are:

- Cross-model numerical summary: `toxictool_bench/results/cross_model_summary.csv`
- Cross-model semantic/schema summary: `toxictool_bench/results/semantic_schema_cross_model_summary.csv`
- Expanded GPT cross-agent summary: `toxictool_bench/results/iclr2027_gpt_expanded_cross_agent_combined_summary.csv`
- Expanded GPT poison breakdown: `toxictool_bench/results/iclr2027_gpt_expanded_cross_agent_combined_poison_summary.csv`
- Expanded GPT severity breakdown: `toxictool_bench/results/iclr2027_gpt_expanded_cross_agent_combined_severity_summary.csv`
- Guarded ablation: `toxictool_bench/results/langgraph_guarded_ablation_summary.csv`
- Guarded suite breakdown: `toxictool_bench/results/langgraph_guarded_ablation_suite_summary.csv`
- Guarded overhead: `toxictool_bench/results/langgraph_guarded_overhead_summary.csv`
- Guard cost/latency distribution: `toxictool_bench/results/guard_cost_latency_distribution.csv`
- Multi-table extension: `toxictool_bench/results/langgraph_multitable_extension_summary.csv`
- AutoGen replication: `toxictool_bench/results/autogen_guarded_replication_summary.csv`
- AutoGen replication CIs: `toxictool_bench/results/autogen_guarded_replication_bootstrap_ci.csv`
- AutoGen combined logs: `toxictool_bench/results/autogen_*_expanded120_combined.jsonl`
- Bootstrap CIs:
  - `toxictool_bench/results/numerical_cross_model_bootstrap_ci.csv`
  - `toxictool_bench/results/semantic_schema_cross_model_bootstrap_ci.csv`
  - `toxictool_bench/results/langgraph_guarded_bootstrap_ci.csv`

## Paper

The paper entry point is `main.tex`. It includes all section files and an appendix skeleton. The file uses `iclr2026_conference.sty` if present and falls back to a standard `article` layout for local sanity checks.

```bash
pdflatex main.tex
pdflatex main.tex
```

The current environment used to prepare this export did not include `pdflatex` or `latexmk`, so PDF compilation was not run before export.

## Reproduction

See `RUN_COMMANDS.md` for the exact experiment commands and `ARTIFACT_MANIFEST.md` for expected outputs. The main scripts are:

```bash
python3 toxictool_bench/check_adapter_readiness.py
ADAPTERS="langgraph_react_full smolagents_toolcalling autogen_tool_agent" \
  bash toxictool_bench/run_expanded_full_adapters.sh gpt-5.4-mini
ADAPTERS="langgraph_react_full langgraph_react_caution langgraph_react_expectation_only langgraph_react_verification_only langgraph_react_guarded langgraph_react_guarded_light" \
  bash toxictool_bench/run_langgraph_guard_ablation.sh gpt-5.4-mini toxictool_bench/tasks/semantic_schema_iclr2027.jsonl
ADAPTERS="autogen_verification_only autogen_guarded" \
  bash toxictool_bench/run_autogen_guard_replication.sh gpt-5.4-mini toxictool_bench/tasks/semantic_schema_iclr2027.jsonl
```

Long expanded runs can be chunked:

```bash
START_INDEX=0 LIMIT=10 bash toxictool_bench/run_iclr2027_experiments.sh
START_INDEX=10 LIMIT=10 bash toxictool_bench/run_iclr2027_experiments.sh
```

Run static and unit checks:

```bash
python3 toxictool_bench/check_paper_static.py --main main.tex
python3 -m pytest toxictool_bench/tests -q
```

Large third-party adapter checkouts do not need to be committed into this repo.
Use external paths when they already exist locally:

```bash
export TOXICTOOL_BASELINE_DIR=/path/to/baseline_agent
```

To regenerate the ICLR 2027 expanded candidate task files:

```bash
python3 toxictool_bench/generate_iclr2027_tasks.py
```

## Security Note

API keys and local endpoint configuration should not be committed. This repository ignores the local `api` file and `.env` files.
