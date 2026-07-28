# ToxicBench Run Commands

Run all commands from the repository root:

```bash
cd /home/taozifu2025/toxicbench
```

## Smoke Tests

No API call:

```bash
python3 toxictool_bench/run_bench.py \
  --agent-profile heuristic_naive \
  --env both \
  --limit 2
```

LangGraph ReAct one-task smoke run:

```bash
TOXICTOOL_BASELINE_DIR=/path/to/baseline_agent \
python3 toxictool_bench/run_full_bench.py \
  --tasks toxictool_bench/tasks/semantic_schema_iclr2027.jsonl \
  --adapter langgraph_react_full \
  --model gpt-5.4-mini \
  --env both \
  --start-index 0 \
  --limit 1 \
  --max-steps 8
```

LangGraph guarded smoke run:

```bash
TOXICTOOL_BASELINE_DIR=/path/to/baseline_agent \
python3 toxictool_bench/run_full_bench.py \
  --tasks toxictool_bench/tasks/semantic_schema_iclr2027.jsonl \
  --adapter langgraph_react_guarded \
  --model gpt-5.4-mini \
  --env both \
  --start-index 0 \
  --limit 1 \
  --max-steps 8
```

## Expanded Cross-Agent Runs

The paper-facing GPT-only expanded run uses public full-framework adapters:

```bash
ADAPTERS="langgraph_react_full smolagents_toolcalling autogen_tool_agent" \
bash toxictool_bench/run_expanded_full_adapters.sh gpt-5.4-mini
```

The expanded task files are:

```text
toxictool_bench/tasks/numerical_iclr2027.jsonl
toxictool_bench/tasks/semantic_schema_iclr2027.jsonl
```

## Cross-Model Runs

Use the smaller 34-task numerical and 24-task semantic/schema suites for cross-model evaluation:

```bash
bash toxictool_bench/run_semantic_schema_full_adapters.sh gpt-5.4-mini
bash toxictool_bench/run_semantic_schema_full_adapters.sh claude-sonnet-4-6
bash toxictool_bench/run_semantic_schema_full_adapters.sh Qwen3.6-35B-A3B-no-thinking
```

For numerical cross-model runs:

```bash
bash toxictool_bench/run_expanded_full_adapters.sh gpt-5.4-mini toxictool_bench/tasks/numerical_expanded.jsonl
bash toxictool_bench/run_expanded_full_adapters.sh claude-sonnet-4-6 toxictool_bench/tasks/numerical_expanded.jsonl
bash toxictool_bench/run_expanded_full_adapters.sh Qwen3.6-35B-A3B-no-thinking toxictool_bench/tasks/numerical_expanded.jsonl
```

## LangGraph Guarded Verification Ablation

Run the six-way ablation on a task file:

```bash
TOXICTOOL_BASELINE_DIR=/path/to/baseline_agent \
ADAPTERS="langgraph_react_full langgraph_react_caution langgraph_react_expectation_only langgraph_react_verification_only langgraph_react_guarded langgraph_react_guarded_light" \
bash toxictool_bench/run_langgraph_guard_ablation.sh \
  gpt-5.4-mini toxictool_bench/tasks/semantic_schema_iclr2027.jsonl
```

Numerical expanded ablation:

```bash
TOXICTOOL_BASELINE_DIR=/path/to/baseline_agent \
ADAPTERS="langgraph_react_full langgraph_react_caution langgraph_react_expectation_only langgraph_react_verification_only langgraph_react_guarded langgraph_react_guarded_light" \
bash toxictool_bench/run_langgraph_guard_ablation.sh \
  gpt-5.4-mini toxictool_bench/tasks/numerical_iclr2027.jsonl
```

Multi-table join extension:

```bash
TOXICTOOL_BASELINE_DIR=/path/to/baseline_agent \
ADAPTERS="langgraph_react_full langgraph_react_guarded langgraph_react_guarded_light" \
bash toxictool_bench/run_langgraph_guard_ablation.sh \
  gpt-5.4-mini toxictool_bench/tasks/realistic_extension_iclr2027.jsonl
```

## AutoGen Guarded Verification Replication

Run AutoGen verification-only and guarded variants on a task file:

```bash
TOXICTOOL_BASELINE_DIR=/path/to/baseline_agent \
ADAPTERS="autogen_verification_only autogen_guarded" \
bash toxictool_bench/run_autogen_guard_replication.sh \
  gpt-5.4-mini toxictool_bench/tasks/semantic_schema_iclr2027.jsonl
```

For long runs, use chunks:

```bash
TOXICTOOL_BASELINE_DIR=/path/to/baseline_agent \
START_INDEX=0 LIMIT=20 ADAPTERS="autogen_guarded" \
bash toxictool_bench/run_autogen_guard_replication.sh \
  gpt-5.4-mini toxictool_bench/tasks/numerical_iclr2027.jsonl
```

## Summaries and Confidence Intervals

Bootstrap confidence intervals:

```bash
python3 toxictool_bench/bootstrap_ci.py \
  toxictool_bench/results/RESULT_1.jsonl \
  toxictool_bench/results/RESULT_2.jsonl \
  --output toxictool_bench/results/bootstrap_ci.csv \
  --iterations 2000
```

Static paper check:

```bash
python3 toxictool_bench/check_paper_static.py --main main.tex
```

Tests:

```bash
python3 -m pytest toxictool_bench/tests -q
```

## Outputs

Results are written to:

```text
toxictool_bench/results/*.jsonl
toxictool_bench/results/*.summary.json
toxictool_bench/results/*.csv
```

Current paper-facing summary artifacts:

```text
toxictool_bench/results/langgraph_guarded_ablation_summary.csv
toxictool_bench/results/langgraph_guarded_ablation_suite_summary.csv
toxictool_bench/results/langgraph_guarded_overhead_summary.csv
toxictool_bench/results/langgraph_guarded_bootstrap_ci.csv
toxictool_bench/results/langgraph_multitable_extension_summary.csv
toxictool_bench/results/autogen_guarded_replication_summary.csv
toxictool_bench/results/autogen_guarded_replication_suite_summary.csv
toxictool_bench/results/autogen_guarded_replication_bootstrap_ci.csv
```
