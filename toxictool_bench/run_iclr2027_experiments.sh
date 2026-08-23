#!/usr/bin/env bash
set -euo pipefail

MODEL="${MODEL:-gpt-5.4-mini}"
ENVIRONMENT="${ENVIRONMENT:-both}"
MAX_STEPS="${MAX_STEPS:-10}"
MAX_TOKENS="${MAX_TOKENS:-3072}"
START_INDEX="${START_INDEX:-0}"
LIMIT="${LIMIT:-0}"
BASELINE_DIR="${TOXICTOOL_BASELINE_DIR:-baseline_agent}"
TASK_SUITES="${TASK_SUITES:-toxictool_bench/tasks/numerical_iclr2027.jsonl toxictool_bench/tasks/semantic_schema_iclr2027.jsonl}"
ADAPTERS="${ADAPTERS:-langgraph_react_full smolagents_toolcalling pandasai_dataframe autogen_tool_agent}"

run_adapter() {
  local adapter="$1"
  local tasks="$2"
  local py_path="toxictool_bench"

  case "$adapter" in
    langgraph_react_full)
      py_path="$py_path:$BASELINE_DIR/langgraph/libs/langgraph:$BASELINE_DIR/langgraph/libs/prebuilt"
      ;;
    smolagents_toolcalling)
      py_path="$py_path:$BASELINE_DIR/smolagents/src"
      ;;
    pandasai_dataframe)
      py_path="$py_path:$BASELINE_DIR/pandas-ai:$BASELINE_DIR/pandas-ai/extensions/llms/litellm"
      ;;
    autogen_tool_agent)
      py_path="$py_path:$BASELINE_DIR/autogen/python/packages/autogen-core/src:$BASELINE_DIR/autogen/python/packages/autogen-agentchat/src:$BASELINE_DIR/autogen/python/packages/autogen-ext/src"
      ;;
    da_agent_full)
      py_path="$py_path:$BASELINE_DIR/da-agent"
      ;;
    *)
      echo "Unknown adapter: $adapter" >&2
      return 2
      ;;
  esac

  echo "==> $adapter | $MODEL | $tasks"
  if [[ "$LIMIT" != "0" ]]; then
    PYTHONPATH="$py_path" python3 toxictool_bench/run_full_bench.py \
      --tasks "$tasks" \
      --adapter "$adapter" \
      --model "$MODEL" \
      --env "$ENVIRONMENT" \
      --max-steps "$MAX_STEPS" \
      --max-tokens "$MAX_TOKENS" \
      --start-index "$START_INDEX" \
      --limit "$LIMIT"
  else
    PYTHONPATH="$py_path" python3 toxictool_bench/run_full_bench.py \
      --tasks "$tasks" \
      --adapter "$adapter" \
      --model "$MODEL" \
      --env "$ENVIRONMENT" \
      --max-steps "$MAX_STEPS" \
      --max-tokens "$MAX_TOKENS" \
      --start-index "$START_INDEX"
  fi
}

python3 toxictool_bench/check_adapter_readiness.py || true

for tasks in $TASK_SUITES; do
  for adapter in $ADAPTERS; do
    run_adapter "$adapter" "$tasks"
  done
done
