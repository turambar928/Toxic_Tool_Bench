#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PREFIX="toxictool_bench/results/leakage_free_defense"

python3 toxictool_bench/summarize_chunked_matrix.py \
  --tasks \
    toxictool_bench/tasks/numerical_iclr2027.jsonl \
    toxictool_bench/tasks/semantic_schema_iclr2027.jsonl \
  --adapters \
    langgraph_react_full \
    langgraph_react_verification_only \
    langgraph_react_double_pass \
    langgraph_react_guarded \
  --suite-chunks 'numerical_iclr2027=0:20,20:20,40:20' \
  --suite-chunks 'semantic_schema_iclr2027=0:5,5:5,10:5,15:5,20:20,40:5,45:5,50:5,55:5' \
  --model claude-haiku-4-5-20251001 \
  --env both \
  --output-prefix "$PREFIX" \
  --bootstrap-iterations 5000 \
  --seed 20260830

python3 toxictool_bench/overhead_audit.py \
  --manifest "${PREFIX}_manifest.csv" \
  --output "${PREFIX}_overhead.csv"
