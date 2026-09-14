#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PREFIX="toxictool_bench/results/leakage_free_defense"

# The released manifest is authoritative; never rediscover logs by file mtime.
python3 toxictool_bench/sync_defense_paper.py
python3 toxictool_bench/summarize_verification_stress.py
python3 toxictool_bench/sync_supplementary_paper.py

python3 toxictool_bench/overhead_audit.py \
  --manifest "${PREFIX}_manifest.csv" \
  --output "${PREFIX}_overhead.csv"
