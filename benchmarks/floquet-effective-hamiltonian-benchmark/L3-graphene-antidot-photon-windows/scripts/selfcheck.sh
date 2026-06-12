#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEV_OUT="${TMPDIR:-/tmp}/floquet_l3_windows_dev_out.csv"

python "$ROOT/solution/run_floquet.py" \
  --params "$ROOT/environment/packet/cases.csv" \
  --out "$DEV_OUT"

python "$ROOT/tests/score.py" \
  --pred "$DEV_OUT" \
  --gold "$ROOT/environment/packet/dev_gold.csv"

bash "$ROOT/tests/test.sh" "$ROOT/solution"
