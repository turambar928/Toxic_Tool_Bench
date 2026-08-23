#!/usr/bin/env bash
set -euo pipefail

TASKS="${TASKS:-toxictool_bench/tasks/numerical_iclr2027.jsonl}"
MODEL="${MODEL:-gpt-5.4-mini}"
ENVIRONMENT="${ENVIRONMENT:-both}"
START_INDEX="${START_INDEX:-0}"
LIMIT="${LIMIT:-0}"
BASELINE_DIR="${TOXICTOOL_BASELINE_DIR:-baseline_agent}"
ADAPTERS="${ADAPTERS:-langgraph_react_full smolagents_toolcalling pandasai_dataframe autogen_tool_agent}"

run_adapter() {
  local adapter="$1"
  local max_steps=8
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
      max_steps=10
      ;;
    *)
      echo "Unknown adapter: $adapter" >&2
      return 2
      ;;
  esac

  echo "==> Running $adapter on $MODEL"
  PYTHONPATH="$py_path" python3 toxictool_bench/run_full_bench.py \
    --tasks "$TASKS" \
    --adapter "$adapter" \
    --model "$MODEL" \
    --env "$ENVIRONMENT" \
    --max-steps "$max_steps" \
    --start-index "$START_INDEX" \
    --limit "$LIMIT"
}

for adapter in $ADAPTERS; do
  run_adapter "$adapter"
done
