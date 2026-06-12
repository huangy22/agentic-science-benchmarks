#!/usr/bin/env python3
import argparse
import csv
import json
import os
import sys
import tomllib
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TERMS = ROOT / "data" / "original_paper_check_terms.csv"
BASE_URL = "https://open.bohrium.com/openapi/v1/lkm"


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def read_key(use_gaia_credentials_file: bool) -> str | None:
    for name in ("GAIA_LKM_ACCESS_KEY", "LKM_ACCESS_KEY"):
        key = os.environ.get(name)
        if key:
            return key
    if not use_gaia_credentials_file:
        return None
    path = Path.home() / ".config" / "gaia" / "credentials.toml"
    if not path.exists():
        return None
    with path.open("rb") as f:
        doc = tomllib.load(f)
    lkm = doc.get("lkm")
    if isinstance(lkm, dict):
        key = lkm.get("access_key")
        if isinstance(key, str) and key:
            return key
    return None


def load_terms(path: Path) -> list[dict[str, object]]:
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    expected = ["reference_case_id", "paper_id", "required_terms"]
    if rows and list(rows[0]) != expected:
        raise ValueError(f"{path}: unexpected columns")
    out = []
    for row in rows:
        terms = [term.strip() for term in row["required_terms"].split(";") if term.strip()]
        if not terms:
            raise ValueError(f"{path}: {row['reference_case_id']} has no terms")
        out.append({**row, "terms": terms})
    return out


def post_content_batch(paper_ids: list[str], key: str, timeout: float) -> dict:
    payload = json.dumps({"paper_ids": paper_ids}).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/papers/content/batch",
        data=payload,
        method="POST",
        headers={"Content-Type": "application/json", "accessKey": key},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_text(url: str, timeout: float) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--terms", type=Path, default=TERMS)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument(
        "--use-gaia-credentials-file",
        action="store_true",
        help="Read ~/.config/gaia/credentials.toml if env vars are unset.",
    )
    args = parser.parse_args()

    key = read_key(args.use_gaia_credentials_file)
    if not key:
        return fail(
            "missing LKM access key; set GAIA_LKM_ACCESS_KEY or LKM_ACCESS_KEY"
        )

    try:
        checks = load_terms(args.terms)
    except Exception as exc:
        return fail(str(exc))
    by_paper: dict[str, list[dict[str, object]]] = defaultdict(list)
    for check in checks:
        by_paper[str(check["paper_id"])].append(check)

    try:
        payload = post_content_batch(sorted(by_paper), key, args.timeout)
    except urllib.error.HTTPError as exc:
        return fail(f"content batch HTTP {exc.code}")
    except Exception as exc:
        return fail(f"content batch request failed: {type(exc).__name__}: {exc}")

    if payload.get("code") != 0:
        return fail(f"content batch returned code {payload.get('code')}")
    data = payload.get("data")
    if not isinstance(data, dict):
        return fail("content batch response missing data object")
    not_found = data.get("not_found") or []
    if not_found:
        return fail(f"content batch did not find papers: {not_found}")
    items = data.get("items") or []
    item_by_paper = {str(item.get("paper_id")): item for item in items}

    failures = []
    checked_terms = 0
    for paper_id, paper_checks in by_paper.items():
        item = item_by_paper.get(paper_id)
        if not item:
            failures.append((paper_id, "(paper)", "missing content item"))
            continue
        markdown_url = item.get("markdown_url")
        if not isinstance(markdown_url, str) or not markdown_url:
            failures.append((paper_id, "(paper)", "missing markdown_url"))
            continue
        try:
            markdown = fetch_text(markdown_url, args.timeout)
        except Exception as exc:
            failures.append((paper_id, "(paper)", f"markdown fetch failed: {exc}"))
            continue
        for check in paper_checks:
            ref_id = str(check["reference_case_id"])
            for term in check["terms"]:
                checked_terms += 1
                if term not in markdown:
                    failures.append((paper_id, ref_id, f"missing term {term!r}"))

    if failures:
        print("FAIL")
        for paper_id, ref_id, message in failures:
            print(f"{paper_id} {ref_id}: {message}")
        return 1

    print("PASS")
    print(f"papers={len(by_paper)} references={len(checks)} terms={checked_terms}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
