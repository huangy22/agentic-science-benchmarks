#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path


def read_scan(path):
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"{path}: empty scan")
    return rows


def locate_minimum(rows, field):
    best = min(rows, key=lambda row: abs(float(row[field])))
    return float(best["E0"])


def solve(row, base_dir):
    scan_path = Path(row["scan_file"])
    if not scan_path.is_absolute():
        scan_path = base_dir / scan_path
    scan = read_scan(scan_path)
    return locate_minimum(scan, "gamma_gap"), locate_minimum(scan, "m_gap")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    params_path = Path(args.params)
    with params_path.open(newline="") as f:
        rows = list(csv.DictReader(f))

    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "E0c1", "E0c2"])
        writer.writeheader()
        for row in rows:
            e0c1, e0c2 = solve(row, params_path.parent)
            writer.writerow(
                {
                    "case_id": row["case_id"],
                    "E0c1": f"{e0c1:.12g}",
                    "E0c2": f"{e0c2:.12g}",
                }
            )


if __name__ == "__main__":
    raise SystemExit(main())
