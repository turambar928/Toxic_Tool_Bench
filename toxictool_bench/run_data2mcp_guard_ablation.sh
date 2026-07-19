#!/usr/bin/env bash
set -euo pipefail

MODEL="${1:-gpt-5.4-mini}"
TASKS="${2:-toxictool_bench/tasks/semantic_schema_iclr2027.jsonl}"
API_FILE="api"

for adapter in data2mcp_dataframe data2mcp_dataframe_guarded data2mcp_dataframe_guarded_light; do
  python3 toxictool_bench/run_full_bench.py \
    --tasks "$TASKS" \
    --api-file "$API_FILE" \
    --adapter "$adapter" \
    --model "$MODEL" \
    --env both \
    --max-steps 10 \
    --max-tokens 3072
done
