#!/usr/bin/env python3
import csv
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "data" / "floquet_reference.csv"
SOURCE_MANIFEST = ROOT / "data" / "lkm_source_manifest.csv"
ORIGINAL_CHECKS = ROOT / "data" / "original_paper_checks.csv"
ORIGINAL_CHECK_TERMS = ROOT / "data" / "original_paper_check_terms.csv"
BENCHMARK_MANIFEST = ROOT / "benchmark_manifest.csv"
RUNNABLE_L1 = ROOT / "L1-paper-formula-renormalization"
RUNNABLE_L2_KICKED = ROOT / "L2-kicked-ssh-quasienergy"
RUNNABLE_L2_SQUARE = ROOT / "L2-square-well-complex-quasienergies"
RUNNABLE_L3_CRITICAL = ROOT / "L3-graphene-antidot-critical-amplitudes"
RUNNABLE_L3_WINDOWS = ROOT / "L3-graphene-antidot-photon-windows"
RUNNABLE_L3_PT_BBH = ROOT / "L3-pt-bbh-mode-counts"
PROTOTYPE = ROOT / "L1-driven-qubit-effective-hamiltonian"

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

ORIGINAL_CHECK_TERMS_COLUMNS = [
    "reference_case_id",
    "paper_id",
    "required_terms",
]

BENCHMARK_MANIFEST_COLUMNS = [
    "task_id",
    "level",
    "status",
    "paper_derived",
    "task_path",
    "reference_case_ids",
    "paper_ids",
    "hidden_gold_type",
    "original_check_required",
    "selfcheck_command",
    "notes",
]

