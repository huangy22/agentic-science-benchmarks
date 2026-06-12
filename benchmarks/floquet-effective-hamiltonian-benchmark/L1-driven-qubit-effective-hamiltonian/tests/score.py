#!/usr/bin/env python3
import argparse
import csv
import math
import sys


FIELDS = ["heff_x", "heff_y", "heff_z", "quasienergy_gap", "p_down"]
TOL = {
    "heff_x": 5e-4,
    "heff_y": 5e-4,
    "heff_z": 5e-4,
    "quasienergy_gap": 5e-4,
    "p_down": 1e-4,
}


def read_table(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    out = {}
    for row in rows:
        cid = row.get("case_id", "").strip()
        if not cid:
            raise ValueError(f"{path}: row without case_id")
        if cid in out:
            raise ValueError(f"{path}: duplicate case_id {cid}")
        out[cid] = row
    return out


def as_float(row, field, cid):
    try:
        val = float(row[field])
    except Exception as exc:
        raise ValueError(f"{cid}: invalid {field}") from exc
    if not math.isfinite(val):
        raise ValueError(f"{cid}: non-finite {field}")
    return val


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred", required=True)
    parser.add_argument("--gold", required=True)
    args = parser.parse_args()

    pred = read_table(args.pred)
    gold = read_table(args.gold)

    missing = sorted(set(gold) - set(pred))
    extra = sorted(set(pred) - set(gold))
    if missing or extra:
        if missing:
            print(f"missing cases: {missing}", file=sys.stderr)
        if extra:
            print(f"extra cases: {extra}", file=sys.stderr)
        return 1

    failures = []
    max_err = {f: 0.0 for f in FIELDS}
    for cid in sorted(gold):
        for field in FIELDS:
            got = as_float(pred[cid], field, cid)
            ref = as_float(gold[cid], field, cid)
            err = abs(got - ref)
            max_err[field] = max(max_err[field], err)
            if err > TOL[field]:
                failures.append((cid, field, got, ref, err, TOL[field]))

    if failures:
        print("FAIL")
        for cid, field, got, ref, err, tol in failures:
            print(
                f"{cid} {field}: got={got:.10g} ref={ref:.10g} "
                f"abs_err={err:.3g} tol={tol:.3g}"
            )
        return 1

    print("PASS")
    for field in FIELDS:
        print(f"max_abs_err[{field}]={max_err[field]:.3g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
