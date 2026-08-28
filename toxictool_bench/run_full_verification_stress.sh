#!/usr/bin/env bash
set -euo pipefail

# Full repeated-observation stress matrix. This never claims source independence:
# all routes still read the same task data and backend.
MODEL="${MODEL:-gpt-5.4-mini}"
API_FILE="${API_FILE:-api}"
MAX_STEPS="${MAX_STEPS:-8}"
MAX_TOKENS="${MAX_TOKENS:-2048}"
PROBABILITIES="${PROBABILITIES:-0.25 0.50 0.75 1.00}"
ADAPTERS="${ADAPTERS:-langgraph_react_verification_only langgraph_react_double_pass langgraph_react_guarded}"
PYTHONPATH_VALUE="${PYTHONPATH_VALUE:-toxictool_bench}"

for tasks in \
  toxictool_bench/tasks/numerical_iclr2027.jsonl \
  toxictool_bench/tasks/semantic_schema_iclr2027.jsonl \
  toxictool_bench/tasks/realistic_extension_iclr2027.jsonl; do
  for probability in $PROBABILITIES; do
    for adapter in $ADAPTERS; do
      echo "==> tasks=$tasks probability=$probability adapter=$adapter model=$MODEL"
      PYTHONPATH="$PYTHONPATH_VALUE:${PYTHONPATH:-}" python3 toxictool_bench/run_full_bench.py \
        --tasks "$tasks" \
        --api-file "$API_FILE" \
        --adapter "$adapter" \
        --model "$MODEL" \
        --env toxic \
        --max-steps "$MAX_STEPS" \
        --max-tokens "$MAX_TOKENS" \
        --poison-repeat \
        --poison-probability "$probability"
    done
  done
done