MIN_HIDDEN_CASES_PER_RUNNABLE_TASK = 5


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

    with ORIGINAL_CHECK_TERMS.open(newline="") as f:
        original_terms_reader = csv.DictReader(f)
        original_terms_rows = list(original_terms_reader)

    with BENCHMARK_MANIFEST.open(newline="") as f:
        benchmark_manifest_reader = csv.DictReader(f)
        benchmark_manifest_rows = list(benchmark_manifest_reader)

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
    if original_terms_reader.fieldnames != ORIGINAL_CHECK_TERMS_COLUMNS:
        return fail(
            "unexpected original-check-terms columns: "
            f"{original_terms_reader.fieldnames!r}; "
            f"expected {ORIGINAL_CHECK_TERMS_COLUMNS!r}"
        )
    if benchmark_manifest_reader.fieldnames != BENCHMARK_MANIFEST_COLUMNS:
        return fail(
            "unexpected benchmark-manifest columns: "
            f"{benchmark_manifest_reader.fieldnames!r}; "
            f"expected {BENCHMARK_MANIFEST_COLUMNS!r}"
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
    original_terms_by_case = {
        r["reference_case_id"]: r for r in original_terms_rows
    }
    if len(original_terms_by_case) != len(original_terms_rows):
        return fail("original paper check terms have duplicate reference_case_id values")
    for ref_id, row in original_terms_by_case.items():
        check = original_by_case.get(ref_id)
        if check is None:
            return fail(f"terms row references unknown original check {ref_id!r}")
        if row["paper_id"] != check["paper_id"]:
            return fail(f"terms paper_id mismatch for {ref_id!r}")
        terms = [term.strip() for term in row["required_terms"].split(";")]
        if not [term for term in terms if term]:
            return fail(f"terms row has no required terms for {ref_id!r}")

    task_ids = [r["task_id"] for r in benchmark_manifest_rows]
    task_dupes = [tid for tid, n in Counter(task_ids).items() if n > 1]
    if task_dupes:
        return fail(f"benchmark manifest has duplicate task_id values: {task_dupes}")
    paper_derived_tasks = [
        r
        for r in benchmark_manifest_rows
        if r["status"] == "runnable" and r["paper_derived"] == "yes"
    ]
    if len(paper_derived_tasks) < 4:
        return fail("expected at least four runnable paper-derived tasks")
    manifest_levels = Counter(r["level"] for r in paper_derived_tasks)
    for level in ("L1", "L2", "L3"):
        if manifest_levels[level] < 1:
            return fail(f"benchmark manifest lacks runnable paper-derived {level} task")
    manifest_papers: set[str] = set()
    manifest_l3_papers: set[str] = set()
    manifest_refs: set[str] = set()
    for row in benchmark_manifest_rows:
        task_path = ROOT / row["task_path"]
        if not task_path.exists():
            return fail(f"manifest task_path does not exist: {task_path}")
        if not (task_path / "task.toml").exists():
            return fail(f"manifest task lacks task.toml: {task_path}")
        if not (task_path / "scripts" / "selfcheck.sh").exists():
            return fail(f"manifest task lacks scripts/selfcheck.sh: {task_path}")
        if row["paper_derived"] == "yes":
            for ref_id in row["reference_case_ids"].split(";"):
                ref = accepted_by_case.get(ref_id)
                if ref is None:
                    return fail(f"manifest references unknown accepted row {ref_id!r}")
                if ref["level"] != row["level"]:
                    return fail(
                        f"manifest level mismatch for {row['task_id']} -> {ref_id}"
                    )
                manifest_refs.add(ref_id)
                if row["original_check_required"] == "yes":
                    original_check = original_by_case.get(ref_id)
                    if original_check is None:
                        return fail(
                            f"manifest task {row['task_id']} requires original "
                            f"check, but {ref_id!r} has no check row"
                        )
                    if ref_id not in original_terms_by_case:
                        return fail(
                            f"manifest task {row['task_id']} requires original "
                            f"check, but {ref_id!r} has no term row"
                        )
                    if original_check["check_status"] != "confirmed":
                        return fail(
                            f"manifest task {row['task_id']} original check for "
                            f"{ref_id!r} is not confirmed"
                        )
                    if original_check["paper_id"] != ref["paper_id"]:
                        return fail(
                            f"manifest task {row['task_id']} original-check "
                            f"paper mismatch for {ref_id!r}"
                        )
                    if "papers/content/batch" not in original_check["original_source"]:
                        return fail(
                            f"manifest task {row['task_id']} original check for "
                            f"{ref_id!r} must use LKM papers/content/batch unless "
                            "explicitly downgraded"
                        )
            for paper_id in row["paper_ids"].split(";"):
                if not paper_id.isdigit():
                    return fail(f"manifest paper id is not numeric: {paper_id!r}")
                manifest_papers.add(paper_id)
                if row["level"] == "L3" and row["status"] == "runnable":
                    manifest_l3_papers.add(paper_id)
            if row["level"] == "L3" and row["original_check_required"] != "yes":
                return fail(f"manifest L3 task must require original check: {row['task_id']}")
        else:
            if row["task_path"] != PROTOTYPE.name:
                return fail(f"only the prototype may be non-paper-derived: {row['task_id']}")
    if len(manifest_papers) < 4:
        return fail("paper-derived runnable manifest must cover at least four papers")
    if len(manifest_l3_papers) < 2:
        return fail("runnable L3 manifest must cover at least two papers")

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

    all_packet_refs: set[str] = set()
    min_hidden_seen: int | None = None
    for task in paper_derived_tasks:
        task_path = ROOT / task["task_path"]
        task_ref_ids = {
            ref_id.strip()
            for ref_id in task["reference_case_ids"].split(";")
            if ref_id.strip()
        }
        case_files = [
            ("public", task_path / "environment" / "packet" / "cases.csv"),
            ("hidden", task_path / "tests" / "hidden" / "cases.csv"),
        ]
        for kind, case_file in case_files:
            if not case_file.exists():
                return fail(f"{task['task_id']}: missing {kind} cases {case_file}")
            with case_file.open(newline="") as f:
                case_reader = csv.DictReader(f)
                case_rows = list(case_reader)
            if "reference_case_id" not in (case_reader.fieldnames or []):
                return fail(
                    f"{case_file}: missing reference_case_id column for "
                    "paper-derived task"
                )
            if "paper_id" not in (case_reader.fieldnames or []):
                return fail(f"{case_file}: missing paper_id column")
            if kind == "hidden":
                min_hidden_seen = (
                    len(case_rows)
                    if min_hidden_seen is None
                    else min(min_hidden_seen, len(case_rows))
                )
                if len(case_rows) < MIN_HIDDEN_CASES_PER_RUNNABLE_TASK:
                    return fail(
                        f"{case_file}: hidden case count {len(case_rows)} is below "
                        f"{MIN_HIDDEN_CASES_PER_RUNNABLE_TASK}"
                    )
            for case in case_rows:
                ref_id = case["reference_case_id"]
                all_packet_refs.add(ref_id)
                ref = accepted_by_case.get(ref_id)
                if ref is None:
                    return fail(
                        f"{case_file}: reference_case_id {ref_id!r} is not an "
                        "accepted reference"
                    )
                if ref_id not in task_ref_ids:
                    return fail(
                        f"{case_file}: {ref_id!r} is absent from manifest "
                        f"reference_case_ids for {task['task_id']}"
                    )
                if ref["level"] != task["level"]:
                    return fail(
                        f"{case_file}: {ref_id!r} level {ref['level']} does not "
                        f"match task level {task['level']}"
                    )
                if case["paper_id"] != ref["paper_id"]:
                    return fail(
                        f"{case_file}: paper_id mismatch for {case['case_id']} "
                        f"({case['paper_id']} != {ref['paper_id']})"
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
        RUNNABLE_L2_KICKED / "environment" / "packet" / "cases.csv",
        RUNNABLE_L2_KICKED / "tests" / "hidden" / "cases.csv",
        RUNNABLE_L2_SQUARE / "environment" / "packet" / "cases.csv",
        RUNNABLE_L2_SQUARE / "tests" / "hidden" / "cases.csv",
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
    if "flq_l2_driven_square_well_quasienergies" not in l2_runnable_refs:
        return fail("runnable L2 task does not cover driven square-well row")

    l3_scan_case_files = [
        RUNNABLE_L3_CRITICAL / "environment" / "packet" / "cases.csv",
        RUNNABLE_L3_CRITICAL / "tests" / "hidden" / "cases.csv",
    ]
    l3_runnable_refs: set[str] = set()
    for case_file in l3_scan_case_files:
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
            if ref_id not in original_terms_by_case:
                return fail(f"{case_file}: {ref_id!r} lacks original-paper check terms")
            if original_check["check_status"] != "confirmed":
                return fail(
                    f"{case_file}: {ref_id!r} original-paper check is not confirmed"
                )
            if original_check["paper_id"] != ref["paper_id"]:
                return fail(f"{case_file}: original-check paper mismatch for {ref_id}")
            if "papers/content/batch" not in original_check["original_source"]:
                return fail(
                    f"{case_file}: {ref_id!r} must use LKM papers/content/batch "
                    "for promoted L3 hidden gold unless explicitly downgraded"
                )
    l3_grid_case_files = [
        RUNNABLE_L3_WINDOWS / "environment" / "packet" / "cases.csv",
        RUNNABLE_L3_WINDOWS / "tests" / "hidden" / "cases.csv",
    ]
    for case_file in l3_grid_case_files:
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
            grid_path = case_dir / row["grid_file"]
            if not grid_path.exists():
                return fail(f"{case_file}: missing grid file {grid_path}")
            original_check = original_by_case.get(ref_id)
            if original_check is None:
                return fail(f"{case_file}: {ref_id!r} lacks original-paper check")
            if ref_id not in original_terms_by_case:
                return fail(f"{case_file}: {ref_id!r} lacks original-paper check terms")
            if original_check["check_status"] != "confirmed":
                return fail(
                    f"{case_file}: {ref_id!r} original-paper check is not confirmed"
                )
            if original_check["paper_id"] != ref["paper_id"]:
                return fail(f"{case_file}: original-check paper mismatch for {ref_id}")
            if "papers/content/batch" not in original_check["original_source"]:
                return fail(
                    f"{case_file}: {ref_id!r} must use LKM papers/content/batch "
                    "for promoted L3 hidden gold unless explicitly downgraded"
                )
    l3_pt_bbh_case_files = [
        RUNNABLE_L3_PT_BBH / "tests" / "hidden" / "cases.csv",
    ]
    for case_file in l3_pt_bbh_case_files:
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
            original_check = original_by_case.get(ref_id)
            if original_check is None:
                return fail(f"{case_file}: {ref_id!r} lacks original-paper check")
            if ref_id not in original_terms_by_case:
                return fail(f"{case_file}: {ref_id!r} lacks original-paper check terms")
            if original_check["check_status"] != "confirmed":
                return fail(
                    f"{case_file}: {ref_id!r} original-paper check is not confirmed"
                )
            if original_check["paper_id"] != ref["paper_id"]:
                return fail(f"{case_file}: original-check paper mismatch for {ref_id}")
            if "papers/content/batch" not in original_check["original_source"]:
                return fail(
                    f"{case_file}: {ref_id!r} must use LKM papers/content/batch "
                    "for promoted L3 hidden gold unless explicitly downgraded"
                )
    if "flq_l3_graphene_antidot_critical_amplitudes" not in l3_runnable_refs:
        return fail("runnable L3 task does not cover graphene critical amplitudes row")
    if "flq_l3_graphene_antidot_photon_windows" not in l3_runnable_refs:
        return fail("runnable L3 task does not cover graphene photon windows row")
    if "flq_l3_pt_bbh_indices_same_gap" not in l3_runnable_refs:
        return fail("runnable L3 task does not cover PT-BBH same-gap row")
    if "flq_l3_pt_bbh_indices_split_gap" not in l3_runnable_refs:
        return fail("runnable L3 task does not cover PT-BBH split-gap row")
    required_manifest_refs = (
        runnable_refs | l2_runnable_refs | l3_runnable_refs | all_packet_refs
    )
    if not required_manifest_refs.issubset(manifest_refs):
        missing = sorted(required_manifest_refs - manifest_refs)
        return fail(f"benchmark manifest missing runnable references: {missing}")

    print("PASS")
    print(f"rows={len(rows)} accepted={len(accepted)} papers={len(paper_ids)}")
    print(f"manifest_papers={len(manifest_rows)}")
    print(f"runnable_paper_derived_tasks={len(paper_derived_tasks)}")
    print(f"runnable_paper_derived_papers={len(manifest_papers)}")
    print(f"runnable_l3_papers={len(manifest_l3_papers)}")
    print(f"min_hidden_cases_per_task={min_hidden_seen}")
    for level in ("L1", "L2", "L3"):
        print(f"accepted[{level}]={accepted_levels[level]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
