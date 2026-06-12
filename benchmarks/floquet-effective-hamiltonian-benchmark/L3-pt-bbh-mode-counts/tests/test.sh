#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

cp "$ROOT/solution/run_floquet.py" "$WORKDIR/run_floquet.py"
python "$WORKDIR/run_floquet.py" \
  --params "$ROOT/tests/hidden/cases.csv" \
  --out "$WORKDIR/out.csv"
python "$ROOT/tests/score.py" \
  --pred "$WORKDIR/out.csv" \
  --gold "$ROOT/tests/gold/gold.csv"
