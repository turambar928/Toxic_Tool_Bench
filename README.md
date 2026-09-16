# ToxicBench

ToxicBench evaluates whether data-analysis agents blindly trust tool outputs that look successful but are silently poisoned. The benchmark focuses on a practical failure mode for tool-augmented agents: the tool call succeeds, the return format is normal, but the returned content is numerically corrupted, semantically misleading, or stale.

The main behavioral metric is blind compliance: whether an agent copies or relies on poisoned tool evidence in its final answer without validation.

For the current submission revision, see the
[repair plan](SCORER_REPAIR_PLAN_CN.md), the
[execution report](SCORER_REPAIR_EXECUTION_CN.md), and
[current status](CURRENT_STATUS.md). The execution report separates completed
offline repairs from the still-pending independent human validation.

The [V4 evidence-control report](EVIDENCE_CONTROLS_V4_CN.md) documents a separate
field-bound intervention and matched-parent experiment across three public
datasets. The [human validation handoff](HUMAN_VALIDATION_HANDOFF_CN.md) explains
how two independent raters and a third adjudicator return the frozen 200-case
validation and 40-case reference review. Automated experiments do not substitute
for these real human annotations.

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
│   ├── 08_appendix_guard_details.tex
│   └── 09_revision_validation.tex
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

After reference auditing, the revised expanded comparisons retain 58 numerical
and 60 semantic/schema tasks. GPT poisoned TSR falls from 0.99 to 0.67 for
LangGraph, from 0.98 to 0.59 for smolagents, and from 0.92 to 0.66 for AutoGen.
These are adapter-level diagnostic results, not deployment-frequency estimates.

In the historical-injector, matched-cap Claude Haiku matrix, Double-pass reaches 1.00
poisoned TSR versus 0.89 for Base over the 118 retained tasks. The paired
difference is +0.110, with template-cluster 95% interval [0.056, 0.171] and
dataset-cluster interval [0.060, 0.172]. Generic Guard reaches 0.97 and does not
outperform Double-pass. This supports the value of another evidence pass, not a
claim that a specialized guard is uniquely effective.

The delivery audit flags 204 off-target sign-flip events among 3,319 recorded
corruptions (157 trajectories), including 20 numeric no-ops. Historical delivery
rates are not certified valid exposure. Removing all eight sign-flip tasks
preserves the direction of the defense comparison on the remaining 110 tasks.
All 152 fresh repaired-injector trajectories are complete; their results and
historical exposure sensitivity are versioned separately under
`output/submission_revision_v3/`. The selected 16-task control has small TSR
differences whose paired intervals include zero. The six public-data tasks show
ceiling performance with residual clean answers still available, not evidence
of deployment robustness.
Matched caps mean route count, steps per route, and output tokens **per request**,
not equal total token cost. See [SUBMISSION_REVISION_V3_CN.md](SUBMISSION_REVISION_V3_CN.md).

The revised scorer reaches 238/240 TSR agreement on the audit-informed
development set, but that is not independent validation. All 200 trajectories
in the post-freeze packet are now prepared: 90 reused semantic trajectories,
90 new Haiku core/repeated trajectories, and 20 new AutoGen trajectories run
with Claude Sonnet 4.6 after a documented pre-run model-availability amendment.
Human validation has not started, so no independent scorer result is claimed.

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
- Versioned scorer analysis: `output/scorer_revision_v2/analysis_manifest.json`
- Reference audit: `toxictool_bench/results/reference_answer_audit.json`
- AutoGen combined logs: `toxictool_bench/results/autogen_*_expanded120_combined.jsonl`
- Bootstrap CIs:
  - `toxictool_bench/results/numerical_cross_model_bootstrap_ci.csv`
  - `toxictool_bench/results/semantic_schema_cross_model_bootstrap_ci.csv`
  - `toxictool_bench/results/langgraph_guarded_bootstrap_ci.csv`

## Paper

The paper entry point is `main.tex`. It uses the included ICLR 2027 style. The
current compiled version ends the main text on page 9 and starts references on
page 10.

```bash
tectonic main.tex --outdir output/scorer_revision_v2/pdf --keep-logs
```

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
