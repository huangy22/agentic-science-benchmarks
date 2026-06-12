#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path


def is_true(value):
    return str(value).strip() in {"1", "true", "True", "yes"}


def read_grid(path):
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    valid = [
        float(row["photon_energy_eV"])
        for row in rows
        if is_true(row["first_zone_ok"]) and is_true(row["two_band_ok"])
    ]
    if not valid:
        raise ValueError(f"{path}: no valid photon-energy grid points")
    return min(valid), max(valid)


def solve(row, base_dir):
    grid_path = Path(row["grid_file"])
    if not grid_path.is_absolute():
        grid_path = base_dir / grid_path
    return read_grid(grid_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    params_path = Path(args.params)
    with params_path.open(newline="") as f:
        rows = list(csv.DictReader(f))

    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["case_id", "window_low_eV", "window_high_eV"]
        )
        writer.writeheader()
        for row in rows:
            low, high = solve(row, params_path.parent)
            writer.writerow(
                {
                    "case_id": row["case_id"],
                    "window_low_eV": f"{low:.12g}",
                    "window_high_eV": f"{high:.12g}",
                }
            )


if __name__ == "__main__":
    raise SystemExit(main())
