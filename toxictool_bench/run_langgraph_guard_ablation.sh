#!/usr/bin/env bash
set -euo pipefail

MODEL="${1:-gpt-5.4-mini}"
TASKS="${2:-toxictool_bench/tasks/semantic_schema_iclr2027.jsonl}"
API_FILE="${API_FILE:-api}"
MAX_STEPS="${MAX_STEPS:-10}"
MAX_TOKENS="${MAX_TOKENS:-3072}"
START_INDEX="${START_INDEX:-0}"
LIMIT="${LIMIT:-0}"
BASELINE_DIR="${TOXICTOOL_BASELINE_DIR:-}"

ADAPTERS="${ADAPTERS:-langgraph_react_full langgraph_react_caution langgraph_react_expectation_only langgraph_react_verification_only langgraph_react_double_pass langgraph_react_guarded langgraph_react_guarded_light}"
PYTHONPATH_VALUE="toxictool_bench"
if [[ -n "$BASELINE_DIR" ]]; then
  PYTHONPATH_VALUE="${PYTHONPATH_VALUE}:${BASELINE_DIR}/langgraph/libs/langgraph:${BASELINE_DIR}/langgraph/libs/prebuilt"
fi

for adapter in $ADAPTERS; do
  PYTHONPATH="$PYTHONPATH_VALUE:${PYTHONPATH:-}" python3 toxictool_bench/run_full_bench.py \
    --tasks "$TASKS" \
    --api-file "$API_FILE" \
    --adapter "$adapter" \
    --model "$MODEL" \
    --env both \
    --max-steps "$MAX_STEPS" \
    --max-tokens "$MAX_TOKENS" \
    --start-index "$START_INDEX" \
    --limit "$LIMIT"
done
