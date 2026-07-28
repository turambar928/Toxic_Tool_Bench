#!/usr/bin/env bash
set -euo pipefail

MODEL="${1:-gpt-5.4-mini}"
TASKS="${2:-toxictool_bench/tasks/semantic_schema_iclr2027.jsonl}"
API_FILE="${API_FILE:-api}"
PYTHONWARNINGS="${PYTHONWARNINGS:-ignore::UserWarning}"
MAX_STEPS="${MAX_STEPS:-8}"
MAX_TOKENS="${MAX_TOKENS:-2048}"
START_INDEX="${START_INDEX:-0}"
LIMIT="${LIMIT:-0}"
BASELINE_DIR="${TOXICTOOL_BASELINE_DIR:-}"

ADAPTERS="${ADAPTERS:-autogen_tool_agent autogen_verification_only autogen_guarded}"
PYTHONPATH_VALUE="toxictool_bench"
if [[ -n "$BASELINE_DIR" ]]; then
  PYTHONPATH_VALUE="${PYTHONPATH_VALUE}:${BASELINE_DIR}/autogen/python/packages/autogen-core/src:${BASELINE_DIR}/autogen/python/packages/autogen-agentchat/src:${BASELINE_DIR}/autogen/python/packages/autogen-ext/src"
fi

for adapter in $ADAPTERS; do
  PYTHONWARNINGS="$PYTHONWARNINGS" PYTHONPATH="$PYTHONPATH_VALUE:${PYTHONPATH:-}" python3 toxictool_bench/run_full_bench.py \
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
