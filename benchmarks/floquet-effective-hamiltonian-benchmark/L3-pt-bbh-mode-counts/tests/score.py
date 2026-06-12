#!/usr/bin/env python3
import argparse
import csv
import sys


FIELDS = [
    "zero_gap_corner_states",
    "pi_gap_corner_states",
    "first_order_boundary_pairs",
    "total_corner_states",
    "same_gap_coexistence",
]


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


def as_int(row, field, cid):
    try:
        value = int(row[field])
    except Exception as exc:
        raise ValueError(f"{cid}: invalid integer field {field}") from exc
    if str(value) != row[field].strip():
        raise ValueError(f"{cid}: non-canonical integer field {field}")
    return value


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
    for cid in sorted(gold):
        for field in FIELDS:
            got = as_int(pred[cid], field, cid)
            ref = as_int(gold[cid], field, cid)
            if got != ref:
                failures.append((cid, field, got, ref))

    if failures:
        print("FAIL")
        for cid, field, got, ref in failures:
            print(f"{cid} {field}: got={got} ref={ref}")
        return 1

    print("PASS")
    print(f"cases={len(gold)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
