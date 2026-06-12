#!/usr/bin/env python3
import argparse
import csv
import subprocess
import tempfile
from pathlib import Path


def run(cmd: list[str]) -> int:
    print("+ " + " ".join(cmd))
    return subprocess.run(cmd).returncode


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def perturb(value: str) -> str:
    text = value.strip()
    try:
        if text and str(int(text)) == text:
            return str(int(text) + 1)
    except ValueError:
        pass
    try:
        val = float(text)
    except ValueError:
        return text
    if abs(val) < 1e-12:
        return "0.123456789"
    return f"{val * 1.2:.12g}"


def write_bad_gold_as_prediction(gold_path: Path, bad_path: Path) -> None:
    fields, rows = read_rows(gold_path)
    if "case_id" not in fields:
        raise ValueError(f"{gold_path}: missing case_id")
    with bad_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            out = {"case_id": row["case_id"]}
            for field in fields:
                if field == "case_id":
                    continue
                out[field] = perturb(row[field])
            writer.writerow(out)


def solve(params: Path, out: Path, runner: Path) -> int:
    return run(["python3", str(runner), "--params", str(params), "--out", str(out)])


def score(pred: Path, gold: Path, scorer: Path) -> int:
    return run(["python3", str(scorer), "--pred", str(pred), "--gold", str(gold)])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--runner-name", default="run_floquet.py")
    args = parser.parse_args()

    task = args.task.resolve()
    runner = task / "solution" / args.runner_name
    scorer = task / "tests" / "score.py"
    public_cases = task / "environment" / "packet" / "cases.csv"
    public_gold = task / "environment" / "packet" / "dev_gold.csv"
    hidden_cases = task / "tests" / "hidden" / "cases.csv"
    hidden_gold = task / "tests" / "gold" / "gold.csv"
    verifier = task / "tests" / "test.sh"

    with tempfile.TemporaryDirectory(prefix="floquet_selfcheck_") as tmp:
        tmp_path = Path(tmp)
        public_out = tmp_path / "public_out.csv"
        hidden_out = tmp_path / "hidden_out.csv"
        bad_out = tmp_path / "bad_out.csv"

        print("== oracle on public packet ==")
        if solve(public_cases, public_out, runner) != 0:
            return 1
        public_status = score(public_out, public_gold, scorer)

        print("\n== oracle on hidden packet ==")
        if solve(hidden_cases, hidden_out, runner) != 0:
            return 1
        hidden_status = score(hidden_out, hidden_gold, scorer)

        print("\n== perturbed hidden gold must FAIL ==")
        write_bad_gold_as_prediction(hidden_gold, bad_out)
        bad_status = score(bad_out, hidden_gold, scorer)

        print("\n== harbor verifier contract ==")
        verifier_status = run(["bash", str(verifier)])

    print("----------------------------------------")
    if (
        public_status == 0
        and hidden_status == 0
        and bad_status != 0
        and verifier_status == 0
    ):
        print("SELFCHECK PASSED (oracle PASS, perturbed FAIL, verifier PASS)")
        return 0
    print(
        "SELFCHECK FAILED "
        f"(public={public_status} hidden={hidden_status} "
        f"bad={bad_status} verifier={verifier_status})"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
