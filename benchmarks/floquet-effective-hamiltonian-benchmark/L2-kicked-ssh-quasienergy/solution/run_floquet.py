#!/usr/bin/env python3
import argparse
import csv
import math


def matmul(a, b):
    return [
        [
            a[0][0] * b[0][0] + a[0][1] * b[1][0],
            a[0][0] * b[0][1] + a[0][1] * b[1][1],
        ],
        [
            a[1][0] * b[0][0] + a[1][1] * b[1][0],
            a[1][0] * b[0][1] + a[1][1] * b[1][1],
        ],
    ]


def exp_pauli(nx, ny, nz, angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return [
        [c - 1j * s * nz, -1j * s * (nx - 1j * ny)],
        [-1j * s * (nx + 1j * ny), c + 1j * s * nz],
    ]


def solve(row):
    dx = float(row["dx"])
    dy = float(row["dy"])
    dz = float(row["dz"])
    alpha_z = float(row["alpha_z"])
    period = float(row["T"])

    energy = math.sqrt(dx * dx + dy * dy + dz * dz)
    if energy == 0.0:
        raise ValueError(f"{row['case_id']}: E_k must be nonzero")
    free = exp_pauli(dx / energy, dy / energy, dz / energy, energy * period)
    kick = exp_pauli(0.0, 0.0, 1.0, alpha_z)
    propagator = matmul(kick, free)
    half_trace = 0.5 * (propagator[0][0] + propagator[1][1]).real
    half_trace = max(-1.0, min(1.0, half_trace))
    return math.acos(half_trace) / period


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
