#!/usr/bin/env bash
set -euo pipefail

MODEL="${1:-gpt-5.4-mini}"
TASKS="${2:-toxictool_bench/tasks/semantic_schema_iclr2027.jsonl}"
API_FILE="api"

ADAPTERS="${ADAPTERS:-dataframe_router dataframe_router_caution dataframe_router_expectation_only dataframe_router_verification_only dataframe_router_guarded dataframe_router_guarded_light}"

for adapter in $ADAPTERS; do
  python3 toxictool_bench/run_full_bench.py \
    --tasks "$TASKS" \
    --api-file "$API_FILE" \
    --adapter "$adapter" \
    --model "$MODEL" \
    --env both \
    --max-steps 10 \
    --max-tokens 3072
done
