#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

cp "$ROOT/solution/run_floquet.py" "$WORKDIR/run_floquet.py"
python "$WORKDIR/run_floquet.py" \
  --params "$ROOT/environment/packet/cases.csv" \
  --out "$WORKDIR/dev_out.csv"
python "$ROOT/tests/score.py" \
  --pred "$WORKDIR/dev_out.csv" \
  --gold "$ROOT/environment/packet/dev_gold.csv"

bash "$ROOT/tests/test.sh"
