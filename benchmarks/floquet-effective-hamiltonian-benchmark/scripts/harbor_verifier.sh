#!/usr/bin/env bash
set -uo pipefail

TASK_ROOT="${1:-}"
RUNNER_NAME="${2:-run_floquet.py}"

if [ -d /app ] && [ -d /tests ]; then
  APP_DIR=/app
  TESTS_DIR=/tests
  HIDDEN_DIR=/tests/hidden
  GOLD_FILE=/tests/gold/gold.csv
  LOG_DIR="${FLOQUET_VERIFIER_LOG_DIR:-/logs/verifier}"
else
  if [ -z "$TASK_ROOT" ]; then
    TASK_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  fi
  APP_DIR="$TASK_ROOT/solution"
  TESTS_DIR="$TASK_ROOT/tests"
  HIDDEN_DIR="$TESTS_DIR/hidden"
  GOLD_FILE="$TESTS_DIR/gold/gold.csv"
  LOG_DIR="${FLOQUET_VERIFIER_LOG_DIR:-$TASK_ROOT/.verifier_logs}"
fi

mkdir -p "$LOG_DIR" /tmp/floquet_p
PRED_DIR="$(mktemp -d /tmp/floquet_p/preds.XXXXXX)"
RUNNER_INPUTS="$(mktemp -d /tmp/floquet_p/runner_inputs.XXXXXX)"
cleanup() {
  rm -rf "$PRED_DIR" "$RUNNER_INPUTS"
}
trap cleanup EXIT

chmod -R a+rwX "$PRED_DIR" "$RUNNER_INPUTS"
if [ "$(id -u)" -eq 0 ]; then
  chmod -R go-rwx "$HIDDEN_DIR" "$(dirname "$GOLD_FILE")"
  chmod go-rwx "$TESTS_DIR/test.sh" "$TESTS_DIR/score.py"
fi
chmod -R a+rX "$APP_DIR"

cp "$HIDDEN_DIR/cases.csv" "$RUNNER_INPUTS/cases.csv"
find "$HIDDEN_DIR" -mindepth 1 ! -name cases.csv -exec cp -R {} "$RUNNER_INPUTS/" \;
chmod -R a+rX "$RUNNER_INPUTS"

run_agent() {
  if [ "$(id -u)" -eq 0 ] && command -v python3 >/dev/null 2>&1; then
    python3 - "$@" <<'PY'
import os
import pwd
import subprocess
import sys

try:
    pw = pwd.getpwnam("nobody")
except KeyError:
    raise SystemExit(subprocess.run(sys.argv[1:]).returncode)
os.setgid(pw.pw_gid)
os.setuid(pw.pw_uid)
raise SystemExit(subprocess.run(sys.argv[1:]).returncode)
PY
  else
    "$@"
  fi
}

fail=0
run_agent python3 "$APP_DIR/$RUNNER_NAME" \
  --params "$RUNNER_INPUTS/cases.csv" \
  --out "$PRED_DIR/out.csv" \
  || { echo "[verifier] runner failed"; fail=1; }

python3 "$TESTS_DIR/score.py" \
  --pred "$PRED_DIR/out.csv" \
  --gold "$GOLD_FILE" \
  > "$LOG_DIR/score.log" 2>&1
score_status=$?

if [ "$fail" -eq 0 ] && [ "$score_status" -eq 0 ]; then
  echo '{"pass": true}' > "$LOG_DIR/result.json"
  echo 1 > "$LOG_DIR/reward.txt"
else
  echo '{"pass": false}' > "$LOG_DIR/result.json"
  echo 0 > "$LOG_DIR/reward.txt"
fi
cat "$LOG_DIR/score.log"
echo "[verifier] reward=$(cat "$LOG_DIR/reward.txt")"
exit $((1 - $(cat "$LOG_DIR/reward.txt")))
