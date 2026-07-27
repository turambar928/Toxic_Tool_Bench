#!/usr/bin/env bash
set -u

MODEL="${MODEL:-claude-sonnet-4-6}"
ENVIRONMENT="${ENVIRONMENT:-both}"
MAX_STEPS="${MAX_STEPS:-10}"
MAX_TOKENS="${MAX_TOKENS:-3072}"
LIMIT="${LIMIT:-5}"
STARTS="${STARTS:-0 5 10 15 20 25 30 35 40 45 50 55}"
TASK_SUITES="${TASK_SUITES:-toxictool_bench/tasks/numerical_iclr2027.jsonl toxictool_bench/tasks/semantic_schema_iclr2027.jsonl}"
ADAPTERS="${ADAPTERS:-langgraph_react_full smolagents_toolcalling dataframe_router pandasai_dataframe autogen_tool_agent}"
OUTPUT_PREFIX="${OUTPUT_PREFIX:-toxictool_bench/results/iclr2027_${MODEL}_expanded_cross_agent}"
BASELINE_DIR="${TOXICTOOL_BASELINE_DIR:-/path/to/baseline_agent}"
DATAFRAME_ROUTER_SRC="${TOXICTOOL_DATAFRAME_ROUTER_SRC:-/path/to/dataframe_router/src}"

run_adapter() {
  local adapter="$1"
  local tasks="$2"
  local start="$3"
  local py_path="toxictool_bench"

  case "$adapter" in
    langgraph_react_full)
      py_path="$py_path:$BASELINE_DIR/langgraph/libs/langgraph:$BASELINE_DIR/langgraph/libs/prebuilt"
      ;;
    smolagents_toolcalling)
      py_path="$py_path:$BASELINE_DIR/smolagents/src"
      ;;
    dataframe_router*)
      py_path="$py_path:$DATAFRAME_ROUTER_SRC"
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
      printf 'Unknown adapter: %s\n' "$adapter" >&2
      return 2
      ;;
  esac

  printf '==> model=%s suite=%s adapter=%s start=%s limit=%s\n' "$MODEL" "$tasks" "$adapter" "$start" "$LIMIT"
  PYTHONPATH="$py_path" python3 toxictool_bench/run_full_bench.py \
    --tasks "$tasks" \
    --adapter "$adapter" \
    --model "$MODEL" \
    --env "$ENVIRONMENT" \
    --max-steps "$MAX_STEPS" \
    --max-tokens "$MAX_TOKENS" \
    --start-index "$start" \
    --limit "$LIMIT"
}

failures=()
for tasks in $TASK_SUITES; do
  for adapter in $ADAPTERS; do
    for start in $STARTS; do
      if ! TOXICTOOL_BASELINE_DIR="$BASELINE_DIR" TOXICTOOL_DATAFRAME_ROUTER_SRC="$DATAFRAME_ROUTER_SRC" run_adapter "$adapter" "$tasks" "$start"; then
        failures+=("$MODEL:$tasks:$adapter:start$start")
      fi
    done
  done
done

python3 toxictool_bench/summarize_chunked_matrix.py \
  --tasks $TASK_SUITES \
  --adapters $ADAPTERS \
  --starts $STARTS \
  --limit "$LIMIT" \
  --model "$MODEL" \
  --env "$ENVIRONMENT" \
  --output-prefix "$OUTPUT_PREFIX" \
  --allow-missing

if ((${#failures[@]})); then
  printf 'Failures:\n' >&2
  printf '%s\n' "${failures[@]}" >&2
  exit 1
fi
