# ToxicBench Run Commands

All commands are intended to be run from the repository root:

```bash
cd /home/taozifu2025/toxicbench
```

## 1. Local smoke test

No API call:

```bash
python3 toxictool_bench/run_bench.py \
  --agent-profile heuristic_naive \
  --env both \
  --limit 2
```

Guarded-verification local smoke test:

```bash
python3 toxictool_bench/run_bench.py \
  --agent-profile heuristic_ibf \
  --env both \
  --limit 2
```

## 2. Check available models

```bash
python3 toxictool_bench/run_bench.py --list-models
```

Recommended first models:

```text
gpt-5.4-mini
claude-sonnet-4-6
Qwen3.6-35B-A3B-no-thinking
```

## 3. Pilot experiment

Vanilla ReAct:

```bash
python3 toxictool_bench/run_bench.py \
  --agent-profile react \
  --model gpt-5.4-mini \
  --env both
```

Caution prompt:

```bash
python3 toxictool_bench/run_bench.py \
  --agent-profile caution \
  --model gpt-5.4-mini \
  --env both
```

Guarded-verification defense:

```bash
python3 toxictool_bench/run_bench.py \
  --agent-profile ibf \
  --model gpt-5.4-mini \
  --env both
```

DataFrame Router prompt-style adapter:

```bash
python3 toxictool_bench/run_bench.py \
  --agent-profile dataframe_router_prompt \
  --model gpt-5.4-mini \
  --env both
```

DA-Agent prompt-style adapter:

```bash
python3 toxictool_bench/run_bench.py \
  --agent-profile da_agent_prompt \
  --model gpt-5.4-mini \
  --env both
```

OpenHands/CodeAct-style profile:

```bash
python3 toxictool_bench/run_bench.py \
  --agent-profile openhands_codeact \
  --model gpt-5.4-mini \
  --env both
```

Plan-and-execute profile:

```bash
python3 toxictool_bench/run_bench.py \
  --agent-profile plan_execute \
  --model gpt-5.4-mini \
  --env both
```

Reflexion-style profile:

```bash
python3 toxictool_bench/run_bench.py \
  --agent-profile reflexion \
  --model gpt-5.4-mini \
  --env both
```

## 4. Cross-model experiment

```bash
for model in gpt-5.4-mini claude-sonnet-4-6 Qwen3.6-35B-A3B-no-thinking; do
  for profile in react caution ibf openhands_codeact plan_execute reflexion dataframe_router_prompt da_agent_prompt; do
    python3 toxictool_bench/run_bench.py \
      --agent-profile "$profile" \
      --model "$model" \
      --env both
  done
done
```

## 5. Outputs

Results are written to:

```text
toxictool_bench/results/*.jsonl
toxictool_bench/results/*.summary.json
```

Each JSONL row contains:

```text
task_id
agent_profile
model
environment
tool_events
final_answer
metrics
```

The API key is read from `api` at runtime and is not written to output files.

## 6. Full Framework Adapters

Before running full adapters, check that the local framework checkouts and Python imports are available:

```bash
python3 toxictool_bench/check_adapter_readiness.py
```

If the heavyweight adapter checkouts live outside this Git repository, point the
runner to them without copying them into Git:

```bash
export TOXICTOOL_BASELINE_DIR=/path/to/baseline_agent
export TOXICTOOL_DATAFRAME_ROUTER_SRC=/path/to/dataframe_router/src
python3 toxictool_bench/check_adapter_readiness.py
```

LangGraph ReAct full adapter:

```bash
PYTHONPATH=toxictool_bench:baseline_agent/langgraph/libs/langgraph:baseline_agent/langgraph/libs/prebuilt \
python3 toxictool_bench/run_full_bench.py \
  --adapter langgraph_react_full \
  --model gpt-5.4-mini \
  --env both
```

smolagents ToolCallingAgent full adapter:

```bash
PYTHONPATH=toxictool_bench:baseline_agent/smolagents/src \
python3 toxictool_bench/run_full_bench.py \
  --adapter smolagents_toolcalling \
  --model gpt-5.4-mini \
  --env both
```

AutoGen AssistantAgent full adapter:

```bash
PYTHONPATH=toxictool_bench:baseline_agent/autogen/python/packages/autogen-core/src:baseline_agent/autogen/python/packages/autogen-agentchat/src:baseline_agent/autogen/python/packages/autogen-ext/src \
python3 toxictool_bench/run_full_bench.py \
  --adapter autogen_tool_agent \
  --model gpt-5.4-mini \
  --env both
```

DataFrame Router full adapter:

```bash
PYTHONPATH=toxictool_bench:src \
python3 toxictool_bench/run_full_bench.py \
  --adapter dataframe_router \
  --model gpt-5.4-mini \
  --env both
```

