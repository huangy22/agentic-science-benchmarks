#!/usr/bin/env python3
import argparse
import csv


def state(real, imag):
    width = -2.0 * imag
    if width <= 0.0:
        raise ValueError("decaying metastable state must have negative Im(epsilon)")
    return {"energy": real, "width": width}


def solve(row):
    a = state(float(row["eps_a_real"]), float(row["eps_a_imag"]))
    b = state(float(row["eps_b_real"]), float(row["eps_b_imag"]))
    less, more = sorted([a, b], key=lambda item: item["width"], reverse=True)
    return {
        "less_stable_energy": less["energy"],
        "less_stable_width": less["width"],
        "more_stable_energy": more["energy"],
        "more_stable_width": more["width"],
        "energy_splitting": less["energy"] - more["energy"],
        "width_ratio": less["width"] / more["width"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    with open(args.params, newline="") as f:
        rows = list(csv.DictReader(f))

    fields = [
        "case_id",
        "less_stable_energy",
        "less_stable_width",
        "more_stable_energy",
        "more_stable_width",
        "energy_splitting",
        "width_ratio",
    ]
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            result = solve(row)
            writer.writerow(
                {
                    "case_id": row["case_id"],
                    **{key: f"{value:.12g}" for key, value in result.items()},
                }
            )


if __name__ == "__main__":
    raise SystemExit(main())
