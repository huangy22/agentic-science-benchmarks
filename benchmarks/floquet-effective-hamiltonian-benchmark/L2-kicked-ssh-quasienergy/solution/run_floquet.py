#!/usr/bin/env python3
import argparse
import csv
import math


def solve(row):
    dx = float(row["dx"])
    dy = float(row["dy"])
    dz = float(row["dz"])
    alpha_z = float(row["alpha_z"])
    period = float(row["T"])

    energy = math.sqrt(dx * dx + dy * dy + dz * dz)
    if energy == 0.0:
        raise ValueError(f"{row['case_id']}: E_k must be nonzero")
    arg = (
        math.cos(alpha_z) * math.cos(energy * period)
        - (dz / energy) * math.sin(alpha_z) * math.sin(energy * period)
    )
    arg = max(-1.0, min(1.0, arg))
    return math.acos(arg) / period


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    with open(args.params, newline="") as f:
        rows = list(csv.DictReader(f))

    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "epsilon"])
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "case_id": row["case_id"],
                    "epsilon": f"{solve(row):.12g}",
                }
            )


if __name__ == "__main__":
    raise SystemExit(main())
