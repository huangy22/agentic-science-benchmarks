#!/usr/bin/env bash
set -euo pipefail
python run_floquet.py --params packet/cases.csv --out out.csv
