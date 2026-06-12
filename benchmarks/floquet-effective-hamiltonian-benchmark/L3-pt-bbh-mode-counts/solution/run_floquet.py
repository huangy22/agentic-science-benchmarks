#!/usr/bin/env python3
import argparse
import csv


def solve(row):
    n0 = int(row["N0"])
    npi = int(row["Npi"])
    vr = int(row["VR"])
    zero_gap_corner_states = 4 * abs(n0)
    pi_gap_corner_states = 4 * abs(npi)
    total_corner_states = zero_gap_corner_states + pi_gap_corner_states
    same_gap_coexistence = int(zero_gap_corner_states > 0 and vr > 0)
    return {
        "zero_gap_corner_states": zero_gap_corner_states,
        "pi_gap_corner_states": pi_gap_corner_states,
        "first_order_boundary_pairs": vr,
        "total_corner_states": total_corner_states,
        "same_gap_coexistence": same_gap_coexistence,
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
        "zero_gap_corner_states",
        "pi_gap_corner_states",
        "first_order_boundary_pairs",
        "total_corner_states",
        "same_gap_coexistence",
    ]
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({"case_id": row["case_id"], **solve(row)})


if __name__ == "__main__":
    raise SystemExit(main())
