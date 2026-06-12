#!/usr/bin/env bash
set -euo pipefail

python run_floquet.py --params "${1:-packet/cases.csv}" --out "${2:-out.csv}"
