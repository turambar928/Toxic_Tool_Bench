#!/usr/bin/env bash
set -euo pipefail

MODEL="${1:-gpt-5.4-mini}"
TASKS="toxictool_bench/tasks/semantic_schema.jsonl"
API_FILE="api"

ADAPTERS=(
  "langgraph_react_full"
  "smolagents_toolcalling"
  "data2mcp_dataframe"
  "pandasai_dataframe"
  "autogen_tool_agent"
)

for adapter in "${ADAPTERS[@]}"; do
  max_steps=8
  max_tokens=2048
  case "$adapter" in
    data2mcp_dataframe)
      max_steps=10
      max_tokens=3072
      ;;
    pandasai_dataframe)
      max_steps=4
      max_tokens=2048
      ;;
  esac

  python3 toxictool_bench/run_full_bench.py \
    --tasks "$TASKS" \
    --api-file "$API_FILE" \
    --adapter "$adapter" \
    --model "$MODEL" \
    --env both \
    --max-steps "$max_steps" \
    --max-tokens "$max_tokens"
done
