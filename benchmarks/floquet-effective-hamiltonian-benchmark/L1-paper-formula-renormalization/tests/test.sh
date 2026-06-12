#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="${1:-$ROOT/solution}"
OUT="${TMPDIR:-/tmp}/floquet_l1_formula_out.csv"

python "$WORK/run_floquet.py" \
  --params "$ROOT/tests/hidden/cases.csv" \
  --out "$OUT"

python "$ROOT/tests/score.py" \
  --pred "$OUT" \
  --gold "$ROOT/tests/gold/gold.csv"