PandasAI DataFrame full adapter:

```bash
PYTHONPATH=toxictool_bench:baseline_agent/pandas-ai:baseline_agent/pandas-ai/extensions/llms/litellm \
python3 toxictool_bench/run_full_bench.py \
  --adapter pandasai_dataframe \
  --model gpt-5.4-mini \
  --env both
```

DA-Agent full adapter:

```bash
PYTHONPATH=toxictool_bench:baseline_agent/da-agent \
python3 toxictool_bench/run_full_bench.py \
  --adapter da_agent_full \
  --model gpt-5.4-mini \
  --env both \
  --max-steps 10
```

## 7. Expanded Full-Adapter Pilot

Use the ICLR 2027 numerical candidate set by default:

```bash
bash toxictool_bench/run_expanded_full_adapters.sh
```

## 7.5 ICLR 2027 Candidate Expansion

Generate 60 numerical tasks and 60 semantic/schema tasks with severity labels:

```bash
python3 toxictool_bench/generate_iclr2027_tasks.py
```

Generated task files:

```text
toxictool_bench/tasks/numerical_iclr2027.jsonl
toxictool_bench/tasks/semantic_schema_iclr2027.jsonl
```

Run a small smoke test on the expanded numerical suite:

```bash
python3 toxictool_bench/run_full_bench.py \
  --tasks toxictool_bench/tasks/numerical_iclr2027.jsonl \
  --api-file api \
  --adapter dataframe_router \
  --model gpt-5.4-mini \
  --env both \
  --limit 5
```

Run the standard ICLR 2027 candidate matrix on both 60-task suites:

```bash
bash toxictool_bench/run_iclr2027_experiments.sh
```

Useful scoped variants:

```bash
LIMIT=5 ADAPTERS="dataframe_router dataframe_router_guarded" \
  bash toxictool_bench/run_iclr2027_experiments.sh

START_INDEX=10 LIMIT=10 ADAPTERS="dataframe_router_guarded_light" \
  bash toxictool_bench/run_iclr2027_experiments.sh

MODEL=claude-sonnet-4-6 ADAPTERS="langgraph_react_full smolagents_toolcalling autogen_tool_agent" \
  bash toxictool_bench/run_iclr2027_experiments.sh
```

Chunked long-run pattern for the 60-task suites:

```bash
for start in 0 10 20 30 40 50; do
  START_INDEX="$start" LIMIT=10 \
  ADAPTERS="dataframe_router dataframe_router_caution dataframe_router_expectation_only dataframe_router_verification_only dataframe_router_guarded dataframe_router_guarded_light" \
  TASK_SUITES="toxictool_bench/tasks/semantic_schema_iclr2027.jsonl toxictool_bench/tasks/numerical_iclr2027.jsonl" \
  bash toxictool_bench/run_iclr2027_experiments.sh
done
```

Chunked result filenames include `_start<index>_limit<count>` before `.jsonl`.

Summarize completed chunks automatically:

```bash
python3 toxictool_bench/summarize_chunked_matrix.py \
  --tasks toxictool_bench/tasks/semantic_schema_iclr2027.jsonl toxictool_bench/tasks/numerical_iclr2027.jsonl \
  --adapters dataframe_router dataframe_router_caution dataframe_router_expectation_only dataframe_router_verification_only dataframe_router_guarded dataframe_router_guarded_light \
  --starts 0 5 \
  --limit 5 \
  --output-prefix toxictool_bench/results/iclr2027_dataframe_router_ablation_auto
```

The summarizer writes suite-level summaries, a combined summary, and a manifest
of the exact raw JSONL files selected for each suite/adapter/chunk.

Run the DataFrame Router guard comparison on the expanded semantic/schema suite. By default this covers six variants:

```text
dataframe_router
dataframe_router_caution
dataframe_router_expectation_only
dataframe_router_verification_only
dataframe_router_guarded
dataframe_router_guarded_light
```

```bash
bash toxictool_bench/run_dataframe_router_guard_ablation.sh gpt-5.4-mini \
  toxictool_bench/tasks/semantic_schema_iclr2027.jsonl
```

Summarize with severity breakdown:

```bash
python3 toxictool_bench/summarize_results.py \
  toxictool_bench/results/RESULT.rescored.jsonl \
  --overall-output toxictool_bench/results/iclr2027_summary.csv \
  --poison-output toxictool_bench/results/iclr2027_poison_summary.csv \
  --severity-output toxictool_bench/results/iclr2027_severity_summary.csv
```

Run each completed full adapter:

