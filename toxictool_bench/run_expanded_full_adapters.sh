#!/usr/bin/env bash
set -euo pipefail

TASKS="${TASKS:-toxictool_bench/tasks/numerical_expanded.jsonl}"
MODEL="${MODEL:-gpt-5.4-mini}"
ENVIRONMENT="${ENVIRONMENT:-both}"
ADAPTERS="${ADAPTERS:-langgraph_react_full smolagents_toolcalling data2mcp_dataframe pandasai_dataframe autogen_tool_agent da_agent_full}"

run_adapter() {
  local adapter="$1"
  local max_steps=8
  local py_path="toxictool_bench"

  case "$adapter" in
    langgraph_react_full)
      py_path="$py_path:baseline_agent/langgraph/libs/langgraph:baseline_agent/langgraph/libs/prebuilt"
      ;;
    smolagents_toolcalling)
      py_path="$py_path:baseline_agent/smolagents/src"
      ;;
    data2mcp_dataframe)
      py_path="$py_path:src"
      ;;
    pandasai_dataframe)
      py_path="$py_path:baseline_agent/pandas-ai:baseline_agent/pandas-ai/extensions/llms/litellm"
      ;;
    autogen_tool_agent)
      py_path="$py_path:baseline_agent/autogen/python/packages/autogen-core/src:baseline_agent/autogen/python/packages/autogen-agentchat/src:baseline_agent/autogen/python/packages/autogen-ext/src"
      ;;
    da_agent_full)
      py_path="$py_path:baseline_agent/da-agent"
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
    --max-steps "$max_steps"
}

for adapter in $ADAPTERS; do
  run_adapter "$adapter"
done
