#!/usr/bin/env python3
import argparse
import csv
import math


def bessel_j0(x):
    term = 1.0
    total = 1.0
    xx = x * x / 4.0
    for m in range(1, 100):
        term *= -xx / (m * m)
        total += term
        if abs(term) < 1e-16:
            break
    return total


def bessel_j1(x):
    term = x / 2.0
    total = term
    xx = x * x / 4.0
    for m in range(1, 100):
        term *= -xx / (m * (m + 1))
        total += term
        if abs(term) < 1e-16:
            break
    return total


def solve(row):
    formula = row["formula"]
    x = float(row["x"])
    phi0 = float(row["phi0"])
    j = float(row["J"])
    omega = float(row["omega"])
    e0 = float(row["E0"])

    if formula == "bh_bessel_tunneling":
        return bessel_j0(x), 0.0, 0.0
    if formula == "raman_coupling":
        return bessel_j0(x), bessel_j0(x), bessel_j0(2.0 * x * math.sin(phi0 / 2.0))
    if formula == "binary_bec_tunneling":
        return bessel_j0(x), 0.0, 0.0
    if formula == "magnon_dm":
        exact = math.sqrt(3.0) * j * j * bessel_j1(e0) ** 2 / omega
        small_drive = math.sqrt(3.0) * j * j * e0 * e0 / (4.0 * omega)
        return exact, small_drive, 0.0
    raise ValueError(f"unknown formula {formula!r}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    with open(args.params, newline="") as f:
        rows = list(csv.DictReader(f))

    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["case_id", "value_1", "value_2", "value_3"])
        writer.writeheader()
        for row in rows:
            v1, v2, v3 = solve(row)
            writer.writerow(
                {
                    "case_id": row["case_id"],
                    "value_1": f"{v1:.12g}",
                    "value_2": f"{v2:.12g}",
                    "value_3": f"{v3:.12g}",
                }
            )


if __name__ == "__main__":
    raise SystemExit(main())
