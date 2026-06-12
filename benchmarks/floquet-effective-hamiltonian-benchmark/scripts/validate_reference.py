#!/usr/bin/env python3
import csv
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data" / "floquet_reference.csv"
SOURCE_MANIFEST = ROOT / "data" / "lkm_source_manifest.csv"
ORIGINAL_CHECKS = ROOT / "data" / "original_paper_checks.csv"
RUNNABLE_L1 = ROOT / "L1-paper-formula-renormalization"
RUNNABLE_L2 = ROOT / "L2-kicked-ssh-quasienergy"
RUNNABLE_L3 = ROOT / "L3-graphene-antidot-critical-amplitudes"

REQUIRED_COLUMNS = [
    "case_id",
    "level",
    "status",
    "paper_id",
    "title",
    "doi",
    "model_system",
    "drive_protocol",
    "expected_method",
    "gold_observable",
    "gold_value",
    "tolerance",
    "verification_mode",
    "source_node_id",
    "source_excerpt",
    "quality_notes",
]

ALLOWED_LEVELS = {"L1", "L2", "L3"}
ALLOWED_STATUS = {"accepted_reference", "needs_original_paper", "rejected"}

MANIFEST_COLUMNS = [
    "paper_id",
    "title",
    "doi",
    "lkm_graph_status",
    "node_count",
    "edge_count",
    "addressed_problem_count",
    "open_question_count",
    "reference_source_nodes",
    "reference_statuses",
    "raw_payload_location",
]

ORIGINAL_CHECK_COLUMNS = [
    "reference_case_id",
    "paper_id",
    "doi",
    "original_source",
    "checked_fields",
    "confirmed_values",
    "check_status",
    "notes",
]