```bash
PYTHONPATH=toxictool_bench:baseline_agent/langgraph/libs/langgraph:baseline_agent/langgraph/libs/prebuilt \
python3 toxictool_bench/run_full_bench.py --tasks "$TASKS" \
  --adapter langgraph_react_full --model gpt-5.4-mini --env both --max-steps 8

PYTHONPATH=toxictool_bench:baseline_agent/smolagents/src \
python3 toxictool_bench/run_full_bench.py --tasks "$TASKS" \
  --adapter smolagents_toolcalling --model gpt-5.4-mini --env both --max-steps 8

PYTHONPATH=toxictool_bench:src \
python3 toxictool_bench/run_full_bench.py --tasks "$TASKS" \
  --adapter dataframe_router --model gpt-5.4-mini --env both --max-steps 8

PYTHONPATH=toxictool_bench:baseline_agent/pandas-ai:baseline_agent/pandas-ai/extensions/llms/litellm \
python3 toxictool_bench/run_full_bench.py --tasks "$TASKS" \
  --adapter pandasai_dataframe --model gpt-5.4-mini --env both --max-steps 8

PYTHONPATH=toxictool_bench:baseline_agent/autogen/python/packages/autogen-core/src:baseline_agent/autogen/python/packages/autogen-agentchat/src:baseline_agent/autogen/python/packages/autogen-ext/src \
python3 toxictool_bench/run_full_bench.py --tasks "$TASKS" \
  --adapter autogen_tool_agent --model gpt-5.4-mini --env both --max-steps 8

PYTHONPATH=toxictool_bench:baseline_agent/da-agent \
python3 toxictool_bench/run_full_bench.py --tasks "$TASKS" \
  --adapter da_agent_full --model gpt-5.4-mini --env both --max-steps 10
```

Equivalent scripted run:

```bash
MODEL=gpt-5.4-mini \
bash toxictool_bench/run_expanded_full_adapters.sh
```

Rescore an expanded result file:

```bash
python3 toxictool_bench/rescore_results.py \
  --tasks toxictool_bench/tasks/numerical_expanded.jsonl \
  toxictool_bench/results/RESULT.jsonl
```

Generate overall and poison-type CSV summaries from rescored JSONL files:

```bash
python3 toxictool_bench/summarize_results.py \
  toxictool_bench/results/EXPANDED_RESULT_1.rescored.jsonl \
  toxictool_bench/results/EXPANDED_RESULT_2.rescored.jsonl \
  --overall-output toxictool_bench/results/cross_model_summary.csv \
  --poison-output toxictool_bench/results/poison_type_summary.csv
```

## 8. Cross-Model Full-Adapter Experiment

Recommended model set:

```text
gpt-5.4-mini
claude-sonnet-4-6
Qwen3.6-35B-A3B-no-thinking
```

Run the same expanded commands above while changing `--model`. For cost control, run one model at a time and rescore before starting the next model.

Scripted cross-model loop:

```bash
for model in gpt-5.4-mini claude-sonnet-4-6 Qwen3.6-35B-A3B-no-thinking; do
  MODEL="$model" bash toxictool_bench/run_expanded_full_adapters.sh
done
```

## 9. Semantic/Schema Expansion

Use the 24-task semantic/schema set:

```bash
TASKS=toxictool_bench/tasks/semantic_schema.jsonl
```

Single-adapter run:

```bash
python3 toxictool_bench/run_full_bench.py \
  --tasks "$TASKS" \
  --adapter langgraph_react_full \
  --model gpt-5.4-mini \
  --env both \
  --max-steps 8
```

Scripted run over practical-speed adapters:

```bash
bash toxictool_bench/run_semantic_schema_full_adapters.sh gpt-5.4-mini
```

## 10. DataFrame Router Guarded Ablation

Run the full defense ablation matrix on the semantic/schema suite:

```bash
bash toxictool_bench/run_dataframe_router_guard_ablation.sh \
  gpt-5.4-mini \
  toxictool_bench/tasks/semantic_schema_iclr2027.jsonl
```

The default matrix is:

```text
base:              dataframe_router
caution prompt:    dataframe_router_caution
expectation only:  dataframe_router_expectation_only
verification only: dataframe_router_verification_only
full guard:        dataframe_router_guarded
light guard:       dataframe_router_guarded_light
```

Restrict the matrix with `ADAPTERS`:

```bash
ADAPTERS="dataframe_router dataframe_router_verification_only dataframe_router_guarded" \
  bash toxictool_bench/run_dataframe_router_guard_ablation.sh \
    gpt-5.4-mini \
    toxictool_bench/tasks/semantic_schema_iclr2027.jsonl
```

Run guarded only on semantic/schema:

