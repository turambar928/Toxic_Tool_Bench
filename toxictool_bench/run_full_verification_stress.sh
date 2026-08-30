#!/usr/bin/env bash
set -euo pipefail

# Full repeated-observation stress matrix. This never claims source independence:
# all routes still read the same task data and backend. Runs are chunked and
# stored by probability so interrupted matrices can resume without ambiguity.
MODEL="${MODEL:-claude-haiku-4-5-20251001}"
API_FILE="${API_FILE:-api}"
MAX_STEPS="${MAX_STEPS:-6}"
MAX_TOKENS="${MAX_TOKENS:-1536}"
PROBABILITIES="${PROBABILITIES:-0.25 0.50 0.75 1.00}"
ADAPTERS="${ADAPTERS:-langgraph_react_verification_only langgraph_react_double_pass langgraph_react_guarded}"
PYTHONPATH_VALUE="${PYTHONPATH_VALUE:-toxictool_bench}"
CHUNK_SIZE="${CHUNK_SIZE:-5}"
OUTPUT_ROOT="${OUTPUT_ROOT:-toxictool_bench/results/verification_stress}"
TASK_FILES="${TASK_FILES:-toxictool_bench/tasks/numerical_iclr2027.jsonl toxictool_bench/tasks/semantic_schema_iclr2027.jsonl toxictool_bench/tasks/realistic_extension_iclr2027.jsonl}"

chunk_complete() {
  local output_dir="$1" adapter="$2" start="$3" limit="$4"
  python3 - "$output_dir" "$adapter" "$MODEL" "$start" "$limit" <<'PY'
import json
import sys
from pathlib import Path

output_dir, adapter, model, start, limit = sys.argv[1:]
expected = int(limit)
pattern = f"*_{adapter}_{model}_toxic_start{start}_limit{limit}.jsonl"
for path in sorted(Path(output_dir).glob(pattern), reverse=True):
    try:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except (OSError, json.JSONDecodeError):
        continue
    if len(rows) == expected and len({row.get("task_id") for row in rows}) == expected:
        raise SystemExit(0)
raise SystemExit(1)
PY
}

for tasks in $TASK_FILES; do
  suite="$(basename "$tasks" .jsonl)"
  total="$(wc -l < "$tasks")"
  for probability in $PROBABILITIES; do
    probability_tag="$(printf '%03d' "$(python3 -c "print(round(float('$probability') * 100))")")"
    output_dir="$OUTPUT_ROOT/$suite/p$probability_tag"
    mkdir -p "$output_dir"
    for adapter in $ADAPTERS; do
      for ((start = 0; start < total; start += CHUNK_SIZE)); do
        limit="$CHUNK_SIZE"
        if ((start + limit > total)); then
          limit=$((total - start))
        fi
        if chunk_complete "$output_dir" "$adapter" "$start" "$limit"; then
          echo "==> skip complete suite=$suite probability=$probability adapter=$adapter start=$start limit=$limit"
          continue
        fi
        echo "==> run suite=$suite probability=$probability adapter=$adapter start=$start limit=$limit model=$MODEL"
        PYTHONPATH="$PYTHONPATH_VALUE:${PYTHONPATH:-}" python3 toxictool_bench/run_full_bench.py \
          --tasks "$tasks" \
          --api-file "$API_FILE" \
          --output-dir "$output_dir" \
          --adapter "$adapter" \
          --model "$MODEL" \
          --env toxic \
          --max-steps "$MAX_STEPS" \
          --max-tokens "$MAX_TOKENS" \
          --start-index "$start" \
          --limit "$limit" \
          --poison-repeat \
          --poison-probability "$probability"
      done
    done
  done
done