def fail(message: str) -> int:
    print(f"FAIL: {message}", file=sys.stderr)
    return 1


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    with REFERENCE.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with SOURCE_MANIFEST.open(newline="") as f:
        manifest_reader = csv.DictReader(f)
        manifest_rows = list(manifest_reader)

    with ORIGINAL_CHECKS.open(newline="") as f:
        original_reader = csv.DictReader(f)
        original_rows = list(original_reader)

    if reader.fieldnames != REQUIRED_COLUMNS:
        return fail(
            "unexpected columns: "
            f"{reader.fieldnames!r}; expected {REQUIRED_COLUMNS!r}"
        )
    if len(rows) < 12:
        return fail("reference table should contain at least 12 candidate cases")
    if manifest_reader.fieldnames != MANIFEST_COLUMNS:
        return fail(
            "unexpected manifest columns: "
            f"{manifest_reader.fieldnames!r}; expected {MANIFEST_COLUMNS!r}"
        )
    if original_reader.fieldnames != ORIGINAL_CHECK_COLUMNS:
        return fail(
            "unexpected original-check columns: "
            f"{original_reader.fieldnames!r}; expected {ORIGINAL_CHECK_COLUMNS!r}"
        )

    ids = [r["case_id"] for r in rows]
    dupes = [cid for cid, n in Counter(ids).items() if n > 1]
    if dupes:
        return fail(f"duplicate case_id values: {dupes}")

    accepted = [r for r in rows if r["status"] == "accepted_reference"]
    accepted_by_case = {r["case_id"]: r for r in accepted}
    if len(accepted) < 10:
        return fail("need at least 10 accepted_reference rows")

    accepted_levels = Counter(r["level"] for r in accepted)
    for level in ("L1", "L2", "L3"):
        if accepted_levels[level] < 3:
            return fail(f"need at least 3 accepted_reference rows for {level}")

    paper_ids = {r["paper_id"] for r in accepted}
    if len(paper_ids) < 7:
        return fail("accepted references must span at least 7 papers")

    manifest_by_paper = {r["paper_id"]: r for r in manifest_rows}
    if len(manifest_by_paper) != len(manifest_rows):
        return fail("manifest has duplicate paper_id values")
    original_by_case = {r["reference_case_id"]: r for r in original_rows}
    if len(original_by_case) != len(original_rows):
        return fail("original paper checks have duplicate reference_case_id values")

    for i, row in enumerate(rows, start=2):
        missing = [c for c in REQUIRED_COLUMNS if not row[c].strip()]
        if missing:
            return fail(f"row {i} missing required values: {missing}")
        if row["level"] not in ALLOWED_LEVELS:
            return fail(f"row {i} invalid level {row['level']!r}")
        if row["status"] not in ALLOWED_STATUS:
            return fail(f"row {i} invalid status {row['status']!r}")
        if not row["paper_id"].isdigit():
            return fail(f"row {i} paper_id is not numeric")
        expected_prefix = f"paper:{row['paper_id']}::"
        if not row["source_node_id"].startswith(expected_prefix):
            return fail(
                f"row {i} source_node_id must start with {expected_prefix!r}"
            )
        if len(row["source_excerpt"]) < 30:
            return fail(f"row {i} source_excerpt is too short")
        manifest = manifest_by_paper.get(row["paper_id"])
        if manifest is None:
            return fail(f"row {i} paper_id missing from source manifest")
        if row["status"] == "accepted_reference":
            if manifest["lkm_graph_status"] != "ok":
                return fail(
                    f"row {i} accepted reference has non-ok graph status "
                    f"{manifest['lkm_graph_status']!r}"
                )
            node_name = row["source_node_id"].split("::", 1)[1]
            manifest_nodes = manifest["reference_source_nodes"].split(";")
            if node_name not in manifest_nodes:
                return fail(
                    f"row {i} source node {node_name!r} is absent from manifest"
                )

    l1_case_files = [
        RUNNABLE_L1 / "environment" / "packet" / "cases.csv",
        RUNNABLE_L1 / "tests" / "hidden" / "cases.csv",
    ]
    runnable_refs: set[str] = set()
    for case_file in l1_case_files:
        for row in load_csv(case_file):
            ref_id = row["reference_case_id"]
            runnable_refs.add(ref_id)
            ref = accepted_by_case.get(ref_id)
            if ref is None:
                return fail(f"{case_file}: unknown accepted reference {ref_id!r}")
            if ref["level"] != "L1":
                return fail(f"{case_file}: {ref_id!r} is not an L1 reference")
            if row["paper_id"] != ref["paper_id"]:
                return fail(
                    f"{case_file}: paper_id mismatch for {row['case_id']} "
                    f"({row['paper_id']} != {ref['paper_id']})"
                )
    accepted_l1_refs = {r["case_id"] for r in accepted if r["level"] == "L1"}
    if not accepted_l1_refs.issubset(runnable_refs):
        missing = sorted(accepted_l1_refs - runnable_refs)
        return fail(f"runnable L1 task does not cover accepted references: {missing}")

    l2_runnable_refs: set[str] = set()
    l2_case_files = [
        RUNNABLE_L2 / "environment" / "packet" / "cases.csv",
        RUNNABLE_L2 / "tests" / "hidden" / "cases.csv",
    ]
    for case_file in l2_case_files:
        for row in load_csv(case_file):
            ref_id = row["reference_case_id"]
            l2_runnable_refs.add(ref_id)
            ref = accepted_by_case.get(ref_id)
            if ref is None:
                return fail(f"{case_file}: unknown accepted reference {ref_id!r}")
            if ref["level"] != "L2":
                return fail(f"{case_file}: {ref_id!r} is not an L2 reference")
            if row["paper_id"] != ref["paper_id"]:
                return fail(
                    f"{case_file}: paper_id mismatch for {row['case_id']} "
                    f"({row['paper_id']} != {ref['paper_id']})"
                )
    if "flq_l2_kicked_ssh_quasienergy_formula" not in l2_runnable_refs:
        return fail("runnable L2 task does not cover kicked SSH quasienergy row")

    l3_case_files = [
        RUNNABLE_L3 / "environment" / "packet" / "cases.csv",
        RUNNABLE_L3 / "tests" / "hidden" / "cases.csv",
    ]
    l3_runnable_refs: set[str] = set()
    for case_file in l3_case_files:
        case_dir = case_file.parent
        for row in load_csv(case_file):
            ref_id = row["reference_case_id"]
            l3_runnable_refs.add(ref_id)
            ref = accepted_by_case.get(ref_id)
            if ref is None:
                return fail(f"{case_file}: unknown accepted reference {ref_id!r}")
            if ref["level"] != "L3":
                return fail(f"{case_file}: {ref_id!r} is not an L3 reference")
            if row["paper_id"] != ref["paper_id"]:
                return fail(
                    f"{case_file}: paper_id mismatch for {row['case_id']} "
                    f"({row['paper_id']} != {ref['paper_id']})"
                )
            scan_path = case_dir / row["scan_file"]
            if not scan_path.exists():
                return fail(f"{case_file}: missing scan file {scan_path}")
            original_check = original_by_case.get(ref_id)
            if original_check is None:
                return fail(f"{case_file}: {ref_id!r} lacks original-paper check")
            if original_check["check_status"] != "confirmed":
                return fail(
                    f"{case_file}: {ref_id!r} original-paper check is not confirmed"
                )
            if original_check["paper_id"] != ref["paper_id"]:
                return fail(f"{case_file}: original-check paper mismatch for {ref_id}")
    if "flq_l3_graphene_antidot_critical_amplitudes" not in l3_runnable_refs:
        return fail("runnable L3 task does not cover graphene critical amplitudes row")

    print("PASS")
    print(f"rows={len(rows)} accepted={len(accepted)} papers={len(paper_ids)}")
    print(f"manifest_papers={len(manifest_rows)}")
    for level in ("L1", "L2", "L3"):
        print(f"accepted[{level}]={accepted_levels[level]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