```bash
python3 toxictool_bench/run_full_bench.py \
  --tasks toxictool_bench/tasks/semantic_schema_iclr2027.jsonl \
  --api-file api \
  --adapter dataframe_router_guarded \
  --model gpt-5.4-mini \
  --env both \
  --max-steps 10 \
  --max-tokens 3072 \
  --start-index 10 \
  --limit 10
```

Run guarded only on the numerical suite:

```bash
python3 toxictool_bench/run_full_bench.py \
  --tasks toxictool_bench/tasks/numerical_iclr2027.jsonl \
  --api-file api \
  --adapter dataframe_router_guarded \
  --model gpt-5.4-mini \
  --env both \
  --max-steps 10 \
  --max-tokens 3072
```

Run the light guarded variant:

```bash
python3 toxictool_bench/run_full_bench.py \
  --tasks toxictool_bench/tasks/semantic_schema_iclr2027.jsonl \
  --api-file api \
  --adapter dataframe_router_guarded_light \
  --model gpt-5.4-mini \
  --env both \
  --max-steps 10 \
  --max-tokens 3072
```

Summarize against the existing base run:

```bash
python3 toxictool_bench/rescore_results.py \
  --tasks toxictool_bench/tasks/semantic_schema.jsonl \
  toxictool_bench/results/RESULT_dataframe_router_guarded.jsonl

python3 toxictool_bench/summarize_results.py \
  toxictool_bench/results/20260717-152700_dataframe_router_gpt-5.4-mini_both.rescored.jsonl \
  toxictool_bench/results/RESULT_dataframe_router_guarded.rescored.jsonl \
  --overall-output toxictool_bench/results/dataframe_router_guarded_semantic_ablation_summary.csv \
  --poison-output toxictool_bench/results/dataframe_router_guarded_semantic_ablation_poison_summary.csv
```

Current completed guarded result:

```text
toxictool_bench/results/20260717-214348_dataframe_router_guarded_gpt-5.4-mini_both.rescored.jsonl
toxictool_bench/results/20260718-153208_dataframe_router_guarded_light_gpt-5.4-mini_both.rescored.jsonl
toxictool_bench/results/dataframe_router_guarded_semantic_ablation_summary.csv
toxictool_bench/results/dataframe_router_guarded_semantic_ablation_poison_summary.csv
toxictool_bench/results/20260718-003358_dataframe_router_guarded_gpt-5.4-mini_both.rescored.jsonl
toxictool_bench/results/20260718-160351_dataframe_router_guarded_light_gpt-5.4-mini_both.rescored.jsonl
toxictool_bench/results/dataframe_router_guarded_numerical_ablation_summary.csv
toxictool_bench/results/dataframe_router_guarded_numerical_ablation_poison_summary.csv
```

Guard overhead and case-study extraction:

```bash
python3 toxictool_bench/analyze_guard_ablation.py \
  --output-csv toxictool_bench/results/dataframe_router_guarded_overhead_summary.csv \
  --output-md GUARDED_CASE_STUDIES.md \
  --semantic-base toxictool_bench/results/20260717-152700_dataframe_router_gpt-5.4-mini_both.rescored.jsonl \
  --semantic-full toxictool_bench/results/20260717-214348_dataframe_router_guarded_gpt-5.4-mini_both.rescored.jsonl \
  --semantic-light toxictool_bench/results/20260718-153208_dataframe_router_guarded_light_gpt-5.4-mini_both.rescored.jsonl \
  --numerical-base toxictool_bench/results/20260707-122940_dataframe_router_gpt-5.4-mini_both.rescored.jsonl \
  --numerical-full toxictool_bench/results/20260718-003358_dataframe_router_guarded_gpt-5.4-mini_both.rescored.jsonl \
  --numerical-light toxictool_bench/results/20260718-160351_dataframe_router_guarded_light_gpt-5.4-mini_both.rescored.jsonl
```

Bootstrap confidence intervals:

```bash
python3 toxictool_bench/bootstrap_ci.py \
  RESULT_1.rescored.jsonl RESULT_2.rescored.jsonl \
  --output toxictool_bench/results/BOOTSTRAP_OUTPUT.csv \
  --iterations 2000 \
  --seed 13
```

Current generated CI files:

```text
toxictool_bench/results/numerical_gpt_bootstrap_ci.csv
toxictool_bench/results/numerical_cross_model_bootstrap_ci.csv
toxictool_bench/results/semantic_schema_cross_model_bootstrap_ci.csv
toxictool_bench/results/dataframe_router_guarded_bootstrap_ci.csv
```

The semantic/schema suite currently includes:

```text
label_swap / treatment_control_flip
column_semantic_swap
stale_metadata
biased_retrieval
```
