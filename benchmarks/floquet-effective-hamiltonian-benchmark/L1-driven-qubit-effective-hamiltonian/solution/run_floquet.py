#!/usr/bin/env python3
import argparse
import csv
import math


def cmatmul(a, b):
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


def step_unitary(hx, hz, dt):
    r = math.hypot(hx, hz)
    if r == 0.0:
        return [[1.0 + 0.0j, 0.0j], [0.0j, 1.0 + 0.0j]]
    c = math.cos(r * dt)
    s_over_r = math.sin(r * dt) / r
    return [
        [c - 1j * s_over_r * hz, -1j * s_over_r * hx],
        [-1j * s_over_r * hx, c + 1j * s_over_r * hz],
    ]


def matpow(u, n):
    out = [[1.0 + 0.0j, 0.0j], [0.0j, 1.0 + 0.0j]]
    base = u
    while n:
        if n & 1:
            out = cmatmul(base, out)
        base = cmatmul(base, base)
        n >>= 1
    return out


def solve_case(row):
    bias = float(row["bias"])
    coupling = float(row["coupling"])
    drive = float(row["drive"])
    omega = float(row["omega"])
    phase = float(row["phase"])
    n_periods = int(row["n_periods"])
    steps = int(row["steps"])

    period = 2.0 * math.pi / omega
    dt = period / steps
    u = [[1.0 + 0.0j, 0.0j], [0.0j, 1.0 + 0.0j]]
    hz = 0.5 * bias

    for k in range(steps):
        t = (k + 0.5) * dt
        hx = coupling + drive * math.cos(omega * t + phase)
        u = cmatmul(step_unitary(hx, hz, dt), u)

    cos_theta = max(-1.0, min(1.0, ((u[0][0] + u[1][1]).real) / 2.0))
    theta = math.acos(cos_theta)
    sin_theta = math.sin(theta)
    quasienergy_gap = 2.0 * theta / period

    if abs(sin_theta) < 1e-12:
        heff_x = heff_y = heff_z = 0.0
    else:
        # B = -i * (cos(theta) I - U) = sin(theta) * n.sigma.
        b00 = -1j * (cos_theta - u[0][0])
        b01 = -1j * (0.0 - u[0][1])
        b10 = -1j * (0.0 - u[1][0])
        b11 = -1j * (cos_theta - u[1][1])
        bx = 0.5 * (b01 + b10)
        by = (b10 - b01) / (2j)
        bz = 0.5 * (b00 - b11)
        scale = theta / (period * sin_theta)
        heff_x = (scale * bx).real
        heff_y = (scale * by).real
        heff_z = (scale * bz).real

    un = matpow(u, n_periods)
    p_down = abs(un[1][0]) ** 2

    return {
        "case_id": row["case_id"],
        "heff_x": heff_x,
        "heff_y": heff_y,
        "heff_z": heff_z,
        "quasienergy_gap": quasienergy_gap,
        "p_down": p_down,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    with open(args.params, newline="") as f:
        rows = list(csv.DictReader(f))

    fields = ["case_id", "heff_x", "heff_y", "heff_z", "quasienergy_gap", "p_down"]
    with open(args.out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            result = solve_case(row)
            writer.writerow(
                {
                    "case_id": result["case_id"],
                    "heff_x": f"{result['heff_x']:.10f}",
                    "heff_y": f"{result['heff_y']:.10f}",
                    "heff_z": f"{result['heff_z']:.10f}",
                    "quasienergy_gap": f"{result['quasienergy_gap']:.10f}",
                    "p_down": f"{result['p_down']:.10f}",
                }
            )


if __name__ == "__main__":
    raise SystemExit(main())
